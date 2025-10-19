"""
Chatbot SAV Page
Interface conversationnelle intelligente pour le service après-vente Free Mobile
"""

import streamlit as st
import requests
import json
import os
import sys
import time
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add components to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.navigation import render_dashboard_navigation, render_page_breadcrumb

# Streamlit Chat import (à installer: pip install streamlit-chat)
try:
    from streamlit_chat import message
    CHAT_AVAILABLE = True
except ImportError:
    CHAT_AVAILABLE = False
    st.error("⚠️ streamlit-chat non installé. Exécutez: pip install streamlit-chat")

# Page configuration
st.set_page_config(
    page_title="Chatbot SAV - FreeMobilaChat",
    page_icon="💬",
    layout="wide"
)

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Free Mobile branding colors
FREE_MOBILE_RED = "#DC143C"
FREE_MOBILE_DARK = "#8B0000"

# Custom CSS pour le design Free Mobile
st.markdown(f"""
<style>
    /* Style général Free Mobile */
    .main-header {{
        background: linear-gradient(135deg, {FREE_MOBILE_RED} 0%, {FREE_MOBILE_DARK} 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(220, 20, 60, 0.3);
    }}
    
    .chat-container {{
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }}
    
    .chat-input {{
        border: 2px solid {FREE_MOBILE_RED};
        border-radius: 25px;
        padding: 0.75rem 1.5rem;
        font-size: 16px;
    }}
    
    .chat-input:focus {{
        border-color: {FREE_MOBILE_DARK};
        box-shadow: 0 0 0 3px rgba(220, 20, 60, 0.1);
    }}
    
    .send-button {{
        background: {FREE_MOBILE_RED};
        color: white;
        border: none;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        cursor: pointer;
        transition: all 0.3s ease;
    }}
    
    .send-button:hover {{
        background: {FREE_MOBILE_DARK};
        transform: scale(1.05);
    }}
    
    .sidebar-config {{
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid {FREE_MOBILE_RED};
    }}
    
    .status-indicator {{
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }}
    
    .status-online {{ background-color: #28a745; }}
    .status-offline {{ background-color: #dc3545; }}
    .status-processing {{ background-color: #ffc107; }}
    
    .source-link {{
        color: {FREE_MOBILE_RED};
        text-decoration: none;
        font-size: 0.9em;
    }}
    
    .source-link:hover {{
        color: {FREE_MOBILE_DARK};
        text-decoration: underline;
    }}
    
    .metrics-card {{
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid {FREE_MOBILE_RED};
        margin-bottom: 1rem;
    }}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'conversation_id' not in st.session_state:
    st.session_state.conversation_id = None
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'chatbot_initialized' not in st.session_state:
    st.session_state.chatbot_initialized = False

# Navigation
render_dashboard_navigation()
render_page_breadcrumb("Chatbot SAV")

# Header
st.markdown("""
<div class="main-header">
    <h1>🤖 Assistant SAV Free Mobile</h1>
    <p>Votre assistant intelligent pour toutes vos questions techniques, de facturation et de service</p>
</div>
""", unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.markdown('<div class="sidebar-config">', unsafe_allow_html=True)
    st.subheader("⚙️ Configuration")
    
    # LLM Provider selection
    llm_provider = st.selectbox(
        "Fournisseur IA",
        options=["mistral", "openai", "anthropic", "ollama"],
        index=0,
        help="Choisissez le fournisseur d'intelligence artificielle"
    )
    
    # Status indicator
    if st.session_state.chatbot_initialized:
        st.markdown('<span class="status-indicator status-online"></span>Chatbot en ligne', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-indicator status-offline"></span>Chatbot hors ligne', unsafe_allow_html=True)
    
    # Initialize button
    if st.button("🚀 Initialiser le chatbot", type="primary"):
        with st.spinner("Initialisation de la base de connaissances..."):
            try:
                response = requests.post(f"{API_BASE_URL}/api/chatbot/initialize", timeout=60)
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        st.session_state.chatbot_initialized = True
                        st.success("✅ Chatbot initialisé avec succès!")
                        st.rerun()
                    else:
                        st.error(f"❌ Erreur d'initialisation: {result.get('error')}")
                else:
                    st.error(f"❌ Erreur HTTP {response.status_code}")
            except Exception as e:
                st.error(f"❌ Erreur de connexion: {str(e)}")
    
    # Clear conversation
    if st.button("🗑️ Nouvelle conversation"):
        st.session_state.messages = []
        st.session_state.conversation_id = None
        st.rerun()
    
    # Statistics
    st.markdown("---")
    st.subheader("📊 Statistiques")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Messages", len(st.session_state.messages))
    with col2:
        user_messages = len([m for m in st.session_state.messages if m['role'] == 'user'])
        st.metric("Questions", user_messages)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Main chat interface
if not CHAT_AVAILABLE:
    st.error("⚠️ Interface de chat non disponible. Veuillez installer streamlit-chat.")
    st.stop()

# Chat container
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display chat messages
if st.session_state.messages:
    for i, msg in enumerate(st.session_state.messages):
        if msg['role'] == 'user':
            message(msg['content'], is_user=True, key=f"user_{i}")
        else:
            message(msg['content'], key=f"bot_{i}")
            
            # Display sources if available
            if msg.get('sources'):
                with st.expander("📚 Sources utilisées"):
                    for source in msg['sources']:
                        st.markdown(f'<a href="{source}" class="source-link" target="_blank">{source}</a>', unsafe_allow_html=True)
else:
    # Welcome message
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: #666;">
        <h3>👋 Bonjour ! Je suis votre assistant SAV Free Mobile</h3>
        <p>Posez-moi vos questions sur :</p>
        <ul style="text-align: left; display: inline-block;">
            <li>🔧 Problèmes techniques avec votre mobile</li>
            <li>💰 Questions de facturation et d'abonnement</li>
            <li>⚙️ Configuration de vos services</li>
            <li>🆘 Dépannage de votre ligne</li>
        </ul>
        <p><strong>Tapez votre message ci-dessous pour commencer !</strong></p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Chat input
if st.session_state.chatbot_initialized:
    # Input form
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([6, 1])
        
        with col1:
            user_input = st.text_input(
                "Votre message",
                placeholder="Tapez votre question ici...",
                label_visibility="collapsed"
            )
        
        with col2:
            send_button = st.form_submit_button("📤", type="primary")
        
        if send_button and user_input.strip():
            # Add user message to chat
            st.session_state.messages.append({
                'role': 'user',
                'content': user_input,
                'timestamp': datetime.now()
            })
            
            # Show processing indicator
            with st.spinner("🤔 Réflexion en cours..."):
                try:
                    # Send message to API
                    payload = {
                        "message": user_input,
                        "conversation_id": st.session_state.conversation_id,
                        "session_id": st.session_state.session_id,
                        "llm_provider": llm_provider
                    }
                    
                    response = requests.post(
                        f"{API_BASE_URL}/api/chatbot/message",
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        if result['success']:
                            # Update conversation ID
                            st.session_state.conversation_id = result['conversation_id']
                            
                            # Add bot response to chat
                            st.session_state.messages.append({
                                'role': 'assistant',
                                'content': result['response'],
                                'sources': result.get('sources', []),
                                'processing_time': result.get('processing_time', 0),
                                'timestamp': datetime.now()
                            })
                            
                            st.rerun()
                        else:
                            st.error(f"❌ Erreur: {result.get('error')}")
                    else:
                        st.error(f"❌ Erreur HTTP {response.status_code}")
                        
                except Exception as e:
                    st.error(f"❌ Erreur de connexion: {str(e)}")
else:
    st.info("ℹ️ Veuillez d'abord initialiser le chatbot dans la barre latérale.")

# Footer with tips
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9em;">
    <p><strong>💡 Conseils d'utilisation :</strong></p>
    <p>• Soyez précis dans vos questions • Mentionnez votre modèle de téléphone si pertinent • N'hésitez pas à reformuler si la réponse ne convient pas</p>
    <p><em>Développé avec ❤️ pour Free Mobile</em></p>
</div>
""", unsafe_allow_html=True)
