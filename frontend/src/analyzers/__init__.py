"""
Data Analysis Module
Automatic file analysis, classification, and insight generation
"""

from .main import analyze_document
from .data_classifier import DataClassifier
from .metric_selector import MetricSelector
from .insight_generator import InsightGenerator

__all__ = [
    'analyze_document',
    'DataClassifier',
    'MetricSelector',
    'InsightGenerator'
]
