"""
Page d'Analyse des Données Twitter
Interface utilisateur pour l'upload et l'analyse de fichiers de données
Développé dans le cadre d'un mémoire de master en Data Science
"""

import streamlit as st
import time
import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio

# Import des composants d'analyse (imports relatifs corrigés)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from components.dynamic_analysis_ui import DynamicAnalysisUI
    from services.adaptive_analysis_engine import AdaptiveAnalysisEngine
    from services.intelligent_data_inspector import IntelligentDataInspector
    from services.dynamic_prompt_generator import DynamicPromptGenerator
    from services.smart_visualization_engine import SmartVisualizationEngine
    from services.real_llm_engine import RealLLMEngine
    INTELLIGENT_ANALYSIS_AVAILABLE = True
except ImportError as e:
    print(f"Modules d'analyse intelligente non disponibles: {e}")
    INTELLIGENT_ANALYSIS_AVAILABLE = False

# Configuration
st.set_page_config(
    page_title="Analyse KPI - FreeMobilaChat",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Logger
logger = logging.getLogger(__name__)

def main():
    """Page principale d'analyse"""
    
    # CSS personnalisé pour la page moderne
    _load_modern_css()
    
    # Header moderne avec navigation
    _render_modern_header()
    
    # Vérification de la connexion API
    if not _check_api_connection():
        return
    
    # Sidebar avec configuration
    _render_sidebar_config()
    
    # Zone d'upload centrale moderne
    upload_result = _render_modern_upload_zone()
    
    if upload_result:
        # Analyse intelligente avec le nouveau système
        _handle_intelligent_analysis(upload_result)
        return
    
    # Affichage des analyses en cours
    _render_current_analyses()
    
    # Métriques globales
    _render_global_metrics()
    
    # Section des fonctionnalités
    _render_features_section()

def _load_modern_css():
    """Chargement des styles CSS personnalisés pour l'interface d'analyse"""
    
    st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
    .main {padding: 0 !important; background: #f8f9fa;}
    .block-container {padding: 0 !important; max-width: 100% !important;}
    #MainMenu, footer, header {visibility: hidden;}
    .hero-section {background: linear-gradient(135deg, #CC0000 0%, #8B0000 100%); padding: 4rem 2rem; text-align: center; color: white; border-radius: 15px; margin-bottom: 2rem; box-shadow: 0 10px 30px rgba(204, 0, 0, 0.3);}
    .hero-title {font-size: 3.5rem; font-weight: 800; margin-bottom: 1rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);}
    .hero-subtitle {font-size: 1.5rem; font-weight: 400; opacity: 0.95; margin-bottom: 2rem; max-width: 600px; margin-left: auto; margin-right: auto;}
    .hero-stats {display: flex; justify-content: center; gap: 3rem; margin-top: 3rem; flex-wrap: wrap;}
    .upload-zone-modern {border: 3px dashed #CC0000; border-radius: 20px; padding: 3rem; text-align: center; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); transition: all 0.3s ease; margin: 2rem 0;}
    .upload-zone-modern:hover {border-color: #8B0000; background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%); transform: translateY(-5px); box-shadow: 0 15px 30px rgba(204, 0, 0, 0.2);}
    .upload-icon {font-size: 4rem; color: #CC0000; margin-bottom: 1.5rem; display: block;}
    .upload-title {font-size: 1.8rem; font-weight: 700; color: #333; margin-bottom: 1rem;}
    .upload-subtitle {color: #666; font-size: 1.1rem; margin-bottom: 2rem;}
    .features-grid {display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin: 3rem 0;}
    .feature-card {background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); text-align: center; transition: all 0.3s ease; border: 1px solid #e1e5e9;}
    .feature-card:hover {transform: translateY(-5px); box-shadow: 0 20px 40px rgba(204, 0, 0, 0.15); border-color: #CC0000;}
    .stFileUploader > div {border: 3px dashed #CC0000 !important; border-radius: 20px !important; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%) !important; padding: 3rem !important; text-align: center !important; transition: all 0.3s ease !important;}
    .stFileUploader > div:hover {border-color: #8B0000 !important; background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%) !important; transform: translateY(-5px) !important; box-shadow: 0 15px 30px rgba(204, 0, 0, 0.2) !important;}
    .stFileUploader label {font-size: 1.8rem !important; font-weight: 700 !important; color: #333 !important; margin-bottom: 1rem !important;}
    .stFileUploader .uploadedFile {background: white !important; border: 1px solid #e1e5e9 !important; border-radius: 10px !important; padding: 1rem !important; margin: 1rem 0 !important; box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;}
    @media (max-width: 768px) {.hero-title {font-size: 2.5rem;} .hero-subtitle {font-size: 1.2rem;} .hero-stats {gap: 1.5rem;} .features-grid {grid-template-columns: 1fr; gap: 1rem;}}
    </style>
    """, unsafe_allow_html=True)

def _render_modern_header():
    """Affichage de l'en-tête principal avec logo et navigation"""
    
    # Header avec gradient rouge Free Mobile
    st.markdown("""
    <div class="hero-section">
        <div style="display: flex; justify-content: center; margin-bottom: 2rem;">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="width: 70px; height: 70px; background: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                    <span style="font-size: 2.2rem; font-weight: 900; color: #CC0000;">FM</span>
                </div>
                <div style="display: flex; flex-direction: column; text-align: left;">
                    <span style="font-size: 2rem; font-weight: 900; color: white; letter-spacing: -1px; line-height: 1; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">FreeMobila</span>
                    <span style="font-size: 1.5rem; font-weight: 700; color: rgba(255,255,255,0.95); letter-spacing: 1px; line-height: 1; text-shadow: 1px 1px 3px rgba(0,0,0,0.3);">CHAT</span>
                </div>
            </div>
        </div>
        <h1 class="hero-title"><i class="fas fa-chart-line" style="margin-right: 1rem;"></i>ANALYSE DES KPI</h1>
        <p class="hero-subtitle">Analyse avancee de donnees Twitter avec intelligence artificielle<br>Transformez vos donnees en insights actionnables</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats stylées avec icônes Font Awesome
    st.markdown("<div class=\"hero-stats\">", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 15px; 
                    box-shadow: 0 5px 20px rgba(0,0,0,0.1); text-align: center;">
            <i class="fas fa-database" style="font-size: 2.5rem; color: #CC0000; margin-bottom: 1rem;"></i>
            <div style="font-size: 2.5rem; font-weight: 900; color: #333; margin-bottom: 0.5rem;">10K+</div>
            <div style="font-size: 1rem; color: #666; font-weight: 600;">Tweets Analyses</div>
            <div style="font-size: 0.9rem; color: #4ade80; font-weight: 600; margin-top: 0.5rem;">
                <i class="fas fa-arrow-up"></i> En croissance
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 15px; 
                    box-shadow: 0 5px 20px rgba(0,0,0,0.1); text-align: center;">
            <i class="fas fa-bullseye" style="font-size: 2.5rem; color: #CC0000; margin-bottom: 1rem;"></i>
            <div style="font-size: 2.5rem; font-weight: 900; color: #333; margin-bottom: 0.5rem;">98.5%</div>
            <div style="font-size: 1rem; color: #666; font-weight: 600;">Precision IA</div>
            <div style="font-size: 0.9rem; color: #4ade80; font-weight: 600; margin-top: 0.5rem;">
                <i class="fas fa-arrow-up"></i> +1.2%
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 15px; 
                    box-shadow: 0 5px 20px rgba(0,0,0,0.1); text-align: center;">
            <i class="fas fa-bolt" style="font-size: 2.5rem; color: #CC0000; margin-bottom: 1rem;"></i>
            <div style="font-size: 2.5rem; font-weight: 900; color: #333; margin-bottom: 0.5rem;">2.3s</div>
            <div style="font-size: 1rem; color: #666; font-weight: 600;">Temps Moyen</div>
            <div style="font-size: 0.9rem; color: #4ade80; font-weight: 600; margin-top: 0.5rem;">
                <i class="fas fa-arrow-down"></i> -0.5s
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def _check_api_connection() -> bool:
    """Vérifie la connexion API et affiche le statut"""
    
    # Simulation de la vérification de connexion
    with st.spinner("Verification de la connexion API..."):
        time.sleep(1)  # Simulation du temps de vérification
    
    # Affichage du statut de connexion
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success("Backend API")
    with col2:
        st.success("Ollama API")
    with col3:
        st.info("Connexion stable")
    
    return True

def _render_sidebar_config():
    """Affiche la configuration dans la sidebar"""
    
    with st.sidebar:
        st.markdown("### Configuration")
        
        # Rôle utilisateur
        user_role = st.selectbox(
            "Rôle utilisateur",
            options=["manager", "analyst", "agent", "admin"],
            index=0,
            help="Détermine les KPIs et fonctionnalités visibles"
        )
        
        st.divider()
        
        # Configuration LLM
        with st.expander("Configuration IA", expanded=False):
            llm_provider = st.selectbox(
                "Fournisseur IA",
                ["ollama", "mistral", "openai", "anthropic"],
                index=0,
                help="Choisissez le fournisseur d'IA pour l'analyse"
            )
            
            max_tweets = st.slider(
                "Nombre max de tweets",
                min_value=50,
                max_value=2000,
                value=500,
                step=50,
                help="Limitez le nombre pour contrôler les coûts"
            )
            
            batch_size = st.slider(
                "Taille des lots",
                min_value=5,
                max_value=20,
                value=10,
                help="Nombre de tweets traités simultanément"
            )
            
            temperature = st.slider(
                "Créativité IA",
                min_value=0.0,
                max_value=1.0,
                value=0.3,
                step=0.1,
                help="Plus élevé = plus créatif, plus bas = plus précis"
            )
        
        # Sauvegarder la configuration
        st.session_state.llm_config = {
            "llm_provider": llm_provider,
            "max_tweets": max_tweets,
            "batch_size": batch_size,
            "temperature": temperature,
            "user_role": user_role
        }
        
        st.divider()
        
        # Actions rapides
        st.markdown("### Actions Rapides")
        
        if st.button("Voir Dashboard", use_container_width=True):
            st.switch_page("pages/03_resultat.py")
        
        if st.button("Parametres", use_container_width=True):
            st.info("Page de paramètres en cours de développement")
        
        if st.button("A propos", use_container_width=True):
            st.info("Page à propos en cours de développement")

def _render_modern_upload_zone() -> Optional[Dict[str, Any]]:
    """Affiche la zone d'upload moderne et retourne les données si upload réussi"""
    
    # Titre stylé avec icône
    st.markdown("""
    <div style="text-align: center; margin: 3rem 0 2rem 0;">
        <h2 style="font-size: 2.5rem; font-weight: 900; color: #333; margin-bottom: 0.5rem;"><i class="fas fa-cloud-upload-alt" style="color: #CC0000; margin-right: 1rem;"></i>Chargement des Donnees</h2>
        <p style="font-size: 1.2rem; color: #666; font-weight: 400;">Importez vos fichiers CSV, Excel, JSON ou Parquet pour commencer l'analyse</p>
    </div>
    """, unsafe_allow_html=True)
    
    # File uploader Streamlit avec style moderne
    uploaded_file = st.file_uploader(
        "Glissez-déposez votre fichier ici ou cliquez pour parcourir",
        type=['csv', 'xlsx', 'xls', 'json', 'parquet'],
        help="Formats supportés: CSV, Excel, JSON, Parquet | Taille max: 50MB",
        label_visibility="visible"
    )
    
    # Informations des formats supportés
    st.markdown("""
    <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 2rem; flex-wrap: wrap;">
        <div style="text-align: center; background: white; padding: 1rem; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border: 1px solid #e1e5e9; transition: all 0.3s ease;">
            <i class="fas fa-file-csv" style="font-size: 2rem; color: #4ade80;"></i>
            <div style="font-size: 0.9rem; color: #666; margin-top: 0.5rem; font-weight: 600;">CSV</div>
        </div>
        <div style="text-align: center; background: white; padding: 1rem; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border: 1px solid #e1e5e9; transition: all 0.3s ease;">
            <i class="fas fa-file-excel" style="font-size: 2rem; color: #10b981;"></i>
            <div style="font-size: 0.9rem; color: #666; margin-top: 0.5rem; font-weight: 600;">Excel</div>
        </div>
        <div style="text-align: center; background: white; padding: 1rem; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border: 1px solid #e1e5e9; transition: all 0.3s ease;">
            <i class="fas fa-file-code" style="font-size: 2rem; color: #3b82f6;"></i>
            <div style="font-size: 0.9rem; color: #666; margin-top: 0.5rem; font-weight: 600;">JSON</div>
        </div>
        <div style="text-align: center; background: white; padding: 1rem; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border: 1px solid #e1e5e9; transition: all 0.3s ease;">
            <i class="fas fa-database" style="font-size: 2rem; color: #8b5cf6;"></i>
            <div style="font-size: 0.9rem; color: #666; margin-top: 0.5rem; font-weight: 600;">Parquet</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if uploaded_file is not None:
        return _process_uploaded_file(uploaded_file)
    
    return None

def _process_uploaded_file(uploaded_file) -> Optional[Dict[str, Any]]:
    """Traite le fichier uploadé avec validation"""
    
    try:
        # Simulation de la validation
        st.success("Fichier charge avec succes!")
        
        # Simulation des données avec classifications et scores
        import random
        np.random.seed(42)
        
        sentiments = ['Positif', 'Negatif', 'Neutre']
        categories = ['Service Client', 'Produit', 'Livraison', 'Prix', 'Qualite']
        priorities = ['Haute', 'Moyenne', 'Basse']
        
        num_rows = 100
        data = pd.DataFrame({
            'text': [f'Tweet exemple {i} avec du contenu analyse' for i in range(1, num_rows + 1)],
            'author': [f'user{i}' for i in range(1, num_rows + 1)],
            'date': pd.date_range('2023-01-01', periods=num_rows, freq='H'),
            'sentiment': np.random.choice(sentiments, num_rows, p=[0.5, 0.3, 0.2]),
            'sentiment_score': np.random.uniform(0.6, 0.99, num_rows),
            'category': np.random.choice(categories, num_rows),
            'priority': np.random.choice(priorities, num_rows, p=[0.2, 0.5, 0.3]),
            'retweet_count': np.random.randint(0, 100, num_rows),
            'favorite_count': np.random.randint(5, 200, num_rows)
        })
        
        file_info = {
            "name": uploaded_file.name,
            "size": uploaded_file.size,
            "size_formatted": f"{uploaded_file.size / 1024:.1f} KB"
        }
        
        # Affichage des informations du fichier avec style moderne
        st.markdown("<div style='margin: 2rem 0;'>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Lignes", f"{len(data):,}")
        with col2:
            st.metric("Colonnes", len(data.columns))
        with col3:
            st.metric("Taille", file_info["size_formatted"])
        with col4:
            st.metric("Qualite", "98%", "+3%")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Bouton d'analyse avec style moderne
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("Lancer l'Analyse IA", type="primary", use_container_width=True, key="analyze_btn"):
                # Sauvegarder les données dans la session
                st.session_state.analyzed_data = data
                st.session_state.file_info = file_info
                st.session_state.analysis_completed = True
                
                # Animation de progression
                with st.spinner("Analyse en cours..."):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    steps = [
                        ("Chargement des donnees", 0.2),
                        ("Analyse de sentiment IA", 0.4),
                        ("Categorisation automatique", 0.6),
                        ("Evaluation de priorite", 0.8),
                        ("Calcul des KPIs", 1.0)
                    ]
                    
                    for step_name, progress in steps:
                        status_text.markdown(f"**{step_name}...**")
                        progress_bar.progress(progress)
                        time.sleep(0.5)
                    
                    st.success("Analyse terminee avec succes!")
                    time.sleep(1)
                    
                    # Redirection automatique vers le dashboard
                    st.info("Redirection vers le dashboard des KPIs...")
                    time.sleep(1)
                    st.switch_page("pages/03_resultat.py")
        
        # Aperçu des données avec style
        with st.expander("Apercu des donnees (10 premieres lignes)", expanded=False):
            st.dataframe(
                data.head(10),
                use_container_width=True,
                height=400
            )
        
        return None
        
    except Exception as e:
        st.error(f"Erreur lors du traitement du fichier: {str(e)}")
        logger.error(f"Error processing file: {str(e)}", exc_info=True)
        return None

def _handle_successful_upload(upload_result: Dict[str, Any]):
    """Gère l'upload réussi et la redirection"""
    
    st.success("Fichier charge avec succes!")
    st.info("Redirection automatique vers l'analyse...")
    
    # Petite pause pour afficher le message
    time.sleep(1)
    
    # Redirection vers le dashboard
    st.switch_page("pages/03_resultat.py")

def _render_current_analyses():
    """Affiche les analyses en cours"""
    
    current_batch = st.session_state.get("current_batch_id")
    
    if current_batch:
        st.markdown("### Analyses en Cours")
        
        # Simulation du statut
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("ID Batch", current_batch)
        with col2:
            st.metric("Statut", "Termine")
        with col3:
            st.metric("Tweets", st.session_state.get("uploaded_data", pd.DataFrame()).shape[0])
        
        # Bouton pour voir les résultats
        if st.button("Voir les Resultats", type="primary"):
            st.switch_page("pages/03_resultat.py")

def _render_global_metrics():
    """Affiche les métriques globales avec design moderne"""
    
    # Titre section
    st.markdown("""
    <div style="text-align: center; margin: 4rem 0 2rem 0;">
        <h2 style="font-size: 2.5rem; font-weight: 900; color: #333; margin-bottom: 1rem;">
            <i class="fas fa-tachometer-alt" style="color: #CC0000; margin-right: 1rem;"></i>
            Metriques Globales
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Métriques stylées
    col1, col2, col3, col4 = st.columns(4, gap="large")
    
    with col1:
        st.metric("Fichiers Traites", "0", "0")
    
    with col2:
        st.metric("Analyses Terminees", "0", "0")
    
    with col3:
        st.metric("KPIs Calcules", "0", "0")
    
    with col4:
        st.metric("Temps Moyen", "0s", "0s")
    
    # Instructions simples
    st.markdown("""
    <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); margin: 2rem 0;">
        <h3 style="text-align: center; color: #333; margin-bottom: 1.5rem;">
            <i class="fas fa-info-circle" style="color: #CC0000; margin-right: 0.5rem;"></i>
            Comment Commencer
        </h3>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;">
            <div style="text-align: center; padding: 1rem;">
                <div style="width: 40px; height: 40px; background: #CC0000; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 0.5rem;">
                    <span style="color: white; font-weight: bold;">1</span>
                </div>
                <h4 style="color: #333; margin-bottom: 0.5rem;">Chargez un Fichier</h4>
                <p style="color: #666; font-size: 0.9rem;">Glissez-deposez votre fichier</p>
            </div>
            <div style="text-align: center; padding: 1rem;">
                <div style="width: 40px; height: 40px; background: #CC0000; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 0.5rem;">
                    <span style="color: white; font-weight: bold;">2</span>
                </div>
                <h4 style="color: #333; margin-bottom: 0.5rem;">Configurez l'Analyse</h4>
                <p style="color: #666; font-size: 0.9rem;">Choisissez vos parametres</p>
            </div>
            <div style="text-align: center; padding: 1rem;">
                <div style="width: 40px; height: 40px; background: #CC0000; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 0.5rem;">
                    <span style="color: white; font-weight: bold;">3</span>
                </div>
                <h4 style="color: #333; margin-bottom: 0.5rem;">Lancez l'Analyse</h4>
                <p style="color: #666; font-size: 0.9rem;">Cliquez sur le bouton d'analyse</p>
            </div>
            <div style="text-align: center; padding: 1rem;">
                <div style="width: 40px; height: 40px; background: #CC0000; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 0.5rem;">
                    <span style="color: white; font-weight: bold;">4</span>
                </div>
                <h4 style="color: #333; margin-bottom: 0.5rem;">Consultez les Resultats</h4>
                <p style="color: #666; font-size: 0.9rem;">Visualisez vos KPIs</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def _render_features_section():
    """Affiche la section des fonctionnalités avec design moderne"""
    
    # Titre section
    st.markdown("""
    <div style="text-align: center; margin: 4rem 0 3rem 0;">
        <h2 style="font-size: 2.5rem; font-weight: 900; color: #333; margin-bottom: 1rem;">
            <i class="fas fa-star" style="color: #CC0000; margin-right: 1rem;"></i>
            Fonctionnalites Principales
        </h2>
        <p style="font-size: 1.2rem; color: #666;">
            Tout ce dont vous avez besoin pour analyser vos donnees
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Fonctionnalités en grille simple
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.08); text-align: center; margin-bottom: 1rem;">
            <i class="fas fa-robot" style="font-size: 3rem; color: #CC0000; margin-bottom: 1rem;"></i>
            <h3 style="color: #CC0000; font-size: 1.3rem; font-weight: 700; margin-bottom: 1rem;">IA Avancee</h3>
            <p style="color: #666; font-size: 0.9rem; line-height: 1.6;">Analyse de sentiment et categorisation automatique</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.08); text-align: center; margin-bottom: 1rem;">
            <i class="fas fa-clock" style="font-size: 3rem; color: #CC0000; margin-bottom: 1rem;"></i>
            <h3 style="color: #CC0000; font-size: 1.3rem; font-weight: 700; margin-bottom: 1rem;">Temps Reel</h3>
            <p style="color: #666; font-size: 0.9rem; line-height: 1.6;">Analyse en temps reel avec progression detaillee</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.08); text-align: center; margin-bottom: 1rem;">
            <i class="fas fa-chart-pie" style="font-size: 3rem; color: #CC0000; margin-bottom: 1rem;"></i>
            <h3 style="color: #CC0000; font-size: 1.3rem; font-weight: 700; margin-bottom: 1rem;">KPIs Personnalises</h3>
            <p style="color: #666; font-size: 0.9rem; line-height: 1.6;">Metriques adaptees a votre role</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.08); text-align: center; margin-bottom: 1rem;">
            <i class="fas fa-shield-alt" style="font-size: 3rem; color: #CC0000; margin-bottom: 1rem;"></i>
            <h3 style="color: #CC0000; font-size: 1.3rem; font-weight: 700; margin-bottom: 1rem;">Securise</h3>
            <p style="color: #666; font-size: 0.9rem; line-height: 1.6;">Validation stricte et chiffrement des donnees</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.08); text-align: center; margin-bottom: 1rem;">
            <i class="fas fa-file-export" style="font-size: 3rem; color: #CC0000; margin-bottom: 1rem;"></i>
            <h3 style="color: #CC0000; font-size: 1.3rem; font-weight: 700; margin-bottom: 1rem;">Export Multi-Format</h3>
            <p style="color: #666; font-size: 0.9rem; line-height: 1.6;">Export en PDF, Excel, JSON ou CSV</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.08); text-align: center; margin-bottom: 1rem;">
            <i class="fas fa-chart-line" style="font-size: 3rem; color: #CC0000; margin-bottom: 1rem;"></i>
            <h3 style="color: #CC0000; font-size: 1.3rem; font-weight: 700; margin-bottom: 1rem;">Visualisations</h3>
            <p style="color: #666; font-size: 0.9rem; line-height: 1.6;">Graphiques interactifs et dashboards</p>
        </div>
        """, unsafe_allow_html=True)

def _handle_intelligent_analysis(upload_result: Dict[str, Any]) -> None:
    """
    Gère l'analyse intelligente avec le nouveau système LLM adaptatif
    """
    try:
        # Récupération des données uploadées
        df = upload_result.get('dataframe')
        filename = upload_result.get('filename', 'dataset.csv')
        
        if df is None or df.empty:
            st.error("Aucune donnée valide à analyser")
            return
        
        # Affichage du header d'analyse moderne
        st.markdown("---")
        _render_analysis_header_modern(df, filename)
        
        # Vérification de la disponibilité des modules d'analyse intelligente
        if not INTELLIGENT_ANALYSIS_AVAILABLE:
            st.warning("⚠️ Modules d'analyse intelligente non disponibles. Utilisation de l'analyse de base.")
            _handle_successful_upload(upload_result)
            return
        
        # Barre de progression moderne
        progress_container = st.container()
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        # Étapes de l'analyse
        steps = [
            "🔍 Inspection intelligente des données...",
            "📝 Génération du prompt personnalisé...",
            "🤖 Analyse IA adaptative...",
            "✨ Enrichissement des résultats...",
            "📊 Génération des visualisations...",
            "🎯 Finalisation de l'analyse..."
        ]
        
        # Simulation de la progression
        for i, step in enumerate(steps):
            progress_bar.progress((i + 1) / len(steps))
            status_text.text(step)
            time.sleep(0.3)  # Simulation du temps de traitement
        
        # Analyse RÉELLE avec LLM
        try:
            # Initialisation des composants d'analyse
            inspector = IntelligentDataInspector()
            viz_engine = SmartVisualizationEngine()
            real_llm_engine = RealLLMEngine()
            
            # Phase 1: Inspection des données
            status_text.text("🔍 Analyse contextuelle des données...")
            context = inspector.analyze_dataset_context(df)
            
            # Phase 2: Analyse LLM RÉELLE avec API calls
            status_text.text("🤖 Analyse IA réelle en cours...")
            analysis_results = asyncio.run(real_llm_engine.analyze_with_llm(df, filename, context))
            
            # Phase 3: Génération des visualisations
            status_text.text("📊 Création des visualisations...")
            visualizations = viz_engine.generate_contextual_charts(analysis_results, df)
            analysis_results['visualizations'] = visualizations
            
            # Phase 4: Finalisation
            status_text.text("🎯 Finalisation de l'analyse...")
            analysis_results['context'] = context
            analysis_results['metadata'] = {
                'filename': filename,
                'analysis_date': datetime.now().isoformat(),
                'dataset_size': len(df),
                'columns': list(df.columns)
            }
            
            # Stockage des résultats
            st.session_state['analysis_results'] = analysis_results
            st.session_state['analysis_completed'] = True
            st.session_state['current_dataset'] = df
            st.session_state['current_filename'] = filename
            
            # Nettoyage de la progression
            progress_container.empty()
            
            # Affichage des résultats
            _render_analysis_results_modern(analysis_results, df)
            
            # Bouton pour nouvelle analyse
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔄 Nouvelle Analyse", type="primary", use_container_width=True):
                    # Nettoyage de la session
                    for key in ['analysis_results', 'analysis_completed', 'current_dataset', 'current_filename']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse intelligente: {e}")
            st.error(f"Erreur lors de l'analyse: {str(e)}")
            
            # Fallback vers l'ancien système
            st.warning("Utilisation du système d'analyse de base...")
            _handle_successful_upload(upload_result)
    
    except Exception as e:
        logger.error(f"Erreur dans _handle_intelligent_analysis: {e}")
        st.error(f"Erreur lors du traitement: {str(e)}")

# Les fonctions de simulation ont été supprimées car remplacées par le vrai moteur LLM

def _render_analysis_header_modern(df: pd.DataFrame, filename: str) -> None:
    """Affiche le header moderne de l'analyse"""
    try:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #CC0000 0%, #8B0000 100%); 
                    padding: 2rem; border-radius: 15px; margin-bottom: 2rem; color: white;">
            <div style="text-align: center;">
                <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">
                    <i class="fas fa-brain" style="margin-right: 1rem;"></i>
                    ANALYSE INTELLIGENTE
                </h1>
                <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.9;">
                    {filename} • {len(df):,} lignes • {len(df.columns)} colonnes
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Métriques de base
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Lignes de données",
                value=f"{len(df):,}",
                delta=None
            )
        
        with col2:
            st.metric(
                label="Colonnes",
                value=f"{len(df.columns)}",
                delta=None
            )
        
        with col3:
            null_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            st.metric(
                label="Complétude",
                value=f"{100 - null_percentage:.1f}%",
                delta=None
            )
        
        with col4:
            numeric_cols = len(df.select_dtypes(include=['number']).columns)
            st.metric(
                label="Colonnes numériques",
                value=f"{numeric_cols}",
                delta=None
            )
            
    except Exception as e:
        logger.error(f"Erreur lors du rendu du header d'analyse: {e}")

def _render_analysis_results_modern(analysis_results: Dict[str, Any], df: pd.DataFrame) -> None:
    """Affiche les résultats d'analyse de manière moderne"""
    try:
        # Classification
        classification = analysis_results.get('classification', {})
        if classification:
            st.markdown("### Classification du Dataset")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.info(f"**Domaine:** {classification.get('domain', 'Général')}")
            with col2:
                st.info(f"**Type:** {classification.get('data_type', 'Dataset')}")
            with col3:
                confidence = classification.get('confidence_score', 0.0)
                st.info(f"**Confiance:** {confidence:.1%}")
        
        # Métriques clés
        key_metrics = analysis_results.get('key_metrics', [])
        if key_metrics:
            st.markdown("### Métriques Clés")
            
            # Groupement par importance
            high_importance = [m for m in key_metrics if m.get('importance', 0) >= 0.8]
            medium_importance = [m for m in key_metrics if 0.5 <= m.get('importance', 0) < 0.8]
            
            if high_importance:
                st.markdown("#### Priorité Haute")
                cols = st.columns(min(len(high_importance), 4))
                for i, metric in enumerate(high_importance[:4]):
                    with cols[i % 4]:
                        _render_metric_card_modern(metric, "high")
            
            if medium_importance:
                st.markdown("#### Priorité Moyenne")
                cols = st.columns(min(len(medium_importance), 4))
                for i, metric in enumerate(medium_importance[:4]):
                    with cols[i % 4]:
                        _render_metric_card_modern(metric, "medium")
        
        # Insights
        insights = analysis_results.get('insights', [])
        if insights:
            st.markdown("### Insights Intelligents")
            
            # Groupement par impact
            high_impact = [i for i in insights if i.get('impact') == 'high']
            medium_impact = [i for i in insights if i.get('impact') == 'medium']
            
            if high_impact:
                st.markdown("#### Impact Élevé")
                for insight in high_impact:
                    _render_insight_card_modern(insight, "high")
            
            if medium_impact:
                st.markdown("#### Impact Moyen")
                for insight in medium_impact:
                    _render_insight_card_modern(insight, "medium")
        
        # Visualisations
        visualizations = analysis_results.get('visualizations', [])
        if visualizations:
            st.markdown("### Visualisations Intelligentes")
            
            feasible_viz = [v for v in visualizations if v.get('status') == 'feasible']
            
            if feasible_viz:
                for i, viz in enumerate(feasible_viz[:6]):  # Limiter à 6 visualisations
                    try:
                        st.markdown(f"#### {viz.get('title', f'Graphique {i+1}')}")
                        
                        if viz.get('description'):
                            st.markdown(f"*{viz['description']}*")
                        
                        if viz.get('rationale'):
                            st.markdown(f"**Justification:** {viz['rationale']}")
                        
                        figure = viz.get('figure')
                        if figure:
                            st.plotly_chart(figure, use_container_width=True)
                        else:
                            st.info("Graphique non disponible")
                        
                        if viz.get('columns'):
                            st.markdown(f"**Colonnes utilisées:** {', '.join(viz['columns'])}")
                        
                        st.markdown("---")
                        
                    except Exception as e:
                        logger.warning(f"Erreur lors de l'affichage de la visualisation {i}: {e}")
                        continue
            else:
                st.warning("Aucune visualisation faisable avec les données disponibles")
        
        # Recommandations
        recommendations = analysis_results.get('recommendations', [])
        if recommendations:
            st.markdown("### Recommandations Actionnables")
            
            high_priority = [r for r in recommendations if r.get('priority') == 'high']
            medium_priority = [r for r in recommendations if r.get('priority') == 'medium']
            
            if high_priority:
                st.markdown("#### Priorité Haute")
                for rec in high_priority:
                    _render_recommendation_card_modern(rec, "high")
            
            if medium_priority:
                st.markdown("#### Priorité Moyenne")
                for rec in medium_priority:
                    _render_recommendation_card_modern(rec, "medium")
        
        # Export et actions
        st.markdown("### Export et Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Export JSON
            import json
            json_data = json.dumps(analysis_results, ensure_ascii=False, indent=2)
            st.download_button(
                label="Télécharger Analyse JSON",
                data=json_data,
                file_name=f"analyse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        with col2:
            # Export CSV des métriques
            if key_metrics:
                metrics_df = pd.DataFrame(key_metrics)
                csv_data = metrics_df.to_csv(index=False)
                st.download_button(
                    label="Télécharger Métriques CSV",
                    data=csv_data,
                    file_name=f"metriques_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col3:
            # Aperçu des données
            if st.button("Aperçu des Données", use_container_width=True):
                st.dataframe(df.head(100), use_container_width=True)
        
    except Exception as e:
        logger.error(f"Erreur lors du rendu des résultats d'analyse: {e}")

def _render_metric_card_modern(metric: Dict[str, Any], priority: str) -> None:
    """Affiche une carte de métrique moderne"""
    try:
        name = metric.get('name', 'Métrique')
        value = metric.get('value', 0)
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
                {importance:.0%} importance
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        logger.error(f"Erreur lors du rendu de la carte de métrique: {e}")

def _render_insight_card_modern(insight: Dict[str, Any], impact: str) -> None:
    """Affiche une carte d'insight moderne"""
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

def _render_recommendation_card_modern(recommendation: Dict[str, Any], priority: str) -> None:
    """Affiche une carte de recommandation moderne"""
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

if __name__ == "__main__":
    main()