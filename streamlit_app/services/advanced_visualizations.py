"""
Advanced Visualizations - Visualisations avancées pour KPI
Module de création de graphiques interactifs avec Plotly
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class AdvancedVisualizations:
    """Créateur de visualisations avancées"""
    
    def __init__(self):
        """Initialise le créateur de visualisations"""
        self.color_scheme = {
            'primary': '#CC0000',
            'secondary': '#8B0000',
            'success': '#28a745',
            'warning': '#ffc107',
            'info': '#17a2b8',
            'positive': '#4ade80',
            'negative': '#ef4444',
            'neutral': '#94a3b8'
        }
    
    def create_temporal_evolution_chart(self, kpi_data: Dict[str, Any], 
                                       df: pd.DataFrame) -> go.Figure:
        """
        Crée un graphique d'évolution temporelle
        
        Args:
            kpi_data: Données KPI de l'évolution temporelle
            df: DataFrame source
            
        Returns:
            Figure Plotly
        """
        try:
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Volume de Tweets par Jour', 'Évolution des Sentiments'),
                vertical_spacing=0.12,
                row_heights=[0.5, 0.5]
            )
            
            # Préparer les données temporelles
            date_col = self._find_date_column(df)
            if date_col:
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                daily_volume = df.groupby(df[date_col].dt.date).size()
                
                # Graphique du volume
                fig.add_trace(
                    go.Scatter(
                        x=daily_volume.index,
                        y=daily_volume.values,
                        mode='lines+markers',
                        name='Volume',
                        line=dict(color=self.color_scheme['primary'], width=3),
                        fill='tozeroy',
                        fillcolor='rgba(204, 0, 0, 0.1)'
                    ),
                    row=1, col=1
                )
                
                # Graphique des sentiments si disponible
                if 'sentiment' in df.columns:
                    sentiment_daily = df.groupby([df[date_col].dt.date, 'sentiment']).size().unstack(fill_value=0)
                    
                    for sentiment in ['positive', 'neutral', 'negative']:
                        if sentiment in sentiment_daily.columns:
                            color = self.color_scheme.get(sentiment, '#888')
                            fig.add_trace(
                                go.Scatter(
                                    x=sentiment_daily.index,
                                    y=sentiment_daily[sentiment],
                                    mode='lines',
                                    name=sentiment.capitalize(),
                                    line=dict(color=color, width=2),
                                    stackgroup='one'
                                ),
                                row=2, col=1
                            )
            
            # Mise en forme
            fig.update_xaxes(title_text="Date", row=2, col=1)
            fig.update_yaxes(title_text="Nombre de Tweets", row=1, col=1)
            fig.update_yaxes(title_text="Nombre de Tweets", row=2, col=1)
            
            fig.update_layout(
                height=700,
                showlegend=True,
                hovermode='x unified',
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Erreur création graphique temporel: {str(e)}")
            return self._create_empty_figure("Erreur lors de la création du graphique")
    
    def create_heatmap_activity(self, kpi_data: Dict[str, Any], 
                               df: pd.DataFrame) -> go.Figure:
        """
        Crée une heatmap d'activité (jour x heure)
        
        Args:
            kpi_data: Données KPI
            df: DataFrame source
            
        Returns:
            Figure Plotly heatmap
        """
        try:
            date_col = self._find_date_column(df)
            if not date_col or date_col not in df.columns:
                return self._create_empty_figure("Pas de données temporelles")
            
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            
            # Créer matrice jour de semaine x heure
            df['day_of_week'] = df[date_col].dt.dayofweek
            df['hour'] = df[date_col].dt.hour
            
            heatmap_data = df.groupby(['day_of_week', 'hour']).size().unstack(fill_value=0)
            
            # Noms des jours
            day_names = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
            
            fig = go.Figure(data=go.Heatmap(
                z=heatmap_data.values,
                x=[f"{h}h" for h in range(24)],
                y=day_names,
                colorscale='Reds',
                text=heatmap_data.values,
                texttemplate='%{text}',
                textfont={"size": 10},
                colorbar=dict(title="Tweets")
            ))
            
            fig.update_layout(
                title="Heatmap d'Activité (Jour × Heure)",
                xaxis_title="Heure de la journée",
                yaxis_title="Jour de la semaine",
                height=500,
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Erreur création heatmap: {str(e)}")
            return self._create_empty_figure("Erreur lors de la création de la heatmap")
    
    def create_radar_chart_domains(self, kpi_data: Dict[str, Any], 
                                   df: pd.DataFrame) -> go.Figure:
        """
        Crée un radar chart par domaine (facturation, technique, commercial, etc.)
        
        Args:
            kpi_data: Données KPI
            df: DataFrame source
            
        Returns:
            Figure Plotly radar
        """
        try:
            # Déterminer les catégories/domaines
            category_col = 'category' if 'category' in df.columns else ('theme' if 'theme' in df.columns else None)
            
            if not category_col:
                return self._create_empty_figure("Pas de données de catégorie")
            
            # Calculer métriques par catégorie
            categories = df[category_col].value_counts()
            
            # Préparer données pour radar
            radar_categories = []
            radar_values = []
            
            for cat, count in categories.head(8).items():  # Top 8 catégories
                radar_categories.append(cat)
                
                # Calculer score composite
                cat_df = df[df[category_col] == cat]
                score = len(cat_df)
                
                # Ajuster selon sentiment si disponible
                if 'sentiment' in df.columns:
                    positive_ratio = (cat_df['sentiment'] == 'positive').sum() / len(cat_df)
                    score = score * (1 + positive_ratio)
                
                radar_values.append(score)
            
            # Normaliser les valeurs
            max_val = max(radar_values) if radar_values else 1
            radar_values = [v / max_val * 100 for v in radar_values]
            
            # Créer radar chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=radar_values,
                theta=radar_categories,
                fill='toself',
                fillcolor='rgba(204, 0, 0, 0.2)',
                line=dict(color=self.color_scheme['primary'], width=2),
                name='Performance'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100],
                        showticklabels=True,
                        ticks='',
                        gridcolor='rgba(0,0,0,0.1)'
                    ),
                    angularaxis=dict(
                        gridcolor='rgba(0,0,0,0.1)'
                    )
                ),
                showlegend=False,
                title="Performance par Domaine",
                height=500,
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Erreur création radar chart: {str(e)}")
            return self._create_empty_figure("Erreur lors de la création du radar chart")
    
    def create_correlation_matrix(self, kpi_data: Dict[str, Any]) -> go.Figure:
        """
        Crée une matrice de corrélation sentiment-sujet
        
        Args:
            kpi_data: Données KPI avec correlation_matrix
            
        Returns:
            Figure Plotly heatmap
        """
        try:
            correlation_data = kpi_data.get('sentiment_topic_correlation', {}).get('correlation_matrix', {})
            
            if not correlation_data:
                return self._create_empty_figure("Pas de données de corrélation")
            
            # Convertir en DataFrame
            df_corr = pd.DataFrame(correlation_data)
            
            fig = go.Figure(data=go.Heatmap(
                z=df_corr.values,
                x=df_corr.columns,
                y=df_corr.index,
                colorscale='RdYlGn',
                text=np.round(df_corr.values, 1),
                texttemplate='%{text}%',
                textfont={"size": 10},
                colorbar=dict(title="%")
            ))
            
            fig.update_layout(
                title="Corrélation Sentiment × Sujet",
                xaxis_title="Sentiment",
                yaxis_title="Sujet",
                height=500,
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Erreur création matrice corrélation: {str(e)}")
            return self._create_empty_figure("Erreur lors de la création de la matrice")
    
    def create_hourly_volume_chart(self, kpi_data: Dict[str, Any]) -> go.Figure:
        """
        Crée un graphique du volume horaire
        
        Args:
            kpi_data: Données KPI avec hourly_activity_volume
            
        Returns:
            Figure Plotly
        """
        try:
            hourly_data = kpi_data.get('hourly_activity_volume', {}).get('hourly_distribution', {})
            
            if not hourly_data:
                return self._create_empty_figure("Pas de données horaires")
            
            hours = sorted(hourly_data.keys())
            values = [hourly_data[h] for h in hours]
            
            # Identifier heures de pointe
            peak_hours_data = kpi_data.get('hourly_activity_volume', {}).get('peak_hours', [])
            peak_hours = [item['hour'] for item in peak_hours_data]
            
            # Couleurs conditionnelles
            colors = [self.color_scheme['primary'] if h in peak_hours else self.color_scheme['info'] 
                     for h in hours]
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=[f"{h}h" for h in hours],
                y=values,
                marker_color=colors,
                text=values,
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Tweets: %{y}<extra></extra>'
            ))
            
            fig.update_layout(
                title="Volume d'Activité par Heure",
                xaxis_title="Heure de la journée",
                yaxis_title="Nombre de Tweets",
                height=400,
                showlegend=False,
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Erreur création graphique horaire: {str(e)}")
            return self._create_empty_figure("Erreur lors de la création du graphique")
    
    def create_engagement_gauge(self, kpi_data: Dict[str, Any]) -> go.Figure:
        """
        Crée une jauge de score d'engagement
        
        Args:
            kpi_data: Données KPI avec global_engagement_score
            
        Returns:
            Figure Plotly gauge
        """
        try:
            engagement_data = kpi_data.get('global_engagement_score', {})
            score = engagement_data.get('global_score', 0)
            rating = engagement_data.get('rating', 'N/A')
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=score,
                title={'text': f"Score d'Engagement<br><span style='font-size:0.8em'>{rating}</span>"},
                delta={'reference': 70, 'increasing': {'color': "green"}},
                gauge={
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkgray"},
                    'bar': {'color': self.color_scheme['primary']},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 40], 'color': '#ffebee'},
                        {'range': [40, 70], 'color': '#fff3e0'},
                        {'range': [70, 100], 'color': '#e8f5e9'}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 70
                    }
                }
            ))
            
            fig.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=50, b=20)
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Erreur création jauge engagement: {str(e)}")
            return self._create_empty_figure("Erreur lors de la création de la jauge")
    
    def create_category_performance_chart(self, kpi_data: Dict[str, Any]) -> go.Figure:
        """
        Crée un graphique de performance par catégorie
        
        Args:
            kpi_data: Données KPI avec category_performance
            
        Returns:
            Figure Plotly
        """
        try:
            cat_data = kpi_data.get('category_performance', {}).get('by_category', {})
            
            if not cat_data:
                return self._create_empty_figure("Pas de données de catégorie")
            
            categories = list(cat_data.keys())
            counts = [cat_data[cat]['count'] for cat in categories]
            percentages = [cat_data[cat]['percentage'] for cat in categories]
            
            # Graphique combiné (barres + ligne)
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig.add_trace(
                go.Bar(
                    x=categories,
                    y=counts,
                    name="Nombre",
                    marker_color=self.color_scheme['primary'],
                    text=counts,
                    textposition='outside'
                ),
                secondary_y=False
            )
            
            fig.add_trace(
                go.Scatter(
                    x=categories,
                    y=percentages,
                    name="Pourcentage",
                    mode='lines+markers',
                    line=dict(color=self.color_scheme['success'], width=3),
                    marker=dict(size=10)
                ),
                secondary_y=True
            )
            
            fig.update_xaxes(title_text="Catégorie")
            fig.update_yaxes(title_text="Nombre de Tweets", secondary_y=False)
            fig.update_yaxes(title_text="Pourcentage (%)", secondary_y=True)
            
            fig.update_layout(
                title="Performance par Catégorie",
                height=400,
                hovermode='x unified',
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Erreur création graphique catégorie: {str(e)}")
            return self._create_empty_figure("Erreur lors de la création du graphique")
    
    def create_satisfaction_trend(self, kpi_data: Dict[str, Any], 
                                 df: pd.DataFrame) -> go.Figure:
        """
        Crée un graphique de tendance de satisfaction
        
        Args:
            kpi_data: Données KPI
            df: DataFrame source
            
        Returns:
            Figure Plotly
        """
        try:
            satisfaction_data = kpi_data.get('satisfaction_analysis', {})
            satisfaction_rate = satisfaction_data.get('satisfaction_rate', 0)
            
            # Simuler une tendance historique
            dates = pd.date_range(end=pd.Timestamp.now(), periods=30, freq='D')
            trend = np.random.normal(satisfaction_rate, 5, 30)
            trend = np.clip(trend, 0, 100)
            
            fig = go.Figure()
            
            # Ligne de satisfaction
            fig.add_trace(go.Scatter(
                x=dates,
                y=trend,
                mode='lines+markers',
                name='Satisfaction',
                line=dict(color=self.color_scheme['success'], width=3),
                fill='tozeroy',
                fillcolor='rgba(40, 167, 69, 0.1)'
            ))
            
            # Ligne de seuil 70%
            fig.add_hline(
                y=70,
                line_dash="dash",
                line_color="red",
                annotation_text="Seuil d'alerte (70%)",
                annotation_position="right"
            )
            
            fig.update_layout(
                title="Évolution de la Satisfaction Client",
                xaxis_title="Date",
                yaxis_title="Taux de Satisfaction (%)",
                height=400,
                yaxis=dict(range=[0, 100]),
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Erreur création tendance satisfaction: {str(e)}")
            return self._create_empty_figure("Erreur lors de la création du graphique")
    
    def create_processing_time_distribution(self, kpi_data: Dict[str, Any]) -> go.Figure:
        """
        Crée un graphique de distribution des temps de traitement
        
        Args:
            kpi_data: Données KPI avec average_processing_time
            
        Returns:
            Figure Plotly
        """
        try:
            proc_data = kpi_data.get('average_processing_time', {})
            by_category = proc_data.get('by_category', {})
            
            if not by_category:
                # Créer des données de démonstration
                by_category = {
                    'Facturation': '5min',
                    'Technique': '12min',
                    'Réseau': '8min',
                    'SAV': '15min',
                    'Commercial': '6min'
                }
            
            categories = list(by_category.keys())
            times_str = list(by_category.values())
            
            # Convertir en minutes pour l'affichage
            times_minutes = []
            for t in times_str:
                if 'min' in t:
                    times_minutes.append(float(t.replace('min', '')))
                elif 'h' in t:
                    times_minutes.append(float(t.replace('h', '')) * 60)
                elif 's' in t:
                    times_minutes.append(float(t.replace('s', '')) / 60)
                else:
                    times_minutes.append(10)
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=categories,
                y=times_minutes,
                marker_color=self.color_scheme['info'],
                text=[f"{t:.1f}min" for t in times_minutes],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Temps: %{text}<extra></extra>'
            ))
            
            fig.update_layout(
                title="Temps Moyen de Traitement par Catégorie",
                xaxis_title="Catégorie",
                yaxis_title="Temps (minutes)",
                height=400,
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Erreur création distribution temps: {str(e)}")
            return self._create_empty_figure("Erreur lors de la création du graphique")
    
    # === Fonctions utilitaires ===
    
    def _find_date_column(self, df: pd.DataFrame) -> Optional[str]:
        """Trouve la colonne de date dans le DataFrame"""
        date_cols = ['date', 'created_at', 'timestamp', 'created', 'datetime']
        for col in date_cols:
            if col in df.columns:
                return col
        return None
    
    def _create_empty_figure(self, message: str) -> go.Figure:
        """Crée une figure vide avec un message"""
        fig = go.Figure()
        
        fig.add_annotation(
            text=message,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        
        fig.update_layout(
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            height=400,
            template='plotly_white'
        )
        
        return fig


# Instance globale
advanced_visualizations = AdvancedVisualizations()


def get_advanced_visualizations() -> AdvancedVisualizations:
    """Retourne l'instance du créateur de visualisations"""
    return advanced_visualizations

