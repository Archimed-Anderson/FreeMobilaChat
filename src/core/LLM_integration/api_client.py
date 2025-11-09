"""
Client API pour intégration LLM
Support multi-providers avec gestion d'erreurs et retry
"""

import asyncio
import os
import time
from typing import Optional, Dict, Any, List
from enum import Enum
import httpx


class LLMProvider(str, Enum):
    """Providers LLM supportés"""
    OPENAI = "openai"
    MISTRAL = "mistral"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


class LLMAPIClient:
    """
    Client API unifié pour différents providers LLM
    Gestion des timeouts, retry et rate limiting
    """
    
    def __init__(self,
                 provider: str = "openai",
                 api_key: Optional[str] = None,
                 base_url: Optional[str] = None,
                 timeout: float = 5.0,
                 max_retries: int = 3):
        """
        Initialise le client API
        
        Args:
            provider: Provider LLM ('openai', 'mistral', 'anthropic', 'ollama')
            api_key: Clé API (optionnelle pour Ollama local)
            base_url: URL de base (pour Ollama ou endpoints custom)
            timeout: Timeout en secondes
            max_retries: Nombre maximum de tentatives
        """
        self.provider = LLMProvider(provider)
        self.api_key = api_key or os.getenv(f"{provider.upper()}_API_KEY")
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Configuration des URLs de base
        self.base_urls = {
            LLMProvider.OPENAI: "https://api.openai.com/v1",
            LLMProvider.MISTRAL: "https://api.mistral.ai/v1",
            LLMProvider.ANTHROPIC: "https://api.anthropic.com/v1",
            LLMProvider.OLLAMA: base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        }
        
        self.base_url = self.base_urls[self.provider]
        
        # Statistiques d'appels
        self.stats = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'total_duration': 0.0,
            'average_duration': 0.0
        }
    
    async def call_api(self, 
                       prompt: str,
                       system_prompt: Optional[str] = None,
                       temperature: float = 0.3,
                       max_tokens: int = 300) -> Optional[Dict[str, Any]]:
        """
        Appel générique à l'API LLM
        
        Args:
            prompt: Prompt utilisateur
            system_prompt: Prompt système (optionnel)
            temperature: Température de génération (0-1)
            max_tokens: Nombre maximum de tokens
            
        Returns:
            Réponse de l'API ou None en cas d'erreur
        """
        start_time = time.time()
        self.stats['total_calls'] += 1
        
        try:
            # Construire les headers
            headers = self._build_headers()
            
            # Construire le payload
            payload = self._build_payload(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Faire l'appel avec retry
            response = await self._call_with_retry(headers, payload)
            
            # Enregistrer les statistiques
            duration = time.time() - start_time
            self.stats['successful_calls'] += 1
            self.stats['total_duration'] += duration
            self.stats['average_duration'] = \
                self.stats['total_duration'] / self.stats['successful_calls']
            
            return response
            
        except Exception as e:
            self.stats['failed_calls'] += 1
            raise RuntimeError(f"Erreur API {self.provider}: {str(e)}")
    
    def _build_headers(self) -> Dict[str, str]:
        """Construit les headers HTTP selon le provider"""
        headers = {"Content-Type": "application/json"}
        
        if self.provider == LLMProvider.OPENAI:
            headers["Authorization"] = f"Bearer {self.api_key}"
        elif self.provider == LLMProvider.MISTRAL:
            headers["Authorization"] = f"Bearer {self.api_key}"
        elif self.provider == LLMProvider.ANTHROPIC:
            headers["x-api-key"] = self.api_key
            headers["anthropic-version"] = "2023-06-01"
        elif self.provider == LLMProvider.OLLAMA:
            # Ollama local n'a pas besoin d'API key par défaut
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
        
        return headers
    
    def _build_payload(self,
                       prompt: str,
                       system_prompt: Optional[str],
                       temperature: float,
                       max_tokens: int) -> Dict[str, Any]:
        """Construit le payload JSON selon le provider"""
        
        # Messages pour OpenAI/Mistral/Ollama
        if self.provider in [LLMProvider.OPENAI, LLMProvider.MISTRAL, LLMProvider.OLLAMA]:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self._get_model(),
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        
        # Format Anthropic
        elif self.provider == LLMProvider.ANTHROPIC:
            payload = {
                "model": self._get_model(),
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}]
            }
            if system_prompt:
                payload["system"] = system_prompt
        
        return payload
    
    def _get_model(self) -> str:
        """Retourne le modèle par défaut pour le provider"""
        default_models = {
            LLMProvider.OPENAI: "gpt-4o-mini",
            LLMProvider.MISTRAL: "mistral-small-latest",
            LLMProvider.ANTHROPIC: "claude-3-haiku-20240307",
            LLMProvider.OLLAMA: "llama3.1:8b"
        }
        
        # Vérifier les variables d'environnement
        env_key = f"{self.provider.value.upper()}_MODEL"
        return os.getenv(env_key, default_models[self.provider])
    
    async def _call_with_retry(self,
                               headers: Dict[str, str],
                               payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Effectue l'appel API avec retry automatique
        
        Args:
            headers: Headers HTTP
            payload: Payload JSON
            
        Returns:
            Réponse parsée
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    # Endpoint selon le provider
                    endpoint = self._get_endpoint()
                    url = f"{self.base_url}{endpoint}"
                    
                    response = await client.post(
                        url,
                        headers=headers,
                        json=payload
                    )
                    
                    response.raise_for_status()
                    
                    # Parser la réponse
                    return self._parse_response(response.json())
                    
            except httpx.TimeoutException:
                last_error = f"Timeout après {self.timeout}s"
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Backoff exponentiel
            except httpx.HTTPStatusError as e:
                last_error = f"HTTP {e.response.status_code}: {e.response.text}"
                if e.response.status_code >= 500 and attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    break
            except Exception as e:
                last_error = str(e)
                break
        
        raise RuntimeError(f"Échec après {self.max_retries} tentatives: {last_error}")
    
    def _get_endpoint(self) -> str:
        """Retourne l'endpoint API selon le provider"""
        endpoints = {
            LLMProvider.OPENAI: "/chat/completions",
            LLMProvider.MISTRAL: "/chat/completions",
            LLMProvider.ANTHROPIC: "/messages",
            LLMProvider.OLLAMA: "/v1/chat/completions"
        }
        return endpoints[self.provider]
    
    def _parse_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse la réponse selon le format du provider
        
        Args:
            response_data: Données JSON de la réponse
            
        Returns:
            Réponse standardisée
        """
        if self.provider in [LLMProvider.OPENAI, LLMProvider.MISTRAL, LLMProvider.OLLAMA]:
            content = response_data['choices'][0]['message']['content']
        elif self.provider == LLMProvider.ANTHROPIC:
            content = response_data['content'][0]['text']
        else:
            content = ""
        
        return {
            'content': content.strip(),
            'raw_response': response_data
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques d'appels"""
        return self.stats.copy()
    
    def reset_stats(self) -> None:
        """Réinitialise les statistiques"""
        self.stats = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'total_duration': 0.0,
            'average_duration': 0.0
        }
    
    async def test_connection(self) -> bool:
        """
        Test la connexion à l'API
        
        Returns:
            True si la connexion fonctionne
        """
        try:
            response = await self.call_api(
                prompt="Test de connexion",
                system_prompt="Réponds simplement 'OK'",
                max_tokens=10
            )
            return response is not None
        except Exception:
            return False

