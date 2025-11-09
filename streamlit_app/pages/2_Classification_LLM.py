"""
Page de Classification LLM - FreeMobilaChat
Classification professionnelle de tweets avec LLM et Machine Learning
Développé dans le cadre d'un mémoire de master en Data Science - Version Académique 2.0
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime
import sys
import os
import logging
from typing import Dict, Any, List, Optional
import warnings
warnings.filterwarnings('ignore')

# ==============================================================================
# CONFIGURATION ET LOGGING
# ==============================================================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ajout du chemin pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend', 'app'))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ==============================================================================
# IMPORTS DES SERVICES D'ANALYSE
# ==============================================================================

# Import des services de classification
try:
    from services.tweet_classifier import TweetClassifier, ClassificationResult
    from services.llm_analysis_engine import LLMAnalysisEngine
    from services.role_manager import initialize_role_system, get_current_role, check_permission
    from services.dynamic_classifier import DynamicClassificationEngine
    CLASSIFICATION_AVAILABLE = True
    ROLE_SYSTEM_AVAILABLE = True
    DYNAMIC_CLASSIFIER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Services de classification non disponibles: {e}")
    CLASSIFICATION_AVAILABLE = False
    ROLE_SYSTEM_AVAILABLE = False
    DYNAMIC_CLASSIFIER_AVAILABLE = False

# Import des KPIs et visualisations avancées pour dashboard business
try:
    from services import enhanced_kpis_vizualizations
    # Import direct des fonctions necessaires
    from services.enhanced_kpis_vizualizations import (
        compute_business_kpis,
        render_business_kpis,
        render_complete_dashboard
    )
    ENHANCED_KPIS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Module Enhanced KPIs non disponible: {e}")
    ENHANCED_KPIS_AVAILABLE = False
    enhanced_kpis_vizualizations = None

# Import du systeme de selection de roles
try:
    from components.role_selector import (
        render_role_selector,
        render_role_specific_header,
        get_current_role,
        filter_kpis_by_role,
        filter_dataframe_by_role,
        get_dashboard_message_by_role,
        has_permission
    )
    ROLE_SELECTOR_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Role selector module not available: {e}")
    ROLE_SELECTOR_AVAILABLE = False

# ==============================================================================
# CONFIGURATION DE LA PAGE
# ==============================================================================
st.set_page_config(
    page_title="Classification LLM - FreeMobilaChat",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# TAXONOMIE DE CLASSIFICATION - Version LLM
# ==============================================================================
CLASSIFICATION_SCHEMA = {
    "is_claim": [0, 1],  # 0 = Non-réclamation, 1 = Réclamation
    "topics": ["fibre", "dsl", "wifi", "tv", "mobile", "facture", 
               "activation", "resiliation", "autre"],
    "sentiment": ["neg", "neu", "pos"],
    "urgence": ["haute", "moyenne", "basse"],
    "incident": ["facturation", "incident_reseau", "livraison", 
                 "information", "processus_sav", "autre"]
}

# ==============================================================================
# FEW-SHOT LEARNING EXAMPLES
# ==============================================================================
FEW_SHOT_EXAMPLES = [
    {
        "tweet": "rt @free: découvrez la nouvelle chaîne imearth en 4k !",
        "result": {
            "is_claim": 0,
            "topics": ["tv"],
            "sentiment": "neu",
            "urgence": "basse",
            "incident": "information",
            "confidence": 0.9
        }
    },
    {
        "tweet": "@free panne fibre à cergy depuis 7h, impossible de bosser",
        "result": {
            "is_claim": 1,
            "topics": ["fibre"],
            "sentiment": "neg",
            "urgence": "haute",
            "incident": "incident_reseau",
            "confidence": 0.95
        }
    },
    {
        "tweet": "@freebox toujours pas de réponse depuis 3 jours, c'est long",
        "result": {
            "is_claim": 1,
            "topics": ["autre"],
            "sentiment": "neg",
            "urgence": "moyenne",
            "incident": "processus_sav",
            "confidence": 0.88
        }
    },
    {
        "tweet": "Merci @free pour la résolution rapide de mon problème de connexion !",
        "result": {
            "is_claim": 0,
            "topics": ["fibre", "dsl"],
            "sentiment": "pos",
            "urgence": "basse",
            "incident": "information",
            "confidence": 0.92
        }
    },
    {
        "tweet": "@free ma facture est incorrecte ce mois-ci, pouvez-vous vérifier ?",
        "result": {
            "is_claim": 1,
            "topics": ["facture"],
            "sentiment": "neu",
            "urgence": "moyenne",
            "incident": "facturation",
            "confidence": 0.91
        }
    }
]

# ==============================================================================
# FONCTIONS PRINCIPALES
# ==============================================================================

def main():
    """
    Point d'entree principal de la page de classification LLM
    
    Cette page permet de classifier des tweets avec un systeme LLM
    et affiche des KPIs business adaptes selon le role de l'utilisateur.
    """
    
    # Chargement des styles CSS professionnels
    _load_professional_css()
    
    # ==============================================================================
    # SYSTEME DE SELECTION DE ROLES
    # ==============================================================================
    # Affiche le selecteur de roles et obtient le role actuel
    # Le role determine quels KPIs sont affiches et les permissions
    if ROLE_SELECTOR_AVAILABLE:
        # Rendre le selecteur de roles dans la sidebar
        current_role = render_role_selector()
        
        # Afficher un header personnalise selon le role
        render_role_specific_header(current_role, "Classification LLM")
    elif ROLE_SYSTEM_AVAILABLE:
        # Fallback sur l'ancien systeme de roles si disponible
        role_manager, role_ui_manager = initialize_role_system()
        current_role = role_ui_manager.render_role_selector()
        role_ui_manager.render_role_specific_header(current_role, "Classification LLM")
    else:
        # Header professionnel par defaut si aucun systeme disponible
        current_role = "Data Analyst"  # Role par defaut
        _render_professional_header()
    
    # Configuration dans la sidebar
    _render_sidebar_config()
    
    # Zone d'upload de fichiers
    uploaded_file = _render_upload_zone()
    
    if uploaded_file is not None:
        # Traitement et analyse du fichier uploadé
        _handle_dynamic_classification(uploaded_file)
    else:
        # Affichage de la page d'accueil avec fonctionnalités
        _render_welcome_section()

# ==============================================================================
# INTERFACE UTILISATEUR
# ==============================================================================

def _load_professional_css():
    """Charge les styles CSS professionnels pour l'interface académique"""
    
    st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
    /* Reset et configuration globale */
    .main {background: #f5f7fa;}
    .block-container {padding: 1.5rem !important; max-width: 1400px !important; margin: 0 auto;}
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Header professionnel */
    .professional-header {
        background: linear-gradient(135deg, #CC0000 0%, #8B0000 100%);
        padding: 2.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 24px rgba(204, 0, 0, 0.25);
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: white;
        text-align: center;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .header-subtitle {
        font-size: 1.1rem;
        font-weight: 400;
        color: rgba(255,255,255,0.95);
        text-align: center;
        margin-top: 0.5rem;
    }
    
    /* Cartes de statistiques */
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-left: 4px solid #CC0000;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(204, 0, 0, 0.15);
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-claim {background: #fee; color: #c53030;}
    .badge-no-claim {background: #e6fffa; color: #047857;}
    .badge-pos {background: #d4edda; color: #155724;}
    .badge-neu {background: #d1ecf1; color: #0c5460;}
    .badge-neg {background: #f8d7da; color: #721c24;}
    .badge-haute {background: #f8d7da; color: #721c24;}
    .badge-moyenne {background: #fff3cd; color: #856404;}
    .badge-basse {background: #d4edda; color: #155724;}
    </style>
    """, unsafe_allow_html=True)

def _render_professional_header():
    """Affiche l'en-tête professionnel de la page"""
    
    st.markdown("""
    <div class="professional-header">
        <div style="display: flex; align-items: center; justify-content: center; gap: 1.5rem; margin-bottom: 1rem;">
            <div style="width: 60px; height: 60px; background: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
                <span style="font-size: 1.8rem; font-weight: 900; color: #CC0000;">FM</span>
            </div>
            <div>
                <div style="font-size: 1.8rem; font-weight: 900; color: white; letter-spacing: -0.5px;">FreeMobilaChat</div>
                <div style="font-size: 0.9rem; color: rgba(255,255,255,0.9); letter-spacing: 0.5px;">Système d'Analyse LLM</div>
            </div>
        </div>
        <h1 class="header-title">
            <i class="fas fa-robot" style="margin-right: 1rem;"></i>
            CLASSIFICATION LLM DES TWEETS
        </h1>
        <p class="header-subtitle">
            Intelligence Artificielle avancée | Few-shot learning | Analyse multi-dimensionnelle
        </p>
    </div>
    """, unsafe_allow_html=True)

def _render_sidebar_config():
    """Configuration dans la barre latérale"""
    
    with st.sidebar:
        st.markdown("### <i class='fas fa-cog'></i> Configuration", unsafe_allow_html=True)
        
        # Paramètres LLM
        with st.expander("Paramètres LLM", expanded=True):
            st.markdown("**Modèle LLM**")
            
            llm_provider = st.selectbox(
                "Fournisseur",
                ["Fallback (Règles)", "Mistral (Ollama)", "Ollama", "OpenAI", "Anthropic"],
                help="Sélectionnez le fournisseur LLM - Mistral (Ollama) utilise le nouveau module de classification avancée"
            )
            
            confidence_threshold = st.slider(
                "Seuil de confiance",
                0.0, 1.0, 0.7, 0.05,
                help="Score minimum pour accepter une classification"
            )
            
            batch_size = st.number_input(
                "Taille des lots",
                10, 100, 50, 10,
                help="Nombre de tweets traités simultanément"
            )
            
            enable_few_shot = st.checkbox(
                "Activer few-shot learning",
                value=True,
                help="Utilise les exemples pré-annotés"
            )
        
        # Sauvegarde de la configuration
        st.session_state.llm_config = {
            "llm_provider": llm_provider,
            "confidence_threshold": confidence_threshold,
            "batch_size": batch_size,
            "enable_few_shot": enable_few_shot
        }
        
        st.markdown("---")
        
        # Navigation rapide
        st.markdown("### <i class='fas fa-compass'></i> Navigation", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Analyse IA", key="nav_ia", use_container_width=True):
                st.switch_page("pages/1_Analyse_Intelligente.py")
        with col2:
            if st.button("Analyse Classique", key="nav_class", use_container_width=True):
                st.switch_page("pages/4_Analyse_Classique.py")

def _render_upload_zone():
    """Zone d'upload de fichiers professionnelle"""
    
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0 1.5rem 0;">
        <h2 style="font-size: 2rem; font-weight: 700; color: #1a202c; margin-bottom: 0.5rem;">
            <i class="fas fa-cloud-upload-alt" style="color: #CC0000; margin-right: 0.5rem;"></i>
            Chargement des Données
        </h2>
        <p style="font-size: 1rem; color: #718096;">
            Formats supportés: CSV, Excel, JSON | Taille maximale: 50 MB
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Sélectionnez votre fichier de tweets",
        type=['csv', 'xlsx', 'xls', 'json'],
        help="Le fichier doit contenir au minimum une colonne 'tweet' ou 'text'",
        label_visibility="collapsed"
    )
    
    return uploaded_file

def _render_welcome_section():
    """Section de bienvenue avec exemples et documentation"""
    
    st.markdown("""
    <div style="background: white; padding: 2rem; border-radius: 10px; margin: 2rem 0;">
        <h2><i class="fas fa-info-circle"></i> Classification LLM - Guide</h2>
        <p>Cette interface permet la classification automatique intelligente selon:</p>
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
    st.markdown("### <i class='fas fa-graduation-cap'></i> Exemples Few-Shot Learning", unsafe_allow_html=True)
    st.info("Le système utilise 5 exemples pré-annotés pour améliorer la précision de la classification.")
    
    for i, ex in enumerate(FEW_SHOT_EXAMPLES, 1):
        st.markdown(f"""
        <div style="background: #f7fafc; padding: 1rem; border-left: 4px solid #CC0000; margin: 1rem 0;">
            <strong>Exemple {i}:</strong> {ex['tweet']}<br>
            <strong>Classification:</strong> {json.dumps(ex['result'], ensure_ascii=False)}
        </div>
        """, unsafe_allow_html=True)

def _preprocess_dataset(df: pd.DataFrame, text_column: str):
    """Prétraite le dataset : nettoyage, normalisation, formatting"""
    
    import re
    
    df_clean = df.copy()
    
    # Statistiques de prétraitement
    stats = {
        'original_rows': len(df),
        'original_nulls': df[text_column].isnull().sum(),
        'original_empty': (df[text_column] == '').sum(),
        'original_duplicates': df[text_column].duplicated().sum()
    }
    
    # 1. Nettoyage des valeurs nulles
    df_clean[text_column] = df_clean[text_column].fillna('')
    
    # 2. Conversion en string
    df_clean[text_column] = df_clean[text_column].astype(str)
    
    # 3. Suppression des espaces multiples
    df_clean[text_column] = df_clean[text_column].apply(lambda x: re.sub(r'\s+', ' ', x).strip())
    
    # 4. Normalisation des caractères spéciaux
    df_clean[text_column] = df_clean[text_column].apply(lambda x: re.sub(r'[\n\r\t]', ' ', x))
    
    # 5. Suppression des URLs
    df_clean[text_column] = df_clean[text_column].apply(
        lambda x: re.sub(r'http\S+|www\S+|https\S+', '[URL]', x, flags=re.MULTILINE)
    )
    
    # 6. Normalisation des mentions
    df_clean[text_column] = df_clean[text_column].apply(
        lambda x: re.sub(r'@(\w+)', r'@\1', x)
    )
    
    # 7. Suppression des lignes vides après nettoyage
    df_clean = df_clean[df_clean[text_column].str.strip() != '']
    
    # 8. Ajout d'une colonne indiquant si le texte a été modifié
    df_clean['preprocessed'] = True
    df_clean['original_length'] = df[text_column].apply(lambda x: len(str(x)) if pd.notna(x) else 0)
    df_clean['cleaned_length'] = df_clean[text_column].apply(len)
    
    # Statistiques finales
    stats['cleaned_rows'] = len(df_clean)
    stats['removed_rows'] = stats['original_rows'] - stats['cleaned_rows']
    stats['avg_original_length'] = df_clean['original_length'].mean()
    stats['avg_cleaned_length'] = df_clean['cleaned_length'].mean()
    stats['reduction_rate'] = (
        (stats['avg_original_length'] - stats['avg_cleaned_length']) / stats['avg_original_length'] * 100
        if stats['avg_original_length'] > 0 else 0
    )
    
    return df_clean, stats

def _display_preprocessing_results(df_original: pd.DataFrame, df_preprocessed: pd.DataFrame, 
                                   stats: Dict[str, Any], text_column: str):
    """Affiche les résultats du prétraitement de manière professionnelle"""
    
    # KPI du prétraitement
    st.markdown("### Résultats du Prétraitement")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <i class="fas fa-file-alt" style="color: #667eea; font-size: 2rem;"></i>
            <div style="font-size: 2rem; font-weight: 700; margin-top: 0.5rem;">{stats['cleaned_rows']}</div>
            <div style="font-size: 0.9rem; color: #666; margin-top: 0.25rem;">Lignes Nettoyées</div>
            <div style="font-size: 0.8rem; color: #999; margin-top: 0.1rem;">(-{stats['removed_rows']} lignes)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <i class="fas fa-eraser" style="color: #48bb78; font-size: 2rem;"></i>
            <div style="font-size: 2rem; font-weight: 700; margin-top: 0.5rem;">{stats['original_nulls']}</div>
            <div style="font-size: 0.9rem; color: #666; margin-top: 0.25rem;">Nulls Traités</div>
            <div style="font-size: 0.8rem; color: #999; margin-top: 0.1rem;">Remplacés par ''</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <i class="fas fa-copy" style="color: #ed8936; font-size: 2rem;"></i>
            <div style="font-size: 2rem; font-weight: 700; margin-top: 0.5rem;">{stats['original_duplicates']}</div>
            <div style="font-size: 0.9rem; color: #666; margin-top: 0.25rem;">Doublons Détectés</div>
            <div style="font-size: 0.8rem; color: #999; margin-top: 0.1rem;">Conservés</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <i class="fas fa-compress-alt" style="color: #4299e1; font-size: 2rem;"></i>
            <div style="font-size: 2rem; font-weight: 700; margin-top: 0.5rem;">{stats['reduction_rate']:.1f}%</div>
            <div style="font-size: 0.9rem; color: #666; margin-top: 0.25rem;">Réduction Texte</div>
            <div style="font-size: 0.8rem; color: #999; margin-top: 0.1rem;">{stats['avg_cleaned_length']:.0f} chars moy.</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Comparaison Avant/Après Nettoyage
    st.markdown("### Comparaison Avant/Apres Nettoyage")
    
    tab1, tab2 = st.tabs(["Donnees Originales", "Donnees Pretraitees"])
    
    with tab1:
        st.markdown("**Dataset Original (Brut)**")
        st.info(f"Affichage des 20 premières lignes du dataset original")
        
        # Affichage avec mise en évidence des problèmes
        display_original = df_original[[text_column]].head(20).copy()
        display_original['Longueur'] = display_original[text_column].apply(lambda x: len(str(x)) if pd.notna(x) else 0)
        display_original['Null'] = df_original[text_column].head(20).isnull()
        display_original['Vide'] = df_original[text_column].head(20).apply(lambda x: str(x).strip() == '' if pd.notna(x) else False)
        
        st.dataframe(display_original, use_container_width=True, height=400)
        
        # Statistiques des données originales
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Longueur Moyenne", f"{stats['avg_original_length']:.0f} chars")
        with col2:
            st.metric("Valeurs Nulles", stats['original_nulls'])
        with col3:
            st.metric("Lignes Vides", stats['original_empty'])
    
    with tab2:
        st.markdown("**Dataset Prétraité (Nettoyé)**")
        st.success(f"Dataset nettoyé prêt pour la classification - {len(df_preprocessed)} lignes")
        
        # Affichage du dataset nettoyé
        display_cleaned = df_preprocessed[[text_column, 'cleaned_length']].head(20).copy()
        display_cleaned.columns = ['Texte Nettoyé', 'Longueur']
        
        st.dataframe(display_cleaned, use_container_width=True, height=400)
        
        # Statistiques des données nettoyées
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Longueur Moyenne", f"{stats['avg_cleaned_length']:.0f} chars")
        with col2:
            st.metric("Valeurs Nulles", 0, delta="-100%", delta_color="normal")
        with col3:
            st.metric("Lignes Vides", 0, delta="-100%", delta_color="normal")
    
    # Exemples de transformations
    st.markdown("### Exemples de Transformations")
    
    # Sélection d'exemples montrant les changements
    examples_df = df_original[[text_column]].head(5).copy()
    examples_df['Avant'] = examples_df[text_column]
    examples_df['Après'] = df_preprocessed[text_column].head(5)
    examples_df = examples_df[['Avant', 'Après']]
    
    for idx, row in examples_df.iterrows():
        if str(row['Avant']) != str(row['Après']):
            st.markdown(f"""
            <div style="background: #f7fafc; padding: 1rem; border-left: 4px solid #667eea; margin: 0.5rem 0;">
                <div style="margin-bottom: 0.5rem;">
                    <strong style="color: #e53e3e;">Avant:</strong> <span style="color: #666;">{row['Avant'][:100]}...</span>
                </div>
                <div>
                    <strong style="color: #38a169;">Après:</strong> <span style="color: #666;">{row['Après'][:100]}...</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

def _handle_dynamic_classification(uploaded_file):
    """
    Gère la classification dynamique du fichier uploadé
    
    Cette fonction garantit que TOUTES les données sont recalculées
    à chaque nouveau fichier uploadé. Un système de détection de
    changement de fichier nettoie automatiquement le cache.
    
    Args:
        uploaded_file: Fichier uploadé via st.file_uploader
    """
    try:
        # ================================================================
        # DÉTECTION DE CHANGEMENT DE FICHIER (Garantit le dynamisme)
        # ================================================================
        current_file_id = f"{uploaded_file.name}_{uploaded_file.size}"
        last_file_id = st.session_state.get('last_processed_file_id', None)
        
        # Si c'est un nouveau fichier, nettoyer tout le cache
        if current_file_id != last_file_id:
            # Nettoyage complet du cache pour garantir recalcul dynamique
            keys_to_clear = [
                'preprocessed_dataframe',
                'preprocessing_stats',
                'classified_dataframe',
                'classification_metrics',
                'text_column',
                'dataframe'
            ]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            
            # Enregistrer le nouveau fichier
            st.session_state['last_processed_file_id'] = current_file_id
            
            # Message de confirmation du nouveau fichier
            st.info(f"**Nouveau fichier detecte:** {uploaded_file.name} - Toutes les donnees seront recalculees dynamiquement")
        
        # Lecture du fichier (TOUJOURS à partir du fichier uploadé, jamais du cache)
        df = _read_uploaded_file(uploaded_file)
        
        if df is None or df.empty:
            st.error("Impossible de lire le fichier ou fichier vide")
            return
        
        # Affichage des informations du fichier (dynamiques)
        _display_file_info(uploaded_file, df)
        
        st.markdown("---")
        
        # SECTION PRÉTRAITEMENT - CORE FEATURE
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; margin: 1.5rem 0;">
            <h2 style="color: white; margin: 0; font-size: 1.8rem;">
                <i class="fas fa-broom" style="margin-right: 0.5rem;"></i>
                PRÉTRAITEMENT DES DONNÉES
            </h2>
            <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1rem;">
                Nettoyage et normalisation automatique avant classification
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Récupération de la colonne de texte (ou sélection interactive)
        text_column = st.session_state.get('text_column', None)
        if text_column is None or text_column not in df.columns:
            text_column = df.columns[0]  # Défaut à la première colonne
        
        # Prétraitement DYNAMIQUE du dataset (recalculé à chaque fois)
        # IMPORTANT: Ne pas utiliser de cache ici pour garantir dynamisme
        df_preprocessed, preprocessing_stats = _preprocess_dataset(df, text_column)
        
        # Affichage des résultats du prétraitement (dynamiques)
        _display_preprocessing_results(df, df_preprocessed, preprocessing_stats, text_column)
        
        # Sauvegarde temporaire UNIQUEMENT pour cette session (pas de cache entre fichiers)
        st.session_state['preprocessed_dataframe'] = df_preprocessed
        st.session_state['preprocessing_stats'] = preprocessing_stats
        st.session_state['current_file_name'] = uploaded_file.name
        
        st.markdown("---")
        
        # Bouton de classification (utilise les données prétraitées)
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0 1rem 0;">
            <h3 style="color: #1a202c;">
                <i class="fas fa-arrow-down" style="color: #CC0000; margin-right: 0.5rem;"></i>
                Dataset prétraité prêt pour la classification
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Lancer la Classification LLM", type="primary", use_container_width=True, key='btn_classify_llm'):
            # ================================================================
            # CLASSIFICATION 100% DYNAMIQUE
            # ================================================================
            # Utilise TOUJOURS le dataset fraîchement prétraité (pas de cache)
            # Chaque fichier uploadé = nouvelles données = nouveaux résultats
            df_to_classify = df_preprocessed  # Utiliser les données fraîches, pas le cache
            
            # Classification dynamique complète (recalcule TOUT)
            df_classified, metrics = _perform_dynamic_classification(df_to_classify, text_column)
            
            if df_classified is not None and metrics is not None:
                # Affichage des résultats (100% dynamiques basés sur df_classified et metrics)
                _display_classification_results(df_classified, metrics)
        
    except Exception as e:
        st.error(f"Erreur lors du traitement du fichier: {str(e)}")
        logger.error(f"Error processing file: {str(e)}", exc_info=True)

def _read_uploaded_file(uploaded_file):
    """Lit le fichier uploadé selon son type"""
    try:
        file_ext = uploaded_file.name.split('.')[-1].lower()
        
        if file_ext == 'csv':
            return pd.read_csv(uploaded_file, encoding='utf-8-sig')
        elif file_ext in ['xlsx', 'xls']:
            return pd.read_excel(uploaded_file)
        elif file_ext == 'json':
            return pd.read_json(uploaded_file)
        else:
            st.error("Format de fichier non supporté")
            return None
    except Exception as e:
        st.error(f"Erreur lors de la lecture: {e}")
        logger.error(f"Error reading file: {e}", exc_info=True)
        return None

def _display_file_info(uploaded_file, df):
    """Affiche les informations du fichier"""
    st.markdown("### <i class='fas fa-info-circle'></i> Informations du Fichier", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="background: #f7fafc; padding: 1rem; border-radius: 8px; text-align: center;">
            <i class="fas fa-file" style="font-size: 1.5rem; color: #CC0000;"></i>
            <div style="font-size: 0.9rem; color: #666; margin-top: 0.5rem;">Nom</div>
            <div style="font-size: 1.1rem; font-weight: 600; margin-top: 0.25rem;">{uploaded_file.name[:20]}...</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: #f7fafc; padding: 1rem; border-radius: 8px; text-align: center;">
            <i class="fas fa-weight" style="font-size: 1.5rem; color: #CC0000;"></i>
            <div style="font-size: 0.9rem; color: #666; margin-top: 0.5rem;">Taille</div>
            <div style="font-size: 1.1rem; font-weight: 600; margin-top: 0.25rem;">{uploaded_file.size / 1024:.1f} KB</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: #f7fafc; padding: 1rem; border-radius: 8px; text-align: center;">
            <i class="fas fa-list" style="font-size: 1.5rem; color: #CC0000;"></i>
            <div style="font-size: 0.9rem; color: #666; margin-top: 0.5rem;">Lignes</div>
            <div style="font-size: 1.1rem; font-weight: 600; margin-top: 0.25rem;">{len(df):,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="background: #f7fafc; padding: 1rem; border-radius: 8px; text-align: center;">
            <i class="fas fa-columns" style="font-size: 1.5rem; color: #CC0000;"></i>
            <div style="font-size: 0.9rem; color: #666; margin-top: 0.5rem;">Colonnes</div>
            <div style="font-size: 1.1rem; font-weight: 600; margin-top: 0.25rem;">{len(df.columns)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Détection automatique de la colonne de texte
    text_columns = [col for col in df.columns if df[col].dtype == 'object']
    if text_columns:
        st.info(f"Colonnes de texte détectées: {', '.join(text_columns[:3])}")
    
    # Configuration de la colonne de texte
    st.markdown("#### <i class='fas fa-cog'></i> Configuration", unsafe_allow_html=True)
    text_column = st.selectbox(
        "Sélectionnez la colonne contenant le texte à classifier:",
        text_columns,
        help="Choisissez la colonne qui contient les tweets ou textes à classifier"
    )
    
    # Sauvegarde de la configuration
    st.session_state['text_column'] = text_column
    st.session_state['dataframe'] = df

def _perform_dynamic_classification(df: pd.DataFrame, text_column: str):
    """
    Effectue la classification LLM sur exactement les 50 premiers tweets
    
    Cette fonction limite le traitement aux 50 premiers tweets du dataset
    pour une analyse rapide. Chaque tweet est classifié selon plusieurs
    dimensions: réclamation, topics, sentiment, urgence, incident, confidence.
    
    Args:
        df: DataFrame contenant les tweets à classifier
        text_column: Nom de la colonne contenant le texte
        
    Returns:
        tuple: (df_classified, metrics) ou (None, None) en cas d'erreur
    """
    # Barre de progression
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # ============================================================
        # LIMITATION À 50 TWEETS - Requirement Principal
        # ============================================================
        TWEETS_LIMIT = 50
        total_in_file = len(df)
        df_to_classify = df.head(TWEETS_LIMIT).copy()
        total_tweets = len(df_to_classify)
        
        # Information utilisateur
        if total_in_file > TWEETS_LIMIT:
            st.info(f"**Analyse limitee:** Traitement des **{TWEETS_LIMIT} premiers tweets** sur {total_in_file:,} disponibles dans le fichier.")
        else:
            st.info(f"**Analyse complete:** Traitement des **{total_tweets} tweets** du fichier.")
        
        # Classification
        status_text.text(f"Classification des {total_tweets} tweets en cours...")
        progress_bar.progress(0.2)
        
        results = []
        for i, text in enumerate(df_to_classify[text_column], 1):
            result = _classify_single_tweet(str(text))
            results.append(result)
            
            # Mise à jour tous les 10 tweets
            if i % 10 == 0 or i == total_tweets:
                progress = 0.2 + (i / total_tweets) * 0.6
                progress_bar.progress(min(progress, 0.8))
                status_text.text(f"Classification: {i}/{total_tweets} tweets ({i/total_tweets*100:.0f}%)")
        
        # Enrichissement du dataset
        status_text.text("Enrichissement des donnees...")
        progress_bar.progress(0.85)
        
        df_classified = df_to_classify.copy()
        df_classified['is_claim'] = [r['is_claim'] for r in results]
        df_classified['topics'] = [r['topics'] for r in results]
        df_classified['sentiment'] = [r['sentiment'] for r in results]
        df_classified['urgence'] = [r['urgence'] for r in results]
        df_classified['incident'] = [r['incident'] for r in results]
        df_classified['confidence'] = [r['confidence'] for r in results]
        
        # Calcul des métriques
        status_text.text("Calcul des metriques...")
        progress_bar.progress(0.95)
        
        metrics = _calculate_classification_metrics(df_classified)
        
        # Finalisation
        progress_bar.progress(1.0)
        status_text.empty()
        progress_bar.empty()
        
        # Message de succès
        st.success(f"""
        **Classification terminee avec succes!**
        - **{total_tweets} tweets** classifies
        - **{metrics['claims']} reclamations** detectees ({metrics['claims_percentage']:.1f}%)
        - **Confiance moyenne:** {metrics['avg_confidence']:.1%}
        """)
        
        return df_classified, metrics
        
    except Exception as e:
        st.error(f"Erreur lors de la classification: {str(e)}")
        logger.error(f"Error during classification: {str(e)}", exc_info=True)
        return None, None

def _classify_single_tweet(tweet: str) -> Dict[str, Any]:
    """Classifie un tweet unique avec le système basé sur des règles"""
    
    tweet_lower = tweet.lower()
    
    # Détection de réclamation
    claim_keywords = ['panne', 'problème', 'bug', 'erreur', '@free', '@freebox', 'ne fonctionne pas', 'dysfonctionnement']
    is_claim = 1 if any(w in tweet_lower for w in claim_keywords) else 0
    
    # Détection des topics
    topics = []
    if any(w in tweet_lower for w in ['fibre', 'ftth']): topics.append('fibre')
    if any(w in tweet_lower for w in ['adsl', 'dsl']): topics.append('dsl')
    if 'wifi' in tweet_lower or 'wi-fi' in tweet_lower: topics.append('wifi')
    if any(w in tweet_lower for w in ['tv', 'télévision', 'freebox']): topics.append('tv')
    if any(w in tweet_lower for w in ['mobile', 'forfait', '4g', '5g']): topics.append('mobile')
    if any(w in tweet_lower for w in ['facture', 'facturation', 'paiement']): topics.append('facture')
    if 'activation' in tweet_lower: topics.append('activation')
    if any(w in tweet_lower for w in ['résiliation', 'resilier']): topics.append('resiliation')
    if not topics: topics = ['autre']
    
    # Analyse de sentiment
    positive_words = ['merci', 'super', 'génial', 'parfait', 'excellent', 'bravo', 'top']
    negative_words = ['panne', 'nul', 'bug', 'problème', 'mauvais', 'honte', 'scandale', 'incompétent']
    
    if any(w in tweet_lower for w in positive_words): sentiment = 'pos'
    elif any(w in tweet_lower for w in negative_words): sentiment = 'neg'
    else: sentiment = 'neu'
    
    # Détection d'urgence
    urgency_keywords = ['urgent', 'immédiat', 'critique', 'grave']
    if any(w in tweet_lower for w in urgency_keywords) or 'panne' in tweet_lower: urgence = 'haute'
    elif is_claim: urgence = 'moyenne'
    else: urgence = 'basse'
    
    # Type d'incident
    if any(w in tweet_lower for w in ['facture', 'facturation', 'paiement']): incident = 'facturation'
    elif any(w in tweet_lower for w in ['panne', 'coupure', 'déconnexion']): incident = 'incident_reseau'
    elif any(w in tweet_lower for w in ['livraison', 'box', 'colis']): incident = 'livraison'
    elif any(w in tweet_lower for w in ['service client', 'sav', 'réponse']): incident = 'processus_sav'
    elif is_claim: incident = 'autre'
    else: incident = 'information'
    
    # Score de confiance basé sur des critères réels
    # Calcul d'un score de confiance basé sur la clarté des indicateurs
    confidence_factors = []
    
    # Facteur 1: Détection claire de réclamation
    if is_claim and any(w in tweet_lower for w in ['panne', 'bug', 'erreur']):
        confidence_factors.append(0.95)
    elif is_claim:
        confidence_factors.append(0.80)
    else:
        confidence_factors.append(0.85)
    
    # Facteur 2: Clarté du sentiment
    strong_positive = ['merci', 'excellent', 'parfait', 'bravo']
    strong_negative = ['nul', 'honte', 'scandale', 'incompétent']
    if any(w in tweet_lower for w in strong_positive + strong_negative):
        confidence_factors.append(0.92)
    else:
        confidence_factors.append(0.78)
    
    # Facteur 3: Spécificité du topic
    if len(topics) == 1 and topics[0] != 'autre':
        confidence_factors.append(0.90)
    elif len(topics) > 1:
        confidence_factors.append(0.85)
    else:
        confidence_factors.append(0.70)
    
    # Calcul de la confiance moyenne
    confidence = sum(confidence_factors) / len(confidence_factors)
    confidence = min(0.98, max(0.65, confidence))  # Borner entre 0.65 et 0.98
    
    return {
        'is_claim': is_claim,
        'topics': topics,
        'sentiment': sentiment,
        'urgence': urgence,
        'incident': incident,
        'confidence': round(confidence, 2)
    }

def _prepare_df_for_business_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prépare le DataFrame pour les KPIs business en convertissant les formats
    
    Convertit les colonnes du format Classification LLM vers le format attendu
    par le module enhanced_kpis_vizualizations:
    - sentiment: 'pos'/'neu'/'neg' → 'positive'/'neutral'/'negative'
    - urgence: 'haute'/'moyenne'/'basse' → priority: 'haute'/'moyenne'/'basse'
    - incident → category
    - topics → conservé tel quel
    
    Args:
        df: DataFrame classifié au format LLM
        
    Returns:
        DataFrame au format compatible avec KPIs business
    """
    # Créer une copie pour ne pas modifier l'original
    df_converted = df.copy()
    
    # Conversion du sentiment (pos/neu/neg → positive/neutral/negative)
    sentiment_mapping = {
        'pos': 'positive',
        'neu': 'neutral',
        'neg': 'negative',
        'positif': 'positive',
        'neutre': 'neutral',
        'negatif': 'negative'
    }
    
    # Appliquer la conversion sur la colonne sentiment
    if 'sentiment' in df_converted.columns:
        df_converted['sentiment'] = df_converted['sentiment'].map(
            lambda x: sentiment_mapping.get(str(x).lower(), str(x))
        )
    
    # Renommer urgence en priority si nécessaire
    if 'urgence' in df_converted.columns and 'priority' not in df_converted.columns:
        df_converted['priority'] = df_converted['urgence']
    
    # Renommer incident en category si nécessaire
    if 'incident' in df_converted.columns and 'category' not in df_converted.columns:
        df_converted['category'] = df_converted['incident']
    
    # S'assurer que is_claim est numérique (pour le calcul du taux)
    if 'is_claim' in df_converted.columns:
        df_converted['is_claim'] = df_converted['is_claim'].astype(int)
    
    # Retourner le DataFrame converti
    return df_converted


def _calculate_classification_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calcule les métriques de classification détaillées pour les 50 tweets
    
    Cette fonction agrège toutes les statistiques de classification
    incluant comptages, pourcentages et distributions pour tous les indicateurs.
    
    Args:
        df: DataFrame classifié avec colonnes is_claim, sentiment, urgence, etc.
        
    Returns:
        Dictionnaire contenant toutes les métriques calculées
    """
    # Calcul du nombre total de tweets
    total_tweets = len(df)
    
    # ==============================================================
    # 1. RÉCLAMATIONS (is_claim) - Comptage + Pourcentage
    # ==============================================================
    claims = df['is_claim'].sum()
    claims_percentage = (claims / total_tweets * 100) if total_tweets > 0 else 0
    non_claims = total_tweets - claims
    non_claims_percentage = 100 - claims_percentage
    
    # ==============================================================
    # 2. TOPICS (fibre, mobile, facture) - Comptages détaillés
    # ==============================================================
    # Topics (flatten list of lists)
    all_topics = [topic for topics in df['topics'] for topic in topics]
    topic_dist = pd.Series(all_topics).value_counts()
    
    # Comptages spécifiques pour les 3 topics principaux
    topic_fibre = sum(1 for topics in df['topics'] if 'fibre' in topics)
    topic_mobile = sum(1 for topics in df['topics'] if 'mobile' in topics)
    topic_facture = sum(1 for topics in df['topics'] if 'facture' in topics)
    
    # ==============================================================
    # 3. SENTIMENT (positif, neutre, négatif) - Comptages
    # ==============================================================
    sentiment_dist = df['sentiment'].value_counts()
    sentiment_positive = len(df[df['sentiment'] == 'pos'])
    sentiment_neutral = len(df[df['sentiment'] == 'neu'])
    sentiment_negative = len(df[df['sentiment'] == 'neg'])
    
    # ==============================================================
    # 4. URGENCE (haute, moyenne, basse) - Comptages
    # ==============================================================
    urgence_dist = df['urgence'].value_counts()
    urgence_haute = len(df[df['urgence'] == 'haute'])
    urgence_moyenne = len(df[df['urgence'] == 'moyenne'])
    urgence_basse = len(df[df['urgence'] == 'basse'])
    
    # ==============================================================
    # 5. INCIDENT - Distribution
    # ==============================================================
    incident_dist = df['incident'].value_counts()
    
    # ==============================================================
    # 6. CONFIDENCE - Statistiques
    # ==============================================================
    avg_confidence = df['confidence'].mean()
    min_confidence = df['confidence'].min()
    max_confidence = df['confidence'].max()
    
    return {
        # Métriques générales
        'total_tweets': total_tweets,
        
        # 1. Réclamations (AVEC pourcentage)
        'claims': int(claims),
        'claims_percentage': claims_percentage,
        'non_claims': non_claims,
        'non_claims_percentage': non_claims_percentage,
        
        # 2. Topics
        'topic_fibre': topic_fibre,
        'topic_mobile': topic_mobile,
        'topic_facture': topic_facture,
        'topic_dist': topic_dist,
        
        # 3. Sentiments
        'sentiment_positive': sentiment_positive,
        'sentiment_neutral': sentiment_neutral,
        'sentiment_negative': sentiment_negative,
        'sentiment_dist': sentiment_dist,
        'negative_sentiments': sentiment_negative,  # Pour compatibilité
        
        # 4. Urgences
        'urgence_haute': urgence_haute,
        'urgence_moyenne': urgence_moyenne,
        'urgence_basse': urgence_basse,
        'urgence_dist': urgence_dist,
        'high_urgency': urgence_haute,  # Pour compatibilité
        
        # 5. Incidents
        'incident_dist': incident_dist,
        
        # 6. Confidence
        'avg_confidence': avg_confidence,
        'min_confidence': min_confidence,
        'max_confidence': max_confidence
    }

def _display_detailed_visualizations_50_tweets(df: pd.DataFrame, metrics: Dict[str, Any]):
    """
    Affiche les visualisations détaillées pour les 50 tweets classifiés
    
    Crée 6 visualisations principales dynamiques:
    1. Détection de réclamations (is_claim) - Donut avec comptage + pourcentage
    2. Distribution des topics (fibre, mobile, facture) - Bar chart
    3. Distribution des sentiments (positif, neutre, négatif) - Donut
    4. Distribution de l'urgence (haute, moyenne, basse) - Bar horizontal
    5. Distribution des incidents - Pie chart
    6. Score de confiance - Histogram avec ligne moyenne
    
    Args:
        df: DataFrame classifié
        metrics: Dictionnaire des métriques
    """
    st.markdown("---")
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 12px; margin: 1.5rem 0; text-align: center;
                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);">
        <h2 style="color: white; margin: 0; font-size: 2rem; font-weight: 700;">
            <i class="fas fa-chart-bar" style="margin-right: 0.75rem;"></i>
            Analyse Detaillee des Classifications
        </h2>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.1rem;">
            Visualisations interactives des {0} tweets analyses
        </p>
    </div>
    """.format(metrics['total_tweets']), unsafe_allow_html=True)
    
    # ROW 1: Réclamations + Topics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### <i class='fas fa-exclamation-circle'></i> Detection de Reclamations", unsafe_allow_html=True)
        fig_claims = go.Figure(data=[go.Pie(
            labels=['Réclamations', 'Non-réclamations'],
            values=[metrics['claims'], metrics['non_claims']],
            hole=0.4,
            marker=dict(colors=['#CC0000', '#48bb78']),
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>Comptage: %{value}<br>Pourcentage: %{percent}<extra></extra>'
        )])
        fig_claims.update_layout(
            showlegend=True,
            height=350,
            margin=dict(t=10, b=10, l=10, r=10),
            annotations=[dict(
                text=f'<b>{metrics["claims"]}</b><br><span style="font-size:0.9em">{metrics["claims_percentage"]:.1f}%</span>',
                x=0.5, y=0.5, font_size=16, showarrow=False
            )]
        )
        st.plotly_chart(fig_claims, use_container_width=True, key='viz_claims_donut')
        st.caption(f"**Info:** {metrics['claims']} reclamations sur {metrics['total_tweets']} tweets ({metrics['claims_percentage']:.1f}%)")
    
    with col2:
        st.markdown("#### <i class='fas fa-tags'></i> Topics Detectes", unsafe_allow_html=True)
        topics_df = pd.DataFrame({
            'Topic': ['Fibre', 'Mobile', 'Facture'],
            'Comptage': [
                metrics['topic_fibre'],
                metrics['topic_mobile'],
                metrics['topic_facture']
            ]
        })
        fig_topics = px.bar(
            topics_df,
            x='Topic',
            y='Comptage',
            color='Topic',
            color_discrete_map={'Fibre': '#667eea', 'Mobile': '#f6ad55', 'Facture': '#48bb78'},
            text='Comptage'
        )
        fig_topics.update_traces(texttemplate='%{text}', textposition='outside')
        fig_topics.update_layout(
            showlegend=False,
            height=350,
            xaxis_title='',
            yaxis_title='Nombre de tweets',
            margin=dict(t=10, b=10, l=10, r=10)
        )
        st.plotly_chart(fig_topics, use_container_width=True, key='viz_topics_bar')
        total_topics_count = metrics['topic_fibre'] + metrics['topic_mobile'] + metrics['topic_facture']
        st.caption(f"**Info:** {total_topics_count} topics identifies (un tweet peut avoir plusieurs topics)")
    
    # ROW 2: Sentiment + Urgence
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("#### <i class='fas fa-smile'></i> Distribution des Sentiments", unsafe_allow_html=True)
        sentiment_df = pd.DataFrame({
            'Sentiment': ['Positif', 'Neutre', 'Négatif'],
            'Comptage': [
                metrics['sentiment_positive'],
                metrics['sentiment_neutral'],
                metrics['sentiment_negative']
            ]
        })
        fig_sentiment = go.Figure(data=[go.Pie(
            labels=sentiment_df['Sentiment'],
            values=sentiment_df['Comptage'],
            hole=0.5,
            marker=dict(colors=['#48bb78', '#90cdf4', '#fc8181']),
            textinfo='label+value',
            hovertemplate='<b>%{label}</b><br>%{value} tweets<br>%{percent}<extra></extra>'
        )])
        fig_sentiment.update_layout(
            showlegend=True,
            height=350,
            margin=dict(t=10, b=10, l=10, r=10)
        )
        st.plotly_chart(fig_sentiment, use_container_width=True, key='viz_sentiment_donut')
        dominant = sentiment_df.loc[sentiment_df['Comptage'].idxmax(), 'Sentiment']
        st.caption(f"**Info:** Sentiment dominant: {dominant} ({sentiment_df['Comptage'].max()} tweets)")
    
    with col4:
        st.markdown("#### <i class='fas fa-bolt'></i> Niveaux d'Urgence", unsafe_allow_html=True)
        urgence_df = pd.DataFrame({
            'Urgence': ['Haute', 'Moyenne', 'Basse'],
            'Comptage': [
                metrics['urgence_haute'],
                metrics['urgence_moyenne'],
                metrics['urgence_basse']
            ]
        })
        fig_urgence = px.bar(
            urgence_df,
            y='Urgence',
            x='Comptage',
            orientation='h',
            color='Urgence',
            color_discrete_map={'Haute': '#e53e3e', 'Moyenne': '#dd6b20', 'Basse': '#48bb78'},
            text='Comptage'
        )
        fig_urgence.update_traces(texttemplate='%{text}', textposition='outside')
        fig_urgence.update_layout(
            showlegend=False,
            height=350,
            xaxis_title='Nombre de tweets',
            yaxis_title='',
            margin=dict(t=10, b=10, l=10, r=10)
        )
        st.plotly_chart(fig_urgence, use_container_width=True, key='viz_urgence_bar')
        urgent_pct = (metrics['urgence_haute'] / metrics['total_tweets'] * 100)
        st.caption(f"**Info:** Tweets urgents: {metrics['urgence_haute']} ({urgent_pct:.1f}%)")
    
    # ROW 3: Incident + Confiance
    col5, col6 = st.columns(2)
    
    with col5:
        st.markdown("#### <i class='fas fa-tools'></i> Types d'Incidents", unsafe_allow_html=True)
        if 'incident_dist' in metrics and not metrics['incident_dist'].empty:
            incident_df = pd.DataFrame({
                'Type': metrics['incident_dist'].index,
                'Comptage': metrics['incident_dist'].values
            })
            fig_incident = px.pie(
                incident_df,
                names='Type',
                values='Comptage',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_incident.update_traces(
                textinfo='label+value',
                hovertemplate='<b>%{label}</b><br>%{value} tweets<br>%{percent}<extra></extra>'
            )
            fig_incident.update_layout(
                showlegend=True,
                height=350,
                margin=dict(t=10, b=10, l=10, r=10)
            )
            st.plotly_chart(fig_incident, use_container_width=True, key='viz_incident_pie')
            top_incident = incident_df.loc[incident_df['Comptage'].idxmax(), 'Type']
            st.caption(f"**Info:** Incident principal: {top_incident}")
        else:
            st.warning("Aucune donnee d'incident disponible")
    
    with col6:
        st.markdown("#### <i class='fas fa-check-circle'></i> Score de Confiance", unsafe_allow_html=True)
        fig_confidence = px.histogram(
            df,
            x='confidence',
            nbins=20,
            color_discrete_sequence=['#667eea'],
            labels={'confidence': 'Score de Confiance', 'count': 'Fréquence'}
        )
        fig_confidence.add_vline(
            x=metrics['avg_confidence'],
            line_dash="dash",
            line_color="#CC0000",
            annotation_text=f"Moyenne: {metrics['avg_confidence']:.2f}",
            annotation_position="top"
        )
        fig_confidence.update_layout(
            showlegend=False,
            height=350,
            xaxis_title='Score de Confiance (0-1)',
            yaxis_title='Nombre de tweets',
            margin=dict(t=10, b=10, l=10, r=10)
        )
        st.plotly_chart(fig_confidence, use_container_width=True, key='viz_confidence_hist')
        st.caption(f"**Info:** Confiance: {metrics['avg_confidence']:.2f} (min: {metrics['min_confidence']:.2f}, max: {metrics['max_confidence']:.2f})")

def _display_classification_results(df: pd.DataFrame, metrics: Dict[str, Any]):
    """Affiche les résultats de classification avec visualisations professionnelles"""
    
    st.markdown("---")
    st.markdown("## <i class='fas fa-chart-pie'></i> Résultats de Classification", unsafe_allow_html=True)
    
    # KPI Cards - 4 cartes professionnelles
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <i class="fas fa-exclamation-circle" style="color: #CC0000; font-size: 2rem;"></i>
            <div style="font-size: 2rem; font-weight: 700; margin-top: 0.5rem;">{metrics['claims']}</div>
            <div style="font-size: 0.9rem; color: #666; margin-top: 0.25rem;">Réclamations</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <i class="fas fa-check-circle" style="color: #38a169; font-size: 2rem;"></i>
            <div style="font-size: 2rem; font-weight: 700; margin-top: 0.5rem;">{metrics['avg_confidence']:.0%}</div>
            <div style="font-size: 0.9rem; color: #666; margin-top: 0.25rem;">Confiance Moyenne</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <i class="fas fa-frown" style="color: #e53e3e; font-size: 2rem;"></i>
            <div style="font-size: 2rem; font-weight: 700; margin-top: 0.5rem;">{metrics['negative_sentiments']}</div>
            <div style="font-size: 0.9rem; color: #666; margin-top: 0.25rem;">Sentiments Négatifs</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <i class="fas fa-bolt" style="color: #dd6b20; font-size: 2rem;"></i>
            <div style="font-size: 2rem; font-weight: 700; margin-top: 0.5rem;">{metrics['high_urgency']}</div>
            <div style="font-size: 0.9rem; color: #666; margin-top: 0.25rem;">Urgence Haute</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ==================================================================
    # SECTION: VISUALISATIONS DÉTAILLÉES DES 50 TWEETS
    # ==================================================================
    # Affichage des 6 graphiques pour analyser les 50 tweets classifiés
    # ==================================================================
    
    _display_detailed_visualizations_50_tweets(df, metrics)
    
    # ==================================================================
    # SECTION: TABLEAU DE BORD BUSINESS (NOUVEAUX KPIs)
    # ==================================================================
    # Cette section affiche les nouveaux KPIs business et visualisations avancées
    # Elle utilise le module enhanced_kpis_vizualizations.py
    # ==================================================================
    
    if ENHANCED_KPIS_AVAILABLE:
        # Séparateur visuel avant le dashboard business
        st.markdown("---")
        
        # Header moderne et professionnel du dashboard business
        # Utilise le gradient rouge Free Mobile pour coherence visuelle avec Page 1
        st.markdown("""
        <div style="background: linear-gradient(135deg, #CC0000 0%, #8B0000 100%); 
                    padding: 2.5rem 2rem; border-radius: 12px; margin: 2rem 0; text-align: center;
                    box-shadow: 0 10px 30px rgba(204, 0, 0, 0.3);">
            <h2 style="color: white; margin: 0; font-size: 2.2rem; font-weight: 800; letter-spacing: -0.5px;">
                <i class="fas fa-chart-line" style="margin-right: 1rem; font-size: 2rem;"></i>
                TABLEAU DE BORD BUSINESS
            </h2>
            <p style="color: rgba(255,255,255,0.95); margin: 1rem 0 0 0; font-size: 1.1rem; font-weight: 400;">
                Indicateurs cles de performance et analyses avancees
            </p>
            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.2);">
                <span style="color: rgba(255,255,255,0.85); font-size: 0.9rem;">
                    Donnees calculees en temps reel sur le dataset actuel
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ================================================================
        # CALCUL DYNAMIQUE DES KPIs BUSINESS
        # ================================================================
        # IMPORTANT: Les KPIs sont TOUJOURS recalcules à partir du DataFrame
        # actuel (df). Aucun cache n'est utilise. Chaque nouveau fichier
        # uploadé génère de nouveaux KPIs basés sur ses propres données.
        # ================================================================
        
        # Preparer le DataFrame au format attendu par les KPIs business
        # Conversion DYNAMIQUE du format LLM (pos/neu/neg) vers format business (positive/neutral/negative)
        df_for_business = _prepare_df_for_business_kpis(df)
        
        # Obtenir le role actuel pour filtrage
        display_role = get_current_role() if ROLE_SELECTOR_AVAILABLE else "Data Analyst"
        
        # Filtrer le DataFrame selon le role (si applicable)
        if ROLE_SELECTOR_AVAILABLE:
            # Appliquer le filtre de role sur les donnees
            df_for_business = filter_dataframe_by_role(df_for_business, display_role)
            
            # Afficher un message personnalise selon le role
            role_message = get_dashboard_message_by_role(display_role)
            if role_message:
                st.markdown(role_message, unsafe_allow_html=True)
        
        # Calculer les KPIs business DYNAMIQUEMENT sur les donnees actuelles
        # Cette fonction recalcule TOUT (pas de cache) à partir de df_for_business
        business_kpis = compute_business_kpis(df_for_business)
        
        # Filtrer les KPIs selon le role
        if ROLE_SELECTOR_AVAILABLE:
            business_kpis = filter_kpis_by_role(business_kpis, display_role)
        
        # Rendre le dashboard avec KPIs filtres selon le role
        render_business_kpis(business_kpis)
        
        # Rendre les visualisations (affichees pour tous les roles)
        # Appel de la fonction depuis le module importe
        enhanced_kpis_vizualizations.render_enhanced_visualizations(df_for_business, business_kpis)
        
        # Section insights (visible pour tous les roles)
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; margin: 1.5rem 0 1rem 0;">
            <h3 style="font-size: 1.5rem; font-weight: 700; color: #1a202c; margin: 0;">
                <i class="fas fa-lightbulb" style="color: #CC0000; margin-right: 0.75rem;"></i>
                Synthese Business
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Affichage des insights en 3 colonnes
        insights_col1, insights_col2, insights_col3 = st.columns(3)
        
        with insights_col1:
            st.info(f"**Volume Total**: {len(df_for_business):,} tweets analyses")
        
        with insights_col2:
            if 'satisfaction_index' in business_kpis:
                satisfaction = business_kpis['satisfaction_index']['value']
                if satisfaction > 60:
                    st.success(f"**Satisfaction**: Positive ({satisfaction:.0f}/100)")
                elif satisfaction > 40:
                    st.warning(f"**Satisfaction**: Neutre ({satisfaction:.0f}/100)")
                else:
                    st.error(f"**Satisfaction**: Negative ({satisfaction:.0f}/100)")
        
        with insights_col3:
            if 'urgency_rate' in business_kpis:
                urgency = business_kpis['urgency_rate']['urgency_pct']
                if urgency > 20:
                    st.error(f"**Urgence**: Elevee ({urgency:.1f}%)")
                elif urgency > 10:
                    st.warning(f"**Urgence**: Moderee ({urgency:.1f}%)")
                else:
                    st.success(f"**Urgence**: Faible ({urgency:.1f}%)")
        
        # Séparateur après le dashboard
        st.markdown("---")
    
    # 3 Tabs de visualisation (anciennes visualisations - retrocompatibilite)
    tab1, tab2, tab3 = st.tabs(["Distribution", "Analyse", "Details"])
    
    with tab1:
        st.markdown("### Distribution des Classifications")
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart - Distribution des incidents
            # Ensure consistent rendering to prevent DOM issues
            try:
                if not metrics['incident_dist'].empty:
                    fig_incident = px.pie(
                        values=metrics['incident_dist'].values,
                        names=metrics['incident_dist'].index,
                        title="<b>Répartition par Type d'Incident</b>",
                        color_discrete_sequence=px.colors.sequential.Reds
                    )
                    fig_incident.update_traces(textposition='inside', textinfo='percent+label')
                    fig_incident.update_layout(title_font_size=16, showlegend=True)
                    st.plotly_chart(fig_incident, use_container_width=True)
                else:
                    st.info("Aucune donnée d'incident disponible")
            except Exception as e:
                st.warning("Impossible d'afficher le graphique des incidents")
                logger.warning(f"Error rendering incident chart: {e}")
        
        with col2:
            # Bar chart - Fréquence des topics
            # Ensure consistent rendering to prevent DOM issues
            try:
                if not metrics['topic_dist'].empty:
                    fig_topics = px.bar(
                        x=metrics['topic_dist'].index,
                        y=metrics['topic_dist'].values,
                        title="<b>Fréquence par Topic</b>",
                        color=metrics['topic_dist'].values,
                        color_continuous_scale='Reds',
                        labels={'x': 'Topic', 'y': 'Nombre'}
                    )
                    fig_topics.update_layout(title_font_size=16, showlegend=False)
                    st.plotly_chart(fig_topics, use_container_width=True)
                else:
                    st.info("Aucune donnée de topic disponible")
            except Exception as e:
                st.warning("Impossible d'afficher le graphique des topics")
                logger.warning(f"Error rendering topics chart: {e}")
    
    with tab2:
        st.markdown("### Analyse Détaillée")
        col1, col2 = st.columns(2)
        
        with col1:
            # Sentiment avec couleurs sémantiques
            # Ensure consistent rendering to prevent DOM issues
            try:
                if not metrics['sentiment_dist'].empty:
                    fig_sentiment = px.bar(
                        x=metrics['sentiment_dist'].index,
                        y=metrics['sentiment_dist'].values,
                        title="<b>Distribution des Sentiments</b>",
                        color=metrics['sentiment_dist'].index,
                        color_discrete_map={
                            'pos': '#38a169',
                            'neu': '#3182ce',
                            'neg': '#e53e3e'
                        },
                        labels={'x': 'Sentiment', 'y': 'Nombre'}
                    )
                    fig_sentiment.update_layout(title_font_size=16, showlegend=False)
                    st.plotly_chart(fig_sentiment, use_container_width=True)
                else:
                    st.info("Aucune donnée de sentiment disponible")
            except Exception as e:
                st.warning("Impossible d'afficher le graphique des sentiments")
                logger.warning(f"Error rendering sentiment chart: {e}")
        
        with col2:
            # Urgence avec niveaux de priorité
            # Ensure consistent rendering to prevent DOM issues
            try:
                if not metrics['urgence_dist'].empty:
                    fig_urgence = px.bar(
                        x=metrics['urgence_dist'].index,
                        y=metrics['urgence_dist'].values,
                        title="<b>Répartition par Urgence</b>",
                        color=metrics['urgence_dist'].values,
                        color_continuous_scale='Oranges',
                        labels={'x': 'Urgence', 'y': 'Nombre'}
                    )
                    fig_urgence.update_layout(title_font_size=16, showlegend=False)
                    st.plotly_chart(fig_urgence, use_container_width=True)
                else:
                    st.info("Aucune donnée d'urgence disponible")
            except Exception as e:
                st.warning("Impossible d'afficher le graphique d'urgence")
                logger.warning(f"Error rendering urgency chart: {e}")
    
    with tab3:
        st.markdown("### <i class='fas fa-table'></i> Tableau Détaillé Interactif", unsafe_allow_html=True)
        
        # Préparation du DataFrame pour l'affichage
        display_df = df.copy()
        display_df['topics'] = display_df['topics'].apply(lambda x: ', '.join(x))
        display_df['confidence'] = display_df['confidence'].apply(lambda x: f"{x:.0%}")
        
        # Filtres interactifs
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_sentiment = st.multiselect(
                "Filtrer par sentiment:",
                options=['pos', 'neu', 'neg'],
                default=['pos', 'neu', 'neg']
            )
        
        with col2:
            filter_urgence = st.multiselect(
                "Filtrer par urgence:",
                options=display_df['urgence'].unique().tolist(),
                default=display_df['urgence'].unique().tolist()
            )
        
        with col3:
            filter_claim = st.selectbox(
                "Type:",
                options=["Tous", "Réclamations", "Non-réclamations"]
            )
        
        # Application des filtres
        filtered_display = display_df[
            (display_df['sentiment'].isin(filter_sentiment)) &
            (display_df['urgence'].isin(filter_urgence))
        ]
        
        if filter_claim == "Réclamations":
            filtered_display = filtered_display[filtered_display['is_claim'] == 1]
        elif filter_claim == "Non-réclamations":
            filtered_display = filtered_display[filtered_display['is_claim'] == 0]
        
        st.info(f"**{len(filtered_display)} tweets** affichés sur {len(df)} total")
        
        # Affichage du tableau avec tri et pagination
        st.dataframe(
            filtered_display,
            use_container_width=True,
            height=400,
            hide_index=True
        )
    
    # Export des résultats
    st.markdown("---")
    st.markdown("### <i class='fas fa-download'></i> Export des Résultats", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Export CSV
        export_df = df.copy()
        export_df['topics'] = export_df['topics'].apply(lambda x: ', '.join(x))
        csv_data = export_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="Télécharger CSV",
            data=csv_data,
            file_name=f"classification_llm_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # Export JSON des métriques
        metrics_json = {
            'total_tweets': metrics['total_tweets'],
            'claims': metrics['claims'],
            'avg_confidence': float(metrics['avg_confidence']),
            'negative_sentiments': metrics['negative_sentiments'],
            'high_urgency': metrics['high_urgency'],
            'distributions': {
                'incidents': metrics['incident_dist'].to_dict(),
                'sentiments': metrics['sentiment_dist'].to_dict(),
                'urgence': metrics['urgence_dist'].to_dict(),
                'topics': metrics['topic_dist'].to_dict()
            }
        }
        json_data = json.dumps(metrics_json, ensure_ascii=False, indent=2)
        st.download_button(
            label="Télécharger JSON",
            data=json_data,
            file_name=f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col3:
        # Nouvelle analyse
        if st.button("Nouvelle Analyse", type="primary", use_container_width=True):
            # Clear session state to start fresh
            keys_to_clear = ['preprocessed_dataframe', 'preprocessing_stats', 'classified_dataframe', 'classification_metrics']
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            
            # Instead of rerun, we'll show a message and let the user upload a new file
            st.info("Veuillez uploader un nouveau fichier pour commencer une nouvelle analyse")
            # Reset the file uploader by clearing the uploaded file
            st.session_state.pop('uploaded_file', None)



if __name__ == "__main__":
    main()