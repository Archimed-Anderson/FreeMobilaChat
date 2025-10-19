"""
FreeMobilaChat - Professional Landing Page & Dashboard
Modern AI-powered tweet analysis platform with Free Mobile branding
"""

import streamlit as st
import pandas as pd
import requests
import time
import base64
from datetime import datetime
import os
import sys
from typing import Dict, Any, List, Optional

# Add components to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components.filters import FilterManager
from components.charts import ChartManager
from components.tables import TableManager
from components.navigation import render_dashboard_navigation, render_page_breadcrumb
from components.analysis_manager import render_analysis_workflow


def validate_tweet_file(df: pd.DataFrame) -> Dict[str, Any]:
    """Validate uploaded tweet file structure and content"""

    validation_result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'suggestions': []
    }

    # Check required columns
    required_columns = ['text']
    missing_required = [col for col in required_columns if col not in df.columns]

    if missing_required:
        validation_result['valid'] = False
        validation_result['errors'].append(f"Colonnes requises manquantes: {', '.join(missing_required)}")
        validation_result['suggestions'].append("Assurez-vous que votre fichier contient au minimum une colonne 'text'")

    # Check recommended columns
    recommended_columns = ['author', 'date', 'retweet_count', 'favorite_count']
    missing_recommended = [col for col in recommended_columns if col not in df.columns]

    if missing_recommended:
        validation_result['warnings'].append(f"Colonnes recommandées manquantes: {', '.join(missing_recommended)}")
        validation_result['suggestions'].append("Ajoutez les colonnes 'author', 'date' pour une meilleure analyse")

    # Check data quality
    if 'text' in df.columns:
        empty_texts = df['text'].isnull().sum()
        if empty_texts > 0:
            validation_result['warnings'].append(f"{empty_texts} tweets avec texte vide")
            validation_result['suggestions'].append("Supprimez les lignes avec des tweets vides")

        # Check text length
        if not df['text'].empty:
            avg_length = df['text'].str.len().mean()
            if avg_length < 10:
                validation_result['warnings'].append("Textes très courts détectés")
            elif avg_length > 500:
                validation_result['warnings'].append("Textes très longs détectés")

    # Check file size
    if len(df) > 10000:
        validation_result['warnings'].append(f"Fichier volumineux ({len(df)} lignes)")
        validation_result['suggestions'].append("Considérez limiter à 1000 tweets pour les premiers tests")
    elif len(df) < 10:
        validation_result['warnings'].append("Fichier très petit (moins de 10 tweets)")

    return validation_result

# Configuration page
st.set_page_config(
    page_title="FreeMobilaChat - AI-Powered Tweet Analysis",
    page_icon="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjMyIiBoZWlnaHQ9IjMyIiByeD0iOCIgZmlsbD0iIzAwNzNlNiIvPgo8cGF0aCBkPSJNOCAxMmg0djhoLTR2LTh6bTYgMGg0djhoLTR2LTh6bTYgMGg0djhoLTR2LTh6IiBmaWxsPSJ3aGl0ZSIvPgo8L3N2Zz4K",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://freemobilachat.com/help',
        'Report a bug': 'https://freemobilachat.com/support',
        'About': "# FreeMobilaChat\nProfessional AI-powered tweet analysis platform"
    }
)

# Initialize managers
if 'filter_manager' not in st.session_state:
    st.session_state.filter_manager = FilterManager()
if 'chart_manager' not in st.session_state:
    st.session_state.chart_manager = ChartManager()
if 'table_manager' not in st.session_state:
    st.session_state.table_manager = TableManager()

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# Modern Free Mobile-inspired CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* Global Styles */
    .main .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
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

    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, #DC143C 0%, #FF6B6B 100%);
        padding: 4rem 2rem;
        text-align: center;
        color: white;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 20px 20px;
    }

    .hero-logo {
        font-size: 3.5rem;
        font-weight: 800;
        font-family: 'Inter', sans-serif;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }

    .hero-tagline {
        font-size: 1.5rem;
        font-weight: 400;
        margin-bottom: 1rem;
        opacity: 0.95;
    }

    .hero-description {
        font-size: 1.1rem;
        font-weight: 300;
        max-width: 600px;
        margin: 0 auto 2rem auto;
        line-height: 1.6;
        opacity: 0.9;
    }

    .cta-button {
        background: white;
        color: #DC143C;
        padding: 1rem 2rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 1.1rem;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        text-decoration: none;
        display: inline-block;
        margin: 0.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }

    .cta-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }

    /* Modern button styling */
    .stButton > button {
        background: linear-gradient(135deg, #DC143C 0%, #FF6B6B 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(220, 20, 60, 0.2);
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(220, 20, 60, 0.3);
        background: linear-gradient(135deg, #B91C3C 0%, #FF5555 100%);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    /* Modern form styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border-radius: 8px;
        border: 2px solid #e1e5e9;
        padding: 0.75rem;
        transition: all 0.3s ease;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #DC143C;
        box-shadow: 0 0 0 3px rgba(220, 20, 60, 0.1);
    }

    /* Modern metrics styling */
    .metric-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid #e1e5e9;
        text-align: center;
        transition: all 0.3s ease;
    }

    .metric-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
    }

    /* Modern FAQ styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 12px;
        border: 1px solid #dee2e6;
        padding: 1rem;
        transition: all 0.3s ease;
    }

    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
        border-color: #DC143C;
        transform: translateY(-1px);
    }

    /* Modern footer styling */
    .footer-section {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        color: white;
        padding: 3rem 0;
        margin-top: 4rem;
    }

    .footer-content {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 2rem;
    }

    .footer-links {
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 2rem;
        margin-bottom: 2rem;
    }

    .footer-column {
        flex: 1;
        min-width: 250px;
    }

    .footer-column h4 {
        color: #DC143C;
        margin-bottom: 1rem;
        font-weight: 600;
    }

    .footer-column p, .footer-column li {
        color: #bdc3c7;
        line-height: 1.6;
        margin-bottom: 0.5rem;
    }

    /* Section Styles */
    .section {
        padding: 3rem 0;
        margin: 2rem 0;
    }

    .section-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #DC143C;
        text-align: center;
        margin-bottom: 3rem;
        font-family: 'Inter', sans-serif;
    }

    .section-subtitle {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 3rem;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }

    /* Feature Cards */
    .feature-card {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 8px 25px rgba(220, 20, 60, 0.1);
        border: 1px solid rgba(220, 20, 60, 0.1);
        transition: all 0.3s ease;
        height: 100%;
        margin-bottom: 2rem;
    }

    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(220, 20, 60, 0.2);
    }

    .feature-icon {
        font-size: 1.2rem;
        color: white;
        background: linear-gradient(135deg, #DC143C 0%, #FF6B6B 100%);
        padding: 1rem;
        border-radius: 50%;
        width: 4rem;
        height: 4rem;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1rem auto;
        font-weight: 700;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 15px rgba(220, 20, 60, 0.3);
    }

    .feature-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 1rem;
    }

    .feature-description {
        color: #666;
        line-height: 1.6;
        font-size: 0.95rem;
    }

    /* Pricing Cards */
    .pricing-card {
        background: white;
        border-radius: 20px;
        padding: 2.5rem 2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        border: 2px solid #f0f0f0;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        margin-bottom: 2rem;
        overflow: hidden;
    }

    .pricing-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(135deg, #DC143C 0%, #FF6B6B 100%);
        transform: scaleX(0);
        transition: transform 0.4s ease;
    }

    .pricing-card.featured {
        border-color: #DC143C;
        transform: scale(1.02);
        box-shadow: 0 15px 40px rgba(220, 20, 60, 0.15);
    }

    .pricing-card.featured::before {
        transform: scaleX(1);
    }

    .pricing-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(220, 20, 60, 0.12);
        border-color: rgba(220, 20, 60, 0.3);
    }

    .pricing-card:hover::before {
        transform: scaleX(1);
    }

    .pricing-badge {
        background: #DC143C;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        position: absolute;
        top: -10px;
        left: 50%;
        transform: translateX(-50%);
    }

    .pricing-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #333;
        margin-bottom: 1rem;
    }

    .pricing-price {
        font-size: 3rem;
        font-weight: 800;
        color: #DC143C;
        margin-bottom: 0.5rem;
    }

    .pricing-period {
        color: #666;
        margin-bottom: 2rem;
    }

    .pricing-features {
        list-style: none;
        padding: 0;
        margin: 2rem 0;
    }

    .pricing-features li {
        padding: 0.5rem 0;
        color: #666;
        border-bottom: 1px solid #f0f0f0;
    }

    .pricing-features li:last-child {
        border-bottom: none;
    }

    .pricing-features li::before {
        content: "✓";
        color: #DC143C;
        font-weight: bold;
        margin-right: 0.5rem;
    }

    /* Partner Logos */
    .partner-logo {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        margin-bottom: 1rem;
    }

    .partner-logo:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }

    .partner-name {
        font-size: 1.2rem;
        font-weight: 600;
        color: #333;
        margin-top: 1rem;
    }

    /* FAQ Styles */
    .faq-item {
        background: white;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
    }

    /* Footer */
    .footer {
        background: #333;
        color: white;
        padding: 3rem 0 2rem 0;
        margin-top: 4rem;
    }

    .footer-section {
        margin-bottom: 2rem;
    }

    .footer-title {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #DC143C;
    }

    .footer-link {
        color: #ccc;
        text-decoration: none;
        display: block;
        padding: 0.3rem 0;
        transition: color 0.3s ease;
    }

    .footer-link:hover {
        color: #DC143C;
    }

    /* Contact Form */
    .contact-form {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }

    /* Smooth animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
    }

    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    /* Apply animations */
    .feature-card {
        animation: fadeInUp 0.6s ease-out;
    }

    .pricing-card {
        animation: fadeInUp 0.8s ease-out;
    }

    .partner-logo {
        animation: slideInLeft 0.6s ease-out;
    }

    /* Responsive Design */
    @media (max-width: 1200px) {
        .hero-content h1 {
            font-size: 3rem;
        }
        .feature-card {
            margin-bottom: 1.5rem;
        }
    }

    @media (max-width: 768px) {
        .hero-logo {
            font-size: 2.2rem;
        }
        .hero-tagline {
            font-size: 1rem;
        }
        .section-title {
            font-size: 1.8rem;
        }
        .pricing-card {
            margin-bottom: 1.5rem;
            padding: 2rem 1.5rem;
        }
        .pricing-card.featured {
            transform: none;
        }
        .feature-icon {
            width: 3rem;
            height: 3rem;
            font-size: 1rem;
        }
        .partner-logo {
            padding: 1rem;
        }
        .footer-links {
            flex-direction: column;
            gap: 1.5rem;
        }
    }

    @media (max-width: 480px) {
        .hero-logo {
            font-size: 1.8rem;
        }
        .section-title {
            font-size: 1.5rem;
        }
        .pricing-card {
            padding: 1.5rem 1rem;
        }
        .feature-card {
            padding: 1.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)


def check_api_health() -> bool:
    """Check if API is available"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except (requests.exceptions.RequestException, requests.exceptions.Timeout, ConnectionError):
        return False


def render_sidebar_configuration():
    """Render the sidebar configuration that can be used in both landing and dashboard modes"""

    # Enhanced sidebar styling
    st.markdown("""
    <style>
        /* Sidebar Configuration Styles */
        .sidebar-section {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
            border-left: 4px solid #DC143C;
        }

        .sidebar-header {
            color: #DC143C;
            font-weight: 600;
            font-size: 1.2rem;
            margin-bottom: 1rem;
            text-align: center;
        }

        /* Enhanced File Uploader Styles */
        [data-testid="stFileUploader"] {
            background: #ffffff;
            border: 2px dashed #DC143C;
            border-radius: 12px;
            padding: 1.5rem;
            transition: all 0.3s ease;
        }

        [data-testid="stFileUploader"]:hover {
            background: #fef7f7;
            border-color: #B91C3C;
            box-shadow: 0 2px 8px rgba(220, 20, 60, 0.1);
        }

        [data-testid="stFileUploader"] section {
            border: none !important;
            background: transparent !important;
        }

        [data-testid="stFileUploader"] label {
            color: #666 !important;
            font-size: 0.9rem !important;
            font-weight: 500 !important;
        }

        [data-testid="stFileUploader"] button {
            background: #DC143C !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            padding: 0.5rem 1.5rem !important;
            font-weight: 500 !important;
            transition: background 0.3s ease !important;
        }

        [data-testid="stFileUploader"] button:hover {
            background: #B91C3C !important;
            box-shadow: 0 2px 6px rgba(220, 20, 60, 0.3) !important;
        }

        [data-testid="stFileUploader"] small {
            color: #999 !important;
            font-size: 0.75rem !important;
        }

        /* Role Selector Styles */
        .role-section {
            margin: 1.5rem 0;
        }

        .role-title {
            color: #333;
            font-weight: 600;
            font-size: 1rem;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        /* LLM Configuration Styles */
        .llm-section {
            margin: 1.5rem 0;
        }

        .llm-expandable {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 0.75rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .llm-expandable:hover {
            background: #e9ecef;
            border-color: #DC143C;
        }

        .llm-title {
            color: #DC143C;
            font-weight: 600;
            font-size: 1rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .file-info {
            background: #e8f5e8;
            border-radius: 6px;
            padding: 0.75rem;
            margin: 0.5rem 0;
            border-left: 3px solid #28a745;
        }

        .analysis-status {
            background: #e3f2fd;
            border-radius: 6px;
            padding: 0.75rem;
            margin: 0.5rem 0;
            border-left: 3px solid #2196f3;
        }
    </style>
    """, unsafe_allow_html=True)

    # Sidebar configuration
    with st.sidebar:
        st.markdown('<div class="sidebar-header">Configuration</div>', unsafe_allow_html=True)

        # Modern file upload section with enhanced styling
        st.markdown("""
        <div style="margin: 1rem 0 0.5rem 0;">
            <div style="color: #DC143C; font-weight: 600; font-size: 1rem; margin-bottom: 0.3rem;">
                📁 Charger vos données
            </div>
            <div style="color: #666; font-size: 0.85rem; margin-bottom: 0.8rem;">
                Formats: CSV, Excel • Max 200MB
            </div>
        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Glissez et déposez votre fichier ici",
            type=['csv', 'xlsx'],
            help="Formats supportés: CSV, Excel (.xlsx)\nFormat attendu: colonnes 'text', 'author', 'date', etc.",
            key="main_file_uploader",
            label_visibility="visible"
        )

        # Display file information if uploaded
        if uploaded_file is not None:
            try:
                import pandas as pd

                # Read file based on extension
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)

                # Display file info in a clean format
                st.markdown(f"""
                <div class="file-info">
                    <strong>📄 {uploaded_file.name}</strong><br>
                    📊 {len(df):,} lignes, {len(df.columns)} colonnes<br>
                    💾 {uploaded_file.size / 1024:.1f} KB
                </div>
                """, unsafe_allow_html=True)

                # Validate file using our validation function
                validation = validate_tweet_file(df)

                if validation['valid']:
                    st.success("Structure validée")
                else:
                    for error in validation['errors']:
                        st.error(f"Erreur: {error}")

                # Show warnings if any
                for warning in validation['warnings']:
                    st.warning(f"Attention: {warning}")

                # Store in session state
                st.session_state.uploaded_data = df
                st.session_state.uploaded_filename = uploaded_file.name

            except Exception as e:
                st.error(f"Erreur de lecture: {str(e)}")

        # User role selection with help icon
        st.markdown("""
        <div class="role-section">
            <div class="role-title">
                Rôle utilisateur
                <span style="color: #999; font-size: 0.8rem;">ⓘ</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        user_role = st.selectbox(
            "Rôle utilisateur",
            ["manager", "Agent SAV", "Analyste", "Admin"],
            index=0,
            help="Détermine les KPIs et fonctionnalités visibles",
            key="main_user_role",
            label_visibility="collapsed"
        )

        # Store user role in session state
        role_mapping = {
            "manager": "manager",
            "Agent SAV": "agent_sav",
            "Analyste": "analyste",
            "Admin": "admin"
        }
        st.session_state.user_role = role_mapping[user_role]
        st.session_state.user_role_display = user_role

        # LLM Configuration with expandable design
        st.markdown("""
        <div class="llm-section">
            <div class="llm-expandable">
                <div class="llm-title">
                    Configuration LLM
                    <span>▶</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("Configuration LLM", expanded=False):
            llm_provider = st.selectbox(
                "Fournisseur IA",
                ["Mistral", "OpenAI", "Anthropic", "Ollama"],
                index=0,
                help="Choisir le fournisseur IA pour l'analyse (Mistral recommandé pour le français)",
                key="main_llm_provider"
            )

            max_tweets = st.slider(
                "Nombre maximum de tweets à analyser",
                min_value=50,
                max_value=1000,
                value=500,
                step=50,
                help="Limiter le nombre pour contrôler les coûts d'analyse",
                key="main_max_tweets"
            )

            batch_size = st.slider(
                "Taille des lots de traitement",
                min_value=5,
                max_value=20,
                value=10,
                help="Nombre de tweets traités simultanément par l'IA",
                key="main_batch_size"
            )

            # Temperature/creativity setting
            temperature = st.slider(
                "Créativité de l'IA (Temperature)",
                min_value=0.0,
                max_value=1.0,
                value=0.3,
                step=0.1,
                help="Plus élevé = plus créatif, plus bas = plus précis",
                key="main_temperature"
            )

            # Store LLM config in session state
            st.session_state.llm_config = {
                "provider": llm_provider.lower(),
                "max_tweets": max_tweets,
                "batch_size": batch_size,
                "temperature": temperature
            }

        # Analysis launch section
        if uploaded_file is not None and 'uploaded_data' in st.session_state:
            st.markdown("---")

            if st.button("Démarrer l'analyse", type="primary", use_container_width=True, key="main_start_analysis"):
                with st.spinner("Démarrage de l'analyse..."):
                    # Prepare analysis configuration
                    analysis_config = {
                        "llm_provider": st.session_state.llm_config["provider"],
                        "max_tweets": st.session_state.llm_config["max_tweets"],
                        "batch_size": st.session_state.llm_config["batch_size"],
                        "temperature": st.session_state.llm_config["temperature"],
                        "user_role": st.session_state.user_role
                    }

                    # Start analysis using existing function
                    batch_id = upload_and_analyze_csv(uploaded_file, analysis_config)

                    if batch_id:
                        st.session_state.current_batch_id = batch_id
                        st.success("✅ Analyse démarrée avec succès!")
                        st.info("🔄 Redirection vers la page d'analyse...")
                        # Small delay to show the success message
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Erreur lors du démarrage de l'analyse")

            # Show current analysis status if any
            if 'current_batch_id' in st.session_state:
                batch_id = st.session_state.current_batch_id

                # Get status
                status = get_analysis_status(batch_id)
                if status:
                    # Progress indicator
                    total = status.get('total_tweets', 0)
                    analyzed = status.get('analyzed_tweets', 0)

                    if total > 0:
                        progress = analyzed / total
                        st.progress(progress)
                        st.caption(f"Progression: {analyzed}/{total} tweets ({progress*100:.1f}%)")

                    # Status badge
                    status_text = status.get('status', 'unknown')
                    if status_text == 'completed':
                        st.success("Analyse terminée")
                    elif status_text == 'processing':
                        st.info("Analyse en cours...")
                    else:
                        st.error("Erreur dans l'analyse")




def render_hero_section():
    """Render the hero section"""
    st.markdown("""
    <div class="hero-section">
        <div class="hero-logo">FreeMobilaChat</div>
        <div class="hero-tagline">AI-Powered Tweet Analysis Platform</div>
        <div class="hero-description">
            Transform your social media monitoring with advanced AI technology.
            Analyze sentiment, detect trends, and gain actionable insights from Twitter data
            with enterprise-grade security and performance.
        </div>
        <div style="margin-top: 2rem;">
            <a href="#features" class="cta-button">Explore Features</a>
            <a href="#pricing" class="cta-button" style="background: transparent; color: white; border: 2px solid white;">View Pricing</a>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_features_section():
    """Render the features section"""
    st.markdown('<div id="features" class="section">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">Powerful Features</h2>', unsafe_allow_html=True)
    st.markdown('<p class="section-subtitle">Discover what makes FreeMobilaChat the leading choice for social media analysis</p>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🧠</div>
            <div class="feature-title">AI-Powered Analysis</div>
            <div class="feature-description">
                Advanced sentiment analysis using Mistral AI, OpenAI, and Anthropic models
                for accurate emotion detection and context understanding.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">RT</div>
            <div class="feature-title">Real-Time Processing</div>
            <div class="feature-description">
                Process thousands of tweets in minutes with our optimized pipeline
                and real-time monitoring dashboard.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">ANALYTICS</div>
            <div class="feature-title">Advanced Analytics</div>
            <div class="feature-description">
                Comprehensive KPIs, trend analysis, and interactive visualizations
                to understand your social media performance.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">SECURE</div>
            <div class="feature-title">Enterprise Security</div>
            <div class="feature-description">
                Bank-grade security with encrypted data processing,
                role-based access control, and compliance standards.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Second row of features
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">TARGET</div>
            <div class="feature-title">Smart Categorization</div>
            <div class="feature-description">
                Automatic tweet categorization and priority scoring
                to focus on what matters most to your business.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">TRENDS</div>
            <div class="feature-title">Trend Detection</div>
            <div class="feature-description">
                Identify emerging trends and topics before they go viral
                with our predictive analytics engine.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">API</div>
            <div class="feature-title">API Integration</div>
            <div class="feature-description">
                Seamless integration with your existing tools through
                our comprehensive REST API and webhooks.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">MOBILE</div>
            <div class="feature-title">Multi-Platform</div>
            <div class="feature-description">
                Access your analytics anywhere with our responsive web interface
                and mobile-optimized dashboard.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def render_pricing_section():
    """Render the pricing section"""
    st.markdown('<div id="pricing" class="section">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">Choose Your Plan</h2>', unsafe_allow_html=True)
    st.markdown('<p class="section-subtitle">Flexible pricing options designed to scale with your business needs</p>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="pricing-card">
            <div class="pricing-title">Starter</div>
            <div class="pricing-price">€29</div>
            <div class="pricing-period">per month</div>
            <ul class="pricing-features">
                <li>Up to 1,000 tweets/month</li>
                <li>Basic sentiment analysis</li>
                <li>Standard dashboard</li>
                <li>Email support</li>
                <li>CSV export</li>
            </ul>
            <button class="cta-button" style="width: 100%; margin-top: 1rem;">Get Started</button>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="pricing-card">
            <div class="pricing-title">Professional</div>
            <div class="pricing-price">€79</div>
            <div class="pricing-period">per month</div>
            <ul class="pricing-features">
                <li>Up to 10,000 tweets/month</li>
                <li>Advanced AI analysis</li>
                <li>Custom categories</li>
                <li>Priority support</li>
                <li>API access</li>
                <li>Advanced analytics</li>
            </ul>
            <button class="cta-button" style="width: 100%; margin-top: 1rem;">Choose Pro</button>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="pricing-card featured">
            <div class="pricing-badge">Most Popular</div>
            <div class="pricing-title">Business</div>
            <div class="pricing-price">€199</div>
            <div class="pricing-period">per month</div>
            <ul class="pricing-features">
                <li>Up to 50,000 tweets/month</li>
                <li>Multi-model AI analysis</li>
                <li>Real-time monitoring</li>
                <li>24/7 support</li>
                <li>Full API access</li>
                <li>Custom integrations</li>
                <li>Team collaboration</li>
            </ul>
            <button class="cta-button" style="width: 100%; margin-top: 1rem; background: #DC143C; color: white;">Choose Business</button>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="pricing-card">
            <div class="pricing-title">Enterprise</div>
            <div class="pricing-price">Custom</div>
            <div class="pricing-period">contact us</div>
            <ul class="pricing-features">
                <li>Unlimited tweets</li>
                <li>Custom AI models</li>
                <li>Dedicated infrastructure</li>
                <li>Dedicated support</li>
                <li>Custom development</li>
                <li>SLA guarantees</li>
                <li>On-premise deployment</li>
            </ul>
            <button class="cta-button" style="width: 100%; margin-top: 1rem;">Contact Sales</button>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def render_partners_section():
    """Render the partners section"""
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">Powered by Leading AI Partners</h2>', unsafe_allow_html=True)
    st.markdown('<p class="section-subtitle">We partner with the world\'s most advanced AI companies to deliver exceptional results</p>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="partner-logo">
            <div style="font-size: 2.5rem; color: #FF7000; font-weight: bold;">AI</div>
            <div class="partner-name">Mistral AI</div>
            <div style="color: #666; font-size: 0.9rem; margin-top: 0.5rem;">
                Advanced French language processing and multilingual sentiment analysis
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="partner-logo">
            <div style="font-size: 2.5rem; color: #00A67E; font-weight: bold;">AI</div>
            <div class="partner-name">OpenAI</div>
            <div style="color: #666; font-size: 0.9rem; margin-top: 0.5rem;">
                GPT-powered analysis for complex context understanding and insights
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="partner-logo">
            <div style="font-size: 2.5rem; color: #D4A574; font-weight: bold;">AI</div>
            <div class="partner-name">Anthropic</div>
            <div style="color: #666; font-size: 0.9rem; margin-top: 0.5rem;">
                Claude AI for safe, reliable, and nuanced text analysis
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="partner-logo">
            <div style="font-size: 2.5rem; color: #0066CC; font-weight: bold;">DOCKER</div>
            <div class="partner-name">Docker</div>
            <div style="color: #666; font-size: 0.9rem; margin-top: 0.5rem;">
                Containerized deployment for scalable and reliable infrastructure
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def render_faq_section():
    """Render the FAQ section"""
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">Frequently Asked Questions</h2>', unsafe_allow_html=True)

    with st.expander("What makes FreeMobilaChat different from other social media analytics tools?"):
        st.markdown("""
        FreeMobilaChat combines multiple state-of-the-art AI models (Mistral AI, OpenAI, Anthropic) to provide
        the most accurate sentiment analysis available. Our platform is specifically optimized for French language
        processing and offers real-time analysis with enterprise-grade security.
        """)

    with st.expander("Security: How secure is my data?"):
        st.markdown("""
        We implement bank-grade security measures including end-to-end encryption, role-based access control,
        and compliance with GDPR and other international data protection standards. Your data is processed
        securely and never shared with third parties.
        """)

    with st.expander("Performance: How fast is the analysis process?"):
        st.markdown("""
        Our optimized pipeline can process thousands of tweets in minutes. The exact speed depends on your plan
        and the complexity of analysis requested. Real-time monitoring provides live updates on processing status.
        """)

    with st.expander("Integration: Can I integrate FreeMobilaChat with my existing tools?"):
        st.markdown("""
        Yes! We provide a comprehensive REST API and webhook system for seamless integration with your existing
        workflow. Popular integrations include Slack, Microsoft Teams, Salesforce, and custom dashboards.
        """)

    with st.expander("Pricing: How is pricing calculated?"):
        st.markdown("""
        Pricing is based on the number of tweets analyzed per month and the features you need. We offer
        transparent pricing with no hidden fees. Enterprise customers can get custom pricing based on volume
        and specific requirements.
        """)

    with st.expander("What languages are supported?"):
        st.markdown("""
        While optimized for French, FreeMobilaChat supports analysis in multiple languages including English,
        Spanish, German, Italian, and more. Our AI models are trained on multilingual datasets for accurate
        cross-language sentiment analysis.
        """)

    st.markdown('</div>', unsafe_allow_html=True)


def render_footer():
    """Render the footer section"""
    # Add additional CSS to ensure footer styles are loaded
    st.markdown("""
    <style>
    /* Footer specific styles - ensuring they are loaded */
    .footer {
        background: #333 !important;
        color: white !important;
        padding: 3rem 0 2rem 0 !important;
        margin-top: 4rem !important;
    }

    .footer-section {
        margin-bottom: 2rem !important;
    }

    .footer-title {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        margin-bottom: 1rem !important;
        color: #DC143C !important;
    }

    .footer-link {
        color: #ccc !important;
        text-decoration: none !important;
        display: block !important;
        padding: 0.3rem 0 !important;
        transition: color 0.3s ease !important;
    }

    .footer-link:hover {
        color: #DC143C !important;
    }
    </style>

    <div class="footer">
        <div style="max-width: 1200px; margin: 0 auto; padding: 0 2rem;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem;">

                <div class="footer-section">
                    <div class="footer-title">Nous Contacter</div>
                    <div style="color: #ccc; line-height: 1.6;">
                        <p style="margin: 0.5rem 0; color: #ccc;">Email: contact@freemobilachat.com</p>
                        <p style="margin: 0.5rem 0; color: #ccc;">Téléphone: +33 1 23 45 67 89</p>
                        <p style="margin: 0.5rem 0; color: #ccc;">Adresse: 123 Avenue des Champs-Élysées<br>75008 Paris, France</p>
                    </div>
                </div>

                <div class="footer-section">
                    <div class="footer-title">Produit</div>
                    <a href="#features" class="footer-link">Fonctionnalités</a>
                    <a href="#pricing" class="footer-link">Tarifs</a>
                    <a href="/api/docs" class="footer-link">Documentation API</a>
                    <a href="/integrations" class="footer-link">Intégrations</a>
                </div>

                <div class="footer-section">
                    <div class="footer-title">Entreprise</div>
                    <a href="/about" class="footer-link">À Propos</a>
                    <a href="/careers" class="footer-link">Carrières</a>
                    <a href="/blog" class="footer-link">Blog</a>
                    <a href="/press" class="footer-link">Kit Presse</a>
                </div>

                <div class="footer-section">
                    <div class="footer-title">Légal</div>
                    <a href="/privacy" class="footer-link">Politique de Confidentialité</a>
                    <a href="/terms" class="footer-link">Conditions d'Utilisation</a>
                    <a href="/security" class="footer-link">Sécurité</a>
                    <a href="/compliance" class="footer-link">Conformité</a>
                </div>

            </div>

            <div style="border-top: 1px solid #555; margin-top: 2rem; padding-top: 2rem; text-align: center;">
                <div style="display: flex; justify-content: center; gap: 2rem; margin-bottom: 1rem; flex-wrap: wrap;">
                    <a href="https://twitter.com/freemobilachat" class="footer-link" style="display: inline-block;">Twitter</a>
                    <a href="https://linkedin.com/company/freemobilachat" class="footer-link" style="display: inline-block;">LinkedIn</a>
                    <a href="https://github.com/freemobilachat" class="footer-link" style="display: inline-block;">GitHub</a>
                    <a href="https://youtube.com/freemobilachat" class="footer-link" style="display: inline-block;">YouTube</a>
                </div>
                <p style="color: #999; font-size: 0.9rem; margin: 1rem 0;">
                    © 2025 FreeMobilaChat. Tous droits réservés. | Fait avec amour en France
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def upload_and_analyze_csv(file, analysis_config: Dict[str, Any]) -> Optional[str]:
    """
    Upload CSV file and start analysis
    
    Args:
        file: Uploaded file object
        analysis_config: Analysis configuration
        
    Returns:
        Batch ID if successful, None otherwise
    """
    try:
        # Prepare files and data for upload
        files = {"file": (file.name, file.getvalue(), "text/csv")}
        data = {
            "llm_provider": analysis_config["llm_provider"],
            "max_tweets": analysis_config["max_tweets"],
            "batch_size": analysis_config["batch_size"],
            "user_role": analysis_config["user_role"]
        }
        
        # Upload file with extended timeout for large files
        response = requests.post(
            f"{API_BASE_URL}/upload-csv",
            files=files,
            data=data,
            timeout=120  # Extended timeout: 2 minutes for upload + validation
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("batch_id")
        else:
            st.error(f"Upload error: {response.text}")
            return None

    except Exception as e:
        st.error(f"Upload error: {str(e)}")
        return None


def get_analysis_status(batch_id: str) -> Optional[Dict[str, Any]]:
    """Get analysis status for batch"""
    try:
        response = requests.get(f"{API_BASE_URL}/analysis-status/{batch_id}")
        if response.status_code == 200:
            return response.json()
        return None
    except (requests.exceptions.RequestException, Exception):
        return None


def get_kpis(batch_id: str, user_role: str) -> Optional[Dict[str, Any]]:
    """Get KPIs for batch"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/kpis/{batch_id}",
            params={"user_role": user_role}
        )
        if response.status_code == 200:
            return response.json()
        return None
    except (requests.exceptions.RequestException, Exception):
        return None


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
    except (requests.exceptions.RequestException, Exception):
        return None


def render_contact_form():
    """Render contact form"""
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">Nous Contacter</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<div class="contact-form">', unsafe_allow_html=True)
        st.subheader("Envoyez-nous un message")

        with st.form("contact_form"):
            name = st.text_input("Nom complet *", placeholder="Entrez votre nom complet")
            email = st.text_input("Adresse email *", placeholder="Entrez votre adresse email")
            subject = st.selectbox("Sujet *", [
                "Demande générale",
                "Question commerciale",
                "Support technique",
                "Opportunité de partenariat",
                "Demande de fonctionnalité",
                "Autre"
            ])
            message = st.text_area("Message *", placeholder="Dites-nous comment nous pouvons vous aider...", height=120)

            submitted = st.form_submit_button("Envoyer le message", use_container_width=True)

            if submitted:
                if name and email and subject and message:
                    st.success(f"Merci pour votre message concernant '{subject}' ! Nous vous répondrons dans les 24 heures.")
                else:
                    st.error("Veuillez remplir tous les champs obligatoires.")

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="padding: 2rem 0;">
            <h4 style="color: #DC143C; margin-bottom: 1rem;">Pourquoi choisir FreeMobilaChat ?</h4>
            <ul style="color: #666; line-height: 1.8; list-style-type: disc; padding-left: 1.5rem;">
                <li>Garantie de disponibilité 99.9%</li>
                <li>Support client 24/7</li>
                <li>Conforme RGPD</li>
                <li>Sécurité entreprise</li>
                <li>Essai gratuit disponible</li>
                <li>Aucun frais d'installation</li>
            </ul>

            <div style="margin-top: 2rem; padding: 1.5rem; background: #f8f9fa; border-radius: 10px;">
                <h5 style="color: #DC143C; margin-bottom: 1rem;">Statistiques Clés</h5>
                <div style="color: #666;">
                    <p><strong>1M+</strong> tweets analysés quotidiennement</p>
                    <p><strong>500+</strong> clients satisfaits</p>
                    <p><strong>99.2%</strong> taux de précision</p>
                    <p><strong>15+</strong> langues supportées</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)








def main():
    """Main application - Unified landing page with dashboard functionality"""

    # Check if user has uploaded a file and should be redirected to analysis
    if 'uploaded_data' in st.session_state and 'current_batch_id' in st.session_state:
        # User has uploaded data and analysis is running/completed
        # Redirect to Analysis page
        st.switch_page("pages/2_Analysis.py")
        return

    # Render sidebar configuration (always visible with all dashboard features)
    render_sidebar_configuration()

    # Main content - Landing page with all sections
    render_hero_section()
    render_features_section()
    render_pricing_section()
    render_partners_section()
    render_faq_section()
    render_contact_form()
    render_footer()


if __name__ == "__main__":
    main()
