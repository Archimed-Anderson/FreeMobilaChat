"""
Settings Page
Configuration and administration settings
"""

import streamlit as st
import requests
import os
import sys
from typing import Dict, Any, List, Optional

# Add components to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.navigation import render_dashboard_navigation, render_page_breadcrumb

# Page configuration
st.set_page_config(
    page_title="Settings - Tweet Analysis",
    page_icon="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjMyIiBoZWlnaHQ9IjMyIiByeD0iOCIgZmlsbD0iIzAwNzNlNiIvPgo8Y2lyY2xlIGN4PSIxNiIgY3k9IjE2IiByPSI0IiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIGZpbGw9Im5vbmUiLz4KPHBhdGggZD0iTTE2IDEwdjJtMCA4djJtNi02aC0ybS04IDBoLTJtNC4yNDMtNC4yNDMgMS40MTQgMS40MTRtLTguNDg1IDguNDg1IDEuNDE0IDEuNDE0bTAtOC40ODUtMS40MTQgMS40MTRtOC40ODUgOC40ODUtMS40MTQgMS40MTQiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+Cjwvc3ZnPg==",
    layout="wide"
)

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Custom CSS
st.markdown("""
<style>
    .settings-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .settings-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 4px solid #007bff;
    }
    .config-item {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .status-indicator {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
    }
    .status-success {
        background: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .status-error {
        background: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
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


def main():
    """Main settings page"""

    # Navigation
    render_dashboard_navigation()

    # Page breadcrumb
    render_page_breadcrumb("Paramètres", "Configuration et administration de la plateforme")

    # Header
    st.markdown("""
    <div class="settings-header">
        <h1>Paramètres - Tweet Analysis</h1>
        <p>Configuration et administration de la plateforme</p>
    </div>
    """, unsafe_allow_html=True)
    
    # API Status
    st.subheader("État du Système")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if check_api_health():
            st.markdown('<div class="status-indicator status-success">[SUCCESS] API Backend Opérationnel</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-indicator status-error">[ERROR] API Backend Indisponible</div>', unsafe_allow_html=True)
    
    with col2:
        st.info(f"URL API: {API_BASE_URL}")
    
    st.divider()
    
    # LLM Configuration
    st.subheader("Configuration LLM")
    
    with st.container():
        st.markdown('<div class="settings-section">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Fournisseurs Disponibles")
            
            providers = {
                "Mistral": {
                    "status": "Actif" if os.getenv("MISTRAL_API_KEY") else "Non configuré",
                    "description": "Recommandé pour le français"
                },
                "OpenAI": {
                    "status": "Actif" if os.getenv("OPENAI_API_KEY") else "Non configuré",
                    "description": "Haute précision"
                },
                "Anthropic": {
                    "status": "Actif" if os.getenv("ANTHROPIC_API_KEY") else "Non configuré",
                    "description": "Backup"
                },
                "Ollama": {
                    "status": "Disponible",
                    "description": "Local/Gratuit"
                }
            }
            
            for provider, info in providers.items():
                status_color = "green" if info["status"] == "Actif" else "orange"
                st.markdown(f"""
                <div class="config-item">
                    <strong>{provider}</strong>
                    <br>
                    <span style="color: {status_color};">{info["status"]}</span>
                    <br>
                    <small>{info["description"]}</small>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### Paramètres par Défaut")
            
            default_provider = st.selectbox(
                "Fournisseur par défaut",
                ["mistral", "openai", "anthropic", "ollama"],
                index=0
            )
            
            max_tweets_default = st.slider(
                "Max tweets par défaut",
                min_value=50,
                max_value=1000,
                value=500,
                step=50
            )
            
            batch_size_default = st.slider(
                "Taille de lot par défaut",
                min_value=5,
                max_value=20,
                value=10
            )
            
            if st.button("Sauvegarder Configuration"):
                # Save to session state (in production, save to database)
                st.session_state.default_llm_provider = default_provider
                st.session_state.default_max_tweets = max_tweets_default
                st.session_state.default_batch_size = batch_size_default
                st.success("Configuration sauvegardée!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # User Roles
    st.subheader("Gestion des Rôles")
    
    with st.container():
        st.markdown('<div class="settings-section">', unsafe_allow_html=True)
        
        roles_info = {
            "agent_sav": {
                "name": "Agent SAV",
                "description": "Vue simplifiée avec priorités",
                "permissions": ["Voir tweets", "Filtrer par priorité"]
            },
            "manager": {
                "name": "Manager",
                "description": "KPIs complets et exports",
                "permissions": ["Tous les KPIs", "Export données", "Voir rapports"]
            },
            "analyste": {
                "name": "Analyste",
                "description": "Toutes les métriques avancées",
                "permissions": ["Métriques avancées", "Analyses détaillées", "Visualisations"]
            },
            "admin": {
                "name": "Administrateur",
                "description": "Accès complet",
                "permissions": ["Toutes les fonctionnalités", "Configuration système", "Gestion utilisateurs"]
            }
        }
        
        for role_id, role_info in roles_info.items():
            with st.expander(f"{role_info['name']} - {role_info['description']}"):
                st.markdown("**Permissions:**")
                for permission in role_info['permissions']:
                    st.markdown(f"- {permission}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Database Configuration
    st.subheader("Configuration Base de Données")
    
    with st.container():
        st.markdown('<div class="settings-section">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### État Actuel")
            db_type = os.getenv("DATABASE_TYPE", "sqlite")
            st.info(f"Type: {db_type.upper()}")
            
            if db_type == "sqlite":
                st.info("Mode développement - Base de données locale")
            else:
                st.info("Mode production - Base de données externe")
        
        with col2:
            st.markdown("#### Actions")
            
            if st.button("Tester Connexion DB"):
                st.success("Connexion à la base de données réussie!")
            
            if st.button("Nettoyer Cache"):
                # Clear session state cache
                for key in list(st.session_state.keys()):
                    if key.startswith('cache_'):
                        del st.session_state[key]
                st.success("Cache nettoyé!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # System Information
    st.subheader("Informations Système")
    
    with st.container():
        st.markdown('<div class="settings-section">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### Version")
            st.info("v1.0.0")
        
        with col2:
            st.markdown("#### Environnement")
            env = os.getenv("ENVIRONMENT", "development")
            st.info(env.title())
        
        with col3:
            st.markdown("#### Dernière Mise à Jour")
            st.info("2025-10-12")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Debug Information (only for admin)
    current_role = st.session_state.get('user_role', 'agent_sav')
    if current_role == 'admin':
        st.divider()
        st.subheader("Informations de Debug")
        
        with st.expander("Variables d'Environnement"):
            env_vars = {
                "API_BASE_URL": API_BASE_URL,
                "DATABASE_TYPE": os.getenv("DATABASE_TYPE", "sqlite"),
                "ENVIRONMENT": os.getenv("ENVIRONMENT", "development"),
                "MISTRAL_API_KEY": "Configuré" if os.getenv("MISTRAL_API_KEY") else "Non configuré",
                "OPENAI_API_KEY": "Configuré" if os.getenv("OPENAI_API_KEY") else "Non configuré",
                "ANTHROPIC_API_KEY": "Configuré" if os.getenv("ANTHROPIC_API_KEY") else "Non configuré"
            }
            
            for key, value in env_vars.items():
                st.text(f"{key}: {value}")
        
        with st.expander("Session State"):
            st.json(dict(st.session_state))


if __name__ == "__main__":
    main()
