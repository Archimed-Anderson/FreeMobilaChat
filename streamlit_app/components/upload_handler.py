"""
Gestionnaire d'upload robuste avec validation et fallback
Support multi-formats avec gestion d'erreurs gracieuse
"""

import os
import io
import time
import logging
import pandas as pd
import streamlit as st
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path
import chardet
import zipfile
from datetime import datetime

from ..config.settings import get_config, UserRole
from ..services.data_processor import DataProcessor
from ..utils.validators import FileValidator
from ..utils.helpers import format_file_size, get_file_extension

logger = logging.getLogger(__name__)

class UploadHandler:
    """Gestionnaire d'upload avec validation et fallback"""
    
    def __init__(self):
        self.config = get_config()
        self.validator = FileValidator()
        self.data_processor = DataProcessor()
        
    def render_upload_zone(self) -> Optional[Dict[str, Any]]:
        """Affiche la zone d'upload et retourne les données si upload réussi"""
        
        # CSS pour la zone d'upload moderne
        st.markdown("""
        <style>
        .upload-zone {
            border: 2px dashed #1f77b4;
            border-radius: 10px;
            padding: 2rem;
            text-align: center;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            transition: all 0.3s ease;
            margin: 1rem 0;
        }
        
        .upload-zone:hover {
            border-color: #0d6efd;
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(31, 119, 180, 0.15);
        }
        
        .upload-icon {
            font-size: 3rem;
            color: #1f77b4;
            margin-bottom: 1rem;
        }
        
        .upload-text {
            font-size: 1.2rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 0.5rem;
        }
        
        .upload-subtext {
            color: #666;
            font-size: 0.9rem;
        }
        
        .file-info {
            background: white;
            border-radius: 8px;
            padding: 1rem;
            margin-top: 1rem;
            border-left: 4px solid #28a745;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .validation-error {
            background: #f8d7da;
            border-left-color: #dc3545;
            color: #721c24;
        }
        
        .validation-warning {
            background: #fff3cd;
            border-left-color: #ffc107;
            color: #856404;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Zone d'upload
        st.markdown("""
        <div class="upload-zone">
            <div class="upload-icon"></div>
            <div class="upload-text">Glissez et déposez votre fichier ici</div>
            <div class="upload-subtext">
                Formats supportés: CSV, Excel, JSON, Parquet<br>
                Taille maximale: {max_size}
            </div>
        </div>
        """.format(max_size=format_file_size(self.config.max_file_size)), 
        unsafe_allow_html=True)
        
        # File uploader Streamlit
        uploaded_file = st.file_uploader(
            "Choisir un fichier",
            type=self.config.supported_formats,
            help=f"Formats supportés: {', '.join(self.config.supported_formats)}",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            return self._process_uploaded_file(uploaded_file)
        
        return None
    
    def _process_uploaded_file(self, uploaded_file) -> Optional[Dict[str, Any]]:
        """Traite le fichier uploadé avec validation"""
        
        try:
            # Validation de base
            validation_result = self.validator.validate_file(uploaded_file)
            
            if not validation_result["valid"]:
                st.error(f" **Erreur de validation**: {validation_result['error']}")
                if validation_result.get("suggestion"):
                    st.info(f" **Suggestion**: {validation_result['suggestion']}")
                return None
            
            # Affichage des informations du fichier
            file_info = self._display_file_info(uploaded_file, validation_result)
            
            # Lecture et validation des données
            with st.spinner(" Lecture et validation des données..."):
                data_result = self._read_file_data(uploaded_file)
            
            if not data_result["success"]:
                st.error(f" **Erreur de lecture**: {data_result['error']}")
                return None
            
            # Validation des données
            data_validation = self.validator.validate_data_structure(data_result["data"])
            
            if not data_validation["valid"]:
                st.error(f" **Structure de données invalide**: {data_validation['error']}")
                if data_validation.get("suggestions"):
                    for suggestion in data_validation["suggestions"]:
                        st.info(f" {suggestion}")
                return None
            
            # Affichage des avertissements
            if data_validation.get("warnings"):
                for warning in data_validation["warnings"]:
                    st.warning(f" {warning}")
            
            # Sauvegarde en session
            self._save_to_session(uploaded_file, data_result["data"], file_info)
            
            # Succès
            st.success(" **Fichier chargé avec succès!**")
            
            return {
                "file": uploaded_file,
                "data": data_result["data"],
                "info": file_info,
                "validation": data_validation
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement du fichier: {str(e)}")
            st.error(f" **Erreur inattendue**: {str(e)}")
            return None
    
    def _display_file_info(self, uploaded_file, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Affiche les informations du fichier"""
        
        file_size = uploaded_file.size
        file_extension = get_file_extension(uploaded_file.name)
        
        info = {
            "name": uploaded_file.name,
            "size": file_size,
            "size_formatted": format_file_size(file_size),
            "extension": file_extension,
            "type": uploaded_file.type,
            "upload_time": datetime.now().isoformat()
        }
        
        # Affichage des informations
        st.markdown(f"""
        <div class="file-info">
            <strong> Fichier:</strong> {info['name']}<br>
            <strong> Taille:</strong> {info['size_formatted']}<br>
            <strong> Type:</strong> {info['extension'].upper()}<br>
            <strong>⏰ Chargé:</strong> {datetime.now().strftime('%H:%M:%S')}
        </div>
        """, unsafe_allow_html=True)
        
        return info
    
    def _read_file_data(self, uploaded_file) -> Dict[str, Any]:
        """Lit les données du fichier avec détection d'encodage"""
        
        try:
            # Détection de l'encodage
            file_content = uploaded_file.read()
            encoding_result = chardet.detect(file_content)
            encoding = encoding_result.get('encoding', 'utf-8')
            
            # Reset du fichier
            uploaded_file.seek(0)
            
            # Lecture selon le type de fichier
            file_extension = get_file_extension(uploaded_file.name).lower()
            
            if file_extension == '.csv':
                data = pd.read_csv(uploaded_file, encoding=encoding)
            elif file_extension in ['.xlsx', '.xls']:
                data = pd.read_excel(uploaded_file)
            elif file_extension == '.json':
                data = pd.read_json(uploaded_file)
            elif file_extension == '.parquet':
                data = pd.read_parquet(uploaded_file)
            else:
                return {"success": False, "error": f"Format non supporté: {file_extension}"}
            
            # Validation des données
            if data.empty:
                return {"success": False, "error": "Le fichier est vide"}
            
            # Nettoyage des données
            data = self.data_processor.clean_data(data)
            
            return {
                "success": True,
                "data": data,
                "encoding": encoding,
                "shape": data.shape
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du fichier: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _save_to_session(self, uploaded_file, data: pd.DataFrame, file_info: Dict[str, Any]):
        """Sauvegarde les données en session"""
        
        st.session_state.uploaded_file = uploaded_file
        st.session_state.uploaded_data = data
        st.session_state.uploaded_filename = file_info["name"]
        st.session_state.file_info = file_info
        st.session_state.upload_time = datetime.now().isoformat()
    
    def get_uploaded_data(self) -> Optional[Dict[str, Any]]:
        """Récupère les données uploadées depuis la session"""
        
        if "uploaded_data" not in st.session_state:
            return None
        
        return {
            "data": st.session_state.uploaded_data,
            "filename": st.session_state.get("uploaded_filename"),
            "file_info": st.session_state.get("file_info", {}),
            "upload_time": st.session_state.get("upload_time")
        }
    
    def clear_uploaded_data(self):
        """Nettoie les données uploadées"""
        
        keys_to_clear = [
            "uploaded_file", "uploaded_data", "uploaded_filename",
            "file_info", "upload_time", "current_batch_id"
        ]
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
    
    def render_upload_progress(self, progress: float, message: str = ""):
        """Affiche la barre de progression d'upload"""
        
        st.progress(progress)
        if message:
            st.caption(message)
    
    def compress_large_file(self, data: pd.DataFrame, max_size: int = 10 * 1024 * 1024) -> bytes:
        """Compresse un fichier si nécessaire"""
        
        # Convertir en CSV
        csv_buffer = io.StringIO()
        data.to_csv(csv_buffer, index=False)
        csv_content = csv_buffer.getvalue().encode('utf-8')
        
        if len(csv_content) <= max_size:
            return csv_content
        
        # Compression ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("data.csv", csv_content)
        
        return zip_buffer.getvalue()

# Instance globale
upload_handler = UploadHandler()

def get_upload_handler() -> UploadHandler:
    """Retourne l'instance du gestionnaire d'upload"""
    return upload_handler
