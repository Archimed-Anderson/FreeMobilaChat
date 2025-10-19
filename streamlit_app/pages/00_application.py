"""
Page d'accueil de l'application FreeMobilaChat
Redirige vers la page principale app.py
"""

import streamlit as st
from streamlit import switch_page

# Configuration de la page
st.set_page_config(
    page_title="FreeMobilaChat - Accueil",
    page_icon=":house:",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Redirection vers la page principale
st.markdown("""
<div style="text-align: center; padding: 4rem 2rem;">
    <h1 style="color: #CC0000; font-size: 3rem; margin-bottom: 2rem;">
        <i class="fas fa-home"></i> FreeMobilaChat
    </h1>
    <p style="font-size: 1.5rem; color: #666; margin-bottom: 3rem;">
        Redirection vers la page principale...
    </p>
    <div style="display: flex; justify-content: center; gap: 2rem;">
        <a href="/" style="background: linear-gradient(135deg, #CC0000 0%, #8B0000 100%); color: white; padding: 1rem 2rem; text-decoration: none; border-radius: 10px; font-weight: 600;">
            <i class="fas fa-arrow-left"></i> Retour à l'accueil
        </a>
    </div>
</div>
""", unsafe_allow_html=True)

# Redirection automatique
st.markdown("""
<script>
setTimeout(function() {
    window.location.href = '/';
}, 2000);
</script>
""", unsafe_allow_html=True)
