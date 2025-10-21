"""
Analysis Results Service for Comprehensive Tweet Analysis Reporting
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import logging
import json
import asyncio
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

from ..models import TweetAnalyzed, SentimentType, CategoryType, PriorityLevel
from ..services.llm_analyzer import LLMAnalyzer, LLMProvider
from ..services.kpi_calculator import KPICalculator
from ..utils.database import DatabaseManager

logger = logging.getLogger(__name__)

class AnalysisResultsService:
    """Service for generating comprehensive analysis results and insights"""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        Initialize analysis results service
        
        Args:
            db_manager: Database manager for data access
        """
        self.db_manager = db_manager or DatabaseManager()
        self.kpi_calculator = KPICalculator()
        
    async def analyze_complete_dataset(self, csv_path: str = "data/raw/free_tweet_export.csv",
                                     provider: LLMProvider = LLMProvider.MISTRAL,
                                     max_tweets: int = 500) -> Dict[str, Any]:
        """
        Analyze the complete tweet dataset
        
        Args:
            csv_path: Path to tweet CSV file
            provider: LLM provider to use
            max_tweets: Maximum number of tweets to analyze
            
        Returns:
            Complete analysis results
        """
        logger.info(f"Starting complete dataset analysis with {provider.value}")
        
        try:
            # Load tweet data
            df = pd.read_csv(csv_path, encoding='utf-8')
            logger.info(f"Loaded {len(df)} tweets from {csv_path}")
            
            # Limit tweets if specified
            if max_tweets and len(df) > max_tweets:
                df = df.sample(n=max_tweets, random_state=42)
                logger.info(f"Sampled {max_tweets} tweets for analysis")
            
            # Initialize analyzer
            analyzer = LLMAnalyzer(provider=provider)
            
            # Analyze tweets
            analyzed_tweets = []
            successful_analyses = 0
            
            for idx, row in df.iterrows():
                try:
                    # Create TweetRaw object
                    from ..models import TweetRaw
                    tweet = TweetRaw(
                        tweet_id=str(row['tweet_id']),
                        author=row['author'],
                        text=row['text'],
                        date=pd.to_datetime(row['date'])
                    )
                    
                    # Analyze tweet
                    result = await analyzer.analyze_tweet(tweet)
                    
                    if result:
                        analyzed_tweets.append(result)
                        successful_analyses += 1
                    
                    # Rate limiting delay
                    await asyncio.sleep(2)
                    
                    if (idx + 1) % 25 == 0:
                        logger.info(f"Analyzed {idx + 1}/{len(df)} tweets ({successful_analyses} successful)")
                        
                except Exception as e:
                    logger.error(f"Error analyzing tweet {row.get('tweet_id', idx)}: {e}")
                    continue
            
            logger.info(f"Analysis completed: {successful_analyses}/{len(df)} tweets analyzed")
            
            # Calculate KPIs
            kpi_metrics = self.kpi_calculator.calculate_metrics(analyzed_tweets)
            
            # Generate comprehensive results
            results = await self.generate_comprehensive_results(
                analyzed_tweets, kpi_metrics, provider.value
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Complete dataset analysis failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def generate_comprehensive_results(self, analyzed_tweets: List[TweetAnalyzed],
                                           kpi_metrics: Any, provider_name: str) -> Dict[str, Any]:
        """
        Generate comprehensive analysis results
        
        Args:
            analyzed_tweets: List of analyzed tweets
            kpi_metrics: KPI metrics object
            provider_name: Name of LLM provider used
            
        Returns:
            Comprehensive results dictionary
        """
        logger.info("Generating comprehensive analysis results")
        
        # Convert tweets to DataFrame for analysis
        tweets_data = []
        for tweet in analyzed_tweets:
            tweets_data.append({
                'tweet_id': tweet.tweet_id,
                'author': tweet.author,
                'text': tweet.text,
                'date': tweet.date,
                'sentiment': tweet.sentiment.value,
                'sentiment_score': tweet.sentiment_score,
                'category': tweet.category.value,
                'priority': tweet.priority.value,
                'keywords': tweet.keywords,
                'is_urgent': tweet.is_urgent,
                'needs_response': tweet.needs_response,
                'estimated_resolution_time': tweet.estimated_resolution_time
            })
        
        df = pd.DataFrame(tweets_data)
        
        # Sentiment Analysis Results
        sentiment_results = self.analyze_sentiment_distribution(df)
        
        # Category Classification Results
        category_results = self.analyze_category_distribution(df)
        
        # Priority Assessment Results
        priority_results = self.analyze_priority_distribution(df)
        
        # Temporal Analysis
        temporal_results = self.analyze_temporal_patterns(df)
        
        # Author Analysis
        author_results = self.analyze_author_patterns(df)
        
        # Keyword Analysis
        keyword_results = self.analyze_keyword_patterns(df)
        
        # Generate insights
        insights = self.generate_insights(df, kpi_metrics)
        
        # Compile comprehensive results
        results = {
            'success': True,
            'analysis_date': datetime.now().isoformat(),
            'provider': provider_name,
            'total_tweets': len(analyzed_tweets),
            'analysis_summary': {
                'sentiment_distribution': sentiment_results,
                'category_distribution': category_results,
                'priority_distribution': priority_results,
                'temporal_patterns': temporal_results,
                'author_patterns': author_results,
                'keyword_patterns': keyword_results
            },
            'kpi_metrics': {
                'total_tweets': kpi_metrics.total_tweets,
                'critical_count': kpi_metrics.critical_count,
                'high_priority_count': kpi_metrics.high_priority_count,
                'tweets_needing_response': kpi_metrics.tweets_needing_response,
                'avg_estimated_resolution': kpi_metrics.avg_estimated_resolution
            },
            'insights_and_recommendations': insights
        }
        
        return results
    
    def analyze_sentiment_distribution(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze sentiment distribution and patterns"""
        sentiment_counts = df['sentiment'].value_counts()
        sentiment_percentages = (sentiment_counts / len(df) * 100).round(2)
        
        # Sentiment score statistics
        sentiment_stats = df.groupby('sentiment')['sentiment_score'].agg([
            'mean', 'std', 'min', 'max', 'count'
        ]).round(3)
        
        return {
            'distribution': sentiment_counts.to_dict(),
            'percentages': sentiment_percentages.to_dict(),
            'statistics': sentiment_stats.to_dict(),
            'avg_sentiment_score': df['sentiment_score'].mean(),
            'sentiment_score_std': df['sentiment_score'].std()
        }
    
    def analyze_category_distribution(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze category distribution and patterns"""
        category_counts = df['category'].value_counts()
        category_percentages = (category_counts / len(df) * 100).round(2)
        
        # Category by sentiment cross-analysis
        category_sentiment = pd.crosstab(df['category'], df['sentiment'], normalize='index') * 100
        
        # Average resolution time by category
        resolution_by_category = df.groupby('category')['estimated_resolution_time'].agg([
            'mean', 'median', 'std'
        ]).round(1)
        
        return {
            'distribution': category_counts.to_dict(),
            'percentages': category_percentages.to_dict(),
            'sentiment_breakdown': category_sentiment.to_dict(),
            'resolution_times': resolution_by_category.to_dict()
        }
    
    def analyze_priority_distribution(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze priority distribution and patterns"""
        priority_counts = df['priority'].value_counts()
        priority_percentages = (priority_counts / len(df) * 100).round(2)
        
        # Priority by category analysis
        priority_category = pd.crosstab(df['priority'], df['category'], normalize='index') * 100
        
        # Urgency analysis
        urgent_by_priority = df.groupby('priority')['is_urgent'].mean() * 100
        response_needed_by_priority = df.groupby('priority')['needs_response'].mean() * 100
        
        return {
            'distribution': priority_counts.to_dict(),
            'percentages': priority_percentages.to_dict(),
            'category_breakdown': priority_category.to_dict(),
            'urgency_rates': urgent_by_priority.to_dict(),
            'response_needed_rates': response_needed_by_priority.to_dict()
        }
    
    def analyze_temporal_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze temporal patterns in tweets"""
        df['hour'] = pd.to_datetime(df['date']).dt.hour
        df['day_of_week'] = pd.to_datetime(df['date']).dt.day_name()
        df['month'] = pd.to_datetime(df['date']).dt.month_name()
        
        # Hourly patterns
        hourly_counts = df['hour'].value_counts().sort_index()
        peak_hour = hourly_counts.idxmax()
        
        # Daily patterns
        daily_counts = df['day_of_week'].value_counts()
        
        # Monthly patterns
        monthly_counts = df['month'].value_counts()
        
        # Sentiment by time patterns
        hourly_sentiment = df.groupby('hour')['sentiment_score'].mean()
        
        return {
            'hourly_distribution': hourly_counts.to_dict(),
            'daily_distribution': daily_counts.to_dict(),
            'monthly_distribution': monthly_counts.to_dict(),
            'peak_hour': int(peak_hour),
            'hourly_sentiment_trend': hourly_sentiment.to_dict()
        }
    
    def analyze_author_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze author patterns and behaviors"""
        # Top authors by tweet count
        top_authors = df['author'].value_counts().head(10)
        
        # Author sentiment patterns
        author_sentiment = df.groupby('author')['sentiment_score'].agg([
            'mean', 'count'
        ]).sort_values('count', ascending=False).head(10)
        
        # Unique authors count
        unique_authors = df['author'].nunique()
        
        return {
            'total_unique_authors': unique_authors,
            'top_authors': top_authors.to_dict(),
            'author_sentiment_patterns': author_sentiment.to_dict(),
            'avg_tweets_per_author': len(df) / unique_authors
        }
    
    def analyze_keyword_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze keyword patterns and trends"""
        # Flatten all keywords
        all_keywords = []
        for keywords_list in df['keywords']:
            if isinstance(keywords_list, list):
                all_keywords.extend(keywords_list)
        
        # Most common keywords
        keyword_counts = Counter(all_keywords)
        top_keywords = dict(keyword_counts.most_common(20))
        
        # Keywords by sentiment
        keyword_sentiment = {}
        for _, row in df.iterrows():
            if isinstance(row['keywords'], list):
                for keyword in row['keywords']:
                    if keyword not in keyword_sentiment:
                        keyword_sentiment[keyword] = []
                    keyword_sentiment[keyword].append(row['sentiment_score'])
        
        # Average sentiment by keyword (for top keywords)
        keyword_avg_sentiment = {}
        for keyword in list(top_keywords.keys())[:10]:
            if keyword in keyword_sentiment:
                keyword_avg_sentiment[keyword] = np.mean(keyword_sentiment[keyword])
        
        return {
            'total_unique_keywords': len(keyword_counts),
            'top_keywords': top_keywords,
            'keyword_sentiment_scores': keyword_avg_sentiment,
            'avg_keywords_per_tweet': len(all_keywords) / len(df)
        }
    
    def generate_insights(self, df: pd.DataFrame, kpi_metrics: Any) -> Dict[str, List[str]]:
        """Generate actionable insights from the analysis"""
        insights = {
            'key_findings': [],
            'recommendations': [],
            'areas_of_concern': [],
            'positive_highlights': []
        }
        
        # Sentiment insights
        negative_pct = (df['sentiment'] == 'negative').mean() * 100
        if negative_pct > 40:
            insights['areas_of_concern'].append(
                f"High negative sentiment rate: {negative_pct:.1f}% of tweets are negative"
            )
        elif negative_pct < 20:
            insights['positive_highlights'].append(
                f"Low negative sentiment rate: Only {negative_pct:.1f}% of tweets are negative"
            )
        
        # Category insights
        top_category = df['category'].value_counts().index[0]
        top_category_pct = (df['category'] == top_category).mean() * 100
        insights['key_findings'].append(
            f"Most common issue category: {top_category} ({top_category_pct:.1f}% of tweets)"
        )
        
        # Priority insights
        critical_pct = (df['priority'] == 'critique').mean() * 100
        if critical_pct > 10:
            insights['areas_of_concern'].append(
                f"High critical priority rate: {critical_pct:.1f}% of tweets are critical"
            )
        
        # Response needs
        response_needed_pct = df['needs_response'].mean() * 100
        insights['key_findings'].append(
            f"Response needed for {response_needed_pct:.1f}% of tweets"
        )
        
        # Recommendations
        insights['recommendations'].extend([
            "Implement automated routing based on category classification",
            "Prioritize critical and high-priority tweets for faster response",
            "Monitor negative sentiment trends for early intervention",
            "Create category-specific response templates",
            "Track resolution times by category for SLA compliance"
        ])
        
        return insights
    
    async def save_analysis_results(self, results: Dict[str, Any], 
                                  output_dir: str = "data/results") -> str:
        """
        Save comprehensive analysis results
        
        Args:
            results: Analysis results dictionary
            output_dir: Output directory
            
        Returns:
            Path to saved results file
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save JSON results
        results_file = output_path / f"analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Analysis results saved: {results_file}")
        return str(results_file)

async def main():
    """Main function for testing analysis results"""
    import asyncio
    
    service = AnalysisResultsService()
    
    # Run complete analysis
    results = await service.analyze_complete_dataset(max_tweets=100)  # Limit for testing
    
    if results['success']:
        print("[SUCCESS] Complete analysis finished successfully!")
        print(f"[INFO] Total tweets analyzed: {results['total_tweets']}")
        print(f"[INFO] Sentiment distribution: {results['analysis_summary']['sentiment_distribution']['percentages']}")
        print(f"[INFO] Top category: {max(results['analysis_summary']['category_distribution']['percentages'], key=results['analysis_summary']['category_distribution']['percentages'].get)}")

        # Save results
        results_file = await service.save_analysis_results(results)
        print(f"[INFO] Results saved: {results_file}")
    else:
        print(f"[ERROR] Analysis failed: {results['error']}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
