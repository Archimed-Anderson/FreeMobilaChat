"""
Main Analysis Module
Entry point for automated data analysis
"""

import pandas as pd
from typing import Dict, Any, Optional
import streamlit as st
import logging
from ..utils.file_handler import FileHandler
from .data_classifier import DataClassifier
from .metric_selector import MetricSelector
from .insight_generator import InsightGenerator

logger = logging.getLogger(__name__)


@st.cache_data(show_spinner=False)
def analyze_document(uploaded_file: st.runtime.uploaded_file_manager.UploadedFile) -> Optional[Dict[str, Any]]:
    """
    Perform comprehensive analysis on uploaded file
    
    This is the main entry point for automated data analysis.
    Handles file reading, classification, profiling, and insight generation.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        Dictionary containing:
        - file_info: File metadata
        - dataframe: Processed DataFrame
        - classification: Data classification results
        - metrics: Recommended metrics and visualizations
        - insights: Generated insights
        - summary: Textual summary
        
    Raises:
        ValueError: If file format is unsupported
        Exception: For other processing errors
    """
    if uploaded_file is None:
        return None
    
    try:
        logger.info(f"Starting analysis of file: {uploaded_file.name}")
        
        # Step 1: Read file
        with st.spinner("📖 Lecture du fichier..."):
            df = FileHandler.read_file(uploaded_file)
            file_info = FileHandler.get_file_info(uploaded_file)
            file_validation = FileHandler.validate_dataframe(df)
        
        if not file_validation['valid']:
            st.error("❌ Fichier invalide")
            for error in file_validation['errors']:
                st.error(f"  - {error}")
            return None
        
        # Display warnings if any
        if file_validation['warnings']:
            for warning in file_validation['warnings']:
                st.warning(f"⚠️ {warning}")
        
        logger.info(f"File read successfully: {len(df)} rows, {len(df.columns)} columns")
        
        # Step 2: Classify data
        with st.spinner("🔍 Classification des données..."):
            classifier = DataClassifier(df)
            classification_results = classifier.classify()
        
        logger.info("Classification completed")
        
        # Step 3: Select metrics
        with st.spinner("📊 Sélection des métriques..."):
            metric_selector = MetricSelector(
                classification_results['column_types'],
                classification_results['column_stats']
            )
            metric_recommendations = metric_selector.select_metrics()
            priority_visualizations = metric_selector.get_priority_visualizations(max_charts=10)
        
        logger.info(f"Metrics selected: {len(priority_visualizations)} priority visualizations")
        
        # Step 4: Generate insights
        with st.spinner("💡 Génération des insights..."):
            insight_generator = InsightGenerator(df, classification_results)
            insights = insight_generator.generate_insights()
            summary = insight_generator.get_summary()
        
        logger.info(f"Generated {len(insights)} insights")
        
        # Compile results
        results = {
            'file_info': file_info,
            'file_validation': file_validation,
            'dataframe': df,
            'classification': classification_results,
            'metric_recommendations': metric_recommendations,
            'priority_visualizations': priority_visualizations,
            'insights': insights,
            'summary': summary
        }
        
        logger.info("Analysis completed successfully")
        
        return results
        
    except ValueError as e:
        st.error(f"❌ Erreur de validation: {str(e)}")
        logger.error(f"Validation error: {str(e)}")
        return None
        
    except Exception as e:
        st.error(f"❌ Erreur lors de l'analyse: {str(e)}")
        logger.error(f"Analysis error: {str(e)}", exc_info=True)
        return None
