"""
Cache persistence utility for development mode
Provides file-based persistence for in-memory caches to survive server reloads
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, UTC
import pandas as pd

from ..models import TweetAnalyzed, AnalysisLog

logger = logging.getLogger(__name__)

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime and Pandas Timestamp objects"""

    def default(self, obj):
        # Handle Pandas Timestamp
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()

        # Handle Python datetime
        if isinstance(obj, datetime):
            return obj.isoformat()

        # Handle other datetime-like objects
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()

        # Handle numpy datetime64
        if hasattr(obj, 'astype') and 'datetime' in str(type(obj)):
            return pd.Timestamp(obj).isoformat()

        # Fallback to string representation
        return str(obj)

def safe_datetime_convert(obj):
    """Safely convert datetime-like objects to ISO strings"""
    if obj is None:
        return None

    # Handle Pandas Timestamp
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()

    # Handle Python datetime
    if isinstance(obj, datetime):
        return obj.isoformat()

    # Handle string that might be datetime
    if isinstance(obj, str):
        return obj

    # Handle other datetime-like objects
    if hasattr(obj, 'isoformat'):
        try:
            return obj.isoformat()
        except:
            pass

    # Handle numpy datetime64
    if hasattr(obj, 'astype') and 'datetime' in str(type(obj)):
        try:
            return pd.Timestamp(obj).isoformat()
        except:
            pass

    # Fallback to string representation
    return str(obj)

class CachePersistence:
    """Handles persistence of cache data to disk"""
    
    def __init__(self, cache_dir: str = "cache"):
        """
        Initialize cache persistence
        
        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        self.tweets_cache_file = self.cache_dir / "analyzed_tweets_cache.json"
        self.logs_cache_file = self.cache_dir / "analysis_logs_cache.json"
        
        logger.info(f"Cache persistence initialized: {self.cache_dir}")
    
    def save_tweets_cache(self, cache: Dict[str, List[TweetAnalyzed]]) -> bool:
        """
        Save analyzed tweets cache to disk

        Args:
            cache: Dictionary of batch_id -> List[TweetAnalyzed]

        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert TweetAnalyzed objects to dictionaries with proper serialization
            serializable_cache = {}
            for batch_id, tweets in cache.items():
                tweet_dicts = []
                for tweet in tweets:
                    tweet_dict = tweet.model_dump()

                    # Safely convert all datetime-like fields
                    for key, value in tweet_dict.items():
                        if value is not None:
                            tweet_dict[key] = safe_datetime_convert(value)

                    tweet_dicts.append(tweet_dict)
                serializable_cache[batch_id] = tweet_dicts

            # Add metadata
            cache_data = {
                "saved_at": datetime.now(UTC).isoformat(),
                "cache": serializable_cache
            }

            with open(self.tweets_cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False, cls=DateTimeEncoder)

            logger.info(f"Saved tweets cache: {len(cache)} batches")
            return True

        except Exception as e:
            logger.error(f"Failed to save tweets cache: {e}")
            return False
    
    def load_tweets_cache(self) -> Dict[str, List[TweetAnalyzed]]:
        """
        Load analyzed tweets cache from disk

        Returns:
            Dictionary of batch_id -> List[TweetAnalyzed]
        """
        try:
            if not self.tweets_cache_file.exists():
                logger.info("No tweets cache file found")
                return {}

            with open(self.tweets_cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            # Convert dictionaries back to TweetAnalyzed objects
            cache = {}
            for batch_id, tweets_data in cache_data.get("cache", {}).items():
                tweets = []
                for tweet_data in tweets_data:
                    # Convert date string back to datetime if needed
                    if 'date' in tweet_data and isinstance(tweet_data['date'], str):
                        try:
                            from datetime import datetime, UTC
                            tweet_data['date'] = datetime.fromisoformat(tweet_data['date'].replace('Z', '+00:00'))
                        except:
                            # If parsing fails, keep as string
                            pass
                    tweets.append(TweetAnalyzed(**tweet_data))
                cache[batch_id] = tweets

            logger.info(f"Loaded tweets cache: {len(cache)} batches")
            return cache

        except Exception as e:
            logger.error(f"Failed to load tweets cache: {e}")
            return {}
    
    def save_logs_cache(self, cache: List[AnalysisLog]) -> bool:
        """
        Save analysis logs cache to disk

        Args:
            cache: List of AnalysisLog objects

        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert AnalysisLog objects to dictionaries with proper serialization
            serializable_cache = []
            for log in cache:
                log_dict = log.model_dump()

                # Safely convert all datetime-like fields
                for key, value in log_dict.items():
                    if value is not None:
                        log_dict[key] = safe_datetime_convert(value)

                serializable_cache.append(log_dict)

            # Add metadata
            cache_data = {
                "saved_at": datetime.now(UTC).isoformat(),
                "cache": serializable_cache
            }

            with open(self.logs_cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False, cls=DateTimeEncoder)

            logger.info(f"Saved logs cache: {len(cache)} logs")
            return True

        except Exception as e:
            logger.error(f"Failed to save logs cache: {e}")
            return False
    
    def load_logs_cache(self) -> List[AnalysisLog]:
        """
        Load analysis logs cache from disk

        Returns:
            List of AnalysisLog objects
        """
        try:
            if not self.logs_cache_file.exists():
                logger.info("No logs cache file found")
                return []

            with open(self.logs_cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            # Convert dictionaries back to AnalysisLog objects
            logs = []
            for log_data in cache_data.get("cache", []):
                # Convert date string back to datetime if needed
                if 'created_at' in log_data and isinstance(log_data['created_at'], str):
                    try:
                        from datetime import datetime, UTC
                        log_data['created_at'] = datetime.fromisoformat(log_data['created_at'].replace('Z', '+00:00'))
                    except:
                        # If parsing fails, keep as string
                        pass
                logs.append(AnalysisLog(**log_data))

            logger.info(f"Loaded logs cache: {len(logs)} logs")
            return logs

        except Exception as e:
            logger.error(f"Failed to load logs cache: {e}")
            return []
    
    def clear_cache(self) -> bool:
        """
        Clear all cache files
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.tweets_cache_file.exists():
                self.tweets_cache_file.unlink()
            if self.logs_cache_file.exists():
                self.logs_cache_file.unlink()
            
            logger.info("Cache files cleared")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get information about cached data
        
        Returns:
            Dictionary with cache information
        """
        info = {
            "tweets_cache_exists": self.tweets_cache_file.exists(),
            "logs_cache_exists": self.logs_cache_file.exists(),
            "tweets_cache_size": 0,
            "logs_cache_size": 0,
            "tweets_cache_modified": None,
            "logs_cache_modified": None
        }
        
        try:
            if info["tweets_cache_exists"]:
                stat = self.tweets_cache_file.stat()
                info["tweets_cache_size"] = stat.st_size
                info["tweets_cache_modified"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
            
            if info["logs_cache_exists"]:
                stat = self.logs_cache_file.stat()
                info["logs_cache_size"] = stat.st_size
                info["logs_cache_modified"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
                
        except Exception as e:
            logger.error(f"Failed to get cache info: {e}")
        
        return info
