"""
Configuration des providers LLM pour l'analyse adaptative
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class LLMProviderConfig:
    """Configuration d'un provider LLM"""
    name: str
    model: str
    api_key_env: str
    base_url: Optional[str] = None
    temperature: float = 0.1
    max_tokens: int = 4000
    timeout: int = 60
    enabled: bool = True

class LLMConfigManager:
    """Gestionnaire de configuration des providers LLM"""
    
    def __init__(self):
        self.providers = self._initialize_providers()
        self.default_provider = "openai"
    
    def _initialize_providers(self) -> Dict[str, LLMProviderConfig]:
        """Initialise les configurations des providers"""
        return {
            "openai": LLMProviderConfig(
                name="OpenAI",
                model="gpt-4-turbo-preview",
                api_key_env="OPENAI_API_KEY",
                temperature=0.1,
                max_tokens=4000,
                timeout=60,
                enabled=self._check_api_key("OPENAI_API_KEY")
            ),
            "anthropic": LLMProviderConfig(
                name="Anthropic Claude",
                model="claude-3-sonnet-20240229",
                api_key_env="ANTHROPIC_API_KEY",
                temperature=0.1,
                max_tokens=4000,
                timeout=60,
                enabled=self._check_api_key("ANTHROPIC_API_KEY")
            ),
            "local": LLMProviderConfig(
                name="Local Ollama",
                model="llama2-13b-chat",
                api_key_env="",
                base_url="http://localhost:11434",
                temperature=0.1,
                max_tokens=4000,
                timeout=120,
                enabled=self._check_local_ollama()
            ),
            "azure_openai": LLMProviderConfig(
                name="Azure OpenAI",
                model="gpt-4-turbo",
                api_key_env="AZURE_OPENAI_API_KEY",
                base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
                temperature=0.1,
                max_tokens=4000,
                timeout=60,
                enabled=self._check_api_key("AZURE_OPENAI_API_KEY")
            )
        }
    
    def _check_api_key(self, env_var: str) -> bool:
        """Vérifie si une clé API est disponible"""
        return os.getenv(env_var) is not None
    
    def _check_local_ollama(self) -> bool:
        """Vérifie si Ollama local est disponible"""
        try:
            import httpx
            response = httpx.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_available_providers(self) -> Dict[str, LLMProviderConfig]:
        """Retourne les providers disponibles"""
        return {name: config for name, config in self.providers.items() if config.enabled}
    
    def get_provider_config(self, provider_name: str) -> Optional[LLMProviderConfig]:
        """Retourne la configuration d'un provider"""
        return self.providers.get(provider_name)
    
    def get_default_provider(self) -> str:
        """Retourne le provider par défaut"""
        available = self.get_available_providers()
        if available:
            return list(available.keys())[0]
        return self.default_provider
    
    def get_fallback_chain(self) -> list:
        """Retourne la chaîne de fallback des providers"""
        available = self.get_available_providers()
        fallback_chain = []
        
        # Priorité des providers
        priority_order = ["openai", "anthropic", "azure_openai", "local"]
        
        for provider in priority_order:
            if provider in available:
                fallback_chain.append(provider)
        
        return fallback_chain
    
    def validate_provider(self, provider_name: str) -> bool:
        """Valide qu'un provider est configuré et disponible"""
        config = self.get_provider_config(provider_name)
        if not config:
            return False
        
        if not config.enabled:
            return False
        
        # Vérification spécifique selon le provider
        if provider_name == "local":
            return self._check_local_ollama()
        else:
            return self._check_api_key(config.api_key_env)
    
    def get_provider_credentials(self, provider_name: str) -> Dict[str, Any]:
        """Retourne les credentials d'un provider"""
        config = self.get_provider_config(provider_name)
        if not config:
            return {}
        
        credentials = {
            "model": config.model,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "timeout": config.timeout
        }
        
        if config.api_key_env:
            credentials["api_key"] = os.getenv(config.api_key_env)
        
        if config.base_url:
            credentials["base_url"] = config.base_url
        
        return credentials

# Instance globale du gestionnaire de configuration
llm_config_manager = LLMConfigManager()

# Configuration des prompts par domaine
DOMAIN_PROMPT_TEMPLATES = {
    "finance": {
        "focus": "Analyse financière et performance",
        "metrics": ["ROI", "marges", "coûts", "revenus", "profitabilité"],
        "visualizations": ["line_chart", "bar_chart", "heatmap", "candlestick"]
    },
    "ecommerce": {
        "focus": "Analyse e-commerce et ventes",
        "metrics": ["CA", "panier moyen", "conversion", "retention", "LTV"],
        "visualizations": ["sales_timeline", "category_performance", "customer_segmentation"]
    },
    "marketing": {
        "focus": "Analyse marketing et campagnes",
        "metrics": ["CTR", "conversion", "CAC", "ROAS", "engagement"],
        "visualizations": ["funnel", "cohort_analysis", "attribution_chart"]
    },
    "hr": {
        "focus": "Analyse RH et personnel",
        "metrics": ["turnover", "satisfaction", "performance", "diversité"],
        "visualizations": ["demographics_pie", "performance_scatter", "tenure_histogram"]
    },
    "ventes": {
        "focus": "Analyse commerciale et ventes",
        "metrics": ["quotas", "performance", "territoires", "produits"],
        "visualizations": ["sales_performance", "territory_analysis", "product_ranking"]
    },
    "logistique": {
        "focus": "Analyse logistique et supply chain",
        "metrics": ["stock", "livraisons", "coûts", "efficacité"],
        "visualizations": ["inventory_trends", "delivery_performance", "cost_analysis"]
    },
    "santé": {
        "focus": "Analyse médicale et soins",
        "metrics": ["patients", "traitements", "qualité", "coûts"],
        "visualizations": ["patient_flow", "outcomes", "resource_utilization"]
    },
    "éducation": {
        "focus": "Analyse éducative et apprentissage",
        "metrics": ["performance", "engagement", "progression", "satisfaction"],
        "visualizations": ["student_performance", "course_analytics", "progress_tracking"]
    }
}

# Configuration des visualisations par type de données
VISUALIZATION_RULES = {
    "temporal_data": {
        "required_columns": 1,
        "chart_types": ["line_chart", "area_chart", "bar_chart"],
        "description": "Données temporelles nécessitant des graphiques chronologiques"
    },
    "categorical_data": {
        "required_columns": 1,
        "chart_types": ["bar_chart", "pie_chart", "donut_chart"],
        "description": "Données catégorielles nécessitant des graphiques de distribution"
    },
    "numerical_data": {
        "required_columns": 1,
        "chart_types": ["histogram", "box_plot", "violin_plot"],
        "description": "Données numériques nécessitant des graphiques de distribution"
    },
    "correlation_data": {
        "required_columns": 2,
        "chart_types": ["scatter_plot", "heatmap", "correlation_matrix"],
        "description": "Données corrélées nécessitant des graphiques de relation"
    },
    "geographical_data": {
        "required_columns": 1,
        "chart_types": ["map", "choropleth", "scatter_mapbox"],
        "description": "Données géographiques nécessitant des cartes"
    }
}

# Configuration des métriques de qualité des données
DATA_QUALITY_THRESHOLDS = {
    "completeness": {
        "excellent": 0.95,
        "good": 0.85,
        "acceptable": 0.70,
        "poor": 0.50
    },
    "consistency": {
        "excellent": 0.95,
        "good": 0.85,
        "acceptable": 0.70,
        "poor": 0.50
    },
    "accuracy": {
        "excellent": 0.95,
        "good": 0.85,
        "acceptable": 0.70,
        "poor": 0.50
    },
    "timeliness": {
        "excellent": 0.95,
        "good": 0.85,
        "acceptable": 0.70,
        "poor": 0.50
    }
}

# Configuration des seuils de confiance pour l'analyse
CONFIDENCE_THRESHOLDS = {
    "high_confidence": 0.8,
    "medium_confidence": 0.6,
    "low_confidence": 0.4,
    "insufficient_data": 0.2
}

def get_llm_config() -> LLMConfigManager:
    """Retourne l'instance du gestionnaire de configuration LLM"""
    return llm_config_manager

def get_domain_config(domain: str) -> Dict[str, Any]:
    """Retourne la configuration d'un domaine"""
    return DOMAIN_PROMPT_TEMPLATES.get(domain.lower(), DOMAIN_PROMPT_TEMPLATES["general"])

def get_visualization_rules(data_type: str) -> Dict[str, Any]:
    """Retourne les règles de visualisation pour un type de données"""
    return VISUALIZATION_RULES.get(data_type, VISUALIZATION_RULES["numerical_data"])

def get_quality_thresholds() -> Dict[str, Dict[str, float]]:
    """Retourne les seuils de qualité des données"""
    return DATA_QUALITY_THRESHOLDS

def get_confidence_thresholds() -> Dict[str, float]:
    """Retourne les seuils de confiance"""
    return CONFIDENCE_THRESHOLDS
