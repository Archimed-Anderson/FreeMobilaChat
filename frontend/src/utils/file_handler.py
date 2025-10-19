"""
File Handler Utility
Universal file reading and validation
"""

import pandas as pd
import json
import io
from typing import Union, Dict, Any, Optional
from pathlib import Path
import logging
import streamlit as st

logger = logging.getLogger(__name__)


class FileHandler:
    """
    Universal file handler for CSV, Excel, and JSON files
    
    Features:
    - Automatic encoding detection
    - Format validation
    - Error handling with user-friendly messages
    - Support for multiple file formats
    """
    
    SUPPORTED_FORMATS = {
        'csv': ['.csv', '.txt'],
        'excel': ['.xlsx', '.xls'],
        'json': ['.json']
    }
    
    @staticmethod
    @st.cache_data(show_spinner=False)
    def read_file(uploaded_file: st.runtime.uploaded_file_manager.UploadedFile) -> Optional[pd.DataFrame]:
        """
        Read uploaded file and convert to pandas DataFrame
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            pd.DataFrame or None if reading fails
            
        Raises:
            ValueError: If file format is not supported
            Exception: For other reading errors
        """
        if uploaded_file is None:
            return None
            
        try:
            file_extension = Path(uploaded_file.name).suffix.lower()
            
            # Read based on file type
            if file_extension in FileHandler.SUPPORTED_FORMATS['csv']:
                return FileHandler._read_csv(uploaded_file)
                
            elif file_extension in FileHandler.SUPPORTED_FORMATS['excel']:
                return FileHandler._read_excel(uploaded_file)
                
            elif file_extension in FileHandler.SUPPORTED_FORMATS['json']:
                return FileHandler._read_json(uploaded_file)
                
            else:
                raise ValueError(
                    f"Format de fichier non supporté: {file_extension}\n"
                    f"Formats acceptés: CSV, Excel (.xlsx, .xls), JSON"
                )
                
        except Exception as e:
            logger.error(f"Error reading file {uploaded_file.name}: {str(e)}")
            raise
    
    @staticmethod
    def _read_csv(uploaded_file) -> pd.DataFrame:
        """
        Read CSV file with multiple encoding attempts
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            pd.DataFrame
        """
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        
        for encoding in encodings:
            try:
                uploaded_file.seek(0)  # Reset file pointer
                df = pd.read_csv(uploaded_file, encoding=encoding)
                logger.info(f"CSV file read successfully with encoding: {encoding}")
                return df
            except UnicodeDecodeError:
                continue
            except Exception as e:
                if encoding == encodings[-1]:  # Last attempt
                    raise ValueError(f"Impossible de lire le fichier CSV: {str(e)}")
                continue
        
        raise ValueError("Impossible de détecter l'encodage du fichier CSV")
    
    @staticmethod
    def _read_excel(uploaded_file) -> pd.DataFrame:
        """
        Read Excel file
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            pd.DataFrame
        """
        try:
            uploaded_file.seek(0)
            df = pd.read_excel(uploaded_file, engine='openpyxl')
            logger.info(f"Excel file read successfully")
            return df
        except Exception as e:
            raise ValueError(f"Impossible de lire le fichier Excel: {str(e)}")
    
    @staticmethod
    def _read_json(uploaded_file) -> pd.DataFrame:
        """
        Read JSON file
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            pd.DataFrame
        """
        try:
            uploaded_file.seek(0)
            content = uploaded_file.read()
            
            # Try to parse JSON
            data = json.loads(content)
            
            # Convert to DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                # If it's a dict, try to convert to DataFrame
                # Assuming dict of lists or list of dicts
                df = pd.DataFrame(data)
            else:
                raise ValueError("Format JSON non reconnu")
                
            logger.info(f"JSON file read successfully")
            return df
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Fichier JSON invalide: {str(e)}")
        except Exception as e:
            raise ValueError(f"Impossible de lire le fichier JSON: {str(e)}")
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate DataFrame structure and content
        
        Args:
            df: pandas DataFrame to validate
            
        Returns:
            Dictionary with validation results
        """
        validation = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'info': {}
        }
        
        # Check if DataFrame is empty
        if df.empty:
            validation['valid'] = False
            validation['errors'].append("Le fichier est vide")
            return validation
        
        # Collect basic info
        validation['info'] = {
            'rows': len(df),
            'columns': len(df.columns),
            'memory_usage': df.memory_usage(deep=True).sum() / 1024**2,  # MB
            'dtypes': df.dtypes.value_counts().to_dict()
        }
        
        # Check for completely null columns
        null_columns = df.columns[df.isnull().all()].tolist()
        if null_columns:
            validation['warnings'].append(
                f"Colonnes entièrement vides: {', '.join(null_columns)}"
            )
        
        # Check for high null percentage
        null_pct = (df.isnull().sum() / len(df) * 100)
        high_null_cols = null_pct[null_pct > 50].index.tolist()
        if high_null_cols:
            validation['warnings'].append(
                f"Colonnes avec >50% de valeurs manquantes: {', '.join(high_null_cols)}"
            )
        
        # Check for duplicate rows
        dup_count = df.duplicated().sum()
        if dup_count > 0:
            validation['warnings'].append(
                f"{dup_count} lignes dupliquées détectées ({dup_count/len(df)*100:.1f}%)"
            )
        
        # Check memory usage
        if validation['info']['memory_usage'] > 100:  # > 100 MB
            validation['warnings'].append(
                f"Fichier volumineux: {validation['info']['memory_usage']:.1f} MB"
            )
        
        return validation
    
    @staticmethod
    def get_file_info(uploaded_file) -> Dict[str, Any]:
        """
        Extract file metadata
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            Dictionary with file information
        """
        return {
            'name': uploaded_file.name,
            'size': uploaded_file.size,
            'size_mb': uploaded_file.size / 1024**2,
            'type': uploaded_file.type,
            'extension': Path(uploaded_file.name).suffix.lower()
        }
