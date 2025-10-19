"""
Dashboard Builder
Constructs interactive Streamlit dashboards from analysis results
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List
from .chart_factory import ChartFactory
import logging

logger = logging.getLogger(__name__)


class DashboardBuilder:
    """
    Builds comprehensive interactive dashboards in Streamlit
    
    Features:
    - Automatic layout generation
    - Interactive filters
    - Responsive design
    - Professional styling
    """
    
    def __init__(self, analysis_results: Dict[str, Any]):
        """
        Initialize dashboard builder
        
        Args:
            analysis_results: Results from analyze_document()
        """
        self.results = analysis_results
        self.df = analysis_results['dataframe']
        self.classification = analysis_results['classification']
        self.insights = analysis_results['insights']
        self.visualizations = analysis_results['priority_visualizations']
        
        # Initialize chart factory
        self.chart_factory = ChartFactory(
            self.df,
            self.classification['column_types']
        )
    
    def generate(self) -> None:
        """
        Generate complete dashboard in Streamlit
        
        This method renders the entire dashboard including:
        - Executive summary
        - Key insights
        - Interactive visualizations
        - Data quality metrics
        - Raw data explorer
        """
        logger.info("Generating dashboard")
        
        # Dashboard header
        self._render_header()
        
        # Executive summary
        self._render_executive_summary()
        
        # Key insights section
        self._render_insights_section()
        
        # Visualizations
        self._render_visualizations()
        
        # Data quality section
        self._render_data_quality()
        
        # Raw data explorer
        self._render_data_explorer()
    
    def _render_header(self) -> None:
        """Render dashboard header"""
        file_info = self.results['file_info']
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #DC143C 0%, #FF6B6B 100%); 
                    padding: 2rem; border-radius: 15px; color: white; margin-bottom: 2rem;">
            <h1 style="margin: 0; font-size: 2.5rem;">📊 Analyse Automatique</h1>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.9;">
                {file_info['name']} ({file_info['size_mb']:.2f} MB)
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_executive_summary(self) -> None:
        """Render executive summary with key metrics"""
        summary = self.classification['dataset_summary']
        quality_score = self.classification['quality_score']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📋 Lignes",
                value=f"{summary['total_rows']:,}",
                delta=None
            )
        
        with col2:
            st.metric(
                label="📊 Colonnes",
                value=summary['total_columns'],
                delta=None
            )
        
        with col3:
            quality_icon = "✅" if quality_score >= 80 else "⚠️" if quality_score >= 60 else "❌"
            st.metric(
                label=f"{quality_icon} Qualité",
                value=f"{quality_score}/100",
                delta=None
            )
        
        with col4:
            st.metric(
                label="🔗 Corrélations",
                value=len(self.classification['correlations']),
                delta=None
            )
        
        # Summary text
        st.info(f"📝 **Résumé**: {self.results['summary']}")
    
    def _render_insights_section(self) -> None:
        """Render key insights"""
        st.markdown("### 💡 Insights Clés")
        
        if not self.insights:
            st.info("Aucun insight particulier détecté")
            return
        
        # Display insights in expandable sections
        for idx, insight in enumerate(self.insights[:10], 1):  # Limit to top 10
            with st.expander(f"Insight #{idx}", expanded=(idx <= 3)):
                st.markdown(insight)
    
    def _render_visualizations(self) -> None:
        """Render all visualizations"""
        st.markdown("### 📈 Visualisations")
        
        if not self.visualizations:
            st.warning("Aucune visualisation disponible")
            return
        
        # Create tabs for different visualization categories
        viz_by_priority = {}
        for viz in self.visualizations:
            priority = viz.get('priority', 99)
            if priority not in viz_by_priority:
                viz_by_priority[priority] = []
            viz_by_priority[priority].append(viz)
        
        # Render visualizations
        for viz in self.visualizations[:8]:  # Limit to 8 charts
            try:
                fig = self.chart_factory.create_chart(viz)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    if viz.get('description'):
                        st.caption(viz['description'])
            except Exception as e:
                logger.error(f"Error rendering visualization: {str(e)}")
                st.error(f"Erreur lors de la génération du graphique: {viz.get('title', 'Unknown')}")
    
    def _render_data_quality(self) -> None:
        """Render data quality section"""
        st.markdown("### 🎯 Qualité des Données")
        
        # Data completeness chart
        try:
            completeness_fig = self.chart_factory.create_data_overview_chart()
            st.plotly_chart(completeness_fig, use_container_width=True)
        except Exception as e:
            logger.error(f"Error creating completeness chart: {str(e)}")
        
        # Detailed quality metrics
        with st.expander("📊 Métriques Détaillées"):
            col_stats = self.classification['column_stats']
            
            quality_data = []
            for col, stats in col_stats.items():
                quality_data.append({
                    'Colonne': col,
                    'Type': stats['type'],
                    'Valeurs Uniques': stats['unique_count'],
                    '% Null': f"{stats['null_percentage']:.1f}%",
                    'Complétude': f"{100 - stats['null_percentage']:.1f}%"
                })
            
            quality_df = pd.DataFrame(quality_data)
            st.dataframe(quality_df, use_container_width=True)
    
    def _render_data_explorer(self) -> None:
        """Render interactive data explorer"""
        st.markdown("### 🔍 Explorateur de Données")
        
        with st.expander("Afficher les données brutes", expanded=False):
            # Column selection
            available_cols = list(self.df.columns)
            selected_cols = st.multiselect(
                "Sélectionner les colonnes à afficher",
                options=available_cols,
                default=available_cols[:min(10, len(available_cols))]
            )
            
            if selected_cols:
                # Row filtering
                num_rows = st.slider(
                    "Nombre de lignes à afficher",
                    min_value=10,
                    max_value=min(1000, len(self.df)),
                    value=min(100, len(self.df)),
                    step=10
                )
                
                # Display data
                st.dataframe(
                    self.df[selected_cols].head(num_rows),
                    use_container_width=True
                )
                
                # Download option
                csv = self.df[selected_cols].head(num_rows).to_csv(index=False)
                st.download_button(
                    label="📥 Télécharger les données (CSV)",
                    data=csv,
                    file_name="data_export.csv",
                    mime="text/csv"
                )
    
    def render_compact(self) -> None:
        """
        Render a compact version of the dashboard
        
        Useful for integrating into existing applications
        """
        # Quick summary
        col1, col2, col3 = st.columns(3)
        
        summary = self.classification['dataset_summary']
        quality_score = self.classification['quality_score']
        
        with col1:
            st.metric("Lignes", f"{summary['total_rows']:,}")
        with col2:
            st.metric("Colonnes", summary['total_columns'])
        with col3:
            st.metric("Qualité", f"{quality_score}/100")
        
        # Top insights (max 3)
        if self.insights:
            st.markdown("**💡 Top Insights:**")
            for insight in self.insights[:3]:
                st.info(insight)
        
        # Key visualization (if available)
        if self.visualizations:
            try:
                fig = self.chart_factory.create_chart(self.visualizations[0])
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            except:
                pass
