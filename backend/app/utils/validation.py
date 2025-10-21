"""
Input validation and data sanitization utilities
"""

import re
import html
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from pathlib import Path
import logging

from ..exceptions import ValidationError

logger = logging.getLogger(__name__)

class DataValidator:
    """Comprehensive data validation and sanitization"""
    
    # Regex patterns for validation
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    TWEET_ID_PATTERN = re.compile(r'^[0-9]+$')
    USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_]{1,15}$')
    HASHTAG_PATTERN = re.compile(r'^#[a-zA-Z0-9_]+$')
    URL_PATTERN = re.compile(r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?')
    
    # Content limits
    MAX_TWEET_LENGTH = 500
    MIN_TWEET_LENGTH = 1
    MAX_AUTHOR_LENGTH = 50
    MAX_BATCH_SIZE = 1000
    
    @classmethod
    def validate_tweet_text(cls, text: str) -> str:
        """Validate and sanitize tweet text"""
        if not isinstance(text, str):
            raise ValidationError("Tweet text must be a string")
        
        # Remove null bytes and control characters
        text = text.replace('\x00', '').replace('\r', '').strip()
        
        # HTML escape for security
        text = html.escape(text)
        
        # Check length
        if len(text) < cls.MIN_TWEET_LENGTH:
            raise ValidationError(f"Tweet text too short (minimum {cls.MIN_TWEET_LENGTH} characters)")
        
        if len(text) > cls.MAX_TWEET_LENGTH:
            raise ValidationError(f"Tweet text too long (maximum {cls.MAX_TWEET_LENGTH} characters)")
        
        return text
    
    @classmethod
    def validate_tweet_id(cls, tweet_id: Union[str, int]) -> str:
        """Validate and normalize tweet ID"""
        if isinstance(tweet_id, int):
            tweet_id = str(tweet_id)
        
        if not isinstance(tweet_id, str):
            raise ValidationError("Tweet ID must be a string or integer")
        
        tweet_id = tweet_id.strip()
        
        if not cls.TWEET_ID_PATTERN.match(tweet_id):
            raise ValidationError("Tweet ID must contain only digits")
        
        if len(tweet_id) > 20:  # Twitter snowflake IDs are max 19 digits
            raise ValidationError("Tweet ID too long")
        
        return tweet_id
    
    @classmethod
    def validate_author(cls, author: str) -> str:
        """Validate and sanitize author name"""
        if not isinstance(author, str):
            raise ValidationError("Author must be a string")
        
        author = author.strip()
        
        if len(author) == 0:
            raise ValidationError("Author cannot be empty")
        
        if len(author) > cls.MAX_AUTHOR_LENGTH:
            raise ValidationError(f"Author name too long (maximum {cls.MAX_AUTHOR_LENGTH} characters)")
        
        # Remove @ symbol if present
        if author.startswith('@'):
            author = author[1:]
        
        # HTML escape for security
        author = html.escape(author)
        
        return author
    
    @classmethod
    def validate_date(cls, date: Union[str, datetime]) -> datetime:
        """Validate and normalize date"""
        if isinstance(date, str):
            try:
                # Try common date formats
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ']:
                    try:
                        return datetime.strptime(date, fmt)
                    except ValueError:
                        continue
                
                # If none work, raise error
                raise ValueError("Unsupported date format")
                
            except ValueError:
                raise ValidationError(f"Invalid date format: {date}")
        
        elif isinstance(date, datetime):
            return date
        
        else:
            raise ValidationError("Date must be a string or datetime object")
    
    @classmethod
    def validate_email(cls, email: str) -> str:
        """Validate email address"""
        if not isinstance(email, str):
            raise ValidationError("Email must be a string")
        
        email = email.strip().lower()
        
        if not cls.EMAIL_PATTERN.match(email):
            raise ValidationError("Invalid email format")
        
        return email
    
    @classmethod
    def validate_batch_size(cls, batch_size: int) -> int:
        """Validate batch size"""
        if not isinstance(batch_size, int):
            raise ValidationError("Batch size must be an integer")
        
        if batch_size < 1:
            raise ValidationError("Batch size must be at least 1")
        
        if batch_size > cls.MAX_BATCH_SIZE:
            raise ValidationError(f"Batch size too large (maximum {cls.MAX_BATCH_SIZE})")
        
        return batch_size
    
    @classmethod
    def validate_file_path(cls, file_path: Union[str, Path]) -> Path:
        """Validate file path"""
        if isinstance(file_path, str):
            file_path = Path(file_path)
        
        if not isinstance(file_path, Path):
            raise ValidationError("File path must be a string or Path object")
        
        # Security check - prevent path traversal
        try:
            file_path.resolve()
        except (OSError, ValueError) as e:
            raise ValidationError(f"Invalid file path: {e}")
        
        # Check for suspicious patterns
        path_str = str(file_path)
        if '..' in path_str or path_str.startswith('/'):
            raise ValidationError("File path contains suspicious patterns")
        
        return file_path
    
    @classmethod
    def validate_csv_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate CSV row data"""
        validated = {}
        
        # Required fields
        required_fields = ['tweet_id', 'author', 'text', 'date']
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")
        
        # Validate each field
        validated['tweet_id'] = cls.validate_tweet_id(data['tweet_id'])
        validated['author'] = cls.validate_author(data['author'])
        validated['text'] = cls.validate_tweet_text(data['text'])
        validated['date'] = cls.validate_date(data['date'])
        
        # Optional fields
        optional_fields = ['mentions', 'hashtags', 'urls', 'retweet_count', 'like_count']
        for field in optional_fields:
            if field in data and data[field] is not None:
                validated[field] = data[field]
        
        return validated
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """Sanitize filename for safe storage while preserving extension"""
        if not isinstance(filename, str):
            raise ValidationError("Filename must be a string")
        
        # Split filename and extension
        if '.' in filename:
            name_part, ext_part = filename.rsplit('.', 1)
            # Preserve the extension, sanitize the name
            name_part = re.sub(r'[<>:"/\\|?*]', '_', name_part)
            name_part = name_part.strip(' ')  # Only strip spaces, not periods
            ext_part = re.sub(r'[<>:"/\\|?*]', '_', ext_part)  # Sanitize extension too
            filename = f"{name_part}.{ext_part}" if name_part else f"file.{ext_part}"
        else:
            # No extension found
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            filename = filename.strip(' ')
        
        if not filename or filename == '.':
            raise ValidationError("Filename cannot be empty after sanitization")
        
        # Limit length while preserving extension
        if len(filename) > 255:
            if '.' in filename:
                name_part, ext_part = filename.rsplit('.', 1)
                # Reserve space for extension and dot
                max_name_length = 250 - len(ext_part)
                filename = name_part[:max_name_length] + '.' + ext_part
            else:
                filename = filename[:255]
        
        return filename
    
    @classmethod
    def validate_api_key(cls, api_key: str, provider: str) -> str:
        """Validate API key format"""
        if not isinstance(api_key, str):
            raise ValidationError("API key must be a string")
        
        api_key = api_key.strip()
        
        if len(api_key) < 10:
            raise ValidationError(f"API key for {provider} too short")
        
        if len(api_key) > 200:
            raise ValidationError(f"API key for {provider} too long")
        
        # Basic format validation for known providers
        if provider == "openai" and not api_key.startswith("sk-"):
            raise ValidationError("OpenAI API key should start with 'sk-'")
        
        return api_key
    
    @classmethod
    def validate_json_data(cls, data: Any, max_depth: int = 10) -> Any:
        """Validate JSON data structure and prevent deeply nested objects"""
        def check_depth(obj, current_depth=0):
            if current_depth > max_depth:
                raise ValidationError(f"JSON data too deeply nested (max depth: {max_depth})")
            
            if isinstance(obj, dict):
                for value in obj.values():
                    check_depth(value, current_depth + 1)
            elif isinstance(obj, list):
                for item in obj:
                    check_depth(item, current_depth + 1)
        
        check_depth(data)
        return data
