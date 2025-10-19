"""
Analysis Manager Component
Handles file uploads, analysis configuration, and batch management
"""

import streamlit as st
import pandas as pd
import requests
import os
import uuid
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple


class AnalysisManager:
    """Manages analysis workflows and file processing"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
    
    def render_file_upload_section(self) -> Optional[pd.DataFrame]:
        """Render file upload interface and return uploaded data"""
        
        st.markdown("""
        <style>
            /* Enhanced File Uploader Styles */
            [data-testid="stFileUploader"] {
                background: #f8f9fa;
                border: 2px dashed #DC143C;
                border-radius: 12px;
                padding: 1.5rem;
                transition: all 0.3s ease;
            }
            
            [data-testid="stFileUploader"]:hover {
                border-color: #B91C3C;
                background: #f5f5f5;
                box-shadow: 0 2px 8px rgba(220, 20, 60, 0.1);
            }
            
            [data-testid="stFileUploader"] section {
                border: none !important;
                background: transparent !important;
            }
            
            [data-testid="stFileUploader"] label {
                color: #333 !important;
                font-size: 1rem !important;
                font-weight: 600 !important;
            }
            
            [data-testid="stFileUploader"] button {
                background: #DC143C !important;
                color: white !important;
                border: none !important;
                border-radius: 8px !important;
                padding: 0.6rem 1.5rem !important;
                font-weight: 500 !important;
                transition: all 0.3s ease !important;
            }
            
            [data-testid="stFileUploader"] button:hover {
                background: #B91C3C !important;
                box-shadow: 0 2px 6px rgba(220, 20, 60, 0.3) !important;
                transform: translateY(-1px);
            }
            
            [data-testid="stFileUploader"] small {
                color: #666 !important;
                font-size: 0.85rem !important;
            }
            
            .file-info {
                background: white;
                border-radius: 8px;
                padding: 1rem;
                margin-top: 1rem;
                border-left: 4px solid #28a745;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Modern header section
        st.markdown("""
        <div style="text-align: center; margin: 1.5rem 0;">
            <div style="font-size: 2.5rem; color: #DC143C; margin-bottom: 0.5rem;">📁</div>
            <div style="font-size: 1.3rem; font-weight: 600; color: #333; margin-bottom: 0.3rem;">
                Charger vos données Twitter
            </div>
            <div style="color: #666; font-size: 0.9rem;">
                Formats supportés: CSV, Excel (.xlsx)
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Glissez et déposez votre fichier ici ou cliquez pour parcourir",
            type=['csv', 'xlsx'],
            help="Fichier CSV ou Excel contenant les données de tweets à analyser",
            label_visibility="visible"
        )
        
        if uploaded_file is not None:
            try:
                # Read the file
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                # Display file info
                st.markdown(f"""
                <div class="file-info">
                    <strong>Fichier chargé:</strong> {uploaded_file.name}<br>
                    <strong>Taille:</strong> {len(df)} lignes, {len(df.columns)} colonnes<br>
                    <strong>Taille du fichier:</strong> {uploaded_file.size / 1024:.1f} KB
                </div>
                """, unsafe_allow_html=True)
                
                # Validate file structure
                validation_result = self.validate_tweet_data(df)
                if validation_result['valid']:
                    st.success("✅ Structure du fichier validée")
                    return df
                else:
                    st.error(f"❌ Erreur de validation: {validation_result['error']}")
                    st.info("💡 " + validation_result['suggestion'])
                    
            except Exception as e:
                st.error(f"Erreur lors de la lecture du fichier: {str(e)}")
        
        return None
    
    def validate_tweet_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate the structure of uploaded tweet data"""
        
        required_columns = ['text']  # Minimum required
        recommended_columns = ['text', 'author', 'date', 'retweet_count', 'favorite_count']
        
        # Check for required columns
        missing_required = [col for col in required_columns if col not in df.columns]
        if missing_required:
            return {
                'valid': False,
                'error': f"Colonnes requises manquantes: {', '.join(missing_required)}",
                'suggestion': "Assurez-vous que votre fichier contient au minimum une colonne 'text' avec le contenu des tweets."
            }
        
        # Check for recommended columns
        missing_recommended = [col for col in recommended_columns if col not in df.columns]
        if missing_recommended:
            st.warning(f"Colonnes recommandées manquantes: {', '.join(missing_recommended)}")
        
        # Check data quality
        if df['text'].isnull().sum() > 0:
            return {
                'valid': False,
                'error': "Des tweets ont un contenu vide",
                'suggestion': "Supprimez les lignes avec des tweets vides avant de charger le fichier."
            }
        
        return {'valid': True, 'error': None, 'suggestion': None}
    
    def render_analysis_configuration(self) -> Dict[str, Any]:
        """Render analysis configuration interface"""
        
        st.subheader("Configuration de l'Analyse")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # LLM Provider selection
            llm_provider = st.selectbox(
                "Fournisseur LLM",
                options=["mistral", "openai", "anthropic", "ollama"],
                index=0,
                help="Choisissez le fournisseur d'IA pour l'analyse"
            )
            
            # Max tweets
            max_tweets = st.slider(
                "Nombre maximum de tweets à analyser",
                min_value=50,
                max_value=1000,
                value=500,
                step=50,
                help="Limitez le nombre de tweets pour contrôler les coûts"
            )
        
        with col2:
            # Batch size
            batch_size = st.slider(
                "Taille des lots",
                min_value=5,
                max_value=20,
                value=10,
                help="Nombre de tweets traités simultanément"
            )
            
            # Analysis options
            include_sentiment = st.checkbox("Analyse de sentiment", value=True)
            include_category = st.checkbox("Catégorisation", value=True)
            include_priority = st.checkbox("Évaluation de priorité", value=True)
        
        return {
            'llm_provider': llm_provider,
            'max_tweets': max_tweets,
            'batch_size': batch_size,
            'include_sentiment': include_sentiment,
            'include_category': include_category,
            'include_priority': include_priority
        }
    
    def start_analysis(self, df: pd.DataFrame, config: Dict[str, Any]) -> Optional[str]:
        """Start analysis with uploaded data and configuration"""
        
        try:
            # Generate batch ID
            batch_id = str(uuid.uuid4())[:8]
            
            # Prepare data for API
            tweets_data = df.head(config['max_tweets']).to_dict('records')
            
            # API payload
            payload = {
                'batch_id': batch_id,
                'tweets': tweets_data,
                'config': config
            }
            
            # Send to API
            response = requests.post(
                f"{self.api_base_url}/analyze",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                st.session_state.current_batch_id = batch_id
                return batch_id
            else:
                st.error(f"Erreur API: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            st.error(f"Erreur de connexion: {str(e)}")
            return None
        except Exception as e:
            st.error(f"Erreur inattendue: {str(e)}")
            return None
    
    def render_analysis_progress(self, batch_id: str):
        """Render analysis progress interface"""
        
        try:
            response = requests.get(f"{self.api_base_url}/status/{batch_id}")
            if response.status_code == 200:
                status = response.json()
                
                # Progress bar
                if status.get('total_tweets', 0) > 0:
                    progress = status.get('analyzed_tweets', 0) / status.get('total_tweets', 1)
                    st.progress(progress)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total", status.get('total_tweets', 0))
                    with col2:
                        st.metric("Analysés", status.get('analyzed_tweets', 0))
                    with col3:
                        st.metric("Échecs", status.get('failed_tweets', 0))
                
                # Status message
                status_msg = status.get('status', 'unknown')
                if status_msg == 'completed':
                    st.success("✅ Analyse terminée!")
                elif status_msg == 'processing':
                    st.info("🔄 Analyse en cours...")
                    # Auto-refresh
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("❌ Erreur dans l'analyse")
                
                return status
            else:
                st.error("Impossible de récupérer le statut")
                return None
                
        except Exception as e:
            st.error(f"Erreur: {str(e)}")
            return None
    
    def render_recent_analyses(self):
        """Render list of recent analyses"""
        
        st.subheader("Analyses Récentes")
        
        # Get from session state or API
        recent_batches = st.session_state.get('recent_batches', [])
        
        if not recent_batches:
            st.info("Aucune analyse récente")
            return
        
        for batch in recent_batches[-5:]:  # Show last 5
            with st.expander(f"Analyse {batch['id']} - {batch['date']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Tweets", batch.get('total_tweets', 0))
                with col2:
                    st.metric("Statut", batch.get('status', 'Unknown'))
                with col3:
                    if st.button(f"Voir", key=f"view_{batch['id']}"):
                        st.session_state.current_batch_id = batch['id']
                        st.rerun()


def render_analysis_workflow():
    """Render the complete analysis workflow"""
    
    manager = AnalysisManager()
    
    # Step 1: File Upload
    st.markdown("### 📁 Étape 1: Chargement des Données")
    uploaded_data = manager.render_file_upload_section()
    
    if uploaded_data is not None:
        # Step 2: Configuration
        st.markdown("### ⚙️ Étape 2: Configuration")
        config = manager.render_analysis_configuration()
        
        # Step 3: Start Analysis
        st.markdown("### 🚀 Étape 3: Lancement de l'Analyse")
        
        if st.button("Démarrer l'Analyse", type="primary", use_container_width=True):
            with st.spinner("Démarrage de l'analyse..."):
                batch_id = manager.start_analysis(uploaded_data, config)
                
                if batch_id:
                    st.success(f"✅ Analyse démarrée! ID: {batch_id}")
                    
                    # Add to recent analyses
                    if 'recent_batches' not in st.session_state:
                        st.session_state.recent_batches = []
                    
                    st.session_state.recent_batches.append({
                        'id': batch_id,
                        'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'total_tweets': len(uploaded_data),
                        'status': 'processing'
                    })
                    
                    st.rerun()
    
    # Show current analysis progress
    current_batch = st.session_state.get('current_batch_id')
    if current_batch:
        st.markdown("### 📊 Analyse en Cours")
        manager.render_analysis_progress(current_batch)
    
    # Show recent analyses
    manager.render_recent_analyses()
