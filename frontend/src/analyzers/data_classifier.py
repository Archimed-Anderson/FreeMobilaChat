"""
Data Classifier
Automatic classification and profiling of datasets
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from ..utils.data_processor import DataProcessor
import logging

logger = logging.getLogger(__name__)


class DataClassifier:
    """
    Classifies and profiles datasets automatically
    
    Features:
    - Column type inference
    - Statistical profiling
    - Data quality assessment
    - Relationship detection
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize classifier with DataFrame
        
        Args:
            df: pandas DataFrame to analyze
        """
        self.df = df
        self.column_types = {}
        self.column_stats = {}
        self.correlations = []
        self.quality_score = 0.0
    
    def classify(self) -> Dict[str, Any]:
        """
        Perform complete classification of the dataset
        
        Returns:
            Dictionary with classification results
        """
        logger.info(f"Starting classification of dataset with {len(self.df)} rows and {len(self.df.columns)} columns")
        
        # Infer column types
        self.column_types = DataProcessor.infer_column_types(self.df)
        logger.info(f"Column types identified: {self.column_types}")
        
        # Calculate column statistics
        self.column_stats = DataProcessor.get_column_stats(self.df, self.column_types)
        logger.info("Column statistics calculated")
        
        # Detect correlations
        self.correlations = DataProcessor.detect_correlations(self.df, threshold=0.5)
        logger.info(f"Found {len(self.correlations)} significant correlations")
        
        # Calculate quality score
        self.quality_score = DataProcessor.calculate_data_quality_score(self.df, self.column_stats)
        logger.info(f"Data quality score: {self.quality_score}/100")
        
        return {
            'column_types': self.column_types,
            'column_stats': self.column_stats,
            'correlations': self.correlations,
            'quality_score': self.quality_score,
            'dataset_summary': self._get_dataset_summary()
        }
    
    def _get_dataset_summary(self) -> Dict[str, Any]:
        """
        Get high-level dataset summary
        
        Returns:
            Summary dictionary
        """
        type_counts = {}
        for col_type in self.column_types.values():
            type_counts[col_type] = type_counts.get(col_type, 0) + 1
        
        return {
            'total_rows': len(self.df),
            'total_columns': len(self.df.columns),
            'memory_mb': self.df.memory_usage(deep=True).sum() / 1024**2,
            'type_distribution': type_counts,
            'null_cells': int(self.df.isnull().sum().sum()),
            'duplicate_rows': int(self.df.duplicated().sum()),
            'numeric_columns': [col for col, t in self.column_types.items() if t == 'numeric'],
            'categorical_columns': [col for col, t in self.column_types.items() if t == 'categorical'],
            'temporal_columns': [col for col, t in self.column_types.items() if t == 'temporal'],
            'text_columns': [col for col, t in self.column_types.items() if t == 'text']
        }
    
    def get_column_by_type(self, col_type: str) -> List[str]:
        """
        Get list of columns of a specific type
        
        Args:
            col_type: Type to filter by
            
        Returns:
            List of column names
        """
        return [col for col, t in self.column_types.items() if t == col_type]
