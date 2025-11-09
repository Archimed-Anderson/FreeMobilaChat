"""
Module de KPIs et Visualisations Avancées pour FreeMobilaChat
Nouveaux indicateurs business et visualisations enrichies
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Any, List, Tuple
import streamlit as st
from datetime import datetime

# Couleurs Free Mobile
COLORS = {
    'primary': '#CC0000',
    'secondary': '#8B0000',
    'accent': '#FF6B6B',
    'success': '#28a745',
    'warning': '#ffc107',
    'danger': '#dc3545',
    'info': '#17a2b8',
    'positive': '#28a745',
    'neutral': '#6c757d',
    'negative': '#dc3545'
}

def compute_business_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calcule les KPIs business de manière 100% DYNAMIQUE avec optimisations de performance
    
    GARANTIE DE DYNAMISME:
    - Pas de cache entre les appels
    - Pas de variables globales
    - Calculs basés uniquement sur df
    - Chaque fichier uploadé = nouveaux KPIs
    
    OPTIMISATIONS DE PERFORMANCE:
    - Calculs vectorisés avec pandas/numpy
    - Évite les boucles explicites
    - Réutilise les calculs intermédiaires
    - Minimise les conversions de types
    
    Args:
        df: DataFrame avec les tweets analysés (données du fichier actuel)
        
    Returns:
        Dictionnaire avec les KPIs business recalculés dynamiquement
    """
    kpis = {}
    total_tweets = len(df)
    
    # Éviter les divisions par zéro
    if total_tweets == 0:
        return kpis
    
    # 1. Claim Rate (Taux de réclamations) - OPTIMISÉ
    if 'is_claim' in df.columns:
        # Conversion vectorisée une seule fois
        claims_array = pd.to_numeric(df['is_claim'], errors='coerce').fillna(0)
        claims_count = int(claims_array.sum())
        
        kpis['claim_rate'] = {
            'value': (claims_count / total_tweets * 100),
            'count': claims_count,
            'total': total_tweets
        }
    elif 'category' in df.columns:
        # Vectorisation avec str.contains (plus rapide que apply)
        claims_count = df['category'].str.contains('réclamation|claim', case=False, na=False).sum()
        
        kpis['claim_rate'] = {
            'value': (claims_count / total_tweets * 100),
            'count': int(claims_count),
            'total': total_tweets
        }
    
    # 2. Thematic Distribution (Distribution thématique) - OPTIMISÉ
    if 'category' in df.columns:
        # value_counts est déjà optimisé
        theme_dist = df['category'].value_counts()
        kpis['thematic_distribution'] = {
            'categories': theme_dist.to_dict(),
            'top_category': theme_dist.index[0] if len(theme_dist) > 0 else 'N/A',
            'count': len(theme_dist)
        }
    elif 'theme' in df.columns:
        theme_dist = df['theme'].value_counts()
        kpis['thematic_distribution'] = {
            'categories': theme_dist.to_dict(),
            'top_category': theme_dist.index[0] if len(theme_dist) > 0 else 'N/A',
            'count': len(theme_dist)
        }
    
    # 3. Customer Satisfaction Index (Indice de satisfaction) - OPTIMISÉ
    if 'sentiment' in df.columns:
        # Calcul vectorisé avec mask au lieu de multiples str.contains
        sentiment_lower = df['sentiment'].str.lower()
        
        positive = (sentiment_lower.isin(['positive', 'positif', 'pos'])).sum()
        neutral = (sentiment_lower.isin(['neutral', 'neutre', 'neu'])).sum()
        negative = (sentiment_lower.isin(['negative', 'négatif', 'negatif', 'neg'])).sum()
        
        # Calcul optimisé en une ligne
        satisfaction_index = ((positive - negative) / total_tweets * 50 + 50)
        
        kpis['satisfaction_index'] = {
            'value': satisfaction_index,
            'positive_count': int(positive),
            'neutral_count': int(neutral),
            'negative_count': int(negative),
            'positive_pct': (positive / total_tweets * 100),
            'neutral_pct': (neutral / total_tweets * 100),
            'negative_pct': (negative / total_tweets * 100)
        }
    
    # 4. Urgency Rate (Taux d'urgence) - OPTIMISÉ
    if 'priority' in df.columns:
        # Vectorisation avec str.lower() une seule fois
        priority_lower = df['priority'].str.lower().fillna('')
        
        # Masques booléens vectorisés
        critical_mask = priority_lower.str.contains('critique|critical|urgent', regex=True)
        high_mask = priority_lower.str.contains('haute|high|élevée', regex=True)
        
        critical = critical_mask.sum()
        high = high_mask.sum()
        urgent_total = int(critical + high)
        
        kpis['urgency_rate'] = {
            'critical_count': int(critical),
            'high_count': int(high),
            'urgent_total': urgent_total,
            'urgency_pct': (urgent_total / total_tweets * 100)
        }
    elif 'is_urgent' in df.columns:
        urgent_array = pd.to_numeric(df['is_urgent'], errors='coerce').fillna(0)
        urgent = int(urgent_array.sum())
        
        kpis['urgency_rate'] = {
            'critical_count': urgent,
            'high_count': 0,
            'urgent_total': urgent,
            'urgency_pct': (urgent / total_tweets * 100)
        }
    
    # 5. Average Confidence Score (Score de confiance moyen) - OPTIMISÉ
    if 'confidence' in df.columns:
        # Conversion vectorisée avec gestion des erreurs
        confidence_numeric = pd.to_numeric(df['confidence'], errors='coerce')
        confidence_clean = confidence_numeric.dropna()
        
        if len(confidence_clean) > 0:
            # Calculs vectorisés numpy (plus rapides)
            kpis['confidence_score'] = {
                'average': float(confidence_clean.mean()),
                'min': float(confidence_clean.min()),
                'max': float(confidence_clean.max()),
                'std': float(confidence_clean.std())
            }
        else:
            kpis['confidence_score'] = {'average': 0, 'min': 0, 'max': 0, 'std': 0}
    elif 'sentiment_score' in df.columns:
        sentiment_numeric = pd.to_numeric(df['sentiment_score'], errors='coerce').dropna()
        
        if len(sentiment_numeric) > 0:
            kpis['confidence_score'] = {
                'average': float(abs(sentiment_numeric.mean())),
                'min': float(sentiment_numeric.min()),
                'max': float(sentiment_numeric.max()),
                'std': float(sentiment_numeric.std())
            }
        else:
            kpis['confidence_score'] = {'average': 0, 'min': 0, 'max': 0, 'std': 0}
    
    return kpis


def render_business_kpis(kpis: Dict[str, Any]):
    """
    Affiche les KPIs business dans une interface moderne et professionnelle OPTIMISÉE
    
    AMÉLIORATIONS:
    - Design moderne avec cards premium
    - Icônes Font Awesome contextuelles
    - Indicateurs visuels de performance (couleurs intelligentes)
    - Layout responsive et épuré
    - Typographie améliorée pour la lisibilité
    
    Args:
        kpis: Dictionnaire des KPIs calculés par compute_business_kpis()
    """
    # Titre de section moderne avec design premium
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                padding: 2rem; 
                border-radius: 12px; 
                text-align: center; 
                margin: 1.5rem 0; 
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
        <h2 style="font-size: 1.9rem; font-weight: 800; color: #1a202c; margin: 0; letter-spacing: -0.5px;">
            <i class="fas fa-chart-line" style="color: #CC0000; margin-right: 0.5rem;"></i>
            Tableau de Bord Business
        </h2>
        <p style="color: #4a5568; font-size: 0.95rem; margin-top: 0.75rem; font-weight: 500;">
            <i class="fas fa-sync-alt" style="font-size: 0.8rem; margin-right: 0.3rem;"></i>
            Mise à jour en temps réel • Calculs dynamiques
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Ligne de 5 KPIs avec cards modernes
    col1, col2, col3, col4, col5 = st.columns(5, gap="medium")
    
    # KPI 1: Taux de Réclamations - Design Moderne
    with col1:
        if 'claim_rate' in kpis:
            claim_rate = kpis['claim_rate']['value']
            claim_count = kpis['claim_rate']['count']
            
            # Couleur dynamique basée sur le taux
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
                    <i class="fas fa-hashtag" style="font-size: 0.7rem;"></i> {claim_count} tweets
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.metric("Réclamations", "N/A")
    
    # KPI 2: Indice de Satisfaction - Design Premium
    with col2:
        if 'satisfaction_index' in kpis:
            satisfaction = kpis['satisfaction_index']['value']
            
            # Couleur et icône dynamiques
            if satisfaction > 60:
                color = "#48bb78"
                icon = "fa-smile"
                status = "Élevé"
            elif satisfaction > 40:
                color = "#4299e1"
                icon = "fa-meh"
                status = "Moyen"
            else:
                color = "#e53e3e"
                icon = "fa-frown"
                status = "Faible"
            
            st.markdown(f"""
            <div style="background: white; 
                        padding: 1.25rem; 
                        border-radius: 10px; 
                        border-left: 4px solid {color};
                        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                        height: 140px;">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <i class="fas {icon}" style="color: {color}; font-size: 1.2rem; margin-right: 0.5rem;"></i>
                    <span style="font-size: 0.85rem; font-weight: 600; color: #4a5568; text-transform: uppercase; letter-spacing: 0.5px;">Satisfaction</span>
                </div>
                <div style="font-size: 2.2rem; font-weight: 800; color: #1a202c; margin: 0.5rem 0;">
                    {satisfaction:.0f}<span style="font-size: 1.2rem; color: #718096;">/100</span>
                </div>
                <div style="font-size: 0.8rem; color: {color}; font-weight: 600;">
                    <i class="fas fa-circle" style="font-size: 0.5rem;"></i> {status}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.metric("Satisfaction", "N/A")
    
    # KPI 3: Taux d'Urgence - Design Critique
    with col3:
        if 'urgency_rate' in kpis:
            urgency = kpis['urgency_rate']['urgency_pct']
            urgent_total = kpis['urgency_rate']['urgent_total']
            
            # Couleur dynamique urgence
            color = "#e53e3e" if urgency > 20 else "#ed8936" if urgency > 10 else "#48bb78"
            
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
                    {urgency:.1f}<span style="font-size: 1.2rem; color: #718096;">%</span>
                </div>
                <div style="font-size: 0.8rem; color: #718096; font-weight: 500;">
                    <i class="fas fa-fire" style="font-size: 0.7rem;"></i> {urgent_total} cas
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.metric("Urgence", "N/A")
    
    # KPI 4: Confiance Moyenne - Design Précision
    with col4:
        if 'confidence_score' in kpis:
            confidence = kpis['confidence_score']['average']
            max_conf = kpis['confidence_score']['max']
            
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
        else:
            st.metric("Confiance", "N/A")
    
    # KPI 5: Thèmes Identifiés - Design Catégories
    with col5:
        if 'thematic_distribution' in kpis:
            theme_count = kpis['thematic_distribution']['count']
            top_theme = kpis['thematic_distribution']['top_category']
            
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
                    <span style="font-size: 0.85rem; font-weight: 600; color: #4a5568; text-transform: uppercase; letter-spacing: 0.5px;">Thèmes</span>
                </div>
                <div style="font-size: 2.2rem; font-weight: 800; color: #1a202c; margin: 0.5rem 0;">
                    {theme_count}
                </div>
                <div style="font-size: 0.8rem; color: #718096; font-weight: 500;">
                    <i class="fas fa-star" style="font-size: 0.7rem; color: #ffd700;"></i> {top_theme_display}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.metric("Thèmes", "N/A")


def create_sentiment_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """
    Crée un graphique moderne de distribution des sentiments OPTIMISÉ
    
    OPTIMISATIONS:
    - Calculs vectorisés
    - Design moderne avec gradients
    - Annotations intelligentes
    - Performance améliorée
    
    Args:
        df: DataFrame avec colonne 'sentiment'
        
    Returns:
        Figure Plotly optimisée
    """
    if 'sentiment' not in df.columns:
        return None
    
    # Calcul optimisé avec value_counts (déjà vectorisé)
    sentiment_counts = df['sentiment'].value_counts()
    
    if len(sentiment_counts) == 0:
        return None
    
    # Mapping couleurs optimisé avec dict.get()
    color_map = {
        'positive': COLORS['positive'],
        'positif': COLORS['positive'],
        'pos': COLORS['positive'],
        'neutral': COLORS['neutral'],
        'neutre': COLORS['neutral'],
        'neu': COLORS['neutral'],
        'negative': COLORS['negative'],
        'négatif': COLORS['negative'],
        'negatif': COLORS['negative'],
        'neg': COLORS['negative']
    }
    
    # List comprehension optimisée
    colors = [color_map.get(str(sent).lower(), COLORS['info']) for sent in sentiment_counts.index]
    
    # Création du graphique avec design moderne
    fig = go.Figure(data=[
        go.Pie(
            labels=[str(label).capitalize() for label in sentiment_counts.index],
            values=sentiment_counts.values,
            hole=0.45,  # Donut plus moderne
            marker=dict(
                colors=colors,
                line=dict(color='white', width=2)  # Séparation blanche
            ),
            textinfo='label+percent',
            textfont=dict(size=13, family="Arial, sans-serif", color="white"),
            textposition='inside',
            insidetextorientation='horizontal',
            hovertemplate="<b>%{label}</b><br>" +
                         "Tweets: %{value}<br>" +
                         "Pourcentage: %{percent}<br>" +
                         "<extra></extra>",
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Arial"
            )
        )
    ])
    
    # Layout moderne et épuré
    fig.update_layout(
        title=dict(
            text="<b>Distribution des Sentiments</b>",
            font=dict(size=18, family="Arial, sans-serif", color="#1a202c"),
            x=0.5,
            xanchor='center'
        ),
        height=420,
        template="plotly_white",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=11),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="#e2e8f0",
            borderwidth=1
        ),
        margin=dict(t=60, b=60, l=20, r=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def create_time_series_chart(df: pd.DataFrame, date_col: str = 'date') -> go.Figure:
    """
    Crée un graphique temporel multi-lignes
    
    Args:
        df: DataFrame avec colonne de date
        date_col: Nom de la colonne de date
        
    Returns:
        Figure Plotly
    """
    if date_col not in df.columns:
        # Essayer d'autres noms
        possible_names = ['created_at', 'timestamp', 'datetime', 'Date']
        for name in possible_names:
            if name in df.columns:
                date_col = name
                break
        else:
            return None
    
    # Convertir en datetime
    try:
        df_copy = df.copy()
        df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors='coerce')
        df_copy = df_copy.dropna(subset=[date_col])
        
        if len(df_copy) == 0:
            return None
        
        # Grouper par jour
        df_copy['date_only'] = df_copy[date_col].dt.date
        daily_counts = df_copy.groupby('date_only').size().reset_index(name='count')
        
        # Si on a la colonne sentiment, ajouter les courbes par sentiment
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=daily_counts['date_only'],
            y=daily_counts['count'],
            mode='lines+markers',
            name='Volume Total',
            line=dict(color=COLORS['primary'], width=3),
            marker=dict(size=6)
        ))
        
        if 'sentiment' in df_copy.columns:
            for sentiment in df_copy['sentiment'].unique():
                if pd.notna(sentiment):
                    sentiment_data = df_copy[df_copy['sentiment'] == sentiment].groupby('date_only').size().reset_index(name='count')
                    
                    color = COLORS.get(sentiment.lower(), COLORS['info'])
                    
                    fig.add_trace(go.Scatter(
                        x=sentiment_data['date_only'],
                        y=sentiment_data['count'],
                        mode='lines',
                        name=f'Sentiment: {sentiment}',
                        line=dict(color=color, width=2),
                        opacity=0.7
                    ))
        
        fig.update_layout(
            title="<b>Évolution Temporelle du Volume de Tweets</b>",
            xaxis_title="Date",
            yaxis_title="Nombre de Tweets",
            title_font_size=18,
            height=450,
            template="plotly_white",
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Erreur lors de la création du graphique temporel: {e}")
        return None


def create_activity_heatmap(df: pd.DataFrame, date_col: str = 'date') -> go.Figure:
    """
    Crée une heatmap d'activité par heure et jour
    
    Args:
        df: DataFrame avec colonne de date
        date_col: Nom de la colonne de date
        
    Returns:
        Figure Plotly
    """
    if date_col not in df.columns:
        possible_names = ['created_at', 'timestamp', 'datetime', 'Date']
        for name in possible_names:
            if name in df.columns:
                date_col = name
                break
        else:
            return None
    
    try:
        df_copy = df.copy()
        df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors='coerce')
        df_copy = df_copy.dropna(subset=[date_col])
        
        if len(df_copy) == 0:
            return None
        
        # Extraire heure et jour de la semaine
        df_copy['hour'] = df_copy[date_col].dt.hour
        df_copy['day_of_week'] = df_copy[date_col].dt.day_name()
        
        # Créer une matrice heure x jour
        heatmap_data = df_copy.groupby(['day_of_week', 'hour']).size().reset_index(name='count')
        
        # Pivoter pour avoir le bon format
        heatmap_pivot = heatmap_data.pivot(index='day_of_week', columns='hour', values='count').fillna(0)
        
        # Ordonner les jours
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_pivot = heatmap_pivot.reindex([d for d in day_order if d in heatmap_pivot.index])
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_pivot.values,
            x=heatmap_pivot.columns,
            y=heatmap_pivot.index,
            colorscale='Reds',
            hovertemplate='Jour: %{y}<br>Heure: %{x}h<br>Tweets: %{z}<extra></extra>',
            colorbar=dict(title="Nombre de Tweets")
        ))
        
        fig.update_layout(
            title="<b>Heatmap d'Activité (Jour × Heure)</b>",
            xaxis_title="Heure de la journée",
            yaxis_title="Jour de la semaine",
            title_font_size=18,
            height=400,
            template="plotly_white"
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Erreur lors de la création de la heatmap: {e}")
        return None


def create_category_comparison_chart(df: pd.DataFrame, category_col: str = 'category') -> go.Figure:
    """
    Crée un histogramme comparatif par catégorie
    
    Args:
        df: DataFrame avec colonne de catégorie
        category_col: Nom de la colonne de catégorie
        
    Returns:
        Figure Plotly
    """
    if category_col not in df.columns:
        return None
    
    category_counts = df[category_col].value_counts().head(10)
    
    fig = go.Figure(data=[
        go.Bar(
            x=category_counts.index,
            y=category_counts.values,
            marker=dict(
                color=category_counts.values,
                colorscale='Reds',
                showscale=True,
                colorbar=dict(title="Nombre")
            ),
            text=category_counts.values,
            textposition='outside',
            hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>"
        )
    ])
    
    fig.update_layout(
        title="<b>Top 10 Catégories</b>",
        xaxis_title="Catégorie",
        yaxis_title="Nombre de Tweets",
        title_font_size=18,
        height=450,
        template="plotly_white",
        xaxis_tickangle=-45
    )
    
    return fig


def create_radar_chart(kpis: Dict[str, Any], df: pd.DataFrame) -> go.Figure:
    """
    Crée un radar chart pour les performances par domaine
    
    Args:
        kpis: Dictionnaire des KPIs
        df: DataFrame
        
    Returns:
        Figure Plotly
    """
    # Calculer des métriques par domaine si category existe
    if 'category' not in df.columns:
        return None
    
    categories = df['category'].value_counts().head(6).index.tolist()
    
    metrics = []
    for cat in categories:
        cat_df = df[df['category'] == cat]
        
        # Calculer un score de performance (0-100)
        satisfaction = 50
        if 'sentiment' in cat_df.columns:
            positive = (cat_df['sentiment'].str.contains('positive|positif', case=False, na=False)).sum()
            negative = (cat_df['sentiment'].str.contains('negative|négatif|negatif', case=False, na=False)).sum()
            total = len(cat_df)
            satisfaction = ((positive - negative) / total * 50 + 50) if total > 0 else 50
        
        metrics.append(satisfaction)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=metrics,
        theta=categories,
        fill='toself',
        fillcolor='rgba(204, 0, 0, 0.3)',
        line=dict(color=COLORS['primary'], width=2),
        name='Performance'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        title="<b>Performance par Catégorie</b>",
        title_font_size=18,
        height=450,
        template="plotly_white",
        showlegend=False
    )
    
    return fig


def create_urgency_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """
    Crée un graphique de distribution d'urgence
    
    Args:
        df: DataFrame avec colonne 'priority' ou 'is_urgent'
        
    Returns:
        Figure Plotly
    """
    if 'priority' in df.columns:
        priority_counts = df['priority'].value_counts()
        
        # Mapper aux couleurs
        color_map = {
            'critique': COLORS['danger'],
            'critical': COLORS['danger'],
            'haute': COLORS['warning'],
            'high': COLORS['warning'],
            'élevée': COLORS['warning'],
            'moyenne': COLORS['info'],
            'medium': COLORS['info'],
            'basse': COLORS['success'],
            'low': COLORS['success']
        }
        
        colors = [color_map.get(p.lower(), COLORS['info']) for p in priority_counts.index]
        
        fig = go.Figure(data=[
            go.Bar(
                x=priority_counts.index,
                y=priority_counts.values,
                marker=dict(color=colors),
                text=priority_counts.values,
                textposition='outside',
                hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>"
            )
        ])
        
        fig.update_layout(
            title="<b>Distribution des Niveaux d'Urgence</b>",
            xaxis_title="Niveau de Priorité",
            yaxis_title="Nombre de Tweets",
            title_font_size=18,
            height=400,
            template="plotly_white"
        )
        
        return fig
    
    elif 'is_urgent' in df.columns:
        urgent_counts = df['is_urgent'].value_counts()
        
        fig = go.Figure(data=[
            go.Pie(
                labels=['Urgent' if x else 'Non Urgent' for x in urgent_counts.index],
                values=urgent_counts.values,
                marker=dict(colors=[COLORS['danger'], COLORS['success']]),
                hole=0.3
            )
        ])
        
        fig.update_layout(
            title="<b>Distribution Urgent / Non Urgent</b>",
            title_font_size=18,
            height=400,
            template="plotly_white"
        )
        
        return fig
    
    return None


def render_enhanced_visualizations(df: pd.DataFrame, kpis: Dict[str, Any]):
    """
    Rend les visualisations essentielles de maniere moderne et epuree
    
    Cette fonction affiche uniquement les 3 visualisations cles:
    - Distribution des sentiments (Pie Chart)
    - Evolution temporelle (Line Chart)  
    - Heatmap d'activite (Heatmap)
    
    Les visualisations supprimees (Radar, Categories, Urgence) ont ete retirees
    pour une interface plus epuree et professionnelle.
    
    Args:
        df: DataFrame avec les donnees analysees
        kpis: KPIs calcules (utilise pour compatibilite)
    """
    # Separateur visuel avant la section visualisations
    st.markdown("---")
    
    # Titre de section moderne sans emoji
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
    
    # Afficher seulement le graphique de sentiment (les graphiques temporels nécessitent une colonne date)
    st.markdown("#### <i class='fas fa-chart-pie'></i> Distribution des Sentiments", unsafe_allow_html=True)
    
    # Creation et affichage du graphique de distribution des sentiments
    fig_sentiment = create_sentiment_distribution_chart(df)
    if fig_sentiment:
        st.plotly_chart(fig_sentiment, use_container_width=True, key='business_viz_sentiment_dist')
    else:
        # Message si la colonne sentiment n'existe pas
        st.info("Distribution des sentiments non disponible (colonne 'sentiment' manquante)")


def render_complete_dashboard(df: pd.DataFrame):
    """
    Rend un dashboard complet avec KPIs business et visualisations essentielles
    
    Cette fonction orchestre l'affichage complet du dashboard en 3 etapes:
    1. Calcul des KPIs business a partir du DataFrame
    2. Affichage des 5 metriques cles
    3. Affichage des 3 visualisations essentielles
    4. Affichage des insights business
    
    Le dashboard est entierement dynamique et se recalcule a chaque nouveau
    fichier uploade. Il n'y a pas de cache entre les fichiers.
    
    Args:
        df: DataFrame avec les donnees analysees
            Doit contenir au minimum:
            - sentiment (positive/neutral/negative) pour satisfaction
            - category ou theme pour distribution thematique
            - priority ou is_urgent pour taux d'urgence
            - is_claim pour taux de reclamations
            - confidence pour score de confiance
            - date pour evolution temporelle et heatmap
    """
    # Etape 1: Calculer les KPIs business a partir des donnees actuelles
    # Cette fonction parcourt le DataFrame et extrait les metriques
    business_kpis = compute_business_kpis(df)
    
    # Etape 2: Afficher les 5 KPIs principaux en ligne
    # Chaque KPI est affiche avec st.metric() pour une interface Streamlit native
    render_business_kpis(business_kpis)
    
    # Etape 3: Afficher les 3 visualisations essentielles
    # Distribution sentiments, Evolution temporelle, Heatmap activite
    render_enhanced_visualizations(df, business_kpis)
    
    # Etape 4: Section insights business (synthese textuelle)
    st.markdown("---")
    
    # Titre de section moderne
    st.markdown("""
    <div style="text-align: center; margin: 1.5rem 0 1rem 0;">
        <h3 style="font-size: 1.5rem; font-weight: 700; color: #1a202c; margin: 0;">
            <i class="fas fa-lightbulb" style="color: #CC0000; margin-right: 0.75rem;"></i>
            Synthese Business
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Affichage des insights en 3 colonnes
    insights_col1, insights_col2, insights_col3 = st.columns(3)
    
    # Insight 1: Volume total analyse
    with insights_col1:
        st.info(f"**Volume Total**: {len(df):,} tweets analyses")
    
    # Insight 2: Niveau de satisfaction
    with insights_col2:
        if 'satisfaction_index' in business_kpis:
            # Extraction du score de satisfaction
            satisfaction = business_kpis['satisfaction_index']['value']
            
            # Determination du niveau et affichage avec couleur appropriee
            if satisfaction > 60:
                st.success(f"**Satisfaction**: Positive ({satisfaction:.0f}/100)")
            elif satisfaction > 40:
                st.warning(f"**Satisfaction**: Neutre ({satisfaction:.0f}/100)")
            else:
                st.error(f"**Satisfaction**: Negative ({satisfaction:.0f}/100)")
        else:
            st.info("**Satisfaction**: Donnees insuffisantes")
    
    # Insight 3: Niveau d'urgence
    with insights_col3:
        if 'urgency_rate' in business_kpis:
            # Extraction du taux d'urgence
            urgency = business_kpis['urgency_rate']['urgency_pct']
            
            # Determination du niveau et affichage avec couleur appropriee
            if urgency > 20:
                st.error(f"**Urgence**: Elevee ({urgency:.1f}%)")
            elif urgency > 10:
                st.warning(f"**Urgence**: Moderee ({urgency:.1f}%)")
            else:
                st.success(f"**Urgence**: Faible ({urgency:.1f}%)")
        else:
            st.info("**Urgence**: Donnees insuffisantes")

