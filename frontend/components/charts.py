"""
Chart components for Streamlit dashboard
Plotly-based visualization components for tweet analysis
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
import numpy as np


class ChartManager:
    """Manages all chart components and visualizations"""
    
    def __init__(self):
        """Initialize chart manager with default styling"""
        self.color_palette = {
            'positive': '#2E8B57',    # Sea Green
            'neutral': '#4682B4',     # Steel Blue  
            'negative': '#DC143C',    # Crimson
            'unknown': '#708090',     # Slate Gray
            'critique': '#FF0000',    # Red
            'haute': '#FF4500',       # Orange Red
            'moyenne': '#FFD700',     # Gold
            'basse': '#32CD32'        # Lime Green
        }
        
        self.chart_config = {
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d']
        }
    
    def sentiment_pie_chart(self, sentiment_data: Dict[str, int], title: str = "Distribution des Sentiments") -> go.Figure:
        """
        Create sentiment distribution pie chart
        
        Args:
            sentiment_data: Dictionary with sentiment counts
            title: Chart title
            
        Returns:
            Plotly figure
        """
        if not sentiment_data:
            return self._create_empty_chart("Aucune donnée de sentiment disponible")
        
        labels = list(sentiment_data.keys())
        values = list(sentiment_data.values())
        colors = [self.color_palette.get(label, '#808080') for label in labels]
        
        fig = go.Figure(data=[go.Pie(
            labels=[self._format_sentiment_label(label) for label in labels],
            values=values,
            hole=0.4,
            marker_colors=colors,
            textinfo='label+percent+value',
            textfont_size=12,
            hovertemplate='<b>%{label}</b><br>Nombre: %{value}<br>Pourcentage: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#1f77b4'}
            },
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05),
            margin=dict(t=60, b=20, l=20, r=120),
            height=400
        )
        
        return fig
    
    def category_bar_chart(self, category_data: Dict[str, int], title: str = "Distribution par Catégorie") -> go.Figure:
        """
        Create category distribution bar chart
        
        Args:
            category_data: Dictionary with category counts
            title: Chart title
            
        Returns:
            Plotly figure
        """
        if not category_data:
            return self._create_empty_chart("Aucune donnée de catégorie disponible")
        
        # Sort by count descending
        sorted_items = sorted(category_data.items(), key=lambda x: x[1], reverse=True)
        categories = [self._format_category_label(cat) for cat, _ in sorted_items]
        counts = [count for _, count in sorted_items]
        
        fig = go.Figure(data=[go.Bar(
            x=categories,
            y=counts,
            marker_color=px.colors.qualitative.Set3,
            text=counts,
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Nombre de tweets: %{y}<extra></extra>'
        )])
        
        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#1f77b4'}
            },
            xaxis_title="Catégories",
            yaxis_title="Nombre de tweets",
            xaxis_tickangle=-45,
            margin=dict(t=60, b=100, l=60, r=20),
            height=450
        )
        
        return fig
    
    def priority_donut_chart(self, priority_data: Dict[str, int], title: str = "Répartition par Priorité") -> go.Figure:
        """
        Create priority distribution donut chart
        
        Args:
            priority_data: Dictionary with priority counts
            title: Chart title
            
        Returns:
            Plotly figure
        """
        if not priority_data:
            return self._create_empty_chart("Aucune donnée de priorité disponible")
        
        # Order by priority level
        priority_order = ['critique', 'haute', 'moyenne', 'basse']
        ordered_data = {p: priority_data.get(p, 0) for p in priority_order if p in priority_data}
        
        labels = [self._format_priority_label(p) for p in ordered_data.keys()]
        values = list(ordered_data.values())
        colors = [self.color_palette.get(p, '#808080') for p in ordered_data.keys()]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.6,
            marker_colors=colors,
            textinfo='label+percent',
            textfont_size=11,
            hovertemplate='<b>%{label}</b><br>Nombre: %{value}<br>Pourcentage: %{percent}<extra></extra>'
        )])
        
        # Add center text
        total_tweets = sum(values)
        fig.add_annotation(
            text=f"<b>{total_tweets}</b><br>tweets",
            x=0.5, y=0.5,
            font_size=16,
            showarrow=False
        )
        
        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#1f77b4'}
            },
            showlegend=True,
            legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5),
            margin=dict(t=60, b=80, l=20, r=20),
            height=400
        )
        
        return fig
    
    def temporal_line_chart(self, temporal_data: Dict[str, int], title: str = "Volume de Tweets par Heure") -> go.Figure:
        """
        Create temporal analysis line chart
        
        Args:
            temporal_data: Dictionary with hour -> count mapping
            title: Chart title
            
        Returns:
            Plotly figure
        """
        if not temporal_data:
            return self._create_empty_chart("Aucune donnée temporelle disponible")
        
        # Ensure all hours are represented
        hours = list(range(24))
        counts = [temporal_data.get(str(h), 0) for h in hours]
        
        fig = go.Figure(data=[go.Scatter(
            x=hours,
            y=counts,
            mode='lines+markers',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8, color='#ff7f0e'),
            fill='tonexty',
            fillcolor='rgba(31, 119, 180, 0.1)',
            hovertemplate='<b>%{x}h</b><br>Tweets: %{y}<extra></extra>'
        )])
        
        # Highlight peak hour
        peak_hour = max(temporal_data.keys(), key=lambda k: temporal_data[k]) if temporal_data else 0
        peak_count = temporal_data.get(peak_hour, 0)
        
        fig.add_annotation(
            x=int(peak_hour),
            y=peak_count,
            text=f"Pic: {peak_hour}h",
            showarrow=True,
            arrowhead=2,
            arrowcolor="red",
            bgcolor="yellow",
            bordercolor="red"
        )
        
        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#1f77b4'}
            },
            xaxis_title="Heure de la journée",
            yaxis_title="Nombre de tweets",
            xaxis=dict(tickmode='linear', tick0=0, dtick=2),
            margin=dict(t=60, b=60, l=60, r=20),
            height=400
        )
        
        return fig
    
    def sentiment_score_histogram(self, sentiment_scores: List[float], title: str = "Distribution des Scores de Sentiment") -> go.Figure:
        """
        Create sentiment score distribution histogram
        
        Args:
            sentiment_scores: List of sentiment scores (-1 to 1)
            title: Chart title
            
        Returns:
            Plotly figure
        """
        if not sentiment_scores:
            return self._create_empty_chart("Aucun score de sentiment disponible")
        
        fig = go.Figure(data=[go.Histogram(
            x=sentiment_scores,
            nbinsx=20,
            marker_color='rgba(31, 119, 180, 0.7)',
            marker_line_color='rgba(31, 119, 180, 1)',
            marker_line_width=1,
            hovertemplate='Score: %{x}<br>Nombre: %{y}<extra></extra>'
        )])
        
        # Add vertical lines for sentiment boundaries
        fig.add_vline(x=-0.1, line_dash="dash", line_color="red", annotation_text="Négatif")
        fig.add_vline(x=0.1, line_dash="dash", line_color="green", annotation_text="Positif")
        
        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#1f77b4'}
            },
            xaxis_title="Score de sentiment",
            yaxis_title="Nombre de tweets",
            xaxis=dict(range=[-1.1, 1.1]),
            margin=dict(t=60, b=60, l=60, r=20),
            height=400
        )
        
        return fig
    
    def kpi_gauge_chart(self, value: float, title: str, max_value: float = 100, 
                       threshold_good: float = 80, threshold_warning: float = 60) -> go.Figure:
        """
        Create KPI gauge chart
        
        Args:
            value: Current value
            title: Chart title
            max_value: Maximum value for gauge
            threshold_good: Good performance threshold
            threshold_warning: Warning threshold
            
        Returns:
            Plotly figure
        """
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title, 'font': {'size': 16}},
            delta={'reference': threshold_good},
            gauge={
                'axis': {'range': [None, max_value]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, threshold_warning], 'color': "lightgray"},
                    {'range': [threshold_warning, threshold_good], 'color': "yellow"},
                    {'range': [threshold_good, max_value], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': threshold_good
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(t=40, b=20, l=20, r=20)
        )
        
        return fig
    
    def correlation_heatmap(self, correlation_data: Dict[str, Dict[str, float]], 
                           title: str = "Corrélation entre Métriques") -> go.Figure:
        """
        Create correlation heatmap
        
        Args:
            correlation_data: Nested dictionary with correlation values
            title: Chart title
            
        Returns:
            Plotly figure
        """
        if not correlation_data:
            return self._create_empty_chart("Aucune donnée de corrélation disponible")
        
        # Convert to matrix format
        labels = list(correlation_data.keys())
        matrix = [[correlation_data[row].get(col, 0) for col in labels] for row in labels]
        
        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            x=labels,
            y=labels,
            colorscale='RdBu',
            zmid=0,
            text=[[f"{val:.2f}" for val in row] for row in matrix],
            texttemplate="%{text}",
            textfont={"size": 10},
            hovertemplate='%{y} vs %{x}<br>Corrélation: %{z:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#1f77b4'}
            },
            height=400,
            margin=dict(t=60, b=60, l=100, r=20)
        )
        
        return fig
    
    def _format_sentiment_label(self, sentiment: str) -> str:
        """Format sentiment label"""
        label_map = {
            'positive': 'Positif',
            'neutral': 'Neutre',
            'negative': 'Négatif',
            'unknown': 'Inconnu'
        }
        return label_map.get(sentiment, sentiment.title())
    
    def _format_category_label(self, category: str) -> str:
        """Format category label"""
        label_map = {
            'facturation': 'Facturation',
            'réseau': 'Réseau',
            'technique': 'Technique',
            'abonnement': 'Abonnement',
            'réclamation': 'Réclamation',
            'compliment': 'Compliment',
            'question': 'Question',
            'autre': 'Autre'
        }
        return label_map.get(category, category.title())
    
    def _format_priority_label(self, priority: str) -> str:
        """Format priority label"""
        label_map = {
            'critique': 'Critique',
            'haute': 'Haute',
            'moyenne': 'Moyenne',
            'basse': 'Basse'
        }
        return label_map.get(priority, priority.title())
    
    def _create_empty_chart(self, message: str) -> go.Figure:
        """Create empty chart with message"""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            font_size=16,
            showarrow=False
        )
        fig.update_layout(
            height=300,
            margin=dict(t=20, b=20, l=20, r=20),
            xaxis={'visible': False},
            yaxis={'visible': False}
        )
        return fig
    
    def create_multi_metric_dashboard(self, kpi_data: Dict[str, Any]) -> List[go.Figure]:
        """
        Create multiple charts for dashboard
        
        Args:
            kpi_data: KPI data dictionary
            
        Returns:
            List of Plotly figures
        """
        charts = []
        
        # Sentiment pie chart
        if 'sentiment_distribution' in kpi_data:
            charts.append(self.sentiment_pie_chart(kpi_data['sentiment_distribution']))
        
        # Category bar chart
        if 'category_distribution' in kpi_data:
            charts.append(self.category_bar_chart(kpi_data['category_distribution']))
        
        # Priority donut chart
        if 'priority_distribution' in kpi_data:
            charts.append(self.priority_donut_chart(kpi_data['priority_distribution']))
        
        # Temporal line chart
        if 'tweets_per_hour' in kpi_data:
            charts.append(self.temporal_line_chart(kpi_data['tweets_per_hour']))
        
        return charts
