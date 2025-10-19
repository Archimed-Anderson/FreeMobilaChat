"""
Metric Selector
Automatically selects appropriate metrics and visualizations
"""

import pandas as pd
from typing import Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


class MetricSelector:
    """
    Selects appropriate metrics and analysis methods based on data types
    
    Features:
    - Automatic metric selection
    - Visualization recommendations
    - Statistical test suggestions
    """
    
    def __init__(self, column_types: Dict[str, str], column_stats: Dict[str, Dict[str, Any]]):
        """
        Initialize metric selector
        
        Args:
            column_types: Dictionary mapping columns to types
            column_stats: Dictionary with column statistics
        """
        self.column_types = column_types
        self.column_stats = column_stats
    
    def select_metrics(self) -> Dict[str, Any]:
        """
        Select appropriate metrics for the dataset
        
        Returns:
            Dictionary with recommended metrics and visualizations
        """
        recommendations = {
            'univariate_analysis': [],
            'bivariate_analysis': [],
            'multivariate_analysis': [],
            'time_series_analysis': []
        }
        
        # Univariate analysis recommendations
        for col, col_type in self.column_types.items():
            if col_type == 'numeric':
                recommendations['univariate_analysis'].append({
                    'column': col,
                    'type': col_type,
                    'charts': ['histogram', 'boxplot', 'violin'],
                    'metrics': ['mean', 'median', 'std', 'quartiles', 'outliers']
                })
            elif col_type == 'categorical':
                recommendations['univariate_analysis'].append({
                    'column': col,
                    'type': col_type,
                    'charts': ['bar', 'pie', 'treemap'],
                    'metrics': ['frequency', 'mode', 'distribution']
                })
            elif col_type == 'temporal':
                recommendations['univariate_analysis'].append({
                    'column': col,
                    'type': col_type,
                    'charts': ['timeline', 'calendar_heatmap'],
                    'metrics': ['date_range', 'frequency_over_time']
                })
                recommendations['time_series_analysis'].append({
                    'column': col,
                    'analyses': ['trend', 'seasonality', 'distribution_over_time']
                })
        
        # Bivariate analysis recommendations
        numeric_cols = [col for col, t in self.column_types.items() if t == 'numeric']
        categorical_cols = [col for col, t in self.column_types.items() if t == 'categorical']
        
        # Numeric vs Numeric
        if len(numeric_cols) >= 2:
            for i, col1 in enumerate(numeric_cols):
                for col2 in numeric_cols[i+1:]:
                    recommendations['bivariate_analysis'].append({
                        'columns': [col1, col2],
                        'types': ['numeric', 'numeric'],
                        'charts': ['scatter', 'hexbin'],
                        'metrics': ['correlation', 'regression']
                    })
        
        # Numeric vs Categorical
        if numeric_cols and categorical_cols:
            for num_col in numeric_cols[:3]:  # Limit to top 3
                for cat_col in categorical_cols[:3]:
                    recommendations['bivariate_analysis'].append({
                        'columns': [num_col, cat_col],
                        'types': ['numeric', 'categorical'],
                        'charts': ['grouped_boxplot', 'violin_by_category'],
                        'metrics': ['mean_by_group', 'anova']
                    })
        
        # Multivariate recommendations
        if len(numeric_cols) >= 3:
            recommendations['multivariate_analysis'].append({
                'analysis': 'correlation_matrix',
                'columns': numeric_cols,
                'charts': ['heatmap', 'correlation_network'],
                'metrics': ['correlation_coefficients']
            })
        
        return recommendations
    
    def get_priority_visualizations(self, max_charts: int = 10) -> List[Dict[str, Any]]:
        """
        Get prioritized list of visualizations to create
        
        Args:
            max_charts: Maximum number of charts to recommend
            
        Returns:
            List of chart specifications
        """
        metrics = self.select_metrics()
        priority_charts = []
        
        # Priority 1: Overview charts (max 2)
        numeric_cols = [col for col, t in self.column_types.items() if t == 'numeric']
        if len(numeric_cols) >= 2:
            priority_charts.append({
                'priority': 1,
                'type': 'correlation_heatmap',
                'title': 'Corrélation entre variables numériques',
                'columns': numeric_cols,
                'description': 'Matrice de corrélation pour identifier les relations'
            })
        
        # Priority 2: Key numeric distributions (max 4)
        for rec in metrics['univariate_analysis'][:4]:
            if rec['type'] == 'numeric':
                priority_charts.append({
                    'priority': 2,
                    'type': 'histogram',
                    'title': f'Distribution: {rec["column"]}',
                    'columns': [rec['column']],
                    'description': f'Distribution des valeurs de {rec["column"]}'
                })
        
        # Priority 3: Key categorical distributions (max 3)
        for rec in metrics['univariate_analysis'][:3]:
            if rec['type'] == 'categorical':
                priority_charts.append({
                    'priority': 3,
                    'type': 'bar',
                    'title': f'Répartition: {rec["column"]}',
                    'columns': [rec['column']],
                    'description': f'Fréquence des catégories de {rec["column"]}'
                })
        
        # Priority 4: Top bivariate relationships (max 2)
        for rec in metrics['bivariate_analysis'][:2]:
            priority_charts.append({
                'priority': 4,
                'type': 'scatter',
                'title': f'{rec["columns"][0]} vs {rec["columns"][1]}',
                'columns': rec['columns'],
                'description': f'Relation entre {rec["columns"][0]} et {rec["columns"][1]}'
            })
        
        # Sort by priority and limit
        priority_charts.sort(key=lambda x: x['priority'])
        return priority_charts[:max_charts]
