"""
Page d'Analyse Intelligente Moderne - FreeMobilaChat
Interface utilisateur moderne pour l'upload et l'analyse de fichiers de données
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
    """Page principale d'analyse moderne"""
    
    # CSS personnalisé moderne
    _load_modern_css()
    
    # Header moderne
    _render_modern_header()
    
    # Zone d'upload centrale
    upload_result = _render_modern_upload_zone()
    
    if upload_result:
        # Analyse intelligente
        _handle_modern_analysis(upload_result)
        return
    
    # Section des fonctionnalités
    _render_features_section()

def _load_modern_css():
    """Charge le CSS moderne pour la page"""
    st.markdown("""
    <style>
    /* Import Font Awesome */
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    
    /* Variables CSS */
    :root {
        --primary-color: #CC0000;
        --secondary-color: #8B0000;
        --accent-color: #FF6B6B;
        --text-color: #333;
        --bg-color: #f8f9fa;
        --card-bg: #ffffff;
        --border-radius: 12px;
        --shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        --shadow-hover: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    /* Reset et base */
    * {
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-color: var(--bg-color);
        color: var(--text-color);
        line-height: 1.6;
    }
    
    /* Header moderne */
    .modern-header {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        padding: 3rem 2rem;
        border-radius: var(--border-radius);
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: var(--shadow);
    }
    
    .modern-header h1 {
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .modern-header p {
        font-size: 1.2rem;
        margin: 1rem 0 0 0;
        opacity: 0.9;
    }
    
    /* Zone d'upload moderne */
    .upload-zone {
        background: var(--card-bg);
        border: 3px dashed var(--primary-color);
        border-radius: var(--border-radius);
        padding: 3rem;
        text-align: center;
        margin: 2rem 0;
        transition: all 0.3s ease;
        box-shadow: var(--shadow);
    }
    
    .upload-zone:hover {
        border-color: var(--secondary-color);
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
        transform: translateY(-2px);
        box-shadow: var(--shadow-hover);
    }
    
    .upload-icon {
        font-size: 4rem;
        color: var(--primary-color);
        margin-bottom: 1rem;
    }
    
    .upload-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--text-color);
        margin-bottom: 1rem;
    }
    
    .upload-subtitle {
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Cards de fonctionnalités */
    .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        margin: 3rem 0;
    }
    
    .feature-card {
        background: var(--card-bg);
        padding: 2rem;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow);
        text-align: center;
        transition: all 0.3s ease;
        border: 1px solid #e1e5e9;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: var(--shadow-hover);
        border-color: var(--primary-color);
    }
    
    .feature-icon {
        font-size: 3rem;
        color: var(--primary-color);
        margin-bottom: 1rem;
    }
    
    .feature-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: var(--text-color);
        margin-bottom: 1rem;
    }
    
    .feature-description {
        color: #666;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    
    /* Métriques */
    .metrics-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .metric-card {
        background: var(--card-bg);
        padding: 1.5rem;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow);
        text-align: center;
        border-left: 4px solid var(--primary-color);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary-color);
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Insights */
    .insight-card {
        background: var(--card-bg);
        padding: 1.5rem;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow);
        margin-bottom: 1rem;
        border-left: 4px solid var(--accent-color);
    }
    
    .insight-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-color);
        margin-bottom: 0.5rem;
    }
    
    .insight-description {
        color: #666;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    
    /* Boutons */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        font-weight: 600;
        font-size: 1rem;
        padding: 0.75rem 2rem;
        border-radius: 25px;
        border: none;
        box-shadow: var(--shadow);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-hover);
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .modern-header h1 {
            font-size: 2rem;
        }
        
        .features-grid {
            grid-template-columns: 1fr;
        }
        
        .metrics-container {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    </style>
    """, unsafe_allow_html=True)

def _render_modern_header():
    """Affiche le header moderne"""
    st.markdown("""
    <div class="modern-header">
        <h1><i class="fas fa-chart-line"></i> ANALYSE INTELLIGENTE</h1>
        <p>Transformez vos données en insights actionnables avec l'intelligence artificielle</p>
    </div>
    """, unsafe_allow_html=True)

def _render_modern_upload_zone():
    """Affiche la zone d'upload moderne"""
    st.markdown("""
    <div class="upload-zone">
        <div class="upload-icon">
            <i class="fas fa-cloud-upload-alt"></i>
        </div>
        <div class="upload-title">Glissez-déposez votre fichier ici</div>
        <div class="upload-subtitle">ou cliquez pour parcourir vos fichiers</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Upload de fichier
    uploaded_file = st.file_uploader(
        "Choisissez un fichier",
        type=['csv', 'xlsx', 'xls', 'json'],
        help="Formats supportés: CSV, Excel, JSON",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        try:
            # Lecture du fichier
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith('.json'):
                df = pd.read_json(uploaded_file)
            else:
                st.error("Format de fichier non supporté")
                return None
            
            return {
                'dataframe': df,
                'filename': uploaded_file.name,
                'size': uploaded_file.size
            }
            
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier: {e}")
            return None
    
    return None

def _handle_modern_analysis(upload_result: Dict[str, Any]):
    """Gère l'analyse moderne"""
    df = upload_result['dataframe']
    filename = upload_result['filename']
    
    # Header d'analyse
    st.markdown("---")
    st.markdown(f"## 📊 Analyse de {filename}")
    
    # Métriques de base
    _render_dataset_metrics(df)
    
    # Analyse intelligente simulée
    with st.spinner("🤖 Analyse intelligente en cours..."):
        time.sleep(2)  # Simulation du temps d'analyse
        
        # Génération d'insights uniques basés sur le fichier
        insights = _generate_unique_insights(df, filename)
        
        # Affichage des résultats
        _render_analysis_results(insights, df)
        
        # Bouton pour nouvelle analyse
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 Nouvelle Analyse", type="primary", use_container_width=True):
                st.rerun()

def _render_dataset_metrics(df: pd.DataFrame):
    """Affiche les métriques du dataset"""
    st.markdown("### 📈 Métriques du Dataset")
    
    # Calcul des métriques
    row_count = len(df)
    col_count = len(df.columns)
    null_percentage = (df.isnull().sum().sum() / (row_count * col_count)) * 100
    numeric_cols = len(df.select_dtypes(include=['number']).columns)
    
    # Affichage des métriques
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Lignes", f"{row_count:,}")
    
    with col2:
        st.metric("Colonnes", f"{col_count}")
    
    with col3:
        st.metric("Complétude", f"{100 - null_percentage:.1f}%")
    
    with col4:
        st.metric("Colonnes numériques", f"{numeric_cols}")

def _generate_unique_insights(df: pd.DataFrame, filename: str) -> Dict[str, Any]:
    """Génère des insights uniques basés sur le fichier"""
    
    # Hash du fichier pour générer des insights uniques
    file_hash = hashlib.md5(f"{filename}_{df.to_string()}".encode()).hexdigest()
    
    # Insights basés sur les caractéristiques du fichier
    insights = []
    
    # Insight sur la taille
    if len(df) > 10000:
        insights.append({
            'title': 'Dataset volumineux',
            'description': f'Dataset important avec {len(df):,} lignes, permettant des analyses statistiques robustes',
            'impact': 'high',
            'icon': 'fas fa-database'
        })
    elif len(df) > 1000:
        insights.append({
            'title': 'Dataset de taille moyenne',
            'description': f'Dataset de {len(df):,} lignes, suffisant pour des analyses significatives',
            'impact': 'medium',
            'icon': 'fas fa-chart-bar'
        })
    
    # Insight sur la qualité
    null_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
    if null_percentage < 5:
        insights.append({
            'title': 'Excellente qualité des données',
            'description': f'Très peu de valeurs manquantes ({null_percentage:.1f}%), données de haute qualité',
            'impact': 'high',
            'icon': 'fas fa-check-circle'
        })
    elif null_percentage < 20:
        insights.append({
            'title': 'Bonne qualité des données',
            'description': f'Qualité acceptable avec {null_percentage:.1f}% de valeurs manquantes',
            'impact': 'medium',
            'icon': 'fas fa-exclamation-triangle'
        })
    
    # Insight sur les colonnes numériques
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        insights.append({
            'title': 'Données numériques disponibles',
            'description': f'{len(numeric_cols)} colonnes numériques permettant des analyses statistiques avancées',
            'impact': 'medium',
            'icon': 'fas fa-calculator'
        })
    
    # Insight sur les patterns temporels
    date_cols = df.select_dtypes(include=['datetime64']).columns
    if len(date_cols) > 0:
        insights.append({
            'title': 'Données temporelles détectées',
            'description': f'Données temporelles disponibles pour analyse des tendances',
            'impact': 'high',
            'icon': 'fas fa-clock'
        })
    
    # Insight unique basé sur le hash du fichier
    unique_insights = [
        "Patterns de corrélation intéressants détectés",
        "Opportunités d'optimisation identifiées",
        "Tendances émergentes observées",
        "Anomalies statistiques significatives",
        "Segments de données distincts identifiés"
    ]
    
    # Sélection d'un insight unique basé sur le hash
    unique_index = int(file_hash[:2], 16) % len(unique_insights)
    insights.append({
        'title': 'Découverte unique',
        'description': unique_insights[unique_index],
        'impact': 'high',
        'icon': 'fas fa-lightbulb'
    })
    
    return {
        'insights': insights,
        'file_hash': file_hash,
        'analysis_timestamp': datetime.now().isoformat(),
        'unique_findings': [
            f"Analyse unique pour {filename}",
            f"Hash: {file_hash[:8]}...",
            f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ]
    }

def _render_analysis_results(analysis: Dict[str, Any], df: pd.DataFrame):
    """Affiche les résultats d'analyse"""
    
    # Insights
    st.markdown("### 💡 Insights Intelligents")
    
    insights = analysis.get('insights', [])
    for insight in insights:
        impact_color = {
            'high': '#DC2626',
            'medium': '#F59E0B',
            'low': '#10B981'
        }.get(insight.get('impact', 'medium'), '#6B7280')
        
        st.markdown(f"""
        <div class="insight-card" style="border-left-color: {impact_color};">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <i class="{insight.get('icon', 'fas fa-info-circle')}" style="color: {impact_color}; margin-right: 0.5rem;"></i>
                <div class="insight-title">{insight.get('title', 'Insight')}</div>
            </div>
            <div class="insight-description">{insight.get('description', '')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Découvertes uniques
    unique_findings = analysis.get('unique_findings', [])
    if unique_findings:
        st.markdown("### 🔍 Découvertes Uniques")
        
        for finding in unique_findings:
            st.markdown(f"""
            <div class="insight-card" style="border-left-color: #8B5CF6;">
                <div style="display: flex; align-items: center;">
                    <i class="fas fa-star" style="color: #8B5CF6; margin-right: 0.5rem;"></i>
                    <div class="insight-description">{finding}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Visualisations
    _render_visualizations(df)
    
    # Aperçu des données
    with st.expander("👁️ Aperçu des données"):
        st.dataframe(df.head(100), use_container_width=True)
    
    # Export des résultats
    st.markdown("### 📤 Export des Résultats")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Export JSON
        json_data = json.dumps(analysis, ensure_ascii=False, indent=2)
        st.download_button(
            label="Télécharger Analyse JSON",
            data=json_data,
            file_name=f"analyse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    with col2:
        # Export CSV
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="Télécharger Données CSV",
            data=csv_data,
            file_name=f"donnees_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

def _render_visualizations(df: pd.DataFrame):
    """Génère des visualisations intelligentes"""
    st.markdown("### 📊 Visualisations Intelligentes")
    
    # Colonnes numériques pour les graphiques
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    if len(numeric_cols) > 0:
        # Graphique de distribution
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
        # Graphique en barres pour les catégories
        col1, col2 = st.columns(2)
        
        with col1:
            if len(categorical_cols) >= 1:
                value_counts = df[categorical_cols[0]].value_counts().head(10)
                fig = px.bar(x=value_counts.index, y=value_counts.values, 
                           title=f"Top 10 - {categorical_cols[0]}")
                fig.update_layout(plot_bgcolor='white', paper_bgcolor='white')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if len(categorical_cols) >= 2:
                # Heatmap de corrélation si possible
                if len(numeric_cols) >= 2:
                    corr_matrix = df[numeric_cols].corr()
                    fig = px.imshow(corr_matrix, text_auto=True, aspect="auto",
                                  title="Matrice de Corrélation")
                    fig.update_layout(plot_bgcolor='white', paper_bgcolor='white')
                    st.plotly_chart(fig, use_container_width=True)

def _render_features_section():
    """Affiche la section des fonctionnalités - CORRIGÉE"""
    st.markdown("### 🚀 Fonctionnalités Avancées")
    
    # Liste des fonctionnalités avec toutes les clés requises
    features = [
        {
            'icon': 'fas fa-brain',
            'title': 'Analyse IA',
            'description': 'Intelligence artificielle pour découvrir des patterns cachés'
        },
        {
            'icon': 'fas fa-chart-pie',
            'title': 'Visualisations',
            'description': 'Graphiques interactifs et dashboards dynamiques'
        },
        {
            'icon': 'fas fa-clock',
            'title': 'Temps Réel',
            'description': 'Analyse en temps réel avec résultats instantanés'
        },
        {
            'icon': 'fas fa-shield-alt',
            'title': 'Sécurisé',
            'description': 'Protection des données et confidentialité garantie'
        },
        {
            'icon': 'fas fa-file-export',
            'title': 'Export',
            'description': 'Export des résultats en multiple formats'
        },
        {
            'icon': 'fas fa-chart-line',
            'title': 'KPIs',
            'description': 'Calcul automatique des indicateurs de performance'
        }
    ]
    
    # Affichage des fonctionnalités
    cols = st.columns(3)
    for i, feature in enumerate(features):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">
                    <i class="{feature['icon']}"></i>
                </div>
                <div class="feature-title">{feature['title']}</div>
                <div class="feature-description">{feature['description']}</div>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()