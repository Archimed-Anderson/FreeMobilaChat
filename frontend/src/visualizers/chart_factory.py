"""
Chart Factory
Creates Plotly visualizations based on data types and analysis results
"""

import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class ChartFactory:
    """
    Factory for creating Plotly charts based on data characteristics
    
    Features:
    - Automatic chart type selection
    - Professional styling
    - Interactive visualizations
    - Responsive design
    """
    
    # Free Mobile color scheme
    COLOR_SCHEME = {
        'primary': '#DC143C',
        'secondary': '#FF6B6B',
        'accent': '#B91C3C',
        'neutral': '#6c757d',
        'success': '#28a745',
        'warning': '#ffc107',
        'danger': '#dc3545',
        'info': '#17a2b8'
    }
    
    PLOTLY_TEMPLATE = 'plotly_white'
    
    def __init__(self, df: pd.DataFrame, column_types: Dict[str, str]):
        """
        Initialize chart factory
        
        Args:
            df: pandas DataFrame
            column_types: Dictionary mapping columns to types
        """
        self.df = df
        self.column_types = column_types
    
    def create_chart(self, chart_spec: Dict[str, Any]) -> Optional[go.Figure]:
        """
        Create chart based on specification
        
        Args:
            chart_spec: Chart specification dictionary with:
                - type: Chart type
                - columns: Column names to visualize
                - title: Chart title
                - description: Chart description
                
        Returns:
            Plotly Figure object or None
        """
        chart_type = chart_spec['type']
        columns = chart_spec['columns']
        title = chart_spec.get('title', '')
        
        try:
            if chart_type == 'histogram':
                return self._create_histogram(columns[0], title)
            elif chart_type == 'boxplot':
                return self._create_boxplot(columns[0], title)
            elif chart_type == 'bar':
                return self._create_bar_chart(columns[0], title)
            elif chart_type == 'pie':
                return self._create_pie_chart(columns[0], title)
            elif chart_type == 'scatter':
                return self._create_scatter(columns[0], columns[1], title)
            elif chart_type == 'correlation_heatmap':
                return self._create_correlation_heatmap(columns, title)
            elif chart_type == 'line':
                return self._create_line_chart(columns[0], columns[1] if len(columns) > 1 else None, title)
            else:
                logger.warning(f"Unknown chart type: {chart_type}")
                return None
        except Exception as e:
            logger.error(f"Error creating {chart_type} chart: {str(e)}")
            return None
    
    def _create_histogram(self, column: str, title: str) -> go.Figure:
        """Create histogram for numeric column"""
        fig = px.histogram(
            self.df,
            x=column,
            title=title,
            nbins=30,
            color_discrete_sequence=[self.COLOR_SCHEME['primary']],
            template=self.PLOTLY_TEMPLATE
        )
        
        fig.update_layout(
            showlegend=False,
            xaxis_title=column,
            yaxis_title='Fréquence',
            hovermode='x unified'
        )
        
        return fig
    
    def _create_boxplot(self, column: str, title: str) -> go.Figure:
        """Create box plot for numeric column"""
        fig = go.Figure()
        
        fig.add_trace(go.Box(
            y=self.df[column].dropna(),
            name=column,
            marker_color=self.COLOR_SCHEME['primary'],
            boxmean='sd'  # Show mean and standard deviation
        ))
        
        fig.update_layout(
            title=title,
            yaxis_title=column,
            showlegend=False,
            template=self.PLOTLY_TEMPLATE
        )
        
        return fig
    
    def _create_bar_chart(self, column: str, title: str, top_n: int = 15) -> go.Figure:
        """Create bar chart for categorical column"""
        value_counts = self.df[column].value_counts().head(top_n)
        
        fig = px.bar(
            x=value_counts.index,
            y=value_counts.values,
            title=title,
            labels={'x': column, 'y': 'Nombre'},
            color=value_counts.values,
            color_continuous_scale=[[0, self.COLOR_SCHEME['secondary']], [1, self.COLOR_SCHEME['primary']]],
            template=self.PLOTLY_TEMPLATE
        )
        
        fig.update_layout(
            showlegend=False,
            xaxis_tickangle=-45
        )
        
        return fig
    
    def _create_pie_chart(self, column: str, title: str, top_n: int = 10) -> go.Figure:
        """Create pie chart for categorical column"""
        value_counts = self.df[column].value_counts().head(top_n)
        
        # Group remaining categories
        if len(self.df[column].value_counts()) > top_n:
            others_count = self.df[column].value_counts()[top_n:].sum()
            value_counts['Autres'] = others_count
        
        fig = px.pie(
            values=value_counts.values,
            names=value_counts.index,
            title=title,
            color_discrete_sequence=px.colors.sequential.Reds,
            template=self.PLOTLY_TEMPLATE
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Nombre: %{value}<br>Pourcentage: %{percent}'
        )
        
        return fig
    
    def _create_scatter(self, x_col: str, y_col: str, title: str) -> go.Figure:
        """Create scatter plot for two numeric columns"""
        fig = px.scatter(
            self.df,
            x=x_col,
            y=y_col,
            title=title,
            color_discrete_sequence=[self.COLOR_SCHEME['primary']],
            template=self.PLOTLY_TEMPLATE,
            trendline='ols',  # Add regression line
            opacity=0.6
        )
        
        fig.update_layout(
            xaxis_title=x_col,
            yaxis_title=y_col,
            hovermode='closest'
        )
        
        return fig
    
    def _create_correlation_heatmap(self, columns: List[str], title: str) -> go.Figure:
        """Create correlation heatmap for numeric columns"""
        # Select numeric columns
        numeric_df = self.df[columns].select_dtypes(include=[np.number])
        
        if numeric_df.empty:
            return None
        
        # Calculate correlation
        corr_matrix = numeric_df.corr()
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu_r',
            zmid=0,
            text=corr_matrix.values.round(2),
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title="Corrélation")
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title='',
            yaxis_title='',
            template=self.PLOTLY_TEMPLATE,
            height=max(400, len(corr_matrix) * 40)
        )
        
        return fig
    
    def _create_line_chart(self, x_col: str, y_col: Optional[str], title: str) -> go.Figure:
        """Create line chart for temporal data"""
        if y_col is None:
            # Count frequency over time
            temporal_counts = self.df[x_col].value_counts().sort_index()
            
            fig = px.line(
                x=temporal_counts.index,
                y=temporal_counts.values,
                title=title,
                labels={'x': x_col, 'y': 'Fréquence'},
                color_discrete_sequence=[self.COLOR_SCHEME['primary']],
                template=self.PLOTLY_TEMPLATE
            )
        else:
            # Plot y over x
            fig = px.line(
                self.df.sort_values(x_col),
                x=x_col,
                y=y_col,
                title=title,
                color_discrete_sequence=[self.COLOR_SCHEME['primary']],
                template=self.PLOTLY_TEMPLATE
            )
        
        fig.update_layout(
            xaxis_title=x_col,
            yaxis_title=y_col or 'Fréquence',
            hovermode='x unified'
        )
        
        return fig
    
    def create_data_overview_chart(self) -> go.Figure:
        """Create overview chart showing data completeness"""
        null_percentages = (self.df.isnull().sum() / len(self.df) * 100).sort_values(ascending=True)
        
        colors = [self.COLOR_SCHEME['success'] if p < 5 else 
                 self.COLOR_SCHEME['warning'] if p < 20 else 
                 self.COLOR_SCHEME['danger'] 
                 for p in null_percentages.values]
        
        fig = go.Figure(data=[
            go.Bar(
                x=null_percentages.values,
                y=null_percentages.index,
                orientation='h',
                marker_color=colors,
                text=null_percentages.values.round(1),
                texttemplate='%{text}%',
                textposition='outside'
            )
        ])
        
        fig.update_layout(
            title='Complétude des données par colonne',
            xaxis_title='% de valeurs manquantes',
            yaxis_title='',
            template=self.PLOTLY_TEMPLATE,
            height=max(400, len(null_percentages) * 25),
            showlegend=False
        )
        
        return fig
