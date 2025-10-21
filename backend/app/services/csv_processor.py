"""
CSV Processor for tweet analysis platform
Handles loading, cleaning, and validation of tweet data from CSV files
"""

import pandas as pd
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging
from pathlib import Path

from ..models import TweetRaw
from ..utils.cleaning import TextCleaner

logger = logging.getLogger(__name__)

class CSVProcessor:
    """
    Traitement et nettoyage CSV tweets
    Handles CSV processing and cleaning for tweet data
    """
    
    def __init__(self, encoding: str = 'utf-8', min_text_length: int = 10):
        """
        Initialize CSV processor with configuration
        
        Args:
            encoding: File encoding for CSV reading
            min_text_length: Minimum tweet text length to keep
        """
        self.encoding = encoding
        self.min_text_length = min_text_length
        self.text_cleaner = TextCleaner()
        
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Nettoyage basique du texte
        Basic text cleaning for tweets
        
        Args:
            text: Raw tweet text
            
        Returns:
            Cleaned tweet text
        """
        if not text or not isinstance(text, str):
            return ""
            
        # Supprimer URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Normaliser espaces multiples
        text = ' '.join(text.split())
        
        # Supprimer mentions multiples redondantes (@user @user @user -> @user)
        text = re.sub(r'(@\w+\s*){3,}', lambda m: m.group(1), text)
        
        # Supprimer caractères de contrôle
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        # Nettoyer emojis excessifs (garder quelques-uns)
        text = re.sub(r'([\U0001F600-\U0001F64F]){3,}', r'\1\1', text)
        
        return text.strip()
    
    @staticmethod
    def extract_metadata(text: str) -> Dict[str, List[str]]:
        """
        Extraire mentions, hashtags, URLs du texte
        Extract mentions, hashtags, URLs from tweet text
        
        Args:
            text: Tweet text to analyze
            
        Returns:
            Dictionary with extracted metadata
        """
        return {
            'mentions': re.findall(r'@(\w+)', text),
            'hashtags': re.findall(r'#(\w+)', text),
            'urls': re.findall(r'http\S+|www\S+|https\S+', text)
        }
    
    def validate_csv_structure(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate CSV structure and required columns
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        required_cols = ['tweet_id', 'author', 'text', 'date']
        
        # Check required columns
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            errors.append(f"Colonnes manquantes: {missing_cols}")
        
        # Check data types and content
        if 'tweet_id' in df.columns:
            if df['tweet_id'].isnull().any():
                errors.append("Des tweet_id sont manquants")
            if df['tweet_id'].duplicated().any():
                errors.append("Des tweet_id sont dupliqués")
        
        if 'text' in df.columns:
            empty_texts = df['text'].isnull().sum()
            if empty_texts > 0:
                errors.append(f"{empty_texts} tweets ont un texte vide")
        
        if 'date' in df.columns:
            try:
                pd.to_datetime(df['date'])
            except Exception as e:
                errors.append(f"Format de date invalide: {str(e)}")
        
        return len(errors) == 0, errors
    
    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and prepare DataFrame for processing
        
        Args:
            df: Raw DataFrame from CSV
            
        Returns:
            Cleaned DataFrame
        """
        logger.info(f"Nettoyage DataFrame: {len(df)} lignes initiales")
        
        # Remove duplicates based on tweet_id
        initial_count = len(df)
        df = df.drop_duplicates(subset=['tweet_id'], keep='first')
        duplicates_removed = initial_count - len(df)
        if duplicates_removed > 0:
            logger.info(f"Supprimé {duplicates_removed} doublons")
        
        # Clean text column
        df['text'] = df['text'].astype(str).apply(self.clean_text)
        
        # Remove tweets that are too short after cleaning
        df = df[df['text'].str.len() >= self.min_text_length]
        short_removed = initial_count - duplicates_removed - len(df)
        if short_removed > 0:
            logger.info(f"Supprimé {short_removed} tweets trop courts")
        
        # Convert date column
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Remove rows with invalid dates
        before_date_filter = len(df)
        df = df.dropna(subset=['date'])
        invalid_dates = before_date_filter - len(df)
        if invalid_dates > 0:
            logger.info(f"Supprimé {invalid_dates} tweets avec dates invalides")
        
        # Ensure numeric columns are properly typed
        numeric_cols = ['retweet_count', 'favorite_count']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        # Remove any remaining null values in required columns
        required_cols = ['tweet_id', 'author', 'text', 'date']
        df = df.dropna(subset=required_cols)
        
        logger.info(f"Nettoyage terminé: {len(df)} lignes conservées")
        return df
    
    def load_and_clean_csv(self, filepath: str) -> List[TweetRaw]:
        """
        Charger et nettoyer le CSV
        Load and clean CSV file, returning list of TweetRaw objects
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            List of validated TweetRaw objects
            
        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If CSV structure is invalid
            Exception: For other processing errors
        """
        logger.info(f"Chargement CSV: {filepath}")
        
        # Check file exists
        if not Path(filepath).exists():
            raise FileNotFoundError(f"Fichier CSV introuvable: {filepath}")
        
        try:
            # Load CSV with multiple encoding attempts
            df = None
            encodings = [self.encoding, 'utf-8', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(filepath, encoding=encoding)
                    logger.info(f"CSV chargé avec encodage: {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                raise ValueError("Impossible de lire le fichier avec les encodages supportés")
            
            logger.info(f"CSV chargé: {len(df)} lignes, {len(df.columns)} colonnes")
            
            # Validate structure
            is_valid, errors = self.validate_csv_structure(df)
            if not is_valid:
                raise ValueError(f"Structure CSV invalide: {'; '.join(errors)}")
            
            # Clean DataFrame
            df_clean = self.clean_dataframe(df)
            
            # Convert to TweetRaw objects
            tweets = []
            conversion_errors = 0
            
            for idx, row in df_clean.iterrows():
                try:
                    # Prepare row data
                    tweet_data = {
                        'tweet_id': str(row['tweet_id']),
                        'author': str(row['author']),
                        'text': str(row['text']),
                        'date': row['date'],
                        'retweet_count': int(row.get('retweet_count', 0)),
                        'favorite_count': int(row.get('favorite_count', 0))
                    }
                    
                    # Create and validate TweetRaw object
                    tweet = TweetRaw(**tweet_data)
                    tweets.append(tweet)
                    
                except Exception as e:
                    conversion_errors += 1
                    logger.warning(f"Erreur conversion ligne {idx}: {e}")
                    continue
            
            if conversion_errors > 0:
                logger.warning(f"{conversion_errors} tweets n'ont pas pu être convertis")
            
            logger.info(f"Traitement terminé: {len(tweets)} tweets valides")
            return tweets
            
        except Exception as e:
            logger.error(f"Erreur traitement CSV: {e}")
            raise
    
    def get_processing_stats(self, tweets: List[TweetRaw]) -> Dict:
        """
        Generate processing statistics
        
        Args:
            tweets: List of processed tweets
            
        Returns:
            Dictionary with processing statistics
        """
        if not tweets:
            return {"total": 0, "error": "No tweets processed"}
        
        # Basic stats
        stats = {
            "total_tweets": len(tweets),
            "date_range": {
                "start": min(tweet.date for tweet in tweets),
                "end": max(tweet.date for tweet in tweets)
            },
            "authors": len(set(tweet.author for tweet in tweets)),
            "avg_text_length": sum(len(tweet.text) for tweet in tweets) / len(tweets),
            "total_retweets": sum(tweet.retweet_count for tweet in tweets),
            "total_favorites": sum(tweet.favorite_count for tweet in tweets)
        }
        
        # Text analysis
        all_text = " ".join(tweet.text for tweet in tweets)
        metadata = self.extract_metadata(all_text)
        stats["metadata"] = {
            "total_mentions": len(metadata['mentions']),
            "unique_mentions": len(set(metadata['mentions'])),
            "total_hashtags": len(metadata['hashtags']),
            "unique_hashtags": len(set(metadata['hashtags'])),
            "total_urls": len(metadata['urls'])
        }
        
        return stats
    
    def export_processed_data(self, tweets: List[TweetRaw], output_path: str) -> bool:
        """
        Export processed tweets to CSV
        
        Args:
            tweets: List of tweets to export
            output_path: Path for output file
            
        Returns:
            True if export successful
        """
        try:
            # Convert to DataFrame
            data = []
            for tweet in tweets:
                data.append({
                    'tweet_id': tweet.tweet_id,
                    'author': tweet.author,
                    'text': tweet.text,
                    'date': tweet.date,
                    'retweet_count': tweet.retweet_count,
                    'favorite_count': tweet.favorite_count
                })
            
            df = pd.DataFrame(data)
            df.to_csv(output_path, index=False, encoding='utf-8')
            logger.info(f"Données exportées vers: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur export: {e}")
            return False
