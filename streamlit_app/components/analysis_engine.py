"""
Moteur d'analyse des données
Gestion de l'analyse et calcul des KPIs
"""

import streamlit as st
import pandas as pd
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import time

from ..config.settings import get_config, get_user_role, UserRole
from ..config.api_config import get_api_client
from ..services.data_processor import get_data_processor
from ..services.kpi_calculator import get_kpi_calculator
from ..utils.helpers import get_current_timestamp, format_number

logger = logging.getLogger(__name__)

class AnalysisEngine:
    """Moteur d'analyse des données avec gestion des KPIs"""
    
    def __init__(self):
        self.config = get_config()
        self.api_client = get_api_client()
        self.data_processor = get_data_processor()
        self.kpi_calculator = get_kpi_calculator()
        
    def start_analysis(self, data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Lance l'analyse des données"""
        
        try:
            logger.info(f"Démarrage de l'analyse de {len(data)} tweets")
            
            # Préparation des données
            prepared_data = self.data_processor.prepare_for_analysis(
                data, 
                config.get("max_tweets", 500)
            )
            
            # Génération de l'ID de batch
            batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Sauvegarde en session
            st.session_state.current_batch_id = batch_id
            st.session_state.analysis_config = config
            st.session_state.analysis_start_time = get_current_timestamp()
            
            # Simulation de l'analyse (en attendant l'API)
            analysis_result = self._simulate_analysis(prepared_data, config)
            
            # Calcul des KPIs
            kpis = self.kpi_calculator.calculate_kpis(prepared_data, config)
            
            # Sauvegarde des résultats
            st.session_state.analysis_result = analysis_result
            st.session_state.kpi_data = kpis
            st.session_state.analysis_status = "completed"
            
            logger.info("Analyse terminée avec succès")
            
            return {
                "batch_id": batch_id,
                "status": "completed",
                "kpis": kpis,
                "analysis_result": analysis_result,
                "timestamp": get_current_timestamp()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse: {str(e)}")
            st.session_state.analysis_status = "error"
            st.session_state.analysis_error = str(e)
            raise
    
    def _simulate_analysis(self, data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Simule l'analyse des données (en attendant l'API)"""
        
        # Simulation des résultats d'analyse
        analysis_result = {
            "total_tweets": len(data),
            "analyzed_tweets": len(data),
            "sentiment_distribution": {
                "positive": 0.4,
                "negative": 0.3,
                "neutral": 0.3
            },
            "category_distribution": {
                "complaint": 0.35,
                "question": 0.25,
                "praise": 0.20,
                "suggestion": 0.20
            },
            "priority_distribution": {
                "high": 0.15,
                "medium": 0.45,
                "low": 0.40
            },
            "keywords": [
                "service", "client", "problème", "satisfaction", "aide"
            ],
            "response_time": "2.5 heures",
            "cost_analysis": {
                "total_cost": 15.50,
                "cost_per_tweet": 0.03
            }
        }
        
        return analysis_result
    
    def get_analysis_status(self, batch_id: str) -> Dict[str, Any]:
        """Récupère le statut de l'analyse"""
        
        if batch_id not in st.session_state:
            return {"status": "not_found", "error": "Batch ID non trouvé"}
        
        status = st.session_state.get("analysis_status", "pending")
        
        if status == "completed":
            return {
                "status": "completed",
                "kpis": st.session_state.get("kpi_data", {}),
                "analysis_result": st.session_state.get("analysis_result", {}),
                "timestamp": st.session_state.get("analysis_start_time")
            }
        elif status == "error":
            return {
                "status": "error",
                "error": st.session_state.get("analysis_error", "Erreur inconnue")
            }
        else:
            return {"status": "pending", "progress": 0.5}
    
    def get_kpis(self, batch_id: str, user_role: UserRole = None) -> Dict[str, Any]:
        """Récupère les KPIs pour un batch"""
        
        if user_role is None:
            user_role = get_user_role()
        
        kpi_data = st.session_state.get("kpi_data", {})
        
        if not kpi_data:
            return {"error": "Aucune donnée KPI disponible"}
        
        # Filtrage des KPIs selon le rôle
        role_kpis = self._filter_kpis_by_role(kpi_data, user_role)
        
        return role_kpis
    
    def _filter_kpis_by_role(self, kpi_data: Dict[str, Any], user_role: UserRole) -> Dict[str, Any]:
        """Filtre les KPIs selon le rôle utilisateur"""
        
        # Configuration des KPIs par rôle
        role_kpi_config = {
            UserRole.MANAGER: [
                "total_tweets", "analyzed_tweets", "success_rate",
                "sentiment_distribution", "priority_distribution",
                "response_time", "cost_analysis"
            ],
            UserRole.ANALYST: [
                "sentiment_analysis", "category_breakdown", "trend_analysis",
                "keyword_extraction", "temporal_patterns", "correlation_analysis"
            ],
            UserRole.AGENT: [
                "urgent_tweets", "response_needed", "sentiment_alerts",
                "category_priorities", "response_suggestions"
            ],
            UserRole.ADMIN: [
                "system_health", "user_activity", "performance_metrics",
                "error_logs", "usage_statistics"
            ]
        }
        
        allowed_kpis = role_kpi_config.get(user_role, role_kpi_config[UserRole.MANAGER])
        
        # Filtrage des KPIs
        filtered_kpis = {}
        for kpi_name in allowed_kpis:
            if kpi_name in kpi_data:
                filtered_kpis[kpi_name] = kpi_data[kpi_name]
        
        return filtered_kpis
    
    def get_tweets(self, batch_id: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Récupère les tweets avec filtres"""
        
        # Récupération des données depuis la session
        data = st.session_state.get("uploaded_data")
        
        if data is None:
            return {"error": "Aucune donnée disponible"}
        
        # Application des filtres
        filtered_data = data.copy()
        
        if filters:
            # Filtre par sentiment
            if filters.get("sentiment"):
                # Simulation du filtrage par sentiment
                sentiment = filters["sentiment"]
                if sentiment == "positive":
                    filtered_data = filtered_data.sample(frac=0.4)
                elif sentiment == "negative":
                    filtered_data = filtered_data.sample(frac=0.3)
                elif sentiment == "neutral":
                    filtered_data = filtered_data.sample(frac=0.3)
            
            # Filtre par catégorie
            if filters.get("category"):
                # Simulation du filtrage par catégorie
                category = filters["category"]
                if category == "complaint":
                    filtered_data = filtered_data.sample(frac=0.35)
                elif category == "question":
                    filtered_data = filtered_data.sample(frac=0.25)
                elif category == "praise":
                    filtered_data = filtered_data.sample(frac=0.20)
                elif category == "suggestion":
                    filtered_data = filtered_data.sample(frac=0.20)
            
            # Filtre par priorité
            if filters.get("priority"):
                # Simulation du filtrage par priorité
                priority = filters["priority"]
                if priority == "high":
                    filtered_data = filtered_data.sample(frac=0.15)
                elif priority == "medium":
                    filtered_data = filtered_data.sample(frac=0.45)
                elif priority == "low":
                    filtered_data = filtered_data.sample(frac=0.40)
        
        # Limitation du nombre de résultats
        limit = filters.get("limit", 100) if filters else 100
        filtered_data = filtered_data.head(limit)
        
        return {
            "tweets": filtered_data.to_dict("records"),
            "total_count": len(filtered_data),
            "filters_applied": filters
        }
    
    def export_results(self, batch_id: str, format: str = "json") -> Dict[str, Any]:
        """Exporte les résultats d'analyse"""
        
        try:
            # Récupération des données
            kpi_data = st.session_state.get("kpi_data", {})
            analysis_result = st.session_state.get("analysis_result", {})
            tweets_data = st.session_state.get("uploaded_data")
            
            if not kpi_data and not analysis_result:
                return {"error": "Aucun résultat à exporter"}
            
            # Préparation des données d'export
            export_data = {
                "batch_id": batch_id,
                "export_timestamp": get_current_timestamp(),
                "kpis": kpi_data,
                "analysis_result": analysis_result,
                "tweets_count": len(tweets_data) if tweets_data is not None else 0
            }
            
            # Export selon le format
            if format == "json":
                import json
                return {
                    "data": json.dumps(export_data, indent=2, ensure_ascii=False),
                    "filename": f"analysis_results_{batch_id}.json",
                    "mime_type": "application/json"
                }
            elif format == "csv":
                # Export des KPIs en CSV
                if kpi_data:
                    df = pd.DataFrame([kpi_data])
                    csv_data = df.to_csv(index=False)
                    return {
                        "data": csv_data,
                        "filename": f"kpis_{batch_id}.csv",
                        "mime_type": "text/csv"
                    }
            
            return {"error": f"Format d'export non supporté: {format}"}
            
        except Exception as e:
            logger.error(f"Erreur lors de l'export: {str(e)}")
            return {"error": str(e)}

# Instance globale
analysis_engine = AnalysisEngine()

def get_analysis_engine() -> AnalysisEngine:
    """Retourne l'instance du moteur d'analyse"""
    return analysis_engine
