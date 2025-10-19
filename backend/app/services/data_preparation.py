"""
Data Preparation Service for Model Training
Handles dataset splitting, stratification, and ground truth preparation
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from pathlib import Path
import logging
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import json

from ..models import TweetRaw, TweetAnalyzed, SentimentType, CategoryType, PriorityLevel
from ..utils.database import DatabaseManager

logger = logging.getLogger(__name__)


class DataPreparationService:
    """Service for preparing training datasets and managing ground truth data"""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        Initialize data preparation service
        
        Args:
            db_manager: Database manager for storing results
        """
        self.db_manager = db_manager or DatabaseManager()
        self.label_encoders = {}
        self.dataset_stats = {}
        
    def load_tweet_data(self, csv_path: str) -> pd.DataFrame:
        """
        Load tweet data from CSV file
        
        Args:
            csv_path: Path to CSV file
            
        Returns:
            DataFrame with tweet data
        """
        logger.info(f"Loading tweet data from {csv_path}")
        
        try:
            df = pd.read_csv(csv_path, encoding='utf-8')
            logger.info(f"Loaded {len(df)} tweets from CSV")
            
            # Ensure required columns exist
            required_columns = ['tweet_id', 'author', 'text', 'date', 'url']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Convert date column
            df['date'] = pd.to_datetime(df['date'])
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading tweet data: {e}")
            raise
    
    def create_ground_truth_labels(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create ground truth labels for training data
        This would typically involve manual annotation, but for demo purposes,
        we'll use rule-based heuristics to create initial labels
        
        Args:
            df: DataFrame with tweet data
            
        Returns:
            DataFrame with ground truth labels
        """
        logger.info("Creating ground truth labels using heuristic rules")
        
        df_labeled = df.copy()
        
        # Sentiment labeling heuristics
        def label_sentiment(text: str) -> str:
            text_lower = text.lower()
            
            # Positive indicators
            positive_words = ['merci', 'excellent', 'parfait', 'super', 'génial', 'bravo', 'formidable']
            # Negative indicators  
            negative_words = ['problème', 'panne', 'bug', 'erreur', 'nul', 'horrible', 'inacceptable', 'urgent']
            
            positive_score = sum(1 for word in positive_words if word in text_lower)
            negative_score = sum(1 for word in negative_words if word in text_lower)
            
            if positive_score > negative_score:
                return 'positive'
            elif negative_score > positive_score:
                return 'negative'
            else:
                return 'neutral'
        
        # Category labeling heuristics
        def label_category(text: str) -> str:
            text_lower = text.lower()
            
            if any(word in text_lower for word in ['facture', 'facturation', 'paiement', 'prix', 'coût']):
                return 'facturation'
            elif any(word in text_lower for word in ['réseau', 'signal', 'couverture', 'antenne']):
                return 'réseau'
            elif any(word in text_lower for word in ['technique', 'bug', 'erreur', 'panne', 'dysfonctionnement']):
                return 'technique'
            elif any(word in text_lower for word in ['abonnement', 'forfait', 'contrat', 'souscription']):
                return 'abonnement'
            elif any(word in text_lower for word in ['réclamation', 'plainte', 'insatisfait', 'mécontent']):
                return 'réclamation'
            elif any(word in text_lower for word in ['merci', 'bravo', 'excellent', 'parfait']):
                return 'compliment'
            elif any(word in text_lower for word in ['comment', 'pourquoi', 'quand', 'où', '?']):
                return 'question'
            else:
                return 'autre'
        
        # Priority labeling heuristics
        def label_priority(text: str) -> str:
            text_lower = text.lower()
            
            if any(word in text_lower for word in ['urgent', 'critique', 'immédiat', 'bloqué', 'plus rien']):
                return 'critique'
            elif any(word in text_lower for word in ['problème', 'panne', 'bug', 'erreur']):
                return 'haute'
            elif any(word in text_lower for word in ['question', 'comment', 'aide']):
                return 'moyenne'
            else:
                return 'basse'
        
        # Apply labeling functions
        df_labeled['sentiment'] = df_labeled['text'].apply(label_sentiment)
        df_labeled['category'] = df_labeled['text'].apply(label_category)
        df_labeled['priority'] = df_labeled['text'].apply(label_priority)
        
        # Add additional labels
        df_labeled['is_urgent'] = df_labeled['priority'].isin(['critique', 'haute'])
        df_labeled['needs_response'] = df_labeled['category'] != 'compliment'
        
        # Estimate resolution time based on category and priority
        def estimate_resolution_time(category: str, priority: str) -> int:
            base_times = {
                'compliment': 5,
                'question': 15,
                'facturation': 30,
                'abonnement': 30,
                'technique': 60,
                'réseau': 90,
                'réclamation': 120,
                'autre': 30
            }
            
            multipliers = {
                'critique': 2.0,
                'haute': 1.5,
                'moyenne': 1.0,
                'basse': 0.5
            }
            
            base_time = base_times.get(category, 30)
            multiplier = multipliers.get(priority, 1.0)
            
            return int(base_time * multiplier)
        
        df_labeled['estimated_resolution_time'] = df_labeled.apply(
            lambda row: estimate_resolution_time(row['category'], row['priority']), 
            axis=1
        )
        
        logger.info(f"Created ground truth labels for {len(df_labeled)} tweets")
        return df_labeled
    
    def stratified_split(self, df: pd.DataFrame, 
                        test_size: float = 0.2, 
                        val_size: float = 0.1,
                        random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Split dataset into train/validation/test sets with stratification
        
        Args:
            df: DataFrame with labeled data
            test_size: Proportion for test set
            val_size: Proportion for validation set (from remaining data)
            random_state: Random seed for reproducibility
            
        Returns:
            Tuple of (train_df, val_df, test_df)
        """
        logger.info(f"Splitting dataset: train/val/test with test_size={test_size}, val_size={val_size}")
        
        # Create stratification key combining sentiment, category, and priority
        df['stratify_key'] = df['sentiment'] + '_' + df['category'] + '_' + df['priority']

        # Check if stratification is possible
        stratify_counts = df['stratify_key'].value_counts()
        min_count = stratify_counts.min()

        if min_count < 2:
            logger.warning(f"Some classes have only {min_count} samples. Using simple random split instead of stratified split.")
            # Use simple random split
            train_val_df, test_df = train_test_split(
                df,
                test_size=test_size,
                random_state=random_state
            )
        else:
            # Use stratified split
            train_val_df, test_df = train_test_split(
                df,
                test_size=test_size,
                stratify=df['stratify_key'],
                random_state=random_state
            )
        
        # Second split: separate validation from training
        if val_size > 0:
            val_size_adjusted = val_size / (1 - test_size)  # Adjust for remaining data

            # Check if stratification is possible for validation split
            train_val_stratify_counts = train_val_df['stratify_key'].value_counts()
            train_val_min_count = train_val_stratify_counts.min()

            if train_val_min_count < 2:
                logger.warning("Using simple random split for validation due to small class sizes.")
                train_df, val_df = train_test_split(
                    train_val_df,
                    test_size=val_size_adjusted,
                    random_state=random_state
                )
            else:
                train_df, val_df = train_test_split(
                    train_val_df,
                    test_size=val_size_adjusted,
                    stratify=train_val_df['stratify_key'],
                    random_state=random_state
                )
        else:
            train_df = train_val_df
            val_df = pd.DataFrame()
        
        # Remove stratification key
        for split_df in [train_df, val_df, test_df]:
            if len(split_df) > 0 and 'stratify_key' in split_df.columns:
                split_df.drop('stratify_key', axis=1, inplace=True)
        
        logger.info(f"Dataset split completed:")
        logger.info(f"  Training set: {len(train_df)} samples")
        logger.info(f"  Validation set: {len(val_df)} samples")
        logger.info(f"  Test set: {len(test_df)} samples")
        
        return train_df, val_df, test_df
    
    def analyze_dataset_distribution(self, df: pd.DataFrame, split_name: str = "dataset") -> Dict:
        """
        Analyze the distribution of labels in the dataset
        
        Args:
            df: DataFrame to analyze
            split_name: Name of the dataset split
            
        Returns:
            Dictionary with distribution statistics
        """
        logger.info(f"Analyzing distribution for {split_name}")
        
        stats = {
            'split_name': split_name,
            'total_samples': len(df),
            'sentiment_distribution': df['sentiment'].value_counts().to_dict(),
            'category_distribution': df['category'].value_counts().to_dict(),
            'priority_distribution': df['priority'].value_counts().to_dict(),
            'urgent_tweets': df['is_urgent'].sum(),
            'needs_response_tweets': df['needs_response'].sum(),
            'avg_text_length': df['text'].str.len().mean(),
            'unique_authors': df['author'].nunique()
        }
        
        # Calculate percentages
        stats['sentiment_percentages'] = {
            k: (v / len(df)) * 100 for k, v in stats['sentiment_distribution'].items()
        }
        stats['category_percentages'] = {
            k: (v / len(df)) * 100 for k, v in stats['category_distribution'].items()
        }
        stats['priority_percentages'] = {
            k: (v / len(df)) * 100 for k, v in stats['priority_distribution'].items()
        }
        
        return stats
    
    def save_datasets(self, train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame,
                     output_dir: str = "data/training") -> Dict[str, str]:
        """
        Save training datasets to files
        
        Args:
            train_df: Training dataset
            val_df: Validation dataset  
            test_df: Test dataset
            output_dir: Output directory
            
        Returns:
            Dictionary with file paths
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        file_paths = {}
        
        # Save datasets
        datasets = {
            'train': train_df,
            'validation': val_df,
            'test': test_df
        }
        
        for split_name, df in datasets.items():
            if len(df) > 0:
                file_path = output_path / f"{split_name}_dataset.csv"
                df.to_csv(file_path, index=False, encoding='utf-8')
                file_paths[split_name] = str(file_path)
                logger.info(f"Saved {split_name} dataset: {file_path} ({len(df)} samples)")
        
        # Save dataset statistics
        stats = {}
        for split_name, df in datasets.items():
            if len(df) > 0:
                stats[split_name] = self.analyze_dataset_distribution(df, split_name)
        
        stats_file = output_path / "dataset_statistics.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False, default=str)
        
        file_paths['statistics'] = str(stats_file)
        logger.info(f"Saved dataset statistics: {stats_file}")
        
        return file_paths
    
    def prepare_training_data(self, csv_path: str, output_dir: str = "data/training") -> Dict:
        """
        Complete data preparation pipeline
        
        Args:
            csv_path: Path to input CSV file
            output_dir: Output directory for prepared datasets
            
        Returns:
            Dictionary with preparation results
        """
        logger.info("Starting complete data preparation pipeline")
        
        try:
            # Load data
            df = self.load_tweet_data(csv_path)
            
            # Create ground truth labels
            df_labeled = self.create_ground_truth_labels(df)
            
            # Split dataset
            train_df, val_df, test_df = self.stratified_split(df_labeled)
            
            # Save datasets
            file_paths = self.save_datasets(train_df, val_df, test_df, output_dir)
            
            # Analyze distributions
            train_stats = self.analyze_dataset_distribution(train_df, "training")
            val_stats = self.analyze_dataset_distribution(val_df, "validation") if len(val_df) > 0 else {}
            test_stats = self.analyze_dataset_distribution(test_df, "test")
            
            # Store in database if available (skip for now - would need async)
            if self.db_manager:
                try:
                    # Note: Database storage would require async context
                    logger.info("Database storage skipped in synchronous context")
                except Exception as e:
                    logger.warning(f"Could not store metadata in database: {e}")
            
            results = {
                'success': True,
                'total_samples': len(df_labeled),
                'splits': {
                    'train': len(train_df),
                    'validation': len(val_df),
                    'test': len(test_df)
                },
                'file_paths': file_paths,
                'statistics': {
                    'train': train_stats,
                    'validation': val_stats,
                    'test': test_stats
                }
            }
            
            logger.info("Data preparation pipeline completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Data preparation pipeline failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }


async def main():
    """Main function for testing data preparation"""
    service = DataPreparationService()
    
    # Prepare training data
    results = service.prepare_training_data(
        csv_path="data/raw/free_tweet_export.csv",
        output_dir="data/training"
    )
    
    if results['success']:
        print("✅ Data preparation completed successfully!")
        print(f"📊 Total samples: {results['total_samples']}")
        print(f"📈 Training: {results['splits']['train']} samples")
        print(f"📉 Validation: {results['splits']['validation']} samples")
        print(f"🧪 Test: {results['splits']['test']} samples")
    else:
        print(f"❌ Data preparation failed: {results['error']}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
