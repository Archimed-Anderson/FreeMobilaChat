"""
Configuration centralisée de l'application
Gestion des paramètres et constantes
"""

import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import streamlit as st

class Environment(Enum):
    """Environnements supportés"""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"

class UserRole(Enum):
    """Rôles utilisateur"""
    MANAGER = "manager"
    ANALYST = "analyst"
    AGENT = "agent"
    ADMIN = "admin"

@dataclass
class AppConfig:
    """Configuration principale de l'application"""
    
    # Application
    app_name: str = "FreeMobilaChat"
    app_version: str = "2.0.0"
    environment: Environment = Environment.DEVELOPMENT
    
    # Interface
    page_title: str = "FreeMobilaChat - Analyse KPI"
    page_icon: str = ""
    layout: str = "wide"
    initial_sidebar_state: str = "expanded"
    
    # API
    api_timeout: int = 60
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    supported_formats: List[str] = None
    
    # Upload
    chunk_size: int = 8192
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Analysis
    default_max_tweets: int = 500
    default_batch_size: int = 10
    default_llm_provider: str = "ollama"
    
    # UI
    theme_primary_color: str = "#1f77b4"
    theme_background_color: str = "#ffffff"
    theme_secondary_background_color: str = "#f0f2f6"
    theme_text_color: str = "#262730"
    
    def __post_init__(self):
        if self.supported_formats is None:
            self.supported_formats = ['.csv', '.xlsx', '.xls', '.json', '.parquet']

# Configuration globale
config = AppConfig()

# Configuration par environnement
ENVIRONMENT_CONFIGS = {
    Environment.DEVELOPMENT: {
        "debug": True,
        "log_level": "DEBUG",
        "api_timeout": 30,
        "max_file_size": 10 * 1024 * 1024,  # 10MB en dev
    },
    Environment.PRODUCTION: {
        "debug": False,
        "log_level": "INFO",
        "api_timeout": 60,
        "max_file_size": 100 * 1024 * 1024,  # 100MB en prod
    },
    Environment.TESTING: {
        "debug": True,
        "log_level": "DEBUG",
        "api_timeout": 10,
        "max_file_size": 1 * 1024 * 1024,  # 1MB en test
    }
}

def get_config() -> AppConfig:
    """Retourne la configuration actuelle"""
    return config

def update_config_from_env():
    """Met à jour la configuration depuis les variables d'environnement"""
    global config
    
    # Environnement
    env_str = os.getenv("STREAMLIT_ENV", "development")
    try:
        config.environment = Environment(env_str)
    except ValueError:
        config.environment = Environment.DEVELOPMENT
    
    # Appliquer la configuration d'environnement
    env_config = ENVIRONMENT_CONFIGS.get(config.environment, {})
    for key, value in env_config.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    # Variables d'environnement spécifiques
    config.api_timeout = int(os.getenv("API_TIMEOUT", config.api_timeout))
    config.max_file_size = int(os.getenv("MAX_FILE_SIZE", config.max_file_size))
    config.default_llm_provider = os.getenv("DEFAULT_LLM_PROVIDER", config.default_llm_provider)

def get_user_role() -> UserRole:
    """Retourne le rôle utilisateur actuel"""
    return st.session_state.get("user_role", UserRole.MANAGER)

def set_user_role(role: UserRole):
    """Définit le rôle utilisateur"""
    st.session_state.user_role = role

def get_current_batch_id() -> Optional[str]:
    """Retourne l'ID du batch actuel"""
    return st.session_state.get("current_batch_id")

def set_current_batch_id(batch_id: str):
    """Définit l'ID du batch actuel"""
    st.session_state.current_batch_id = batch_id

def clear_session():
    """Nettoie la session"""
    keys_to_clear = [
        "current_batch_id",
        "uploaded_data",
        "uploaded_filename",
        "analysis_status",
        "kpi_data",
        "tweets_data"
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

# Configuration des couleurs par rôle
ROLE_COLORS = {
    UserRole.MANAGER: {
        "primary": "#1f77b4",
        "secondary": "#ff7f0e",
        "accent": "#2ca02c"
    },
    UserRole.ANALYST: {
        "primary": "#d62728",
        "secondary": "#9467bd",
        "accent": "#8c564b"
    },
    UserRole.AGENT: {
        "primary": "#17becf",
        "secondary": "#bcbd22",
        "accent": "#e377c2"
    },
    UserRole.ADMIN: {
        "primary": "#2ca02c",
        "secondary": "#ff7f0e",
        "accent": "#d62728"
    }
}

def get_role_colors(role: UserRole) -> Dict[str, str]:
    """Retourne les couleurs pour un rôle"""
    return ROLE_COLORS.get(role, ROLE_COLORS[UserRole.MANAGER])

# Configuration des KPIs par rôle
ROLE_KPIS = {
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

def get_role_kpis(role: UserRole) -> List[str]:
    """Retourne les KPIs pour un rôle"""
    return ROLE_KPIS.get(role, ROLE_KPIS[UserRole.MANAGER])

# Initialisation
update_config_from_env()
