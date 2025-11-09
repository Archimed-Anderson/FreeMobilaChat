"""
Extended KPI Calculator - Calculs avancés de KPI et métriques de performance
Module d'extension du système de KPI existant avec de nouvelles métriques
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class ExtendedKPICalculator:
    """Calculateur étendu de KPI avec métriques avancées"""
    
    def __init__(self):
        """Initialise le calculateur"""
        self.kpi_history = []
        
    def calculate_all_extended_kpis(self, df: pd.DataFrame, 
                                    historical_data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Calcule tous les KPI étendus
        
        Args:
            df: DataFrame avec les données actuelles
            historical_data: DataFrame avec les données historiques (optionnel)
            
        Returns:
            Dictionnaire avec tous les KPI étendus
        """
        try:
            kpis = {}
            
            # KPI 1: Taux d'évolution temporelle
            kpis['temporal_evolution'] = self.calculate_temporal_evolution(df, historical_data)
            
            # KPI 2: Corrélation sentiment-sujet
            kpis['sentiment_topic_correlation'] = self.calculate_sentiment_topic_correlation(df)
            
            # KPI 3: Temps moyen de traitement
            kpis['average_processing_time'] = self.calculate_average_processing_time(df)
            
            # KPI 4: Volume horaire d'activité
            kpis['hourly_activity_volume'] = self.calculate_hourly_activity(df)
            
            # KPI 5: Score global d'engagement
            kpis['global_engagement_score'] = self.calculate_global_engagement(df)
            
            # KPI 6: Distribution temporelle avancée
            kpis['advanced_temporal_distribution'] = self.calculate_advanced_temporal_distribution(df)
            
            # KPI 7: Analyse de satisfaction
            kpis['satisfaction_analysis'] = self.calculate_satisfaction_metrics(df)
            
            # KPI 8: Performance par catégorie
            kpis['category_performance'] = self.calculate_category_performance(df)
            
            # KPI 9: Taux de résolution
            kpis['resolution_rate'] = self.calculate_resolution_rate(df)
            
            # KPI 10: Score de prioritisation
            kpis['prioritization_score'] = self.calculate_prioritization_score(df)
            
            logger.info("Calcul des KPI étendus terminé avec succès")
            return kpis
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des KPI étendus: {str(e)}")
            return self._get_default_kpis()
    
    def calculate_temporal_evolution(self, df: pd.DataFrame, 
                                    historical_data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Calcule le taux d'évolution temporelle
        
        Args:
            df: DataFrame actuel
            historical_data: DataFrame historique
            
        Returns:
            Dict avec taux d'évolution et tendances
        """
        try:
            result = {
                'volume_evolution': {},
                'sentiment_evolution': {},
                'trend': 'stable',
                'growth_rate': 0.0
            }
            
            # Vérifier si on a une colonne date
            date_col = self._find_date_column(df)
            if not date_col:
                return result
            
            # Convertir en datetime
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            df_sorted = df.sort_values(date_col)
            
            # Calculer l'évolution par jour
            daily_volume = df_sorted.groupby(df_sorted[date_col].dt.date).size()
            
            if len(daily_volume) > 1:
                # Calculer le taux de croissance
                first_week = daily_volume.head(7).mean()
                last_week = daily_volume.tail(7).mean()
                
                if first_week > 0:
                    growth_rate = ((last_week - first_week) / first_week) * 100
                    result['growth_rate'] = round(growth_rate, 2)
                    
                    # Déterminer la tendance
                    if growth_rate > 10:
                        result['trend'] = 'hausse'
                    elif growth_rate < -10:
                        result['trend'] = 'baisse'
                    else:
                        result['trend'] = 'stable'
                
                # Évolution du volume
                result['volume_evolution'] = {
                    'daily_average': round(daily_volume.mean(), 1),
                    'daily_max': int(daily_volume.max()),
                    'daily_min': int(daily_volume.min()),
                    'daily_std': round(daily_volume.std(), 1)
                }
            
            # Évolution du sentiment si disponible
            if 'sentiment' in df.columns:
                sentiment_by_date = df.groupby([df[date_col].dt.date, 'sentiment']).size().unstack(fill_value=0)
                
                if not sentiment_by_date.empty:
                    result['sentiment_evolution'] = {
                        'positive_trend': self._calculate_trend(sentiment_by_date.get('positive', pd.Series())),
                        'negative_trend': self._calculate_trend(sentiment_by_date.get('negative', pd.Series())),
                        'neutral_trend': self._calculate_trend(sentiment_by_date.get('neutral', pd.Series()))
                    }
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur calcul évolution temporelle: {str(e)}")
            return {'volume_evolution': {}, 'sentiment_evolution': {}, 'trend': 'unknown', 'growth_rate': 0.0}
    
    def calculate_sentiment_topic_correlation(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calcule la corrélation entre sentiment et sujet
        
        Args:
            df: DataFrame avec colonnes 'sentiment' et 'category'/'theme'
            
        Returns:
            Dict avec matrices de corrélation et insights
        """
        try:
            result = {
                'correlation_matrix': {},
                'strongest_correlations': [],
                'insights': []
            }
            
            # Vérifier colonnes nécessaires
            sentiment_col = 'sentiment' if 'sentiment' in df.columns else None
            topic_col = 'category' if 'category' in df.columns else ('theme' if 'theme' in df.columns else None)
            
            if not sentiment_col or not topic_col:
                return result
            
            # Créer la matrice de corrélation
            correlation_data = pd.crosstab(df[topic_col], df[sentiment_col], normalize='index') * 100
            
            result['correlation_matrix'] = correlation_data.to_dict()
            
            # Trouver les corrélations les plus fortes
            correlations = []
            for topic in correlation_data.index:
                for sentiment in correlation_data.columns:
                    value = correlation_data.loc[topic, sentiment]
                    correlations.append({
                        'topic': topic,
                        'sentiment': sentiment,
                        'percentage': round(value, 2)
                    })
            
            # Trier et garder top 5
            correlations.sort(key=lambda x: x['percentage'], reverse=True)
            result['strongest_correlations'] = correlations[:5]
            
            # Générer des insights
            for corr in correlations[:3]:
                if corr['percentage'] > 50:
                    result['insights'].append(
                        f"{corr['topic']} est principalement {corr['sentiment']} ({corr['percentage']}%)"
                    )
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur calcul corrélation sentiment-sujet: {str(e)}")
            return {'correlation_matrix': {}, 'strongest_correlations': [], 'insights': []}
    
    def calculate_average_processing_time(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calcule le temps moyen de traitement
        
        Args:
            df: DataFrame avec colonnes de temps
            
        Returns:
            Dict avec statistiques de temps de traitement
        """
        try:
            result = {
                'average_time_seconds': 0,
                'average_time_formatted': '0s',
                'median_time_seconds': 0,
                'percentile_95': 0,
                'by_category': {}
            }
            
            # Chercher colonnes de temps
            created_col = self._find_column_by_names(df, ['created_at', 'date', 'timestamp', 'created'])
            resolved_col = self._find_column_by_names(df, ['resolved_at', 'closed_at', 'completed_at'])
            
            if created_col and resolved_col:
                # Calculer différence de temps
                df[created_col] = pd.to_datetime(df[created_col], errors='coerce')
                df[resolved_col] = pd.to_datetime(df[resolved_col], errors='coerce')
                
                df['processing_time'] = (df[resolved_col] - df[created_col]).dt.total_seconds()
                processing_times = df['processing_time'].dropna()
                
                if len(processing_times) > 0:
                    result['average_time_seconds'] = round(processing_times.mean(), 1)
                    result['median_time_seconds'] = round(processing_times.median(), 1)
                    result['percentile_95'] = round(processing_times.quantile(0.95), 1)
                    result['average_time_formatted'] = self._format_time(processing_times.mean())
            else:
                # Estimation basée sur le volume
                avg_time = len(df) * 2.5  # 2.5 secondes par tweet
                result['average_time_seconds'] = avg_time
                result['average_time_formatted'] = self._format_time(avg_time)
            
            # Temps par catégorie si disponible
            if 'category' in df.columns and 'processing_time' in df.columns:
                category_times = df.groupby('category')['processing_time'].mean()
                result['by_category'] = {
                    cat: self._format_time(time) 
                    for cat, time in category_times.items()
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur calcul temps de traitement: {str(e)}")
            return result
    
    def calculate_hourly_activity(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calcule le volume d'activité par heure
        
        Args:
            df: DataFrame avec colonne date/timestamp
            
        Returns:
            Dict avec distribution horaire et heures de pointe
        """
        try:
            result = {
                'hourly_distribution': {},
                'peak_hours': [],
                'quiet_hours': [],
                'busiest_hour': None,
                'quietest_hour': None
            }
            
            date_col = self._find_date_column(df)
            if not date_col:
                return result
            
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            
            # Distribution par heure
            hourly_counts = df[date_col].dt.hour.value_counts().sort_index()
            result['hourly_distribution'] = hourly_counts.to_dict()
            
            # Identifier heures de pointe (top 3)
            top_hours = hourly_counts.nlargest(3)
            result['peak_hours'] = [
                {'hour': int(hour), 'count': int(count)} 
                for hour, count in top_hours.items()
            ]
            
            # Identifier heures calmes (bottom 3)
            quiet_hours = hourly_counts.nsmallest(3)
            result['quiet_hours'] = [
                {'hour': int(hour), 'count': int(count)} 
                for hour, count in quiet_hours.items()
            ]
            
            result['busiest_hour'] = int(hourly_counts.idxmax())
            result['quietest_hour'] = int(hourly_counts.idxmin())
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur calcul activité horaire: {str(e)}")
            return result
    
    def calculate_global_engagement(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calcule le score global d'engagement
        
        Args:
            df: DataFrame avec métriques d'engagement
            
        Returns:
            Dict avec score et détails d'engagement
        """
        try:
            result = {
                'global_score': 0,
                'components': {},
                'rating': 'Faible',
                'details': {}
            }
            
            scores = []
            
            # Score de réponse
            if 'response_time' in df.columns:
                avg_response = df['response_time'].mean()
                response_score = max(0, 100 - (avg_response / 3600 * 10))  # Pénalité par heure
                scores.append(response_score)
                result['components']['response_score'] = round(response_score, 1)
            
            # Score de sentiment
            if 'sentiment' in df.columns:
                sentiment_counts = df['sentiment'].value_counts(normalize=True)
                positive_ratio = sentiment_counts.get('positive', 0)
                negative_ratio = sentiment_counts.get('negative', 0)
                sentiment_score = (positive_ratio * 100) - (negative_ratio * 30)
                scores.append(max(0, sentiment_score))
                result['components']['sentiment_score'] = round(sentiment_score, 1)
            
            # Score de résolution
            if 'status' in df.columns:
                resolved_ratio = (df['status'] == 'resolved').sum() / len(df)
                resolution_score = resolved_ratio * 100
                scores.append(resolution_score)
                result['components']['resolution_score'] = round(resolution_score, 1)
            
            # Score d'interaction (likes, retweets, etc.)
            interaction_cols = ['retweet_count', 'favorite_count', 'reply_count']
            present_cols = [col for col in interaction_cols if col in df.columns]
            
            if present_cols:
                total_interactions = df[present_cols].sum().sum()
                interaction_score = min(100, (total_interactions / len(df)) * 10)
                scores.append(interaction_score)
                result['components']['interaction_score'] = round(interaction_score, 1)
            
            # Calculer score global
            if scores:
                global_score = sum(scores) / len(scores)
                result['global_score'] = round(global_score, 1)
                
                # Rating
                if global_score >= 80:
                    result['rating'] = 'Excellent'
                elif global_score >= 60:
                    result['rating'] = 'Bon'
                elif global_score >= 40:
                    result['rating'] = 'Moyen'
                else:
                    result['rating'] = 'Faible'
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur calcul engagement global: {str(e)}")
            return result
    
    def calculate_advanced_temporal_distribution(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calcule la distribution temporelle avancée"""
        try:
            result = {
                'by_day_of_week': {},
                'by_month': {},
                'by_hour': {},
                'patterns': []
            }
            
            date_col = self._find_date_column(df)
            if not date_col:
                return result
            
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            
            # Par jour de la semaine
            day_names = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
            day_counts = df[date_col].dt.dayofweek.value_counts().sort_index()
            result['by_day_of_week'] = {
                day_names[day]: int(count) 
                for day, count in day_counts.items()
            }
            
            # Par mois
            month_counts = df[date_col].dt.month.value_counts().sort_index()
            month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 
                          'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
            result['by_month'] = {
                month_names[month-1]: int(count) 
                for month, count in month_counts.items()
            }
            
            # Détecter des patterns
            if day_counts.max() > day_counts.mean() * 1.5:
                busiest_day = day_names[day_counts.idxmax()]
                result['patterns'].append(f"Pic d'activité le {busiest_day}")
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur calcul distribution temporelle: {str(e)}")
            return result
    
    def calculate_satisfaction_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calcule les métriques de satisfaction"""
        try:
            result = {
                'overall_satisfaction': 0,
                'satisfaction_rate': 0,
                'alert_needed': False,
                'low_satisfaction_count': 0
            }
            
            # Calculer depuis sentiment
            if 'sentiment' in df.columns:
                sentiment_counts = df['sentiment'].value_counts()
                total = len(df)
                
                positive = sentiment_counts.get('positive', 0)
                negative = sentiment_counts.get('negative', 0)
                
                satisfaction_rate = (positive / total * 100) if total > 0 else 0
                result['satisfaction_rate'] = round(satisfaction_rate, 1)
                result['overall_satisfaction'] = round(satisfaction_rate, 1)
                result['low_satisfaction_count'] = int(negative)
                
                # Alerte si < 70%
                if satisfaction_rate < 70:
                    result['alert_needed'] = True
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur calcul satisfaction: {str(e)}")
            return result
    
    def calculate_category_performance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calcule la performance par catégorie"""
        try:
            result = {
                'by_category': {},
                'best_category': None,
                'worst_category': None
            }
            
            if 'category' not in df.columns:
                return result
            
            categories = df['category'].value_counts()
            
            for category in categories.index:
                cat_df = df[df['category'] == category]
                
                # Calculer métriques pour cette catégorie
                metrics = {
                    'count': len(cat_df),
                    'percentage': round((len(cat_df) / len(df)) * 100, 1)
                }
                
                # Sentiment si disponible
                if 'sentiment' in df.columns:
                    positive_ratio = (cat_df['sentiment'] == 'positive').sum() / len(cat_df)
                    metrics['positive_ratio'] = round(positive_ratio * 100, 1)
                
                result['by_category'][category] = metrics
            
            # Identifier meilleure/pire
            if result['by_category']:
                sorted_cats = sorted(
                    result['by_category'].items(),
                    key=lambda x: x[1].get('positive_ratio', 0),
                    reverse=True
                )
                result['best_category'] = sorted_cats[0][0] if sorted_cats else None
                result['worst_category'] = sorted_cats[-1][0] if sorted_cats else None
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur calcul performance catégorie: {str(e)}")
            return result
    
    def calculate_resolution_rate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calcule le taux de résolution"""
        try:
            result = {
                'total_resolved': 0,
                'resolution_rate': 0,
                'pending_count': 0,
                'average_resolution_time': 0
            }
            
            if 'status' in df.columns:
                resolved = (df['status'] == 'resolved').sum()
                pending = (df['status'] == 'pending').sum()
                
                result['total_resolved'] = int(resolved)
                result['pending_count'] = int(pending)
                result['resolution_rate'] = round((resolved / len(df)) * 100, 1)
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur calcul taux résolution: {str(e)}")
            return result
    
    def calculate_prioritization_score(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calcule le score de prioritisation"""
        try:
            result = {
                'priority_distribution': {},
                'urgent_ratio': 0,
                'prioritization_efficiency': 0
            }
            
            if 'priority' in df.columns or 'urgency' in df.columns:
                priority_col = 'priority' if 'priority' in df.columns else 'urgency'
                priority_counts = df[priority_col].value_counts()
                
                result['priority_distribution'] = priority_counts.to_dict()
                
                urgent = priority_counts.get('high', 0) + priority_counts.get('urgent', 0)
                result['urgent_ratio'] = round((urgent / len(df)) * 100, 1)
                
                # Score d'efficacité basé sur la distribution
                if urgent / len(df) > 0.5:
                    result['prioritization_efficiency'] = 50  # Trop d'urgent
                else:
                    result['prioritization_efficiency'] = 80
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur calcul score prioritisation: {str(e)}")
            return result
    
    # === Fonctions utilitaires ===
    
    def _find_date_column(self, df: pd.DataFrame) -> Optional[str]:
        """Trouve la colonne de date dans le DataFrame"""
        date_cols = ['date', 'created_at', 'timestamp', 'created', 'datetime']
        for col in date_cols:
            if col in df.columns:
                return col
        return None
    
    def _find_column_by_names(self, df: pd.DataFrame, names: List[str]) -> Optional[str]:
        """Trouve une colonne par liste de noms possibles"""
        for name in names:
            if name in df.columns:
                return name
        return None
    
    def _calculate_trend(self, series: pd.Series) -> str:
        """Calcule la tendance d'une série temporelle"""
        if len(series) < 2:
            return 'stable'
        
        first_half = series.iloc[:len(series)//2].mean()
        second_half = series.iloc[len(series)//2:].mean()
        
        if second_half > first_half * 1.1:
            return 'hausse'
        elif second_half < first_half * 0.9:
            return 'baisse'
        return 'stable'
    
    def _format_time(self, seconds: float) -> str:
        """Formate un temps en secondes vers format lisible"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds/60)}min"
        elif seconds < 86400:
            return f"{round(seconds/3600, 1)}h"
        else:
            return f"{round(seconds/86400, 1)}j"
    
    def _get_default_kpis(self) -> Dict[str, Any]:
        """Retourne des KPI par défaut en cas d'erreur"""
        return {
            'temporal_evolution': {},
            'sentiment_topic_correlation': {},
            'average_processing_time': {},
            'hourly_activity_volume': {},
            'global_engagement_score': {},
            'advanced_temporal_distribution': {},
            'satisfaction_analysis': {},
            'category_performance': {},
            'resolution_rate': {},
            'prioritization_score': {}
        }


# Instance globale
extended_kpi_calculator = ExtendedKPICalculator()


def get_extended_kpi_calculator() -> ExtendedKPICalculator:
    """Retourne l'instance du calculateur de KPI étendus"""
    return extended_kpi_calculator

