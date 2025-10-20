"""
Page de Résultats d'Analyse
Interface de visualisation des résultats d'analyse des données Twitter
Développé dans le cadre d'un mémoire de master en Data Science
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta

# Configuration
st.set_page_config(
    page_title="Resultat KPI - FreeMobilaChat",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
/* Titre de page stylé */
.page-title {
    font-size: 3.5rem;
    font-weight: 900;
    color: #CC0000;
    text-align: center;
    margin: 2rem 0;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    letter-spacing: -1px;
}

/* Cards KPI */
.kpi-card {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    border-left: 4px solid #CC0000;
    transition: all 0.3s;
}

.kpi-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(204, 0, 0, 0.2);
}

/* Section headers */
.section-header {
    font-size: 1.8rem;
    font-weight: 700;
    color: #CC0000;
    margin: 2rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 3px solid #CC0000;
}
</style>
""", unsafe_allow_html=True)

def main():
    """Fonction principale d'affichage des résultats d'analyse"""
    
    # Header stylé avec logo
    st.markdown("""
    <div style="background: linear-gradient(135deg, #CC0000 0%, #8B0000 100%); padding: 3rem 2rem; text-align: center; color: white; border-radius: 15px; margin-bottom: 2rem; box-shadow: 0 10px 30px rgba(204, 0, 0, 0.3);">
        <div style="display: flex; justify-content: center; margin-bottom: 2rem;">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="width: 70px; height: 70px; background: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                    <span style="font-size: 2.2rem; font-weight: 900; color: #CC0000;">FM</span>
                </div>
                <div style="display: flex; flex-direction: column; text-align: left;">
                    <span style="font-size: 2rem; font-weight: 900; color: white; letter-spacing: -1px; line-height: 1;">FreeMobila</span>
                    <span style="font-size: 1.5rem; font-weight: 700; color: rgba(255,255,255,0.95); letter-spacing: 1px; line-height: 1;">CHAT</span>
                </div>
            </div>
        </div>
        <h1 style="font-size: 3.5rem; font-weight: 900; margin-bottom: 1rem; color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); letter-spacing: -1px;">DASHBOARD DES RESULTATS</h1>
        <p style="font-size: 1.4rem; color: white; opacity: 0.95; font-weight: 500;">Visualisations • Classifications • Scores d'Analyse IA</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Vérifier si des données analysées existent
    if 'analyzed_data' not in st.session_state or st.session_state.analyzed_data is None:
        st.warning("Aucune donnee analysee disponible. Veuillez d'abord uploader et analyser un fichier.")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Aller a la page d'analyse", type="primary", use_container_width=True):
                st.switch_page("pages/analyse_intelligente.py")
        return
    
    data = st.session_state.analyzed_data
    
    # Métriques principales
    render_main_metrics(data)
    
    # Classifications et Scores
    st.markdown("---")
    render_classifications(data)
    
    # Visualisations KPI
    st.markdown("---")
    render_visualizations(data)
    
    # Tableau détaillé
    st.markdown("---")
    render_detailed_table(data)
    
    # Actions rapides
    st.markdown("---")
    render_quick_actions()

def render_main_metrics(data):
    """Affiche les métriques principales"""
    
    st.markdown("<h2 class='section-header'>Métriques Principales</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Total Tweets",
            f"{len(data):,}",
            delta="Nouveau fichier",
            delta_color="normal"
        )
    
    with col2:
        avg_score = data['sentiment_score'].mean()
        st.metric(
            "Score Moyen IA",
            f"{avg_score:.1%}",
            delta=f"+{(avg_score - 0.85):.1%}",
            delta_color="normal"
        )
    
    with col3:
        positive_pct = (data['sentiment'] == 'Positif').sum() / len(data)
        st.metric(
            "Sentiment Positif",
            f"{positive_pct:.1%}",
            delta=f"+{positive_pct - 0.45:.1%}",
            delta_color="normal"
        )
    
    with col4:
        high_priority = (data['priority'] == 'Haute').sum()
        st.metric(
            "Priorité Haute",
            high_priority,
            delta=f"{high_priority/len(data):.1%}",
            delta_color="inverse"
        )
    
    with col5:
        unique_categories = data['category'].nunique()
        st.metric(
            "Catégories",
            unique_categories,
            delta="Détectées",
            delta_color="off"
        )

def render_classifications(data):
    """Affiche les classifications détaillées"""
    
    st.markdown("<h2 class='section-header'>Classifications & Scores</h2>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Sentiments", "Catégories", "Priorités"])
    
    with tab1:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### Distribution des Sentiments")
            sentiment_counts = data['sentiment'].value_counts()
            
            for sentiment, count in sentiment_counts.items():
                percentage = (count / len(data)) * 100
                emoji = "Positif" if sentiment == "Positif" else "Negatif" if sentiment == "Negatif" else "Neutre"
                st.markdown(f"""
                <div class="kpi-card" style="margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 1.2rem;"><strong>{emoji} {sentiment}</strong></span>
                        <span style="font-size: 1.5rem; color: #CC0000; font-weight: 700;">{count}</span>
                    </div>
                    <div style="background: #f0f0f0; height: 8px; border-radius: 4px; margin-top: 0.5rem;">
                        <div style="background: #CC0000; height: 100%; width: {percentage}%; border-radius: 4px;"></div>
                    </div>
                    <div style="text-align: right; margin-top: 0.3rem; color: #666;">{percentage:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            fig = px.pie(
                values=sentiment_counts.values,
                names=sentiment_counts.index,
                title="Répartition des Sentiments",
                color=sentiment_counts.index,
                color_discrete_map={'Positif': '#4ade80', 'Negatif': '#ef4444', 'Neutre': '#60a5fa'},
                hole=0.4
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### Distribution des Catégories")
            category_counts = data['category'].value_counts()
            
            for category, count in category_counts.items():
                percentage = (count / len(data)) * 100
                st.markdown(f"""
                <div class="kpi-card" style="margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 1.1rem;"><strong>{category}</strong></span>
                        <span style="font-size: 1.4rem; color: #CC0000; font-weight: 700;">{count}</span>
                    </div>
                    <div style="background: #f0f0f0; height: 6px; border-radius: 3px; margin-top: 0.5rem;">
                        <div style="background: linear-gradient(90deg, #CC0000, #8B0000); height: 100%; width: {percentage}%; border-radius: 3px;"></div>
                    </div>
                    <div style="text-align: right; margin-top: 0.3rem; color: #666; font-size: 0.9rem;">{percentage:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            fig = px.bar(
                x=category_counts.index,
                y=category_counts.values,
                title="Nombre de Tweets par Catégorie",
                labels={'x': 'Catégorie', 'y': 'Nombre de Tweets'},
                color=category_counts.values,
                color_continuous_scale='Reds'
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### Distribution des Priorités")
            priority_counts = data['priority'].value_counts()
            priority_order = ['Haute', 'Moyenne', 'Basse']
            priority_counts = priority_counts.reindex(priority_order, fill_value=0)
            
            colors = {'Haute': '#ef4444', 'Moyenne': '#f97316', 'Basse': '#4ade80'}
            
            for priority, count in priority_counts.items():
                percentage = (count / len(data)) * 100 if len(data) > 0 else 0
                emoji = "Haute" if priority == "Haute" else "Moyenne" if priority == "Moyenne" else "Basse"
                st.markdown(f"""
                <div class="kpi-card" style="margin-bottom: 1rem; border-left-color: {colors[priority]};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 1.2rem;"><strong>{emoji} {priority}</strong></span>
                        <span style="font-size: 1.5rem; color: {colors[priority]}; font-weight: 700;">{count}</span>
                    </div>
                    <div style="background: #f0f0f0; height: 8px; border-radius: 4px; margin-top: 0.5rem;">
                        <div style="background: {colors[priority]}; height: 100%; width: {percentage}%; border-radius: 4px;"></div>
                    </div>
                    <div style="text-align: right; margin-top: 0.3rem; color: #666;">{percentage:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            fig = px.pie(
                values=priority_counts.values,
                names=priority_counts.index,
                title="Répartition par Priorité",
                color=priority_counts.index,
                color_discrete_map=colors,
                hole=0.4
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

def render_visualizations(data):
    """Affiche les visualisations KPI avancées"""
    
    st.markdown("<h2 class='section-header'>Visualisations Avancées</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Scores de sentiment
        st.markdown("### Distribution des Scores IA")
        fig = px.histogram(
            data,
            x='sentiment_score',
            nbins=20,
            title="Distribution des Scores de Confiance IA",
            labels={'sentiment_score': 'Score de Confiance', 'count': 'Nombre'},
            color_discrete_sequence=['#CC0000']
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Corrélation Sentiment/Score
        st.markdown("### Sentiment vs Score IA")
        fig = px.box(
            data,
            x='sentiment',
            y='sentiment_score',
            title="Scores IA par Sentiment",
            labels={'sentiment': 'Sentiment', 'sentiment_score': 'Score IA'},
            color='sentiment',
            color_discrete_map={'Positif': '#4ade80', 'Negatif': '#ef4444', 'Neutre': '#60a5fa'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Timeline
    st.markdown("### Evolution Temporelle")
    data_time = data.copy()
    data_time['hour'] = pd.to_datetime(data_time['date']).dt.hour
    hourly_sentiment = data_time.groupby(['hour', 'sentiment']).size().reset_index(name='count')
    
    fig = px.line(
        hourly_sentiment,
        x='hour',
        y='count',
        color='sentiment',
        title="Evolution des Sentiments par Heure",
        labels={'hour': 'Heure', 'count': 'Nombre de Tweets', 'sentiment': 'Sentiment'},
        color_discrete_map={'Positif': '#4ade80', 'Negatif': '#ef4444', 'Neutre': '#60a5fa'}
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def render_detailed_table(data):
    """Affiche le tableau détaillé des données"""
    
    st.markdown("<h2 class='section-header'>Tableau Détaillé des Analyses</h2>", unsafe_allow_html=True)
    
    # Filtres
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sentiment_filter = st.multiselect(
            "Filtrer par Sentiment",
            options=data['sentiment'].unique(),
            default=data['sentiment'].unique()
        )
    
    with col2:
        category_filter = st.multiselect(
            "Filtrer par Catégorie",
            options=data['category'].unique(),
            default=data['category'].unique()
        )
    
    with col3:
        priority_filter = st.multiselect(
            "Filtrer par Priorité",
            options=data['priority'].unique(),
            default=data['priority'].unique()
        )
    
    # Filtrage des données
    filtered_data = data[
        (data['sentiment'].isin(sentiment_filter)) &
        (data['category'].isin(category_filter)) &
        (data['priority'].isin(priority_filter))
    ]
    
    st.info(f"Affichage de {len(filtered_data)} tweets sur {len(data)} au total")
    
    # Affichage du tableau
    display_cols = ['text', 'sentiment', 'sentiment_score', 'category', 'priority', 'date']
    st.dataframe(
        filtered_data[display_cols].head(50),
        use_container_width=True,
        height=400
    )
    
    # Bouton d'export
    csv = filtered_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Télécharger les données (CSV)",
        data=csv,
        file_name=f"analyse_tweets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )

def render_quick_actions():
    """Affiche les actions rapides"""
    
    st.markdown("<h2 class='section-header'>Actions Rapides</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Nouvelle Analyse", use_container_width=True, type="primary"):
            st.session_state.analyzed_data = None
            st.session_state.file_info = None
            st.switch_page("pages/analyse_intelligente.py")
    
    with col2:
        if st.button("Actualiser Dashboard", use_container_width=True):
            st.rerun()
    
    with col3:
        if st.button("Paramètres", use_container_width=True):
            st.info("Page de parametres en cours de developpement")

if __name__ == "__main__":
    main()
