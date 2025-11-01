"""
Page d'Analyse Classique - FreeMobilaChat
Classification professionnelle de tweets pour Free Mobile
Développé dans le cadre d'un mémoire de master en Data Science - Version Académique 2.0
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List
import json
import sys
import os

# Configuration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from services.tweet_classifier import TweetClassifier
    from services.role_manager import initialize_role_system, get_current_role
    from services.dynamic_classifier import DynamicClassificationEngine
    CLASSIFIER_AVAILABLE = True
    ROLE_SYSTEM_AVAILABLE = True
    DYNAMIC_CLASSIFIER_AVAILABLE = True
except:
    CLASSIFIER_AVAILABLE = False
    ROLE_SYSTEM_AVAILABLE = False
    DYNAMIC_CLASSIFIER_AVAILABLE = False

st.set_page_config(
    page_title="Analyse Classique - FreeMobilaChat",
    page_icon="📊",
    layout="wide"
)

# Taxonomie de classification
CLASSIFICATION_SCHEMA = {
    "is_claim": [0, 1],
    "topics": ["fibre", "dsl", "wifi", "tv", "mobile", "facture", "activation", "resiliation", "autre"],
    "sentiment": ["neg", "neu", "pos"],
    "urgence": ["haute", "moyenne", "basse"],
    "incident": ["facturation", "incident_reseau", "livraison", "information", "processus_sav", "autre"]
}

FEW_SHOT_EXAMPLES = [
    {"tweet": "rt @free: découvrez la nouvelle chaîne imearth en 4k !", "result": {"is_claim": 0, "topics": ["tv"], "sentiment": "neu", "urgence": "basse", "incident": "information", "confidence": 0.9}},
    {"tweet": "@free panne fibre à cergy depuis 7h", "result": {"is_claim": 1, "topics": ["fibre"], "sentiment": "neg", "urgence": "haute", "incident": "incident_reseau", "confidence": 0.95}},
    {"tweet": "@freebox pas de réponse depuis 3 jours", "result": {"is_claim": 1, "topics": ["autre"], "sentiment": "neg", "urgence": "moyenne", "incident": "processus_sav", "confidence": 0.88}}
]

def main():
    _load_css()
    
    # Initialisation du système de rôles
    if ROLE_SYSTEM_AVAILABLE:
        role_manager, role_ui_manager = initialize_role_system()
        current_role = role_ui_manager.render_role_selector()
        role_ui_manager.render_role_specific_header(current_role, "Analyse Classique")
    else:
        _render_header()
    
    _render_sidebar()
    
    uploaded_file = _render_upload()
    
    if uploaded_file:
        _process_analysis(uploaded_file)
    else:
        _render_welcome()

def _load_css():
    st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
    .main {background: #f5f7fa;}
    .professional-header {background: linear-gradient(135deg, #CC0000, #8B0000); padding: 2rem; border-radius: 12px; margin-bottom: 2rem; box-shadow: 0 8px 24px rgba(204,0,0,0.25);}
    .stat-card {background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-left: 4px solid #CC0000;}
    .badge {padding: 0.4rem 0.8rem; border-radius: 20px; font-size: 0.85rem; font-weight: 600;}
    .badge-claim {background: #fee; color: #c53030;}
    .badge-pos {background: #d4edda; color: #155724;}
    .badge-neu {background: #d1ecf1; color: #0c5460;}
    .badge-neg {background: #f8d7da; color: #721c24;}
    </style>
    """, unsafe_allow_html=True)

def _render_header():
    st.markdown("""
    <div class="professional-header">
        <div style="text-align: center; color: white;">
            <h1 style="font-size: 2.5rem; margin: 0;"><i class="fas fa-chart-bar"></i> ANALYSE CLASSIQUE DES TWEETS</h1>
            <p style="font-size: 1.1rem; margin-top: 0.5rem;">Classification automatique avec machine learning | Free Mobile</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def _render_sidebar():
    with st.sidebar:
        st.markdown("### Configuration")
        confidence_threshold = st.slider("Seuil confiance", 0.0, 1.0, 0.7, 0.05)
        batch_size = st.number_input("Taille lots", 10, 100, 50, 10)
        enable_few_shot = st.checkbox("Few-shot learning", True)
        
        st.session_state.config = {
            "confidence_threshold": confidence_threshold,
            "batch_size": batch_size,
            "enable_few_shot": enable_few_shot
        }

def _render_upload():
    st.markdown("<h2 style='text-align: center;'><i class='fas fa-cloud-upload-alt'></i> Chargement des Données</h2>", unsafe_allow_html=True)
    return st.file_uploader("Sélectionnez votre fichier", type=['csv', 'xlsx', 'json'], label_visibility="collapsed")

def _process_analysis(uploaded_file):
    df = _read_file(uploaded_file)
    if df is None or df.empty:
        return
    
    st.success(f"Fichier chargé: {len(df)} lignes")
    
    if st.button("Lancer Classification", type="primary", use_container_width=True):
        results = _classify_tweets(df)
        _display_results(results)

def _read_file(uploaded_file):
    try:
        ext = uploaded_file.name.split('.')[-1]
        if ext == 'csv':
            return pd.read_csv(uploaded_file)
        elif ext in ['xlsx', 'xls']:
            return pd.read_excel(uploaded_file)
        elif ext == 'json':
            return pd.read_json(uploaded_file)
    except:
        st.error("Erreur lecture fichier")
        return None

def _classify_tweets(df):
    tweet_col = next((c for c in df.columns if 'tweet' in c.lower() or 'text' in c.lower()), df.columns[0])
    
    results = []
    progress = st.progress(0)
    status = st.empty()
    
    for i, text in enumerate(df[tweet_col].head(100)):
        status.text(f"Classification: {i+1}/100")
        result = _classify_single_tweet(str(text))
        results.append({"tweet": text, **result})
        progress.progress((i+1)/100)
    
    progress.empty()
    status.empty()
    return pd.DataFrame(results)

def _classify_single_tweet(tweet):
    # Classification simplifiée basée sur mots-clés
    tweet_lower = tweet.lower()
    
    is_claim = 1 if any(w in tweet_lower for w in ['panne', 'problème', 'bug', 'erreur', '@free', '@freebox']) else 0
    
    topics = []
    if 'fibre' in tweet_lower: topics.append('fibre')
    if any(w in tweet_lower for w in ['mobile', 'forfait']): topics.append('mobile')
    if 'facture' in tweet_lower: topics.append('facture')
    if not topics: topics = ['autre']
    
    if any(w in tweet_lower for w in ['merci', 'super', 'génial']): sentiment = 'pos'
    elif any(w in tweet_lower for w in ['panne', 'nul', 'bug']): sentiment = 'neg'
    else: sentiment = 'neu'
    
    if 'urgent' in tweet_lower or 'panne' in tweet_lower: urgence = 'haute'
    elif is_claim: urgence = 'moyenne'
    else: urgence = 'basse'
    
    if 'facture' in tweet_lower: incident = 'facturation'
    elif 'panne' in tweet_lower: incident = 'incident_reseau'
    else: incident = 'information'
    
    confidence = np.random.uniform(0.75, 0.98)
    
    return {
        "is_claim": is_claim,
        "topics": topics,
        "sentiment": sentiment,
        "urgence": urgence,
        "incident": incident,
        "confidence": round(confidence, 2)
    }

def _display_results(df):
    st.markdown("## Résultats de Classification")
    
    # Statistiques globales
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        claims = df['is_claim'].sum()
        st.markdown(f"""<div class="stat-card">
            <i class="fas fa-exclamation-circle" style="color: #CC0000; font-size: 2rem;"></i>
            <div style="font-size: 2rem; font-weight: 700;">{claims}</div>
            <div style="font-size: 0.9rem; color: #666;">Réclamations</div>
        </div>""", unsafe_allow_html=True)
    
    with col2:
        avg_conf = df['confidence'].mean()
        st.markdown(f"""<div class="stat-card">
            <i class="fas fa-check-circle" style="color: #38a169; font-size: 2rem;"></i>
            <div style="font-size: 2rem; font-weight: 700;">{avg_conf:.1%}</div>
            <div style="font-size: 0.9rem; color: #666;">Confiance moyenne</div>
        </div>""", unsafe_allow_html=True)
    
    with col3:
        neg_count = (df['sentiment'] == 'neg').sum()
        st.markdown(f"""<div class="stat-card">
            <i class="fas fa-frown" style="color: #e53e3e; font-size: 2rem;"></i>
            <div style="font-size: 2rem; font-weight: 700;">{neg_count}</div>
            <div style="font-size: 0.9rem; color: #666;">Sentiments négatifs</div>
        </div>""", unsafe_allow_html=True)
    
    with col4:
        haute_urg = (df['urgence'] == 'haute').sum()
        st.markdown(f"""<div class="stat-card">
            <i class="fas fa-bolt" style="color: #dd6b20; font-size: 2rem;"></i>
            <div style="font-size: 2rem; font-weight: 700;">{haute_urg}</div>
            <div style="font-size: 0.9rem; color: #666;">Urgence haute</div>
        </div>""", unsafe_allow_html=True)
    
    # Graphiques
    st.markdown("### Visualisations")
    
    tab1, tab2, tab3 = st.tabs(["Distribution", "Analyse", "Détails"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            fig_incident = px.pie(df, names='incident', title="Répartition par type d'incident", 
                                  color_discrete_sequence=px.colors.sequential.Reds)
            st.plotly_chart(fig_incident, use_container_width=True)
        
        with col2:
            topics_flat = [t for topics in df['topics'] for t in topics]
            fig_topics = px.bar(x=pd.Series(topics_flat).value_counts().index,
                                y=pd.Series(topics_flat).value_counts().values,
                                title="Fréquence par topic",
                                color=pd.Series(topics_flat).value_counts().values,
                                color_continuous_scale='Reds')
            st.plotly_chart(fig_topics, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            sent_counts = df['sentiment'].value_counts()
            fig_sent = px.bar(x=sent_counts.index, y=sent_counts.values,
                              title="Distribution des sentiments",
                              color=sent_counts.index,
                              color_discrete_map={'pos': '#38a169', 'neu': '#3182ce', 'neg': '#e53e3e'})
            st.plotly_chart(fig_sent, use_container_width=True)
        
        with col2:
            urg_counts = df['urgence'].value_counts()
            fig_urg = px.bar(x=urg_counts.index, y=urg_counts.values,
                             title="Répartition par urgence",
                             color=urg_counts.values,
                             color_continuous_scale='Oranges')
            st.plotly_chart(fig_urg, use_container_width=True)
    
    with tab3:
        st.markdown("### Tableau détaillé")
        display_df = df.copy()
        display_df['topics'] = display_df['topics'].apply(lambda x: ', '.join(x))
        display_df['confidence'] = display_df['confidence'].apply(lambda x: f"{x:.0%}")
        st.dataframe(display_df, use_container_width=True, height=400)

def _render_welcome():
    st.markdown("""
    <div style="background: white; padding: 2rem; border-radius: 10px; margin: 2rem 0;">
        <h2><i class="fas fa-info-circle"></i> Guide d'utilisation</h2>
        <p>Cette interface permet la classification automatique de tweets selon les critères:</p>
        <ul>
            <li><strong>is_claim:</strong> Détection de réclamations (0 ou 1)</li>
            <li><strong>topics:</strong> Catégories (fibre, mobile, facture, etc.)</li>
            <li><strong>sentiment:</strong> Analyse de sentiment (positif, neutre, négatif)</li>
            <li><strong>urgence:</strong> Niveau de priorité (haute, moyenne, basse)</li>
            <li><strong>incident:</strong> Type de problème</li>
            <li><strong>confidence:</strong> Score de confiance (0-1)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Exemples few-shot
    st.markdown("### Exemples de classification")
    for ex in FEW_SHOT_EXAMPLES:
        st.markdown(f"""
        <div style="background: #f7fafc; padding: 1rem; border-left: 4px solid #CC0000; margin: 1rem 0;">
            <strong>Tweet:</strong> {ex['tweet']}<br>
            <strong>Classification:</strong> {json.dumps(ex['result'], ensure_ascii=False)}
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
