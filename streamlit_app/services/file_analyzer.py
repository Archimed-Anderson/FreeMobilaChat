"""
Service d'analyse de fichiers robuste
Gère l'upload, la validation et l'analyse de fichiers CSV/XLSX/JSON
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import chardet
import json
from dataclasses import dataclass, asdict
from datetime import datetime
import io

logger = logging.getLogger(__name__)

@dataclass
class FileAnalysisResult:
    """Résultat de l'analyse d'un fichier"""
    success: bool
    filename: str
    file_size: int
    file_type: str
    encoding: Optional[str]
    rows_count: int
    columns_count: int
    columns: List[str]
    data_preview: Optional[pd.DataFrame]
    errors: List[str]
    warnings: List[str]
    processing_time: float
    timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        result = asdict(self)
        if self.data_preview is not None:
            result['data_preview'] = self.data_preview.to_dict()
        return result

class FileAnalyzer:
    """
    Analyseur de fichiers robuste avec gestion d'erreurs complète
    """
    
    SUPPORTED_EXTENSIONS = {'.csv', '.xlsx', '.xls', '.json', '.parquet'}
    MAX_FILE_SIZE_MB = 50
    ENCODING_FALLBACKS = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    
    def __init__(self):
        """Initialisation de l'analyseur"""
        self.logger = logging.getLogger(__name__)
    
    def analyze_file(
        self,
        uploaded_file,
        detect_encoding: bool = True,
        preview_rows: int = 10
    ) -> FileAnalysisResult:
        """
        Analyse complète d'un fichier uploadé
        
        Args:
            uploaded_file: Fichier uploadé (Streamlit UploadedFile)
            detect_encoding: Détecter automatiquement l'encodage
            preview_rows: Nombre de lignes pour l'aperçu
            
        Returns:
            FileAnalysisResult avec toutes les informations
        """
        start_time = datetime.now()
        errors = []
        warnings = []
        
        try:
            # 1. Validation de base
            validation_result = self._validate_file(uploaded_file)
            if not validation_result['valid']:
                return FileAnalysisResult(
                    success=False,
                    filename=uploaded_file.name,
                    file_size=uploaded_file.size,
                    file_type=Path(uploaded_file.name).suffix,
                    encoding=None,
                    rows_count=0,
                    columns_count=0,
                    columns=[],
                    data_preview=None,
                    errors=validation_result['errors'],
                    warnings=[],
                    processing_time=(datetime.now() - start_time).total_seconds(),
                    timestamp=datetime.now().isoformat()
                )
            
            # 2. Détection de l'encodage
            encoding = None
            if detect_encoding and Path(uploaded_file.name).suffix == '.csv':
                uploaded_file.seek(0)
                sample = uploaded_file.read(10000)
                uploaded_file.seek(0)
                
                try:
                    detected = chardet.detect(sample)
                    encoding = detected['encoding']
                    confidence = detected['confidence']
                    
                    if confidence < 0.7:
                        warnings.append(f"Encodage détecté avec faible confiance: {confidence:.2%}")
                    
                    self.logger.info(f"Encodage détecté: {encoding} (confiance: {confidence:.2%})")
                except Exception as e:
                    warnings.append(f"Échec détection encodage: {str(e)}")
                    encoding = 'utf-8'
            
            # 3. Lecture du fichier
            df, read_errors = self._read_file(uploaded_file, encoding)
            
            if df is None:
                return FileAnalysisResult(
                    success=False,
                    filename=uploaded_file.name,
                    file_size=uploaded_file.size,
                    file_type=Path(uploaded_file.name).suffix,
                    encoding=encoding,
                    rows_count=0,
                    columns_count=0,
                    columns=[],
                    data_preview=None,
                    errors=read_errors,
                    warnings=warnings,
                    processing_time=(datetime.now() - start_time).total_seconds(),
                    timestamp=datetime.now().isoformat()
                )
            
            errors.extend(read_errors)
            
            # 4. Validation des données
            data_warnings = self._validate_data(df)
            warnings.extend(data_warnings)
            
            # 5. Préparation du résultat
            return FileAnalysisResult(
                success=True,
                filename=uploaded_file.name,
                file_size=uploaded_file.size,
                file_type=Path(uploaded_file.name).suffix,
                encoding=encoding,
                rows_count=len(df),
                columns_count=len(df.columns),
                columns=df.columns.tolist(),
                data_preview=df.head(preview_rows) if len(df) > 0 else None,
                errors=errors,
                warnings=warnings,
                processing_time=(datetime.now() - start_time).total_seconds(),
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            self.logger.error(f"Erreur analyse fichier: {str(e)}", exc_info=True)
            return FileAnalysisResult(
                success=False,
                filename=uploaded_file.name if uploaded_file else "unknown",
                file_size=uploaded_file.size if uploaded_file else 0,
                file_type="unknown",
                encoding=None,
                rows_count=0,
                columns_count=0,
                columns=[],
                data_preview=None,
                errors=[f"Erreur critique: {str(e)}"],
                warnings=warnings,
                processing_time=(datetime.now() - start_time).total_seconds(),
                timestamp=datetime.now().isoformat()
            )
    
    def _validate_file(self, uploaded_file) -> Dict[str, Any]:
        """Validation de base du fichier"""
        errors = []
        
        if uploaded_file is None:
            errors.append("Aucun fichier fourni")
            return {'valid': False, 'errors': errors}
        
        # Vérifier l'extension
        ext = Path(uploaded_file.name).suffix.lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            errors.append(
                f"Extension {ext} non supportée. "
                f"Extensions acceptées: {', '.join(self.SUPPORTED_EXTENSIONS)}"
            )
        
        # Vérifier la taille
        max_size_bytes = self.MAX_FILE_SIZE_MB * 1024 * 1024
        if uploaded_file.size > max_size_bytes:
            errors.append(
                f"Fichier trop volumineux ({uploaded_file.size / 1024 / 1024:.1f} MB). "
                f"Taille maximale: {self.MAX_FILE_SIZE_MB} MB"
            )
        
        # Vérifier que le fichier n'est pas vide
        if uploaded_file.size == 0:
            errors.append("Le fichier est vide")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _read_file(
        self,
        uploaded_file,
        encoding: Optional[str] = None
    ) -> Tuple[Optional[pd.DataFrame], List[str]]:
        """
        Lit le fichier avec gestion d'erreurs et fallbacks
        
        Returns:
            Tuple (DataFrame, Liste d'erreurs)
        """
        errors = []
        ext = Path(uploaded_file.name).suffix.lower()
        
        uploaded_file.seek(0)
        
        try:
            # CSV
            if ext == '.csv':
                return self._read_csv(uploaded_file, encoding, errors)
            
            # Excel
            elif ext in ['.xlsx', '.xls']:
                return self._read_excel(uploaded_file, errors)
            
            # JSON
            elif ext == '.json':
                return self._read_json(uploaded_file, encoding, errors)
            
            # Parquet
            elif ext == '.parquet':
                return self._read_parquet(uploaded_file, errors)
            
            else:
                errors.append(f"Format non géré: {ext}")
                return None, errors
                
        except Exception as e:
            self.logger.error(f"Erreur lecture fichier {ext}: {str(e)}", exc_info=True)
            errors.append(f"Erreur lecture: {str(e)}")
            return None, errors
    
    def _read_csv(
        self,
        uploaded_file,
        encoding: Optional[str],
        errors: List[str]
    ) -> Tuple[Optional[pd.DataFrame], List[str]]:
        """Lit un fichier CSV avec fallbacks d'encodage"""
        
        encodings_to_try = [encoding] if encoding else self.ENCODING_FALLBACKS
        
        for enc in encodings_to_try:
            if enc is None:
                continue
                
            try:
                uploaded_file.seek(0)
                df = pd.read_csv(
                    uploaded_file,
                    encoding=enc,
                    on_bad_lines='skip',
                    engine='python'
                )
                
                self.logger.info(f"CSV lu avec succès (encodage: {enc})")
                return df, errors
                
            except Exception as e:
                self.logger.warning(f"Échec lecture CSV avec {enc}: {str(e)}")
                continue
        
        errors.append(
            f"Impossible de lire le CSV avec les encodages testés: {', '.join(filter(None, encodings_to_try))}"
        )
        return None, errors
    
    def _read_excel(
        self,
        uploaded_file,
        errors: List[str]
    ) -> Tuple[Optional[pd.DataFrame], List[str]]:
        """Lit un fichier Excel"""
        
        try:
            uploaded_file.seek(0)
            
            # Essayer de lire toutes les feuilles
            excel_file = pd.ExcelFile(uploaded_file)
            
            if len(excel_file.sheet_names) > 1:
                errors.append(
                    f"Fichier contient {len(excel_file.sheet_names)} feuilles. "
                    f"Seule la première sera analysée."
                )
            
            df = pd.read_excel(uploaded_file, sheet_name=0)
            self.logger.info(f"Excel lu avec succès ({len(df)} lignes)")
            return df, errors
            
        except Exception as e:
            self.logger.error(f"Erreur lecture Excel: {str(e)}", exc_info=True)
            errors.append(f"Erreur lecture Excel: {str(e)}")
            return None, errors
    
    def _read_json(
        self,
        uploaded_file,
        encoding: Optional[str],
        errors: List[str]
    ) -> Tuple[Optional[pd.DataFrame], List[str]]:
        """Lit un fichier JSON"""
        
        try:
            uploaded_file.seek(0)
            content = uploaded_file.read()
            
            # Essayer de décoder
            if encoding:
                text = content.decode(encoding)
            else:
                text = content.decode('utf-8')
            
            # Parser JSON
            data = json.loads(text)
            
            # Convertir en DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                errors.append("Format JSON non reconnu")
                return None, errors
            
            self.logger.info(f"JSON lu avec succès ({len(df)} lignes)")
            return df, errors
            
        except Exception as e:
            self.logger.error(f"Erreur lecture JSON: {str(e)}", exc_info=True)
            errors.append(f"Erreur lecture JSON: {str(e)}")
            return None, errors
    
    def _read_parquet(
        self,
        uploaded_file,
        errors: List[str]
    ) -> Tuple[Optional[pd.DataFrame], List[str]]:
        """Lit un fichier Parquet"""
        
        try:
            uploaded_file.seek(0)
            df = pd.read_parquet(uploaded_file)
            self.logger.info(f"Parquet lu avec succès ({len(df)} lignes)")
            return df, errors
            
        except Exception as e:
            self.logger.error(f"Erreur lecture Parquet: {str(e)}", exc_info=True)
            errors.append(f"Erreur lecture Parquet: {str(e)}")
            return None, errors
    
    def _validate_data(self, df: pd.DataFrame) -> List[str]:
        """Valide les données et génère des avertissements"""
        warnings = []
        
        # Vérifier les lignes vides
        empty_rows = df.isnull().all(axis=1).sum()
        if empty_rows > 0:
            warnings.append(f"{empty_rows} ligne(s) complètement vide(s) détectée(s)")
        
        # Vérifier les colonnes sans nom
        unnamed_cols = [col for col in df.columns if str(col).startswith('Unnamed:')]
        if unnamed_cols:
            warnings.append(f"{len(unnamed_cols)} colonne(s) sans nom détectée(s)")
        
        # Vérifier les doublons
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            warnings.append(f"{duplicates} ligne(s) dupliquée(s) détectée(s)")
        
        # Vérifier les types de données incohérents
        for col in df.columns:
            if df[col].dtype == 'object':
                # Vérifier si mélange de types
                non_null = df[col].dropna()
                if len(non_null) > 0:
                    types = non_null.apply(type).unique()
                    if len(types) > 1:
                        warnings.append(
                            f"Colonne '{col}': types de données mixtes détectés"
                        )
        
        return warnings

# Instance globale
_file_analyzer = None

def get_file_analyzer() -> FileAnalyzer:
    """Retourne l'instance globale de FileAnalyzer"""
    global _file_analyzer
    if _file_analyzer is None:
        _file_analyzer = FileAnalyzer()
    return _file_analyzer

