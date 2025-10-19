"""
Unit tests for Data Processor utility
"""

import pytest
import pandas as pd
import numpy as np
from ..utils.data_processor import DataProcessor


class TestDataProcessor:
    """Test suite for DataProcessor class"""
    
    @pytest.fixture
    def sample_df(self):
        """Create sample DataFrame for testing"""
        return pd.DataFrame({
            'numeric_col': [1, 2, 3, 4, 5, 100],  # Has outlier
            'categorical_col': ['A', 'B', 'A', 'C', 'A', 'B'],
            'text_col': ['Hello world', 'Test text', 'Another example'] * 2,
            'date_col': pd.date_range('2024-01-01', periods=6),
            'boolean_col': [True, False, True, True, False, True],
            'identifier_col': range(6)
        })
    
    def test_infer_column_types(self, sample_df):
        """Test column type inference"""
        column_types = DataProcessor.infer_column_types(sample_df)
        
        assert column_types['numeric_col'] == 'numeric'
        assert column_types['categorical_col'] == 'categorical'
        assert column_types['text_col'] == 'text'
        assert column_types['date_col'] == 'temporal'
        assert column_types['boolean_col'] == 'boolean'
        assert column_types['identifier_col'] == 'identifier'
    
    def test_numeric_stats(self, sample_df):
        """Test numeric statistics calculation"""
        column_types = DataProcessor.infer_column_types(sample_df)
        stats = DataProcessor.get_column_stats(sample_df, column_types)
        
        numeric_stats = stats['numeric_col']
        assert 'mean' in numeric_stats
        assert 'median' in numeric_stats
        assert 'std' in numeric_stats
        assert numeric_stats['outlier_count'] > 0  # Should detect 100 as outlier
    
    def test_categorical_stats(self, sample_df):
        """Test categorical statistics"""
        column_types = DataProcessor.infer_column_types(sample_df)
        stats = DataProcessor.get_column_stats(sample_df, column_types)
        
        cat_stats = stats['categorical_col']
        assert 'mode' in cat_stats
        assert cat_stats['mode'] == 'A'  # Most frequent
        assert 'num_categories' in cat_stats
    
    def test_detect_correlations(self, sample_df):
        """Test correlation detection"""
        # Add correlated column
        sample_df['correlated'] = sample_df['numeric_col'] * 2
        
        correlations = DataProcessor.detect_correlations(sample_df, threshold=0.5)
        
        assert len(correlations) > 0
        assert any(cor[2] > 0.9 for cor in correlations)  # Strong correlation
    
    def test_data_quality_score(self, sample_df):
        """Test data quality score calculation"""
        column_types = DataProcessor.infer_column_types(sample_df)
        stats = DataProcessor.get_column_stats(sample_df, column_types)
        
        quality_score = DataProcessor.calculate_data_quality_score(sample_df, stats)
        
        assert 0 <= quality_score <= 100
        assert quality_score > 80  # Should be high for clean data
    
    def test_empty_dataframe(self):
        """Test handling of empty DataFrame"""
        empty_df = pd.DataFrame()
        column_types = DataProcessor.infer_column_types(empty_df)
        
        assert column_types == {}
    
    def test_null_handling(self):
        """Test handling of null values"""
        df_with_nulls = pd.DataFrame({
            'col1': [1, 2, None, 4, 5],
            'col2': ['a', None, 'c', None, 'e']
        })
        
        column_types = DataProcessor.infer_column_types(df_with_nulls)
        stats = DataProcessor.get_column_stats(df_with_nulls, column_types)
        
        assert stats['col1']['null_percentage'] == 20.0
        assert stats['col2']['null_percentage'] == 40.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
