#!/usr/bin/env python3
"""
GPU Model Training Script for FreeMobilaChat
Trains a fine-tuned model on French customer service tweets using local GPU
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from datetime import datetime
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv(Path(__file__).parent / ".env.gpu_training")  # Load GPU training config

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

try:
    from app.services.model_training import GPUModelTrainer
    from app.services.data_preparation import DataPreparationService
    from app.utils.database import DatabaseManager
    from app.config import config
    import torch
    GPU_AVAILABLE = True
except ImportError as e:
    print(f"❌ GPU training dependencies not available: {e}")
    print("Run: python setup_gpu_training.py")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class TrainingPipeline:
    """Complete GPU training pipeline"""
    
    def __init__(self, model_name: str = None):
        """Initialize training pipeline"""
        self.model_name = model_name or config.gpu_training.model_name
        self.gpu_trainer = GPUModelTrainer()
        self.data_prep_service = DataPreparationService()
        
        logger.info(f"Initialized training pipeline with model: {self.model_name}")
    
    def check_prerequisites(self) -> bool:
        """Check if system is ready for training"""
        logger.info("Checking training prerequisites...")
        
        # Check GPU
        gpu_info = self.gpu_trainer.check_gpu_memory()
        if not gpu_info.get("gpu_available", False):
            logger.warning("⚠️ No GPU detected. Training will be very slow on CPU.")
        else:
            logger.info(f"✅ GPU detected: {gpu_info}")
        
        # Check CUDA
        if torch.cuda.is_available():
            logger.info(f"✅ CUDA available: {torch.version.cuda}")
            logger.info(f"✅ GPU count: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                name = torch.cuda.get_device_name(i)
                memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
                logger.info(f"   GPU {i}: {name} ({memory:.1f} GB)")
        else:
            logger.warning("⚠️ CUDA not available")
        
        # Check training data
        data_dir = Path("data/training")
        required_files = ["train_dataset.csv", "validation_dataset.csv", "test_dataset.csv"]
        
        for file in required_files:
            if not (data_dir / file).exists():
                logger.error(f"❌ Missing training data: {data_dir / file}")
                return False
        
        logger.info("✅ All training data files found")
        return True
    
    def prepare_data_if_needed(self, csv_path: str = "data/raw/free_tweet_export.csv") -> bool:
        """Prepare training data if not already prepared"""
        data_dir = Path("data/training")
        
        if not data_dir.exists() or not (data_dir / "train_dataset.csv").exists():
            logger.info("Preparing training data...")
            
            if not Path(csv_path).exists():
                logger.error(f"❌ Raw data file not found: {csv_path}")
                return False
            
            results = self.data_prep_service.prepare_training_data(
                csv_path=csv_path,
                output_dir="data/training"
            )
            
            if not results['success']:
                logger.error(f"❌ Data preparation failed: {results['error']}")
                return False
            
            logger.info("✅ Data preparation completed")
            logger.info(f"   Total samples: {results['total_samples']}")
            logger.info(f"   Training: {results['splits']['train']} samples")
            logger.info(f"   Validation: {results['splits']['validation']} samples")
            logger.info(f"   Test: {results['splits']['test']} samples")
        
        return True
    
    async def run_training(self, output_dir: str = None) -> dict:
        """Run the complete training pipeline"""
        logger.info("🚀 Starting GPU training pipeline")
        start_time = datetime.now()
        
        try:
            # Check prerequisites
            if not self.check_prerequisites():
                return {'success': False, 'error': 'Prerequisites check failed'}
            
            # Prepare data if needed
            if not self.prepare_data_if_needed():
                return {'success': False, 'error': 'Data preparation failed'}
            
            # Run training
            logger.info("🔥 Starting model training...")
            results = await self.gpu_trainer.train_model(
                data_dir="data/training",
                output_dir=output_dir
            )
            
            if results['success']:
                end_time = datetime.now()
                duration = end_time - start_time
                
                logger.info("🎉 Training completed successfully!")
                logger.info(f"   Duration: {duration}")
                logger.info(f"   Model saved to: {results['model_path']}")
                logger.info(f"   Final train loss: {results.get('train_loss', 'N/A')}")
                logger.info(f"   Final eval loss: {results.get('eval_loss', 'N/A')}")
                
                results['duration'] = str(duration)
                results['start_time'] = start_time.isoformat()
                results['end_time'] = end_time.isoformat()
            else:
                logger.error(f"❌ Training failed: {results['error']}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Training pipeline failed: {e}")
            return {'success': False, 'error': str(e)}


def main():
    """Main training function"""
    parser = argparse.ArgumentParser(description="Train FreeMobilaChat model on GPU")
    parser.add_argument("--model", type=str, help="Model name to fine-tune")
    parser.add_argument("--output", type=str, help="Output directory for trained model")
    parser.add_argument("--data", type=str, default="data/raw/free_tweet_export.csv", 
                       help="Path to raw CSV data")
    parser.add_argument("--check-only", action="store_true", 
                       help="Only check prerequisites, don't train")
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = TrainingPipeline(model_name=args.model)
    
    if args.check_only:
        logger.info("🔍 Checking prerequisites only...")
        success = pipeline.check_prerequisites()
        if success:
            logger.info("✅ System ready for training!")
        else:
            logger.error("❌ System not ready for training")
        sys.exit(0 if success else 1)
    
    # Run training
    logger.info("🚀 FreeMobilaChat GPU Training")
    logger.info("=" * 60)
    logger.info(f"Model: {pipeline.model_name}")
    logger.info(f"Data: {args.data}")
    logger.info(f"Output: {args.output or config.gpu_training.output_dir}")
    logger.info("=" * 60)
    
    # Run async training
    results = asyncio.run(pipeline.run_training(output_dir=args.output))
    
    if results['success']:
        logger.info("\n🎉 Training completed successfully!")
        logger.info("Next steps:")
        logger.info("1. Test the model: python test_trained_model.py")
        logger.info("2. Compare with API models: python compare_models.py")
        logger.info("3. Deploy for inference: Update model_training.py to use local model")
    else:
        logger.error(f"\n❌ Training failed: {results['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
