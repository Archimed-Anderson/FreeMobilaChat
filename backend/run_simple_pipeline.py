#!/usr/bin/env python3
"""
Simple Tweet Analysis Pipeline Demo
Windows-compatible version without emojis
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from datetime import datetime
import argparse

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
    print(f"Environment loaded. Mistral API key configured: {bool(os.getenv('MISTRAL_API_KEY'))}")
except ImportError:
    print("Warning: python-dotenv not installed. Environment variables may not be loaded.")

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.services.data_preparation import DataPreparationService
from app.services.analysis_results import AnalysisResultsService
from app.services.llm_analyzer import LLMProvider

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class SimplePipeline:
    """Simple tweet analysis pipeline for demonstration"""
    
    def __init__(self, provider: LLMProvider = LLMProvider.MISTRAL):
        """Initialize pipeline"""
        self.provider = provider
        self.data_prep_service = DataPreparationService()
        self.analysis_service = AnalysisResultsService()
        
        logger.info(f"Pipeline initialized with {provider.value} provider")
    
    async def run_data_preparation(self, csv_path: str = "../data/raw/free_tweet_export.csv") -> dict:
        """Phase 1: Data Preparation"""
        logger.info("Starting Phase 1: Data Preparation")
        
        try:
            results = self.data_prep_service.prepare_training_data(
                csv_path=csv_path,
                output_dir="../data/training"
            )
            
            if results['success']:
                logger.info("Phase 1 completed successfully")
                logger.info(f"Total samples: {results['total_samples']}")
                logger.info(f"Training: {results['splits']['train']} samples")
                logger.info(f"Validation: {results['splits']['validation']} samples")
                logger.info(f"Test: {results['splits']['test']} samples")
            else:
                logger.error(f"Phase 1 failed: {results['error']}")
            
            return results
            
        except Exception as e:
            logger.error(f"Phase 1 failed with exception: {e}")
            return {'success': False, 'error': str(e)}
    
    async def run_analysis(self, max_tweets: int = 20) -> dict:
        """Phase 2: Tweet Analysis"""
        logger.info(f"Starting Phase 2: Tweet Analysis (max {max_tweets} tweets)")
        
        try:
            results = await self.analysis_service.analyze_complete_dataset(
                csv_path="../data/raw/free_tweet_export.csv",
                provider=self.provider,
                max_tweets=max_tweets
            )
            
            if results['success']:
                logger.info("Phase 2 completed successfully")
                logger.info(f"Total tweets analyzed: {results['total_tweets']}")
                
                # Show sentiment distribution
                sentiment_dist = results['analysis_summary']['sentiment_distribution']['percentages']
                logger.info(f"Sentiment distribution: {sentiment_dist}")
                
                # Save results
                results_file = await self.analysis_service.save_analysis_results(results)
                logger.info(f"Results saved: {results_file}")
                
                results['results_file'] = results_file
            else:
                logger.error(f"Phase 2 failed: {results['error']}")
            
            return results
            
        except Exception as e:
            logger.error(f"Phase 2 failed with exception: {e}")
            return {'success': False, 'error': str(e)}
    
    async def run_complete_demo(self, csv_path: str = "../data/raw/free_tweet_export.csv",
                               max_tweets: int = 20) -> dict:
        """Run complete pipeline demo"""
        logger.info("Starting Complete Tweet Analysis Pipeline Demo")
        start_time = datetime.now()
        
        demo_results = {
            'start_time': start_time,
            'phases': {},
            'overall_success': True
        }
        
        try:
            # Phase 1: Data Preparation
            phase1_results = await self.run_data_preparation(csv_path)
            demo_results['phases']['data_preparation'] = phase1_results
            
            if not phase1_results['success']:
                demo_results['overall_success'] = False
                logger.error("Demo stopped due to Phase 1 failure")
                return demo_results
            
            # Phase 2: Tweet Analysis
            phase2_results = await self.run_analysis(max_tweets)
            demo_results['phases']['analysis'] = phase2_results
            
            if not phase2_results['success']:
                demo_results['overall_success'] = False
                logger.error("Phase 2 failed")
            
            # Calculate total execution time
            end_time = datetime.now()
            demo_results['end_time'] = end_time
            demo_results['total_duration'] = (end_time - start_time).total_seconds()
            
            if demo_results['overall_success']:
                logger.info("Complete demo executed successfully!")
                logger.info(f"Total execution time: {demo_results['total_duration']:.1f} seconds")
            else:
                logger.error("Demo completed with errors")
            
            return demo_results
            
        except Exception as e:
            logger.error(f"Demo failed with critical error: {e}")
            demo_results['overall_success'] = False
            demo_results['critical_error'] = str(e)
            return demo_results
    
    def print_demo_summary(self, results: dict):
        """Print a summary of demo results"""
        print("\n" + "="*80)
        print("TWEET ANALYSIS PIPELINE DEMO SUMMARY")
        print("="*80)
        
        if results['overall_success']:
            print("Status: SUCCESS")
        else:
            print("Status: FAILED")
        
        print(f"Duration: {results.get('total_duration', 0):.1f} seconds")
        print(f"Started: {results['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        if 'end_time' in results:
            print(f"Ended: {results['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\nPHASE RESULTS:")
        
        # Phase 1: Data Preparation
        if 'data_preparation' in results['phases']:
            phase1 = results['phases']['data_preparation']
            status = "SUCCESS" if phase1['success'] else "FAILED"
            print(f"  Phase 1 - Data Preparation: {status}")
            if phase1['success']:
                print(f"      Total samples: {phase1['total_samples']}")
                print(f"      Training: {phase1['splits']['train']}")
                print(f"      Validation: {phase1['splits']['validation']}")
                print(f"      Test: {phase1['splits']['test']}")
        
        # Phase 2: Analysis
        if 'analysis' in results['phases']:
            phase2 = results['phases']['analysis']
            status = "SUCCESS" if phase2['success'] else "FAILED"
            print(f"  Phase 2 - Tweet Analysis: {status}")
            if phase2['success']:
                print(f"      Tweets analyzed: {phase2['total_tweets']}")
                if 'results_file' in phase2:
                    print(f"      Results file: {phase2['results_file']}")
        
        print("\n" + "="*80)

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Run simple tweet analysis pipeline demo')
    parser.add_argument('--csv-path', default='../data/raw/free_tweet_export.csv',
                       help='Path to input CSV file')
    parser.add_argument('--max-tweets', type=int, default=20,
                       help='Maximum number of tweets to analyze')
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
    pipeline = SimplePipeline(provider=provider)
    
    results = await pipeline.run_complete_demo(
        csv_path=args.csv_path,
        max_tweets=args.max_tweets
    )
    
    # Print summary
    pipeline.print_demo_summary(results)
    
    # Exit with appropriate code
    sys.exit(0 if results['overall_success'] else 1)

if __name__ == "__main__":
    asyncio.run(main())
