"""
Page de Classification LLM - FreeMobilaChat
===========================================

Interface Streamlit pour la classification intelligente des tweets Free
avec le nouveau moteur LLM multi-label.

Fonctionnalités:
    - Upload de fichiers CSV de tweets
    - Classification automatique multi-label
    - Visualisation des résultats par dimension
    - Export des résultats annotés
    - Statistiques et métriques en temps réel

Auteur: Archimed Anderson
Date: Octobre 2024
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
import json
import logging
from typing import List, Dict
from datetime import datetime

# Ajouter le chemin backend au sys.path
backend_path = Path(__file__).parent.parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.append(str(backend_path))

try:
    from app.services.tweet_classifier import TweetClassifier, ClassificationResult
    CLASSIFIER_AVAILABLE = True
except ImportError as e:
    st.error(f"Erreur d'import du classificateur: {e}")
    CLASSIFIER_AVAILABLE = False

# Configuration de la page
st.set_page_config(
    page_title="Classification LLM - FreeMobilaChat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Logger
logger = logging.getLogger(__name__)


def load_custom_css():
    """Charge le CSS personnalisé Free Mobile"""
    st.markdown("""
    <style>
    /* Theme Free Mobile - Rouge et Noir */
    :root {
        --free-red: #CC0000;
        --free-dark-red: #8B0000;
        --free-black: #1a1a1a;
        --free-light-gray: #f8f9fa;
        --free-border: #e0e0e0;
    }
    
    /* Header */
    .main-header {
        background: linear-gradient(135deg, var(--free-red) 0%, var(--free-dark-red) 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(204, 0, 0, 0.2);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.95;
    }
    
    /* Cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid var(--free-red);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .metric-card h3 {
        color: var(--free-black);
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
    }
    
    .metric-card p {
        color: #666;
        font-size: 0.9rem;
        margin: 0.5rem 0 0 0;
    }
    
    /* Upload Zone */
    .upload-container {
        background: var(--free-light-gray);
        border: 2px dashed var(--free-red);
        border-radius: 15px;
        padding: 3rem;
        text-align: center;
        margin: 2rem 0;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div {
        background-color: var(--free-red);
    }
    
    /* Buttons */
    .stButton > button {
        background: var(--free-red);
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: var(--free-dark-red);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(204, 0, 0, 0.3);
    }
    
    /* Tables */
    .dataframe {
        font-size: 0.9rem;
    }
    
    .dataframe th {
        background-color: var(--free-red) !important;
        color: white !important;
        font-weight: 600;
    }
    
    /* Info/Success/Warning boxes */
    .stAlert {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)


def render_header():
    """Affiche le header de la page"""
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Classification Intelligente LLM</h1>
        <p>Analyse multi-label automatisée des tweets Free avec intelligence artificielle</p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Affiche la sidebar avec configuration"""
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Sélection du modèle LLM
        model_options = ["gpt-4", "gpt-3.5-turbo", "claude-3-opus", "claude-3-sonnet", "fallback (sans LLM)"]
        selected_model = st.selectbox(
            "Modèle LLM",
            options=model_options,
            index=4,  # Par défaut fallback
            help="Sélectionnez le modèle LLM à utiliser pour la classification"
        )
        
        # API Key (si nécessaire)
        api_key = None
        if "fallback" not in selected_model:
            api_key = st.text_input(
                "Clé API",
                type="password",
                help="Entrez votre clé API OpenAI ou Anthropic"
            )
        
        # Options avancées
        with st.expander("🔧 Options Avancées"):
            temperature = st.slider(
                "Température",
                min_value=0.0,
                max_value=1.0,
                value=0.1,
                step=0.1,
                help="0 = déterministe, 1 = créatif"
            )
            
            max_tokens = st.number_input(
                "Max Tokens",
                min_value=100,
                max_value=500,
                value=300,
                help="Nombre maximum de tokens dans la réponse"
            )
            
            show_confidence = st.checkbox(
                "Afficher scores de confiance",
                value=True
            )
            
            filter_low_confidence = st.checkbox(
                "Filtrer faible confiance (< 0.7)",
                value=False
            )
        
        # Instructions
        st.markdown("---")
        st.markdown("### 📖 Instructions")
        st.markdown("""
        1. **Uploadez** un fichier CSV contenant une colonne `text` avec les tweets
        2. **Configurez** le modèle LLM (ou utilisez le fallback)
        3. **Lancez** la classification
        4. **Analysez** les résultats et exportez
        """)
        
        # Taxonomie
        with st.expander("📊 Taxonomie de Classification"):
            st.markdown("""
            **is_reclamation**: OUI | NON
            
            **theme**: FIBRE | MOBILE | TV | FACTURE | SAV | RESEAU | AUTRE
            
            **sentiment**: NEGATIF | NEUTRE | POSITIF
            
            **urgence**: FAIBLE | MOYENNE | ELEVEE | CRITIQUE
            
            **type_incident**: PANNE | LENTEUR | FACTURATION | PROCESSUS_SAV | INFO | AUTRE
            """)
        
        # Retourner la configuration
        return {
            "model": selected_model,
            "api_key": api_key,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "show_confidence": show_confidence,
            "filter_low_confidence": filter_low_confidence
        }


def load_and_validate_csv(uploaded_file) -> pd.DataFrame:
    """
    Charge et valide le fichier CSV.
    
    Args:
        uploaded_file: Fichier uploadé depuis Streamlit
        
    Returns:
        DataFrame validé
    """
    try:
        df = pd.read_csv(uploaded_file)
        
        # Vérifier la présence de la colonne 'text'
        if 'text' not in df.columns:
            st.error("❌ Le fichier doit contenir une colonne 'text' avec les tweets")
            return None
        
        # Nettoyer les valeurs nulles
        df = df.dropna(subset=['text'])
        df = df[df['text'].str.strip() != '']
        
        st.success(f"✅ Fichier chargé: {len(df)} tweets")
        
        return df
        
    except Exception as e:
        st.error(f"❌ Erreur de chargement: {e}")
        return None


def classify_tweets(
    df: pd.DataFrame,
    classifier: TweetClassifier,
    config: Dict
) -> pd.DataFrame:
    """
    Classifie les tweets du DataFrame.
    
    Args:
        df: DataFrame avec colonne 'text'
        classifier: Instance du classificateur
        config: Configuration utilisateur
        
    Returns:
        DataFrame avec classifications
    """
    tweets = df['text'].tolist()
    tweet_ids = df['tweet_id'].tolist() if 'tweet_id' in df.columns else None
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    results = []
    total = len(tweets)
    
    for i, (tweet, tweet_id) in enumerate(zip(tweets, tweet_ids or [None] * total)):
        try:
            # Classifier le tweet
            result = classifier.classify(tweet, tweet_id)
            results.append(result.dict())
            
            # Mettre à jour la progression
            progress = (i + 1) / total
            progress_bar.progress(progress)
            status_text.text(f"Classification: {i + 1}/{total} tweets ({progress:.1%})")
            
        except Exception as e:
            logger.error(f"Erreur tweet {i}: {e}")
            # Ajouter un résultat vide
            results.append({
                "is_reclamation": "NON",
                "theme": "AUTRE",
                "sentiment": "NEUTRE",
                "urgence": "FAIBLE",
                "type_incident": "AUTRE",
                "confidence": 0.0,
                "justification": f"Erreur: {str(e)}",
                "tweet_id": tweet_id
            })
    
    progress_bar.empty()
    status_text.empty()
    
    # Créer le DataFrame de résultats
    results_df = pd.DataFrame(results)
    
    # Fusionner avec le DataFrame original
    df_classified = pd.concat([df.reset_index(drop=True), results_df], axis=1)
    
    # Filtrer par confiance si demandé
    if config.get('filter_low_confidence', False):
        df_classified = df_classified[df_classified['confidence'] >= 0.7]
        st.info(f"Filtrage appliqué: {len(df_classified)} tweets avec confiance ≥ 0.7")
    
    return df_classified


def display_classification_metrics(df: pd.DataFrame):
    """
    Affiche les métriques de classification.
    
    Args:
        df: DataFrame avec classifications
    """
    st.markdown("### 📊 Métriques de Classification")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_reclamations = (df['is_reclamation'] == 'OUI').sum()
        pct_reclamations = (total_reclamations / len(df)) * 100
        st.markdown(f"""
        <div class="metric-card">
            <h3>{total_reclamations}</h3>
            <p>Réclamations ({pct_reclamations:.1f}%)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_confidence = df['confidence'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <h3>{avg_confidence:.2f}</h3>
            <p>Confiance Moyenne</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        negative_sentiment = (df['sentiment'] == 'NEGATIF').sum()
        pct_negative = (negative_sentiment / len(df)) * 100
        st.markdown(f"""
        <div class="metric-card">
            <h3>{negative_sentiment}</h3>
            <p>Sentiment Négatif ({pct_negative:.1f}%)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        critical_urgency = (df['urgence'] == 'CRITIQUE').sum()
        high_urgency = (df['urgence'] == 'ELEVEE').sum()
        urgent_total = critical_urgency + high_urgency
        st.markdown(f"""
        <div class="metric-card">
            <h3>{urgent_total}</h3>
            <p>Urgent/Critique</p>
        </div>
        """, unsafe_allow_html=True)


def display_visualizations(df: pd.DataFrame):
    """
    Affiche les visualisations des résultats.
    
    Args:
        df: DataFrame avec classifications
    """
    st.markdown("### 📈 Visualisations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribution des thèmes
        theme_counts = df['theme'].value_counts()
        fig_theme = px.bar(
            x=theme_counts.index,
            y=theme_counts.values,
            labels={'x': 'Thème', 'y': 'Nombre de tweets'},
            title="Distribution des Thèmes",
            color=theme_counts.values,
            color_continuous_scale=['#CC0000', '#8B0000']
        )
        fig_theme.update_layout(showlegend=False)
        st.plotly_chart(fig_theme, use_container_width=True)
        
        # Distribution des types d'incidents
        incident_counts = df['type_incident'].value_counts()
        fig_incident = px.pie(
            values=incident_counts.values,
            names=incident_counts.index,
            title="Types d'Incidents",
            color_discrete_sequence=px.colors.sequential.Reds_r
        )
        st.plotly_chart(fig_incident, use_container_width=True)
    
    with col2:
        # Distribution sentiment
        sentiment_counts = df['sentiment'].value_counts()
        colors = {'NEGATIF': '#CC0000', 'NEUTRE': '#666666', 'POSITIF': '#28a745'}
        fig_sentiment = px.bar(
            x=sentiment_counts.index,
            y=sentiment_counts.values,
            labels={'x': 'Sentiment', 'y': 'Nombre de tweets'},
            title="Distribution des Sentiments",
            color=sentiment_counts.index,
            color_discrete_map=colors
        )
        st.plotly_chart(fig_sentiment, use_container_width=True)
        
        # Distribution urgence
        urgence_counts = df['urgence'].value_counts()
        fig_urgence = px.funnel(
            y=urgence_counts.index,
            x=urgence_counts.values,
            title="Niveaux d'Urgence",
            color=urgence_counts.index,
            color_discrete_sequence=px.colors.sequential.Reds
        )
        st.plotly_chart(fig_urgence, use_container_width=True)
    
    # Distribution de confiance
    st.markdown("#### Distribution des Scores de Confiance")
    fig_conf = px.histogram(
        df,
        x='confidence',
        nbins=20,
        title="Distribution des Scores de Confiance",
        labels={'confidence': 'Score de Confiance', 'count': 'Fréquence'},
        color_discrete_sequence=['#CC0000']
    )
    fig_conf.add_vline(
        x=df['confidence'].mean(),
        line_dash="dash",
        line_color="black",
        annotation_text=f"Moyenne: {df['confidence'].mean():.2f}"
    )
    st.plotly_chart(fig_conf, use_container_width=True)


def display_sample_classifications(df: pd.DataFrame, n_samples: int = 10):
    """
    Affiche un échantillon de classifications.
    
    Args:
        df: DataFrame avec classifications
        n_samples: Nombre d'échantillons à afficher
    """
    st.markdown("### 🔍 Échantillon de Classifications")
    
    # Filtrer les colonnes à afficher
    display_cols = [
        'text',
        'is_reclamation',
        'theme',
        'sentiment',
        'urgence',
        'type_incident',
        'confidence',
        'justification'
    ]
    
    # Prendre un échantillon aléatoire
    sample_df = df[display_cols].sample(min(n_samples, len(df)))
    
    # Styler le DataFrame
    def color_confidence(val):
        if val >= 0.8:
            color = '#28a745'  # Vert
        elif val >= 0.6:
            color = '#ffc107'  # Jaune
        else:
            color = '#CC0000'  # Rouge
        return f'background-color: {color}; color: white'
    
    styled_df = sample_df.style.applymap(
        color_confidence,
        subset=['confidence']
    )
    
    st.dataframe(styled_df, use_container_width=True, height=400)


def export_results(df: pd.DataFrame):
    """
    Permet l'export des résultats.
    
    Args:
        df: DataFrame avec classifications
    """
    st.markdown("### 💾 Export des Résultats")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Export CSV
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger CSV",
            data=csv_data,
            file_name=f"classifications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col2:
        # Export JSON
        json_data = df.to_json(orient='records', force_ascii=False, indent=2)
        st.download_button(
            label="📥 Télécharger JSON",
            data=json_data,
            file_name=f"classifications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    with col3:
        # Export Excel
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Classifications')
        excel_data = output.getvalue()
        st.download_button(
            label="📥 Télécharger Excel",
            data=excel_data,
            file_name=f"classifications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


def main():
    """Fonction principale"""
    
    # Charger le CSS
    load_custom_css()
    
    # Afficher le header
    render_header()
    
    # Vérifier que le classificateur est disponible
    if not CLASSIFIER_AVAILABLE:
        st.error("❌ Le module de classification n'est pas disponible. Vérifiez l'installation.")
        return
    
    # Sidebar avec configuration
    config = render_sidebar()
    
    # Zone d'upload
    st.markdown('<div class="upload-container">', unsafe_allow_html=True)
    st.markdown("### 📤 Upload de Fichier CSV")
    st.markdown("Uploadez un fichier CSV contenant une colonne **`text`** avec les tweets à classifier")
    
    uploaded_file = st.file_uploader(
        "Choisir un fichier CSV",
        type=['csv'],
        help="Le fichier doit contenir au minimum une colonne 'text' avec les tweets"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    if uploaded_file is not None:
        # Charger et valider le CSV
        df = load_and_validate_csv(uploaded_file)
        
        if df is not None:
            # Afficher un aperçu
            with st.expander("👀 Aperçu des Données", expanded=False):
                st.dataframe(df.head(10), use_container_width=True)
            
            # Bouton de lancement de classification
            if st.button("🚀 Lancer la Classification", type="primary"):
                with st.spinner("⏳ Classification en cours..."):
                    try:
                        # Initialiser le classificateur
                        classifier = TweetClassifier(
                            model_name=config['model'],
                            api_key=config.get('api_key'),
                            temperature=config['temperature'],
                            max_tokens=config['max_tokens']
                        )
                        
                        # Classifier les tweets
                        df_classified = classify_tweets(df, classifier, config)
                        
                        # Sauvegarder dans session state
                        st.session_state['df_classified'] = df_classified
                        
                        st.success(f"✅ Classification terminée: {len(df_classified)} tweets classifiés")
                        
                    except Exception as e:
                        st.error(f"❌ Erreur lors de la classification: {e}")
                        logger.error(f"Erreur classification: {e}", exc_info=True)
            
            # Afficher les résultats si disponibles
            if 'df_classified' in st.session_state:
                df_classified = st.session_state['df_classified']
                
                # Métriques
                display_classification_metrics(df_classified)
                
                # Visualisations
                display_visualizations(df_classified)
                
                # Échantillon
                display_sample_classifications(df_classified)
                
                # Export
                export_results(df_classified)


if __name__ == "__main__":
    main()

