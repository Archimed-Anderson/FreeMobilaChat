"""
Advanced Metrics Service - Service de calcul des métriques avancées
Module d'extension des KPI existants avec de nouvelles métriques de performance

Ce module fournit des métriques avancées pour l'analyse des tweets :
- Taux d'évolution temporelle
- Corrélation sentiment-sujet
- Temps moyen de traitement
- Volume horaire d'activité
- Score global d'engagement
- Et bien plus...

Author: FreeMobilaChat Team
Date: 2025
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class AdvancedMetrics:
    """Calculateur de métriques avancées pour l'analyse des tweets"""
    
    def __init__(self):
        """Initialise le calculateur de métriques"""
        self.history = []
        self.baseline_metrics = {}
        
    def calculate_all_metrics(self, df: pd.DataFrame, 
                              historical_df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Calcule toutes les métriques avancées
        
        Args:
            df: DataFrame avec les données actuelles
            historical_df: DataFrame avec les données historiques (optionnel)
            
        Returns:
            Dictionnaire avec toutes les métriques avancées organisées
        """
        try:
            logger.info(f"Calcul des métriques avancées pour {len(df)} tweets")
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'data_info': self._get_data_info(df),
                'core_metrics': self._calculate_core_metrics(df),
                'temporal_metrics': self._calculate_temporal_metrics(df, historical_df),
                'engagement_metrics': self._calculate_engagement_metrics(df),
                'sentiment_metrics': self._calculate_sentiment_metrics(df),
                'performance_metrics': self._calculate_performance_metrics(df),
                'quality_metrics': self._calculate_quality_metrics(df),
                'alerts': self._generate_alerts(df)
            }
            
            logger.info("Calcul des métriques avancées terminé avec succès")
            return metrics
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des métriques: {str(e)}", exc_info=True)
            return self._get_default_metrics()
    
    def _get_data_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Retourne les informations de base sur les données"""
        return {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'columns': list(df.columns),
            'date_range': self._get_date_range(df),
            'memory_usage_mb': round(df.memory_usage(deep=True).sum() / (1024**2), 2)
        }
    
    def _calculate_core_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        KPI 1-2: Métriques de base et d'évolution
        
        Calcule:
        - Total de tweets
        - Répartition des sentiments
        - Distribution d'urgence
        - Top sujets
        - Répartition des types (plaintes/questions/demandes)
        """
        metrics = {
            'total_tweets': len(df),
            'sentiment_distribution': {},
            'urgency_distribution': {},
            'top_topics': {},
            'type_distribution': {},
            'confidence_score': 0.0
        }
        
        # Distribution des sentiments
        if 'sentiment' in df.columns:
            sentiment_counts = df['sentiment'].value_counts()
            total = len(df)
            metrics['sentiment_distribution'] = {
                'counts': sentiment_counts.to_dict(),
                'percentages': {
                    k: round(v / total * 100, 2) 
                    for k, v in sentiment_counts.items()
                }
            }
        
        # Distribution d'urgence
        urgency_col = self._find_column(df, ['urgency', 'priority', 'priorite'])
        if urgency_col:
            urgency_counts = df[urgency_col].value_counts()
            total = len(df)
            metrics['urgency_distribution'] = {
                'counts': urgency_counts.to_dict(),
                'percentages': {
                    k: round(v / total * 100, 2) 
                    for k, v in urgency_counts.items()
                }
            }
        
        # Top sujets/catégories
        category_col = self._find_column(df, ['category', 'theme', 'sujet', 'topic'])
        if category_col:
            top_categories = df[category_col].value_counts().head(10)
            metrics['top_topics'] = {
                'categories': top_categories.to_dict(),
                'total_categories': df[category_col].nunique()
            }
        
        # Répartition des types (plaintes, questions, demandes)
        type_col = self._find_column(df, ['type', 'request_type', 'type_demande'])
        if type_col:
            type_counts = df[type_col].value_counts()
            total = len(df)
            metrics['type_distribution'] = {
                'counts': type_counts.to_dict(),
                'percentages': {
                    k: round(v / total * 100, 2) 
                    for k, v in type_counts.items()
                }
            }
        
        # Score de confiance moyen
        confidence_col = self._find_column(df, ['confidence', 'confidence_score', 'score'])
        if confidence_col:
            metrics['confidence_score'] = round(df[confidence_col].mean(), 2)
        
        return metrics
    
    def _calculate_temporal_metrics(self, df: pd.DataFrame, 
                                    historical_df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        KPI 3-4: Métriques temporelles avancées
        
        Calcule:
        - Taux d'évolution temporelle
        - Volume horaire d'activité
        - Patterns temporels
        - Tendances
        """
        metrics = {
            'evolution_rate': {},
            'hourly_volume': {},
            'daily_volume': {},
            'weekly_pattern': {},
            'peak_hours': [],
            'quiet_hours': [],
            'trend': 'stable',
            'growth_rate_percentage': 0.0
        }
        
        date_col = self._find_date_column(df)
        if not date_col:
            logger.warning("Pas de colonne de date trouvée")
            return metrics
        
        # Convertir en datetime
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df_clean = df.dropna(subset=[date_col])
        
        if df_clean.empty:
            return metrics
        
        # Volume par heure
        hourly_counts = df_clean.groupby(df_clean[date_col].dt.hour).size()
        metrics['hourly_volume'] = {
            'distribution': hourly_counts.to_dict(),
            'mean': round(hourly_counts.mean(), 1),
            'std': round(hourly_counts.std(), 1)
        }
        
        # Heures de pointe (top 3)
        top_hours = hourly_counts.nlargest(3)
        metrics['peak_hours'] = [
            {'hour': int(h), 'count': int(c), 'percentage': round(c/len(df_clean)*100, 1)}
            for h, c in top_hours.items()
        ]
        
        # Heures calmes (bottom 3)
        quiet_hours = hourly_counts.nsmallest(3)
        metrics['quiet_hours'] = [
            {'hour': int(h), 'count': int(c), 'percentage': round(c/len(df_clean)*100, 1)}
            for h, c in quiet_hours.items()
        ]
        
        # Volume par jour
        daily_counts = df_clean.groupby(df_clean[date_col].dt.date).size()
        metrics['daily_volume'] = {
            'distribution': {str(k): int(v) for k, v in daily_counts.items()},
            'mean': round(daily_counts.mean(), 1),
            'std': round(daily_counts.std(), 1),
            'min': int(daily_counts.min()),
            'max': int(daily_counts.max())
        }
        
        # Pattern hebdomadaire
        day_names = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        weekly_counts = df_clean.groupby(df_clean[date_col].dt.dayofweek).size()
        metrics['weekly_pattern'] = {
            day_names[i]: int(weekly_counts.get(i, 0))
            for i in range(7)
        }
        
        # Taux d'évolution et tendance
        if len(daily_counts) > 7:
            first_week_avg = daily_counts.head(7).mean()
            last_week_avg = daily_counts.tail(7).mean()
            
            if first_week_avg > 0:
                growth_rate = ((last_week_avg - first_week_avg) / first_week_avg) * 100
                metrics['growth_rate_percentage'] = round(growth_rate, 2)
                
                if growth_rate > 10:
                    metrics['trend'] = 'hausse'
                elif growth_rate < -10:
                    metrics['trend'] = 'baisse'
                else:
                    metrics['trend'] = 'stable'
            
            metrics['evolution_rate'] = {
                'first_week_average': round(first_week_avg, 1),
                'last_week_average': round(last_week_avg, 1),
                'change': round(last_week_avg - first_week_avg, 1),
                'change_percentage': round(growth_rate, 2) if first_week_avg > 0 else 0
            }
        
        # Comparaison avec historique si disponible
        if historical_df is not None and not historical_df.empty:
            hist_date_col = self._find_date_column(historical_df)
            if hist_date_col:
                historical_df[hist_date_col] = pd.to_datetime(
                    historical_df[hist_date_col], errors='coerce'
                )
                hist_count = len(historical_df)
                current_count = len(df_clean)
                
                if hist_count > 0:
                    evolution_vs_historical = ((current_count - hist_count) / hist_count) * 100
                    metrics['vs_historical'] = {
                        'historical_count': hist_count,
                        'current_count': current_count,
                        'evolution_percentage': round(evolution_vs_historical, 2)
                    }
        
        return metrics
    
    def _calculate_engagement_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        KPI 5: Score global d'engagement
        
        Calcule:
        - Score global d'engagement
        - Métriques d'interaction
        - Taux de réponse
        - Temps de traitement
        """
        metrics = {
            'global_score': 0.0,
            'rating': 'Faible',
            'components': {},
            'interaction_stats': {},
            'response_stats': {}
        }
        
        scores = []
        
        # Score de sentiment
        if 'sentiment' in df.columns:
            sentiment_counts = df['sentiment'].value_counts(normalize=True)
            positive_ratio = sentiment_counts.get('positive', 0)
            negative_ratio = sentiment_counts.get('negative', 0)
            neutral_ratio = sentiment_counts.get('neutral', 0)
            
            # Score basé sur les sentiments (positif +100, neutre +30, négatif -50)
            sentiment_score = (positive_ratio * 100) + (neutral_ratio * 30) - (negative_ratio * 50)
            sentiment_score = max(0, min(100, sentiment_score))
            
            scores.append(sentiment_score)
            metrics['components']['sentiment_score'] = round(sentiment_score, 1)
        
        # Score de réactivité/réponse
        response_col = self._find_column(df, ['response_time', 'temps_reponse'])
        if response_col:
            avg_response_time = df[response_col].mean()
            # Score inversement proportionnel au temps (1h = 95, 24h = 50, 48h+ = 0)
            response_score = max(0, 100 - (avg_response_time / 3600 * 2))
            scores.append(response_score)
            metrics['components']['response_score'] = round(response_score, 1)
            metrics['response_stats'] = {
                'average_hours': round(avg_response_time / 3600, 1),
                'median_hours': round(df[response_col].median() / 3600, 1)
            }
        
        # Score de résolution
        status_col = self._find_column(df, ['status', 'statut', 'etat'])
        if status_col:
            resolved_values = ['resolved', 'résolu', 'closed', 'fermé', 'terminé']
            resolved_count = df[status_col].isin(resolved_values).sum()
            resolution_ratio = resolved_count / len(df)
            resolution_score = resolution_ratio * 100
            
            scores.append(resolution_score)
            metrics['components']['resolution_score'] = round(resolution_score, 1)
        
        # Score d'interaction (likes, retweets, replies)
        interaction_cols = ['retweet_count', 'favorite_count', 'reply_count', 'likes', 'shares']
        present_cols = [col for col in interaction_cols if col in df.columns]
        
        if present_cols:
            total_interactions = df[present_cols].sum().sum()
            avg_interactions = total_interactions / len(df)
            # Score basé sur moyenne d'interactions (10+ interactions = 100%)
            interaction_score = min(100, avg_interactions * 10)
            
            scores.append(interaction_score)
            metrics['components']['interaction_score'] = round(interaction_score, 1)
            metrics['interaction_stats'] = {
                'total': int(total_interactions),
                'average_per_tweet': round(avg_interactions, 2)
            }
        
        # Calcul du score global
        if scores:
            global_score = sum(scores) / len(scores)
            metrics['global_score'] = round(global_score, 1)
            
            # Attribution du rating
            if global_score >= 80:
                metrics['rating'] = 'Excellent'
            elif global_score >= 65:
                metrics['rating'] = 'Bon'
            elif global_score >= 50:
                metrics['rating'] = 'Moyen'
            else:
                metrics['rating'] = 'Faible'
        
        return metrics
    
    def _calculate_sentiment_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        KPI 6: Métriques de sentiment avancées
        
        Calcule:
        - Corrélation sentiment-sujet
        - Évolution du sentiment
        - Analyse par catégorie
        """
        metrics = {
            'correlation_matrix': {},
            'strongest_correlations': [],
            'sentiment_by_category': {},
            'insights': []
        }
        
        if 'sentiment' not in df.columns:
            return metrics
        
        # Corrélation sentiment-sujet
        category_col = self._find_column(df, ['category', 'theme', 'sujet', 'topic'])
        if category_col:
            # Créer matrice de corrélation
            correlation_data = pd.crosstab(
                df[category_col], 
                df['sentiment'], 
                normalize='index'
            ) * 100
            
            metrics['correlation_matrix'] = correlation_data.to_dict()
            
            # Trouver les corrélations les plus fortes
            correlations = []
            for category in correlation_data.index:
                for sentiment in correlation_data.columns:
                    value = correlation_data.loc[category, sentiment]
                    correlations.append({
                        'category': category,
                        'sentiment': sentiment,
                        'percentage': round(value, 2)
                    })
            
            # Trier et garder top 10
            correlations.sort(key=lambda x: x['percentage'], reverse=True)
            metrics['strongest_correlations'] = correlations[:10]
            
            # Analyse par catégorie
            for category in df[category_col].unique():
                cat_df = df[df[category_col] == category]
                sentiment_dist = cat_df['sentiment'].value_counts(normalize=True) * 100
                
                metrics['sentiment_by_category'][category] = {
                    'distribution': sentiment_dist.to_dict(),
                    'dominant_sentiment': sentiment_dist.idxmax(),
                    'count': len(cat_df)
                }
            
            # Générer des insights
            for corr in correlations[:5]:
                if corr['percentage'] > 60:
                    metrics['insights'].append(
                        f"⚠️ {corr['category']} est majoritairement {corr['sentiment']} ({corr['percentage']}%)"
                    )
        
        return metrics
    
    def _calculate_performance_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        KPI 7: Métriques de performance
        
        Calcule:
        - Temps moyen de traitement
        - Taux de résolution
        - Efficacité par agent
        """
        metrics = {
            'processing_time': {},
            'resolution_rate': {},
            'agent_performance': {},
            'efficiency_score': 0.0
        }
        
        # Temps de traitement
        created_col = self._find_column(df, ['created_at', 'date', 'timestamp', 'date_creation'])
        resolved_col = self._find_column(df, ['resolved_at', 'closed_at', 'date_resolution'])
        
        if created_col and resolved_col:
            df_copy = df.copy()
            df_copy[created_col] = pd.to_datetime(df_copy[created_col], errors='coerce')
            df_copy[resolved_col] = pd.to_datetime(df_copy[resolved_col], errors='coerce')
            
            df_copy['processing_time'] = (
                df_copy[resolved_col] - df_copy[created_col]
            ).dt.total_seconds()
            
            processing_times = df_copy['processing_time'].dropna()
            
            if len(processing_times) > 0:
                metrics['processing_time'] = {
                    'average_seconds': round(processing_times.mean(), 1),
                    'average_formatted': self._format_duration(processing_times.mean()),
                    'median_seconds': round(processing_times.median(), 1),
                    'median_formatted': self._format_duration(processing_times.median()),
                    'percentile_90': round(processing_times.quantile(0.9), 1),
                    'min': round(processing_times.min(), 1),
                    'max': round(processing_times.max(), 1)
                }
        else:
            # Estimation basée sur le volume (2.5s par tweet)
            estimated_time = len(df) * 2.5
            metrics['processing_time'] = {
                'estimated_seconds': estimated_time,
                'estimated_formatted': self._format_duration(estimated_time),
                'note': 'Estimation basée sur le volume'
            }
        
        # Taux de résolution
        status_col = self._find_column(df, ['status', 'statut', 'etat'])
        if status_col:
            resolved_values = ['resolved', 'résolu', 'closed', 'fermé', 'terminé']
            resolved_count = df[status_col].isin(resolved_values).sum()
            pending_values = ['pending', 'en_attente', 'open', 'ouvert']
            pending_count = df[status_col].isin(pending_values).sum()
            
            metrics['resolution_rate'] = {
                'resolved_count': int(resolved_count),
                'pending_count': int(pending_count),
                'total_count': len(df),
                'resolution_percentage': round(resolved_count / len(df) * 100, 1),
                'pending_percentage': round(pending_count / len(df) * 100, 1)
            }
        
        # Performance par agent
        agent_col = self._find_column(df, ['agent', 'assigned_to', 'agent_id', 'responsable'])
        if agent_col:
            agent_stats = {}
            for agent in df[agent_col].unique():
                if pd.isna(agent):
                    continue
                    
                agent_df = df[df[agent_col] == agent]
                
                agent_stats[str(agent)] = {
                    'total_tickets': len(agent_df),
                    'resolved': 0,
                    'pending': 0,
                    'average_processing_time': 0
                }
                
                if status_col:
                    agent_stats[str(agent)]['resolved'] = int(
                        agent_df[status_col].isin(resolved_values).sum()
                    )
                    agent_stats[str(agent)]['pending'] = int(
                        agent_df[status_col].isin(pending_values).sum()
                    )
                
                if 'processing_time' in agent_df.columns:
                    avg_time = agent_df['processing_time'].mean()
                    agent_stats[str(agent)]['average_processing_time'] = round(avg_time, 1)
            
            metrics['agent_performance'] = agent_stats
        
        # Score d'efficacité global
        efficiency_components = []
        
        if metrics['resolution_rate'].get('resolution_percentage'):
            efficiency_components.append(metrics['resolution_rate']['resolution_percentage'])
        
        if metrics['processing_time'].get('average_seconds'):
            # Score inversement proportionnel au temps (plus rapide = meilleur)
            avg_time_hours = metrics['processing_time']['average_seconds'] / 3600
            time_score = max(0, 100 - (avg_time_hours * 5))
            efficiency_components.append(time_score)
        
        if efficiency_components:
            metrics['efficiency_score'] = round(sum(efficiency_components) / len(efficiency_components), 1)
        
        return metrics
    
    def _calculate_quality_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        KPI 8: Métriques de qualité des données
        
        Calcule:
        - Complétude des données
        - Cohérence
        - Score de qualité global
        """
        metrics = {
            'completeness': {},
            'consistency': {},
            'quality_score': 0.0,
            'data_issues': []
        }
        
        # Complétude
        total_cells = len(df) * len(df.columns)
        null_cells = df.isnull().sum().sum()
        completeness_percentage = ((total_cells - null_cells) / total_cells) * 100
        
        metrics['completeness'] = {
            'total_cells': total_cells,
            'null_cells': int(null_cells),
            'filled_cells': total_cells - int(null_cells),
            'percentage': round(completeness_percentage, 2)
        }
        
        # Cohérence - dupli cats
        duplicate_count = df.duplicated().sum()
        duplicate_percentage = (duplicate_count / len(df)) * 100
        
        metrics['consistency'] = {
            'total_rows': len(df),
            'duplicate_rows': int(duplicate_count),
            'unique_rows': len(df) - int(duplicate_count),
            'duplicate_percentage': round(duplicate_percentage, 2),
            'uniqueness_percentage': round(100 - duplicate_percentage, 2)
        }
        
        # Score de qualité global
        quality_components = [
            completeness_percentage,
            100 - duplicate_percentage
        ]
        
        # Vérifier la présence de colonnes essentielles
        essential_cols = ['text', 'content', 'message', 'tweet']
        has_text_col = any(col in df.columns for col in essential_cols)
        if has_text_col:
            quality_components.append(100)
        else:
            quality_components.append(50)
            metrics['data_issues'].append("⚠️ Aucune colonne de texte détectée")
        
        # Vérifier colonnes temporelles
        date_col = self._find_date_column(df)
        if date_col:
            quality_components.append(100)
        else:
            quality_components.append(50)
            metrics['data_issues'].append("⚠️ Aucune colonne de date détectée")
        
        metrics['quality_score'] = round(sum(quality_components) / len(quality_components), 1)
        
        # Ajouter des recommandations
        if completeness_percentage < 90:
            metrics['data_issues'].append(
                f"⚠️ Taux de complétude faible ({completeness_percentage:.1f}%) - nettoyage recommandé"
            )
        
        if duplicate_percentage > 5:
            metrics['data_issues'].append(
                f"⚠️ Présence de doublons ({duplicate_percentage:.1f}%) - déduplication recommandée"
            )
        
        return metrics
    
    def _generate_alerts(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Génère des alertes automatiques basées sur les données
        
        Returns:
            Liste d'alertes avec niveau de sévérité
        """
        alerts = []
        
        # Alerte satisfaction < 70%
        if 'sentiment' in df.columns:
            sentiment_counts = df['sentiment'].value_counts(normalize=True) * 100
            positive_percentage = sentiment_counts.get('positive', 0)
            negative_percentage = sentiment_counts.get('negative', 0)
            
            satisfaction_score = positive_percentage
            
            if satisfaction_score < 70:
                alerts.append({
                    'type': 'satisfaction',
                    'level': 'high' if satisfaction_score < 50 else 'medium',
                    'title': 'Satisfaction Client Faible',
                    'message': f"Le taux de satisfaction est de {satisfaction_score:.1f}% (seuil: 70%)",
                    'recommendation': "Analyser les causes des sentiments négatifs et mettre en place des actions correctives"
                })
            
            if negative_percentage > 30:
                alerts.append({
                    'type': 'negative_sentiment',
                    'level': 'high',
                    'title': 'Taux de Sentiment Négatif Élevé',
                    'message': f"Les sentiments négatifs représentent {negative_percentage:.1f}% des tweets",
                    'recommendation': "Intervention urgente recommandée pour traiter les problèmes récurrents"
                })
        
        # Alerte volume anormal
        date_col = self._find_date_column(df)
        if date_col:
            df_copy = df.copy()
            df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors='coerce')
            daily_counts = df_copy.groupby(df_copy[date_col].dt.date).size()
            
            if len(daily_counts) > 7:
                mean_volume = daily_counts.mean()
                std_volume = daily_counts.std()
                recent_volume = daily_counts.tail(3).mean()
                
                if recent_volume > mean_volume + (2 * std_volume):
                    alerts.append({
                        'type': 'volume_spike',
                        'level': 'medium',
                        'title': 'Pic de Volume Détecté',
                        'message': f"Le volume récent ({recent_volume:.0f}/jour) est significativement plus élevé que la moyenne ({mean_volume:.0f}/jour)",
                        'recommendation': "Vérifier s'il y a un événement particulier ou un problème système"
                    })
                elif recent_volume < mean_volume - (2 * std_volume):
                    alerts.append({
                        'type': 'volume_drop',
                        'level': 'medium',
                        'title': 'Chute de Volume Détectée',
                        'message': f"Le volume récent ({recent_volume:.0f}/jour) est significativement plus bas que la moyenne ({mean_volume:.0f}/jour)",
                        'recommendation': "Vérifier la collecte des données et l'engagement utilisateur"
                    })
        
        # Alerte tickets en attente
        status_col = self._find_column(df, ['status', 'statut', 'etat'])
        if status_col:
            pending_values = ['pending', 'en_attente', 'open', 'ouvert']
            pending_count = df[status_col].isin(pending_values).sum()
            pending_percentage = (pending_count / len(df)) * 100
            
            if pending_percentage > 50:
                alerts.append({
                    'type': 'pending_tickets',
                    'level': 'high' if pending_percentage > 70 else 'medium',
                    'title': 'Taux Élevé de Tickets en Attente',
                    'message': f"{pending_count} tickets en attente ({pending_percentage:.1f}%)",
                    'recommendation': "Augmenter les ressources de support ou revoir la priorisation"
                })
        
        # Alerte urgence haute
        urgency_col = self._find_column(df, ['urgency', 'priority', 'priorite'])
        if urgency_col:
            high_urgency_values = ['high', 'haute', 'urgent', 'critique']
            high_urgency_count = df[urgency_col].astype(str).str.lower().isin(high_urgency_values).sum()
            high_urgency_percentage = (high_urgency_count / len(df)) * 100
            
            if high_urgency_count > 0 and high_urgency_percentage > 20:
                alerts.append({
                    'type': 'high_urgency',
                    'level': 'high',
                    'title': 'Nombre Élevé de Tickets Urgents',
                    'message': f"{high_urgency_count} tickets marqués comme urgents ({high_urgency_percentage:.1f}%)",
                    'recommendation': "Prioriser le traitement des tickets urgents"
                })
        
        return alerts
    
    # === Fonctions utilitaires ===
    
    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
        """Trouve une colonne parmi plusieurs noms possibles"""
        df_columns_lower = {col.lower(): col for col in df.columns}
        for name in possible_names:
            if name.lower() in df_columns_lower:
                return df_columns_lower[name.lower()]
        return None
    
    def _find_date_column(self, df: pd.DataFrame) -> Optional[str]:
        """Trouve la colonne de date dans le DataFrame"""
        date_names = ['date', 'created_at', 'timestamp', 'datetime', 'created', 'date_creation']
        return self._find_column(df, date_names)
    
    def _get_date_range(self, df: pd.DataFrame) -> Optional[Dict[str, str]]:
        """Retourne la plage de dates du DataFrame"""
        date_col = self._find_date_column(df)
        if date_col:
            try:
                df_copy = df.copy()
                df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors='coerce')
                df_clean = df_copy.dropna(subset=[date_col])
                
                if not df_clean.empty:
                    return {
                        'start': df_clean[date_col].min().isoformat(),
                        'end': df_clean[date_col].max().isoformat(),
                        'duration_days': (df_clean[date_col].max() - df_clean[date_col].min()).days
                    }
            except Exception as e:
                logger.warning(f"Erreur lors du calcul de la plage de dates: {e}")
        
        return None
    
    def _format_duration(self, seconds: float) -> str:
        """Formate une durée en secondes vers un format lisible"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds / 60)}min"
        elif seconds < 86400:
            hours = seconds / 3600
            return f"{hours:.1f}h"
        else:
            days = seconds / 86400
            return f"{days:.1f}j"
    
    def _get_default_metrics(self) -> Dict[str, Any]:
        """Retourne des métriques par défaut en cas d'erreur"""
        return {
            'timestamp': datetime.now().isoformat(),
            'data_info': {},
            'core_metrics': {},
            'temporal_metrics': {},
            'engagement_metrics': {},
            'sentiment_metrics': {},
            'performance_metrics': {},
            'quality_metrics': {},
            'alerts': []
        }


# Instance globale
_advanced_metrics_instance = None

def get_advanced_metrics() -> AdvancedMetrics:
    """Retourne l'instance singleton du calculateur de métriques avancées"""
    global _advanced_metrics_instance
    if _advanced_metrics_instance is None:
        _advanced_metrics_instance = AdvancedMetrics()
    return _advanced_metrics_instance


