"""
Data Processor Utility
Data cleaning, transformation, and preprocessing
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Advanced data processing and cleaning utilities
    
    Features:
    - Automatic data type inference
    - Missing value handling
    - Outlier detection
    - Data normalization
    """
    
    @staticmethod
    def infer_column_types(df: pd.DataFrame) -> Dict[str, str]:
        """
        Automatically infer semantic column types
        
        Args:
            df: pandas DataFrame
            
        Returns:
            Dictionary mapping column names to types:
            - 'numeric': Continuous numerical data
            - 'categorical': Discrete categories
            - 'temporal': Date/time data
            - 'text': Free text
            - 'boolean': Binary data
            - 'identifier': Unique identifiers
        """
        column_types = {}
        
        for col in df.columns:
            col_type = DataProcessor._classify_column(df[col])
            column_types[col] = col_type
            
        return column_types
    
    @staticmethod
    def _classify_column(series: pd.Series) -> str:
        """
        Classify a single column
        
        Args:
            series: pandas Series
            
        Returns:
            Column type as string
        """
        # Remove null values for analysis
        non_null = series.dropna()
        
        if len(non_null) == 0:
            return 'unknown'
        
        # Check if boolean
        if series.dtype == 'bool' or set(non_null.unique()) <= {0, 1, True, False, 'True', 'False', 'true', 'false'}:
            return 'boolean'
        
        # Check if numeric
        if pd.api.types.is_numeric_dtype(series):
            # Check if it's an identifier (high uniqueness ratio)
            uniqueness_ratio = len(non_null.unique()) / len(non_null)
            if uniqueness_ratio > 0.95:
                return 'identifier'
            
            # Check if it's actually categorical (low cardinality)
            if len(non_null.unique()) <= 20:
                return 'categorical'
            
            return 'numeric'
        
        # Check if datetime
        if pd.api.types.is_datetime64_any_dtype(series):
            return 'temporal'
        
        # Try to parse as datetime
        if series.dtype == 'object':
            try:
                pd.to_datetime(non_null.head(100), errors='raise')
                return 'temporal'
            except:
                pass
        
        # Check if categorical (low cardinality strings)
        if series.dtype == 'object':
            uniqueness_ratio = len(non_null.unique()) / len(non_null)
            
            if uniqueness_ratio > 0.95:
                return 'identifier'
            
            if len(non_null.unique()) <= 50:
                return 'categorical'
            
            # Check average text length
            avg_length = non_null.astype(str).str.len().mean()
            if avg_length > 100:
                return 'text'
            
            return 'categorical'
        
        return 'unknown'
    
    @staticmethod
    def get_column_stats(df: pd.DataFrame, column_types: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """
        Calculate statistics for each column based on its type
        
        Args:
            df: pandas DataFrame
            column_types: Dictionary of column types from infer_column_types
            
        Returns:
            Dictionary with statistics for each column
        """
        stats = {}
        
        for col in df.columns:
            col_type = column_types.get(col, 'unknown')
            series = df[col]
            
            col_stats = {
                'type': col_type,
                'count': len(series),
                'null_count': series.isnull().sum(),
                'null_percentage': series.isnull().sum() / len(series) * 100,
                'unique_count': series.nunique(),
                'uniqueness_ratio': series.nunique() / len(series)
            }
            
            # Type-specific statistics
            if col_type == 'numeric':
                col_stats.update(DataProcessor._numeric_stats(series))
            elif col_type == 'categorical':
                col_stats.update(DataProcessor._categorical_stats(series))
            elif col_type == 'temporal':
                col_stats.update(DataProcessor._temporal_stats(series))
            elif col_type == 'text':
                col_stats.update(DataProcessor._text_stats(series))
            elif col_type == 'boolean':
                col_stats.update(DataProcessor._boolean_stats(series))
            
            stats[col] = col_stats
        
        return stats
    
    @staticmethod
    def _numeric_stats(series: pd.Series) -> Dict[str, Any]:
        """Calculate statistics for numeric columns"""
        non_null = series.dropna()
        
        if len(non_null) == 0:
            return {}
        
        stats = {
            'mean': float(non_null.mean()),
            'median': float(non_null.median()),
            'std': float(non_null.std()) if len(non_null) > 1 else 0,
            'min': float(non_null.min()),
            'max': float(non_null.max()),
            'q25': float(non_null.quantile(0.25)),
            'q75': float(non_null.quantile(0.75)),
            'skewness': float(non_null.skew()) if len(non_null) > 1 else 0,
            'kurtosis': float(non_null.kurtosis()) if len(non_null) > 1 else 0
        }
        
        # Detect outliers using IQR method
        iqr = stats['q75'] - stats['q25']
        lower_bound = stats['q25'] - 1.5 * iqr
        upper_bound = stats['q75'] + 1.5 * iqr
        outliers = non_null[(non_null < lower_bound) | (non_null > upper_bound)]
        
        stats['outlier_count'] = len(outliers)
        stats['outlier_percentage'] = len(outliers) / len(non_null) * 100 if len(non_null) > 0 else 0
        
        return stats
    
    @staticmethod
    def _categorical_stats(series: pd.Series) -> Dict[str, Any]:
        """Calculate statistics for categorical columns"""
        non_null = series.dropna()
        
        if len(non_null) == 0:
            return {}
        
        value_counts = non_null.value_counts()
        
        return {
            'mode': str(value_counts.index[0]) if len(value_counts) > 0 else None,
            'mode_frequency': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
            'mode_percentage': float(value_counts.iloc[0] / len(non_null) * 100) if len(value_counts) > 0 else 0,
            'categories': value_counts.head(10).to_dict(),
            'num_categories': len(value_counts)
        }
    
    @staticmethod
    def _temporal_stats(series: pd.Series) -> Dict[str, Any]:
        """Calculate statistics for temporal columns"""
        # Try to convert to datetime if not already
        try:
            temporal_series = pd.to_datetime(series, errors='coerce')
            non_null = temporal_series.dropna()
            
            if len(non_null) == 0:
                return {}
            
            return {
                'min_date': non_null.min().isoformat(),
                'max_date': non_null.max().isoformat(),
                'date_range_days': (non_null.max() - non_null.min()).days,
                'most_common_year': non_null.dt.year.mode()[0] if len(non_null) > 0 else None,
                'most_common_month': non_null.dt.month.mode()[0] if len(non_null) > 0 else None
            }
        except:
            return {}
    
    @staticmethod
    def _text_stats(series: pd.Series) -> Dict[str, Any]:
        """Calculate statistics for text columns"""
        non_null = series.dropna().astype(str)
        
        if len(non_null) == 0:
            return {}
        
        lengths = non_null.str.len()
        
        return {
            'avg_length': float(lengths.mean()),
            'min_length': int(lengths.min()),
            'max_length': int(lengths.max()),
            'empty_strings': int((non_null == '').sum()),
            'sample_values': non_null.head(3).tolist()
        }
    
    @staticmethod
    def _boolean_stats(series: pd.Series) -> Dict[str, Any]:
        """Calculate statistics for boolean columns"""
        non_null = series.dropna()
        
        if len(non_null) == 0:
            return {}
        
        value_counts = non_null.value_counts()
        
        return {
            'true_count': int(value_counts.get(True, value_counts.get(1, value_counts.get('True', value_counts.get('true', 0))))),
            'false_count': int(value_counts.get(False, value_counts.get(0, value_counts.get('False', value_counts.get('false', 0))))),
            'true_percentage': float(value_counts.get(True, 0) / len(non_null) * 100) if len(non_null) > 0 else 0
        }
    
    @staticmethod
    def detect_correlations(df: pd.DataFrame, threshold: float = 0.5) -> List[Tuple[str, str, float]]:
        """
        Detect correlations between numeric columns
        
        Args:
            df: pandas DataFrame
            threshold: Minimum correlation coefficient (absolute value)
            
        Returns:
            List of tuples (col1, col2, correlation)
        """
        # Select only numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return []
        
        # Calculate correlation matrix
        corr_matrix = df[numeric_cols].corr()
        
        # Find high correlations
        correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) >= threshold:
                    correlations.append((
                        corr_matrix.columns[i],
                        corr_matrix.columns[j],
                        float(corr_value)
                    ))
        
        # Sort by absolute correlation value
        correlations.sort(key=lambda x: abs(x[2]), reverse=True)
        
        return correlations
    
    @staticmethod
    def calculate_data_quality_score(df: pd.DataFrame, column_stats: Dict[str, Dict[str, Any]]) -> float:
        """
        Calculate overall data quality score (0-100)
        
        Args:
            df: pandas DataFrame
            column_stats: Column statistics from get_column_stats
            
        Returns:
            Quality score as float
        """
        scores = []
        
        # Completeness score (based on null values)
        avg_null_pct = np.mean([stats['null_percentage'] for stats in column_stats.values()])
        completeness_score = max(0, 100 - avg_null_pct)
        scores.append(completeness_score)
        
        # Uniqueness score (avoid too many duplicates)
        dup_pct = df.duplicated().sum() / len(df) * 100 if len(df) > 0 else 0
        uniqueness_score = max(0, 100 - dup_pct)
        scores.append(uniqueness_score)
        
        # Consistency score (based on data type consistency)
        unknown_type_count = sum(1 for stats in column_stats.values() if stats['type'] == 'unknown')
        consistency_score = max(0, 100 - (unknown_type_count / len(column_stats) * 100)) if len(column_stats) > 0 else 0
        scores.append(consistency_score)
        
        # Overall score (weighted average)
        quality_score = (
            completeness_score * 0.4 +
            uniqueness_score * 0.3 +
            consistency_score * 0.3
        )
        
        return round(quality_score, 2)
