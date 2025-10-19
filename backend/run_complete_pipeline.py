#!/usr/bin/env python3
"""
Complete Tweet Analysis Pipeline
Runs data preparation, model training, evaluation, and comprehensive analysis
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

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.services.data_preparation import DataPreparationService
from app.services.model_training import ModelTrainingService
from app.services.analysis_results import AnalysisResultsService
from app.utils.database import DatabaseManager
from app.services.llm_analyzer import LLMProvider

# Configure logging with UTF-8 encoding for Windows
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class CompletePipeline:
    """Complete tweet analysis pipeline orchestrator"""
    
    def __init__(self, provider: LLMProvider = LLMProvider.MISTRAL):
        """
        Initialize pipeline
        
        Args:
            provider: LLM provider to use
        """
        self.provider = provider
        self.db_manager = DatabaseManager(
            database_type=os.getenv("DATABASE_TYPE", "postgresql"),
            connection_string=os.getenv("DATABASE_URL")
        )
        
        # Initialize services
        self.data_prep_service = DataPreparationService(self.db_manager)
        self.training_service = ModelTrainingService(self.db_manager)
        self.analysis_service = AnalysisResultsService(self.db_manager)
        
        logger.info(f"Pipeline initialized with {provider.value} provider")
    
    async def run_phase_1_data_preparation(self, csv_path: str = "data/raw/free_tweet_export.csv") -> dict:
        """
        Phase 1: Data Preparation and Dataset Creation
        
        Args:
            csv_path: Path to input CSV file
            
        Returns:
            Data preparation results
        """
        logger.info("[PHASE 1] Starting Data Preparation")

        try:
            # Prepare training data
            results = self.data_prep_service.prepare_training_data(
                csv_path=csv_path,
                output_dir="data/training"
            )

            if results['success']:
                logger.info("[SUCCESS] Phase 1 completed successfully")
                logger.info(f"[INFO] Total samples: {results['total_samples']}")
                logger.info(f"[INFO] Training: {results['splits']['train']} samples")
                logger.info(f"[INFO] Validation: {results['splits']['validation']} samples")
                logger.info(f"[INFO] Test: {results['splits']['test']} samples")
            else:
                logger.error(f"[ERROR] Phase 1 failed: {results['error']}")

            return results

        except Exception as e:
            logger.error(f"[ERROR] Phase 1 failed with exception: {e}")
            return {'success': False, 'error': str(e)}
    
    async def run_phase_2_model_evaluation(self) -> dict:
        """
        Phase 2: Model Training and Evaluation
        
        Returns:
            Model evaluation results
        """
        logger.info("[PHASE 2] Starting Model Training and Evaluation")

        try:
            # Run comprehensive evaluation
            results = await self.training_service.run_comprehensive_evaluation(
                data_dir="data/training",
                output_dir="data/results"
            )

            if results['success']:
                logger.info("[SUCCESS] Phase 2 completed successfully")
                logger.info(f"[INFO] Test samples: {results['test_samples']}")
                logger.info(f"[INFO] Average accuracy: {results['metrics']['overall']['avg_accuracy']:.3f}")
                logger.info(f"[INFO] Average F1-score: {results['metrics']['overall']['avg_f1']:.3f}")
                logger.info(f"[INFO] Report: {results['files']['report']}")
            else:
                logger.error(f"[ERROR] Phase 2 failed: {results['error']}")

            return results

        except Exception as e:
            logger.error(f"[ERROR] Phase 2 failed with exception: {e}")
            return {'success': False, 'error': str(e)}
    
    async def run_phase_3_comprehensive_analysis(self, csv_path: str, max_tweets: int = 500) -> dict:
        """
        Phase 3: Comprehensive Analysis and Reporting

        Args:
            csv_path: Path to the CSV file to analyze
            max_tweets: Maximum number of tweets to analyze

        Returns:
            Comprehensive analysis results
        """
        logger.info("[PHASE 3] Starting Comprehensive Analysis")

        try:
            # Run complete dataset analysis
            results = await self.analysis_service.analyze_complete_dataset(
                csv_path=csv_path,
                provider=self.provider,
                max_tweets=max_tweets
            )

            if results['success']:
                logger.info("[SUCCESS] Phase 3 completed successfully")
                logger.info(f"[INFO] Total tweets analyzed: {results['total_tweets']}")
                logger.info(f"[INFO] Sentiment distribution: {results['analysis_summary']['sentiment_distribution']['percentages']}")

                # Save results
                results_file = await self.analysis_service.save_analysis_results(results)
                logger.info(f"[INFO] Results saved: {results_file}")

                results['results_file'] = results_file
            else:
                logger.error(f"[ERROR] Phase 3 failed: {results['error']}")

            return results

        except Exception as e:
            logger.error(f"[ERROR] Phase 3 failed with exception: {e}")
            return {'success': False, 'error': str(e)}
    
    async def run_complete_pipeline(self, csv_path: str = "data/raw/free_tweet_export.csv",
                                  max_tweets: int = 500) -> dict:
        """
        Run the complete pipeline
        
        Args:
            csv_path: Path to input CSV file
            max_tweets: Maximum number of tweets to analyze in Phase 3
            
        Returns:
            Complete pipeline results
        """
        logger.info("[PIPELINE] Starting Complete Tweet Analysis Pipeline")
        start_time = datetime.now()
        
        pipeline_results = {
            'start_time': start_time,
            'phases': {},
            'overall_success': True
        }
        
        try:
            # Initialize database (skip for now - not implemented)
            # await self.db_manager.initialize()
            
            # Phase 1: Data Preparation
            phase1_results = await self.run_phase_1_data_preparation(csv_path)
            pipeline_results['phases']['data_preparation'] = phase1_results
            
            if not phase1_results['success']:
                pipeline_results['overall_success'] = False
                logger.error("[ERROR] Pipeline stopped due to Phase 1 failure")
                return pipeline_results
            
            # Phase 2: Model Evaluation
            phase2_results = await self.run_phase_2_model_evaluation()
            pipeline_results['phases']['model_evaluation'] = phase2_results
            
            if not phase2_results['success']:
                logger.warning("[WARNING] Phase 2 failed, continuing with Phase 3")

            # Phase 3: Comprehensive Analysis
            phase3_results = await self.run_phase_3_comprehensive_analysis(csv_path, max_tweets)
            pipeline_results['phases']['comprehensive_analysis'] = phase3_results

            if not phase3_results['success']:
                pipeline_results['overall_success'] = False
                logger.error("[ERROR] Phase 3 failed")

            # Calculate total execution time
            end_time = datetime.now()
            pipeline_results['end_time'] = end_time
            pipeline_results['total_duration'] = (end_time - start_time).total_seconds()

            if pipeline_results['overall_success']:
                logger.info("[SUCCESS] Complete pipeline executed successfully!")
                logger.info(f"[INFO] Total execution time: {pipeline_results['total_duration']:.1f} seconds")
            else:
                logger.error("[ERROR] Pipeline completed with errors")

            return pipeline_results

        except Exception as e:
            logger.error(f"[ERROR] Pipeline failed with critical error: {e}")
            pipeline_results['overall_success'] = False
            pipeline_results['critical_error'] = str(e)
            return pipeline_results
        
        finally:
            # Close database connections (skip for now)
            try:
                # await self.db_manager.close()
                pass
            except:
                pass
    
    def print_pipeline_summary(self, results: dict):
        """Print a summary of pipeline results"""
        print("\n" + "="*80)
        print("TWEET ANALYSIS PIPELINE SUMMARY")
        print("="*80)

        if results['overall_success']:
            print("[SUCCESS] Status: SUCCESS")
        else:
            print("[FAILED] Status: FAILED")

        print(f"[INFO] Duration: {results.get('total_duration', 0):.1f} seconds")
        print(f"[INFO] Started: {results['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")

        if 'end_time' in results:
            print(f"[INFO] Ended: {results['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")

        print("\nPHASE RESULTS:")

        # Phase 1: Data Preparation
        if 'data_preparation' in results['phases']:
            phase1 = results['phases']['data_preparation']
            status = "[SUCCESS]" if phase1['success'] else "[FAILED]"
            print(f"  {status} Phase 1 - Data Preparation")
            if phase1['success']:
                print(f"      [INFO] Total samples: {phase1['total_samples']}")
                print(f"      [INFO] Training: {phase1['splits']['train']}")
                print(f"      [INFO] Validation: {phase1['splits']['validation']}")
                print(f"      [INFO] Test: {phase1['splits']['test']}")

        # Phase 2: Model Evaluation
        if 'model_evaluation' in results['phases']:
            phase2 = results['phases']['model_evaluation']
            status = "[SUCCESS]" if phase2['success'] else "[FAILED]"
            print(f"  {status} Phase 2 - Model Evaluation")
            if phase2['success']:
                print(f"      [INFO] Test samples: {phase2['test_samples']}")
                print(f"      [INFO] Avg accuracy: {phase2['metrics']['overall']['avg_accuracy']:.3f}")
                print(f"      [INFO] Avg F1-score: {phase2['metrics']['overall']['avg_f1']:.3f}")

        # Phase 3: Comprehensive Analysis
        if 'comprehensive_analysis' in results['phases']:
            phase3 = results['phases']['comprehensive_analysis']
            status = "[SUCCESS]" if phase3['success'] else "[FAILED]"
            print(f"  {status} Phase 3 - Comprehensive Analysis")
            if phase3['success']:
                print(f"      [INFO] Tweets analyzed: {phase3['total_tweets']}")
                if 'results_file' in phase3:
                    print(f"      [INFO] Results file: {phase3['results_file']}")

        print("\n" + "="*80)


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Run complete tweet analysis pipeline')
    parser.add_argument('--csv-path', default='data/raw/free_tweet_export.csv',
                       help='Path to input CSV file')
    parser.add_argument('--max-tweets', type=int, default=500,
                       help='Maximum number of tweets to analyze in Phase 3')
    parser.add_argument('--provider', choices=['mistral', 'ollama', 'openai', 'anthropic'],
                       default='mistral', help='LLM provider to use')
    
    args = parser.parse_args()
    
    # Convert provider string to enum
    provider_map = {
        'mistral': LLMProvider.MISTRAL,
        'ollama': LLMProvider.OLLAMA,
        'openai': LLMProvider.OPENAI,
        'anthropic': LLMProvider.ANTHROPIC
    }
    
    provider = provider_map[args.provider]
    
    # Initialize and run pipeline
    pipeline = CompletePipeline(provider=provider)
    
    results = await pipeline.run_complete_pipeline(
        csv_path=args.csv_path,
        max_tweets=args.max_tweets
    )
    
    # Print summary
    pipeline.print_pipeline_summary(results)
    
    # Exit with appropriate code
    sys.exit(0 if results['overall_success'] else 1)


if __name__ == "__main__":
    asyncio.run(main())
