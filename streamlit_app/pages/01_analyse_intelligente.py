"""
Page d'Analyse Intelligente - FreeMobilaChat
Interface utilisateur pour l'upload et l'analyse de fichiers de données avec LLM
Développé dans le cadre d'un mémoire de master en Data Science
"""

import streamlit as st
import time
import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import hashlib
import os
import plotly.express as px
import plotly.graph_objects as go
import random
import re
import warnings
warnings.filterwarnings('ignore')

# Imports conditionnels pour éviter les erreurs
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

try:
    import nltk
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import IsolationForest
    from sklearn.metrics import silhouette_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    from langchain.llms import Ollama
    from langchain.prompts import PromptTemplate
    from langchain.chains import LLMChain
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Configuration
st.set_page_config(
    page_title="Analyse Intelligente - FreeMobilaChat",
    page_icon=":brain:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Logger
logger = logging.getLogger(__name__)

def main():
    """Page principale d'analyse intelligente"""
    
    # CSS personnalisé moderne
    _load_modern_css()
    
    # Header moderne
    _render_modern_header()
    
    # Sidebar avec configuration
    _render_sidebar_config()
    
    # Zone d'upload multiple
    uploaded_files = _render_multiple_upload_zone()
    
    if uploaded_files:
        # Analyse intelligente de tous les fichiers
        _handle_multiple_file_analysis(uploaded_files)
        return
    
    # Section des fonctionnalités
    _render_features_section()

def _load_modern_css():
    """Charge le CSS moderne pour la page"""
    st.markdown("""
    <style>
    /* Import Font Awesome */
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');
    
    /* Variables CSS */
    :root {
        --primary-color: #CC0000 !important;
        --secondary-color: #8B0000 !important;
        --accent-color: #FF6B6B !important;
        --text-color: #000000 !important;
        --text-light: #333333 !important;
        --bg-color: #f8f9fa !important;
        --card-bg: #ffffff !important;
        --border-radius: 12px !important;
        --shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        --shadow-hover: 0 8px 25px rgba(0, 0, 0, 0.15) !important;
    }
    
    /* Reset et base */
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px !important;
    }
    
    /* Header moderne */
    .modern-header {
        background: linear-gradient(135deg, #CC0000 0%, #8B0000 100%) !important;
        padding: 3rem 2rem !important;
        border-radius: 12px !important;
        margin-bottom: 2rem !important;
        color: white !important;
        text-align: center !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
    }
    
    .modern-header h1 {
        font-size: 3rem !important;
        font-weight: 800 !important;
        margin: 0 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3) !important;
        color: white !important;
    }
    
    .modern-header p {
        font-size: 1.2rem !important;
        margin: 1rem 0 0 0 !important;
        opacity: 0.9 !important;
        color: white !important;
    }
    
    /* Zone d'upload multiple */
    .upload-zone {
        background: #ffffff !important;
        border: 3px dashed #CC0000 !important;
        border-radius: 12px !important;
        padding: 3rem !important;
        text-align: center !important;
        margin: 2rem 0 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
    }
    
    .upload-zone:hover {
        border-color: #8B0000 !important;
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15) !important;
    }
    
    .upload-icon {
        font-size: 4rem !important;
        color: #CC0000 !important;
        margin-bottom: 1rem !important;
    }
    
    .upload-title {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #000000 !important;
        margin-bottom: 1rem !important;
    }
    
    .upload-subtitle {
        color: #333333 !important;
        font-size: 1.1rem !important;
        margin-bottom: 2rem !important;
    }
    
    /* Cards de résultats */
    .result-card {
        background: #ffffff !important;
        padding: 2rem !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        margin-bottom: 2rem !important;
        border-left: 4px solid #CC0000 !important;
    }
    
    .result-card h3 {
        color: #CC0000 !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 1rem !important;
    }
    
    /* Métriques */
    .metric-card {
        background: #ffffff !important;
        padding: 1.5rem !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        text-align: center !important;
        border-left: 4px solid #CC0000 !important;
        margin-bottom: 1rem !important;
    }
    
    .metric-value {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #CC0000 !important;
        margin-bottom: 0.5rem !important;
    }
    
    .metric-label {
        font-size: 0.9rem !important;
        color: #333333 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    /* Insights */
    .insight-card {
        background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%) !important;
        padding: 1.5rem !important;
        border-radius: 12px !important;
        margin-bottom: 1rem !important;
        border-left: 4px solid #FF6B6B !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
        transition: all 0.3s ease !important;
    }
    
    .insight-card:hover {
        transform: translateX(5px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
    }
    
    .insight-title {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #000000 !important;
        margin-bottom: 0.5rem !important;
    }
    
    .insight-description {
        color: #333333 !important;
        font-size: 0.95rem !important;
        line-height: 1.5 !important;
    }
    
    /* Boutons */
    .stButton > button {
        background: linear-gradient(135deg, #CC0000 0%, #8B0000 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        padding: 0.75rem 2rem !important;
        border-radius: 25px !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15) !important;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .modern-header h1 {
            font-size: 2rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def _render_modern_header():
    """Affiche le header moderne"""
    st.markdown("""
    <div class="modern-header">
        <h1><i class="fas fa-brain"></i> ANALYSE INTELLIGENTE</h1>
        <p>Analysez vos données avec l'intelligence artificielle et découvrez des insights uniques</p>
    </div>
    """, unsafe_allow_html=True)

def _render_sidebar_config():
    """Affiche la configuration dans la sidebar"""
    with st.sidebar:
        st.markdown("### Configuration IA")
        
        # Fournisseur LLM
        llm_provider = st.selectbox(
            "Fournisseur LLM",
            ["ollama", "openai", "anthropic", "local"],
            index=0,
            help="Choisissez le fournisseur d'IA pour l'analyse"
        )
        
        # Modèle
        if llm_provider == "ollama":
            model = st.selectbox(
                "Modèle Ollama",
                ["llama2", "mistral", "codellama", "neural-chat"],
                index=0
            )
        elif llm_provider == "openai":
            model = st.selectbox(
                "Modèle OpenAI",
                ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
                index=0
            )
        else:
            model = st.text_input("Modèle", value="claude-3-sonnet")
        
        # Paramètres
        temperature = st.slider(
            "Créativité IA",
            min_value=0.0,
            max_value=1.0,
            value=0.3,
            step=0.1,
            help="Plus élevé = plus créatif, plus bas = plus précis"
        )
        
        max_tokens = st.slider(
            "Tokens maximum",
            min_value=100,
            max_value=4000,
            value=1000,
            step=100,
            help="Nombre maximum de tokens pour la réponse"
        )
        
        # Sauvegarder la configuration
        st.session_state.llm_config = {
            "provider": llm_provider,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        st.divider()
        
        # Statut des bibliothèques
        st.markdown("### Statut des Bibliothèques")
        
        libraries = [
            ("TextBlob", TEXTBLOB_AVAILABLE),
            ("NLTK", NLTK_AVAILABLE),
            ("Scikit-learn", SKLEARN_AVAILABLE),
            ("Sentence Transformers", SENTENCE_TRANSFORMERS_AVAILABLE),
            ("FAISS", FAISS_AVAILABLE),
            ("LangChain", LANGCHAIN_AVAILABLE),
            ("OpenAI", OPENAI_AVAILABLE)
        ]
        
        for lib_name, available in libraries:
            status = "✅" if available else "❌"
            st.markdown(f"{status} {lib_name}")

def _render_multiple_upload_zone():
    """Affiche la zone d'upload multiple"""
    
    # Upload multiple de fichiers avec style personnalisé intégré
    uploaded_files = st.file_uploader(
        "Importez vos fichiers CSV - Glissez-déposez un ou plusieurs fichiers ou cliquez pour parcourir",
        type=['csv'],
        accept_multiple_files=True,
        help="Formats supportés: CSV | Taille max: 50MB par fichier",
        label_visibility="visible"
    )
    
    return uploaded_files

def _handle_multiple_file_analysis(uploaded_files):
    """Gère l'analyse de plusieurs fichiers"""
    
    if not uploaded_files:
        return
    
    st.markdown("---")
    st.markdown(f"## <i class='fas fa-chart-bar'></i> Analyse de {len(uploaded_files)} fichier(s)", unsafe_allow_html=True)
    
    # Barre de progression globale
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    all_results = []
    
    for i, uploaded_file in enumerate(uploaded_files):
        # Mise à jour de la progression
        progress = (i + 1) / len(uploaded_files)
        progress_bar.progress(progress)
        status_text.text(f"Analyse du fichier {i+1}/{len(uploaded_files)}: {uploaded_file.name}")
        
        try:
            # Lecture du fichier
            df = pd.read_csv(uploaded_file)
            
            # Analyse du fichier
            result = analyze_csv(uploaded_file, df)
            all_results.append(result)
            
            # Affichage des résultats pour ce fichier
            _render_file_analysis_result(result, df, uploaded_file.name)
            
        except Exception as e:
            st.error(f"Erreur lors de l'analyse de {uploaded_file.name}: {str(e)}")
            continue
    
    # Nettoyage de la progression
    progress_bar.empty()
    status_text.empty()
    
    # Résumé global
    if all_results:
        _render_global_summary(all_results)

def analyze_csv(uploaded_file, df: pd.DataFrame) -> Dict[str, Any]:
    """Analyse un fichier CSV et retourne les résultats"""
    
    filename = uploaded_file.name
    file_size = uploaded_file.size
    
    # Calcul des KPIs
    kpis = compute_kpis(df)
    
    # Génération des insights
    insights = generate_insights(kpis, df, filename)
    
    # Classification si possible
    classification = classify(df)
    
    # Détection d'anomalies
    anomalies = detect_anomalies(df)
    
    return {
        'filename': filename,
        'file_size': file_size,
        'kpis': kpis,
        'insights': insights,
        'classification': classification,
        'anomalies': anomalies,
        'timestamp': datetime.now().isoformat()
    }

def compute_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """Calcule les KPIs dynamiques pour un DataFrame"""
    
    kpis = {}
    
    # KPIs de base - conversion explicite en types Python natifs
    kpis['basic'] = {
        'row_count': int(len(df)),
        'column_count': int(len(df.columns)),
        'memory_usage': float(df.memory_usage(deep=True).sum() / (1024 * 1024)),  # MB
        'null_percentage': float((df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100),
        'duplicate_percentage': float((df.duplicated().sum() / len(df)) * 100)
    }
    
    # KPIs numériques
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        kpis['numeric'] = {}
        for col in numeric_cols:
            # Conversion explicite de tous les types NumPy
            mean_val = df[col].mean()
            median_val = df[col].median()
            std_val = df[col].std()
            min_val = df[col].min()
            max_val = df[col].max()
            null_count = df[col].isnull().sum()
            
            kpis['numeric'][col] = {
                'mean': float(mean_val) if pd.notna(mean_val) else None,
                'median': float(median_val) if pd.notna(median_val) else None,
                'std': float(std_val) if pd.notna(std_val) else None,
                'min': float(min_val) if pd.notna(min_val) else None,
                'max': float(max_val) if pd.notna(max_val) else None,
                'null_count': int(null_count),
                'null_percentage': float((null_count / len(df)) * 100)
            }
    
    # KPIs catégoriels
    categorical_cols = df.select_dtypes(include=['object']).columns
    if len(categorical_cols) > 0:
        kpis['categorical'] = {}
        for col in categorical_cols:
            value_counts = df[col].value_counts()
            null_count = df[col].isnull().sum()
            
            kpis['categorical'][col] = {
                'unique_count': int(df[col].nunique()),
                'most_common': str(value_counts.index[0]) if len(value_counts) > 0 else None,
                'most_common_count': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                'null_count': int(null_count),
                'null_percentage': float((null_count / len(df)) * 100)
            }
    
    # Corrélations
    if len(numeric_cols) >= 2:
        corr_matrix = df[numeric_cols].corr()
        strong_correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:
                    strong_correlations.append({
                        'col1': str(corr_matrix.columns[i]),
                        'col2': str(corr_matrix.columns[j]),
                        'correlation': float(corr_value)
                    })
        kpis['correlations'] = strong_correlations
    
    return kpis

def generate_insights(kpis: Dict[str, Any], df: pd.DataFrame, filename: str) -> str:
    """Génère des insights uniques via LLM"""
    
    # Préparation des données pour le LLM
    basic_info = kpis.get('basic', {})
    numeric_info = kpis.get('numeric', {})
    categorical_info = kpis.get('categorical', {})
    correlations = kpis.get('correlations', [])
    
    # Création du prompt
    prompt = f"""
    Analysez ce dataset CSV nommé "{filename}" avec les caractéristiques suivantes:
    
    Informations de base:
    - Nombre de lignes: {basic_info.get('row_count', 0):,}
    - Nombre de colonnes: {basic_info.get('column_count', 0)}
    - Pourcentage de valeurs manquantes: {basic_info.get('null_percentage', 0):.1f}%
    - Pourcentage de duplicats: {basic_info.get('duplicate_percentage', 0):.1f}%
    
    Colonnes numériques: {len(numeric_info)}
    Colonnes catégorielles: {len(categorical_info)}
    Corrélations fortes détectées: {len(correlations)}
    
    Générez des insights uniques et actionnables sur ce dataset. Concentrez-vous sur:
    1. La qualité des données
    2. Les patterns intéressants
    3. Les opportunités d'amélioration
    4. Les recommandations spécifiques
    
    Répondez en français, de manière concise et professionnelle.
    """
    
    # Génération des insights via LLM
    try:
        if LANGCHAIN_AVAILABLE and st.session_state.llm_config.get('provider') == 'ollama':
            insights = _generate_insights_with_ollama(prompt)
        elif OPENAI_AVAILABLE and st.session_state.llm_config.get('provider') == 'openai':
            insights = _generate_insights_with_openai(prompt)
        else:
            insights = _generate_fallback_insights(kpis, df, filename)
    except Exception as e:
        logger.error(f"Erreur lors de la génération des insights: {e}")
        insights = _generate_fallback_insights(kpis, df, filename)
    
    return insights

def _generate_insights_with_ollama(prompt: str) -> str:
    """Génère des insights avec Ollama via LangChain"""
    try:
        llm = Ollama(
            model=st.session_state.llm_config.get('model', 'llama2'),
            temperature=st.session_state.llm_config.get('temperature', 0.3)
        )
        
        template = PromptTemplate(
            input_variables=["prompt"],
            template="{prompt}"
        )
        
        chain = LLMChain(llm=llm, prompt=template)
        result = chain.run(prompt=prompt)
        
        return result
    except Exception as e:
        logger.error(f"Erreur Ollama: {e}")
        return "Erreur lors de la génération des insights avec Ollama."

def _generate_insights_with_openai(prompt: str) -> str:
    """Génère des insights avec OpenAI"""
    try:
        client = openai.OpenAI()
        
        response = client.chat.completions.create(
            model=st.session_state.llm_config.get('model', 'gpt-3.5-turbo'),
            messages=[
                {"role": "system", "content": "Vous êtes un expert en analyse de données. Répondez en français de manière concise et professionnelle."},
                {"role": "user", "content": prompt}
            ],
            temperature=st.session_state.llm_config.get('temperature', 0.3),
            max_tokens=st.session_state.llm_config.get('max_tokens', 1000)
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Erreur OpenAI: {e}")
        return "Erreur lors de la génération des insights avec OpenAI."

def _generate_fallback_insights(kpis: Dict[str, Any], df: pd.DataFrame, filename: str) -> str:
    """Génère des insights de fallback sans LLM"""
    
    basic_info = kpis.get('basic', {})
    numeric_info = kpis.get('numeric', {})
    categorical_info = kpis.get('categorical', {})
    correlations = kpis.get('correlations', [])
    
    insights = []
    
    # Insight sur la taille
    row_count = basic_info.get('row_count', 0)
    if row_count > 10000:
        insights.append(f"Dataset volumineux avec {row_count:,} lignes, offrant une puissance statistique élevée.")
    elif row_count > 1000:
        insights.append(f"Dataset de taille moyenne avec {row_count:,} lignes, suffisant pour des analyses significatives.")
    else:
        insights.append(f"Dataset compact avec {row_count:,} lignes, idéal pour des analyses rapides.")
    
    # Insight sur la qualité
    null_percentage = basic_info.get('null_percentage', 0)
    if null_percentage < 5:
        insights.append(f"Excellente qualité des données avec seulement {null_percentage:.1f}% de valeurs manquantes.")
    elif null_percentage < 20:
        insights.append(f"Qualité acceptable des données avec {null_percentage:.1f}% de valeurs manquantes.")
    else:
        insights.append(f"Qualité des données à améliorer avec {null_percentage:.1f}% de valeurs manquantes.")
    
    # Insight sur les colonnes numériques
    if len(numeric_info) > 0:
        insights.append(f"Présence de {len(numeric_info)} colonnes numériques permettant des analyses statistiques avancées.")
    
    # Insight sur les corrélations
    if len(correlations) > 0:
        insights.append(f"Détection de {len(correlations)} corrélations fortes entre variables, révélant des relations importantes.")
    
    # Insight sur les colonnes catégorielles
    if len(categorical_info) > 0:
        insights.append(f"Dataset avec {len(categorical_info)} colonnes catégorielles, idéal pour l'analyse de segments.")
    
    return "\n\n".join(insights)

def classify(df: pd.DataFrame) -> Dict[str, Any]:
    """Classifie le dataset si une colonne cible est détectée"""
    
    classification = {
        'has_target': False,
        'target_column': None,
        'classification_type': None,
        'unique_values': None
    }
    
    # Recherche d'une colonne cible potentielle
    potential_targets = []
    
    for col in df.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in ['target', 'label', 'class', 'category', 'sentiment', 'type']):
            potential_targets.append(col)
    
    if potential_targets:
        target_col = potential_targets[0]
        unique_values = df[target_col].nunique()
        
        classification['has_target'] = True
        classification['target_column'] = target_col
        classification['unique_values'] = unique_values
        
        # Détermination du type de classification
        if unique_values == 2:
            classification['classification_type'] = 'binary'
        elif unique_values <= 10:
            classification['classification_type'] = 'multiclass'
        else:
            classification['classification_type'] = 'regression'
    
    return classification

def detect_anomalies(df: pd.DataFrame) -> Dict[str, Any]:
    """Détecte les anomalies dans le dataset"""
    
    anomalies = {
        'outliers': [],
        'missing_patterns': [],
        'data_types': []
    }
    
    # Détection d'outliers pour les colonnes numériques
    numeric_cols = df.select_dtypes(include=['number']).columns
    
    if len(numeric_cols) > 0 and SKLEARN_AVAILABLE:
        try:
            # Utilisation d'Isolation Forest
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            outlier_labels = iso_forest.fit_predict(df[numeric_cols].fillna(0))
            
            outlier_indices = df[outlier_labels == -1].index.tolist()
            anomalies['outliers'] = {
                'count': int(len(outlier_indices)),
                'percentage': float((len(outlier_indices) / len(df)) * 100),
                'indices': [int(idx) for idx in outlier_indices[:10]]  # Limiter à 10 pour l'affichage
            }
        except Exception as e:
            logger.error(f"Erreur lors de la détection d'outliers: {e}")
            anomalies['outliers'] = {
                'count': 0,
                'percentage': 0.0,
                'indices': []
            }
    
    # Patterns de valeurs manquantes
    missing_data = df.isnull().sum()
    missing_cols = missing_data[missing_data > 0].sort_values(ascending=False)
    
    if len(missing_cols) > 0:
        anomalies['missing_patterns'] = {
            'columns_with_missing': int(len(missing_cols)),
            'most_missing': str(missing_cols.index[0]),
            'missing_percentage': float((missing_cols.iloc[0] / len(df)) * 100)
        }
    else:
        anomalies['missing_patterns'] = {
            'columns_with_missing': 0,
            'most_missing': None,
            'missing_percentage': 0.0
        }
    
    # Vérification des types de données
    data_types = df.dtypes.value_counts().to_dict()
    anomalies['data_types'] = {str(k): int(v) for k, v in data_types.items()}
    
    return anomalies

def _render_file_analysis_result(result: Dict[str, Any], df: pd.DataFrame, filename: str):
    """Affiche les résultats d'analyse pour un fichier"""
    
    st.markdown(f"### <i class='fas fa-file-csv'></i> {filename}", unsafe_allow_html=True)
    
    # Métriques de base
    kpis = result['kpis']
    basic_info = kpis.get('basic', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Lignes", f"{basic_info.get('row_count', 0):,}")
    
    with col2:
        st.metric("Colonnes", basic_info.get('column_count', 0))
    
    with col3:
        st.metric("Complétude", f"{100 - basic_info.get('null_percentage', 0):.1f}%")
    
    with col4:
        st.metric("Taille", f"{result['file_size'] / 1024:.1f} KB")
    
    # Insights IA
    st.markdown("#### <i class='fas fa-brain'></i> Insights IA", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-description">
            {result['insights']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Classification
    classification = result['classification']
    if classification['has_target']:
        st.markdown("#### <i class='fas fa-tags'></i> Classification", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"**Colonne cible:** {classification['target_column']}")
        with col2:
            st.info(f"**Type:** {classification['classification_type']}")
        with col3:
            st.info(f"**Valeurs uniques:** {classification['unique_values']}")
    
    # Anomalies
    anomalies = result['anomalies']
    if anomalies['outliers'] or anomalies['missing_patterns']:
        st.markdown("#### <i class='fas fa-exclamation-triangle'></i> Anomalies Détectées", unsafe_allow_html=True)
        
        if anomalies['outliers']:
            outliers_info = anomalies['outliers']
            st.warning(f"**Outliers:** {outliers_info['count']} ({outliers_info['percentage']:.1f}%)")
        
        if anomalies['missing_patterns']:
            missing_info = anomalies['missing_patterns']
            st.warning(f"**Valeurs manquantes:** {missing_info['columns_with_missing']} colonnes affectées")
    
    # Visualisations
    _render_visualizations(df, filename)
    
    st.markdown("---")

def _render_visualizations(df: pd.DataFrame, filename: str):
    """Génère des visualisations pour le dataset"""
    
    st.markdown("#### <i class='fas fa-chart-pie'></i> Visualisations", unsafe_allow_html=True)
    
    numeric_cols = df.select_dtypes(include=['number']).columns
    categorical_cols = df.select_dtypes(include=['object']).columns
    
    if len(numeric_cols) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            if len(numeric_cols) >= 1:
                fig = px.histogram(df, x=numeric_cols[0], title=f"Distribution de {numeric_cols[0]}")
                fig.update_layout(plot_bgcolor='white', paper_bgcolor='white')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if len(numeric_cols) >= 2:
                fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1], 
                               title=f"Relation {numeric_cols[0]} vs {numeric_cols[1]}")
                fig.update_layout(plot_bgcolor='white', paper_bgcolor='white')
                st.plotly_chart(fig, use_container_width=True)
    
    if len(categorical_cols) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            if len(categorical_cols) >= 1:
                value_counts = df[categorical_cols[0]].value_counts().head(10)
                fig = px.bar(x=value_counts.index, y=value_counts.values, 
                           title=f"Top 10 - {categorical_cols[0]}")
                fig.update_layout(plot_bgcolor='white', paper_bgcolor='white')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if len(numeric_cols) >= 2:
                corr_matrix = df[numeric_cols].corr()
                fig = px.imshow(corr_matrix, text_auto=True, aspect="auto",
                              title="Matrice de Corrélation")
                fig.update_layout(plot_bgcolor='white', paper_bgcolor='white')
                st.plotly_chart(fig, use_container_width=True)

def _convert_numpy_types(obj):
    """Convertit les types NumPy en types Python natifs pour la sérialisation JSON"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: _convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_convert_numpy_types(item) for item in obj]
    else:
        return obj

def _render_global_summary(all_results: List[Dict[str, Any]]):
    """Affiche un résumé global de toutes les analyses"""
    
    st.markdown("## <i class='fas fa-chart-line'></i> Résumé Global", unsafe_allow_html=True)
    
    # Métriques globales
    total_files = len(all_results)
    total_rows = sum(result['kpis']['basic']['row_count'] for result in all_results)
    total_columns = sum(result['kpis']['basic']['column_count'] for result in all_results)
    avg_completeness = np.mean([100 - result['kpis']['basic']['null_percentage'] for result in all_results])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Fichiers Analysés", total_files)
    
    with col2:
        st.metric("Total Lignes", f"{total_rows:,}")
    
    with col3:
        st.metric("Total Colonnes", total_columns)
    
    with col4:
        st.metric("Complétude Moyenne", f"{avg_completeness:.1f}%")
    
    # Export global
    st.markdown("#### <i class='fas fa-download'></i> Export Global", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Export JSON avec conversion des types NumPy
        try:
            # Conversion des types NumPy avant sérialisation
            converted_results = _convert_numpy_types(all_results)
            json_data = json.dumps(converted_results, ensure_ascii=False, indent=2)
            st.download_button(
                label="Télécharger Analyse JSON",
                data=json_data,
                file_name=f"analyse_globale_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        except Exception as e:
            st.error(f"Erreur lors de la génération du JSON: {e}")
            # Fallback: export simplifié
            simplified_results = []
            for result in all_results:
                simplified_result = {
                    'filename': result['filename'],
                    'file_size': int(result['file_size']),
                    'timestamp': result['timestamp'],
                    'kpis': {
                        'basic': {
                            'row_count': int(result['kpis']['basic']['row_count']),
                            'column_count': int(result['kpis']['basic']['column_count']),
                            'memory_usage': float(result['kpis']['basic']['memory_usage']),
                            'null_percentage': float(result['kpis']['basic']['null_percentage']),
                            'duplicate_percentage': float(result['kpis']['basic']['duplicate_percentage'])
                        }
                    }
                }
                simplified_results.append(simplified_result)
            
            json_data = json.dumps(simplified_results, ensure_ascii=False, indent=2)
            st.download_button(
                label="Télécharger Analyse JSON (Simplifié)",
                data=json_data,
                file_name=f"analyse_globale_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        # Export CSV des métriques
        try:
            metrics_data = []
            for result in all_results:
                basic = result['kpis']['basic']
                metrics_data.append({
                    'filename': result['filename'],
                    'rows': int(basic['row_count']),
                    'columns': int(basic['column_count']),
                    'completeness': float(100 - basic['null_percentage']),
                    'duplicates': float(basic['duplicate_percentage'])
                })
            
            metrics_df = pd.DataFrame(metrics_data)
            csv_data = metrics_df.to_csv(index=False)
            st.download_button(
                label="Télécharger Métriques CSV",
                data=csv_data,
                file_name=f"metriques_globales_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"Erreur lors de la génération du CSV: {e}")

def _render_features_section():
    """Affiche la section des fonctionnalités"""
    st.markdown("### <i class='fas fa-star'></i> Fonctionnalités Avancées", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="result-card">
            <h3><i class="fas fa-brain"></i> Analyse IA</h3>
            <p>Intelligence artificielle pour découvrir des patterns cachés et générer des insights uniques</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="result-card">
            <h3><i class="fas fa-chart-pie"></i> KPIs Dynamiques</h3>
            <p>Calcul automatique de métriques adaptées à vos données</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="result-card">
            <h3><i class="fas fa-shield-alt"></i> Détection d'Anomalies</h3>
            <p>Identification automatique des valeurs aberrantes et patterns anormaux</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
