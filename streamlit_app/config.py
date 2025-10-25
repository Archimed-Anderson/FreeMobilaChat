"""
Configuration du Système de Classification LLM
==============================================

Configuration centralisée pour le système de classification LLM intelligent.
Contient tous les paramètres, constantes et configurations.

Développé dans le cadre d'un mémoire de master en Data Science
"""

import os
from pathlib import Path
from typing import Dict, List, Any

# Chemins de base
BASE_DIR = Path(__file__).parent
SERVICES_DIR = BASE_DIR / "services"
TESTS_DIR = BASE_DIR / "tests"
DATA_DIR = BASE_DIR.parent / "data"

# Configuration des LLM
LLM_CONFIG = {
    "ollama": {
        "model": "llama2",
        "temperature": 0.3,
        "max_tokens": 1000,
        "timeout": 30
    },
    "openai": {
        "model": "gpt-3.5-turbo",
        "temperature": 0.3,
        "max_tokens": 1000,
        "timeout": 30
    },
    "fallback": {
        "enabled": True,
        "confidence_threshold": 0.5
    }
}

# Taxonomie de classification
TAXONOMY = {
    "is_reclamation": ["OUI", "NON"],
    "theme": ["FIBRE", "MOBILE", "TV", "FACTURE", "SAV", "RESEAU", "AUTRE"],
    "sentiment": ["NEGATIF", "NEUTRE", "POSITIF"],
    "urgence": ["FAIBLE", "MOYENNE", "ELEVEE", "CRITIQUE"],
    "type_incident": ["PANNE", "LENTEUR", "FACTURATION", "PROCESSUS_SAV", "INFO", "AUTRE"]
}

# Patterns de détection pour le mode fallback
DETECTION_PATTERNS = {
    "reclamation_keywords": [
        "problème", "panne", "coupé", "lent", "bug", "erreur", "dysfonctionnement",
        "insatisfait", "mécontent", "déçu", "frustré", "énervé", "colère",
        "réclamation", "plainte", "insatisfaction", "défaillance"
    ],
    "theme_fibre": [
        "fibre", "internet", "débit", "connexion", "wifi", "box", "freebox",
        "ligne", "adsl", "vdsl", "fibre optique"
    ],
    "theme_mobile": [
        "mobile", "téléphone", "portable", "smartphone", "forfait", "data",
        "sms", "appel", "réseau mobile", "4g", "5g"
    ],
    "theme_tv": [
        "télévision", "tv", "chaîne", "canal", "programme", "replay",
        "streaming", "netflix", "prime", "disney"
    ],
    "theme_facture": [
        "facture", "facturation", "prix", "coût", "tarif", "abonnement",
        "paiement", "prélèvement", "montant"
    ],
    "theme_sav": [
        "sav", "service client", "support", "assistance", "aide",
        "technicien", "intervention", "rendez-vous"
    ],
    "theme_reseau": [
        "réseau", "infrastructure", "antenne", "couverture", "signal",
        "zone blanche", "déploiement"
    ],
    "sentiment_negatif": [
        "nul", "horrible", "catastrophe", "dégoûté", "énervé", "frustré",
        "déçu", "insatisfait", "mécontent", "colère", "rage"
    ],
    "sentiment_positif": [
        "super", "excellent", "génial", "parfait", "content", "satisfait",
        "ravi", "heureux", "merci", "bravo", "félicitations"
    ],
    "urgence_critique": [
        "urgence", "critique", "grave", "bloqué", "impossible", "catastrophe",
        "plus rien ne fonctionne", "totalement coupé"
    ],
    "urgence_elevee": [
        "depuis longtemps", "plusieurs heures", "toute la journée",
        "depuis ce matin", "depuis hier", "urgent"
    ],
    "type_panne": [
        "panne", "coupé", "ne fonctionne plus", "plus de service",
        "dysfonctionnement", "arrêt"
    ],
    "type_lenteur": [
        "lent", "lenteur", "débit faible", "ralentissement", "performance"
    ],
    "type_facturation": [
        "facture", "facturation", "prix", "coût", "tarif", "montant"
    ],
    "type_processus_sav": [
        "sav", "service client", "support", "assistance", "technicien"
    ]
}

# Configuration des types de données
DATA_TYPES = {
    "SOCIAL_MEDIA": {
        "keywords": ["tweet", "text", "message", "post"],
        "kpis": ["engagement", "sentiment", "reach"]
    },
    "ECOMMERCE": {
        "keywords": ["product", "price", "order", "customer"],
        "kpis": ["revenue", "conversion", "cart_abandonment"]
    },
    "FINANCIAL": {
        "keywords": ["amount", "balance", "transaction", "revenue"],
        "kpis": ["profit", "loss", "roi", "volatility"]
    },
    "IOT_SENSORS": {
        "keywords": ["sensor", "measurement", "value", "reading"],
        "kpis": ["data_quality", "sampling_rate", "anomalies"]
    },
    "TEMPORAL": {
        "keywords": ["date", "time", "timestamp", "hour"],
        "kpis": ["trends", "seasonality", "patterns"]
    }
}

# Configuration des métriques de performance
PERFORMANCE_METRICS = {
    "accuracy_threshold": 0.85,
    "confidence_threshold": 0.7,
    "processing_speed_threshold": 100,  # tweets/seconde
    "memory_limit_mb": 1000,
    "timeout_seconds": 30
}

# Configuration des tests
TEST_CONFIG = {
    "test_tweets": [
        "@Free Internet coupé depuis ce matin à Marseille, aidez-moi !",
        "📢 Free annonce le déploiement de la fibre dans 200 nouvelles communes !",
        "@Free J'attends depuis 2 semaines une réponse du SAV pour ma box, toujours rien !",
        "Merci @Free pour le service client rapide et efficace !",
        "La 4G de Free fonctionne parfaitement dans ma région"
    ],
    "benchmark_volumes": [10, 50, 100, 500],
    "expected_accuracy": 0.85,
    "expected_confidence": 0.8
}

# Configuration de l'interface Streamlit
STREAMLIT_CONFIG = {
    "page_title": "FreeMobilaChat - Classification LLM",
    "page_icon": ":brain:",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Configuration des couleurs
COLORS = {
    "primary": "#CC0000",
    "secondary": "#8B0000",
    "accent": "#FF6B6B",
    "success": "#28a745",
    "warning": "#ffc107",
    "danger": "#dc3545",
    "info": "#17a2b8"
}

# Configuration des logs
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "handlers": ["file", "console"]
}

# Configuration des exports
EXPORT_CONFIG = {
    "csv_encoding": "utf-8",
    "json_indent": 2,
    "date_format": "%Y%m%d_%H%M%S"
}

# Configuration des modèles
MODEL_CONFIG = {
    "batch_size": 100,
    "max_retries": 3,
    "retry_delay": 1,
    "cache_size": 1000
}

# Configuration des visualisations
VISUALIZATION_CONFIG = {
    "default_width": 800,
    "default_height": 600,
    "color_scheme": "Set3",
    "animation_duration": 500
}

def get_config() -> Dict[str, Any]:
    """Retourne la configuration complète"""
    return {
        "base_dir": str(BASE_DIR),
        "services_dir": str(SERVICES_DIR),
        "tests_dir": str(TESTS_DIR),
        "data_dir": str(DATA_DIR),
        "llm_config": LLM_CONFIG,
        "taxonomy": TAXONOMY,
        "patterns": DETECTION_PATTERNS,
        "data_types": DATA_TYPES,
        "performance": PERFORMANCE_METRICS,
        "tests": TEST_CONFIG,
        "streamlit": STREAMLIT_CONFIG,
        "colors": COLORS,
        "logging": LOGGING_CONFIG,
        "export": EXPORT_CONFIG,
        "model": MODEL_CONFIG,
        "visualization": VISUALIZATION_CONFIG
    }

def get_llm_config(provider: str = "fallback") -> Dict[str, Any]:
    """Retourne la configuration LLM pour un fournisseur"""
    return LLM_CONFIG.get(provider, LLM_CONFIG["fallback"])

def get_patterns(category: str) -> List[str]:
    """Retourne les patterns pour une catégorie"""
    return DETECTION_PATTERNS.get(category, [])

def get_data_type_config(data_type: str) -> Dict[str, Any]:
    """Retourne la configuration pour un type de données"""
    return DATA_TYPES.get(data_type, {})

def is_development_mode() -> bool:
    """Vérifie si on est en mode développement"""
    return os.getenv("ENVIRONMENT", "development") == "development"

def get_debug_mode() -> bool:
    """Vérifie si le mode debug est activé"""
    return os.getenv("DEBUG", "false").lower() == "true"

def get_log_level() -> str:
    """Retourne le niveau de log configuré"""
    return os.getenv("LOG_LEVEL", "INFO")

def get_llm_provider() -> str:
    """Retourne le fournisseur LLM configuré"""
    return os.getenv("LLM_PROVIDER", "fallback")

def get_llm_model() -> str:
    """Retourne le modèle LLM configuré"""
    provider = get_llm_provider()
    return os.getenv("LLM_MODEL", LLM_CONFIG[provider]["model"])

# Configuration par défaut
DEFAULT_CONFIG = get_config()

# Export des configurations principales
__all__ = [
    "BASE_DIR", "SERVICES_DIR", "TESTS_DIR", "DATA_DIR",
    "LLM_CONFIG", "TAXONOMY", "DETECTION_PATTERNS", "DATA_TYPES",
    "PERFORMANCE_METRICS", "TEST_CONFIG", "STREAMLIT_CONFIG",
    "COLORS", "LOGGING_CONFIG", "EXPORT_CONFIG", "MODEL_CONFIG",
    "VISUALIZATION_CONFIG", "get_config", "get_llm_config",
    "get_patterns", "get_data_type_config", "is_development_mode",
    "get_debug_mode", "get_log_level", "get_llm_provider", "get_llm_model"
]



