"""
Interface Streamlit adaptative basée sur les résultats LLM
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import json

from ..services.adaptive_analysis_engine import AdaptiveAnalysisEngine
from ..services.smart_visualization_engine import SmartVisualizationEngine

logger = logging.getLogger(__name__)

class DynamicAnalysisUI:
    """
    Interface Streamlit adaptative basée sur les résultats LLM
    """
    
    def __init__(self):
        self.analysis_engine = AdaptiveAnalysisEngine()
        self.viz_engine = SmartVisualizationEngine()
        
    def render_dynamic_dashboard(self, analysis_results: Dict[str, Any]):
        """
        RENDU OBLIGATOIRE :
        - Header avec contexte détecté automatiquement
        - Métriques KPI personnalisées selon le domaine
        - Insights sous forme de cards intelligentes
        - Visualisations adaptatives en temps réel
        - Recommandations actionnables
        - Export rapport personnalisé
        """
        try:
            # Header avec contexte détecté
            self._render_analysis_header(analysis_results)
            
            # Métriques dynamiques
            self._render_adaptive_metrics(analysis_results)
            
            # Insights personnalisés
            self._render_contextual_insights(analysis_results)
            
            # Visualisations intelligentes
            self._render_smart_visualizations(analysis_results)
            
            # Recommandations actionnables
            self._render_actionable_recommendations(analysis_results)
            
            # Export et actions
            self._render_export_actions(analysis_results)
            
        except Exception as e:
            logger.error(f"Erreur lors du rendu du dashboard dynamique: {e}")
            st.error("Erreur lors de l'affichage des résultats d'analyse")

    def _render_analysis_header(self, analysis_results: Dict[str, Any]):
        """Affiche le header avec le contexte détecté"""
        try:
            classification = analysis_results.get('analysis', {}).get('classification', {})
            context = analysis_results.get('context', {})
            
            # Informations de base
            domain = classification.get('domain', 'Général')
            confidence = classification.get('confidence_score', 0.0)
            data_type = classification.get('data_type', 'Dataset')
            
            # Métriques du dataset
            dataset_metrics = analysis_results.get('analysis', {}).get('dataset_metrics', {})
            row_count = dataset_metrics.get('row_count', 0)
            column_count = dataset_metrics.get('column_count', 0)
            
            # Header principal
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #CC0000 0%, #8B0000 100%); 
                        padding: 2rem; border-radius: 15px; margin-bottom: 2rem; color: white;">
                <div style="text-align: center;">
                    <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">
                        <i class="fas fa-chart-line" style="margin-right: 1rem;"></i>
                        ANALYSE INTELLIGENTE
                    </h1>
                    <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.9;">
                        {domain} • {data_type} • {confidence:.1%} de confiance
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Métriques de base
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="Lignes de données",
                    value=f"{row_count:,}",
                    delta=None
                )
            
            with col2:
                st.metric(
                    label="Colonnes",
                    value=f"{column_count}",
                    delta=None
                )
            
            with col3:
                confidence_pct = f"{confidence:.1%}"
                st.metric(
                    label="Confiance IA",
                    value=confidence_pct,
                    delta=None
                )
            
            with col4:
                data_quality = analysis_results.get('analysis', {}).get('data_quality', {})
                completeness = 100 - data_quality.get('null_percentage', 0)
                st.metric(
                    label="Complétude",
                    value=f"{completeness:.1f}%",
                    delta=None
                )
            
        except Exception as e:
            logger.error(f"Erreur lors du rendu du header: {e}")

    def _render_adaptive_metrics(self, analysis_results: Dict[str, Any]):
        """Affiche les métriques adaptatives selon le domaine"""
        try:
            key_metrics = analysis_results.get('analysis', {}).get('key_metrics', [])
            
            if not key_metrics:
                st.info("Aucune métrique clé détectée pour ce dataset")
                return
            
            st.markdown("### Métriques Clés")
            
            # Groupement des métriques par importance
            high_importance = [m for m in key_metrics if m.get('importance', 0) >= 0.8]
            medium_importance = [m for m in key_metrics if 0.5 <= m.get('importance', 0) < 0.8]
            low_importance = [m for m in key_metrics if m.get('importance', 0) < 0.5]
            
            # Métriques haute importance
            if high_importance:
                st.markdown("#### Priorité Haute")
                cols = st.columns(min(len(high_importance), 4))
                for i, metric in enumerate(high_importance[:4]):
                    with cols[i % 4]:
                        self._render_metric_card(metric, "high")
            
            # Métriques moyenne importance
            if medium_importance:
                st.markdown("#### Priorité Moyenne")
                cols = st.columns(min(len(medium_importance), 4))
                for i, metric in enumerate(medium_importance[:4]):
                    with cols[i % 4]:
                        self._render_metric_card(metric, "medium")
            
            # Métriques basse importance
            if low_importance:
                with st.expander("Métriques Supplémentaires"):
                    cols = st.columns(min(len(low_importance), 4))
                    for i, metric in enumerate(low_importance[:8]):
                        with cols[i % 4]:
                            self._render_metric_card(metric, "low")
            
        except Exception as e:
            logger.error(f"Erreur lors du rendu des métriques: {e}")

    def _render_metric_card(self, metric: Dict[str, Any], priority: str):
        """Affiche une carte de métrique"""
        try:
            name = metric.get('name', 'Métrique')
            value = metric.get('value', 0)
            metric_type = metric.get('type', 'count')
            importance = metric.get('importance', 0.5)
            
            # Formatage de la valeur
            if isinstance(value, (int, float)):
                if value >= 1000000:
                    formatted_value = f"{value/1000000:.1f}M"
                elif value >= 1000:
                    formatted_value = f"{value/1000:.1f}K"
                else:
                    formatted_value = f"{value:,.0f}"
            else:
                formatted_value = str(value)
            
            # Couleur selon la priorité
            color_map = {
                'high': '#CC0000',
                'medium': '#FF6B6B',
                'low': '#FFB3B3'
            }
            color = color_map.get(priority, '#CC0000')
            
            st.markdown(f"""
            <div style="background: white; padding: 1rem; border-radius: 10px; 
                        border-left: 4px solid {color}; box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
                        margin-bottom: 1rem;">
                <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">
                    {name}
                </div>
                <div style="font-size: 1.5rem; font-weight: 700; color: {color};">
                    {formatted_value}
                </div>
                <div style="font-size: 0.8rem; color: #999;">
                    {metric_type} • {importance:.0%} importance
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            logger.error(f"Erreur lors du rendu de la carte de métrique: {e}")

    def _render_contextual_insights(self, analysis_results: Dict[str, Any]):
        """Affiche les insights contextuels"""
        try:
            insights = analysis_results.get('analysis', {}).get('insights', [])
            
            if not insights:
                st.info("Aucun insight spécifique généré pour ce dataset")
                return
            
            st.markdown("### Insights Intelligents")
            
            # Groupement par impact
            high_impact = [i for i in insights if i.get('impact') == 'high']
            medium_impact = [i for i in insights if i.get('impact') == 'medium']
            low_impact = [i for i in insights if i.get('impact') == 'low']
            
            # Affichage des insights haute impact
            if high_impact:
                st.markdown("#### Impact Élevé")
                for insight in high_impact:
                    self._render_insight_card(insight, "high")
            
            # Affichage des insights moyenne impact
            if medium_impact:
                st.markdown("#### Impact Moyen")
                for insight in medium_impact:
                    self._render_insight_card(insight, "medium")
            
            # Affichage des insights basse impact
            if low_impact:
                with st.expander("Insights Supplémentaires"):
                    for insight in low_impact:
                        self._render_insight_card(insight, "low")
            
        except Exception as e:
            logger.error(f"Erreur lors du rendu des insights: {e}")

    def _render_insight_card(self, insight: Dict[str, Any], impact: str):
        """Affiche une carte d'insight"""
        try:
            title = insight.get('title', 'Insight')
            description = insight.get('description', '')
            evidence = insight.get('evidence', '')
            confidence = insight.get('confidence', 0.7)
            
            # Icône selon l'impact
            icon_map = {
                'high': 'fas fa-exclamation-triangle',
                'medium': 'fas fa-info-circle',
                'low': 'fas fa-lightbulb'
            }
            icon = icon_map.get(impact, 'fas fa-info-circle')
            
            # Couleur selon l'impact
            color_map = {
                'high': '#DC2626',
                'medium': '#F59E0B',
                'low': '#10B981'
            }
            color = color_map.get(impact, '#6B7280')
            
            st.markdown(f"""
            <div style="background: white; padding: 1.5rem; border-radius: 10px; 
                        border-left: 4px solid {color}; box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
                        margin-bottom: 1rem;">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <i class="{icon}" style="color: {color}; font-size: 1.2rem; margin-right: 0.5rem;"></i>
                    <h4 style="margin: 0; color: {color}; font-weight: 600;">
                        {title}
                    </h4>
                </div>
                <p style="margin: 0 0 1rem 0; color: #374151; line-height: 1.6;">
                    {description}
                </p>
                {f'<p style="margin: 0; font-size: 0.9rem; color: #6B7280; font-style: italic;">Evidence: {evidence}</p>' if evidence else ''}
                <div style="margin-top: 1rem; font-size: 0.8rem; color: #9CA3AF;">
                    Confiance: {confidence:.0%} • Impact: {impact.title()}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            logger.error(f"Erreur lors du rendu de la carte d'insight: {e}")

    def _render_smart_visualizations(self, analysis_results: Dict[str, Any]):
        """Affiche les visualisations intelligentes"""
        try:
            visualizations = analysis_results.get('visualizations', [])
            
            if not visualizations:
                st.info("Aucune visualisation générée pour ce dataset")
                return
            
            st.markdown("### Visualisations Intelligentes")
            
            # Filtrage des visualisations faisables
            feasible_viz = [v for v in visualizations if v.get('status') == 'feasible']
            
            if not feasible_viz:
                st.warning("Aucune visualisation faisable avec les données disponibles")
                return
            
            # Affichage des visualisations
            for i, viz in enumerate(feasible_viz):
                try:
                    st.markdown(f"#### {viz.get('title', f'Graphique {i+1}')}")
                    
                    # Description
                    if viz.get('description'):
                        st.markdown(f"*{viz['description']}*")
                    
                    # Rationale
                    if viz.get('rationale'):
                        st.markdown(f"**Justification:** {viz['rationale']}")
                    
                    # Affichage du graphique
                    figure = viz.get('figure')
                    if figure:
                        st.plotly_chart(figure, use_container_width=True)
                    else:
                        st.info("Graphique non disponible")
                    
                    # Métadonnées
                    if viz.get('columns'):
                        st.markdown(f"**Colonnes utilisées:** {', '.join(viz['columns'])}")
                    
                    st.markdown("---")
                    
                except Exception as e:
                    logger.warning(f"Erreur lors de l'affichage de la visualisation {i}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Erreur lors du rendu des visualisations: {e}")

    def _render_actionable_recommendations(self, analysis_results: Dict[str, Any]):
        """Affiche les recommandations actionnables"""
        try:
            recommendations = analysis_results.get('analysis', {}).get('recommendations', [])
            
            if not recommendations:
                st.info("Aucune recommandation générée pour ce dataset")
                return
            
            st.markdown("### Recommandations Actionnables")
            
            # Groupement par priorité
            high_priority = [r for r in recommendations if r.get('priority') == 'high']
            medium_priority = [r for r in recommendations if r.get('priority') == 'medium']
            low_priority = [r for r in recommendations if r.get('priority') == 'low']
            
            # Affichage des recommandations haute priorité
            if high_priority:
                st.markdown("#### Priorité Haute")
                for rec in high_priority:
                    self._render_recommendation_card(rec, "high")
            
            # Affichage des recommandations moyenne priorité
            if medium_priority:
                st.markdown("#### Priorité Moyenne")
                for rec in medium_priority:
                    self._render_recommendation_card(rec, "medium")
            
            # Affichage des recommandations basse priorité
            if low_priority:
                with st.expander("Recommandations Supplémentaires"):
                    for rec in low_priority:
                        self._render_recommendation_card(rec, "low")
            
        except Exception as e:
            logger.error(f"Erreur lors du rendu des recommandations: {e}")

    def _render_recommendation_card(self, recommendation: Dict[str, Any], priority: str):
        """Affiche une carte de recommandation"""
        try:
            action = recommendation.get('action', 'Action recommandée')
            expected_impact = recommendation.get('expected_impact', 'Impact non spécifié')
            
            # Icône selon la priorité
            icon_map = {
                'high': 'fas fa-exclamation-circle',
                'medium': 'fas fa-info-circle',
                'low': 'fas fa-lightbulb'
            }
            icon = icon_map.get(priority, 'fas fa-info-circle')
            
            # Couleur selon la priorité
            color_map = {
                'high': '#DC2626',
                'medium': '#F59E0B',
                'low': '#10B981'
            }
            color = color_map.get(priority, '#6B7280')
            
            st.markdown(f"""
            <div style="background: white; padding: 1.5rem; border-radius: 10px; 
                        border-left: 4px solid {color}; box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
                        margin-bottom: 1rem;">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <i class="{icon}" style="color: {color}; font-size: 1.2rem; margin-right: 0.5rem;"></i>
                    <h4 style="margin: 0; color: {color}; font-weight: 600;">
                        Action Recommandée
                    </h4>
                </div>
                <p style="margin: 0 0 1rem 0; color: #374151; line-height: 1.6;">
                    {action}
                </p>
                <div style="background: #F3F4F6; padding: 0.75rem; border-radius: 6px; margin-top: 1rem;">
                    <strong>Impact attendu:</strong> {expected_impact}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            logger.error(f"Erreur lors du rendu de la carte de recommandation: {e}")

    def _render_export_actions(self, analysis_results: Dict[str, Any]):
        """Affiche les actions d'export et de téléchargement"""
        try:
            st.markdown("### Export et Actions")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Export JSON
                json_data = json.dumps(analysis_results, ensure_ascii=False, indent=2)
                st.download_button(
                    label="Télécharger Analyse JSON",
                    data=json_data,
                    file_name=f"analyse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            
            with col2:
                # Export CSV des métriques
                metrics = analysis_results.get('analysis', {}).get('key_metrics', [])
                if metrics:
                    metrics_df = pd.DataFrame(metrics)
                    csv_data = metrics_df.to_csv(index=False)
                    st.download_button(
                        label="Télécharger Métriques CSV",
                        data=csv_data,
                        file_name=f"metriques_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            
            with col3:
                # Nouvelle analyse
                if st.button("Nouvelle Analyse", type="primary"):
                    st.session_state.clear()
                    st.rerun()
            
        except Exception as e:
            logger.error(f"Erreur lors du rendu des actions d'export: {e}")

    async def analyze_and_display(self, df: pd.DataFrame, filename: str):
        """Analyse le dataset et affiche les résultats"""
        try:
            # Affichage du spinner pendant l'analyse
            with st.spinner("Analyse intelligente en cours..."):
                # Analyse du dataset
                analysis_results = await self.analysis_engine.analyze_dataset(df, filename)
                
                # Génération des visualisations
                visualizations = self.viz_engine.generate_contextual_charts(
                    analysis_results.get('analysis', {}), df
                )
                analysis_results['visualizations'] = visualizations
                
                # Stockage en session state
                st.session_state['analysis_results'] = analysis_results
                st.session_state['analysis_completed'] = True
            
            # Affichage des résultats
            self.render_dynamic_dashboard(analysis_results)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse et de l'affichage: {e}")
            st.error(f"Erreur lors de l'analyse: {str(e)}")

    def render_analysis_progress(self, step: str, progress: float = 0.0):
        """Affiche la progression de l'analyse"""
        try:
            progress_bar = st.progress(progress)
            
            steps = {
                'inspection': "Inspection intelligente des données...",
                'prompt_generation': "Génération du prompt personnalisé...",
                'llm_analysis': "Analyse IA adaptative...",
                'enrichment': "Enrichissement des résultats...",
                'visualization': "Génération des visualisations...",
                'complete': "Analyse terminée!"
            }
            
            st.markdown(f"**{steps.get(step, step)}**")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage de la progression: {e}")
