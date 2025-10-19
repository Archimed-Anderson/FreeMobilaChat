"""
Text cleaning utilities for tweet processing
Advanced text cleaning and normalization functions
"""

import re
import html
from typing import List, Dict, Optional
import unicodedata


class TextCleaner:
    """Advanced text cleaning for tweet analysis"""
    
    def __init__(self):
        """Initialize text cleaner with patterns"""
        # Common patterns for cleaning
        self.url_pattern = re.compile(r'http\S+|www\S+|https\S+', re.MULTILINE)
        self.mention_pattern = re.compile(r'@\w+')
        self.hashtag_pattern = re.compile(r'#\w+')
        self.emoji_pattern = re.compile(
            r'[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|[\U0001F680-\U0001F6FF]|[\U0001F1E0-\U0001F1FF]'
        )
        self.whitespace_pattern = re.compile(r'\s+')
        
        # French stopwords for keyword extraction
        self.french_stopwords = {
            'le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir', 'que', 'pour',
            'dans', 'ce', 'son', 'une', 'sur', 'avec', 'ne', 'se', 'pas', 'tout', 'plus',
            'par', 'grand', 'en', 'une', 'être', 'et', 'de', 'il', 'avoir', 'ne', 'je',
            'son', 'que', 'se', 'qui', 'ce', 'dans', 'en', 'du', 'elle', 'au', 'de',
            'ce', 'le', 'pour', 'sont', 'avec', 'ils', 'tout', 'nous', 'sa', 'sur'
        }
    
    def clean_basic(self, text: str) -> str:
        """
        Basic text cleaning
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Remove control characters
        text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C')
        
        # Normalize whitespace
        text = self.whitespace_pattern.sub(' ', text)
        
        return text.strip()
    
    def remove_urls(self, text: str) -> str:
        """Remove URLs from text"""
        return self.url_pattern.sub('', text)
    
    def remove_mentions(self, text: str) -> str:
        """Remove @mentions from text"""
        return self.mention_pattern.sub('', text)
    
    def remove_hashtags(self, text: str) -> str:
        """Remove #hashtags from text"""
        return self.hashtag_pattern.sub('', text)
    
    def remove_emojis(self, text: str) -> str:
        """Remove emojis from text"""
        return self.emoji_pattern.sub('', text)
    
    def extract_mentions(self, text: str) -> List[str]:
        """Extract @mentions from text"""
        matches = self.mention_pattern.findall(text)
        return [match[1:] for match in matches]  # Remove @ symbol
    
    def extract_hashtags(self, text: str) -> List[str]:
        """Extract #hashtags from text"""
        matches = self.hashtag_pattern.findall(text)
        return [match[1:] for match in matches]  # Remove # symbol
    
    def extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text"""
        return self.url_pattern.findall(text)
    
    def clean_for_analysis(self, text: str, preserve_mentions: bool = True, 
                          preserve_hashtags: bool = True) -> str:
        """
        Clean text for LLM analysis while preserving important elements
        
        Args:
            text: Text to clean
            preserve_mentions: Whether to keep @mentions
            preserve_hashtags: Whether to keep #hashtags
            
        Returns:
            Cleaned text suitable for analysis
        """
        if not text:
            return ""
        
        # Basic cleaning
        text = self.clean_basic(text)
        
        # Remove URLs (usually not useful for sentiment analysis)
        text = self.remove_urls(text)
        
        # Optionally remove mentions and hashtags
        if not preserve_mentions:
            text = self.remove_mentions(text)
        if not preserve_hashtags:
            text = self.remove_hashtags(text)
        
        # Normalize repeated characters (e.g., "noooooo" -> "nooo")
        text = re.sub(r'(.)\1{3,}', r'\1\1\1', text)
        
        # Clean up whitespace
        text = self.whitespace_pattern.sub(' ', text).strip()
        
        return text
    
    def extract_keywords(self, text: str, min_length: int = 3, max_keywords: int = 10) -> List[str]:
        """
        Extract potential keywords from text
        
        Args:
            text: Text to analyze
            min_length: Minimum word length
            max_keywords: Maximum number of keywords to return
            
        Returns:
            List of potential keywords
        """
        if not text:
            return []
        
        # Clean text and convert to lowercase
        clean_text = self.clean_for_analysis(text, preserve_mentions=False, preserve_hashtags=False)
        clean_text = clean_text.lower()
        
        # Split into words and filter
        words = re.findall(r'\b\w+\b', clean_text)
        
        # Filter words
        keywords = []
        for word in words:
            if (len(word) >= min_length and 
                word not in self.french_stopwords and
                not word.isdigit() and
                word.isalpha()):
                keywords.append(word)
        
        # Count frequency and return most common
        from collections import Counter
        word_counts = Counter(keywords)
        return [word for word, count in word_counts.most_common(max_keywords)]
    
    def detect_language(self, text: str) -> str:
        """
        Simple language detection (French vs other)
        
        Args:
            text: Text to analyze
            
        Returns:
            Detected language code ('fr' or 'other')
        """
        if not text:
            return 'unknown'
        
        # Simple heuristic based on common French words
        french_indicators = ['le', 'la', 'les', 'de', 'du', 'des', 'et', 'est', 'avec', 'pour', 'sur', 'dans']
        text_lower = text.lower()
        
        french_count = sum(1 for word in french_indicators if word in text_lower)
        
        return 'fr' if french_count >= 2 else 'other'
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text for consistent processing
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        if not text:
            return ""
        
        # Unicode normalization
        text = unicodedata.normalize('NFKD', text)
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove accents (optional, might want to preserve for French)
        # text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
        
        # Clean and normalize whitespace
        text = self.whitespace_pattern.sub(' ', text).strip()
        
        return text
    
    def is_spam_like(self, text: str) -> bool:
        """
        Detect spam-like characteristics in text
        
        Args:
            text: Text to analyze
            
        Returns:
            True if text appears spam-like
        """
        if not text:
            return True
        
        # Check for excessive repetition
        if len(set(text.lower().split())) < len(text.split()) * 0.3:
            return True
        
        # Check for excessive mentions
        mentions = len(self.extract_mentions(text))
        if mentions > 5:
            return True
        
        # Check for excessive hashtags
        hashtags = len(self.extract_hashtags(text))
        if hashtags > 8:
            return True
        
        # Check for excessive URLs
        urls = len(self.extract_urls(text))
        if urls > 3:
            return True
        
        # Check for excessive capitalization
        if len(text) > 10:
            caps_ratio = sum(1 for c in text if c.isupper()) / len(text)
            if caps_ratio > 0.7:
                return True
        
        return False
    
    def clean_for_display(self, text: str, max_length: int = 100) -> str:
        """
        Clean text for display in UI
        
        Args:
            text: Text to clean
            max_length: Maximum length for display
            
        Returns:
            Cleaned text suitable for display
        """
        if not text:
            return ""
        
        # Basic cleaning
        text = self.clean_basic(text)
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length-3] + "..."
        
        return text
