"""
Custom exceptions for the FreeMobilaChat tweet analysis application
"""

from typing import Optional, Any, Dict


class FreeMobilaChatException(Exception):
    """Base exception for FreeMobilaChat application"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class DataProcessingError(FreeMobilaChatException):
    """Raised when data processing fails"""
    pass


class LLMAnalysisError(FreeMobilaChatException):
    """Raised when LLM analysis fails"""
    pass


class APIConnectionError(FreeMobilaChatException):
    """Raised when API connection fails"""
    pass


class RateLimitExceededError(FreeMobilaChatException):
    """Raised when API rate limit is exceeded"""
    pass


class ValidationError(FreeMobilaChatException):
    """Raised when data validation fails"""
    pass


class ConfigurationError(FreeMobilaChatException):
    """Raised when configuration is invalid"""
    pass


class DatabaseError(FreeMobilaChatException):
    """Raised when database operations fail"""
    pass


class FileProcessingError(FreeMobilaChatException):
    """Raised when file processing fails"""
    pass


class ModelTrainingError(FreeMobilaChatException):
    """Raised when model training fails"""
    pass


class CacheError(FreeMobilaChatException):
    """Raised when cache operations fail"""
    pass
