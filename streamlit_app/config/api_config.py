"""
Configuration API centralisée avec gestion robuste des connexions
Gestion des fallbacks et retry automatique
"""

import os
import time
import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import streamlit as st

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIType(Enum):
    """Types d'API supportés"""
    BACKEND = "backend"
    OLLAMA = "ollama"
    MISTRAL = "mistral"
    OPENAI = "openai"

@dataclass
class APIConfig:
    """Configuration d'une API"""
    name: str
    base_urls: List[str]
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    health_endpoint: str = "/health"
    api_type: APIType = APIType.BACKEND

class RobustAPIClient:
    """
    Client API robuste avec fallback automatique et retry
    """
    
    def __init__(self):
        self.configs = self._load_api_configs()
        self.session = self._create_session()
        self._current_config = None
        
    def _load_api_configs(self) -> Dict[str, APIConfig]:
        """Charge les configurations API avec fallbacks"""
        return {
            "backend": APIConfig(
                name="Backend API",
                base_urls=[
                    "http://127.0.0.1:8000",
                    "http://localhost:8000",
                    "http://0.0.0.0:8000"
                ],
                timeout=60,  # Timeout plus long pour uploads
                max_retries=3,
                health_endpoint="/health",
                api_type=APIType.BACKEND
            ),
            "ollama": APIConfig(
                name="Ollama API",
                base_urls=[
                    "http://127.0.0.1:11434",
                    "http://localhost:11434"
                ],
                timeout=30,
                max_retries=2,
                health_endpoint="/api/tags",
                api_type=APIType.OLLAMA
            )
        }
    
    def _create_session(self) -> requests.Session:
        """Crée une session avec retry automatique"""
        session = requests.Session()
        
        # Configuration retry
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _test_connection(self, config: APIConfig) -> Optional[str]:
        """Teste la connexion à une URL"""
        for url in config.base_urls:
            try:
                full_url = f"{url}{config.health_endpoint}"
                logger.info(f"Testing connection to: {full_url}")
                
                response = self.session.get(
                    full_url, 
                    timeout=config.timeout,
                    headers={'User-Agent': 'FreeMobilaChat/1.0'}
                )
                
                if response.status_code == 200:
                    logger.info(f" Connection successful to: {url}")
                    return url
                else:
                    logger.warning(f" Health check failed: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f" Connection failed to {url}: {str(e)}")
                continue
        
        return None
    
    def get_working_url(self, api_name: str = "backend") -> Optional[str]:
        """Trouve une URL fonctionnelle pour l'API"""
        if api_name not in self.configs:
            logger.error(f"API {api_name} not configured")
            return None
        
        config = self.configs[api_name]
        
        # Vérifier le cache de session
        cache_key = f"api_url_{api_name}"
        if cache_key in st.session_state:
            cached_url = st.session_state[cache_key]
            if self._test_connection(config):
                return cached_url
        
        # Tester toutes les URLs
        working_url = self._test_connection(config)
        if working_url:
            st.session_state[cache_key] = working_url
            self._current_config = config
            return working_url
        
        logger.error(f" No working URL found for {api_name}")
        return None
    
    def make_request(self, 
                    method: str, 
                    endpoint: str, 
                    api_name: str = "backend",
                    **kwargs) -> Optional[requests.Response]:
        """Fait une requête avec fallback automatique"""
        
        working_url = self.get_working_url(api_name)
        if not working_url:
            logger.error(f"No working URL for {api_name}")
            return None
        
        full_url = f"{working_url}{endpoint}"
        
        try:
            logger.info(f"Making {method} request to: {full_url}")
            
            # Headers par défaut
            headers = kwargs.get('headers', {})
            headers.update({
                'User-Agent': 'FreeMobilaChat/1.0',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            })
            kwargs['headers'] = headers
            
            # Timeout par défaut
            if 'timeout' not in kwargs:
                config = self.configs[api_name]
                kwargs['timeout'] = config.timeout
            
            response = self.session.request(method, full_url, **kwargs)
            
            # Log de la réponse
            logger.info(f"Response: {response.status_code}")
            
            return response
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout on {full_url}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error on {full_url}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error on {full_url}: {str(e)}")
            return None
    
    def upload_file(self, file_data: bytes, filename: str, 
                   analysis_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Upload un fichier avec gestion robuste"""
        
        # Préparer les données
        files = {"file": (filename, file_data, "text/csv")}
        data = {
            "llm_provider": analysis_config.get("llm_provider", "ollama"),
            "max_tweets": analysis_config.get("max_tweets", 500),
            "batch_size": analysis_config.get("batch_size", 10),
            "user_role": analysis_config.get("user_role", "manager")
        }
        
        response = self.make_request(
            "POST",
            "/upload-csv",
            files=files,
            data=data
        )
        
        if response and response.status_code == 200:
            return response.json()
        
        return None
    
    def get_analysis_status(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Récupère le statut d'analyse"""
        response = self.make_request("GET", f"/analysis-status/{batch_id}")
        
        if response and response.status_code == 200:
            return response.json()
        
        return None
    
    def get_kpis(self, batch_id: str, user_role: str = "manager") -> Optional[Dict[str, Any]]:
        """Récupère les KPIs"""
        response = self.make_request(
            "GET", 
            f"/kpis/{batch_id}",
            params={"user_role": user_role}
        )
        
        if response and response.status_code == 200:
            return response.json()
        
        return None
    
    def get_tweets(self, batch_id: str, filters: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Récupère les tweets avec filtres"""
        params = {"limit": 1000, "offset": 0}
        if filters:
            params.update({k: v for k, v in filters.items() if v is not None and v != False})
        
        response = self.make_request(
            "GET",
            f"/tweets/{batch_id}",
            params=params
        )
        
        if response and response.status_code == 200:
            return response.json()
        
        return None

# Instance globale
api_client = RobustAPIClient()

def get_api_client() -> RobustAPIClient:
    """Retourne l'instance du client API"""
    return api_client

def test_all_connections() -> Dict[str, bool]:
    """Teste toutes les connexions API"""
    results = {}
    
    for api_name in api_client.configs.keys():
        working_url = api_client.get_working_url(api_name)
        results[api_name] = working_url is not None
        
        if working_url:
            logger.info(f" {api_name}: {working_url}")
        else:
            logger.error(f" {api_name}: No working connection")
    
    return results
