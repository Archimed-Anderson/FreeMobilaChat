"""
Composants UI modernes pour l'application
Interface utilisateur professionnelle avec animations
"""

import streamlit as st
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..config.settings import get_config, get_user_role, UserRole
from ..config.api_config import get_api_client, test_all_connections
from ..utils.helpers import get_current_timestamp, create_metric_card, create_status_badge

def render_modern_header(title: str, subtitle: str, show_connection_status: bool = False):
    """Affiche un header moderne avec statut de connexion"""
    
    # CSS pour le header
    st.markdown("""
    <style>
    .modern-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .modern-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        opacity: 0.3;
    }
    
    .header-content {
        position: relative;
        z-index: 1;
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        font-family: 'Inter', sans-serif;
    }
    
    .header-subtitle {
        font-size: 1.2rem;
        font-weight: 400;
        opacity: 0.95;
        margin-bottom: 1rem;
    }
    
    .connection-status {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(255, 255, 255, 0.2);
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.9rem;
        backdrop-filter: blur(10px);
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #4ade80;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .header-actions {
        margin-top: 1rem;
        display: flex;
        gap: 1rem;
        justify-content: center;
        flex-wrap: wrap;
    }
    
    .action-btn {
        background: rgba(255, 255, 255, 0.2);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 0.5rem 1rem;
        border-radius: 25px;
        text-decoration: none;
        font-weight: 500;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .action-btn:hover {
        background: rgba(255, 255, 255, 0.3);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Contenu du header
    status_html = ""
    if show_connection_status:
        connections = test_all_connections()
        backend_status = "" if connections.get("backend", False) else ""
        ollama_status = "" if connections.get("ollama", False) else ""
        
        status_html = f"""
        <div class="connection-status">
            <div class="status-dot"></div>
            <span>Backend: {backend_status} | Ollama: {ollama_status}</span>
        </div>
        """
    
    header_html = f"""
    <div class="modern-header">
        <div class="header-content">
            <div class="header-title">{title}</div>
            <div class="header-subtitle">{subtitle}</div>
            {status_html}
            <div class="header-actions">
                <a href="#" class="action-btn"> Dashboard</a>
                <a href="#" class="action-btn"> Paramètres</a>
                <a href="#" class="action-btn"> Aide</a>
            </div>
        </div>
    </div>
    """
    
    st.markdown(header_html, unsafe_allow_html=True)

def render_metrics_dashboard(metrics: Dict[str, Any]):
    """Affiche un dashboard de métriques moderne"""
    
    # CSS pour les métriques
    st.markdown("""
    <style>
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid #e1e5e9;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
    }
    
    .metric-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: #333;
        margin-bottom: 0.5rem;
        font-family: 'Inter', sans-serif;
    }
    
    .metric-delta {
        font-size: 0.8rem;
        font-weight: 600;
        padding: 0.2rem 0.5rem;
        border-radius: 12px;
        display: inline-block;
    }
    
    .delta-positive {
        background: #d4edda;
        color: #155724;
    }
    
    .delta-negative {
        background: #f8d7da;
        color: #721c24;
    }
    
    .delta-neutral {
        background: #d1ecf1;
        color: #0c5460;
    }
    
    .metric-icon {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
        display: block;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Affichage des métriques
    if not metrics:
        st.info("Aucune métrique disponible")
        return
    
    # Création des cartes de métriques
    metric_cards = []
    
    for key, value in metrics.items():
        if isinstance(value, dict):
            title = value.get("title", key.replace("_", " ").title())
            val = value.get("value", 0)
            delta = value.get("delta")
            delta_color = value.get("delta_color", "neutral")
            icon = value.get("icon", "")
        else:
            title = key.replace("_", " ").title()
            val = value
            delta = None
            delta_color = "neutral"
            icon = ""
        
        delta_html = ""
        if delta:
            delta_html = f'<div class="metric-delta delta-{delta_color}">{delta}</div>'
        
        card_html = f"""
        <div class="metric-card">
            <div class="metric-icon">{icon}</div>
            <div class="metric-title">{title}</div>
            <div class="metric-value">{val}</div>
            {delta_html}
        </div>
        """
        
        metric_cards.append(card_html)
    
    # Affichage en grille
    st.markdown(f"""
    <div class="metrics-grid">
        {''.join(metric_cards)}
    </div>
    """, unsafe_allow_html=True)

def render_loading_spinner(message: str = "Chargement...", size: str = "large"):
    """Affiche un spinner de chargement moderne"""
    
    # CSS pour le spinner
    st.markdown("""
    <style>
    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        text-align: center;
    }
    
    .spinner {
        width: 40px;
        height: 40px;
        border: 4px solid #f3f3f3;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 1rem;
    }
    
    .spinner-large {
        width: 60px;
        height: 60px;
        border-width: 6px;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .loading-message {
        font-size: 1.1rem;
        font-weight: 500;
        color: #666;
        margin-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    size_class = "spinner-large" if size == "large" else "spinner"
    
    spinner_html = f"""
    <div class="loading-container">
        <div class="spinner {size_class}"></div>
        <div class="loading-message">{message}</div>
    </div>
    """
    
    st.markdown(spinner_html, unsafe_allow_html=True)

def render_progress_bar(progress: float, message: str = "", show_percentage: bool = True):
    """Affiche une barre de progression moderne"""
    
    # CSS pour la barre de progression
    st.markdown("""
    <style>
    .progress-container {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .progress-bar {
        width: 100%;
        height: 8px;
        background: #e9ecef;
        border-radius: 4px;
        overflow: hidden;
        margin-bottom: 0.5rem;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 4px;
        transition: width 0.3s ease;
        position: relative;
    }
    
    .progress-fill::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .progress-message {
        font-size: 0.9rem;
        color: #666;
        margin-bottom: 0.5rem;
    }
    
    .progress-percentage {
        font-size: 0.8rem;
        color: #999;
        text-align: right;
    }
    </style>
    """, unsafe_allow_html=True)
    
    percentage_text = f"{progress:.1f}%" if show_percentage else ""
    
    progress_html = f"""
    <div class="progress-container">
        <div class="progress-message">{message}</div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {progress * 100}%"></div>
        </div>
        <div class="progress-percentage">{percentage_text}</div>
    </div>
    """
    
    st.markdown(progress_html, unsafe_allow_html=True)

def render_error_message(error: str, suggestions: List[str] = None):
    """Affiche un message d'erreur avec suggestions"""
    
    # CSS pour les erreurs
    st.markdown("""
    <style>
    .error-container {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #721c24;
    }
    
    .error-title {
        font-weight: 600;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .error-message {
        margin-bottom: 1rem;
    }
    
    .error-suggestions {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 6px;
        padding: 0.75rem;
        margin-top: 1rem;
    }
    
    .suggestion-title {
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #856404;
    }
    
    .suggestion-list {
        margin: 0;
        padding-left: 1.5rem;
    }
    
    .suggestion-item {
        margin-bottom: 0.25rem;
        color: #856404;
    }
    </style>
    """, unsafe_allow_html=True)
    
    suggestions_html = ""
    if suggestions:
        suggestions_list = "".join([f"<li class='suggestion-item'>{s}</li>" for s in suggestions])
        suggestions_html = f"""
        <div class="error-suggestions">
            <div class="suggestion-title"> Suggestions :</div>
            <ul class="suggestion-list">
                {suggestions_list}
            </ul>
        </div>
        """
    
    error_html = f"""
    <div class="error-container">
        <div class="error-title">
             Erreur
        </div>
        <div class="error-message">{error}</div>
        {suggestions_html}
    </div>
    """
    
    st.markdown(error_html, unsafe_allow_html=True)

def render_success_message(message: str, details: str = None):
    """Affiche un message de succès"""
    
    # CSS pour les messages de succès
    st.markdown("""
    <style>
    .success-container {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #155724;
    }
    
    .success-title {
        font-weight: 600;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .success-message {
        margin-bottom: 0.5rem;
    }
    
    .success-details {
        font-size: 0.9rem;
        opacity: 0.8;
    }
    </style>
    """, unsafe_allow_html=True)
    
    details_html = f"<div class='success-details'>{details}</div>" if details else ""
    
    success_html = f"""
    <div class="success-container">
        <div class="success-title">
             Succès
        </div>
        <div class="success-message">{message}</div>
        {details_html}
    </div>
    """
    
    st.markdown(success_html, unsafe_allow_html=True)

def render_info_card(title: str, content: str, icon: str = "ℹ"):
    """Affiche une carte d'information"""
    
    # CSS pour les cartes d'information
    st.markdown("""
    <style>
    .info-card {
        background: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #0c5460;
    }
    
    .info-title {
        font-weight: 600;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .info-content {
        line-height: 1.5;
    }
    </style>
    """, unsafe_allow_html=True)
    
    info_html = f"""
    <div class="info-card">
        <div class="info-title">
            {icon} {title}
        </div>
        <div class="info-content">{content}</div>
    </div>
    """
    
    st.markdown(info_html, unsafe_allow_html=True)
