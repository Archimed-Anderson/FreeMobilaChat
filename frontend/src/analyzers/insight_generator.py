"""
Insight Generator
Generates human-readable insights from data analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class InsightGenerator:
    """
    Generates actionable insights from analyzed data
    
    Features:
    - Automatic insight detection
    - Natural language summaries
    - Anomaly highlighting
    - Data quality warnings
    """
    
    def __init__(self, df: pd.DataFrame, classification_results: Dict[str, Any]):
        """
        Initialize insight generator
        
        Args:
            df: Original DataFrame
            classification_results: Results from DataClassifier
        """
        self.df = df
        self.results = classification_results
        self.column_types = classification_results['column_types']
        self.column_stats = classification_results['column_stats']
        self.correlations = classification_results['correlations']
        self.quality_score = classification_results['quality_score']
    
    def generate_insights(self) -> List[str]:
        """
        Generate comprehensive insights
        
        Returns:
            List of insight strings
        """
        insights = []
        
        # Dataset overview insights
        insights.extend(self._dataset_overview_insights())
        
        # Data quality insights
        insights.extend(self._data_quality_insights())
        
        # Statistical insights
        insights.extend(self._statistical_insights())
        
        # Correlation insights
        insights.extend(self._correlation_insights())
        
        # Anomaly insights
        insights.extend(self._anomaly_insights())
        
        return insights
    
    def _dataset_overview_insights(self) -> List[str]:
        """Generate high-level dataset insights"""
        insights = []
        summary = self.results['dataset_summary']
        
        insights.append(
            f"📊 **Aperçu des données**: {summary['total_rows']:,} lignes et "
            f"{summary['total_columns']} colonnes ({summary['memory_mb']:.1f} MB)"
        )
        
        # Type distribution
        type_dist = summary['type_distribution']
        if 'numeric' in type_dist:
            insights.append(
                f"🔢 **Variables numériques**: {type_dist['numeric']} colonnes disponibles pour l'analyse quantitative"
            )
        if 'categorical' in type_dist:
            insights.append(
                f"🏷️ **Variables catégorielles**: {type_dist['categorical']} colonnes pour la segmentation"
            )
        if 'temporal' in type_dist:
            insights.append(
                f"📅 **Données temporelles**: {type_dist['temporal']} colonnes de dates détectées"
            )
        
        return insights
    
    def _data_quality_insights(self) -> List[str]:
        """Generate data quality insights"""
        insights = []
        summary = self.results['dataset_summary']
        
        # Overall quality
        if self.quality_score >= 90:
            insights.append(f"✅ **Excellente qualité des données** ({self.quality_score}/100)")
        elif self.quality_score >= 70:
            insights.append(f"⚠️ **Bonne qualité des données** ({self.quality_score}/100) - quelques améliorations possibles")
        else:
            insights.append(f"❌ **Qualité des données à améliorer** ({self.quality_score}/100)")
        
        # Missing values
        null_cells = summary['null_cells']
        total_cells = summary['total_rows'] * summary['total_columns']
        null_pct = (null_cells / total_cells * 100) if total_cells > 0 else 0
        
        if null_pct > 10:
            insights.append(
                f"⚠️ **Valeurs manquantes**: {null_pct:.1f}% des cellules sont vides "
                f"({null_cells:,} valeurs manquantes)"
            )
        
        # Duplicates
        if summary['duplicate_rows'] > 0:
            dup_pct = summary['duplicate_rows'] / summary['total_rows'] * 100
            insights.append(
                f"⚠️ **Lignes dupliquées**: {summary['duplicate_rows']:,} lignes "
                f"({dup_pct:.1f}%) sont des doublons"
            )
        
        return insights
    
    def _statistical_insights(self) -> List[str]:
        """Generate statistical insights"""
        insights = []
        
        # Numeric column insights
        numeric_cols = [col for col, t in self.column_types.items() if t == 'numeric']
        
        for col in numeric_cols[:5]:  # Top 5 numeric columns
            stats = self.column_stats[col]
            
            # Check for skewness
            if abs(stats.get('skewness', 0)) > 1:
                skew_direction = "positive" if stats['skewness'] > 0 else "négative"
                insights.append(
                    f"📈 **{col}**: Distribution {skew_direction}ment asymétrique "
                    f"(moyenne={stats['mean']:.2f}, médiane={stats['median']:.2f})"
                )
            
            # Check for outliers
            if stats.get('outlier_percentage', 0) > 5:
                insights.append(
                    f"⚠️ **{col}**: {stats['outlier_count']} valeurs aberrantes détectées "
                    f"({stats['outlier_percentage']:.1f}%)"
                )
        
        # Categorical insights
        categorical_cols = [col for col, t in self.column_types.items() if t == 'categorical']
        
        for col in categorical_cols[:3]:  # Top 3 categorical
            stats = self.column_stats[col]
            
            if stats.get('mode_percentage', 0) > 50:
                insights.append(
                    f"🏷️ **{col}**: Dominé par '{stats['mode']}' "
                    f"({stats['mode_percentage']:.1f}% des valeurs)"
                )
        
        return insights
    
    def _correlation_insights(self) -> List[str]:
        """Generate correlation insights"""
        insights = []
        
        if not self.correlations:
            return insights
        
        # Strong positive correlations
        strong_positive = [c for c in self.correlations if c[2] > 0.7]
        if strong_positive:
            col1, col2, corr = strong_positive[0]
            insights.append(
                f"🔗 **Forte corrélation positive**: {col1} et {col2} sont "
                f"fortement corrélés (r={corr:.2f})"
            )
        
        # Strong negative correlations
        strong_negative = [c for c in self.correlations if c[2] < -0.7]
        if strong_negative:
            col1, col2, corr = strong_negative[0]
            insights.append(
                f"🔗 **Forte corrélation négative**: {col1} et {col2} évoluent "
                f"en sens inverse (r={corr:.2f})"
            )
        
        return insights
    
    def _anomaly_insights(self) -> List[str]:
        """Generate anomaly detection insights"""
        insights = []
        
        for col, stats in self.column_stats.items():
            col_type = self.column_types.get(col, 'unknown')
            
            # Check for extremely high null percentage
            if stats['null_percentage'] > 80:
                insights.append(
                    f"❌ **{col}**: Colonne presque vide ({stats['null_percentage']:.1f}% de valeurs manquantes)"
                )
            
            # Check for suspiciously low uniqueness in identifiers
            if col_type == 'identifier' and stats['uniqueness_ratio'] < 0.9:
                insights.append(
                    f"⚠️ **{col}**: Identifiant avec des doublons ({stats['uniqueness_ratio']*100:.1f}% unique)"
                )
            
            # Check for single-value columns
            if stats['unique_count'] == 1:
                insights.append(
                    f"⚠️ **{col}**: Colonne constante (une seule valeur unique)"
                )
        
        return insights
    
    def get_summary(self) -> str:
        """
        Get a concise summary of the dataset
        
        Returns:
            Summary string
        """
        summary = self.results['dataset_summary']
        
        return (
            f"Dataset de {summary['total_rows']:,} lignes et {summary['total_columns']} colonnes. "
            f"Qualité des données: {self.quality_score}/100. "
            f"{len(self.correlations)} corrélations significatives détectées."
        )
