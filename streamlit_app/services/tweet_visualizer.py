"""
Module de Visualisation de Tweets - FreeMobilaChat
===================================================

Visualisations avancées pour les résultats de classification.
Conforme aux spécifications techniques du projet.

Fonctionnalités:
- Métriques de nettoyage
- Distribution sentiment
- Charts par catégorie
- Export CSV
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Couleurs Free Mobile
COLORS = {
    'primary': '#CC0000',
    'secondary': '#8B0000',
    'positive': '#28a745',
    'neutral': '#6c757d',
    'negative': '#dc3545',
    'info': '#17a2b8',
    'warning': '#ffc107'
}


def display_cleaning_stats(stats: Dict):
    """
    Affiche les métriques de nettoyage en colonnes
    
    Args:
        stats: Dictionnaire de statistiques de nettoyage
    """
    st.markdown("### 🧹 Statistiques de Nettoyage", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Tweets Originaux",
            f"{stats.get('total_original', 0):,}",
            help="Nombre total de tweets dans le fichier uploadé"
        )
    
    with col2:
        removed = stats.get('total_original', 0) - stats.get('total_cleaned', 0)
        st.metric(
            "Tweets Supprimés",
            f"{removed:,}",
            delta=f"-{removed}",
            delta_color="inverse",
            help="Valeurs manquantes + doublons"
        )
    
    with col3:
        st.metric(
            "Doublons Retirés",
            f"{stats.get('duplicates_removed', 0):,}",
            help="Tweets identiques détectés par hash MD5"
        )
    
    with col4:
        st.metric(
            "Tweets Nettoyés",
            f"{stats.get('total_cleaned', 0):,}",
            delta=f"+{stats.get('total_cleaned', 0)}",
            delta_color="normal",
            help="Tweets prêts pour classification"
        )
    
    # Détails supplémentaires
    with st.expander("📊 Détails du Nettoyage", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Longueur Moyenne**")
            st.write(f"- Avant: {stats.get('avg_length_before', 0):.1f} caractères")
            st.write(f"- Après: {stats.get('avg_length_after', 0):.1f} caractères")
        
        with col2:
            st.markdown("**Opérations**")
            for op in stats.get('cleaning_operations', []):
                st.write(f"- {op}")


def display_sentiment_metrics(df: pd.DataFrame):
    """
    Affiche la distribution du sentiment
    
    Args:
        df: DataFrame avec colonne 'sentiment'
    """
    if 'sentiment' not in df.columns:
        st.warning("Colonne 'sentiment' non trouvée")
        return
    
    st.markdown("### 😊 Distribution des Sentiments", unsafe_allow_html=True)
    
    # Comptage
    sentiment_counts = df['sentiment'].value_counts()
    total = len(df)
    
    # KPIs en colonnes
    col1, col2, col3 = st.columns(3)
    
    with col1:
        positif_count = sentiment_counts.get('positif', 0)
        positif_pct = (positif_count / total * 100) if total > 0 else 0
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['positive']}22, {COLORS['positive']}11); 
                    padding: 1.5rem; border-radius: 10px; border-left: 4px solid {COLORS['positive']};">
            <h3 style="color: {COLORS['positive']}; margin: 0;">😊 Positif</h3>
            <div style="font-size: 2rem; font-weight: 800; color: #1a202c; margin: 0.5rem 0;">
                {positif_count:,}
            </div>
            <div style="font-size: 0.9rem; color: #666;">
                {positif_pct:.1f}% du total
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        neutre_count = sentiment_counts.get('neutre', 0)
        neutre_pct = (neutre_count / total * 100) if total > 0 else 0
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['neutral']}22, {COLORS['neutral']}11); 
                    padding: 1.5rem; border-radius: 10px; border-left: 4px solid {COLORS['neutral']};">
            <h3 style="color: {COLORS['neutral']}; margin: 0;">😐 Neutre</h3>
            <div style="font-size: 2rem; font-weight: 800; color: #1a202c; margin: 0.5rem 0;">
                {neutre_count:,}
            </div>
            <div style="font-size: 0.9rem; color: #666;">
                {neutre_pct:.1f}% du total
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        negatif_count = sentiment_counts.get('negatif', 0)
        negatif_pct = (negatif_count / total * 100) if total > 0 else 0
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['negative']}22, {COLORS['negative']}11); 
                    padding: 1.5rem; border-radius: 10px; border-left: 4px solid {COLORS['negative']};">
            <h3 style="color: {COLORS['negative']}; margin: 0;">☹️ Négatif</h3>
            <div style="font-size: 2rem; font-weight: 800; color: #1a202c; margin: 0.5rem 0;">
                {negatif_count:,}
            </div>
            <div style="font-size: 0.9rem; color: #666;">
                {negatif_pct:.1f}% du total
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Graphique donut
    fig = go.Figure(data=[
        go.Pie(
            labels=['Positif', 'Neutre', 'Négatif'],
            values=[
                sentiment_counts.get('positif', 0),
                sentiment_counts.get('neutre', 0),
                sentiment_counts.get('negatif', 0)
            ],
            hole=0.5,
            marker=dict(colors=[COLORS['positive'], COLORS['neutral'], COLORS['negative']]),
            textinfo='label+percent',
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Pourcentage: %{percent}<extra></extra>"
        )
    ])
    
    fig.update_layout(
        title="<b>Répartition des Sentiments</b>",
        title_font_size=16,
        height=400,
        template="plotly_white",
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True, key='mistral_sentiment_donut')


def display_category_chart(df: pd.DataFrame):
    """
    Bar chart des catégories
    
    Args:
        df: DataFrame avec colonne 'categorie'
    """
    if 'categorie' not in df.columns:
        st.warning("Colonne 'categorie' non trouvée")
        return
    
    st.markdown("### 📊 Distribution par Catégorie", unsafe_allow_html=True)
    
    # Comptage
    category_counts = df['categorie'].value_counts().sort_values(ascending=False)
    
    # Bar chart
    fig = px.bar(
        x=category_counts.index,
        y=category_counts.values,
        labels={'x': 'Catégorie', 'y': 'Nombre de Tweets'},
        title="<b>Répartition par Catégorie</b>",
        color=category_counts.values,
        color_continuous_scale='Reds'
    )
    
    fig.update_layout(
        title_font_size=16,
        height=400,
        template="plotly_white",
        showlegend=False,
        xaxis_title="Catégorie",
        yaxis_title="Nombre de Tweets"
    )
    
    st.plotly_chart(fig, use_container_width=True, key='mistral_category_bar')


def display_confidence_distribution(df: pd.DataFrame):
    """
    Affiche la distribution des scores de confiance
    
    Args:
        df: DataFrame avec colonne 'score_confiance'
    """
    if 'score_confiance' not in df.columns:
        return
    
    st.markdown("### 🎯 Distribution de la Confiance", unsafe_allow_html=True)
    
    # Histogramme
    fig = px.histogram(
        df,
        x='score_confiance',
        nbins=20,
        title="<b>Distribution des Scores de Confiance</b>",
        labels={'score_confiance': 'Score de Confiance', 'count': 'Fréquence'},
        color_discrete_sequence=[COLORS['primary']]
    )
    
    fig.update_layout(
        title_font_size=16,
        height=350,
        template="plotly_white",
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True, key='mistral_confidence_hist')
    
    # Statistiques
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Confiance Moyenne", f"{df['score_confiance'].mean():.2f}")
    with col2:
        st.metric("Confiance Min", f"{df['score_confiance'].min():.2f}")
    with col3:
        st.metric("Confiance Max", f"{df['score_confiance'].max():.2f}")


def display_classification_summary(df: pd.DataFrame):
    """
    Affiche un résumé complet de la classification
    
    Args:
        df: DataFrame classifié
    """
    st.markdown("### 📈 Résumé de la Classification", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="background: white; padding: 1.25rem; border-radius: 10px; 
                    border-left: 4px solid {COLORS['primary']}; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
            <div style="font-size: 0.85rem; font-weight: 600; color: #4a5568; margin-bottom: 0.5rem;">
                <i class="fas fa-hashtag" style="color: {COLORS['primary']};"></i> TOTAL TWEETS
            </div>
            <div style="font-size: 2rem; font-weight: 800; color: #1a202c;">
                {len(df):,}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_conf = df['score_confiance'].mean() if 'score_confiance' in df.columns else 0
        color = COLORS['positive'] if avg_conf > 0.75 else COLORS['warning'] if avg_conf > 0.5 else COLORS['negative']
        st.markdown(f"""
        <div style="background: white; padding: 1.25rem; border-radius: 10px; 
                    border-left: 4px solid {color}; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
            <div style="font-size: 0.85rem; font-weight: 600; color: #4a5568; margin-bottom: 0.5rem;">
                <i class="fas fa-shield-alt" style="color: {color};"></i> CONFIANCE MOY.
            </div>
            <div style="font-size: 2rem; font-weight: 800; color: #1a202c;">
                {avg_conf:.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if 'sentiment' in df.columns:
            negatif_count = (df['sentiment'] == 'negatif').sum()
            negatif_pct = (negatif_count / len(df) * 100) if len(df) > 0 else 0
            st.markdown(f"""
            <div style="background: white; padding: 1.25rem; border-radius: 10px; 
                        border-left: 4px solid {COLORS['negative']}; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                <div style="font-size: 0.85rem; font-weight: 600; color: #4a5568; margin-bottom: 0.5rem;">
                    <i class="fas fa-frown" style="color: {COLORS['negative']};"></i> NÉGATIFS
                </div>
                <div style="font-size: 2rem; font-weight: 800; color: #1a202c;">
                    {negatif_pct:.1f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        if 'categorie' in df.columns:
            unique_categories = df['categorie'].nunique()
            st.markdown(f"""
            <div style="background: white; padding: 1.25rem; border-radius: 10px; 
                        border-left: 4px solid {COLORS['info']}; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                <div style="font-size: 0.85rem; font-weight: 600; color: #4a5568; margin-bottom: 0.5rem;">
                    <i class="fas fa-tags" style="color: {COLORS['info']};"></i> CATÉGORIES
                </div>
                <div style="font-size: 2rem; font-weight: 800; color: #1a202c;">
                    {unique_categories}
                </div>
            </div>
            """, unsafe_allow_html=True)


def export_results_csv(df: pd.DataFrame, filename: str = "results.csv") -> bytes:
    """
    Génère CSV pour download button
    
    Args:
        df: DataFrame à exporter
        filename: Nom du fichier (non utilisé, pour compatibilité)
        
    Returns:
        Bytes du CSV encodé
    """
    try:
        # Conversion en CSV
        csv_data = df.to_csv(index=False).encode('utf-8')
        logger.info(f"CSV généré: {len(df)} lignes")
        return csv_data
    except Exception as e:
        logger.error(f"Erreur génération CSV: {e}")
        return b""


def display_mistral_results(df: pd.DataFrame, stats: Optional[Dict] = None):
    """
    Affiche un dashboard complet des résultats Mistral
    
    Args:
        df: DataFrame avec classifications Mistral
        stats: Statistiques optionnelles
    """
    st.markdown("## 🤖 Résultats de Classification Mistral", unsafe_allow_html=True)
    
    # Résumé
    display_classification_summary(df)
    
    st.markdown("---")
    
    # Visualisations en colonnes
    col1, col2 = st.columns(2)
    
    with col1:
        display_sentiment_metrics(df)
    
    with col2:
        display_category_chart(df)
    
    # Distribution confiance
    if 'score_confiance' in df.columns:
        st.markdown("---")
        display_confidence_distribution(df)
    
    # Tableau détaillé
    st.markdown("---")
    st.markdown("### 📋 Tableau Détaillé", unsafe_allow_html=True)
    
    # Colonnes à afficher
    display_columns = ['sentiment', 'categorie', 'score_confiance']
    if 'text_cleaned' in df.columns:
        display_columns = ['text_cleaned'] + display_columns
    elif 'text' in df.columns:
        display_columns = ['text'] + display_columns
    
    # Filtrer les colonnes existantes
    display_columns = [col for col in display_columns if col in df.columns]
    
    st.dataframe(
        df[display_columns].head(100),
        use_container_width=True,
        height=400
    )


def create_comparison_chart(df: pd.DataFrame, method1_col: str, method2_col: str):
    """
    Crée un graphique de comparaison entre deux méthodes de classification
    
    Args:
        df: DataFrame avec résultats
        method1_col: Colonne première méthode
        method2_col: Colonne deuxième méthode
    """
    if method1_col not in df.columns or method2_col not in df.columns:
        return
    
    # Comptage croisé
    comparison = pd.crosstab(df[method1_col], df[method2_col], margins=True)
    
    st.markdown("### 🔄 Comparaison des Méthodes", unsafe_allow_html=True)
    st.dataframe(comparison, use_container_width=True)


# Fonction helper pour afficher les métriques Mistral
def display_mistral_metrics(classifier_stats: Dict):
    """
    Affiche les métriques de performance du classificateur Mistral
    
    Args:
        classifier_stats: Stats retournées par MistralClassifier.get_classification_stats()
    """
    st.markdown("### 🎯 Métriques de Classification", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Classifié", f"{classifier_stats.get('total_classified', 0):,}")
    
    with col2:
        st.metric("Confiance Moyenne", f"{classifier_stats.get('avg_confidence', 0):.2f}")
    
    with col3:
        sentiment_dist = classifier_stats.get('sentiment_distribution', {})
        dominant_sentiment = max(sentiment_dist, key=sentiment_dist.get) if sentiment_dist else 'N/A'
        st.metric("Sentiment Dominant", dominant_sentiment.capitalize())

