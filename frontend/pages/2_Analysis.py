"""
Enhanced Analysis Dashboard Page
Comprehensive analytics dashboard with advanced filtering and detailed insights
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import sys
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
    page_title="Analyse - FreeMobilaChat",
    page_icon="🔍",
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
    .analysis-header {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 25px rgba(17, 153, 142, 0.2);
    }
    
    .analysis-title {
        font-size: 2.5rem;
        font-weight: 800;
        font-family: 'Inter', sans-serif;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .analysis-subtitle {
        font-size: 1.2rem;
        font-weight: 400;
        opacity: 0.95;
    }
    
    /* Filter Container */
    .filter-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid #e1e5e9;
        margin-bottom: 1.5rem;
    }
    
    .filter-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 1rem;
        font-family: 'Inter', sans-serif;
    }
    
    /* Tweet Cards */
    .tweet-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #007bff;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        position: relative;
    }
    
    .tweet-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
    }
    
    .tweet-card.sentiment-negative {
        border-left-color: #dc3545 !important;
    }
    
    .tweet-card.sentiment-neutral {
        border-left-color: #6c757d !important;
    }
    
    .tweet-card.sentiment-positive {
        border-left-color: #28a745 !important;
    }
    
    .tweet-card.sentiment-critical {
        border-left-color: #ff6b35 !important;
        background: linear-gradient(135deg, #fff5f5 0%, #ffffff 100%);
    }
    
    .tweet-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #e9ecef;
    }
    
    .tweet-author {
        font-weight: 600;
        color: #DC143C;
        font-size: 1rem;
    }
    
    .tweet-date {
        color: #6c757d;
        font-size: 0.8rem;
    }
    
    .tweet-text {
        color: #333;
        line-height: 1.6;
        margin-bottom: 1rem;
        font-size: 0.95rem;
    }
    
    .tweet-tags {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin-bottom: 0.5rem;
    }
    
    .tweet-tag {
        background: #e9ecef;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.75rem;
        font-weight: 500;
        color: #495057;
    }
    
    .tweet-tag.sentiment-positive {
        background: #d4edda;
        color: #155724;
    }
    
    .tweet-tag.sentiment-negative {
        background: #f8d7da;
        color: #721c24;
    }
    
    .tweet-tag.sentiment-neutral {
        background: #d1ecf1;
        color: #0c5460;
    }
    
    .tweet-tag.priority-critical {
        background: #fff3cd;
        color: #856404;
        font-weight: 600;
    }
    
    .tweet-tag.priority-high {
        background: #f8d7da;
        color: #721c24;
    }
    
    .tweet-tag.urgent {
        background: #ff6b35;
        color: white;
        font-weight: 600;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    /* Stats Cards */
    .stats-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid #e1e5e9;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stats-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
    }
    
    .stats-value {
        font-size: 2rem;
        font-weight: 800;
        color: #DC143C;
        margin-bottom: 0.5rem;
        font-family: 'Inter', sans-serif;
    }
    
    .stats-label {
        color: #666;
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
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
    
    /* Export Section */
    .export-section {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #dee2e6;
        margin-bottom: 1.5rem;
    }
    
    .export-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #DC143C;
        margin-bottom: 1rem;
    }
    
    /* Pagination */
    .pagination {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .pagination button {
        background: #DC143C;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .pagination button:hover {
        background: #B91C3C;
        transform: translateY(-1px);
    }
    
    .pagination button:disabled {
        background: #6c757d;
        cursor: not-allowed;
        transform: none;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .analysis-title {
            font-size: 2rem;
        }
        .tweet-card {
            padding: 1rem;
        }
        .tweet-tags {
            flex-direction: column;
            gap: 0.3rem;
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


def get_tweets(batch_id: str, filters: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
    """Get tweets with filters"""
    try:
        params = {"limit": 1000, "offset": 0}
        if filters:
            params.update({k: v for k, v in filters.items() if v is not None and v != False})
        
        response = requests.get(f"{API_BASE_URL}/tweets/{batch_id}", params=params)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def get_kpis(batch_id: str, user_role: str = "analyste") -> Optional[Dict[str, Any]]:
    """Get KPIs for batch"""
    try:
        response = requests.get(f"{API_BASE_URL}/kpis/{batch_id}", params={"user_role": user_role})
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def create_word_cloud_data(tweets: List[Dict]) -> Dict[str, int]:
    """Create word frequency data for word cloud"""
    from collections import Counter
    import re
    
    # Combine all tweet texts
    all_text = " ".join([tweet.get('text', '') for tweet in tweets])
    
    # Extract words (simple approach)
    words = re.findall(r'\b\w+\b', all_text.lower())
    
    # Filter out common French stop words
    stop_words = {'le', 'la', 'les', 'de', 'du', 'des', 'un', 'une', 'et', 'ou', 'mais', 'donc', 'or', 'ni', 'car', 'que', 'qui', 'quoi', 'dont', 'où', 'à', 'au', 'aux', 'avec', 'sans', 'pour', 'par', 'sur', 'dans', 'en', 'vers', 'chez', 'entre', 'sous', 'contre', 'depuis', 'jusqu', 'pendant', 'avant', 'après', 'il', 'elle', 'nous', 'vous', 'ils', 'elles', 'je', 'tu', 'ce', 'cette', 'ces', 'son', 'sa', 'ses', 'mon', 'ma', 'mes', 'ton', 'ta', 'tes', 'notre', 'nos', 'votre', 'vos', 'leur', 'leurs', 'être', 'avoir', 'faire', 'dire', 'aller', 'voir', 'savoir', 'pouvoir', 'falloir', 'vouloir', 'devoir', 'venir', 'prendre', 'donner', 'mettre', 'partir', 'rester', 'passer', 'sortir', 'entrer', 'monter', 'descendre', 'ouvrir', 'fermer', 'commencer', 'finir', 'continuer', 'arrêter', 'revenir', 'retourner', 'reprendre', 'recommencer', 'refaire', 'redire', 'revoir', 'reprendre', 'recommencer', 'refaire', 'redire', 'revoir'}
    
    # Count words
    word_counts = Counter([word for word in words if len(word) > 3 and word not in stop_words])
    
    return dict(word_counts.most_common(50))


def create_sentiment_timeline(tweets: List[Dict]) -> go.Figure:
    """Create a timeline chart showing sentiment over time"""
    if not tweets:
        return go.Figure()
    
    df = pd.DataFrame(tweets)
    df['date'] = pd.to_datetime(df.get('date', datetime.now()))
    df['date'] = df['date'].dt.floor('H')  # Group by hour
    
    hourly_sentiment = df.groupby(['date', 'sentiment']).size().unstack(fill_value=0)
    
    fig = go.Figure()
    
    colors = {'positive': '#28a745', 'negative': '#dc3545', 'neutral': '#6c757d'}
    
    for sentiment in ['positive', 'negative', 'neutral']:
        if sentiment in hourly_sentiment.columns:
            fig.add_trace(go.Scatter(
                x=hourly_sentiment.index,
                y=hourly_sentiment[sentiment],
                mode='lines+markers',
                name=sentiment.title(),
                line=dict(color=colors[sentiment], width=3),
                marker=dict(size=6),
                fill='tonexty' if sentiment != 'positive' else None
            ))
    
    fig.update_layout(
        title="Évolution du Sentiment dans le Temps",
        xaxis_title="Heure",
        yaxis_title="Nombre de Tweets",
        height=400,
        font={'family': "Inter", 'size': 12},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified'
    )
    
    return fig


def create_category_sunburst(tweets: List[Dict]) -> go.Figure:
    """Create a sunburst chart for category and sentiment distribution"""
    if not tweets:
        return go.Figure()
    
    df = pd.DataFrame(tweets)
    
    # Create hierarchical data
    category_sentiment = df.groupby(['category', 'sentiment']).size().reset_index(name='count')
    
    # Create labels and parents for sunburst
    labels = []
    parents = []
    values = []
    
    # Add root
    labels.append("Total")
    parents.append("")
    values.append(category_sentiment['count'].sum())
    
    # Add categories
    for category in category_sentiment['category'].unique():
        labels.append(category)
        parents.append("Total")
        values.append(category_sentiment[category_sentiment['category'] == category]['count'].sum())
        
        # Add sentiments for each category
        for sentiment in category_sentiment[category_sentiment['category'] == category]['sentiment'].unique():
            labels.append(f"{category} - {sentiment}")
            parents.append(category)
            values.append(category_sentiment[
                (category_sentiment['category'] == category) & 
                (category_sentiment['sentiment'] == sentiment)
            ]['count'].iloc[0])
    
    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",
        hovertemplate='<b>%{label}</b><br>Count: %{value}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Distribution par Catégorie et Sentiment",
        height=400,
        font={'family': "Inter", 'size': 12},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def main():
    """Main analysis page"""

    # Navigation
    render_dashboard_navigation()

    # Page breadcrumb
    render_page_breadcrumb("Analyse Détaillée", "Exploration avancée et analyse approfondie des tweets")

    # Dashboard Header
    col1, col2 = st.columns([3, 1])
    
    with col1:
    st.markdown("""
    <div class="analysis-header">
            <div class="analysis-title">🔍 Analyse Détaillée</div>
            <div class="analysis-subtitle">Exploration avancée et analyse approfondie des tweets</div>
    </div>
    """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
        if st.button("🆕 Nouvelle Analyse", use_container_width=True, type="primary"):
            # Clear session state and redirect to main page
            for key in ['uploaded_data', 'current_batch_id', 'uploaded_filename']:
                if key in st.session_state:
                    del st.session_state[key]
            st.switch_page("streamlit_app.py")
    
    # Check API health
    if not check_api_health():
        st.error("🚨 **API Backend non disponible** - Vérifiez que le serveur FastAPI est démarré sur le port 8000")
        st.info("💡 **Solution**: Exécutez `python backend/start_server.py` dans un terminal séparé")
        return
    
    # Get current batch ID from session state
    batch_id = st.session_state.get('current_batch_id')
    
    if not batch_id:
        st.warning("⚠️ **Aucune analyse en cours** - Retournez à la page principale pour démarrer une analyse")
        return
    
    # Sidebar filters
    with st.sidebar:
        st.markdown("### 🔍 Filtres d'Analyse")
        
        # Create filters
        filters = st.session_state.filter_manager.create_sidebar_filters()
        
        st.divider()
        
        # Export options
        st.markdown("### 📤 Export")
        
        if st.button("📊 Exporter CSV", use_container_width=True):
            # Get filtered data
            tweets_data = get_tweets(batch_id, filters)
            if tweets_data and tweets_data.get('tweets'):
                df = pd.DataFrame(tweets_data['tweets'])
                csv = df.to_csv(index=False)
                st.download_button(
                    label="💾 Télécharger CSV",
                    data=csv,
                    file_name=f"tweets_analysis_{batch_id}.csv",
                    mime="text/csv"
                )
        
        if st.button("📈 Exporter Excel", use_container_width=True):
            tweets_data = get_tweets(batch_id, filters)
            if tweets_data and tweets_data.get('tweets'):
                df = pd.DataFrame(tweets_data['tweets'])
                # Create Excel file in memory
                from io import BytesIO
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Tweets', index=False)
                output.seek(0)
                st.download_button(
                    label="📊 Télécharger Excel",
                    data=output.getvalue(),
                    file_name=f"tweets_analysis_{batch_id}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📝 Tweets Détaillés")
        
        # Get filtered tweets
        with st.spinner("🔄 Chargement des tweets..."):
        tweets_data = get_tweets(batch_id, filters)
        
        if tweets_data and tweets_data.get('tweets'):
            tweets_list = tweets_data['tweets']
            
            # Apply additional filters
            filtered_tweets = st.session_state.filter_manager.apply_filters_to_data(
                tweets_list, filters
            )
            
            # Display filter summary
            filter_summary = st.session_state.filter_manager.get_filter_summary(filters)
            st.caption(f"🔍 **Filtres actifs**: {filter_summary}")
            st.caption(f"📊 **Tweets affichés**: {len(filtered_tweets)} sur {len(tweets_list)}")
            
            # Pagination
            page_size = 10
            total_pages = (len(filtered_tweets) + page_size - 1) // page_size
            
            if total_pages > 1:
                col_page1, col_page2, col_page3 = st.columns([1, 2, 1])
                with col_page2:
                    page = st.selectbox("📄 Page", range(1, total_pages + 1)) - 1
                start_idx = page * page_size
                end_idx = min(start_idx + page_size, len(filtered_tweets))
                page_tweets = filtered_tweets[start_idx:end_idx]
            else:
                page_tweets = filtered_tweets[:page_size]
            
            # Display tweets
            for i, tweet in enumerate(page_tweets):
                sentiment = tweet.get('sentiment', 'neutral')
                priority = tweet.get('priority', 'normal')
                is_urgent = tweet.get('is_urgent', False)
                
                # Determine CSS classes
                sentiment_class = f"sentiment-{sentiment}"
                if is_urgent:
                    sentiment_class += " sentiment-critical"
                
                # Create tags
                tags_html = ""
                if sentiment:
                    tags_html += f'<span class="tweet-tag sentiment-{sentiment}">Sentiment: {sentiment.title()}</span>'
                if tweet.get('category'):
                    tags_html += f'<span class="tweet-tag">Catégorie: {tweet.get("category")}</span>'
                if priority:
                    priority_class = f"priority-{priority}" if priority != 'normal' else ""
                    tags_html += f'<span class="tweet-tag {priority_class}">Priorité: {priority.title()}</span>'
                if is_urgent:
                    tags_html += '<span class="tweet-tag urgent">🚨 URGENT</span>'
                if tweet.get('needs_response'):
                    tags_html += '<span class="tweet-tag">💬 Réponse requise</span>'
                
                st.markdown(f"""
                <div class="tweet-card {sentiment_class}">
                    <div class="tweet-header">
                        <div class="tweet-author">@{tweet.get('author', 'Unknown')}</div>
                        <div class="tweet-date">{tweet.get('date', '')}</div>
                    </div>
                    <div class="tweet-text">{tweet.get('text', '')}</div>
                    <div class="tweet-tags">
                        {tags_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        else:
            st.warning("⚠️ **Aucun tweet trouvé** avec les filtres sélectionnés")
    
    with col2:
        st.markdown("### 📊 Statistiques")
        
        # Get KPIs
        with st.spinner("🔄 Chargement des statistiques..."):
        kpi_data = get_kpis(batch_id, "analyste")
        
        if kpi_data:
            kpis = kpi_data.get('kpis', {})
            
            # Quick stats
            total_tweets = kpis.get('total_tweets', 0)
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-value">{total_tweets:,}</div>
                <div class="stats-label">Total Tweets</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Sentiment breakdown
            sentiment_pct = kpis.get('sentiment_percentages', {})
            for sentiment, pct in sentiment_pct.items():
                st.markdown(f"""
                <div class="stats-card">
                    <div class="stats-value">{pct:.1f}%</div>
                    <div class="stats-label">{sentiment.title()}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.divider()
            
            # Advanced Charts
            if tweets_data and tweets_data.get('tweets'):
                tweets_list = tweets_data['tweets']
                
                # Sentiment Timeline
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<div class="chart-title">📈 Évolution Temporelle</div>', unsafe_allow_html=True)
                timeline_chart = create_sentiment_timeline(tweets_list)
                st.plotly_chart(timeline_chart, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Category Sunburst
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<div class="chart-title">☀️ Distribution Hiérarchique</div>', unsafe_allow_html=True)
                sunburst_chart = create_category_sunburst(tweets_list)
                st.plotly_chart(sunburst_chart, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Word Cloud Data
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<div class="chart-title">☁️ Mots les Plus Fréquents</div>', unsafe_allow_html=True)
                word_data = create_word_cloud_data(tweets_list)
                if word_data:
                    # Create a simple bar chart for word frequency
                    words_df = pd.DataFrame(list(word_data.items()), columns=['Mot', 'Fréquence'])
                    words_df = words_df.head(20)  # Top 20 words
                    
                    fig = px.bar(
                        words_df, 
                        x='Fréquence', 
                        y='Mot', 
                        orientation='h',
                        title="Top 20 Mots les Plus Fréquents",
                        color='Fréquence',
                        color_continuous_scale='Reds'
                    )
                    fig.update_layout(
                        height=400,
                        font={'family': "Inter", 'size': 12},
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Données de mots non disponibles")
                st.markdown('</div>', unsafe_allow_html=True)
        
        else:
            st.error("❌ **Impossible de récupérer les statistiques**")


if __name__ == "__main__":
    main()