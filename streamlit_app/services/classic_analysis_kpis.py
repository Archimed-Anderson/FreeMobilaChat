"""
Module de KPIs Modernes pour Analyse Classique - FreeMobilaChat
Visualisations dynamiques et interactives pour tous les indicateurs
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List, Optional
import streamlit as st

# Couleurs Free Mobile
COLORS = {
    'primary': '#CC0000',
    'secondary': '#8B0000',
    'success': '#28a745',
    'warning': '#ffc107',
    'danger': '#dc3545',
    'info': '#17a2b8',
    'positive': '#28a745',
    'neutral': '#6c757d',
    'negative': '#dc3545'
}


def compute_classic_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calcule les KPIs de manière 100% DYNAMIQUE avec optimisations de performance
    
    KPIs calculés:
    - is_claim: Détection de réclamations (count + %)
    - topics: Distribution par catégorie (fibre, mobile, facture, etc.)
    - sentiment: Analyse de sentiment (positif, neutre, négatif)
    - urgence: Niveaux de priorité (haute, moyenne, basse)
    - incident: Types de problèmes
    - confidence: Score de confiance (moyenne, min, max)
    
    GARANTIE DE DYNAMISME:
    - Pas de cache entre les appels
    - Calculs basés uniquement sur df
    - Chaque fichier uploadé = nouveaux KPIs
    
    OPTIMISATIONS:
    - Calculs vectorisés pandas/numpy
    - Réutilisation des calculs intermédiaires
    - Gestion optimisée des valeurs manquantes
    
    Args:
        df: DataFrame avec colonnes is_claim, topics, sentiment, urgence, incident, confidence
        
    Returns:
        Dictionnaire avec tous les KPIs calculés dynamiquement
    """
    kpis = {}
    total_tweets = len(df)
    
    if total_tweets == 0:
        return kpis
    
    # 1. Claim Detection (is_claim) - OPTIMISÉ
    if 'is_claim' in df.columns:
        # Gérer les listes et valeurs simples
        if df['is_claim'].dtype == 'object':
            # Si c'est une liste, extraire la première valeur
            claims_array = df['is_claim'].apply(
                lambda x: int(x[0]) if isinstance(x, list) and len(x) > 0 else (int(x) if pd.notna(x) else 0)
            )
        else:
            claims_array = pd.to_numeric(df['is_claim'], errors='coerce').fillna(0)
        
        claims_count = int(claims_array.sum())
        
        kpis['claim_rate'] = {
            'value': (claims_count / total_tweets * 100),
            'count': claims_count,
            'total': total_tweets,
            'non_claims': total_tweets - claims_count
        }
    
    # 2. Topics Distribution - OPTIMISÉ
    if 'topics' in df.columns:
        # Aplatir les listes de topics
        topics_flat = []
        for topics_list in df['topics']:
            if isinstance(topics_list, list):
                topics_flat.extend(topics_list)
            elif pd.notna(topics_list):
                topics_flat.append(str(topics_list))
        
        if topics_flat:
            topics_series = pd.Series(topics_flat)
            topics_counts = topics_series.value_counts()
            
            kpis['topics_distribution'] = {
                'categories': topics_counts.to_dict(),
                'top_category': topics_counts.index[0] if len(topics_counts) > 0 else 'N/A',
                'count': len(topics_counts),
                'total_mentions': len(topics_flat)
            }
    
    # 3. Sentiment Analysis - OPTIMISÉ
    if 'sentiment' in df.columns:
        sentiment_lower = df['sentiment'].str.lower().fillna('neu')
        
        positive = (sentiment_lower.isin(['positive', 'positif', 'pos'])).sum()
        neutral = (sentiment_lower.isin(['neutral', 'neutre', 'neu'])).sum()
        negative = (sentiment_lower.isin(['negative', 'négatif', 'negatif', 'neg'])).sum()
        
        satisfaction_index = ((positive - negative) / total_tweets * 50 + 50) if total_tweets > 0 else 50
        
        kpis['sentiment_analysis'] = {
            'positive_count': int(positive),
            'neutral_count': int(neutral),
            'negative_count': int(negative),
            'positive_pct': (positive / total_tweets * 100),
            'neutral_pct': (neutral / total_tweets * 100),
            'negative_pct': (negative / total_tweets * 100),
            'satisfaction_index': satisfaction_index
        }
    
    # 4. Urgency Levels - OPTIMISÉ
    if 'urgence' in df.columns:
        urgency_lower = df['urgence'].str.lower().fillna('basse')
        
        haute = (urgency_lower.isin(['haute', 'high', 'urgent', 'critique'])).sum()
        moyenne = (urgency_lower.isin(['moyenne', 'medium', 'moyen'])).sum()
        basse = (urgency_lower.isin(['basse', 'low', 'faible'])).sum()
        
        kpis['urgency_levels'] = {
            'haute_count': int(haute),
            'moyenne_count': int(moyenne),
            'basse_count': int(basse),
            'haute_pct': (haute / total_tweets * 100),
            'moyenne_pct': (moyenne / total_tweets * 100),
            'basse_pct': (basse / total_tweets * 100),
            'urgent_total': int(haute + moyenne)
        }
    elif 'priority' in df.columns:
        priority_lower = df['priority'].str.lower().fillna('low')
        haute = (priority_lower.isin(['haute', 'high', 'urgent'])).sum()
        moyenne = (priority_lower.isin(['moyenne', 'medium'])).sum()
        basse = (priority_lower.isin(['basse', 'low'])).sum()
        
        kpis['urgency_levels'] = {
            'haute_count': int(haute),
            'moyenne_count': int(moyenne),
            'basse_count': int(basse),
            'haute_pct': (haute / total_tweets * 100),
            'moyenne_pct': (moyenne / total_tweets * 100),
            'basse_pct': (basse / total_tweets * 100),
            'urgent_total': int(haute + moyenne)
        }
    
    # 5. Incident Types - OPTIMISÉ
    if 'incident' in df.columns:
        incident_counts = df['incident'].value_counts()
        
        kpis['incident_types'] = {
            'categories': incident_counts.to_dict(),
            'top_incident': incident_counts.index[0] if len(incident_counts) > 0 else 'N/A',
            'count': len(incident_counts)
        }
    
    # 6. Confidence Score - OPTIMISÉ
    if 'confidence' in df.columns:
        # Gérer les listes et valeurs simples
        if df['confidence'].dtype == 'object':
            confidence_array = df['confidence'].apply(
                lambda x: float(x[0]) if isinstance(x, list) and len(x) > 0 else (float(x) if pd.notna(x) else 0.5)
            )
        else:
            confidence_array = pd.to_numeric(df['confidence'], errors='coerce').fillna(0.5)
        
        confidence_clean = confidence_array[confidence_array > 0]
        
        if len(confidence_clean) > 0:
            kpis['confidence_score'] = {
                'average': float(confidence_clean.mean()),
                'min': float(confidence_clean.min()),
                'max': float(confidence_clean.max()),
                'std': float(confidence_clean.std()),
                'median': float(confidence_clean.median())
            }
        else:
            kpis['confidence_score'] = {
                'average': 0.5,
                'min': 0.0,
                'max': 1.0,
                'std': 0.0,
                'median': 0.5
            }
    
    return kpis


def render_modern_kpi_cards(kpis: Dict[str, Any], role: str = "Agent SAV"):
    """
    Affiche les KPIs dans des cards modernes et interactives
    
    Design premium avec:
    - Cards blanches avec ombres
    - Bordures colorées à gauche
    - Icônes Font Awesome contextuelles
    - Couleurs adaptatives selon les valeurs
    - Layout responsive
    
    Args:
        kpis: Dictionnaire des KPIs calculés
        role: Rôle actuel pour personnalisation
    """
    # Header moderne
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                padding: 2rem; 
                border-radius: 12px; 
                text-align: center; 
                margin: 1.5rem 0; 
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
        <h2 style="font-size: 1.9rem; font-weight: 800; color: #1a202c; margin: 0; letter-spacing: -0.5px;">
            <i class="fas fa-tachometer-alt" style="color: #CC0000; margin-right: 0.5rem;"></i>
            Indicateurs de Performance Clés
        </h2>
        <p style="color: #4a5568; font-size: 0.95rem; margin-top: 0.75rem; font-weight: 500;">
            <i class="fas fa-sync-alt" style="font-size: 0.8rem; margin-right: 0.3rem;"></i>
            Mise à jour en temps réel • Calculs dynamiques
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 6 KPIs en 2 lignes (3 + 3)
    col1, col2, col3 = st.columns(3, gap="medium")
    
    # Ligne 1: Claim, Sentiment, Urgency
    with col1:
        _render_claim_kpi(kpis.get('claim_rate'))
    
    with col2:
        _render_sentiment_kpi(kpis.get('sentiment_analysis'))
    
    with col3:
        _render_urgency_kpi(kpis.get('urgency_levels'))
    
    # Ligne 2: Topics, Incident, Confidence
    col4, col5, col6 = st.columns(3, gap="medium")
    
    with col4:
        _render_topics_kpi(kpis.get('topics_distribution'))
    
    with col5:
        _render_incident_kpi(kpis.get('incident_types'))
    
    with col6:
        _render_confidence_kpi(kpis.get('confidence_score'))


def _render_claim_kpi(claim_data: Optional[Dict[str, Any]]):
    """Card KPI pour is_claim (Réclamations)"""
    if not claim_data:
        st.metric("Réclamations", "N/A")
        return
    
    claim_rate = claim_data['value']
    claim_count = claim_data['count']
    
    # Couleur adaptative
    color = "#e53e3e" if claim_rate > 30 else "#ed8936" if claim_rate > 15 else "#48bb78"
    
    st.markdown(f"""
    <div style="background: white; 
                padding: 1.25rem; 
                border-radius: 10px; 
                border-left: 4px solid {color};
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                height: 140px;">
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <i class="fas fa-exclamation-triangle" style="color: {color}; font-size: 1.2rem; margin-right: 0.5rem;"></i>
            <span style="font-size: 0.85rem; font-weight: 600; color: #4a5568; text-transform: uppercase; letter-spacing: 0.5px;">Réclamations</span>
        </div>
        <div style="font-size: 2.2rem; font-weight: 800; color: #1a202c; margin: 0.5rem 0;">
            {claim_rate:.1f}<span style="font-size: 1.2rem; color: #718096;">%</span>
        </div>
        <div style="font-size: 0.8rem; color: #718096; font-weight: 500;">
            <i class="fas fa-hashtag" style="font-size: 0.7rem;"></i> {claim_count} sur {claim_data['total']}
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_sentiment_kpi(sentiment_data: Optional[Dict[str, Any]]):
    """Card KPI pour sentiment"""
    if not sentiment_data:
        st.metric("Sentiment", "N/A")
        return
    
    satisfaction = sentiment_data.get('satisfaction_index', 50)
    positive_pct = sentiment_data.get('positive_pct', 0)
    
    # Couleur et icône dynamiques
    if satisfaction > 60:
        color = "#48bb78"
        icon = "fa-smile"
        status = "Positif"
    elif satisfaction > 40:
        color = "#4299e1"
        icon = "fa-meh"
        status = "Neutre"
    else:
        color = "#e53e3e"
        icon = "fa-frown"
        status = "Négatif"
    
    st.markdown(f"""
    <div style="background: white; 
                padding: 1.25rem; 
                border-radius: 10px; 
                border-left: 4px solid {color};
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                height: 140px;">
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <i class="fas {icon}" style="color: {color}; font-size: 1.2rem; margin-right: 0.5rem;"></i>
            <span style="font-size: 0.85rem; font-weight: 600; color: #4a5568; text-transform: uppercase; letter-spacing: 0.5px;">Sentiment</span>
        </div>
        <div style="font-size: 2.2rem; font-weight: 800; color: #1a202c; margin: 0.5rem 0;">
            {satisfaction:.0f}<span style="font-size: 1.2rem; color: #718096;">/100</span>
        </div>
        <div style="font-size: 0.8rem; color: {color}; font-weight: 600;">
            <i class="fas fa-circle" style="font-size: 0.5rem;"></i> {status} ({positive_pct:.1f}% positif)
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_urgency_kpi(urgency_data: Optional[Dict[str, Any]]):
    """Card KPI pour urgence"""
    if not urgency_data:
        st.metric("Urgence", "N/A")
        return
    
    urgent_total = urgency_data.get('urgent_total', 0)
    haute_pct = urgency_data.get('haute_pct', 0)
    
    # Couleur adaptative
    color = "#e53e3e" if haute_pct > 20 else "#ed8936" if haute_pct > 10 else "#48bb78"
    
    st.markdown(f"""
    <div style="background: white; 
                padding: 1.25rem; 
                border-radius: 10px; 
                border-left: 4px solid {color};
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                height: 140px;">
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <i class="fas fa-bolt" style="color: {color}; font-size: 1.2rem; margin-right: 0.5rem;"></i>
            <span style="font-size: 0.85rem; font-weight: 600; color: #4a5568; text-transform: uppercase; letter-spacing: 0.5px;">Urgence</span>
        </div>
        <div style="font-size: 2.2rem; font-weight: 800; color: #1a202c; margin: 0.5rem 0;">
            {haute_pct:.1f}<span style="font-size: 1.2rem; color: #718096;">%</span>
        </div>
        <div style="font-size: 0.8rem; color: #718096; font-weight: 500;">
            <i class="fas fa-fire" style="font-size: 0.7rem;"></i> {urgent_total} cas urgents
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_topics_kpi(topics_data: Optional[Dict[str, Any]]):
    """Card KPI pour topics"""
    if not topics_data:
        st.metric("Topics", "N/A")
        return
    
    theme_count = topics_data.get('count', 0)
    top_theme = topics_data.get('top_category', 'N/A')
    
    # Tronquer proprement
    top_theme_display = top_theme[:12] + "..." if len(top_theme) > 12 else top_theme
    
    st.markdown(f"""
    <div style="background: white; 
                padding: 1.25rem; 
                border-radius: 10px; 
                border-left: 4px solid #667eea;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                height: 140px;">
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <i class="fas fa-tags" style="color: #667eea; font-size: 1.2rem; margin-right: 0.5rem;"></i>
            <span style="font-size: 0.85rem; font-weight: 600; color: #4a5568; text-transform: uppercase; letter-spacing: 0.5px;">Catégories</span>
        </div>
        <div style="font-size: 2.2rem; font-weight: 800; color: #1a202c; margin: 0.5rem 0;">
            {theme_count}
        </div>
        <div style="font-size: 0.8rem; color: #718096; font-weight: 500;">
            <i class="fas fa-star" style="font-size: 0.7rem; color: #ffd700;"></i> {top_theme_display}
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_incident_kpi(incident_data: Optional[Dict[str, Any]]):
    """Card KPI pour incident"""
    if not incident_data:
        st.metric("Incidents", "N/A")
        return
    
    incident_count = incident_data.get('count', 0)
    top_incident = incident_data.get('top_incident', 'N/A')
    
    # Tronquer proprement
    top_incident_display = top_incident[:12] + "..." if len(top_incident) > 12 else top_incident
    
    st.markdown(f"""
    <div style="background: white; 
                padding: 1.25rem; 
                border-radius: 10px; 
                border-left: 4px solid #ed8936;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                height: 140px;">
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <i class="fas fa-bug" style="color: #ed8936; font-size: 1.2rem; margin-right: 0.5rem;"></i>
            <span style="font-size: 0.85rem; font-weight: 600; color: #4a5568; text-transform: uppercase; letter-spacing: 0.5px;">Incidents</span>
        </div>
        <div style="font-size: 2.2rem; font-weight: 800; color: #1a202c; margin: 0.5rem 0;">
            {incident_count}
        </div>
        <div style="font-size: 0.8rem; color: #718096; font-weight: 500;">
            <i class="fas fa-chart-pie" style="font-size: 0.7rem;"></i> {top_incident_display}
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_confidence_kpi(confidence_data: Optional[Dict[str, Any]]):
    """Card KPI pour confidence"""
    if not confidence_data:
        st.metric("Confiance", "N/A")
        return
    
    confidence = confidence_data.get('average', 0)
    max_conf = confidence_data.get('max', 0)
    
    # Couleur basée sur la confiance
    color = "#48bb78" if confidence > 0.8 else "#4299e1" if confidence > 0.6 else "#ed8936"
    
    st.markdown(f"""
    <div style="background: white; 
                padding: 1.25rem; 
                border-radius: 10px; 
                border-left: 4px solid {color};
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                height: 140px;">
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <i class="fas fa-shield-alt" style="color: {color}; font-size: 1.2rem; margin-right: 0.5rem;"></i>
            <span style="font-size: 0.85rem; font-weight: 600; color: #4a5568; text-transform: uppercase; letter-spacing: 0.5px;">Confiance</span>
        </div>
        <div style="font-size: 2.2rem; font-weight: 800; color: #1a202c; margin: 0.5rem 0;">
            {confidence:.2f}
        </div>
        <div style="font-size: 0.8rem; color: #718096; font-weight: 500;">
            <i class="fas fa-arrow-up" style="font-size: 0.7rem;"></i> Max: {max_conf:.2f}
        </div>
    </div>
    """, unsafe_allow_html=True)


def create_claim_donut_chart(kpis: Dict[str, Any]) -> Optional[go.Figure]:
    """Crée un graphique donut pour is_claim"""
    if 'claim_rate' not in kpis:
        return None
    
    claim_data = kpis['claim_rate']
    claims = claim_data['count']
    non_claims = claim_data['non_claims']
    
    fig = go.Figure(data=[
        go.Pie(
            labels=['Réclamations', 'Non-réclamations'],
            values=[claims, non_claims],
            hole=0.5,
            marker=dict(colors=['#e53e3e', '#48bb78']),
            textinfo='label+percent',
            textfont=dict(size=13, color="white"),
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Pourcentage: %{percent}<extra></extra>"
        )
    ])
    
    fig.update_layout(
        title="<b>Détection de Réclamations</b>",
        title_font_size=16,
        height=350,
        template="plotly_white",
        showlegend=True,
        margin=dict(t=50, b=50, l=20, r=20)
    )
    
    return fig


def create_topics_bar_chart(kpis: Dict[str, Any]) -> Optional[go.Figure]:
    """Crée un graphique bar pour topics"""
    if 'topics_distribution' not in kpis:
        return None
    
    topics_data = kpis['topics_distribution']
    categories = topics_data.get('categories', {})
    
    if not categories:
        return None
    
    topics_df = pd.DataFrame(list(categories.items()), columns=['Topic', 'Count'])
    topics_df = topics_df.sort_values('Count', ascending=False).head(10)
    
    fig = px.bar(
        topics_df,
        x='Topic',
        y='Count',
        color='Count',
        color_continuous_scale='Reds',
        title="<b>Distribution par Catégorie</b>",
        labels={'Topic': 'Catégorie', 'Count': 'Nombre'}
    )
    
    fig.update_layout(
        title_font_size=16,
        height=350,
        template="plotly_white",
        showlegend=False,
        xaxis_tickangle=-45,
        margin=dict(t=50, b=80, l=40, r=20)
    )
    
    return fig


def create_sentiment_bar_chart(kpis: Dict[str, Any]) -> Optional[go.Figure]:
    """Crée un graphique bar pour sentiment"""
    if 'sentiment_analysis' not in kpis:
        return None
    
    sentiment_data = kpis['sentiment_analysis']
    
    fig = go.Figure(data=[
        go.Bar(
            x=['Positif', 'Neutre', 'Négatif'],
            y=[
                sentiment_data.get('positive_count', 0),
                sentiment_data.get('neutral_count', 0),
                sentiment_data.get('negative_count', 0)
            ],
            marker=dict(color=['#28a745', '#6c757d', '#dc3545']),
            text=[
                f"{sentiment_data.get('positive_pct', 0):.1f}%",
                f"{sentiment_data.get('neutral_pct', 0):.1f}%",
                f"{sentiment_data.get('negative_pct', 0):.1f}%"
            ],
            textposition='outside',
            hovertemplate="<b>%{x}</b><br>Count: %{y}<br>Pourcentage: %{text}<extra></extra>"
        )
    ])
    
    fig.update_layout(
        title="<b>Analyse de Sentiment</b>",
        title_font_size=16,
        height=350,
        template="plotly_white",
        showlegend=False,
        xaxis_title="Sentiment",
        yaxis_title="Nombre",
        margin=dict(t=50, b=50, l=40, r=20)
    )
    
    return fig


def create_urgency_bar_chart(kpis: Dict[str, Any]) -> Optional[go.Figure]:
    """Crée un graphique bar pour urgence"""
    if 'urgency_levels' not in kpis:
        return None
    
    urgency_data = kpis['urgency_levels']
    
    fig = go.Figure(data=[
        go.Bar(
            x=['Haute', 'Moyenne', 'Basse'],
            y=[
                urgency_data.get('haute_count', 0),
                urgency_data.get('moyenne_count', 0),
                urgency_data.get('basse_count', 0)
            ],
            marker=dict(color=['#e53e3e', '#ed8936', '#48bb78']),
            text=[
                f"{urgency_data.get('haute_pct', 0):.1f}%",
                f"{urgency_data.get('moyenne_pct', 0):.1f}%",
                f"{urgency_data.get('basse_pct', 0):.1f}%"
            ],
            textposition='outside',
            hovertemplate="<b>%{x}</b><br>Count: %{y}<br>Pourcentage: %{text}<extra></extra>"
        )
    ])
    
    fig.update_layout(
        title="<b>Niveaux d'Urgence</b>",
        title_font_size=16,
        height=350,
        template="plotly_white",
        showlegend=False,
        xaxis_title="Urgence",
        yaxis_title="Nombre",
        margin=dict(t=50, b=50, l=40, r=20)
    )
    
    return fig


def create_incident_pie_chart(df: pd.DataFrame) -> Optional[go.Figure]:
    """Crée un graphique pie pour incident"""
    if 'incident' not in df.columns:
        return None
    
    incident_counts = df['incident'].value_counts()
    
    if len(incident_counts) == 0:
        return None
    
    fig = go.Figure(data=[
        go.Pie(
            labels=incident_counts.index,
            values=incident_counts.values,
            hole=0.4,
            marker=dict(colors=px.colors.sequential.Reds),
            textinfo='label+percent',
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Pourcentage: %{percent}<extra></extra>"
        )
    ])
    
    fig.update_layout(
        title="<b>Répartition par Type d'Incident</b>",
        title_font_size=16,
        height=350,
        template="plotly_white",
        showlegend=True,
        margin=dict(t=50, b=50, l=20, r=20)
    )
    
    return fig


def create_confidence_histogram(df: pd.DataFrame) -> Optional[go.Figure]:
    """Crée un histogramme pour confidence"""
    if 'confidence' not in df.columns:
        return None
    
    # Extraire les valeurs de confidence
    confidence_values = []
    for conf in df['confidence']:
        if isinstance(conf, list) and len(conf) > 0:
            confidence_values.append(float(conf[0]))
        elif pd.notna(conf):
            try:
                confidence_values.append(float(conf))
            except:
                continue
    
    if not confidence_values:
        return None
    
    fig = go.Figure(data=[
        go.Histogram(
            x=confidence_values,
            nbinsx=20,
            marker=dict(color='#CC0000'),
            hovertemplate="<b>Confidence</b><br>Intervalle: %{x}<br>Count: %{y}<extra></extra>"
        )
    ])
    
    fig.update_layout(
        title="<b>Distribution du Score de Confiance</b>",
        title_font_size=16,
        height=350,
        template="plotly_white",
        showlegend=False,
        xaxis_title="Score de Confiance",
        yaxis_title="Fréquence",
        margin=dict(t=50, b=50, l=40, r=20)
    )
    
    return fig


def render_modern_visualizations(df: pd.DataFrame, kpis: Dict[str, Any], role: str = "Agent SAV"):
    """
    Affiche toutes les visualisations modernes et interactives
    
    Args:
        df: DataFrame avec les données classifiées
        kpis: Dictionnaire des KPIs calculés
        role: Rôle actuel pour contrôle d'accès
    """
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0 1.5rem 0;">
        <h2 style="font-size: 1.8rem; font-weight: 700; color: #1a202c; margin: 0;">
            <i class="fas fa-chart-line" style="color: #CC0000; margin-right: 0.75rem;"></i>
            Visualisations Analytiques
        </h2>
        <p style="color: #718096; font-size: 1rem; margin-top: 0.5rem;">
            Graphiques interactifs pour analyser les tendances et patterns
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tab 1: Distribution
    tab1, tab2, tab3 = st.tabs(["Distribution", "Analyse", "Détails"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Incident Pie Chart
            fig_incident = create_incident_pie_chart(df)
            if fig_incident:
                st.plotly_chart(fig_incident, use_container_width=True, key='classique_viz_incident_pie')
            else:
                st.info("Données d'incident non disponibles")
        
        with col2:
            # Claim Donut Chart
            fig_claim = create_claim_donut_chart(kpis)
            if fig_claim:
                st.plotly_chart(fig_claim, use_container_width=True, key='classique_viz_claim_donut')
            else:
                st.info("Données de réclamations non disponibles")
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Sentiment Bar Chart
            fig_sentiment = create_sentiment_bar_chart(kpis)
            if fig_sentiment:
                st.plotly_chart(fig_sentiment, use_container_width=True, key='classique_viz_sentiment_bar')
            else:
                st.info("Données de sentiment non disponibles")
        
        with col2:
            # Urgency Bar Chart
            fig_urgency = create_urgency_bar_chart(kpis)
            if fig_urgency:
                st.plotly_chart(fig_urgency, use_container_width=True, key='classique_viz_urgency_bar')
            else:
                st.info("Données d'urgence non disponibles")
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            # Topics Bar Chart
            fig_topics = create_topics_bar_chart(kpis)
            if fig_topics:
                st.plotly_chart(fig_topics, use_container_width=True, key='classique_viz_topics_bar')
            else:
                st.info("Données de topics non disponibles")
        
        with col2:
            # Confidence Histogram
            fig_confidence = create_confidence_histogram(df)
            if fig_confidence:
                st.plotly_chart(fig_confidence, use_container_width=True, key='classique_viz_confidence_hist')
            else:
                st.info("Données de confiance non disponibles")

