"""
Page Dashboard - FreeMobilaChat
Visualisations avancées et KPIs interactifs
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# Imports locaux - correction des imports relatifs
import sys
from pathlib import Path

# Ajout du répertoire parent au path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

try:
    from config.settings import get_config, get_user_role, UserRole
    from config.api_config import get_api_client
    from components.ui_components import render_modern_header, render_metrics_dashboard
    from components.analysis_engine import get_analysis_engine
    from services.kpi_calculator import get_kpi_calculator
    from utils.helpers import format_number, get_current_timestamp, create_metric_card
except ImportError as e:
    # Fallback si les imports échouent
    logger = logging.getLogger(__name__)
    logger.warning(f"Import error: {e}. Using fallback mode.")
    
    # Définitions de fallback
    def get_config():
        from dataclasses import dataclass
        @dataclass
        class Config:
            max_file_size: int = 50
            supported_formats: list = None
        return Config()
    
    def get_api_client():
        return None
    
    def render_modern_header(title, subtitle, show_connection_status=False):
        st.markdown(f"<h1 style='text-align: center; color: #667eea;'>{title}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #666;'>{subtitle}</p>", unsafe_allow_html=True)
    
    def render_metrics_dashboard(metrics):
        cols = st.columns(len(metrics))
        for i, metric in enumerate(metrics):
            with cols[i]:
                st.metric(metric.get('label', ''), metric.get('value', ''), metric.get('delta', ''))
    
    def get_analysis_engine():
        return None
    
    def get_kpi_calculator():
        return None
    
    def format_number(value, decimals=0):
        return f"{value:,.{decimals}f}"
    
    def get_current_timestamp():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def create_metric_card(label, value, delta=None):
        return {"label": label, "value": value, "delta": delta}
    
    class UserRole:
        MANAGER = "manager"
        ANALYST = "analyst"
        AGENT = "agent"
        ADMIN = "admin"
    
    def get_user_role():
        return UserRole.MANAGER

# Configuration
st.set_page_config(
    page_title="Dashboard KPI - FreeMobilaChat",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Logger
logger = logging.getLogger(__name__)

def main():
    """Page principale du dashboard"""
    
    # Configuration
    config = get_config()
    api_client = get_api_client()
    analysis_engine = get_analysis_engine()
    kpi_calculator = get_kpi_calculator()
    
    # Header moderne
    render_modern_header(
        title=" Dashboard KPI",
        subtitle="Visualisations avancées et indicateurs de performance",
        show_connection_status=True
    )
    
    # Vérification des données
    if not _check_analysis_data():
        return
    
    # Sidebar avec filtres
    filters = _render_sidebar_filters()
    
    # Récupération des données
    kpi_data = st.session_state.get("kpi_data", {})
    analysis_result = st.session_state.get("analysis_result", {})
    tweets_data = st.session_state.get("uploaded_data")
    
    # Affichage des métriques principales
    _render_main_metrics(kpi_data)
    
    # Tabs pour différentes vues
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        " Vue d'ensemble", 
        " Sentiment", 
        " Catégories", 
        " Priorités", 
        " Détails"
    ])
    
    with tab1:
        _render_overview_tab(kpi_data, analysis_result)
    
    with tab2:
        _render_sentiment_tab(kpi_data, tweets_data, filters)
    
    with tab3:
        _render_category_tab(kpi_data, tweets_data, filters)
    
    with tab4:
        _render_priority_tab(kpi_data, tweets_data, filters)
    
    with tab5:
        _render_details_tab(tweets_data, filters)
    
    # Actions en bas de page
    _render_bottom_actions()

def _check_analysis_data() -> bool:
    """Vérifie si des données d'analyse sont disponibles"""
    
    if "kpi_data" not in st.session_state or not st.session_state.kpi_data:
        st.warning("""
         **Aucune donnée d'analyse disponible**
        
        Pour voir le dashboard, vous devez d'abord :
        1. Charger un fichier de données
        2. Lancer une analyse
        
        [Retourner à l'analyse](pages/01_analyse.py)
        """)
        return False
    
    return True

def _render_sidebar_filters() -> Dict[str, Any]:
    """Affiche les filtres dans la sidebar"""
    
    with st.sidebar:
        st.markdown("###  Filtres")
        
        # Filtre par sentiment
        sentiment = st.selectbox(
            "Sentiment",
            ["Tous", "Positif", "Négatif", "Neutre"],
            index=0
        )
        
        # Filtre par catégorie
        category = st.selectbox(
            "Catégorie",
            ["Toutes", "Plainte", "Question", "Éloge", "Suggestion"],
            index=0
        )
        
        # Filtre par priorité
        priority = st.selectbox(
            "Priorité",
            ["Toutes", "Haute", "Moyenne", "Basse"],
            index=0
        )
        
        # Filtre par date
        date_range = st.date_input(
            "Plage de dates",
            value=None,
            help="Sélectionnez une plage de dates"
        )
        
        # Filtre par longueur de texte
        text_length = st.slider(
            "Longueur minimale du texte",
            min_value=0,
            max_value=500,
            value=0,
            step=10
        )
        
        st.divider()
        
        # Actions rapides
        st.markdown("###  Actions")
        
        if st.button(" Actualiser", use_container_width=True):
            st.rerun()
        
        if st.button(" Exporter", use_container_width=True):
            _export_data()
        
        if st.button(" Nouvelle Analyse", use_container_width=True):
            _clear_analysis_data()
    
    return {
        "sentiment": sentiment if sentiment != "Tous" else None,
        "category": category if category != "Toutes" else None,
        "priority": priority if priority != "Toutes" else None,
        "date_range": date_range,
        "text_length": text_length
    }

def _render_main_metrics(kpi_data: Dict[str, Any]):
    """Affiche les métriques principales"""
    
    st.markdown("###  Métriques Principales")
    
    # Création des métriques
    metrics = {
        "total_tweets": {
            "title": "Total Tweets",
            "value": format_number(kpi_data.get("total_tweets", 0)),
            "icon": ""
        },
        "sentiment_score": {
            "title": "Score Sentiment",
            "value": f"{kpi_data.get('sentiment_score', 0):.2f}",
            "icon": ""
        },
        "priority_score": {
            "title": "Score Priorité",
            "value": f"{kpi_data.get('priority_score', 0):.2f}",
            "icon": ""
        },
        "quality_score": {
            "title": "Qualité Données",
            "value": f"{kpi_data.get('data_quality_score', 0):.0f}%",
            "icon": ""
        }
    }
    
    # Affichage des métriques
    render_metrics_dashboard(metrics)

def _render_overview_tab(kpi_data: Dict[str, Any], analysis_result: Dict[str, Any]):
    """Affiche l'onglet vue d'ensemble"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Graphique de distribution des sentiments
        if "sentiment_distribution" in kpi_data:
            st.markdown("####  Distribution des Sentiments")
            
            sentiment_data = kpi_data["sentiment_distribution"]
            fig = px.pie(
                values=list(sentiment_data.values()),
                names=list(sentiment_data.keys()),
                title="Répartition des sentiments",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Graphique de distribution des catégories
        if "category_distribution" in kpi_data:
            st.markdown("####  Distribution des Catégories")
            
            category_data = kpi_data["category_distribution"]
            fig = px.bar(
                x=list(category_data.keys()),
                y=list(category_data.values()),
                title="Répartition par catégorie",
                color=list(category_data.keys()),
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # Métriques d'engagement
    if "engagement_kpis" in kpi_data:
        st.markdown("####  Métriques d'Engagement")
        
        engagement = kpi_data["engagement_kpis"]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Retweets Total", format_number(engagement.get("total_retweets", 0)))
        with col2:
            st.metric("Favoris Total", format_number(engagement.get("total_favorites", 0)))
        with col3:
            st.metric("Retweets Moyen", f"{engagement.get('avg_retweets_per_tweet', 0):.1f}")
        with col4:
            st.metric("Favoris Moyen", f"{engagement.get('avg_favorites_per_tweet', 0):.1f}")

def _render_sentiment_tab(kpi_data: Dict[str, Any], tweets_data: pd.DataFrame, filters: Dict[str, Any]):
    """Affiche l'onglet sentiment"""
    
    if "sentiment_distribution" not in kpi_data:
        st.info("Aucune donnée de sentiment disponible")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Graphique en barres des sentiments
        st.markdown("####  Répartition des Sentiments")
        
        sentiment_data = kpi_data["sentiment_distribution"]
        fig = px.bar(
            x=list(sentiment_data.keys()),
            y=list(sentiment_data.values()),
            title="Distribution des sentiments",
            color=list(sentiment_data.keys()),
            color_discrete_map={
                "positive": "#2E8B57",
                "negative": "#DC143C",
                "neutral": "#FFD700"
            }
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Score de sentiment
        st.markdown("####  Score de Sentiment")
        
        sentiment_score = kpi_data.get("sentiment_score", 0)
        
        # Gauge chart
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = sentiment_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Score Global"},
            delta = {'reference': 0},
            gauge = {
                'axis': {'range': [-1, 1]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [-1, -0.5], 'color': "lightgray"},
                    {'range': [-0.5, 0.5], 'color': "gray"},
                    {'range': [0.5, 1], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 0
                }
            }
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Analyse détaillée des sentiments
    st.markdown("####  Analyse Détaillée")
    
    sentiment_counts = kpi_data.get("sentiment_counts", {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Positif",
            format_number(sentiment_counts.get("positive", 0)),
            delta=f"{kpi_data['sentiment_distribution']['positive']*100:.1f}%"
        )
    
    with col2:
        st.metric(
            "Négatif",
            format_number(sentiment_counts.get("negative", 0)),
            delta=f"{kpi_data['sentiment_distribution']['negative']*100:.1f}%"
        )
    
    with col3:
        st.metric(
            "Neutre",
            format_number(sentiment_counts.get("neutral", 0)),
            delta=f"{kpi_data['sentiment_distribution']['neutral']*100:.1f}%"
        )

def _render_category_tab(kpi_data: Dict[str, Any], tweets_data: pd.DataFrame, filters: Dict[str, Any]):
    """Affiche l'onglet catégories"""
    
    if "category_distribution" not in kpi_data:
        st.info("Aucune donnée de catégorie disponible")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Graphique en barres des catégories
        st.markdown("####  Répartition par Catégorie")
        
        category_data = kpi_data["category_distribution"]
        fig = px.bar(
            x=list(category_data.keys()),
            y=list(category_data.values()),
            title="Distribution des catégories",
            color=list(category_data.keys()),
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Graphique en donut des catégories
        st.markdown("####  Répartition Circulaire")
        
        category_data = kpi_data["category_distribution"]
        fig = px.pie(
            values=list(category_data.values()),
            names=list(category_data.keys()),
            title="Répartition des catégories",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    # Top catégorie
    top_category = kpi_data.get("top_category", "N/A")
    st.info(f" **Catégorie dominante** : {top_category}")

def _render_priority_tab(kpi_data: Dict[str, Any], tweets_data: pd.DataFrame, filters: Dict[str, Any]):
    """Affiche l'onglet priorités"""
    
    if "priority_distribution" not in kpi_data:
        st.info("Aucune donnée de priorité disponible")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Graphique en barres des priorités
        st.markdown("####  Répartition par Priorité")
        
        priority_data = kpi_data["priority_distribution"]
        fig = px.bar(
            x=list(priority_data.keys()),
            y=list(priority_data.values()),
            title="Distribution des priorités",
            color=list(priority_data.keys()),
            color_discrete_map={
                "high": "#FF4444",
                "medium": "#FFA500",
                "low": "#32CD32"
            }
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Score de priorité
        st.markdown("####  Score de Priorité")
        
        priority_score = kpi_data.get("priority_score", 0)
        
        # Gauge chart
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = priority_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Score Global"},
            gauge = {
                'axis': {'range': [0, 1]},
                'bar': {'color': "darkred"},
                'steps': [
                    {'range': [0, 0.33], 'color': "lightgreen"},
                    {'range': [0.33, 0.66], 'color': "orange"},
                    {'range': [0.66, 1], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 0.5
                }
            }
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Tweets urgents
    urgent_tweets = kpi_data.get("urgent_tweets", 0)
    st.warning(f" **{urgent_tweets} tweets urgents** nécessitent une attention immédiate")

def _render_details_tab(tweets_data: pd.DataFrame, filters: Dict[str, Any]):
    """Affiche l'onglet détails"""
    
    if tweets_data is None or tweets_data.empty:
        st.info("Aucune donnée de tweets disponible")
        return
    
    st.markdown("####  Détails des Tweets")
    
    # Filtrage des données
    filtered_data = tweets_data.copy()
    
    if filters.get("text_length", 0) > 0:
        filtered_data = filtered_data[filtered_data['text'].str.len() >= filters["text_length"]]
    
    # Affichage des données
    st.dataframe(
        filtered_data[['text', 'author', 'date']].head(100),
        use_container_width=True,
        height=400
    )
    
    # Statistiques
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Tweets affichés", len(filtered_data))
    with col2:
        st.metric("Longueur moyenne", f"{filtered_data['text'].str.len().mean():.1f} caractères")
    with col3:
        st.metric("Auteurs uniques", filtered_data['author'].nunique())

def _render_bottom_actions():
    """Affiche les actions en bas de page"""
    
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button(" Exporter PDF", use_container_width=True):
            st.info("Fonctionnalité d'export PDF en cours de développement")
    
    with col2:
        if st.button(" Exporter Excel", use_container_width=True):
            st.info("Fonctionnalité d'export Excel en cours de développement")
    
    with col3:
        if st.button(" Actualiser", use_container_width=True):
            st.rerun()
    
    with col4:
        if st.button(" Nouvelle Analyse", use_container_width=True):
            _clear_analysis_data()

def _export_data():
    """Exporte les données"""
    
    st.info("Fonctionnalité d'export en cours de développement")

def _clear_analysis_data():
    """Nettoie les données d'analyse"""
    
    keys_to_clear = [
        "kpi_data", "analysis_result", "uploaded_data", 
        "current_batch_id", "analysis_status"
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    st.success("Données d'analyse nettoyées")
    st.switch_page("pages/01_analyse.py")

if __name__ == "__main__":
    main()
