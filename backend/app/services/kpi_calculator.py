"""
KPI Calculator for tweet analysis dashboard
Calculates comprehensive metrics and KPIs for business intelligence
"""

from typing import List, Dict, Any, Tuple, Optional
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import logging
from statistics import mean, median, stdev

from ..models import TweetAnalyzed, KPIMetrics, SentimentType, CategoryType, PriorityLevel

logger = logging.getLogger(__name__)


class KPICalculator:
    """
    Calcul métriques dashboard
    Comprehensive KPI calculation for tweet analysis dashboard
    """
    
    def __init__(self):
        """Initialize KPI calculator"""
        self.priority_weights = {
            PriorityLevel.CRITICAL: 4,
            PriorityLevel.HIGH: 3,
            PriorityLevel.MEDIUM: 2,
            PriorityLevel.LOW: 1
        }
    
    def calculate_metrics(self, tweets: List[TweetAnalyzed]) -> KPIMetrics:
        """
        Génération KPIs complets
        Generate comprehensive KPIs from analyzed tweets
        
        Args:
            tweets: List of analyzed tweets
            
        Returns:
            KPIMetrics object with all calculated metrics
            
        Raises:
            ValueError: If no tweets provided
        """
        if not tweets:
            raise ValueError("Aucun tweet à analyser")
        
        logger.info(f"Calculating KPIs for {len(tweets)} tweets")
        
        # Basic metrics
        total_tweets = len(tweets)
        date_range = (
            min(tweet.date for tweet in tweets),
            max(tweet.date for tweet in tweets)
        )
        
        # Sentiment analysis
        sentiment_distribution, sentiment_percentages = self._calculate_sentiment_metrics(tweets)
        
        # Category analysis
        category_distribution = self._calculate_category_metrics(tweets)
        
        # Priority analysis
        priority_metrics = self._calculate_priority_metrics(tweets)
        
        # Response metrics
        response_metrics = self._calculate_response_metrics(tweets)
        
        # Temporal analysis
        temporal_metrics = self._calculate_temporal_metrics(tweets)
        
        # Create KPIMetrics object
        kpis = KPIMetrics(
            total_tweets=total_tweets,
            date_range=date_range,
            sentiment_distribution=sentiment_distribution,
            sentiment_percentages=sentiment_percentages,
            category_distribution=category_distribution,
            critical_count=priority_metrics['critical_count'],
            high_priority_count=priority_metrics['high_priority_count'],
            avg_priority_score=priority_metrics['avg_priority_score'],
            tweets_needing_response=response_metrics['tweets_needing_response'],
            avg_estimated_resolution=response_metrics['avg_estimated_resolution'],
            tweets_per_hour=temporal_metrics['tweets_per_hour'],
            peak_hour=temporal_metrics['peak_hour']
        )
        
        logger.info("KPI calculation completed successfully")
        return kpis
    
    def _calculate_sentiment_metrics(self, tweets: List[TweetAnalyzed]) -> Tuple[Dict[SentimentType, int], Dict[SentimentType, float]]:
        """Calculate sentiment distribution and percentages"""
        sentiments = [tweet.sentiment for tweet in tweets]
        sentiment_counts = Counter(sentiments)
        total = len(tweets)
        
        # Ensure all sentiment types are represented
        sentiment_distribution = {}
        sentiment_percentages = {}
        
        for sentiment_type in SentimentType:
            count = sentiment_counts.get(sentiment_type, 0)
            sentiment_distribution[sentiment_type] = count
            sentiment_percentages[sentiment_type] = (count / total * 100) if total > 0 else 0.0
        
        return sentiment_distribution, sentiment_percentages
    
    def _calculate_category_metrics(self, tweets: List[TweetAnalyzed]) -> Dict[CategoryType, int]:
        """Calculate category distribution"""
        categories = [tweet.category for tweet in tweets]
        category_counts = Counter(categories)
        
        # Ensure all category types are represented
        category_distribution = {}
        for category_type in CategoryType:
            category_distribution[category_type] = category_counts.get(category_type, 0)
        
        return category_distribution
    
    def _calculate_priority_metrics(self, tweets: List[TweetAnalyzed]) -> Dict[str, Any]:
        """Calculate priority-related metrics"""
        priorities = [tweet.priority for tweet in tweets]
        priority_counts = Counter(priorities)
        
        critical_count = priority_counts.get(PriorityLevel.CRITICAL, 0)
        high_priority_count = priority_counts.get(PriorityLevel.HIGH, 0)
        
        # Calculate weighted average priority score
        total_weight = sum(self.priority_weights[priority] for priority in priorities)
        avg_priority_score = total_weight / len(tweets) if tweets else 0.0
        
        return {
            'critical_count': critical_count,
            'high_priority_count': high_priority_count,
            'avg_priority_score': avg_priority_score,
            'priority_distribution': dict(priority_counts)
        }
    
    def _calculate_response_metrics(self, tweets: List[TweetAnalyzed]) -> Dict[str, Any]:
        """Calculate response-related metrics"""
        tweets_needing_response = sum(1 for tweet in tweets if tweet.needs_response)
        urgent_tweets = sum(1 for tweet in tweets if tweet.is_urgent)
        
        # Calculate average resolution time
        resolution_times = [
            tweet.estimated_resolution_time 
            for tweet in tweets 
            if tweet.estimated_resolution_time is not None
        ]
        
        avg_estimated_resolution = mean(resolution_times) if resolution_times else 0.0
        median_resolution_time = median(resolution_times) if resolution_times else 0.0
        
        return {
            'tweets_needing_response': tweets_needing_response,
            'urgent_tweets': urgent_tweets,
            'avg_estimated_resolution': avg_estimated_resolution,
            'median_resolution_time': median_resolution_time,
            'response_rate_percentage': (tweets_needing_response / len(tweets) * 100) if tweets else 0.0
        }
    
    def _calculate_temporal_metrics(self, tweets: List[TweetAnalyzed]) -> Dict[str, Any]:
        """Calculate temporal analysis metrics"""
        # Tweets per hour
        hours = [tweet.date.hour for tweet in tweets]
        tweets_per_hour = Counter(hours)
        
        # Ensure all hours are represented
        for hour in range(24):
            if hour not in tweets_per_hour:
                tweets_per_hour[hour] = 0
        
        # Find peak hour
        peak_hour = max(tweets_per_hour, key=tweets_per_hour.get) if tweets_per_hour else 0
        
        # Daily distribution
        dates = [tweet.date.date() for tweet in tweets]
        tweets_per_day = Counter(dates)
        
        return {
            'tweets_per_hour': dict(tweets_per_hour),
            'peak_hour': peak_hour,
            'tweets_per_day': {str(date): count for date, count in tweets_per_day.items()}
        }
    
    def calculate_advanced_metrics(self, tweets: List[TweetAnalyzed]) -> Dict[str, Any]:
        """
        Calculate advanced analytics metrics
        
        Args:
            tweets: List of analyzed tweets
            
        Returns:
            Dictionary with advanced metrics
        """
        if not tweets:
            return {}
        
        logger.info("Calculating advanced metrics")
        
        # Sentiment analysis
        sentiment_scores = [tweet.sentiment_score for tweet in tweets]
        sentiment_stats = {
            'avg_sentiment_score': mean(sentiment_scores),
            'median_sentiment_score': median(sentiment_scores),
            'sentiment_std_dev': stdev(sentiment_scores) if len(sentiment_scores) > 1 else 0.0,
            'sentiment_range': max(sentiment_scores) - min(sentiment_scores)
        }
        
        # Author analysis
        authors = [tweet.author for tweet in tweets]
        author_counts = Counter(authors)
        top_authors = author_counts.most_common(10)
        
        # Keyword analysis
        all_keywords = []
        for tweet in tweets:
            all_keywords.extend(tweet.keywords)
        
        keyword_counts = Counter(all_keywords)
        top_keywords = keyword_counts.most_common(20)
        
        # Hashtag and mention analysis
        all_hashtags = []
        all_mentions = []
        for tweet in tweets:
            all_hashtags.extend(tweet.hashtags)
            all_mentions.extend(tweet.mentions)
        
        hashtag_counts = Counter(all_hashtags)
        mention_counts = Counter(all_mentions)
        
        # Urgency analysis
        urgent_by_category = defaultdict(int)
        urgent_by_sentiment = defaultdict(int)
        
        for tweet in tweets:
            if tweet.is_urgent:
                urgent_by_category[tweet.category] += 1
                urgent_by_sentiment[tweet.sentiment] += 1
        
        # Resolution time analysis by category
        resolution_by_category = defaultdict(list)
        for tweet in tweets:
            if tweet.estimated_resolution_time:
                resolution_by_category[tweet.category].append(tweet.estimated_resolution_time)
        
        avg_resolution_by_category = {
            category: mean(times) if times else 0.0
            for category, times in resolution_by_category.items()
        }
        
        return {
            'sentiment_statistics': sentiment_stats,
            'top_authors': top_authors,
            'top_keywords': top_keywords,
            'top_hashtags': hashtag_counts.most_common(10),
            'top_mentions': mention_counts.most_common(10),
            'urgency_by_category': dict(urgent_by_category),
            'urgency_by_sentiment': dict(urgent_by_sentiment),
            'avg_resolution_by_category': avg_resolution_by_category,
            'total_unique_authors': len(set(authors)),
            'total_unique_keywords': len(set(all_keywords)),
            'avg_keywords_per_tweet': len(all_keywords) / len(tweets) if tweets else 0.0
        }
    
    def calculate_time_series_metrics(self, tweets: List[TweetAnalyzed], 
                                    interval: str = 'hour') -> Dict[str, Any]:
        """
        Calculate time series metrics for trend analysis
        
        Args:
            tweets: List of analyzed tweets
            interval: Time interval ('hour', 'day', 'week')
            
        Returns:
            Time series data for visualization
        """
        if not tweets:
            return {}
        
        logger.info(f"Calculating time series metrics with {interval} interval")
        
        # Group tweets by time interval
        time_groups = defaultdict(list)
        
        for tweet in tweets:
            if interval == 'hour':
                key = tweet.date.replace(minute=0, second=0, microsecond=0)
            elif interval == 'day':
                key = tweet.date.replace(hour=0, minute=0, second=0, microsecond=0)
            elif interval == 'week':
                # Start of week (Monday)
                days_since_monday = tweet.date.weekday()
                key = tweet.date.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_since_monday)
            else:
                raise ValueError(f"Unsupported interval: {interval}")
            
            time_groups[key].append(tweet)
        
        # Calculate metrics for each time period
        time_series = {}
        for timestamp, period_tweets in time_groups.items():
            period_metrics = {
                'timestamp': timestamp.isoformat(),
                'total_tweets': len(period_tweets),
                'sentiment_distribution': dict(Counter(t.sentiment for t in period_tweets)),
                'category_distribution': dict(Counter(t.category for t in period_tweets)),
                'priority_distribution': dict(Counter(t.priority for t in period_tweets)),
                'urgent_count': sum(1 for t in period_tweets if t.is_urgent),
                'avg_sentiment_score': mean([t.sentiment_score for t in period_tweets]),
                'response_needed_count': sum(1 for t in period_tweets if t.needs_response)
            }
            time_series[timestamp.isoformat()] = period_metrics
        
        return {
            'interval': interval,
            'time_series': time_series,
            'total_periods': len(time_series)
        }
    
    def calculate_comparative_metrics(self, current_tweets: List[TweetAnalyzed], 
                                    previous_tweets: List[TweetAnalyzed]) -> Dict[str, Any]:
        """
        Calculate comparative metrics between two periods
        
        Args:
            current_tweets: Current period tweets
            previous_tweets: Previous period tweets
            
        Returns:
            Comparative analysis metrics
        """
        if not current_tweets or not previous_tweets:
            return {}
        
        logger.info("Calculating comparative metrics")
        
        # Calculate basic metrics for both periods
        current_kpis = self.calculate_metrics(current_tweets)
        previous_kpis = self.calculate_metrics(previous_tweets)
        
        # Calculate changes
        volume_change = len(current_tweets) - len(previous_tweets)
        volume_change_pct = (volume_change / len(previous_tweets) * 100) if previous_tweets else 0.0
        
        # Sentiment changes
        sentiment_changes = {}
        for sentiment in SentimentType:
            current_pct = current_kpis.sentiment_percentages.get(sentiment, 0.0)
            previous_pct = previous_kpis.sentiment_percentages.get(sentiment, 0.0)
            sentiment_changes[sentiment] = current_pct - previous_pct
        
        # Priority changes
        critical_change = current_kpis.critical_count - previous_kpis.critical_count
        high_priority_change = current_kpis.high_priority_count - previous_kpis.high_priority_count
        
        # Response metrics changes
        response_change = current_kpis.tweets_needing_response - previous_kpis.tweets_needing_response
        resolution_time_change = current_kpis.avg_estimated_resolution - previous_kpis.avg_estimated_resolution
        
        return {
            'volume_change': volume_change,
            'volume_change_percentage': volume_change_pct,
            'sentiment_changes': sentiment_changes,
            'critical_tweets_change': critical_change,
            'high_priority_change': high_priority_change,
            'response_needed_change': response_change,
            'avg_resolution_time_change': resolution_time_change,
            'comparison_summary': {
                'current_period_tweets': len(current_tweets),
                'previous_period_tweets': len(previous_tweets),
                'overall_trend': 'improving' if sentiment_changes.get(SentimentType.POSITIVE, 0) > 0 else 'declining'
            }
        }
    
    def generate_insights(self, tweets: List[TweetAnalyzed]) -> List[str]:
        """
        Generate business insights from tweet analysis
        
        Args:
            tweets: List of analyzed tweets
            
        Returns:
            List of insight strings
        """
        if not tweets:
            return ["Aucune donnée disponible pour générer des insights"]
        
        insights = []
        
        # Calculate basic metrics
        kpis = self.calculate_metrics(tweets)
        advanced = self.calculate_advanced_metrics(tweets)
        
        # Volume insights
        insights.append(f"Analyse de {kpis.total_tweets} tweets sur la période")
        
        # Sentiment insights
        negative_pct = kpis.sentiment_percentages.get(SentimentType.NEGATIVE, 0)
        if negative_pct > 50:
            insights.append(f"⚠️ Taux de sentiment négatif élevé: {negative_pct:.1f}%")
        elif negative_pct < 20:
            insights.append(f"✅ Sentiment globalement positif: {negative_pct:.1f}% de tweets négatifs")
        
        # Priority insights
        if kpis.critical_count > 0:
            insights.append(f"🚨 {kpis.critical_count} tweets critiques nécessitent une attention immédiate")
        
        # Response insights
        response_rate = (kpis.tweets_needing_response / kpis.total_tweets * 100)
        insights.append(f"📞 {response_rate:.1f}% des tweets nécessitent une réponse")
        
        # Temporal insights
        insights.append(f"📈 Pic d'activité à {kpis.peak_hour}h")
        
        # Category insights
        top_category = max(kpis.category_distribution, key=kpis.category_distribution.get)
        top_category_count = kpis.category_distribution[top_category]
        insights.append(f"🏷️ Catégorie principale: {top_category.value} ({top_category_count} tweets)")
        
        return insights
