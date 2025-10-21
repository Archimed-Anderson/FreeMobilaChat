"""
Model Training Service for Fine-tuning LLM on French Customer Service Tweets
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
from datetime import datetime
import logging
import json
import asyncio
import os
from pathlib import Path
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt
import seaborn as sns

# GPU Training imports
try:
    import torch
    import torch.nn as nn
    from torch.utils.data import Dataset, DataLoader
    from transformers import (
        AutoTokenizer, AutoModelForSequenceClassification,
        TrainingArguments, Trainer, EarlyStoppingCallback,
        DataCollatorWithPadding, get_linear_schedule_with_warmup
    )
    from peft import LoraConfig, get_peft_model, TaskType, PeftModel
    from accelerate import Accelerator
    import bitsandbytes as bnb
    from datasets import Dataset as HFDataset
    import wandb
    GPU_AVAILABLE = True
except ImportError as e:
    print(f"GPU training dependencies not available: {e}")
    GPU_AVAILABLE = False

from ..models import TweetAnalyzed, TweetRaw, SentimentType, CategoryType, PriorityLevel
from ..services.llm_analyzer import LLMAnalyzer, LLMProvider
from ..utils.database import DatabaseManager
from ..config_pkg import gpu_config as config

logger = logging.getLogger(__name__)

class ModelTrainingService:
    """Service for training and evaluating LLM models on tweet analysis tasks"""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        Initialize model training service
        
        Args:
            db_manager: Database manager for storing results
        """
        self.db_manager = db_manager or DatabaseManager()
        self.training_results = {}
        self.evaluation_metrics = {}
        
    def load_training_data(self, data_dir: str = "data/training") -> Dict[str, pd.DataFrame]:
        """
        Load prepared training datasets with validation

        Args:
            data_dir: Directory containing training data

        Returns:
            Dictionary with train/val/test DataFrames

        Raises:
            ValueError: If required columns are missing or data is invalid
        """
        logger.info(f"Loading training data from {data_dir}")

        data_path = Path(data_dir)
        datasets = {}
        required_columns = ['tweet_id', 'author', 'text', 'date', 'sentiment', 'category', 'priority']

        for split in ['train', 'validation', 'test']:
            file_path = data_path / f"{split}_dataset.csv"
            if file_path.exists():
                try:
                    df = pd.read_csv(file_path, encoding='utf-8')

                    # Validate required columns
                    missing_columns = [col for col in required_columns if col not in df.columns]
                    if missing_columns:
                        raise ValueError(f"Missing required columns in {split} dataset: {missing_columns}")

                    # Validate data types and content
                    if df.empty:
                        raise ValueError(f"{split} dataset is empty")

                    # Check for null values in critical columns
                    critical_columns = ['text', 'sentiment', 'category', 'priority']
                    null_counts = df[critical_columns].isnull().sum()
                    if null_counts.any():
                        logger.warning(f"Found null values in {split} dataset: {null_counts.to_dict()}")

                    # Validate enum values
                    valid_sentiments = [e.value for e in SentimentType]
                    valid_categories = [e.value for e in CategoryType]
                    valid_priorities = [e.value for e in PriorityLevel]

                    invalid_sentiments = df[~df['sentiment'].isin(valid_sentiments)]['sentiment'].unique()
                    invalid_categories = df[~df['category'].isin(valid_categories)]['category'].unique()
                    invalid_priorities = df[~df['priority'].isin(valid_priorities)]['priority'].unique()

                    if len(invalid_sentiments) > 0:
                        logger.warning(f"Invalid sentiment values in {split}: {invalid_sentiments}")
                    if len(invalid_categories) > 0:
                        logger.warning(f"Invalid category values in {split}: {invalid_categories}")
                    if len(invalid_priorities) > 0:
                        logger.warning(f"Invalid priority values in {split}: {invalid_priorities}")

                    datasets[split] = df
                    logger.info(f" Loaded {split} dataset: {len(df)} samples")

                except Exception as e:
                    logger.error(f" Error loading {split} dataset from {file_path}: {e}")
                    raise ValueError(f"Failed to load {split} dataset: {e}")
            else:
                logger.warning(f"Dataset file not found: {file_path}")

        if not datasets:
            raise ValueError(f"No valid datasets found in {data_dir}")

        return datasets
    
    async def evaluate_baseline_model(self, test_df: pd.DataFrame, 
                                    provider: LLMProvider = LLMProvider.MISTRAL) -> Dict[str, Any]:
        """
        Evaluate baseline (non-fine-tuned) model performance
        
        Args:
            test_df: Test dataset
            provider: LLM provider to use
            
        Returns:
            Evaluation results
        """
        logger.info(f"Evaluating baseline model with {provider.value}")
        
        analyzer = LLMAnalyzer(provider=provider)
        
        predictions = {
            'sentiment': [],
            'category': [],
            'priority': []
        }
        
        ground_truth = {
            'sentiment': test_df['sentiment'].tolist(),
            'category': test_df['category'].tolist(),
            'priority': test_df['priority'].tolist()
        }
        
        # Prepare tweets for batch analysis
        tweets_to_analyze = []
        failed_tweets = 0

        for _, row in test_df.iterrows():
            try:
                tweet = TweetRaw(
                    tweet_id=str(row['tweet_id']),
                    author=row['author'],
                    text=row['text'],
                    date=pd.to_datetime(row['date'])
                )
                tweets_to_analyze.append(tweet)
            except Exception as e:
                logger.error(f"Error creating tweet object for {row['tweet_id']}: {e}")
                failed_tweets += 1

        if not tweets_to_analyze:
            raise ValueError("No valid tweets found for analysis")

        logger.info(f"Starting batch analysis of {len(tweets_to_analyze)} tweets ({failed_tweets} failed to parse)")

        # Use batch processing for much better performance
        try:
            analyzed_results = await analyzer.analyze_batch(tweets_to_analyze)
        except Exception as e:
            logger.error(f"Batch analysis failed: {e}")
            raise RuntimeError(f"LLM analysis failed: {e}")

        # Process results and align with test_df order
        successful_analyses = len(analyzed_results)
        total_samples = len(test_df)

        # Create a mapping of tweet_id to results for quick lookup
        results_map = {result.tweet_id: result for result in analyzed_results}

        # Fill predictions in the same order as test_df
        for _, row in test_df.iterrows():
            tweet_id = str(row['tweet_id'])

            if tweet_id in results_map:
                result = results_map[tweet_id]
                predictions['sentiment'].append(result.sentiment.value)
                predictions['category'].append(result.category.value)
                predictions['priority'].append(result.priority.value)
            else:
                # Use default predictions for failed analyses
                predictions['sentiment'].append('neutral')
                predictions['category'].append('autre')
                predictions['priority'].append('moyenne')

        # Calculate metrics
        metrics = self.calculate_metrics(ground_truth, predictions)
        metrics['successful_analyses'] = successful_analyses
        metrics['success_rate'] = successful_analyses / total_samples

        logger.info(f"Baseline evaluation completed: {successful_analyses}/{total_samples} successful")
        return metrics
    
    def calculate_metrics(self, ground_truth: Dict[str, List], 
                         predictions: Dict[str, List]) -> Dict[str, Any]:
        """
        Calculate comprehensive evaluation metrics
        
        Args:
            ground_truth: Ground truth labels
            predictions: Model predictions
            
        Returns:
            Dictionary with metrics
        """
        metrics = {}
        
        for task in ['sentiment', 'category', 'priority']:
            y_true = ground_truth[task]
            y_pred = predictions[task]
            
            # Basic metrics
            accuracy = accuracy_score(y_true, y_pred)
            precision, recall, f1, support = precision_recall_fscore_support(
                y_true, y_pred, average='weighted', zero_division=0
            )
            
            # Per-class metrics
            class_report = classification_report(
                y_true, y_pred, output_dict=True, zero_division=0
            )
            
            # Confusion matrix
            cm = confusion_matrix(y_true, y_pred)
            unique_labels = sorted(list(set(y_true + y_pred)))
            
            metrics[task] = {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'support': int(np.sum(support)),
                'classification_report': class_report,
                'confusion_matrix': cm.tolist(),
                'labels': unique_labels
            }
            
            logger.info(f"{task.capitalize()} - Accuracy: {accuracy:.3f}, F1: {f1:.3f}")
        
        # Overall metrics
        metrics['overall'] = {
            'avg_accuracy': np.mean([metrics[task]['accuracy'] for task in metrics.keys() if task != 'overall']),
            'avg_f1': np.mean([metrics[task]['f1_score'] for task in metrics.keys() if task != 'overall']),
            'total_samples': len(ground_truth['sentiment'])
        }
        
        return metrics
    
    def generate_confusion_matrices(self, metrics: Dict[str, Any], 
                                  output_dir: str = "data/results") -> Dict[str, str]:
        """
        Generate and save confusion matrix visualizations
        
        Args:
            metrics: Evaluation metrics
            output_dir: Output directory for plots
            
        Returns:
            Dictionary with plot file paths
        """
        logger.info("Generating confusion matrix visualizations")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        plot_files = {}
        
        for task in ['sentiment', 'category', 'priority']:
            if task in metrics:
                plt.figure(figsize=(10, 8))
                
                cm = np.array(metrics[task]['confusion_matrix'])
                labels = metrics[task]['labels']
                
                sns.heatmap(
                    cm, 
                    annot=True, 
                    fmt='d', 
                    cmap='Blues',
                    xticklabels=labels,
                    yticklabels=labels
                )
                
                plt.title(f'Confusion Matrix - {task.capitalize()}')
                plt.xlabel('Predicted')
                plt.ylabel('Actual')
                plt.tight_layout()
                
                plot_file = output_path / f"confusion_matrix_{task}.png"
                plt.savefig(plot_file, dpi=300, bbox_inches='tight')
                plt.close()
                
                plot_files[task] = str(plot_file)
                logger.info(f"Saved confusion matrix for {task}: {plot_file}")
        
        return plot_files
    
    def generate_performance_report(self, metrics: Dict[str, Any], 
                                  model_name: str = "Baseline",
                                  output_dir: str = "data/results") -> str:
        """
        Generate comprehensive performance report
        
        Args:
            metrics: Evaluation metrics
            model_name: Name of the model
            output_dir: Output directory
            
        Returns:
            Path to generated report
        """
        logger.info(f"Generating performance report for {model_name}")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        report_file = output_path / f"performance_report_{model_name.lower()}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# Performance Report - {model_name}\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Overall metrics
            if 'overall' in metrics:
                f.write("## Overall Performance\n\n")
                f.write(f"- **Average Accuracy:** {metrics['overall']['avg_accuracy']:.3f}\n")
                f.write(f"- **Average F1-Score:** {metrics['overall']['avg_f1']:.3f}\n")
                f.write(f"- **Total Samples:** {metrics['overall']['total_samples']}\n")
                
                if 'success_rate' in metrics:
                    f.write(f"- **Success Rate:** {metrics['success_rate']:.3f}\n")
                
                f.write("\n")
            
            # Task-specific metrics
            for task in ['sentiment', 'category', 'priority']:
                if task in metrics:
                    task_metrics = metrics[task]
                    f.write(f"## {task.capitalize()} Analysis\n\n")
                    f.write(f"- **Accuracy:** {task_metrics['accuracy']:.3f}\n")
                    f.write(f"- **Precision:** {task_metrics['precision']:.3f}\n")
                    f.write(f"- **Recall:** {task_metrics['recall']:.3f}\n")
                    f.write(f"- **F1-Score:** {task_metrics['f1_score']:.3f}\n")
                    f.write(f"- **Support:** {task_metrics['support']}\n\n")
                    
                    # Per-class performance
                    f.write(f"### Per-Class Performance ({task.capitalize()})\n\n")
                    f.write("| Class | Precision | Recall | F1-Score | Support |\n")
                    f.write("|-------|-----------|--------|----------|----------|\n")
                    
                    class_report = task_metrics['classification_report']
                    for class_name, class_metrics in class_report.items():
                        if isinstance(class_metrics, dict) and class_name not in ['accuracy', 'macro avg', 'weighted avg']:
                            f.write(f"| {class_name} | {class_metrics['precision']:.3f} | "
                                   f"{class_metrics['recall']:.3f} | {class_metrics['f1-score']:.3f} | "
                                   f"{class_metrics['support']} |\n")
                    
                    f.write("\n")
            
            # Insights and recommendations
            f.write("## Key Insights\n\n")
            
            # Identify best and worst performing tasks
            task_accuracies = {task: metrics[task]['accuracy'] for task in ['sentiment', 'category', 'priority'] if task in metrics}
            if task_accuracies:
                best_task = max(task_accuracies, key=task_accuracies.get)
                worst_task = min(task_accuracies, key=task_accuracies.get)
                
                f.write(f"- **Best performing task:** {best_task.capitalize()} (Accuracy: {task_accuracies[best_task]:.3f})\n")
                f.write(f"- **Most challenging task:** {worst_task.capitalize()} (Accuracy: {task_accuracies[worst_task]:.3f})\n")
            
            f.write("\n## Recommendations\n\n")
            f.write("- Consider fine-tuning the model on domain-specific data\n")
            f.write("- Improve training data quality and balance\n")
            f.write("- Implement ensemble methods for better performance\n")
            f.write("- Add more French-specific preprocessing steps\n")
        
        logger.info(f"Performance report saved: {report_file}")
        return str(report_file)
    
    async def run_comprehensive_evaluation(self, data_dir: str = "data/training",
                                         output_dir: str = "data/results") -> Dict[str, Any]:
        """
        Run comprehensive model evaluation pipeline
        
        Args:
            data_dir: Directory with training data
            output_dir: Output directory for results
            
        Returns:
            Complete evaluation results
        """
        logger.info("Starting comprehensive model evaluation")
        
        try:
            # Load datasets
            datasets = self.load_training_data(data_dir)
            
            if 'test' not in datasets:
                raise ValueError("Test dataset not found")
            
            test_df = datasets['test']
            
            # Evaluate baseline model
            baseline_metrics = await self.evaluate_baseline_model(test_df)
            
            # Generate visualizations
            plot_files = self.generate_confusion_matrices(baseline_metrics, output_dir)
            
            # Generate report
            report_file = self.generate_performance_report(baseline_metrics, "Baseline", output_dir)
            
            # Save detailed results
            results_file = Path(output_dir) / "evaluation_results.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(baseline_metrics, f, indent=2, ensure_ascii=False, default=str)
            
            # Store in database if available
            if self.db_manager:
                try:
                    await self.db_manager.store_evaluation_results({
                        'evaluation_date': datetime.now(),
                        'model_name': 'Baseline',
                        'test_samples': len(test_df),
                        'metrics': baseline_metrics,
                        'files': {
                            'report': report_file,
                            'results': str(results_file),
                            'plots': plot_files
                        }
                    })
                except Exception as e:
                    logger.warning(f"Could not store results in database: {e}")
            
            results = {
                'success': True,
                'model_name': 'Baseline',
                'test_samples': len(test_df),
                'metrics': baseline_metrics,
                'files': {
                    'report': report_file,
                    'results': str(results_file),
                    'plots': plot_files
                }
            }
            
            logger.info("Comprehensive evaluation completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

if GPU_AVAILABLE:
    from torch.utils.data import Dataset as TorchDataset

    class TweetDataset(TorchDataset):
        """PyTorch Dataset for tweet classification"""

        def __init__(self, texts: List[str], labels: Dict[str, List], tokenizer, max_length: int = 512):
            self.texts = texts
            self.sentiment_labels = labels['sentiment']
            self.category_labels = labels['category']
            self.priority_labels = labels['priority']
            self.tokenizer = tokenizer
            self.max_length = max_length

            # Create label mappings
            self.sentiment_to_id = {label: idx for idx, label in enumerate(sorted(set(self.sentiment_labels)))}
            self.category_to_id = {label: idx for idx, label in enumerate(sorted(set(self.category_labels)))}
            self.priority_to_id = {label: idx for idx, label in enumerate(sorted(set(self.priority_labels)))}

            self.id_to_sentiment = {idx: label for label, idx in self.sentiment_to_id.items()}
            self.id_to_category = {idx: label for label, idx in self.category_to_id.items()}
            self.id_to_priority = {idx: label for label, idx in self.priority_to_id.items()}

        def __len__(self):
            return len(self.texts)

        def __getitem__(self, idx):
            text = str(self.texts[idx])

            # Tokenize
            encoding = self.tokenizer(
                text,
                truncation=True,
                padding='max_length',
                max_length=self.max_length,
                return_tensors='pt'
            )

            return {
                'input_ids': encoding['input_ids'].flatten(),
                'attention_mask': encoding['attention_mask'].flatten(),
                'sentiment_labels': torch.tensor(self.sentiment_to_id[self.sentiment_labels[idx]], dtype=torch.long),
                'category_labels': torch.tensor(self.category_to_id[self.category_labels[idx]], dtype=torch.long),
                'priority_labels': torch.tensor(self.priority_to_id[self.priority_labels[idx]], dtype=torch.long)
            }

    class MultiTaskModel(nn.Module):
        """Multi-task model for sentiment, category, and priority classification"""

        def __init__(self, model_name: str, num_sentiment_labels: int, num_category_labels: int, num_priority_labels: int, **model_kwargs):
            super().__init__()
            # Apply model_kwargs (including quantization config) to backbone model
            backbone_kwargs = {
                "num_labels": num_sentiment_labels,  # Primary task
                "cache_dir": config.gpu_training.cache_dir,
                **model_kwargs
            }
            self.backbone = AutoModelForSequenceClassification.from_pretrained(
                model_name,
                **backbone_kwargs
            )

            # Additional classification heads
            hidden_size = self.backbone.config.hidden_size
            self.category_classifier = nn.Linear(hidden_size, num_category_labels)
            self.priority_classifier = nn.Linear(hidden_size, num_priority_labels)

            self.dropout = nn.Dropout(0.1)

        def forward(self, input_ids, attention_mask, sentiment_labels=None, category_labels=None, priority_labels=None):
            # Get backbone outputs
            outputs = self.backbone(input_ids=input_ids, attention_mask=attention_mask, output_hidden_states=True)

            # Extract hidden states
            hidden_states = outputs.hidden_states[-1]  # Last layer
            pooled_output = hidden_states[:, 0]  # CLS token
            pooled_output = self.dropout(pooled_output)

            # Classification heads
            sentiment_logits = outputs.logits  # Primary task from backbone
            category_logits = self.category_classifier(pooled_output)
            priority_logits = self.priority_classifier(pooled_output)

            loss = None
            if sentiment_labels is not None and category_labels is not None and priority_labels is not None:
                loss_fct = nn.CrossEntropyLoss()
                sentiment_loss = loss_fct(sentiment_logits, sentiment_labels)
                category_loss = loss_fct(category_logits, category_labels)
                priority_loss = loss_fct(priority_logits, priority_labels)

                # Weighted combination of losses
                loss = sentiment_loss + 0.8 * category_loss + 0.6 * priority_loss

            return {
                'loss': loss,
                'sentiment_logits': sentiment_logits,
                'category_logits': category_logits,
                'priority_logits': priority_logits
            }

else:
    # Placeholder classes when GPU dependencies are not available
    class TweetDataset:
        def __init__(self, *args, **kwargs):
            raise ImportError("GPU training dependencies not available. Install torch, transformers, etc.")

    class MultiTaskModel:
        def __init__(self, *args, **kwargs):
            raise ImportError("GPU training dependencies not available. Install torch, transformers, etc.")

class GPUModelTrainer:
    """GPU-accelerated model training service"""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db_manager = db_manager
        if GPU_AVAILABLE:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = None
        self.logger = logging.getLogger(__name__)

        if not GPU_AVAILABLE:
            raise ImportError("GPU training dependencies not installed. Run: pip install torch transformers peft accelerate bitsandbytes")

        if GPU_AVAILABLE and not torch.cuda.is_available():
            self.logger.warning("CUDA not available. Training will use CPU (very slow)")

    def check_gpu_memory(self) -> Dict[str, Any]:
        """Check GPU memory status and clear cache if needed"""
        if not torch.cuda.is_available():
            return {"gpu_available": False}

        # Clear GPU cache before checking memory
        torch.cuda.empty_cache()

        gpu_info = {}
        for i in range(torch.cuda.device_count()):
            total_memory = torch.cuda.get_device_properties(i).total_memory / 1024**3  # GB
            allocated_memory = torch.cuda.memory_allocated(i) / 1024**3  # GB
            reserved_memory = torch.cuda.memory_reserved(i) / 1024**3  # GB
            free_memory = total_memory - allocated_memory

            gpu_info[f"gpu_{i}"] = {
                "name": torch.cuda.get_device_name(i),
                "memory_total": total_memory,
                "memory_allocated": allocated_memory,
                "memory_reserved": reserved_memory,
                "memory_free": free_memory,
                "memory_usage_percent": (allocated_memory / total_memory) * 100
            }

            # Log warning if memory usage is high
            if (allocated_memory / total_memory) > 0.8:
                self.logger.warning(f"GPU {i} memory usage is high: {allocated_memory:.1f}GB / {total_memory:.1f}GB")

        return {
            "gpu_available": True,
            "device_count": torch.cuda.device_count(),
            "current_device": torch.cuda.current_device(),
            "gpu_info": gpu_info
        }

    def prepare_datasets(self, train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame,
                        model_name: str) -> Tuple[Any, Any, Any, Any]:
        """Prepare datasets for training"""
        self.logger.info(f"Preparing datasets for model: {model_name}")

        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=config.gpu_training.cache_dir)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        # Prepare labels
        train_labels = {
            'sentiment': train_df['sentiment'].tolist(),
            'category': train_df['category'].tolist(),
            'priority': train_df['priority'].tolist()
        }

        val_labels = {
            'sentiment': val_df['sentiment'].tolist(),
            'category': val_df['category'].tolist(),
            'priority': val_df['priority'].tolist()
        }

        test_labels = {
            'sentiment': test_df['sentiment'].tolist(),
            'category': test_df['category'].tolist(),
            'priority': test_df['priority'].tolist()
        }

        # Create datasets
        train_dataset = TweetDataset(train_df['text'].tolist(), train_labels, tokenizer)
        val_dataset = TweetDataset(val_df['text'].tolist(), val_labels, tokenizer)
        test_dataset = TweetDataset(test_df['text'].tolist(), test_labels, tokenizer)

        return train_dataset, val_dataset, test_dataset, tokenizer

    def setup_model_with_lora(self, model_name: str, train_dataset: Any) -> Tuple[Any, Any]:
        """Setup model with LoRA configuration"""
        self.logger.info(f"Setting up model with LoRA: {model_name}")

        # Model configuration
        num_sentiment_labels = len(train_dataset.sentiment_to_id)
        num_category_labels = len(train_dataset.category_to_id)
        num_priority_labels = len(train_dataset.priority_to_id)

        # Load model with quantization if enabled
        model_kwargs = {"cache_dir": config.gpu_training.cache_dir}

        if config.gpu_training.use_quantization and torch.cuda.is_available():
            from transformers import BitsAndBytesConfig

            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_use_double_quant=True,
            )
            model_kwargs["quantization_config"] = bnb_config
            model_kwargs["device_map"] = "auto"

        # Create multi-task model with quantization config if available
        model = MultiTaskModel(model_name, num_sentiment_labels, num_category_labels, num_priority_labels, **model_kwargs)

        if config.gpu_training.use_lora:
            # LoRA configuration
            lora_config = LoraConfig(
                task_type=TaskType.SEQ_CLS,
                r=config.gpu_training.lora_r,
                lora_alpha=config.gpu_training.lora_alpha,
                lora_dropout=config.gpu_training.lora_dropout,
                target_modules=["query", "value", "key", "dense"]  # Common attention modules
            )

            model = get_peft_model(model, lora_config)
            model.print_trainable_parameters()

        return model, model_kwargs

    async def train_model(self, data_dir: str = "data/training", output_dir: Optional[str] = None) -> Dict[str, Any]:
        """Train model on GPU with comprehensive error handling"""
        if output_dir is None:
            output_dir = config.gpu_training.output_dir

        try:
            self.logger.info(" Starting GPU model training")

            # Check GPU status and memory
            gpu_info = self.check_gpu_memory()
            self.logger.info(f"GPU Status: {gpu_info}")

            if not gpu_info.get("gpu_available", False):
                raise RuntimeError("GPU not available for training")

            # Create output directory
            Path(output_dir).mkdir(parents=True, exist_ok=True)

            # Load and validate datasets
            self.logger.info(" Loading training datasets...")
            data_path = Path(data_dir)

            # Check if dataset files exist
            required_files = ["train_dataset.csv", "validation_dataset.csv", "test_dataset.csv"]
            missing_files = [f for f in required_files if not (data_path / f).exists()]
            if missing_files:
                raise FileNotFoundError(f"Missing dataset files: {missing_files}")

            try:
                train_df = pd.read_csv(data_path / "train_dataset.csv", encoding='utf-8')
                val_df = pd.read_csv(data_path / "validation_dataset.csv", encoding='utf-8')
                test_df = pd.read_csv(data_path / "test_dataset.csv", encoding='utf-8')
            except Exception as e:
                raise ValueError(f"Failed to load dataset files: {e}")

            self.logger.info(f" Loaded datasets - Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")

            # Prepare datasets with validation
            self.logger.info(" Preparing datasets for training...")
            try:
                train_dataset, val_dataset, test_dataset, tokenizer = self.prepare_datasets(
                    train_df, val_df, test_df, config.gpu_training.model_name
                )
            except Exception as e:
                raise ValueError(f"Failed to prepare datasets: {e}")

            # Setup model with error handling
            self.logger.info("🤖 Setting up model architecture...")
            try:
                model, model_kwargs = self.setup_model_with_lora(config.gpu_training.model_name, train_dataset)
            except Exception as e:
                raise RuntimeError(f"Failed to setup model: {e}")

            # Training arguments
            training_args = TrainingArguments(
                output_dir=output_dir,
                num_train_epochs=config.gpu_training.num_epochs,
                per_device_train_batch_size=config.gpu_training.batch_size,
                per_device_eval_batch_size=config.gpu_training.batch_size,
                gradient_accumulation_steps=config.gpu_training.gradient_accumulation_steps,
                warmup_steps=config.gpu_training.warmup_steps,
                weight_decay=config.gpu_training.weight_decay,
                learning_rate=config.gpu_training.learning_rate,
                max_grad_norm=config.gpu_training.max_grad_norm,

                # Evaluation and saving
                evaluation_strategy="steps",
                eval_steps=config.gpu_training.eval_steps,
                save_steps=config.gpu_training.save_steps,
                save_total_limit=3,
                load_best_model_at_end=True,
                metric_for_best_model="eval_loss",
                greater_is_better=False,

                # Logging
                logging_steps=config.gpu_training.logging_steps,
                logging_dir=f"{output_dir}/logs",
                report_to="tensorboard",

                # Memory optimization
                gradient_checkpointing=config.gpu_training.use_gradient_checkpointing,
                fp16=config.gpu_training.use_mixed_precision and torch.cuda.is_available(),
                dataloader_num_workers=config.gpu_training.dataloader_num_workers,

                # Other settings
                remove_unused_columns=False,
                push_to_hub=False,
                seed=42
            )

            # Data collator
            data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

            # Custom trainer for multi-task learning
            trainer = MultiTaskTrainer(
                model=model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=val_dataset,
                tokenizer=tokenizer,
                data_collator=data_collator,
                callbacks=[EarlyStoppingCallback(early_stopping_patience=config.gpu_training.early_stopping_patience)]
            )

            # Start training
            self.logger.info("Starting training...")
            train_result = trainer.train()

            # Save model
            trainer.save_model()
            tokenizer.save_pretrained(output_dir)

            # Evaluate on test set
            self.logger.info("Evaluating on test set...")
            test_results = trainer.evaluate(eval_dataset=test_dataset)

            # Save training results
            results = {
                'success': True,
                'train_runtime': train_result.metrics['train_runtime'],
                'train_loss': train_result.metrics['train_loss'],
                'eval_loss': test_results['eval_loss'],
                'model_path': output_dir,
                'gpu_info': gpu_info,
                'training_args': training_args.to_dict()
            }

            # Save results to file
            results_file = Path(output_dir) / "training_results.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)

            self.logger.info(f" Training completed successfully. Model saved to: {output_dir}")
            return results

        except torch.cuda.OutOfMemoryError as e:
            self.logger.error(f" GPU out of memory during training: {e}")
            return {
                'success': False,
                'error': f"GPU out of memory: {e}",
                'error_type': 'OutOfMemoryError'
            }
        except FileNotFoundError as e:
            self.logger.error(f" Required files not found: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': 'FileNotFoundError'
            }
        except ValueError as e:
            self.logger.error(f" Data validation error: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': 'ValueError'
            }
        except RuntimeError as e:
            self.logger.error(f" Runtime error during training: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': 'RuntimeError'
            }
        except Exception as e:
            self.logger.error(f" Unexpected error during training: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': 'UnexpectedError'
            }
        finally:
            # Clean up GPU memory regardless of success or failure
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                self.logger.info("🧹 GPU memory cache cleared")

if GPU_AVAILABLE:
    class MultiTaskTrainer(Trainer):
        """Custom trainer for multi-task learning"""

        def compute_loss(self, model, inputs, return_outputs=False):
            """Custom loss computation for multi-task model"""
            outputs = model(**inputs)
            loss = outputs['loss']
            return (loss, outputs) if return_outputs else loss
else:
    class MultiTaskTrainer:
        def __init__(self, *args, **kwargs):
            raise ImportError("GPU training dependencies not available. Install torch, transformers, etc.")

class LocalModelInference:
    """Inference service for locally fine-tuned models"""

    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.logger = logging.getLogger(__name__)

        self._load_model()

    def _load_model(self):
        """Load the fine-tuned model and tokenizer"""
        try:
            self.logger.info(f"Loading model from: {self.model_path}")

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)

            # Load model
            if config.gpu_training.use_lora:
                # Load base model first
                base_model = AutoModelForSequenceClassification.from_pretrained(
                    config.gpu_training.model_name,
                    cache_dir=config.gpu_training.cache_dir
                )
                # Load LoRA weights
                self.model = PeftModel.from_pretrained(base_model, self.model_path)
            else:
                self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)

            self.model.to(self.device)
            self.model.eval()

            self.logger.info(" Model loaded successfully")

        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            raise

    def predict(self, text: str) -> Dict[str, Any]:
        """Make prediction on a single text"""
        try:
            # Tokenize
            inputs = self.tokenizer(
                text,
                truncation=True,
                padding=True,
                max_length=512,
                return_tensors='pt'
            ).to(self.device)

            # Predict
            with torch.no_grad():
                outputs = self.model(**inputs)

            # Process outputs (this would need to be adapted based on your model architecture)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=-1)
            predicted_class = torch.argmax(probabilities, dim=-1).item()
            confidence = probabilities.max().item()

            return {
                'predicted_class': predicted_class,
                'confidence': confidence,
                'probabilities': probabilities.cpu().numpy().tolist()
            }

        except Exception as e:
            self.logger.error(f"Prediction failed: {e}")
            return None

async def main():
    """Main function for testing model training"""
    service = ModelTrainingService()
    
    # Run comprehensive evaluation
    results = await service.run_comprehensive_evaluation()
    
    if results['success']:
        print("[SUCCESS] Model evaluation completed successfully!")
        print(f"[INFO] Test samples: {results['test_samples']}")
        print(f"[INFO] Average accuracy: {results['metrics']['overall']['avg_accuracy']:.3f}")
        print(f"[INFO] Average F1-score: {results['metrics']['overall']['avg_f1']:.3f}")
        print(f"[INFO] Report: {results['files']['report']}")
    else:
        print(f"[ERROR] Model evaluation failed: {results['error']}")

if __name__ == "__main__":
    asyncio.run(main())
