"""
Navigation Component for FreeMobilaChat Dashboard
Professional navigation bar and page routing
"""

import streamlit as st
from typing import Dict, List, Optional


def render_dashboard_navigation():
    """Render the main dashboard navigation bar"""
    
    # Navigation CSS
    st.markdown("""
    <style>
        .dashboard-nav {
            background: linear-gradient(135deg, #DC143C 0%, #FF6B6B 100%);
            padding: 1rem 2rem;
            margin: -1rem -1rem 2rem -1rem;
            border-radius: 0 0 15px 15px;
            box-shadow: 0 4px 20px rgba(220, 20, 60, 0.15);
        }
        
        .nav-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .nav-brand {
            color: white;
            font-size: 1.8rem;
            font-weight: 800;
            font-family: 'Inter', sans-serif;
            text-decoration: none;
        }
        
        .nav-links {
            display: flex;
            gap: 2rem;
            align-items: center;
        }
        
        .nav-link {
            color: rgba(255, 255, 255, 0.9);
            text-decoration: none;
            font-weight: 500;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            transition: all 0.3s ease;
            border: 1px solid transparent;
        }
        
        .nav-link:hover {
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border-color: rgba(255, 255, 255, 0.2);
        }
        
        .nav-link.active {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border-color: rgba(255, 255, 255, 0.3);
        }
        
        .nav-user {
            display: flex;
            align-items: center;
            gap: 1rem;
            color: white;
        }
        
        .user-badge {
            background: rgba(255, 255, 255, 0.2);
            padding: 0.3rem 0.8rem;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        
        .status-indicator {
            width: 8px;
            height: 8px;
            background: #28a745;
            border-radius: 50%;
            display: inline-block;
            margin-right: 0.5rem;
        }
        
        @media (max-width: 768px) {
            .nav-container {
                flex-direction: column;
                gap: 1rem;
            }
            
            .nav-links {
                gap: 1rem;
            }
            
            .nav-brand {
                font-size: 1.5rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Get current page info
    current_page = get_current_page()
    user_role = st.session_state.get('user_role', 'manager')
    batch_id = st.session_state.get('current_batch_id')
    
    # Render navigation
    nav_html = f"""
    <div class="dashboard-nav">
        <div class="nav-container">
            <div class="nav-brand">FreeMobilaChat</div>
            
            <div class="nav-links">
                <a href="/" class="nav-link {'active' if current_page == 'main' else ''}">
                    🏠 Accueil
                </a>
                <a href="/1_Overview" class="nav-link {'active' if current_page == 'overview' else ''}">
                    📊 Aperçu
                </a>
                <a href="/2_Analysis" class="nav-link {'active' if current_page == 'analysis' else ''}">
                    🔍 Analyse
                </a>
                <a href="/3_Settings" class="nav-link {'active' if current_page == 'settings' else ''}">
                    ⚙️ Paramètres
                </a>
            </div>
            
            <div class="nav-user">
                <div class="status-indicator"></div>
                <span>Connecté</span>
                <div class="user-badge">{user_role.title()}</div>
            </div>
        </div>
    </div>
    """
    
    st.markdown(nav_html, unsafe_allow_html=True)
    
    # Add batch status if available
    if batch_id:
        render_batch_status_bar(batch_id)


def render_batch_status_bar(batch_id: str):
    """Render a status bar showing current batch information"""
    
    st.markdown("""
    <style>
        .batch-status-bar {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 0.75rem 1rem;
            margin-bottom: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .batch-info {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .batch-id {
            font-family: monospace;
            background: #e9ecef;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
        }
        
        .batch-actions {
            display: flex;
            gap: 0.5rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    status_html = f"""
    <div class="batch-status-bar">
        <div class="batch-info">
            <strong>Analyse en cours:</strong>
            <span class="batch-id">{batch_id}</span>
        </div>
        <div class="batch-actions">
            <small style="color: #666;">Dernière mise à jour: {get_current_time()}</small>
        </div>
    </div>
    """
    
    st.markdown(status_html, unsafe_allow_html=True)


def render_page_breadcrumb(page_title: str, subtitle: Optional[str] = None):
    """Render breadcrumb navigation for current page"""
    
    st.markdown("""
    <style>
        .page-breadcrumb {
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #e9ecef;
        }
        
        .breadcrumb-title {
            font-size: 2rem;
            font-weight: 700;
            color: #333;
            margin-bottom: 0.5rem;
        }
        
        .breadcrumb-subtitle {
            color: #666;
            font-size: 1rem;
        }
        
        .breadcrumb-path {
            color: #DC143C;
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    current_page = get_current_page()
    page_path = get_page_path(current_page)
    
    breadcrumb_html = f"""
    <div class="page-breadcrumb">
        <div class="breadcrumb-path">{page_path}</div>
        <div class="breadcrumb-title">{page_title}</div>
        {f'<div class="breadcrumb-subtitle">{subtitle}</div>' if subtitle else ''}
    </div>
    """
    
    st.markdown(breadcrumb_html, unsafe_allow_html=True)


def get_current_page() -> str:
    """Get the current page identifier"""
    try:
        # Try to get from Streamlit's page info
        if hasattr(st, 'get_script_run_ctx'):
            ctx = st.get_script_run_ctx()
            if ctx and hasattr(ctx, 'page_script_hash'):
                # This is a multi-page app
                if '1_Overview' in str(ctx):
                    return 'overview'
                elif '2_Analysis' in str(ctx):
                    return 'analysis'
                elif '3_Settings' in str(ctx):
                    return 'settings'
        
        # Fallback: check session state or URL
        if 'current_page' in st.session_state:
            return st.session_state.current_page
            
        return 'main'
    except:
        return 'main'


def get_page_path(page: str) -> str:
    """Get breadcrumb path for current page"""
    paths = {
        'main': 'Dashboard',
        'overview': 'Dashboard > Aperçu',
        'analysis': 'Dashboard > Analyse',
        'settings': 'Dashboard > Paramètres'
    }
    return paths.get(page, 'Dashboard')


def get_current_time() -> str:
    """Get current time formatted for display"""
    from datetime import datetime
    return datetime.now().strftime("%H:%M:%S")


def render_quick_actions():
    """Render quick action buttons"""
    
    st.markdown("""
    <style>
        .quick-actions {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        .quick-actions-title {
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #333;
        }
        
        .action-buttons {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }
        
        .action-btn {
            background: #DC143C;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .action-btn:hover {
            background: #B91C3C;
            transform: translateY(-1px);
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="quick-actions">
        <div class="quick-actions-title">Actions Rapides</div>
        <div class="action-buttons">
            <button class="action-btn" onclick="window.location.href='/'">Nouvelle Analyse</button>
            <button class="action-btn" onclick="window.location.href='/2_Analysis'">Voir Détails</button>
            <button class="action-btn" onclick="window.location.href='/3_Settings'">Configuration</button>
        </div>
    </div>
    """, unsafe_allow_html=True)
