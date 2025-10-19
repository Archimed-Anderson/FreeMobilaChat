"""
Moteur de visualisations intelligentes et contextuelles
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class SmartVisualizationEngine:
    """
    Sélection et génération automatique de visualisations contextuelles
    """
    
    def __init__(self):
        self.chart_templates = {
            'financial_data': self._get_financial_charts(),
            'sales_data': self._get_sales_charts(),
            'hr_data': self._get_hr_charts(),
            'marketing_data': self._get_marketing_charts(),
            'ecommerce_data': self._get_ecommerce_charts(),
            'logistics_data': self._get_logistics_charts(),
            'healthcare_data': self._get_healthcare_charts(),
            'education_data': self._get_education_charts(),
            'general': self._get_general_charts()
        }
        
        self.color_palettes = {
            'free_mobile': ['#CC0000', '#8B0000', '#FF6B6B', '#FF8E8E', '#FFB3B3'],
            'professional': ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#7209B7'],
            'modern': ['#6366F1', '#8B5CF6', '#EC4899', '#F59E0B', '#10B981'],
            'corporate': ['#1F2937', '#374151', '#6B7280', '#9CA3AF', '#D1D5DB']
        }

    def generate_contextual_charts(self, analysis: Dict[str, Any], df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Génère des visualisations basées sur :
        - Type de données détecté
        - Insights LLM spécifiques
        - Meilleures pratiques dataviz
        - Contexte métier identifié
        """
        try:
            logger.info("Génération des visualisations contextuelles")
            
            # Détection du domaine
            domain = analysis.get('classification', {}).get('domain', 'general').lower()
            
            # Récupération des visualisations suggérées
            suggested_viz = analysis.get('visualizations', [])
            
            # Génération des visualisations contextuelles
            contextual_charts = []
            
            # 1. Visualisations suggérées par le LLM
            for viz in suggested_viz:
                if viz.get('status') == 'feasible':
                    chart = self._create_chart_from_suggestion(viz, df)
                    if chart:
                        contextual_charts.append(chart)
            
            # 2. Visualisations automatiques basées sur le domaine
            domain_charts = self._generate_domain_specific_charts(domain, df, analysis)
            contextual_charts.extend(domain_charts)
            
            # 3. Visualisations de base pour tous les datasets
            base_charts = self._generate_base_charts(df, analysis)
            contextual_charts.extend(base_charts)
            
            # 4. Optimisation et finalisation
            final_charts = self._optimize_charts(contextual_charts, df)
            
            logger.info(f"Génération terminée: {len(final_charts)} visualisations créées")
            return final_charts
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération des visualisations: {e}")
            return self._get_fallback_charts(df)

    def _create_chart_from_suggestion(self, viz: Dict[str, Any], df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Crée un graphique à partir d'une suggestion LLM"""
        try:
            viz_type = viz.get('type', '').lower()
            columns = viz.get('columns', [])
            title = viz.get('title', f"Graphique {viz_type}")
            
            # Vérification de la disponibilité des colonnes
            available_columns = [col for col in columns if col in df.columns]
            if not available_columns:
                logger.warning(f"Colonnes non disponibles pour {viz_type}: {columns}")
                return None
            
            # Création du graphique selon le type
            if viz_type in ['bar_chart', 'bar']:
                return self._create_bar_chart(df, available_columns, title)
            elif viz_type in ['line_chart', 'line']:
                return self._create_line_chart(df, available_columns, title)
            elif viz_type in ['scatter_plot', 'scatter']:
                return self._create_scatter_plot(df, available_columns, title)
            elif viz_type in ['pie_chart', 'pie']:
                return self._create_pie_chart(df, available_columns, title)
            elif viz_type in ['histogram']:
                return self._create_histogram(df, available_columns, title)
            elif viz_type in ['heatmap']:
                return self._create_heatmap(df, available_columns, title)
            else:
                logger.warning(f"Type de visualisation non supporté: {viz_type}")
                return None
                
        except Exception as e:
            logger.error(f"Erreur lors de la création du graphique {viz.get('type')}: {e}")
            return None

    def _generate_domain_specific_charts(self, domain: str, df: pd.DataFrame, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Génère des graphiques spécifiques au domaine métier"""
        charts = []
        
        # Récupération des templates du domaine
        domain_templates = self.chart_templates.get(domain, self.chart_templates['general'])
        
        for template in domain_templates:
            try:
                chart = self._apply_template(template, df, analysis)
                if chart:
                    charts.append(chart)
            except Exception as e:
                logger.warning(f"Erreur lors de l'application du template {template.get('name')}: {e}")
                continue
        
        return charts

    def _generate_base_charts(self, df: pd.DataFrame, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Génère des graphiques de base pour tous les datasets"""
        charts = []
        
        # 1. Aperçu des données
        charts.append(self._create_data_overview(df))
        
        # 2. Distribution des colonnes numériques
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols[:3]:  # Limiter à 3 colonnes
            charts.append(self._create_distribution_chart(df, col))
        
        # 3. Corrélations si applicable
        if len(numeric_cols) >= 2:
            charts.append(self._create_correlation_heatmap(df, numeric_cols))
        
        # 4. Valeurs manquantes
        charts.append(self._create_missing_values_chart(df))
        
        return charts

    def _create_bar_chart(self, df: pd.DataFrame, columns: List[str], title: str) -> Dict[str, Any]:
        """Crée un graphique en barres"""
        try:
            if len(columns) == 1:
                # Graphique simple
                fig = px.bar(
                    df[columns[0]].value_counts().head(20),
                    title=title,
                    color_discrete_sequence=self.color_palettes['free_mobile']
                )
            else:
                # Graphique groupé
                x_col, y_col = columns[0], columns[1]
                if df[y_col].dtype in ['object', 'category']:
                    # Groupement par catégorie
                    grouped_data = df.groupby(x_col)[y_col].value_counts().reset_index()
                    fig = px.bar(
                        grouped_data,
                        x=x_col,
                        y='count',
                        color=y_col,
                        title=title,
                        color_discrete_sequence=self.color_palettes['free_mobile']
                    )
                else:
                    # Groupement numérique
                    grouped_data = df.groupby(x_col)[y_col].mean().reset_index()
                    fig = px.bar(
                        grouped_data,
                        x=x_col,
                        y=y_col,
                        title=title,
                        color_discrete_sequence=self.color_palettes['free_mobile']
                    )
            
            return {
                'type': 'bar_chart',
                'title': title,
                'figure': fig,
                'columns': columns,
                'description': f"Graphique en barres pour {', '.join(columns)}"
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du graphique en barres: {e}")
            return None

    def _create_line_chart(self, df: pd.DataFrame, columns: List[str], title: str) -> Dict[str, Any]:
        """Crée un graphique linéaire"""
        try:
            if len(columns) >= 2:
                x_col, y_col = columns[0], columns[1]
                
                # Vérification si la colonne x est temporelle
                if pd.api.types.is_datetime64_any_dtype(df[x_col]):
                    fig = px.line(
                        df.sort_values(x_col),
                        x=x_col,
                        y=y_col,
                        title=title,
                        color_discrete_sequence=self.color_palettes['free_mobile']
                    )
                else:
                    fig = px.line(
                        df,
                        x=x_col,
                        y=y_col,
                        title=title,
                        color_discrete_sequence=self.color_palettes['free_mobile']
                    )
                
                return {
                    'type': 'line_chart',
                    'title': title,
                    'figure': fig,
                    'columns': columns,
                    'description': f"Graphique linéaire pour {', '.join(columns)}"
                }
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du graphique linéaire: {e}")
            return None

    def _create_scatter_plot(self, df: pd.DataFrame, columns: List[str], title: str) -> Dict[str, Any]:
        """Crée un graphique de dispersion"""
        try:
            if len(columns) >= 2:
                x_col, y_col = columns[0], columns[1]
                
                # Ajout d'une colonne de couleur si disponible
                color_col = None
                if len(columns) >= 3:
                    color_col = columns[2]
                
                fig = px.scatter(
                    df,
                    x=x_col,
                    y=y_col,
                    color=color_col,
                    title=title,
                    color_discrete_sequence=self.color_palettes['free_mobile']
                )
                
                return {
                    'type': 'scatter_plot',
                    'title': title,
                    'figure': fig,
                    'columns': columns,
                    'description': f"Graphique de dispersion pour {', '.join(columns)}"
                }
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du graphique de dispersion: {e}")
            return None

    def _create_pie_chart(self, df: pd.DataFrame, columns: List[str], title: str) -> Dict[str, Any]:
        """Crée un graphique en secteurs"""
        try:
            if len(columns) >= 1:
                col = columns[0]
                value_counts = df[col].value_counts().head(10)  # Limiter à 10 catégories
                
                fig = px.pie(
                    values=value_counts.values,
                    names=value_counts.index,
                    title=title,
                    color_discrete_sequence=self.color_palettes['free_mobile']
                )
                
                return {
                    'type': 'pie_chart',
                    'title': title,
                    'figure': fig,
                    'columns': columns,
                    'description': f"Graphique en secteurs pour {col}"
                }
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du graphique en secteurs: {e}")
            return None

    def _create_histogram(self, df: pd.DataFrame, columns: List[str], title: str) -> Dict[str, Any]:
        """Crée un histogramme"""
        try:
            if len(columns) >= 1:
                col = columns[0]
                
                fig = px.histogram(
                    df,
                    x=col,
                    title=title,
                    color_discrete_sequence=self.color_palettes['free_mobile']
                )
                
                return {
                    'type': 'histogram',
                    'title': title,
                    'figure': fig,
                    'columns': columns,
                    'description': f"Histogramme pour {col}"
                }
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'histogramme: {e}")
            return None

    def _create_heatmap(self, df: pd.DataFrame, columns: List[str], title: str) -> Dict[str, Any]:
        """Crée une heatmap de corrélation"""
        try:
            # Utilisation de toutes les colonnes numériques si pas spécifiées
            if not columns:
                numeric_cols = df.select_dtypes(include=['number']).columns
                columns = list(numeric_cols)
            
            # Calcul de la matrice de corrélation
            corr_matrix = df[columns].corr()
            
            fig = px.imshow(
                corr_matrix,
                title=title,
                color_continuous_scale='RdBu',
                aspect="auto"
            )
            
            return {
                'type': 'heatmap',
                'title': title,
                'figure': fig,
                'columns': columns,
                'description': f"Heatmap de corrélation pour {len(columns)} variables"
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de la heatmap: {e}")
            return None

    def _create_data_overview(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Crée un aperçu général des données"""
        try:
            # Statistiques de base
            stats = {
                'Lignes': len(df),
                'Colonnes': len(df.columns),
                'Valeurs manquantes': df.isnull().sum().sum(),
                'Doublons': df.duplicated().sum(),
                'Mémoire (MB)': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
            }
            
            # Création d'un graphique de métriques
            fig = go.Figure()
            
            fig.add_trace(go.Indicator(
                mode="number",
                value=stats['Lignes'],
                title={"text": "Lignes"},
                domain={'x': [0, 0.2], 'y': [0, 1]}
            ))
            
            fig.add_trace(go.Indicator(
                mode="number",
                value=stats['Colonnes'],
                title={"text": "Colonnes"},
                domain={'x': [0.2, 0.4], 'y': [0, 1]}
            ))
            
            fig.add_trace(go.Indicator(
                mode="number",
                value=stats['Valeurs manquantes'],
                title={"text": "Valeurs manquantes"},
                domain={'x': [0.4, 0.6], 'y': [0, 1]}
            ))
            
            fig.add_trace(go.Indicator(
                mode="number",
                value=stats['Doublons'],
                title={"text": "Doublons"},
                domain={'x': [0.6, 0.8], 'y': [0, 1]}
            ))
            
            fig.add_trace(go.Indicator(
                mode="number",
                value=stats['Mémoire (MB)'],
                title={"text": "Mémoire (MB)"},
                domain={'x': [0.8, 1], 'y': [0, 1]}
            ))
            
            fig.update_layout(
                title="Aperçu du Dataset",
                height=200,
                showlegend=False
            )
            
            return {
                'type': 'data_overview',
                'title': 'Aperçu du Dataset',
                'figure': fig,
                'columns': [],
                'description': 'Métriques de base du dataset',
                'stats': stats
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'aperçu des données: {e}")
            return None

    def _create_distribution_chart(self, df: pd.DataFrame, column: str) -> Dict[str, Any]:
        """Crée un graphique de distribution"""
        try:
            fig = px.histogram(
                df,
                x=column,
                title=f"Distribution de {column}",
                color_discrete_sequence=self.color_palettes['free_mobile']
            )
            
            return {
                'type': 'distribution',
                'title': f"Distribution de {column}",
                'figure': fig,
                'columns': [column],
                'description': f"Distribution statistique de {column}"
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du graphique de distribution: {e}")
            return None

    def _create_correlation_heatmap(self, df: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
        """Crée une heatmap de corrélation"""
        try:
            corr_matrix = df[columns].corr()
            
            fig = px.imshow(
                corr_matrix,
                title="Matrice de Corrélation",
                color_continuous_scale='RdBu',
                aspect="auto"
            )
            
            return {
                'type': 'correlation_heatmap',
                'title': 'Matrice de Corrélation',
                'figure': fig,
                'columns': columns,
                'description': f"Corrélations entre {len(columns)} variables numériques"
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de la heatmap de corrélation: {e}")
            return None

    def _create_missing_values_chart(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Crée un graphique des valeurs manquantes"""
        try:
            missing_data = df.isnull().sum()
            missing_data = missing_data[missing_data > 0].sort_values(ascending=False)
            
            if len(missing_data) == 0:
                return None
            
            fig = px.bar(
                x=missing_data.index,
                y=missing_data.values,
                title="Valeurs Manquantes par Colonne",
                color_discrete_sequence=self.color_palettes['free_mobile']
            )
            
            fig.update_xaxes(title="Colonnes")
            fig.update_yaxes(title="Nombre de valeurs manquantes")
            
            return {
                'type': 'missing_values',
                'title': 'Valeurs Manquantes par Colonne',
                'figure': fig,
                'columns': list(missing_data.index),
                'description': f"Valeurs manquantes dans {len(missing_data)} colonnes"
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du graphique des valeurs manquantes: {e}")
            return None

    def _optimize_charts(self, charts: List[Dict[str, Any]], df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Optimise et finalise les graphiques"""
        optimized_charts = []
        
        for chart in charts:
            if chart and chart.get('figure'):
                try:
                    # Optimisation du graphique
                    fig = chart['figure']
                    
                    # Mise à jour du style
                    fig.update_layout(
                        font=dict(family="Arial", size=12),
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        margin=dict(l=50, r=50, t=50, b=50)
                    )
                    
                    # Ajout de la palette de couleurs Free Mobile
                    if hasattr(fig, 'data') and fig.data:
                        for trace in fig.data:
                            if hasattr(trace, 'marker'):
                                trace.marker.color = self.color_palettes['free_mobile'][0]
                    
                    chart['figure'] = fig
                    optimized_charts.append(chart)
                    
                except Exception as e:
                    logger.warning(f"Erreur lors de l'optimisation du graphique {chart.get('title')}: {e}")
                    continue
        
        return optimized_charts

    def _get_fallback_charts(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Graphiques de fallback en cas d'erreur"""
        try:
            charts = []
            
            # Aperçu des données
            overview = self._create_data_overview(df)
            if overview:
                charts.append(overview)
            
            # Distribution d'une colonne numérique si disponible
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                distribution = self._create_distribution_chart(df, numeric_cols[0])
                if distribution:
                    charts.append(distribution)
            
            return charts
            
        except Exception as e:
            logger.error(f"Erreur lors de la création des graphiques de fallback: {e}")
            return []

    # Templates de graphiques par domaine
    def _get_financial_charts(self) -> List[Dict[str, Any]]:
        return [
            {'name': 'revenue_trend', 'type': 'line_chart', 'priority': 'high'},
            {'name': 'profit_margin', 'type': 'bar_chart', 'priority': 'high'},
            {'name': 'cost_analysis', 'type': 'pie_chart', 'priority': 'medium'},
            {'name': 'financial_ratios', 'type': 'heatmap', 'priority': 'medium'}
        ]

    def _get_sales_charts(self) -> List[Dict[str, Any]]:
        return [
            {'name': 'sales_performance', 'type': 'bar_chart', 'priority': 'high'},
            {'name': 'sales_trend', 'type': 'line_chart', 'priority': 'high'},
            {'name': 'territory_analysis', 'type': 'scatter_plot', 'priority': 'medium'},
            {'name': 'product_performance', 'type': 'pie_chart', 'priority': 'medium'}
        ]

    def _get_hr_charts(self) -> List[Dict[str, Any]]:
        return [
            {'name': 'demographics', 'type': 'pie_chart', 'priority': 'high'},
            {'name': 'performance_distribution', 'type': 'histogram', 'priority': 'high'},
            {'name': 'department_analysis', 'type': 'bar_chart', 'priority': 'medium'},
            {'name': 'tenure_analysis', 'type': 'line_chart', 'priority': 'medium'}
        ]

    def _get_marketing_charts(self) -> List[Dict[str, Any]]:
        return [
            {'name': 'campaign_performance', 'type': 'bar_chart', 'priority': 'high'},
            {'name': 'conversion_funnel', 'type': 'funnel', 'priority': 'high'},
            {'name': 'channel_analysis', 'type': 'pie_chart', 'priority': 'medium'},
            {'name': 'audience_segmentation', 'type': 'scatter_plot', 'priority': 'medium'}
        ]

    def _get_ecommerce_charts(self) -> List[Dict[str, Any]]:
        return [
            {'name': 'sales_timeline', 'type': 'line_chart', 'priority': 'high'},
            {'name': 'category_performance', 'type': 'bar_chart', 'priority': 'high'},
            {'name': 'customer_segmentation', 'type': 'scatter_plot', 'priority': 'medium'},
            {'name': 'geographic_distribution', 'type': 'map', 'priority': 'medium'}
        ]

    def _get_logistics_charts(self) -> List[Dict[str, Any]]:
        return [
            {'name': 'inventory_trends', 'type': 'line_chart', 'priority': 'high'},
            {'name': 'delivery_performance', 'type': 'bar_chart', 'priority': 'high'},
            {'name': 'supply_chain_flow', 'type': 'sankey', 'priority': 'medium'},
            {'name': 'cost_analysis', 'type': 'pie_chart', 'priority': 'medium'}
        ]

    def _get_healthcare_charts(self) -> List[Dict[str, Any]]:
        return [
            {'name': 'patient_flow', 'type': 'line_chart', 'priority': 'high'},
            {'name': 'treatment_outcomes', 'type': 'bar_chart', 'priority': 'high'},
            {'name': 'resource_utilization', 'type': 'heatmap', 'priority': 'medium'},
            {'name': 'quality_metrics', 'type': 'scatter_plot', 'priority': 'medium'}
        ]

    def _get_education_charts(self) -> List[Dict[str, Any]]:
        return [
            {'name': 'student_performance', 'type': 'histogram', 'priority': 'high'},
            {'name': 'course_analytics', 'type': 'bar_chart', 'priority': 'high'},
            {'name': 'engagement_metrics', 'type': 'line_chart', 'priority': 'medium'},
            {'name': 'progress_tracking', 'type': 'scatter_plot', 'priority': 'medium'}
        ]

    def _get_general_charts(self) -> List[Dict[str, Any]]:
        return [
            {'name': 'data_overview', 'type': 'data_overview', 'priority': 'high'},
            {'name': 'distribution_analysis', 'type': 'histogram', 'priority': 'medium'},
            {'name': 'correlation_analysis', 'type': 'heatmap', 'priority': 'medium'},
            {'name': 'missing_values', 'type': 'missing_values', 'priority': 'low'}
        ]

    def _apply_template(self, template: Dict[str, Any], df: pd.DataFrame, analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Applique un template de graphique"""
        try:
            chart_type = template.get('type')
            priority = template.get('priority', 'medium')
            
            # Logique d'application du template selon le type
            if chart_type == 'line_chart':
                return self._create_trend_chart(df, analysis)
            elif chart_type == 'bar_chart':
                return self._create_performance_chart(df, analysis)
            elif chart_type == 'pie_chart':
                return self._create_composition_chart(df, analysis)
            elif chart_type == 'scatter_plot':
                return self._create_relationship_chart(df, analysis)
            else:
                return None
                
        except Exception as e:
            logger.warning(f"Erreur lors de l'application du template {template.get('name')}: {e}")
            return None

    def _create_trend_chart(self, df: pd.DataFrame, analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Crée un graphique de tendance"""
        # Logique de création de graphique de tendance
        return None

    def _create_performance_chart(self, df: pd.DataFrame, analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Crée un graphique de performance"""
        # Logique de création de graphique de performance
        return None

    def _create_composition_chart(self, df: pd.DataFrame, analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Crée un graphique de composition"""
        # Logique de création de graphique de composition
        return None

    def _create_relationship_chart(self, df: pd.DataFrame, analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Crée un graphique de relation"""
        # Logique de création de graphique de relation
        return None
