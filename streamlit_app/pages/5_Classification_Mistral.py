"""
FreeMobilaChat - Classification System
Master Thesis Project - Data Science & AI

Advanced NLP Classification with Multi-Model Architecture:
- Mistral AI (LLM)
- BERT (Deep Learning)
- Rule-Based Classifier

Version: 4.1 Professional Edition
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
import logging
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration des chemins
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Professional Icons (Material Design System)
class Icons:
    """Modern professional icons for academic dashboard"""
    # Navigation & Actions
    HOME = "⌂"
    DASHBOARD = "▦"
    UPLOAD = "⇑"
    DOWNLOAD = "⇓"
    SETTINGS = "⚙"
    SEARCH = "⌕"
    REFRESH = "↻"
    
    # Status Indicators
    SUCCESS = "✓"
    ERROR = "✕"
    WARNING = "△"
    INFO = "ⓘ"
    PROGRESS = "◷"
    
    # Arrows & Navigation
    RIGHT = "→"
    LEFT = "←"
    UP = "↑"
    DOWN = "↓"
    
    # Classification Features
    MODEL = "⬡"
    DATA = "▦"
    CHART = "◱"
    DOCUMENT = "⎙"
    
    # Processing Modes
    FAST = "⟩⟩"
    BALANCED = "▸▸"
    PRECISE = "●"
    
    # Menu & UI Elements
    MENU = "☰"
    DOT = "●"
    SQUARE = "■"
    CIRCLE = "◉"
    CHECK = "✓"
    CROSS = "✕"

# Import des modules
MODULES_AVAILABLE = False
IMPORT_ERROR = None

try:
    logger.info(f"{Icons.RIGHT} Loading classification modules...")
    
    from services.tweet_cleaner import TweetCleaner
    from services.mistral_classifier import (
        MistralClassifier,
        check_ollama_availability,
        list_available_models
    )
    from services.multi_model_orchestrator import MultiModelOrchestrator
    from services.bert_classifier import BERTClassifier
    from services.rule_classifier import EnhancedRuleClassifier
    
    # Role Management System
    from services.role_manager import (
        initialize_role_system,
        get_current_role,
        check_permission,
        check_feature
    )
    from services.auth_service import AuthService
    
    MODULES_AVAILABLE = True
    ROLE_SYSTEM_AVAILABLE = True
    logger.info(f"{Icons.SUCCESS} All modules loaded successfully (with role system)")
except Exception as e:
    IMPORT_ERROR = str(e)
    MODULES_AVAILABLE = False
    ROLE_SYSTEM_AVAILABLE = False
    logger.error(f"{Icons.ERROR} Module import error: {e}")

# Page Configuration
st.set_page_config(
    page_title="Classification System | FreeMobilaChat",
    page_icon="▦",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Point d'entrée principal"""
    if not MODULES_AVAILABLE:
        _render_error_page()
        return
    
    # Initialize role system
    if ROLE_SYSTEM_AVAILABLE:
        role_manager, role_ui_manager = initialize_role_system()
        # Set default role if none selected
        if not get_current_role():
            role_manager.set_current_role("manager")  # Default to Manager
    
    _load_modern_css()
    _render_sidebar()
    _render_header()
    _render_workflow_indicator()
    
    # Workflow
    if 'workflow_step' not in st.session_state:
        st.session_state.workflow_step = 'upload'
    
    # Routing des sections
    if st.session_state.workflow_step == 'upload':
        _section_upload()
    elif st.session_state.workflow_step == 'classify':
        _section_classification()
    elif st.session_state.workflow_step == 'results':
        _section_results()

def _load_modern_css():
    """Charge les styles CSS ultra-modernes v4.0"""
    st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
    /* ============================================ */
    /* Ultra-Modern Professional Theme v4.0        */
    /* ============================================ */
    
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --primary: #1E3A5F;
        --primary-light: #2E4A6F;
        --secondary: #2E86DE;
        --secondary-light: #4A9AE8;
        --success: #10AC84;
        --success-light: #2EBD9E;
        --warning: #F79F1F;
        --warning-light: #F9AB3F;
        --danger: #EE5A6F;
        --danger-light: #F17283;
        --light: #F5F6FA;
        --dark: #2C3E50;
        --shadow: rgba(0,0,0,0.08);
        --shadow-lg: rgba(0,0,0,0.15);
        --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #F5F7FA 0%, #FFFFFF 100%);
        animation: fadeIn 0.5s ease-in-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* Typography - Enhanced */
    h1 {
        font-size: 2.4rem; 
        font-weight: 800; 
        color: var(--primary); 
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
        animation: slideIn 0.6s ease-out;
    }
    h2 {
        font-size: 1.8rem; 
        font-weight: 700; 
        color: var(--primary); 
        margin-top: 2rem;
        letter-spacing: -0.3px;
    }
    h3 {
        font-size: 1.4rem; 
        font-weight: 600; 
        color: var(--dark);
        letter-spacing: -0.2px;
    }
    
    /* Cards & Containers - Enhanced with Hover */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column"] > [data-testid="stVerticalBlock"] {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 2px 12px var(--shadow);
        border: 1px solid #E8E8E8;
        transition: var(--transition);
        animation: fadeIn 0.4s ease-out;
    }
    
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column"] > [data-testid="stVerticalBlock"]:hover {
        box-shadow: 0 8px 24px var(--shadow-lg);
        transform: translateY(-2px);
        border-color: var(--secondary-light);
    }
    
    /* Metrics - Modern Cards with Gradient Background */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem;
        font-weight: 800;
        color: var(--primary);
        letter-spacing: -0.5px;
        transition: var(--transition);
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        font-weight: 700;
        color: var(--dark);
        text-transform: uppercase;
        letter-spacing: 1px;
        opacity: 0.8;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.9rem;
        font-weight: 600;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        background: rgba(46, 134, 222, 0.1);
    }
    
    /* Buttons - Modern & Elevated with Animation */
    .stButton > button {
        background: linear-gradient(135deg, var(--secondary) 0%, #1A6FC7 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.875rem 2.5rem;
        font-weight: 700;
        font-size: 1.05rem;
        letter-spacing: 0.3px;
        transition: var(--transition);
        box-shadow: 0 4px 16px rgba(46, 134, 222, 0.35);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton > button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .stButton > button:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 12px 28px rgba(46, 134, 222, 0.5);
        background: linear-gradient(135deg, var(--secondary-light) 0%, var(--secondary) 100%);
    }
    
    .stButton > button:active {
        transform: translateY(-1px) scale(0.98);
        box-shadow: 0 4px 12px rgba(46, 134, 222, 0.3);
    }
    
    /* Progress Bar - Gradient */
    .stProgress > div > div {
        background: linear-gradient(90deg, #2E86DE 0%, #10AC84 50%, #0FBCF9 100%);
        height: 8px;
        border-radius: 10px;
    }
    
    /* Tabs - Modern Design */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: var(--light);
        padding: 0.75rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 55px;
        background: white;
        border-radius: 8px;
        color: var(--dark);
        font-weight: 600;
        font-size: 0.95rem;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #F0F0F0;
        border-color: var(--secondary);
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--secondary);
        color: white;
        border-color: var(--secondary);
        box-shadow: 0 4px 12px rgba(46, 134, 222, 0.3);
    }
    
    /* Expander - Modern with Hover Effect */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, var(--light) 0%, #EAECF0 100%);
        border-radius: 12px;
        font-weight: 700;
        font-size: 1.05rem;
        color: var(--primary);
        padding: 1.25rem 1.5rem;
        transition: var(--transition);
        border: 2px solid transparent;
        box-shadow: 0 2px 8px var(--shadow);
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #EAECF0 0%, #E0E4EA 100%);
        border-color: var(--secondary-light);
        box-shadow: 0 4px 12px var(--shadow-lg);
        transform: translateX(5px);
    }
    
    .streamlit-expanderContent {
        border-left: 3px solid var(--secondary);
        padding-left: 1.5rem;
        animation: slideIn 0.4s ease-out;
    }
    
    /* File Uploader - Modern */
    [data-testid="stFileUploadDropzone"] {
        border: 2px dashed var(--secondary);
        border-radius: 12px;
        background: linear-gradient(135deg, #F5F7FA 0%, #FFFFFF 100%);
        padding: 2rem;
    }
    
    /* Dataframes - Professional */
    .dataframe {
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        overflow: hidden;
    }
    
    .dataframe thead tr th {
        background: var(--primary);
        color: white !important;
        font-weight: 600;
        text-align: left;
        padding: 1rem;
        border: none;
    }
    
    .dataframe tbody tr:nth-child(even) {
        background: #F9F9F9;
    }
    
    .dataframe tbody tr:hover {
        background: #F0F0F0;
    }
    
    .dataframe tbody td {
        padding: 0.75rem;
        border-bottom: 1px solid #E8E8E8;
    }
    
    /* Alert Messages - Modern with Icons & Animation */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 12px;
        padding: 1.25rem 1.75rem;
        margin: 1rem 0;
        border-left: 5px solid;
        font-weight: 600;
        font-size: 1.02rem;
        box-shadow: 0 2px 12px var(--shadow);
        animation: slideIn 0.4s ease-out;
        transition: var(--transition);
    }
    
    .stSuccess {
        background: linear-gradient(135deg, rgba(16, 172, 132, 0.12) 0%, rgba(16, 172, 132, 0.06) 100%);
        border-left-color: var(--success);
    }
    
    .stSuccess:hover {
        background: linear-gradient(135deg, rgba(16, 172, 132, 0.18) 0%, rgba(16, 172, 132, 0.09) 100%);
        box-shadow: 0 4px 16px rgba(16, 172, 132, 0.2);
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(238, 90, 111, 0.12) 0%, rgba(238, 90, 111, 0.06) 100%);
        border-left-color: var(--danger);
    }
    
    .stError:hover {
        background: linear-gradient(135deg, rgba(238, 90, 111, 0.18) 0%, rgba(238, 90, 111, 0.09) 100%);
        box-shadow: 0 4px 16px rgba(238, 90, 111, 0.2);
    }
    
    .stWarning {
        background: linear-gradient(135deg, rgba(247, 159, 31, 0.12) 0%, rgba(247, 159, 31, 0.06) 100%);
        border-left-color: var(--warning);
    }
    
    .stWarning:hover {
        background: linear-gradient(135deg, rgba(247, 159, 31, 0.18) 0%, rgba(247, 159, 31, 0.09) 100%);
        box-shadow: 0 4px 16px rgba(247, 159, 31, 0.2);
    }
    
    .stInfo {
        background: linear-gradient(135deg, rgba(46, 134, 222, 0.12) 0%, rgba(46, 134, 222, 0.06) 100%);
        border-left-color: var(--secondary);
    }
    
    .stInfo:hover {
        background: linear-gradient(135deg, rgba(46, 134, 222, 0.18) 0%, rgba(46, 134, 222, 0.09) 100%);
        box-shadow: 0 4px 16px rgba(46, 134, 222, 0.2);
    }
    
    /* Sidebar - Modern */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #F8F9FA 0%, #FFFFFF 100%);
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Radio Buttons - Modern */
    [data-testid="stRadio"] > label {
        font-weight: 600;
        color: var(--primary);
    }
    
    /* Checkboxes - Modern */
    [data-testid="stCheckbox"] > label {
        font-weight: 500;
        color: var(--dark);
    }
    
    /* Spinner - Modern */
    .stSpinner > div {
        border-top-color: var(--secondary);
    }
    </style>
    """, unsafe_allow_html=True)

def _render_header():
    """Modern professional dashboard header"""
    # Version badge
    st.markdown(f"""
    <div style="text-align: right; margin-bottom: -10px;">
        <span style="background: linear-gradient(135deg, var(--secondary) 0%, var(--primary) 100%);
                     color: white; padding: 0.5rem 1.5rem; border-radius: 25px;
                     font-weight: 700; font-size: 0.85rem; letter-spacing: 1px;
                     box-shadow: 0 4px 12px rgba(46, 134, 222, 0.3);">
            VERSION 4.1 | PROFESSIONAL EDITION
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"""
        <div style="animation: slideIn 0.6s ease-out;">
            <h1 style="margin-bottom: 0.5rem;">{Icons.DASHBOARD} Automated Classification System</h1>
            <p style="font-size: 1.1rem; color: var(--dark); font-weight: 500; opacity: 0.85; margin-top: 0;">
                Advanced NLP with <strong>Mistral AI</strong>, <strong>BERT</strong> & <strong>Rules</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # System status
        modules_status = f"{Icons.SUCCESS} Operational" if MODULES_AVAILABLE else f"{Icons.ERROR} Error"
        st.metric(
            f"{Icons.MODEL} System Status",
            modules_status,
            help="Classification modules state"
        )
    
    with col3:
        # Workflow status
        current_step = st.session_state.get('workflow_step', 'upload')
        step_names = {'upload': 'Upload', 'classify': 'Classification', 'results': 'Results'}
        step_icons = {'upload': Icons.UPLOAD, 'classify': Icons.DASHBOARD, 'results': Icons.CHART}
        st.metric(
            f"{Icons.PROGRESS} Current Step",
            f"{step_icons.get(current_step, Icons.UPLOAD)} {step_names.get(current_step, 'N/A')}",
            help="Workflow progression"
        )
    
    st.markdown("---")

def _render_workflow_indicator():
    """Visual workflow progress indicator"""
    current_step = st.session_state.get('workflow_step', 'upload')
    
    steps = {
        'upload': {'num': 1, 'name': 'Upload & Cleaning', 'icon': Icons.UPLOAD},
        'classify': {'num': 2, 'name': 'Classification', 'icon': Icons.DASHBOARD},
        'results': {'num': 3, 'name': 'Results & Export', 'icon': Icons.CHART}
    }
    
    cols = st.columns(3)
    
    for idx, (step_key, step_info) in enumerate(steps.items()):
        with cols[idx]:
            is_current = (step_key == current_step)
            is_completed = (
                (step_key == 'upload' and current_step in ['classify', 'results']) or
                (step_key == 'classify' and current_step == 'results')
            )
            
            if is_current:
                st.info(f"**{step_info['icon']} [{step_info['num']}] {step_info['name']}**\n\n{Icons.PROGRESS} In progress...")
            elif is_completed:
                st.success(f"**{Icons.SUCCESS} [{step_info['num']}] {step_info['name']}**\n\n{Icons.CHECK} Completed")
            else:
                st.caption(f"{step_info['icon']} [{step_info['num']}] {step_info['name']}")
    
    st.markdown("---")

def _render_sidebar():
    """Modern professional sidebar with configuration options"""
    with st.sidebar:
        # Professional header with icon
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1E3A5F 0%, #2E4A6F 100%);
                    padding: 1.5rem 1rem; border-radius: 16px; margin-bottom: 1.5rem;
                    box-shadow: 0 8px 24px rgba(30, 58, 95, 0.35);
                    border: 2px solid rgba(255, 255, 255, 0.1);">
            <div style="text-align: center;">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));">
                    {Icons.SETTINGS}
                </div>
                <h2 style="color: white; margin: 0; font-size: 1.4rem; font-weight: 800;
                           text-shadow: 2px 2px 4px rgba(0,0,0,0.3); letter-spacing: 0.5px;">
                    Configuration
                </h2>
                <div style="background: linear-gradient(135deg, rgba(255,255,255,0.25) 0%, rgba(255,255,255,0.15) 100%);
                            color: white; padding: 0.4rem 1.2rem; border-radius: 20px; margin-top: 0.75rem;
                            font-size: 0.7rem; font-weight: 700; letter-spacing: 1.2px;
                            box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);">
                    SYSTEM PARAMETERS
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # System status section
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #F8F9FA 0%, #EAECF0 100%);
                    padding: 1rem; border-radius: 12px; margin-bottom: 1rem;
                    border-left: 4px solid #2E86DE;">
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
                <div style="font-size: 1.8rem; filter: drop-shadow(0 2px 4px rgba(46, 134, 222, 0.3));">
                    {Icons.INFO}
                </div>
                <h3 style="margin: 0; color: var(--primary); font-size: 1.1rem; font-weight: 700;">
                    System Status
                </h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if MODULES_AVAILABLE:
            # Liste déroulante des classificateurs
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(16, 172, 132, 0.15) 0%, rgba(16, 172, 132, 0.08) 100%);
                        padding: 0.75rem 1rem; border-radius: 10px; margin-bottom: 1rem;
                        border-left: 4px solid #10AC84;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-size: 1.2rem;"></span>
                    <strong style="color: #10AC84;">Modules chargés</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander(f" **Classificateurs Disponibles** ({5})", expanded=False):
                classificateurs = [
                    (" BERT Classifier", "Deep Learning - Analyse de sentiment", " Actif"),
                    (" Rule Classifier", "Classification par règles métier", " Actif"),
                    (" Mistral Classifier", "LLM Mistral AI via Ollama", " Actif"),
                    (" Multi-Model Orchestrator", "Orchestration intelligente", " Actif"),
                    (" Ultra-Optimized V2", "Performance 3x optimisée", " Actif")
                ]
                
                for name, desc, status in classificateurs:
                    st.markdown(f"""
                    <div style="background: white; padding: 0.75rem; border-radius: 8px; margin-bottom: 0.5rem;
                                border: 1px solid #E0E0E0; box-shadow: 0 2px 6px rgba(0,0,0,0.05);">
                        <div style="font-weight: 700; color: #1E3A5F; font-size: 0.95rem; margin-bottom: 0.25rem;">
                            {name}
                        </div>
                        <div style="font-size: 0.8rem; color: #666; margin-bottom: 0.25rem;">
                            {desc}
                        </div>
                        <div style="font-size: 0.75rem; color: #10AC84; font-weight: 600;">
                            {status}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Ollama et modèles disponibles
            ollama_available = check_ollama_availability()
            
            if ollama_available:
                st.markdown("""
                <div style="background: linear-gradient(135deg, rgba(16, 172, 132, 0.15) 0%, rgba(16, 172, 132, 0.08) 100%);
                            padding: 0.75rem 1rem; border-radius: 10px; margin-bottom: 1rem;
                            border-left: 4px solid #10AC84;">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.2rem;"></span>
                        <strong style="color: #10AC84;">Ollama actif</strong>
                        <span style="color: #666;">| Service LLM opérationnel</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                models = list_available_models()
                if models:
                    with st.expander(f" **Modèles LLM Disponibles** ({len(models)})", expanded=False):
                        for idx, model in enumerate(models):
                            model_icon = "" if idx == 0 else ""
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #F8F9FA 0%, #FFFFFF 100%);
                                        padding: 0.75rem; border-radius: 8px; margin-bottom: 0.5rem;
                                        border-left: 3px solid #2E86DE; box-shadow: 0 2px 6px rgba(0,0,0,0.05);">
                                <div style="display: flex; align-items: center; gap: 0.75rem;">
                                    <span style="font-size: 1.2rem;">{model_icon}</span>
                                    <div>
                                        <div style="font-weight: 700; color: #1E3A5F; font-size: 0.9rem;">
                                            {model}
                                        </div>
                                        <div style="font-size: 0.75rem; color: #10AC84; font-weight: 600;">
                                            {"• Recommandé" if idx == 0 else "• Disponible"}
                                        </div>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.caption("Aucun modèle détecté")
            else:
                st.markdown("""
                <div style="background: linear-gradient(135deg, rgba(238, 90, 111, 0.15) 0%, rgba(238, 90, 111, 0.08) 100%);
                            padding: 0.75rem 1rem; border-radius: 10px; margin-bottom: 1rem;
                            border-left: 4px solid #EE5A6F;">
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                        <span style="font-size: 1.2rem;"></span>
                        <strong style="color: #EE5A6F;">Ollama inactif</strong>
                    </div>
                    <div style="font-size: 0.85rem; color: #666; margin-bottom: 0.5rem;">
                        Service LLM non disponible
                    </div>
                    <div style="background: rgba(247, 159, 31, 0.1); padding: 0.5rem; border-radius: 6px;
                                border-left: 3px solid #F79F1F;">
                        <div style="font-weight: 600; color: #F79F1F; font-size: 0.8rem; margin-bottom: 0.25rem;">
                             Solution rapide :
                        </div>
                        <code style="font-size: 0.75rem; color: #2C3E50;">ollama serve</code>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error(f"{"[ERROR]"} **Modules non chargés** | Erreur critique")
            st.caption("Vérifiez l'installation des dépendances")
        
        st.markdown("---")
        
        # Classification mode selection
        st.markdown(f"### {Icons.MENU} Classification Mode")
        
        mode = st.radio(
            "Select strategy:",
            options=['fast', 'balanced', 'precise'],
            format_func=lambda x: {
                'fast': f'{Icons.FAST} FAST (20s)',
                'balanced': f'{Icons.BALANCED} BALANCED (2min)',
                'precise': f'{Icons.PRECISE} PRECISE (10min)'
            }[x],
            index=1,  # BALANCED by default
            key='classification_mode_radio'
        )
        
        # Info du mode
        mode_details = {
            'fast': {
                'models': 'BERT + Règles',
                'precision': '75%',
                'time': '20s',
                'description': 'Classification rapide, idéale pour tests'
            },
            'balanced': {
                'models': 'BERT + Règles + Mistral (20%)',
                'precision': '88%',
                'time': '2min',
                'description': 'Recommandé - Meilleur compromis vitesse/précision'
            },
            'precise': {
                'models': 'BERT + Mistral (100%)',
                'precision': '95%',
                'time': '10min',
                'description': 'Précision maximale, analyses critiques'
            }
        }
        
        detail = mode_details[mode]
        
        st.info(f"""
**Mode {mode.upper()}**

• Modèles: {detail['models']}
• Précision: {detail['precision']}
• Temps estimé: {detail['time']}

{detail['description']}
        """)
        
        st.session_state.config = {'mode': mode}
        
        st.markdown("---")
        
        # Cleaning parameters
        with st.expander(f"{Icons.SETTINGS} Cleaning Parameters"):
            st.caption("Preprocessing options")
            
            remove_duplicates = st.checkbox("Supprimer les doublons", value=True, key='remove_dupes')
            remove_urls = st.checkbox("Supprimer les URLs", value=True, key='remove_urls')
            remove_mentions = st.checkbox("Supprimer les @mentions", value=True, key='remove_mentions')
            remove_hashtags = st.checkbox("Supprimer les #hashtags", value=False, key='remove_hashtags')
            convert_emojis = st.checkbox("Convertir les emojis en texte", value=True, key='convert_emojis')
            
            st.session_state.cleaning_config = {
                'remove_duplicates': remove_duplicates,
                'remove_urls': remove_urls,
                'remove_mentions': remove_mentions,
                'remove_hashtags': remove_hashtags,
                'convert_emojis': convert_emojis
            }
        
        # Informations système ultra-moderne
        with st.expander(" **Informations Système & Performance**", expanded=False):
            try:
                bert = BERTClassifier(use_gpu=False)
                info = bert.get_model_info()
                
                st.markdown("""
                <div style="background: linear-gradient(135deg, #F8F9FA 0%, #FFFFFF 100%);
                            padding: 1rem; border-radius: 12px; border: 1px solid #E0E0E0;">
                    <div style="font-weight: 700; color: #1E3A5F; font-size: 1rem; margin-bottom: 1rem;
                                border-bottom: 2px solid #2E86DE; padding-bottom: 0.5rem;">
                         Modèle BERT
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Device
                device_icon = "️" if info['device'].upper() == "CPU" else ""
                device_color = "#F79F1F" if info['device'].upper() == "CPU" else "#10AC84"
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, {device_color}15 0%, {device_color}08 100%);
                            padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0;
                            border-left: 3px solid {device_color};">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.3rem;">{device_icon}</span>
                        <div>
                            <div style="font-size: 0.75rem; color: #666; font-weight: 600; text-transform: uppercase;">
                                Device
                            </div>
                            <div style="font-size: 1rem; font-weight: 700; color: {device_color};">
                                {info['device'].upper()}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Model
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #2E86DE15 0%, #2E86DE08 100%);
                            padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0;
                            border-left: 3px solid #2E86DE;">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.3rem;">️</span>
                        <div style="flex: 1;">
                            <div style="font-size: 0.75rem; color: #666; font-weight: 600; text-transform: uppercase;">
                                Model Name
                            </div>
                            <div style="font-size: 0.85rem; font-weight: 700; color: #2E86DE; word-break: break-all;">
                                {info['model_name']}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Batch Size
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #10AC8415 0%, #10AC8408 100%);
                            padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0;
                            border-left: 3px solid #10AC84;">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.3rem;"></span>
                        <div>
                            <div style="font-size: 0.75rem; color: #666; font-weight: 600; text-transform: uppercase;">
                                Batch Size
                            </div>
                            <div style="font-size: 1rem; font-weight: 700; color: #10AC84;">
                                {info['batch_size']} tweets/batch
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.warning(f"️ **Informations non disponibles**\n\n{str(e)[:100]}")
        
        # Role Management Tab
        st.markdown("---")
        
        if ROLE_SYSTEM_AVAILABLE:
            _render_role_management_tab()
        
        # Footer
        st.markdown("---")
        st.caption(f"Version 4.1 Professional | {datetime.now().strftime('%Y-%m-%d')}")

def _section_upload():
    """Modern upload section"""
    st.markdown(f"## {Icons.UPLOAD} Step 1 | Upload & Data Cleaning")
    
    # Instructions
    with st.expander(f"{Icons.INFO} Usage Instructions", expanded=True):
        st.markdown("""
        **Prepare your data:**
        
        1. Required format: CSV file
        2. Content: At least one text column with tweets
        3. Max size: 200 MB
        4. Encoding: UTF-8 (recommended)
        """)
    
    st.markdown(f"### {Icons.DOCUMENT} File Selection")
    
    uploaded_file = st.file_uploader(
        "Déposez votre fichier CSV ici",
        type=['csv'],
        key='file_uploader',
        help="Glissez-déposez ou cliquez pour sélectionner"
    )
    
    if uploaded_file:
        try:
            # Chargement
            with st.spinner("[⟳] Chargement du fichier..."):
                df = pd.read_csv(uploaded_file)
            
            st.success(f"{Icons.SUCCESS} File loaded successfully | **{len(df):,}** rows • **{len(df.columns)}** columns")
            
            # Preview
            with st.expander(f"{Icons.DATA} Data Preview (first 10 rows)", expanded=True):
                st.dataframe(df.head(10), use_container_width=True, height=300)
                
                # Stats basiques
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Lignes", f"{len(df):,}")
                with col2:
                    st.metric("Colonnes", len(df.columns))
                with col3:
                    memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
                    st.metric("Taille", f"{memory_mb:.1f} MB")
            
            st.markdown(f"### {Icons.MENU} Text Column Selection")
            
            text_columns = df.select_dtypes(include=['object']).columns.tolist()
            
            if text_columns:
                selected_column = st.selectbox(
                    "Choisissez la colonne contenant le texte des tweets:",
                    options=text_columns,
                    key='text_column_selector',
                    help="Sélectionnez la colonne principale à analyser"
                )
                
                st.session_state.selected_text_column = selected_column
                st.session_state.df_original = df
                
                # Aperçu du texte sélectionné
                sample_text = str(df[selected_column].iloc[0])
                st.info(f"""
**[i] Exemple de texte:**

{sample_text[:300]}{'...' if len(sample_text) > 300 else ''}
                """)
                
                # Stats colonne
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Textes non vides", f"{df[selected_column].notna().sum():,}")
                with col2:
                    avg_length = df[selected_column].astype(str).str.len().mean()
                    st.metric("Longueur moyenne", f"{avg_length:.0f} car.")
                with col3:
                    duplicates = df[selected_column].duplicated().sum()
                    st.metric("Doublons détectés", f"{duplicates:,}")
                
                # Cleaning button
                st.markdown(f"### {Icons.RIGHT} Start Cleaning")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    if st.button(f"{Icons.RIGHT} Clean and Prepare Data", type="primary", use_container_width=True, key='clean_btn'):
                        with st.spinner(f"{Icons.REFRESH} Cleaning in progress..."):
                            cleaner = TweetCleaner()
                            
                            progress_bar = st.progress(0)
                            progress_bar.progress(0.3)
                            
                            df_cleaned, stats = cleaner.process_dataframe(
                                df.copy(),
                                selected_column
                            )
                            
                            progress_bar.progress(1.0)
                            
                            st.session_state.df_cleaned = df_cleaned
                            st.session_state.cleaning_stats = stats
                            st.session_state.workflow_step = 'classify'
                            
                            st.success(f"{Icons.SUCCESS} Cleaning completed!")
                            time.sleep(1)
                            st.rerun()
                
                with col2:
                    if st.button(f"{Icons.REFRESH} Reset", use_container_width=True):
                        if 'df_original' in st.session_state:
                            del st.session_state['df_original']
                        st.rerun()
            else:
                st.error(f"{Icons.ERROR} No text column found")
                st.caption("Make sure your CSV contains at least one text column")
                
        except Exception as e:
            st.error(f"{Icons.ERROR} Loading error: {str(e)}")
            logger.error(f"Erreur upload: {e}", exc_info=True)
            
            with st.expander("[i] Détails de l'erreur"):
                st.code(str(e), language="text")

def _section_classification():
    """Section classification modernisée"""
    st.markdown(f"## {"[DASHBOARD]"} Étape 2 | Classification Intelligente Multi-Modèle")
    
    if 'df_cleaned' not in st.session_state:
        st.warning("[!] Aucune donnée nettoyée trouvée")
        if st.button("[←] Retour à l'upload", type="secondary"):
            st.session_state.workflow_step = 'upload'
            st.rerun()
        return
    
    df_cleaned = st.session_state.df_cleaned
    text_col = st.session_state.selected_text_column
    stats = st.session_state.get('cleaning_stats', {})
    
    # Résumé du nettoyage
    st.markdown(f"### {"[*]"} Résumé du Nettoyage")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Tweets Originaux",
            f"{stats.get('total_original', 0):,}"
        )
    
    with col2:
        st.metric(
            "Tweets Nettoyés",
            f"{stats.get('total_cleaned', 0):,}",
            delta=f"-{stats.get('duplicates_removed', 0):,} doublons",
            delta_color="inverse"
        )
    
    with col3:
        reduction_pct = (1 - stats.get('total_cleaned', 1)/stats.get('total_original', 1)) * 100 if stats.get('total_original', 0) > 0 else 0
        st.metric(
            "Réduction",
            f"{reduction_pct:.1f}%"
        )
    
    with col4:
        st.metric(
            "Prêt à classifier",
            f"{len(df_cleaned):,}",
            delta=f"{"[OK]"} Validé"
        )
    
    # Aperçu données nettoyées
    with st.expander("[▤] Aperçu des Données Nettoyées", expanded=False):
        key_cols = ['text_cleaned', 'date', 'time', 'content_type']
        available = [c for c in key_cols if c in df_cleaned.columns]
        
        if available:
            st.dataframe(df_cleaned[available].head(10), use_container_width=True, height=300)
        else:
            st.dataframe(df_cleaned.head(10), use_container_width=True, height=300)
    
    st.markdown("---")
    
    # Configuration de classification
    st.markdown("### [▶] Configuration de la Classification")
    
    config = st.session_state.config
    mode = config.get('mode', 'balanced')
    
    # Info du mode sélectionné
    mode_info = {
        'fast': {'icon': '⟩⟩', 'models': 'BERT + Règles', 'time': '~20 sec', 'precision': '75%'},
        'balanced': {'icon': "[*]", 'models': 'BERT + Règles + Mistral (échantillon 20%)', 'time': '~2 min', 'precision': '88%'},
        'precise': {'icon': "[O]", 'models': 'BERT + Mistral (complet)', 'time': '~10 min', 'precision': '95%'}
    }
    
    info = mode_info[mode]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info(f"""
**Mode {info['icon']} {mode.upper()} sélectionné**

• Dataset: **{len(df_cleaned):,}** tweets
• Modèles: {info['models']}
• Temps estimé: {info['time']}
• Précision: {info['precision']}
• KPIs calculés: **6** (Sentiment, Réclamation, Urgence, Thème, Incident, Confiance)
        """)
    
    with col2:
        # Option classificateur optimisé
        use_optimized = st.checkbox(
            "Utiliser Ultra-Optimisé V2",
            value=True,
            help="Version optimisée 3x plus rapide avec cache intelligent"
        )
        
        st.caption(f"{"[OK]"} Batch processing (50)")
        st.caption(f"{"[OK]"} Cache multi-niveau")
        st.caption(f"{"[OK]"} Sampling stratégique")
    
    # Lancement
    st.markdown("### [▶] Lancement")
    
    if st.button("[▶] Lancer la Classification Intelligente", type="primary", use_container_width=True, key='classify_btn'):
        progress_bar = st.progress(0, text="Initialisation...")
        status_placeholder = st.empty()
        metrics_placeholder = st.empty()
        
        try:
            if use_optimized:
                # Classificateur Ultra-Optimisé
                from services.ultra_optimized_classifier import UltraOptimizedClassifier
                
                status_placeholder.info("[→] Initialisation du classificateur ultra-optimisé...")
                
                classifier = UltraOptimizedClassifier(
                    batch_size=50,
                    max_workers=4,
                    use_cache=True,
                    enable_logging=True
                )
                
                # Callback
                def update_progress(message, progress_pct):
                    progress_bar.progress(progress_pct, text=message)
                    status_placeholder.info(f"[⟳] {message}")
                    
                    # Métriques temps réel
                    if hasattr(classifier, 'phase_times') and classifier.phase_times:
                        phases = "\n".join([f"• {phase}: {t:.1f}s" for phase, t in classifier.phase_times.items()])
                        metrics_placeholder.markdown(f"**Temps par phase:**\n{phases}")
                
                # Classification
                start = time.time()
                
                results, benchmark = classifier.classify_tweets_batch(
                    df_cleaned,
                    f'{text_col}_cleaned',
                    mode=mode,
                    progress_callback=update_progress
                )
                
                elapsed = time.time() - start
                
                # Stocker
                st.session_state.df_classified = results
                st.session_state.classification_report = {
                    'mode': mode,
                    'total_tweets': int(len(results)),
                    'time': float(elapsed),
                    'tweets_per_second': float(len(results) / elapsed if elapsed > 0 else 0),
                    'benchmark': benchmark.to_dict()
                }
                
                progress_bar.progress(1.0, text=f"{"[OK]"} Terminé!")
                status_placeholder.success(f"{"[OK]"} Classification réussie | **{len(results):,}** tweets en **{elapsed:.1f}s** (**{len(results)/elapsed:.1f}** tweets/s)")
                
                # Benchmark
                st.balloons()
                
                with st.expander(f"{"[*]"} Métriques de Performance", expanded=True):
                    st.markdown("#### Performance du Traitement")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "Vitesse",
                            f"{benchmark.tweets_per_second:.1f} tw/s"
                        )
                    
                    with col2:
                        st.metric(
                            "Temps Total",
                            f"{benchmark.total_time_seconds:.1f}s"
                        )
                    
                    with col3:
                        st.metric(
                            "Mémoire",
                            f"{benchmark.memory_mb:.0f} MB"
                        )
                    
                    with col4:
                        cache_rate = (benchmark.cache_hits / (benchmark.cache_hits + benchmark.cache_misses) * 100) if (benchmark.cache_hits + benchmark.cache_misses) > 0 else 0
                        st.metric(
                            "Cache Hit",
                            f"{cache_rate:.0f}%"
                        )
                    
                    st.markdown("#### Détails Techniques")
                    st.json(benchmark.to_dict())
                
            else:
                # Ancien classificateur
                orchestrator = MultiModelOrchestrator(mode=mode)
                
                def update_progress(message, progress_pct):
                    progress_bar.progress(progress_pct, text=message)
                    status_placeholder.info(f"[⟳] {message}")
                
                status_placeholder.info("[▤] Chargement des modèles...")
                orchestrator.load_models(progress_callback=update_progress)
                
                status_placeholder.info(f"{"[*]"} Classification en cours...")
                
                df_classified = orchestrator.classify_intelligent(
                    df_cleaned,
                    text_col,
                    progress_callback=update_progress
                )
                
                report = orchestrator.get_classification_report(df_classified)
                
                st.session_state.df_classified = df_classified
                st.session_state.classification_report = report
                st.session_state.classification_mode = mode
                
                progress_bar.progress(1.0, text=f"{"[OK]"} Terminé!")
                status_placeholder.success(f"{"[OK]"} **{len(df_classified):,}** tweets classifiés")
            
            # Passer aux résultats
            time.sleep(1)
            st.session_state.workflow_step = 'results'
            st.rerun()
            
        except Exception as e:
            st.error(f"{"[ERROR]"} Erreur lors de la classification")
            st.exception(e)
            logger.error(f"Erreur classification: {e}", exc_info=True)

def _section_results():
    """Section résultats ultra-moderne"""
    st.markdown(f"## {"[DASHBOARD]"} Étape 3 | Résultats et Export")
    
    df = st.session_state.df_classified
    report = st.session_state.get('classification_report', {})
    mode = st.session_state.get('classification_mode', 'balanced')
    
    # Header résultats
    mode_badges = {
        'fast': '⟩⟩ FAST',
        'balanced': f'{"[BALANCED]"} BALANCED',
        'precise': f'{"[PRECISE]"} PRECISE'
    }
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.info(f"**{mode_badges.get(mode, mode.upper())} | {len(df):,} tweets classifiés avec succès**")
    
    with col2:
        if 'benchmark' in report:
            bench = report['benchmark']
            st.metric(
                "Temps",
                f"{bench.get('total_time_seconds', report.get('time', 0)):.1f}s"
            )
    
    # KPIs
    st.markdown(f"### {"[*]"} Indicateurs Clés de Performance")
    
    kpis = _calculate_kpis_from_report(df, report)
    
    # Première ligne KPIs
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "KPI 1 | Réclamations",
            f"{kpis['claims_count']:,}",
            delta=f"{kpis['claims_percentage']:.1f}% du total"
        )
    
    with col2:
        st.metric(
            "KPI 2 | Sentiment Négatif",
            f"{kpis['negative_count']:,}",
            delta=f"{kpis['negative_percentage']:.1f}% du total"
        )
    
    with col3:
        st.metric(
            "KPI 3 | Urgence Critique",
            f"{kpis['urgence_critique_count']:,}",
            delta=f"{kpis['urgence_critique_percentage']:.1f}% du total"
        )
    
    # Deuxième ligne KPIs
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.metric(
            "KPI 4 | Confiance Moyenne",
            f"{kpis['confidence_avg']:.3f}",
            delta="Score de 0 à 1"
        )
    
    with col5:
        st.metric(
            "KPI 5 | Thème Principal",
            kpis['top_topic'],
            delta=f"{kpis['top_topic_count']:,} tweets"
        )
    
    with col6:
        st.metric(
            "KPI 6 | Incident Principal",
            kpis['top_incident'],
            delta=f"{kpis['top_incident_count']:,} tweets"
        )
    
    st.markdown("---")
    
    # NEW: Advanced Business KPIs (with role-based access)
    current_role = get_current_role() if ROLE_SYSTEM_AVAILABLE else "director"
    can_view_advanced = check_permission("access_advanced_analytics") if ROLE_SYSTEM_AVAILABLE else True
    
    if can_view_advanced or current_role in ["director", "data_analyst", "manager"]:
        st.markdown(f"### {Icons.CHART} Advanced Analytics Dashboard")
        _render_advanced_kpis(df, kpis)
        st.markdown("---")
    else:
        st.info(f"{Icons.INFO} Advanced Analytics available for Manager, Data Analyst, and Director roles")
    
    # Visualisations
    st.markdown(f"### {Icons.CHART} Interactive Visualizations")
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        f"{Icons.CHART} Sentiment",
        f"{Icons.DOT} Claims",
        f"{Icons.WARNING} Urgency",
        f"{Icons.DATA} Topics",
        f"{Icons.ERROR} Incidents",
        f"{Icons.PROGRESS} Confidence",
        f"{Icons.CHART} Time Series",
        f"{Icons.DASHBOARD} Multi-Analysis"
    ])
    
    with tab1:
        _render_sentiment_chart(df)
    
    with tab2:
        _render_claims_chart(df)
    
    with tab3:
        _render_urgence_chart(df)
    
    with tab4:
        _render_topics_chart(df)
    
    with tab5:
        _render_incidents_chart(df)
    
    with tab6:
        _render_distribution_chart(df)
    
    with tab7:
        _render_time_series_charts(df)
    
    with tab8:
        _render_multi_analysis(df)
    
    st.markdown("---")
    
    # Tableau des résultats
    st.markdown("### [▤] Données Classifiées")
    
    display_cols = ['text_cleaned', 'sentiment', 'is_claim', 'urgence', 'topics', 'incident', 'confidence']
    available_cols = [col for col in display_cols if col in df.columns]
    
    if available_cols:
        # Options d'affichage
        col1, col2 = st.columns([1, 3])
        
        with col1:
            n_rows = st.selectbox(
                "Lignes à afficher:",
                options=[10, 25, 50, 100, 500, len(df)],
                index=2,
                key='table_rows'
            )
        
        with col2:
            filter_col = st.selectbox(
                "Filtrer par:",
                options=['Tous'] + available_cols,
                key='filter_col'
            )
        
        # Filtrage
        df_display = df[available_cols]
        
        if filter_col != 'Tous':
            unique_vals = df_display[filter_col].unique().tolist()
            selected_val = st.multiselect(
                f"Valeurs de '{filter_col}':",
                options=unique_vals,
                default=unique_vals[:3] if len(unique_vals) >= 3 else unique_vals,
                key='filter_values'
            )
            
            if selected_val:
                df_display = df_display[df_display[filter_col].isin(selected_val)]
        
        st.dataframe(
            df_display.head(n_rows),
            use_container_width=True,
            height=450
        )
        
        st.caption(f"Affichage de {min(n_rows, len(df_display)):,} lignes sur {len(df):,} au total")
    else:
        st.warning("[!] Colonnes de résultats non disponibles")
    
    st.markdown("---")
    
    # Export (with role-based permissions)
    st.markdown(f"### {Icons.DOWNLOAD} Export Results")
    
    # Check export permissions
    current_role = get_current_role() if ROLE_SYSTEM_AVAILABLE else "director"
    can_export = check_permission("export_data") if ROLE_SYSTEM_AVAILABLE else True
    
    if not can_export:
        st.warning(f"{Icons.WARNING} Export permission required. Current role: {current_role}")
        st.info("Please contact your administrator to get export permissions.")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            f"{Icons.DOWNLOAD} Export CSV",
            csv,
            f"classification_{timestamp}.csv",
            "text/csv",
            use_container_width=True,
            key='export_csv'
        )
    
    with col2:
        from io import BytesIO
        buffer = BytesIO()
        
        # Clean DataFrame for Excel export (remove timezone-aware dates)
        df_excel = df.copy()
        for col in df_excel.columns:
            if df_excel[col].dtype == 'datetime64[ns, UTC]' or str(df_excel[col].dtype).startswith('datetime64'):
                try:
                    df_excel[col] = df_excel[col].dt.tz_localize(None)
                except:
                    try:
                        df_excel[col] = df_excel[col].dt.tz_convert(None)
                    except:
                        pass
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_excel.to_excel(writer, sheet_name='Classification', index=False)
            
            # Add KPIs sheet
            kpis_df = pd.DataFrame([kpis])
            kpis_df.to_excel(writer, sheet_name='KPIs', index=False)
        
        st.download_button(
            f"{Icons.DOWNLOAD} Export Excel",
            buffer.getvalue(),
            f"classification_{timestamp}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key='export_excel'
        )
    
    with col3:
        import json
        kpis_export = _calculate_kpis_from_report(df, report)
        stats_json = json.dumps(kpis_export, indent=2, ensure_ascii=False)
        
        st.download_button(
            f"{Icons.DOWNLOAD} Export JSON",
            stats_json.encode('utf-8'),
            f"kpis_{timestamp}.json",
            "application/json",
            use_container_width=True,
            key='export_json'
        )
    
    with col4:
        # Export complete report
        full_report = {
            'metadata': {
                'date': datetime.now().isoformat(),
                'mode': mode,
                'total_tweets': int(len(df)),
                'version': '4.1'
            },
            'kpis': kpis_export,
            'performance': report.get('benchmark', {})
        }
        
        report_json = json.dumps(full_report, indent=2, ensure_ascii=False)
        
        st.download_button(
            f"{Icons.DOWNLOAD} Full Report",
            report_json.encode('utf-8'),
            f"full_report_{timestamp}.json",
            "application/json",
            use_container_width=True,
            key='export_report'
        )
    
    # Actions
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("[↺] Nouvelle Classification", use_container_width=True):
            for key in ['df_cleaned', 'df_classified', 'classification_report', 'cleaning_stats']:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.workflow_step = 'upload'
            st.rerun()
    
    with col2:
        if st.button("[←] Retour à la classification", use_container_width=True):
            st.session_state.workflow_step = 'classify'
            st.rerun()
    
    with col3:
        if st.button("[STATS] Afficher les statistiques", use_container_width=True):
            with st.expander("Statistiques Détaillées", expanded=True):
                # Affichage formaté au lieu du JSON brut
                st.markdown("#### Réclamations")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Nombre", f"{kpis_export.get('claims_count', 0):,}")
                with col_b:
                    st.metric("Pourcentage", f"{kpis_export.get('claims_percentage', 0):.1f}%")
                
                st.markdown("#### Sentiment")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Négatifs", f"{kpis_export.get('negative_count', 0):,}")
                with col_b:
                    st.metric("Pourcentage", f"{kpis_export.get('negative_percentage', 0):.1f}%")
                
                if 'sentiment_distribution' in kpis_export:
                    st.caption("Distribution:")
                    for sent, count in kpis_export['sentiment_distribution'].items():
                        st.text(f"  - {sent}: {count:,}")
                
                st.markdown("#### Urgence Critique")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Nombre", f"{kpis_export.get('urgence_critique_count', 0):,}")
                with col_b:
                    st.metric("Pourcentage", f"{kpis_export.get('urgence_critique_percentage', 0):.1f}%")
                
                if 'urgence_distribution' in kpis_export:
                    st.caption("Distribution:")
                    for urg, count in kpis_export['urgence_distribution'].items():
                        st.text(f"  - {urg}: {count:,}")
                
                st.markdown("#### Confiance")
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Moyenne", f"{kpis_export.get('confidence_avg', 0):.3f}")
                with col_b:
                    st.metric("Min", f"{kpis_export.get('confidence_min', 0):.3f}")
                with col_c:
                    st.metric("Max", f"{kpis_export.get('confidence_max', 0):.3f}")
                
                st.markdown("#### Thème Principal")
                st.info(f"**{kpis_export.get('top_topic', 'N/A')}** ({kpis_export.get('top_topic_count', 0):,} tweets)")
                
                st.markdown("#### Incident Principal")
                st.info(f"**{kpis_export.get('top_incident', 'N/A')}** ({kpis_export.get('top_incident_count', 0):,} tweets)")

def _calculate_kpis_from_report(df, report):
    """Calcule tous les KPIs (types Python natifs pour JSON)"""
    kpis = {}
    
    # KPI 1: Réclamations
    if 'is_claim' in df.columns:
        claims = df[df['is_claim'] == 'oui']
        kpis['claims_count'] = int(len(claims))
        kpis['claims_percentage'] = float((len(claims) / len(df) * 100) if len(df) > 0 else 0)
    else:
        kpis['claims_count'] = 0
        kpis['claims_percentage'] = 0.0
    
    # KPI 2: Sentiment négatif
    if 'sentiment' in df.columns:
        negative = df[df['sentiment'] == 'negatif']
        kpis['negative_count'] = int(len(negative))
        kpis['negative_percentage'] = float((len(negative) / len(df) * 100) if len(df) > 0 else 0)
        
        # Distribution complète
        kpis['sentiment_distribution'] = {
            str(k): int(v) for k, v in df['sentiment'].value_counts().to_dict().items()
        }
    else:
        kpis['negative_count'] = 0
        kpis['negative_percentage'] = 0.0
        kpis['sentiment_distribution'] = {}
    
    # KPI 3: Urgence critique (CORRIGÉ: 'haute' au lieu de 'critique')
    if 'urgence' in df.columns:
        urgence_critique = df[df['urgence'] == 'haute']  # CORRECTION: 'haute' au lieu de 'critique'
        kpis['urgence_critique_count'] = int(len(urgence_critique))
        kpis['urgence_critique_percentage'] = float((len(urgence_critique) / len(df) * 100) if len(df) > 0 else 0)
        
        # Distribution complète
        kpis['urgence_distribution'] = {
            str(k): int(v) for k, v in df['urgence'].value_counts().to_dict().items()
        }
    else:
        kpis['urgence_critique_count'] = 0
        kpis['urgence_critique_percentage'] = 0.0
        kpis['urgence_distribution'] = {}
    
    # KPI 4: Confiance moyenne
    if 'confidence' in df.columns:
        kpis['confidence_avg'] = float(df['confidence'].mean())
        kpis['confidence_min'] = float(df['confidence'].min())
        kpis['confidence_max'] = float(df['confidence'].max())
        kpis['confidence_std'] = float(df['confidence'].std())
    else:
        kpis['confidence_avg'] = 0.0
        kpis['confidence_min'] = 0.0
        kpis['confidence_max'] = 0.0
        kpis['confidence_std'] = 0.0
    
    # KPI 5: Thème principal
    if 'topics' in df.columns:
        value_counts = df['topics'].value_counts()
        if len(value_counts) > 0:
            kpis['top_topic'] = str(value_counts.index[0])
            kpis['top_topic_count'] = int(value_counts.iloc[0])
            kpis['topics_distribution'] = {
                str(k): int(v) for k, v in value_counts.head(10).to_dict().items()
            }
        else:
            kpis['top_topic'] = 'N/A'
            kpis['top_topic_count'] = 0
            kpis['topics_distribution'] = {}
    else:
        kpis['top_topic'] = 'N/A'
        kpis['top_topic_count'] = 0
        kpis['topics_distribution'] = {}
    
    # KPI 6: Incident principal
    if 'incident' in df.columns:
        value_counts = df['incident'].value_counts()
        if len(value_counts) > 0:
            kpis['top_incident'] = str(value_counts.index[0])
            kpis['top_incident_count'] = int(value_counts.iloc[0])
            kpis['incidents_distribution'] = {
                str(k): int(v) for k, v in value_counts.head(10).to_dict().items()
            }
        else:
            kpis['top_incident'] = 'N/A'
            kpis['top_incident_count'] = 0
            kpis['incidents_distribution'] = {}
    else:
        kpis['top_incident'] = 'N/A'
        kpis['top_incident_count'] = 0
        kpis['incidents_distribution'] = {}
    
    return kpis

def _render_sentiment_chart(df):
    """Graphique sentiment moderne v4.0 avec interactivité avancée"""
    if 'sentiment' in df.columns:
        sentiment_counts = df['sentiment'].value_counts()
        
        # Couleurs modernes avec gradients
        colors = {
            'negatif': '#E74C3C',
            'neutre': '#95A5A6',
            'positif': '#27AE60'
        }
        
        # Graphique en barres avec animation
        fig = go.Figure(data=[go.Bar(
            x=sentiment_counts.index,
            y=sentiment_counts.values,
            marker=dict(
                color=[colors.get(s, '#95A5A6') for s in sentiment_counts.index],
                line=dict(color='rgba(0,0,0,0.2)', width=2)
            ),
            text=[f"<b>{v:,}</b><br>{v/len(df)*100:.1f}%" for v in sentiment_counts.values],
            textposition='outside',
            textfont=dict(size=14, family='Inter, sans-serif', color='#2C3E50'),
            hovertemplate='<b style="font-size: 16px;">%{x}</b><br>' +
                         '<b>Tweets:</b> %{y:,}<br>' +
                         '<b>Pourcentage:</b> %{customdata:.2f}%<extra></extra>',
            customdata=[v/len(df)*100 for v in sentiment_counts.values]
        )])
        
        fig.update_layout(
            title={
                'text': "<b>Distribution des Sentiments</b>",
                'font': {'size': 20, 'family': 'Inter, sans-serif', 'color': '#1E3A5F'},
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis=dict(
                title="<b>Catégorie de Sentiment</b>",
                titlefont=dict(size=14, family='Inter, sans-serif'),
                tickfont=dict(size=13, family='Inter, sans-serif'),
                showgrid=False
            ),
            yaxis=dict(
                title="<b>Nombre de Tweets</b>",
                titlefont=dict(size=14, family='Inter, sans-serif'),
                tickfont=dict(size=12, family='Inter, sans-serif'),
                gridcolor='rgba(0,0,0,0.05)'
            ),
            height=500,
            template="plotly_white",
            showlegend=False,
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=80, b=60, l=60, r=40)
        )
        
        # Animation
        fig.update_traces(marker_line_width=2)
        
        st.plotly_chart(fig, use_container_width=True, key='sentiment_chart', config={'displayModeBar': False})
        
        # Stats supplémentaires avec badges
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        for idx, (sentiment, count) in enumerate(sentiment_counts.items()):
            with [col1, col2, col3][idx % 3]:
                pct = count / len(df) * 100
                color = colors.get(sentiment, '#95A5A6')
                sentiment_str = str(sentiment).capitalize() if isinstance(sentiment, str) else str(sentiment)
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, {color}15 0%, {color}08 100%);
                            padding: 1rem; border-radius: 12px; border-left: 4px solid {color};
                            text-align: center;">
                    <div style="font-size: 0.9rem; font-weight: 700; color: #2C3E50; text-transform: uppercase; letter-spacing: 0.5px;">
                        {sentiment_str}
                    </div>
                    <div style="font-size: 1.8rem; font-weight: 800; color: {color}; margin: 0.5rem 0;">
                        {count:,}
                    </div>
                    <div style="font-size: 1rem; font-weight: 600; color: #2C3E50;">
                        {pct:.1f}%
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning(f"{"[WARNING]"} Colonne 'sentiment' non disponible dans les résultats")

def _render_claims_chart(df):
    """Graphique réclamations moderne"""
    if 'is_claim' in df.columns:
        claims_counts = df['is_claim'].value_counts()
        
        fig = go.Figure(data=[go.Pie(
            labels=claims_counts.index,
            values=claims_counts.values,
            marker_colors=['#E74C3C', '#10AC84'],
            hole=0.5,
            textinfo='label+percent',
            textfont_size=14,
            hovertemplate='<b>%{label}</b><br>Tweets: %{value:,}<br>Pourcentage: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title={
                'text': "Répartition Réclamations vs Non-Réclamations",
                'font': {'size': 18}
            },
            height=450,
            template="plotly_white",
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
        )
        
        st.plotly_chart(fig, use_container_width=True, key='claims_chart')
        
        # Stats
        col1, col2 = st.columns(2)
        for idx, (claim, count) in enumerate(claims_counts.items()):
            with [col1, col2][idx]:
                pct = count / len(df) * 100
                claim_str = str(claim).capitalize() if isinstance(claim, str) else str(claim)
                st.caption(f"**{claim_str}**: {count:,} ({pct:.1f}%)")
    else:
        st.warning("[!] Colonne 'is_claim' non disponible")

def _render_urgence_chart(df):
    """Graphique urgence moderne"""
    if 'urgence' in df.columns:
        urgence_counts = df['urgence'].value_counts()
        
        # Ordre logique
        order = ['faible', 'moyenne', 'critique']
        urgence_counts = urgence_counts.reindex(order, fill_value=0)
        
        colors = {
            'faible': '#10AC84',
            'moyenne': '#F79F1F',
            'critique': '#EE5A6F'
        }
        
        fig = go.Figure(data=[go.Bar(
            x=urgence_counts.index,
            y=urgence_counts.values,
            marker_color=[colors.get(u, '#95A5A6') for u in urgence_counts.index],
            text=[f"{v:,}<br>({v/len(df)*100:.1f}%)" for v in urgence_counts.values],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Tweets: %{y:,}<extra></extra>'
        )])
        
        fig.update_layout(
            title={
                'text': "Niveaux d'Urgence",
                'font': {'size': 18}
            },
            xaxis_title="Niveau d'Urgence",
            yaxis_title="Nombre de Tweets",
            height=450,
            template="plotly_white",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True, key='urgence_chart')
        
        # Stats
        col1, col2, col3 = st.columns(3)
        for idx, (urg, count) in enumerate(urgence_counts.items()):
            with [col1, col2, col3][idx]:
                pct = count / len(df) * 100 if len(df) > 0 else 0
                urg_str = str(urg).capitalize() if isinstance(urg, str) else str(urg)
                st.caption(f"**{urg_str}**: {count:,} ({pct:.1f}%)")
    else:
        st.warning("[!] Colonne 'urgence' non disponible")

def _render_topics_chart(df):
    """Graphique thèmes moderne"""
    if 'topics' in df.columns:
        topics_counts = df['topics'].value_counts().head(15)
        
        fig = go.Figure(data=[go.Bar(
            y=topics_counts.index,
            x=topics_counts.values,
            orientation='h',
            marker=dict(
                color=topics_counts.values,
                colorscale='Blues',
                showscale=False
            ),
            text=[f"{v:,} ({v/len(df)*100:.1f}%)" for v in topics_counts.values],
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>Tweets: %{x:,}<extra></extra>'
        )])
        
        fig.update_layout(
            title={
                'text': "Top 15 Thèmes Identifiés",
                'font': {'size': 18}
            },
            xaxis_title="Nombre de Tweets",
            yaxis_title="Thème",
            height=600,
            template="plotly_white",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True, key='topics_chart')
        
        st.caption(f"Total de {len(df['topics'].unique())} thèmes différents identifiés")
    else:
        st.warning("[!] Colonne 'topics' non disponible")

def _render_incidents_chart(df):
    """Graphique incidents moderne"""
    if 'incident' in df.columns:
        incidents_counts = df['incident'].value_counts().head(12)
        
        fig = go.Figure(data=[go.Pie(
            labels=incidents_counts.index,
            values=incidents_counts.values,
            marker_colors=px.colors.qualitative.Set3,
            textinfo='label+percent',
            textfont_size=12,
            hovertemplate='<b>%{label}</b><br>Tweets: %{value:,}<br>Pourcentage: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title={
                'text': "Distribution des Types d'Incidents (Top 12)",
                'font': {'size': 18}
            },
            height=550,
            template="plotly_white",
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.05
            )
        )
        
        st.plotly_chart(fig, use_container_width=True, key='incidents_chart')
        
        st.caption(f"Total de {len(df['incident'].unique())} types d'incidents identifiés")
    else:
        st.warning("[!] Colonne 'incident' non disponible")

def _render_role_management_tab():
    """Role Management Tab in Sidebar"""
    with st.expander(f"{Icons.SETTINGS} Role Management", expanded=False):
        st.markdown("#### 👤 User Role & Permissions")
        
        # Initialize role system
        role_manager, role_ui_manager = initialize_role_system()
        
        # Role selector
        roles = role_manager.get_all_roles()
        role_options = {role.display_name: role.role_id for role in roles}
        
        current_role = get_current_role()
        current_display = None
        if current_role:
            config = role_manager.get_role_config(current_role)
            current_display = config.display_name if config else None
        
        selected_display = st.selectbox(
            "Change role:",
            options=list(role_options.keys()),
            index=list(role_options.values()).index(current_role) if current_role and current_role in role_options.values() else 1,
            help="Select your role to adapt the interface",
            key='role_selector_mistral'
        )
        
        selected_role = role_options[selected_display]
        role_manager.set_current_role(selected_role)
        
        # Display role information
        role_config = role_manager.get_role_config(selected_role)
        if role_config:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {role_config.color}22 0%, {role_config.color}11 100%); 
                        padding: 1rem; border-radius: 8px; margin-top: 0.5rem; border-left: 4px solid {role_config.color};">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <i class="fas {role_config.icon}" style="color: {role_config.color}; font-size: 1.5rem; margin-right: 0.75rem;"></i>
                    <strong style="color: {role_config.color}; font-size: 1.1rem;">{role_config.display_name}</strong>
                </div>
                <p style="margin: 0; font-size: 0.85rem; color: #666; line-height: 1.4;">
                    {role_config.description}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Permissions summary
            st.markdown("**Key Permissions:**")
            key_perms = {
                'export_data': f'{Icons.DOWNLOAD} Export Data',
                'view_all_stats': f'{Icons.CHART} View All Stats',
                'access_advanced_analytics': f'{Icons.DASHBOARD} Advanced Analytics',
                'create_reports': f'{Icons.DOCUMENT} Create Reports'
            }
            
            for perm_key, perm_label in key_perms.items():
                has_perm = perm_key in role_config.permissions or "all" in role_config.permissions
                icon = Icons.SUCCESS if has_perm else Icons.ERROR
                color = "#10AC84" if has_perm else "#95A5A6"
                st.markdown(f"<span style='color: {color};'>{icon} {perm_label}</span>", unsafe_allow_html=True)
            
            # Features count
            st.caption(f"📦 {len(role_config.features)} features available")


def _render_distribution_chart(df):
    """Graphique distribution confiance moderne"""
    if 'confidence' in df.columns:
        # Histogramme + Courbe de densité
        fig = go.Figure()
        
        # Histogramme
        fig.add_trace(go.Histogram(
            x=df['confidence'],
            nbinsx=50,
            name='Distribution',
            marker_color='#2E86DE',
            opacity=0.7,
            hovertemplate='Score: %{x:.2f}<br>Nombre: %{y}<extra></extra>'
        ))
        
        fig.update_layout(
            title={
                'text': "Distribution du Score de Confiance",
                'font': {'size': 18}
            },
            xaxis_title="Score de Confiance (0-1)",
            yaxis_title="Nombre de Tweets",
            height=450,
            template="plotly_white",
            showlegend=False,
            bargap=0.1
        )
        
        # Ajouter ligne verticale pour la moyenne
        mean_conf = df['confidence'].mean()
        fig.add_vline(
            x=mean_conf,
            line_dash="dash",
            line_color="#E74C3C",
            annotation_text=f"Moyenne: {mean_conf:.3f}",
            annotation_position="top"
        )
        
        st.plotly_chart(fig, use_container_width=True, key='confidence_chart')
        
        # Statistiques
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.caption(f"**Moyenne**: {df['confidence'].mean():.3f}")
        with col2:
            st.caption(f"**Médiane**: {df['confidence'].median():.3f}")
        with col3:
            st.caption(f"**Min**: {df['confidence'].min():.3f}")
        with col4:
            st.caption(f"**Max**: {df['confidence'].max():.3f}")
    else:
        st.warning("[!] Colonne 'confidence' non disponible")

def _render_advanced_kpis(df: pd.DataFrame, kpis: dict):
    """Render advanced business KPIs"""
    from services.advanced_analytics import (
        calculate_thematic_distribution,
        calculate_satisfaction_index,
        calculate_urgency_rate,
        calculate_message_type_distribution
    )
    
    # Calculate new KPIs
    thematic_dist = calculate_thematic_distribution(df)
    satisfaction = calculate_satisfaction_index(df)
    urgency_data = calculate_urgency_rate(df)
    msg_types = calculate_message_type_distribution(df)
    
    # Display in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Thematic Distribution - Top category
        if thematic_dist:
            top_category = max(thematic_dist, key=thematic_dist.get)
            top_count = thematic_dist[top_category]
            st.metric(
                f"{Icons.DATA} Top Category",
                top_category,
                delta=f"{top_count} tweets",
                help="Most frequent service category"
            )
        else:
            st.metric(f"{Icons.DATA} Top Category", "N/A")
    
    with col2:
        # Customer Satisfaction Index
        sat_score = satisfaction['score']
        sat_level = satisfaction['level']
        color = "🟢" if sat_score >= 70 else "🟡" if sat_score >= 50 else "🔴"
        st.metric(
            f"{Icons.SUCCESS} Satisfaction Index",
            f"{sat_score}%",
            delta=f"{color} {sat_level}",
            help="Overall customer satisfaction (0-100)"
        )
    
    with col3:
        # Urgency Rate
        st.metric(
            f"{Icons.WARNING} Urgency Rate",
            f"{urgency_data['rate']}%",
            delta=f"{urgency_data['count']} critical",
            help="Proportion of high-urgency messages"
        )
    
    with col4:
        # Average Confidence (already calculated)
        st.metric(
            f"{Icons.PROGRESS} Avg Confidence",
            f"{kpis['confidence_avg']:.3f}",
            delta=f"σ={kpis.get('confidence_std', 0):.3f}",
            help="Mean confidence of classification model"
        )
    
    # Second row with distributions
    st.markdown("#### 📊 Detailed Distributions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Thematic distribution chart
        if thematic_dist:
            fig = go.Figure(data=[go.Bar(
                x=list(thematic_dist.keys()),
                y=list(thematic_dist.values()),
                marker_color='#2E86DE',
                text=list(thematic_dist.values()),
                textposition='outside'
            )])
            fig.update_layout(
                title="Distribution by Service Category",
                xaxis_title="Category",
                yaxis_title="Volume",
                height=300,
                template="plotly_white",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True, key='thematic_dist_chart')
    
    with col2:
        # Message type distribution
        if msg_types:
            fig = go.Figure(data=[go.Pie(
                labels=list(msg_types.keys()),
                values=list(msg_types.values()),
                marker_colors=['#E74C3C', '#F79F1F', '#2E86DE', '#10AC84'],
                hole=0.4
            )])
            fig.update_layout(
                title="Message Type Distribution",
                height=300,
                template="plotly_white"
            )
            st.plotly_chart(fig, use_container_width=True, key='msg_type_chart')


def _render_time_series_charts(df: pd.DataFrame):
    """Render time series evolution charts"""
    from services.advanced_analytics import generate_time_series_data
    
    st.markdown("### 📈 Time Series Analysis")
    st.caption("Evolution over time (simulated distribution)")
    
    # Generate time series data
    df_ts = generate_time_series_data(df)
    date_col = 'synthetic_date' if 'synthetic_date' in df_ts.columns else 'parsed_date'
    
    if date_col not in df_ts.columns:
        st.warning("No date information available for time series")
        return
    
    # Aggregate by date
    df_ts['date_only'] = df_ts[date_col].dt.date
    
    # Volume evolution
    volume_ts = df_ts.groupby('date_only').size().reset_index(name='volume')
    
    fig_volume = go.Figure()
    fig_volume.add_trace(go.Scatter(
        x=volume_ts['date_only'],
        y=volume_ts['volume'],
        mode='lines+markers',
        name='Volume',
        line=dict(color='#2E86DE', width=3),
        marker=dict(size=6)
    ))
    fig_volume.update_layout(
        title="📊 Message Volume Evolution",
        xaxis_title="Date",
        yaxis_title="Number of Messages",
        height=400,
        template="plotly_white",
        hovermode='x unified'
    )
    st.plotly_chart(fig_volume, use_container_width=True, key='volume_ts_chart')
    
    # Sentiment evolution
    if 'sentiment' in df_ts.columns:
        sentiment_ts = df_ts.groupby(['date_only', 'sentiment']).size().reset_index(name='count')
        sentiment_pivot = sentiment_ts.pivot(index='date_only', columns='sentiment', values='count').fillna(0)
        
        fig_sentiment = go.Figure()
        
        colors = {'positif': '#10AC84', 'neutre': '#95A5A6', 'negatif': '#E74C3C'}
        for sentiment in sentiment_pivot.columns:
            fig_sentiment.add_trace(go.Scatter(
                x=sentiment_pivot.index,
                y=sentiment_pivot[sentiment],
                mode='lines',
                name=sentiment.capitalize(),
                line=dict(color=colors.get(sentiment, '#2E86DE'), width=2),
                stackgroup='one'
            ))
        
        fig_sentiment.update_layout(
            title="😊 Sentiment Evolution (Stacked Area)",
            xaxis_title="Date",
            yaxis_title="Number of Messages",
            height=400,
            template="plotly_white",
            hovermode='x unified'
        )
        st.plotly_chart(fig_sentiment, use_container_width=True, key='sentiment_ts_chart')
    
    # Claims rate evolution
    if 'is_claim' in df_ts.columns:
        df_ts['is_claim_binary'] = (df_ts['is_claim'] == 'oui').astype(int)
        claims_ts = df_ts.groupby('date_only')['is_claim_binary'].agg(['sum', 'count']).reset_index()
        claims_ts['rate'] = (claims_ts['sum'] / claims_ts['count'] * 100).fillna(0)
        
        fig_claims = go.Figure()
        fig_claims.add_trace(go.Scatter(
            x=claims_ts['date_only'],
            y=claims_ts['rate'],
            mode='lines+markers',
            name='Claims Rate',
            line=dict(color='#E74C3C', width=3),
            marker=dict(size=6),
            fill='tozeroy',
            fillcolor='rgba(231, 76, 60, 0.1)'
        ))
        fig_claims.update_layout(
            title="📢 Claims Rate Evolution (%)",
            xaxis_title="Date",
            yaxis_title="Claims Rate (%)",
            height=400,
            template="plotly_white",
            hovermode='x unified'
        )
        st.plotly_chart(fig_claims, use_container_width=True, key='claims_ts_chart')


def _render_multi_analysis(df: pd.DataFrame):
    """Render multi-dimensional analysis with radar and comparative charts"""
    from services.advanced_analytics import create_radar_chart_data, calculate_response_priority_matrix
    
    st.markdown("### 🎯 Multi-Dimensional Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Radar chart - Performance by domain
        st.markdown("#### 🕸️ Performance Radar")
        radar_data = create_radar_chart_data(df)
        
        if radar_data:
            categories_list = list(radar_data.keys())
            values_list = list(radar_data.values())
            
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=values_list,
                theta=categories_list,
                fill='toself',
                fillcolor='rgba(46, 134, 222, 0.2)',
                line=dict(color='#2E86DE', width=2),
                marker=dict(size=8, color='#2E86DE'),
                name='Performance Score'
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100],
                        showticklabels=True,
                        ticks='outside'
                    )
                ),
                height=450,
                template="plotly_white",
                title="Performance Score by Category (0-100)"
            )
            st.plotly_chart(fig_radar, use_container_width=True, key='radar_chart')
        else:
            st.info("Insufficient data for radar chart")
    
    with col2:
        # Comparative histogram - Sentiment by category
        st.markdown("#### 📊 Comparative Analysis")
        
        if 'topics' in df.columns and 'sentiment' in df.columns:
            # Get top 5 topics
            top_topics = df['topics'].value_counts().head(5).index.tolist()
            df_top = df[df['topics'].isin(top_topics)]
            
            # Group by topic and sentiment
            comparison = df_top.groupby(['topics', 'sentiment']).size().reset_index(name='count')
            
            fig_comparison = px.bar(
                comparison,
                x='topics',
                y='count',
                color='sentiment',
                barmode='group',
                color_discrete_map={
                    'positif': '#10AC84',
                    'neutre': '#95A5A6',
                    'negatif': '#E74C3C'
                },
                title="Sentiment Distribution by Top 5 Topics"
            )
            fig_comparison.update_layout(
                height=450,
                template="plotly_white",
                xaxis_title="Topic",
                yaxis_title="Count",
                legend_title="Sentiment"
            )
            st.plotly_chart(fig_comparison, use_container_width=True, key='comparison_chart')
        else:
            st.info("Insufficient data for comparative analysis")
    
    # Priority matrix heatmap
    st.markdown("#### 🔥 Priority Response Matrix")
    st.caption("Urgency level vs Topic volume - Darker = Higher priority")
    
    matrix = calculate_response_priority_matrix(df)
    
    if not matrix.empty:
        # Take top 10 topics for readability
        if len(matrix) > 10:
            matrix = matrix.nlargest(10, matrix.sum(axis=1))
        
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=matrix.values,
            x=matrix.columns,
            y=matrix.index,
            colorscale='RdYlGn_r',  # Red for high priority
            text=matrix.values,
            texttemplate='%{text:.0f}',
            textfont={"size": 10},
            colorbar=dict(title="Volume")
        ))
        
        fig_heatmap.update_layout(
            title="Urgency vs Topic Heatmap",
            xaxis_title="Urgency Level",
            yaxis_title="Topic",
            height=500,
            template="plotly_white"
        )
        st.plotly_chart(fig_heatmap, use_container_width=True, key='heatmap_chart')
    else:
        st.info("Insufficient data for priority matrix")


def _render_error_page():
    """Page d'erreur professionnelle v4.0"""
    # En-tête d'erreur stylisé
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(238, 90, 111, 0.15) 0%, rgba(238, 90, 111, 0.08) 100%);
                padding: 2rem; border-radius: 16px; border-left: 5px solid var(--danger);
                box-shadow: 0 4px 16px rgba(238, 90, 111, 0.2); margin-bottom: 2rem;">
        <h2 style="color: var(--danger); margin: 0;">
            {"[ERROR]"} Erreur de Configuration Critique
        </h2>
        <p style="font-size: 1.1rem; color: var(--dark); margin-top: 0.5rem; font-weight: 500;">
            Les modules de classification n'ont pas pu être chargés. L'application ne peut pas démarrer.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Modules requis avec statut
    st.markdown("###  Modules Requis")
    
    modules = [
        ('services.tweet_cleaner', 'Nettoyage et prétraitement des tweets'),
        ('services.mistral_classifier', 'Classificateur Mistral AI (LLM)'),
        ('services.bert_classifier', 'Classificateur BERT (Deep Learning)'),
        ('services.rule_classifier', 'Classificateur par règles'),
        ('services.multi_model_orchestrator', 'Orchestrateur multi-modèles')
    ]
    
    for module, description in modules:
        st.error(f"{"[X]"} **{module}**\n\n{description}")
    
    st.markdown("---")
    
    # Détails de l'erreur
    if IMPORT_ERROR:
        with st.expander(f"{"[INFO]"} Détails Techniques de l'Erreur", expanded=True):
            st.code(IMPORT_ERROR, language="python")
            st.caption("Copiez cette erreur pour obtenir de l'aide")
    
    st.markdown("---")
    
    # Solutions avec étapes numérotées
    st.markdown("###  Solutions Recommandées")
    
    tab1, tab2, tab3 = st.tabs([
        "① Installation", 
        "② Structure", 
        "③ Redémarrage"
    ])
    
    with tab1:
        st.info("""
        **Étape 1: Vérifier et installer les dépendances**
        
        Exécutez cette commande dans votre terminal:
        """)
        st.code("pip install -r requirements_optimized.txt", language="bash")
        st.caption("Cette commande installera toutes les dépendances nécessaires")
    
    with tab2:
        st.info("""
        **Étape 2: Vérifier la structure du projet**
        
        Assurez-vous que votre structure de fichiers est correcte:
        """)
        st.code("""FreeMobilaChat/
└── streamlit_app/
    └── services/
        ├── __init__.py
        ├── tweet_cleaner.py
        ├── mistral_classifier.py
        ├── bert_classifier.py
        ├── rule_classifier.py
        └── multi_model_orchestrator.py""", language="text")
        st.caption("Tous ces fichiers doivent être présents")
    
    with tab3:
        st.info("""
        **Étape 3: Relancer l'application**
        
        Redémarrez l'application avec:
        """)
        st.code("streamlit run streamlit_app/app.py --server.port=8502", language="bash")
        st.caption("L'application devrait démarrer correctement")
    
    st.markdown("---")
    
    # Support
    st.warning(f"""
    {"[WARNING]"} **Besoin d'aide supplémentaire?**
    
    Si le problème persiste après avoir suivi toutes les étapes :
    1. Vérifiez la version de Python (3.8+ requis)
    2. Vérifiez que tous les fichiers sont bien présents
    3. Consultez le fichier README.md pour plus d'informations
    """)

if __name__ == '__main__':
    main()
