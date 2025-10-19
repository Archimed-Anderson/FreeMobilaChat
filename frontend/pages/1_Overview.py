"""
Modern Overview Dashboard Page
Professional KPI dashboard with real-time metrics and insights
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import numpy as np

# Add components to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.filters import FilterManager
from components.charts import ChartManager
from components.tables import TableManager
from components.navigation import render_dashboard_navigation, render_page_breadcrumb

# Page configuration
st.set_page_config(
    page_title="Aperçu - FreeMobilaChat",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize managers
if 'filter_manager' not in st.session_state:
    st.session_state.filter_manager = FilterManager()
if 'chart_manager' not in st.session_state:
    st.session_state.chart_manager = ChartManager()
if 'table_manager' not in st.session_state:
    st.session_state.table_manager = TableManager()

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Modern Professional CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Modern scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb {
        background: #DC143C;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #B91C3C;
    }
    
    /* Dashboard Header */
    .dashboard-header {
        background: linear-gradient(135deg, #DC143C 0%, #FF6B6B 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 25px rgba(220, 20, 60, 0.2);
    }
    
    .dashboard-title {
        font-size: 2.5rem;
        font-weight: 800;
        font-family: 'Inter', sans-serif;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .dashboard-subtitle {
        font-size: 1.2rem;
        font-weight: 400;
        opacity: 0.95;
    }
    
    /* KPI Cards */
    .kpi-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid #e1e5e9;
        text-align: center;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(135deg, #DC143C 0%, #FF6B6B 100%);
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
    }
    
    .kpi-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #DC143C;
        margin-bottom: 0.5rem;
        font-family: 'Inter', sans-serif;
    }
    
    .kpi-label {
        color: #666;
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .kpi-change {
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    .kpi-change.positive {
        color: #28a745;
    }
    
    .kpi-change.negative {
        color: #dc3545;
    }
    
    .kpi-change.neutral {
        color: #6c757d;
    }
    
    /* Status Indicators */
    .status-indicator {
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        font-weight: 600;
        text-align: center;
        margin: 1rem 0;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-success {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .status-warning {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        color: #856404;
        border: 1px solid #ffeaa7;
    }
    
    .status-error {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    
    .status-processing {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        color: #0c5460;
        border: 1px solid #bee5eb;
    }
    
    /* Chart Containers */
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid #e1e5e9;
        margin-bottom: 1.5rem;
    }
    
    .chart-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 1rem;
        font-family: 'Inter', sans-serif;
    }
    
    /* Insights Cards */
    .insight-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #DC143C;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .insight-card:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .insight-title {
        font-weight: 600;
        color: #DC143C;
        margin-bottom: 0.5rem;
        font-size: 1rem;
    }
    
    .insight-text {
        color: #666;
        line-height: 1.5;
        font-size: 0.9rem;
    }
    
    /* Loading Animation */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid #DC143C;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .dashboard-title {
            font-size: 2rem;
        }
        .kpi-value {
            font-size: 2rem;
        }
        .kpi-card {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)


def check_api_health() -> bool:
    """Check if API is available"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def get_analysis_status(batch_id: str) -> Optional[Dict[str, Any]]:
    """Get analysis status"""
    try:
        response = requests.get(f"{API_BASE_URL}/analysis-status/{batch_id}")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def get_kpis(batch_id: str, user_role: str = "manager") -> Optional[Dict[str, Any]]:
    """Get KPIs for batch"""
    try:
        response = requests.get(f"{API_BASE_URL}/kpis/{batch_id}", params={"user_role": user_role})
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def create_sentiment_gauge(sentiment_data: Dict[str, int]) -> go.Figure:
    """Create a modern sentiment gauge chart"""
    total = sum(sentiment_data.values())
    if total == 0:
        return go.Figure()
    
    positive_pct = (sentiment_data.get('positive', 0) / total) * 100
    negative_pct = (sentiment_data.get('negative', 0) / total) * 100
    neutral_pct = (sentiment_data.get('neutral', 0) / total) * 100
    
    # Calculate overall sentiment score (-100 to +100)
    sentiment_score = positive_pct - negative_pct
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = sentiment_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Score de Sentiment Global"},
        delta = {'reference': 0},
        gauge = {
            'axis': {'range': [-100, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [-100, -50], 'color': "lightgray"},
                {'range': [-50, 0], 'color': "orange"},
                {'range': [0, 50], 'color': "lightgreen"},
                {'range': [50, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 0
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        font={'family': "Inter", 'size': 12},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def create_priority_radar(priority_data: Dict[str, int]) -> go.Figure:
    """Create a radar chart for priority distribution"""
    categories = list(priority_data.keys())
    values = list(priority_data.values())
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Priorités',
        line_color='#DC143C',
        fillcolor='rgba(220, 20, 60, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(values) if values else 1]
            )),
        showlegend=True,
        height=300,
        font={'family': "Inter", 'size': 12},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def create_trend_chart(tweets_data: List[Dict]) -> go.Figure:
    """Create a trend chart showing sentiment over time"""
    if not tweets_data:
        return go.Figure()
    
    # Group by date and calculate sentiment distribution
    df = pd.DataFrame(tweets_data)
    df['date'] = pd.to_datetime(df.get('date', datetime.now()))
    df['date'] = df['date'].dt.date
    
    daily_sentiment = df.groupby(['date', 'sentiment']).size().unstack(fill_value=0)
    
    fig = go.Figure()
    
    colors = {'positive': '#28a745', 'negative': '#dc3545', 'neutral': '#6c757d'}
    
    for sentiment in ['positive', 'negative', 'neutral']:
        if sentiment in daily_sentiment.columns:
            fig.add_trace(go.Scatter(
                x=daily_sentiment.index,
                y=daily_sentiment[sentiment],
                mode='lines+markers',
                name=sentiment.title(),
                line=dict(color=colors[sentiment], width=3),
                marker=dict(size=6)
            ))
    
    fig.update_layout(
        title="Évolution du Sentiment dans le Temps",
        xaxis_title="Date",
        yaxis_title="Nombre de Tweets",
        height=300,
        font={'family': "Inter", 'size': 12},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def main():
    """Main overview page"""

    # Navigation
    render_dashboard_navigation()

    # Page breadcrumb
    render_page_breadcrumb("Aperçu", "Tableau de bord principal avec métriques en temps réel")

    # Dashboard Header
    st.markdown("""
    <div class="dashboard-header">
        <div class="dashboard-title">📊 Tableau de Bord Principal</div>
        <div class="dashboard-subtitle">Analyse en temps réel des performances et métriques clés</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Check API health
    if not check_api_health():
        st.error("🚨 **API Backend non disponible** - Vérifiez que le serveur FastAPI est démarré sur le port 8000")
        st.info("💡 **Solution**: Exécutez `python backend/start_server.py` dans un terminal séparé")
        return
    
    # Get current batch ID from session state
    batch_id = st.session_state.get('current_batch_id')
    
    if not batch_id:
        st.warning("⚠️ **Aucune analyse en cours** - Retournez à la page principale pour démarrer une analyse")
        
        # Show sample data or instructions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="kpi-card">
                <div class="kpi-value">📁</div>
                <div class="kpi-label">Charger un fichier</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="kpi-card">
                <div class="kpi-value">⚙️</div>
                <div class="kpi-label">Configurer l'analyse</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="kpi-card">
                <div class="kpi-value">🚀</div>
                <div class="kpi-label">Lancer l'analyse</div>
            </div>
            """, unsafe_allow_html=True)
        
        return
    
    # Get analysis status
    with st.spinner("🔄 Chargement des données..."):
    status = get_analysis_status(batch_id)
    
    if not status:
        st.error("❌ **Impossible de récupérer le statut de l'analyse**")
        return
    
    # Status indicator
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        status_text = status.get('status', 'unknown')
        if status_text == 'completed':
            st.markdown('<div class="status-indicator status-success">✅ Analyse Terminée</div>', unsafe_allow_html=True)
        elif status_text == 'processing':
            st.markdown('<div class="status-indicator status-processing">🔄 Analyse en Cours</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-indicator status-error">❌ Erreur dans l\'Analyse</div>', unsafe_allow_html=True)
    
    # Main KPI Cards
    st.subheader("📈 Métriques Principales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_tweets = status.get('total_tweets', 0)
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{total_tweets:,}</div>
            <div class="kpi-label">Total Tweets</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        analyzed_tweets = status.get('analyzed_tweets', 0)
        success_rate = (analyzed_tweets / total_tweets * 100) if total_tweets > 0 else 0
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{analyzed_tweets:,}</div>
            <div class="kpi-label">Analysés</div>
            <div class="kpi-change {'positive' if success_rate > 90 else 'negative' if success_rate < 70 else 'neutral'}">
                {success_rate:.1f}% de réussite
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        failed_tweets = status.get('failed_tweets', 0)
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{failed_tweets:,}</div>
            <div class="kpi-label">Échecs</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        cost = status.get('estimated_cost', 0)
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">€{cost:.4f}</div>
            <div class="kpi-label">Coût Estimé</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Detailed KPIs (only if analysis is complete)
    if status['status'] == 'completed':
        st.divider()
        
        # Get detailed KPIs
        user_role = st.session_state.get('user_role', 'manager')
        kpi_data = get_kpis(batch_id, user_role)
        
        if kpi_data:
            kpis = kpi_data.get('kpis', {})
            insights = kpi_data.get('insights', [])
            advanced_metrics = kpi_data.get('advanced_metrics', {})
            
            # Advanced Metrics Row
            st.subheader("📊 Métriques Avancées")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                sentiment_pct = kpis.get('sentiment_percentages', {})
                positive_pct = sentiment_pct.get('positive', 0)
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-value">{positive_pct:.1f}%</div>
                    <div class="kpi-label">Sentiment Positif</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                critical_count = kpis.get('critical_count', 0)
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-value">{critical_count:,}</div>
                    <div class="kpi-label">Priorité Critique</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                urgent_count = kpis.get('urgent_count', 0)
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-value">{urgent_count:,}</div>
                    <div class="kpi-label">Tweets Urgents</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                response_needed = kpis.get('response_needed_count', 0)
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-value">{response_needed:,}</div>
                    <div class="kpi-label">Réponse Requise</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Charts Section
            st.subheader("📈 Visualisations")
                
                chart_col1, chart_col2 = st.columns(2)
                
                with chart_col1:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<div class="chart-title">Distribution du Sentiment</div>', unsafe_allow_html=True)
                
                if 'sentiment_distribution' in kpis:
                    sentiment_chart = st.session_state.chart_manager.sentiment_pie_chart(
                        kpis['sentiment_distribution']
                    )
                    st.plotly_chart(sentiment_chart, use_container_width=True)
                else:
                    st.info("Données de sentiment non disponibles")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                with chart_col2:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<div class="chart-title">Répartition par Catégorie</div>', unsafe_allow_html=True)
                
                    if 'category_distribution' in kpis:
                        category_chart = st.session_state.chart_manager.category_bar_chart(
                            kpis['category_distribution']
                        )
                        st.plotly_chart(category_chart, use_container_width=True)
                else:
                    st.info("Données de catégorie non disponibles")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Advanced Charts Row
            chart_col3, chart_col4 = st.columns(2)
            
            with chart_col3:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<div class="chart-title">Score de Sentiment Global</div>', unsafe_allow_html=True)
                
                if 'sentiment_distribution' in kpis:
                    sentiment_gauge = create_sentiment_gauge(kpis['sentiment_distribution'])
                    st.plotly_chart(sentiment_gauge, use_container_width=True)
                else:
                    st.info("Données de sentiment non disponibles")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with chart_col4:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<div class="chart-title">Distribution des Priorités</div>', unsafe_allow_html=True)
                
                if 'priority_distribution' in kpis:
                    priority_radar = create_priority_radar(kpis['priority_distribution'])
                    st.plotly_chart(priority_radar, use_container_width=True)
                else:
                    st.info("Données de priorité non disponibles")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Insights Section
            if insights:
                st.subheader("💡 Insights Automatiques")
                
                for i, insight in enumerate(insights[:3]):  # Show top 3 insights
                    st.markdown(f"""
                    <div class="insight-card">
                        <div class="insight-title">💡 Insight #{i+1}</div>
                        <div class="insight-text">{insight}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        else:
            st.error("❌ **Impossible de récupérer les KPIs détaillés**")
    
    else:
        st.info("⏳ **L'analyse est en cours** - Les métriques détaillées seront disponibles une fois l'analyse terminée")
        
        # Show progress bar
        if status.get('total_tweets', 0) > 0:
            progress = status.get('analyzed_tweets', 0) / status.get('total_tweets', 1)
            st.progress(progress)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total", status.get('total_tweets', 0))
            with col2:
                st.metric("Analysés", status.get('analyzed_tweets', 0))
            with col3:
                st.metric("Progression", f"{progress*100:.1f}%")
        
        # Auto-refresh for processing status
        if status['status'] == 'processing':
            time.sleep(5)
            st.rerun()


if __name__ == "__main__":
    main()