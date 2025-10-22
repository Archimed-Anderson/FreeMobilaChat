"""
Page de Classification LLM - FreeMobilaChat
==========================================

Page dédiée à l'affichage et à l'analyse des résultats de classification LLM.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from pathlib import Path
from datetime import datetime
import sys
import os

# Ajout du chemin pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend', 'app'))

# Configuration de la page
st.set_page_config(
    page_title="Classification LLM - FreeMobilaChat",
    page_icon=":brain:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #CC0000 0%, #8B0000 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #CC0000;
        margin-bottom: 1rem;
    }
    
    .classification-example {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 3px solid #CC0000;
        margin: 0.5rem 0;
    }
    
    .reclamation-high {
        border-left-color: #dc3545 !important;
    }
    
    .reclamation-medium {
        border-left-color: #ffc107 !important;
    }
    
    .reclamation-low {
        border-left-color: #28a745 !important;
    }
</style>
""", unsafe_allow_html=True)

def load_classification_results():
    """Charge les résultats de classification depuis le fichier CSV"""
    try:
        csv_path = Path("backend/data/intelligent_training/dataset_classified_enriched.csv")
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            return df
        else:
            st.error(f"Fichier de résultats non trouvé: {csv_path}")
            return None
    except Exception as e:
        st.error(f"Erreur lors du chargement: {e}")
        return None

def load_analysis_report():
    """Charge le rapport d'analyse"""
    try:
        report_path = Path("backend/data/intelligent_training/rapport_analyse_intelligente.md")
        if report_path.exists():
            with open(report_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return None
    except Exception as e:
        st.error(f"Erreur lors du chargement du rapport: {e}")
        return None

def create_classification_metrics(df):
    """Crée les métriques de classification"""
    total_tweets = len(df)
    reclamations = len(df[df['is_reclamation'] == 'OUI'])
    reclamation_rate = (reclamations / total_tweets * 100) if total_tweets > 0 else 0
    
    # Distribution des thèmes
    theme_dist = df['theme'].value_counts()
    
    # Distribution des sentiments
    sentiment_dist = df['sentiment'].value_counts()
    
    # Distribution des urgences
    urgence_dist = df['urgence'].value_counts()
    
    # Confiance moyenne
    avg_confidence = df['confidence'].mean()
    
    return {
        'total_tweets': total_tweets,
        'reclamations': reclamations,
        'reclamation_rate': reclamation_rate,
        'theme_dist': theme_dist,
        'sentiment_dist': sentiment_dist,
        'urgence_dist': urgence_dist,
        'avg_confidence': avg_confidence
    }

def render_classification_dashboard(df, metrics):
    """Affiche le tableau de bord de classification"""
    
    # En-tête principal
    st.markdown("""
    <div class="main-header">
        <h1>🧠 Classification LLM - FreeMobilaChat</h1>
        <p>Analyse intelligente des tweets Free Mobile avec Intelligence Artificielle</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Tweets",
            value=f"{metrics['total_tweets']:,}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="Réclamations",
            value=f"{metrics['reclamations']:,}",
            delta=f"{metrics['reclamation_rate']:.1f}%"
        )
    
    with col3:
        st.metric(
            label="Confiance Moyenne",
            value=f"{metrics['avg_confidence']:.2f}",
            delta=None
        )
    
    with col4:
        st.metric(
            label="Mode Classification",
            value="Fallback",
            delta="Règles automatiques"
        )
    
    st.markdown("---")
    
    # Graphiques de distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Distribution des Thèmes")
        fig_theme = px.pie(
            values=metrics['theme_dist'].values,
            names=metrics['theme_dist'].index,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_theme.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_theme, use_container_width=True)
    
    with col2:
        st.subheader("😊 Distribution des Sentiments")
        fig_sentiment = px.bar(
            x=metrics['sentiment_dist'].index,
            y=metrics['sentiment_dist'].values,
            color=metrics['sentiment_dist'].index,
            color_discrete_map={
                'POSITIF': '#28a745',
                'NEUTRE': '#6c757d',
                'NEGATIF': '#dc3545'
            }
        )
        fig_sentiment.update_layout(showlegend=False, xaxis_title="Sentiment", yaxis_title="Nombre")
        st.plotly_chart(fig_sentiment, use_container_width=True)
    
    # Graphique des urgences
    st.subheader("⚠️ Distribution des Niveaux d'Urgence")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig_urgence = px.bar(
            x=metrics['urgence_dist'].index,
            y=metrics['urgence_dist'].values,
            color=metrics['urgence_dist'].index,
            color_discrete_map={
                'CRITIQUE': '#dc3545',
                'ELEVEE': '#fd7e14',
                'MOYENNE': '#ffc107',
                'FAIBLE': '#28a745'
            }
        )
        fig_urgence.update_layout(showlegend=False, xaxis_title="Niveau d'Urgence", yaxis_title="Nombre")
        st.plotly_chart(fig_urgence, use_container_width=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4>📈 Statistiques Clés</h4>
            <p><strong>Réclamations:</strong> {:.1f}%</p>
            <p><strong>Sentiment Négatif:</strong> {} tweets</p>
            <p><strong>Urgence Élevée:</strong> {} tweets</p>
            <p><strong>Confiance Moyenne:</strong> {:.2f}</p>
        </div>
        """.format(
            metrics['reclamation_rate'],
            metrics['sentiment_dist'].get('NEGATIF', 0),
            metrics['urgence_dist'].get('ELEVEE', 0) + metrics['urgence_dist'].get('CRITIQUE', 0),
            metrics['avg_confidence']
        ), unsafe_allow_html=True)

def render_classification_examples(df):
    """Affiche des exemples de classification"""
    st.subheader("🔍 Exemples de Classification")
    
    # Filtres
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_theme = st.selectbox(
            "Filtrer par thème:",
            ["Tous"] + list(df['theme'].unique())
        )
    
    with col2:
        selected_sentiment = st.selectbox(
            "Filtrer par sentiment:",
            ["Tous"] + list(df['sentiment'].unique())
        )
    
    with col3:
        selected_reclamation = st.selectbox(
            "Type de tweet:",
            ["Tous", "Réclamations", "Informatifs"]
        )
    
    # Application des filtres
    filtered_df = df.copy()
    
    if selected_theme != "Tous":
        filtered_df = filtered_df[filtered_df['theme'] == selected_theme]
    
    if selected_sentiment != "Tous":
        filtered_df = filtered_df[filtered_df['sentiment'] == selected_sentiment]
    
    if selected_reclamation == "Réclamations":
        filtered_df = filtered_df[filtered_df['is_reclamation'] == 'OUI']
    elif selected_reclamation == "Informatifs":
        filtered_df = filtered_df[filtered_df['is_reclamation'] == 'NON']
    
    # Affichage des exemples
    st.write(f"**{len(filtered_df)} tweets trouvés**")
    
    for idx, row in filtered_df.head(10).iterrows():
        # Déterminer la classe CSS selon l'urgence
        urgency_class = ""
        if row['urgence'] == 'CRITIQUE':
            urgency_class = "reclamation-high"
        elif row['urgence'] == 'ELEVEE':
            urgency_class = "reclamation-medium"
        else:
            urgency_class = "reclamation-low"
        
        st.markdown(f"""
        <div class="classification-example {urgency_class}">
            <h5>📝 Tweet #{row['tweet_id']}</h5>
            <p><strong>Texte:</strong> {row['text_clean'][:200]}{'...' if len(row['text_clean']) > 200 else ''}</p>
            <div style="display: flex; gap: 1rem; margin-top: 0.5rem;">
                <span><strong>Réclamation:</strong> {row['is_reclamation']}</span>
                <span><strong>Thème:</strong> {row['theme']}</span>
                <span><strong>Sentiment:</strong> {row['sentiment']}</span>
                <span><strong>Urgence:</strong> {row['urgence']}</span>
                <span><strong>Confiance:</strong> {row['confidence']:.2f}</span>
            </div>
            <p style="margin-top: 0.5rem; font-style: italic;"><strong>Justification:</strong> {row['justification']}</p>
        </div>
        """, unsafe_allow_html=True)

def render_data_table(df):
    """Affiche le tableau de données complet"""
    st.subheader("📋 Tableau de Données Complet")
    
    # Options d'affichage
    col1, col2 = st.columns(2)
    
    with col1:
        show_columns = st.multiselect(
            "Colonnes à afficher:",
            options=df.columns.tolist(),
            default=['tweet_id', 'text_clean', 'is_reclamation', 'theme', 'sentiment', 'urgence', 'confidence']
        )
    
    with col2:
        max_rows = st.slider("Nombre de lignes à afficher:", 10, len(df), 50)
    
    # Affichage du tableau
    display_df = df[show_columns].head(max_rows)
    st.dataframe(display_df, use_container_width=True)
    
    # Bouton de téléchargement
    csv_data = df.to_csv(index=False, encoding='utf-8')
    st.download_button(
        label="📥 Télécharger le dataset complet",
        data=csv_data,
        file_name=f"free_tweets_classified_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

def main():
    """Fonction principale"""
    
    # Chargement des données
    df = load_classification_results()
    
    if df is None:
        st.error("Impossible de charger les résultats de classification.")
        st.info("Exécutez d'abord le script d'entraînement: `python backend/train_simple_classifier.py`")
        return
    
    # Calcul des métriques
    metrics = create_classification_metrics(df)
    
    # Interface utilisateur
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🔍 Exemples", "📋 Données", "📄 Rapport"])
    
    with tab1:
        render_classification_dashboard(df, metrics)
    
    with tab2:
        render_classification_examples(df)
    
    with tab3:
        render_data_table(df)
    
    with tab4:
        st.subheader("📄 Rapport d'Analyse Complet")
        report_content = load_analysis_report()
        if report_content:
            st.markdown(report_content)
        else:
            st.error("Rapport d'analyse non trouvé.")
    
    # Sidebar avec informations
    with st.sidebar:
        st.header("ℹ️ Informations")
        st.info(f"""
        **Dataset analysé:** {len(df)} tweets
        
        **Réclamations détectées:** {metrics['reclamations']} ({metrics['reclamation_rate']:.1f}%)
        
        **Confiance moyenne:** {metrics['avg_confidence']:.2f}
        
        **Mode de classification:** Fallback (Règles automatiques)
        """)
        
        st.header("🔧 Actions")
        if st.button("🔄 Recharger les données"):
            st.rerun()
        
        if st.button("📊 Nouvelle analyse"):
            st.info("Utilisez le script d'entraînement pour une nouvelle analyse")

if __name__ == "__main__":
    main()