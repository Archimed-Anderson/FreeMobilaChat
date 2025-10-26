"""
Page de Résultats - FreeMobilaChat
Interface dynamique pour l'affichage des résultats d'analyse
Développé dans le cadre d'un mémoire de master en Data Science
"""

import streamlit as st
import logging
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp
import numpy as np
from typing import Dict, Any, List
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Imports des services d'analyse
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from services.llm_analysis_engine import LLMAnalysisEngine, DatasetProfile
    from services.tweet_classifier import TweetClassifier
    ANALYSIS_ENGINE_AVAILABLE = True
except ImportError as e:
    print(f"Modules d'analyse non disponibles: {e}")
    ANALYSIS_ENGINE_AVAILABLE = False

# Imports conditionnels pour les bibliothèques avancées
try:
    from ydata_profiling import ProfileReport
    YDATA_PROFILING_AVAILABLE = True
except ImportError:
    YDATA_PROFILING_AVAILABLE = False

try:
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Configuration
st.set_page_config(
    page_title="Résultats d'Analyse - FreeMobilaChat",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Logger
logger = logging.getLogger(__name__)

def main():
    """Fonction principale d'affichage des résultats d'analyse dynamique"""
    
    # CSS personnalisé pour la page moderne
    _load_modern_css()
    
    # Header moderne avec navigation
    _render_modern_header()
    
    # Sidebar avec configuration
    _render_sidebar_config()
    
    # Zone d'upload centrale moderne
    uploaded_file = _render_modern_upload_zone()
    
    if uploaded_file is not None:
        # Analyse dynamique du fichier uploadé
        _handle_dynamic_analysis(uploaded_file)
        return
    
    # Affichage des résultats en cours
    _render_current_results()
    
    # Métriques globales
    _render_global_metrics()
    
    # Section des fonctionnalités
    _render_features_section()

def _load_modern_css():
    """Charge le CSS moderne pour la page"""
    st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem 0;
            margin-bottom: 2rem;
            border-radius: 10px;
            text-align: center;
            color: white;
        }
        
        .upload-zone {
            border: 2px dashed #CC0000;
            border-radius: 10px;
            padding: 2rem;
            text-align: center;
            background: #f8f9fa;
            margin: 2rem 0;
        }

        .kpi-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin: 1rem 0;
            border-left: 4px solid #CC0000;
        }
        
        .section-header {
            color: #CC0000;
            border-bottom: 2px solid #CC0000;
            padding-bottom: 0.5rem;
            margin-bottom: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

def _render_modern_header():
    """Affiche le header moderne"""
    st.markdown("""
    <div class="main-header">
        <h1>📊 Résultats d'Analyse Dynamique</h1>
        <p>Interface moderne pour l'affichage des résultats d'analyse de données</p>
    </div>
    """, unsafe_allow_html=True)
    
def _render_sidebar_config():
    """Affiche la configuration dans la sidebar"""
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        # Configuration de l'analyse
        st.markdown("#### 🔧 Paramètres d'Analyse")
        analysis_mode = st.selectbox(
            "Mode d'analyse",
            ["Complet", "Rapide", "Personnalisé"],
            help="Choisissez le mode d'analyse"
        )
        
        # Configuration des visualisations
        st.markdown("#### 📈 Visualisations")
        show_outliers = st.checkbox("Détecter les outliers", value=True)
        show_clustering = st.checkbox("Effectuer le clustering", value=True)
        max_visualizations = st.slider("Nombre max de visualisations", 1, 10, 5)
        
        # Configuration de l'export
        st.markdown("#### 💾 Export")
        export_format = st.selectbox(
            "Format d'export",
            ["CSV", "JSON", "Excel"],
            help="Format pour l'export des résultats"
        )
        
        # Sauvegarde de la configuration
        st.session_state['analysis_config'] = {
            'mode': analysis_mode,
            'show_outliers': show_outliers,
            'show_clustering': show_clustering,
            'max_visualizations': max_visualizations,
            'export_format': export_format
        }

def _render_modern_upload_zone():
    """Affiche la zone d'upload moderne"""
    st.markdown("### 📁 Upload de Fichier pour Analyse")
    
    uploaded_file = st.file_uploader(
        "Glissez-déposez votre fichier ici ou cliquez pour sélectionner",
        type=['csv', 'xlsx', 'json'],
        help="Formats supportés: CSV, Excel, JSON"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ Fichier '{uploaded_file.name}' chargé avec succès!")
        
        # Aperçu du fichier
        with st.expander("👀 Aperçu du fichier", expanded=True):
            try:
                if uploaded_file.name.endswith('.csv'):
                    df_preview = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith('.xlsx'):
                    df_preview = pd.read_excel(uploaded_file)
                elif uploaded_file.name.endswith('.json'):
                    df_preview = pd.read_json(uploaded_file)
                
                st.dataframe(df_preview.head(10), use_container_width=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Lignes", f"{len(df_preview):,}")
                with col2:
                    st.metric("Colonnes", len(df_preview.columns))
                with col3:
                    st.metric("Taille", f"{uploaded_file.size / 1024:.1f} KB")
                
            except Exception as e:
                st.error(f"Erreur lors de la lecture du fichier: {e}")
                return None
    
    return uploaded_file

def _handle_dynamic_analysis(uploaded_file):
    """Gère l'analyse dynamique du fichier uploadé"""
    
    try:
        # Lecture du fichier
        df = _read_uploaded_file(uploaded_file)
        
        if df is None or df.empty:
            st.error("Impossible de lire le fichier ou fichier vide")
        return
    
        # Affichage des informations du fichier
        _display_file_info(uploaded_file, df)
        
        # Bouton d'analyse
        if st.button("🚀 Lancer l'Analyse Dynamique", type="primary", use_container_width=True):
            # Analyse dynamique complète
            _perform_dynamic_analysis(df, uploaded_file.name)
        
        # Aperçu des données
        with st.expander("📋 Aperçu des données", expanded=True):
            st.dataframe(df.head(20), use_container_width=True, height=400)
            
            # Statistiques de base
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Lignes", f"{len(df):,}")
            with col2:
                st.metric("Colonnes", len(df.columns))
            with col3:
                st.metric("Valeurs manquantes", f"{df.isnull().sum().sum():,}")
        
    except Exception as e:
        st.error(f"Erreur lors du traitement du fichier: {str(e)}")
        logger.error(f"Error processing file: {str(e)}", exc_info=True)

def _read_uploaded_file(uploaded_file):
    """Lit le fichier uploadé selon son type"""
    try:
        if uploaded_file.name.endswith('.csv'):
            return pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx'):
            return pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith('.json'):
            return pd.read_json(uploaded_file)
        else:
            st.error("Format de fichier non supporté")
            return None
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier: {e}")
        return None

def _display_file_info(uploaded_file, df):
    """Affiche les informations du fichier"""
    st.markdown("### 📊 Informations du Fichier")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📁 Nom", uploaded_file.name)
    with col2:
        st.metric("📏 Taille", f"{uploaded_file.size / 1024:.1f} KB")
    with col3:
        st.metric("📊 Lignes", f"{len(df):,}")
    with col4:
        st.metric("📋 Colonnes", len(df.columns))
    
    # Détection automatique des types de colonnes
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
    datetime_columns = df.select_dtypes(include=['datetime64']).columns.tolist()
    
    if numeric_columns:
        st.info(f"🔢 Colonnes numériques détectées: {', '.join(numeric_columns[:3])}")
    if categorical_columns:
        st.info(f"📝 Colonnes catégorielles détectées: {', '.join(categorical_columns[:3])}")
    if datetime_columns:
        st.info(f"📅 Colonnes de date détectées: {', '.join(datetime_columns[:3])}")

def _perform_dynamic_analysis(df: pd.DataFrame, filename: str):
    """Effectue une analyse dynamique complète du dataset"""
    
    # Barre de progression
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Étape 1: Analyse des données de base
        status_text.text("🔍 Analyse des données de base...")
        progress_bar.progress(0.2)
        
        # Profil du dataset
        profile = _create_dataset_profile(df, filename)
        
        # Étape 2: Calcul des KPIs dynamiques
        status_text.text("📊 Calcul des KPIs dynamiques...")
        progress_bar.progress(0.4)
        
        kpis = _calculate_dynamic_kpis(df, profile)
        
        # Étape 3: Génération des visualisations
        status_text.text("📈 Génération des visualisations...")
        progress_bar.progress(0.6)
        
        visualizations = _generate_dynamic_visualizations(df, profile)
        
        # Étape 4: Analyse avancée
        status_text.text("🧠 Analyse avancée...")
        progress_bar.progress(0.8)
        
        advanced_analysis = _perform_advanced_analysis(df, profile)
        
        # Étape 5: Finalisation
        status_text.text("✅ Finalisation de l'analyse...")
        progress_bar.progress(1.0)
        
        # Nettoyage de la progression
        progress_bar.empty()
        status_text.empty()
        
        # Affichage des résultats
        _display_analysis_results(df, profile, kpis, visualizations, advanced_analysis)
        
    except Exception as e:
        st.error(f"Erreur lors de l'analyse: {str(e)}")
        logger.error(f"Error during analysis: {str(e)}", exc_info=True)

def _create_dataset_profile(df: pd.DataFrame, filename: str) -> Dict[str, Any]:
    """Crée un profil détaillé du dataset"""
    
    profile = {
        'filename': filename,
        'shape': df.shape,
        'columns': list(df.columns),
        'dtypes': df.dtypes.to_dict(),
        'memory_usage': df.memory_usage(deep=True).sum() / (1024 * 1024),  # MB
        'null_counts': df.isnull().sum().to_dict(),
        'null_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
        'duplicate_count': df.duplicated().sum(),
        'duplicate_percentage': (df.duplicated().sum() / len(df)) * 100,
        'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
        'categorical_columns': df.select_dtypes(include=['object']).columns.tolist(),
        'datetime_columns': df.select_dtypes(include=['datetime64']).columns.tolist(),
        'boolean_columns': df.select_dtypes(include=['bool']).columns.tolist()
    }
    
    return profile

def _calculate_dynamic_kpis(df: pd.DataFrame, profile: Dict[str, Any]) -> Dict[str, Any]:
    """Calcule les KPIs dynamiques selon le type de données"""
    
    kpis = {
        'basic_stats': {},
        'data_quality': {},
        'column_stats': {}
    }
    
    # Statistiques de base
    kpis['basic_stats'] = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'memory_usage_mb': profile['memory_usage'],
        'null_percentage': profile['null_percentage'],
        'duplicate_percentage': profile['duplicate_percentage']
    }
    
    # Qualité des données
    kpis['data_quality'] = {
        'completeness_score': 100 - profile['null_percentage'],
        'uniqueness_score': 100 - profile['duplicate_percentage'],
        'consistency_score': 85.0  # Score par défaut
    }
    
    # Statistiques par colonne
    for col in df.columns:
        col_stats = {
            'dtype': str(df[col].dtype),
            'null_count': df[col].isnull().sum(),
            'null_percentage': (df[col].isnull().sum() / len(df)) * 100,
            'unique_count': df[col].nunique(),
            'unique_percentage': (df[col].nunique() / len(df)) * 100
        }
        
        if col in profile['numeric_columns']:
            col_stats.update({
                'mean': df[col].mean(),
                'std': df[col].std(),
                'min': df[col].min(),
                'max': df[col].max(),
                'median': df[col].median()
            })
        
        kpis['column_stats'][col] = col_stats
    
    return kpis

def _generate_dynamic_visualizations(df: pd.DataFrame, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Génère des visualisations dynamiques selon le type de données"""
    
    visualizations = []
    
    # Visualisations numériques
    if profile['numeric_columns']:
        numeric_cols = profile['numeric_columns']
        
        # Histogrammes pour les colonnes numériques
        for col in numeric_cols[:3]:  # Limiter à 3 colonnes
            fig = px.histogram(
                df, x=col, 
                title=f"Distribution de {col}",
                color_discrete_sequence=['#CC0000']
            )
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(size=12)
            )
            visualizations.append({
                'type': 'histogram',
                'title': f'Distribution de {col}',
                'figure': fig,
                'description': f'Distribution des valeurs pour la colonne {col}'
            })
        
        # Scatter plot si plusieurs colonnes numériques
        if len(numeric_cols) >= 2:
            fig = px.scatter(
                df, x=numeric_cols[0], y=numeric_cols[1],
                title=f"Relation {numeric_cols[0]} vs {numeric_cols[1]}",
                color_discrete_sequence=['#CC0000']
            )
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(size=12)
            )
            visualizations.append({
                'type': 'scatter',
                'title': f'Relation {numeric_cols[0]} vs {numeric_cols[1]}',
                'figure': fig,
                'description': f'Relation entre {numeric_cols[0]} et {numeric_cols[1]}'
            })
        
        # Matrice de corrélation
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            fig = px.imshow(
                corr_matrix, 
                text_auto=True, 
                aspect="auto",
                title="Matrice de Corrélation",
                color_continuous_scale='RdBu'
            )
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(size=12)
            )
            visualizations.append({
                'type': 'heatmap',
                'title': 'Matrice de Corrélation',
                'figure': fig,
                'description': 'Corrélations entre les variables numériques'
            })
    
    # Visualisations catégorielles
    if profile['categorical_columns']:
        categorical_cols = profile['categorical_columns']
        
        for col in categorical_cols[:2]:  # Limiter à 2 colonnes
            value_counts = df[col].value_counts().head(10)
            fig = px.bar(
                x=value_counts.index, 
                y=value_counts.values,
                title=f"Top 10 - {col}",
                color=value_counts.values,
                color_continuous_scale='Reds'
            )
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(size=12),
                xaxis_tickangle=-45
            )
            visualizations.append({
                'type': 'bar',
                'title': f'Top 10 - {col}',
                'figure': fig,
                'description': f'Top 10 des valeurs les plus fréquentes pour {col}'
            })
    
    return visualizations

def _perform_advanced_analysis(df: pd.DataFrame, profile: Dict[str, Any]) -> Dict[str, Any]:
    """Effectue des analyses avancées selon les données disponibles"""
    
    analysis = {
        'outliers': [],
        'clusters': None,
        'anomalies': [],
        'insights': []
    }
    
    # Détection d'outliers pour les colonnes numériques
    if profile['numeric_columns'] and SKLEARN_AVAILABLE:
        for col in profile['numeric_columns']:
            outliers = _detect_outliers(df[col])
            if outliers:
                analysis['outliers'].append({
                    'column': col,
                    'count': len(outliers),
                    'percentage': (len(outliers) / len(df)) * 100
                })
    
    # Clustering si suffisamment de colonnes numériques
    if len(profile['numeric_columns']) >= 2 and SKLEARN_AVAILABLE:
        try:
            clusters = _perform_clustering(df[profile['numeric_columns']])
            analysis['clusters'] = clusters
        except Exception as e:
            logger.warning(f"Clustering failed: {e}")
    
    # Génération d'insights
    analysis['insights'] = _generate_insights(df, profile)
    
    return analysis

def _detect_outliers(series: pd.Series) -> List[int]:
    """Détecte les outliers dans une série numérique"""
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = series[(series < lower_bound) | (series > upper_bound)]
    return outliers.index.tolist()

def _perform_clustering(df_numeric: pd.DataFrame) -> Dict[str, Any]:
    """Effectue un clustering K-means sur les données numériques"""
    try:
        # Normalisation des données
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(df_numeric.fillna(0))
        
        # Clustering K-means
        kmeans = KMeans(n_clusters=3, random_state=42)
        clusters = kmeans.fit_predict(data_scaled)
        
        # Score de silhouette
        silhouette_avg = silhouette_score(data_scaled, clusters)
        
        return {
            'n_clusters': 3,
            'silhouette_score': silhouette_avg,
            'cluster_centers': kmeans.cluster_centers_.tolist(),
            'cluster_labels': clusters.tolist()
        }
    except Exception as e:
        logger.error(f"Clustering error: {e}")
        return None

def _generate_insights(df: pd.DataFrame, profile: Dict[str, Any]) -> List[str]:
    """Génère des insights automatiques sur les données"""
    
    insights = []
    
    # Insight sur la taille du dataset
    if len(df) > 10000:
        insights.append(f"Dataset volumineux avec {len(df):,} lignes - analyse robuste possible")
    elif len(df) < 100:
        insights.append(f"Dataset petit avec {len(df)} lignes - attention aux généralisations")
    
    # Insight sur les valeurs manquantes
    null_percentage = profile['null_percentage']
    if null_percentage > 20:
        insights.append(f"Taux élevé de valeurs manquantes ({null_percentage:.1f}%) - nettoyage recommandé")
    elif null_percentage < 5:
        insights.append(f"Dataset de bonne qualité avec seulement {null_percentage:.1f}% de valeurs manquantes")
    
    # Insight sur les colonnes numériques
    if len(profile['numeric_columns']) > 5:
        insights.append(f"Dataset riche avec {len(profile['numeric_columns'])} variables numériques")
    
    # Insight sur les doublons
    if profile['duplicate_percentage'] > 10:
        insights.append(f"Présence de doublons ({profile['duplicate_percentage']:.1f}%) - déduplication recommandée")
    
    return insights

def _display_analysis_results(df: pd.DataFrame, profile: Dict[str, Any], kpis: Dict[str, Any], 
                           visualizations: List[Dict[str, Any]], advanced_analysis: Dict[str, Any]):
    """Affiche les résultats de l'analyse"""
    
    st.markdown("## 📊 Résultats de l'Analyse Dynamique")
    
    # Métriques principales
    st.markdown("### 📈 Métriques Principales")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Lignes", f"{kpis['basic_stats']['total_rows']:,}")
    with col2:
        st.metric("Colonnes", kpis['basic_stats']['total_columns'])
    with col3:
        st.metric("Qualité", f"{kpis['data_quality']['completeness_score']:.1f}%")
    with col4:
        st.metric("Mémoire", f"{kpis['basic_stats']['memory_usage_mb']:.1f} MB")
    
    # Visualisations
    st.markdown("### 📈 Visualisations Dynamiques")
    for i, viz in enumerate(visualizations):
        st.markdown(f"#### {viz['title']}")
        st.plotly_chart(viz['figure'], use_container_width=True)
        st.caption(viz['description'])
        
        if i >= st.session_state.get('analysis_config', {}).get('max_visualizations', 5) - 1:
            break
    
    # Analyse avancée
    if advanced_analysis['outliers']:
        st.markdown("### 🔍 Détection d'Outliers")
        for outlier in advanced_analysis['outliers']:
            st.warning(f"Colonne {outlier['column']}: {outlier['count']} outliers ({outlier['percentage']:.1f}%)")
    
    if advanced_analysis['clusters']:
        st.markdown("### 🎯 Clustering")
        st.info(f"Score de silhouette: {advanced_analysis['clusters']['silhouette_score']:.3f}")
    
    # Insights
    if advanced_analysis['insights']:
        st.markdown("### 💡 Insights Automatiques")
        for insight in advanced_analysis['insights']:
            st.info(insight)
    
    # Export des résultats
    st.markdown("### 💾 Export des Résultats")
    col1, col2 = st.columns(2)
    
    with col1:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Télécharger CSV",
            data=csv,
            file_name=f"analyse_{profile['filename']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col2:
        results_json = {
            'profile': profile,
            'kpis': kpis,
            'analysis_timestamp': datetime.now().isoformat()
        }
        json_data = pd.Series(results_json).to_json(orient='index')
        st.download_button(
            label="📋 Télécharger JSON",
            data=json_data,
            file_name=f"kpis_{profile['filename']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

def _render_current_results():
    """Affiche les résultats en cours"""
    st.markdown("### 📊 Analyses en Cours")
    
    if 'analysis_results' in st.session_state:
        results = st.session_state['analysis_results']
        st.success(f"✅ Analyse terminée pour: {results['filename']}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Lignes analysées", f"{results['kpis']['basic_stats']['total_rows']:,}")
        with col2:
            st.metric("Qualité des données", f"{results['kpis']['data_quality']['completeness_score']:.1f}%")
    else:
        st.info("Aucune analyse en cours. Uploadez un fichier pour commencer.")

def _render_global_metrics():
    """Affiche les métriques globales"""
    st.markdown("### 🌍 Métriques Globales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Analyses effectuées", "0", "Nouvelle session")
    with col2:
        st.metric("Fichiers traités", "0", "Aucun")
    with col3:
        st.metric("Temps moyen", "0s", "N/A")
    with col4:
        st.metric("Taux de succès", "100%", "Prêt")

def _render_features_section():
    """Affiche la section des fonctionnalités"""
    st.markdown("### 🚀 Fonctionnalités Disponibles")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="kpi-card">
            <h4>📊 Analyse Dynamique</h4>
            <ul>
                <li>Profiling automatique</li>
                <li>Détection des types</li>
                <li>Calcul de KPIs adaptatifs</li>
                <li>Visualisations interactives</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="kpi-card">
            <h4>🔍 Analyse Avancée</h4>
            <ul>
                <li>Détection d'outliers</li>
                <li>Clustering automatique</li>
                <li>Insights générés</li>
                <li>Rapports détaillés</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()