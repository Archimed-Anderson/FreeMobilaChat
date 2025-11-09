"""
Gestionnaire de réponses LLM
Parsing, validation et traitement des réponses LLM
"""

import json
import re
from typing import Dict, Any, Optional, List
from enum import Enum


class ResponseValidationError(Exception):
    """Exception pour les erreurs de validation de réponse"""
    pass


class ResponseHandler:
    """
    Gestionnaire de réponses LLM
    Parse et valide les réponses JSON des LLMs
    """
    
    def __init__(self):
        """Initialise le gestionnaire de réponses"""
        # Schéma attendu pour les réponses d'analyse de sentiment
        self.expected_schema = {
            'sentiment': ['positive', 'neutral', 'negative'],
            'sentiment_score': (float, -1.0, 1.0),
            'category': [
                'facturation', 'réseau', 'technique', 'abonnement',
                'réclamation', 'compliment', 'question', 'autre'
            ],
            'priority': ['critique', 'haute', 'moyenne', 'basse'],
            'keywords': list,
            'is_urgent': bool,
            'needs_response': bool,
            'estimated_resolution_time': (int, type(None))
        }
    
    def parse_llm_response(self, raw_response: str) -> Optional[Dict[str, Any]]:
        """
        Parse une réponse LLM (potentiellement avec markdown)
        
        Args:
            raw_response: Réponse brute du LLM
            
        Returns:
            Dictionnaire parsé ou None si échec
            
        Examples:
            >>> handler = ResponseHandler()
            >>> response = '```json\\n{"sentiment": "positive"}\\n```'
            >>> handler.parse_llm_response(response)
            {'sentiment': 'positive'}
        """
        if not raw_response or not isinstance(raw_response, str):
            return None
        
        # Nettoyer la réponse
        cleaned = self._clean_response(raw_response)
        
        # Tenter de parser le JSON
        try:
            parsed = json.loads(cleaned)
            return parsed
        except json.JSONDecodeError:
            # Tenter d'extraire le JSON d'un texte
            return self._extract_json_from_text(cleaned)
    
    def _clean_response(self, response: str) -> str:
        """
        Nettoie une réponse LLM des marqueurs markdown
        
        Args:
            response: Réponse brute
            
        Returns:
            Réponse nettoyée
        """
        # Supprimer les blocs markdown
        response = re.sub(r'```json\s*', '', response)
        response = re.sub(r'```\s*', '', response)
        
        # Supprimer les espaces superflus
        response = response.strip()
        
        return response
    
    def _extract_json_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extrait un objet JSON d'un texte
        
        Args:
            text: Texte contenant potentiellement du JSON
            
        Returns:
            Dictionnaire parsé ou None
        """
        # Chercher un objet JSON dans le texte
        json_pattern = r'\{[^{}]*\}'
        matches = re.finditer(json_pattern, text, re.DOTALL)
        
        for match in matches:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                continue
        
        return None
    
    def validate_response(self, response: Dict[str, Any]) -> bool:
        """
        Valide qu'une réponse respecte le schéma attendu
        
        Args:
            response: Réponse à valider
            
        Returns:
            True si valide
            
        Raises:
            ResponseValidationError: Si la validation échoue
        """
        if not response or not isinstance(response, dict):
            raise ResponseValidationError("Réponse vide ou invalide")
        
        # Vérifier chaque champ du schéma
        for field, expected_type in self.expected_schema.items():
            # Vérifier la présence du champ
            if field not in response:
                raise ResponseValidationError(f"Champ manquant: {field}")
            
            value = response[field]
            
            # Valider selon le type
            if isinstance(expected_type, list):
                # Le champ doit être dans la liste de valeurs
                if value not in expected_type:
                    raise ResponseValidationError(
                        f"Valeur invalide pour {field}: {value}. "
                        f"Attendu: {expected_type}"
                    )
            
            elif isinstance(expected_type, tuple):
                # Type avec contraintes
                if len(expected_type) == 2:
                    # Type nullable
                    valid_type, none_type = expected_type
                    if value is not None and not isinstance(value, valid_type):
                        raise ResponseValidationError(
                            f"Type invalide pour {field}: {type(value).__name__}. "
                            f"Attendu: {valid_type.__name__} ou None"
                        )
                elif len(expected_type) == 3:
                    # Type avec range (min, max)
                    valid_type, min_val, max_val = expected_type
                    if not isinstance(value, valid_type):
                        raise ResponseValidationError(
                            f"Type invalide pour {field}: {type(value).__name__}. "
                            f"Attendu: {valid_type.__name__}"
                        )
                    if not (min_val <= value <= max_val):
                        raise ResponseValidationError(
                            f"Valeur hors limites pour {field}: {value}. "
                            f"Attendu: [{min_val}, {max_val}]"
                        )
            
            elif expected_type == list:
                # Le champ doit être une liste
                if not isinstance(value, list):
                    raise ResponseValidationError(
                        f"Type invalide pour {field}: {type(value).__name__}. "
                        f"Attendu: list"
                    )
            
            elif expected_type == bool:
                # Le champ doit être un booléen
                if not isinstance(value, bool):
                    raise ResponseValidationError(
                        f"Type invalide pour {field}: {type(value).__name__}. "
                        f"Attendu: bool"
                    )
        
        return True
    
    def handle_empty_response(self) -> Dict[str, Any]:
        """
        Génère une réponse par défaut pour les réponses vides
        
        Returns:
            Dictionnaire avec valeurs par défaut
        """
        return {
            'sentiment': 'neutral',
            'sentiment_score': 0.0,
            'category': 'autre',
            'priority': 'moyenne',
            'keywords': [],
            'is_urgent': False,
            'needs_response': True,
            'estimated_resolution_time': None,
            '_is_default': True
        }
    
    def process_response(self, 
                        raw_response: str,
                        allow_defaults: bool = True) -> Dict[str, Any]:
        """
        Traitement complet d'une réponse LLM
        
        Args:
            raw_response: Réponse brute du LLM
            allow_defaults: Autoriser les valeurs par défaut si parsing échoue
            
        Returns:
            Réponse parsée et validée
            
        Raises:
            ResponseValidationError: Si validation échoue et defaults non autorisés
        """
        # Vérifier si la réponse est vide
        if not raw_response or raw_response.strip() == "":
            if allow_defaults:
                return self.handle_empty_response()
            else:
                raise ResponseValidationError("Réponse vide du LLM")
        
        # Parser la réponse
        parsed = self.parse_llm_response(raw_response)
        
        if parsed is None:
            if allow_defaults:
                return self.handle_empty_response()
            else:
                raise ResponseValidationError("Impossible de parser la réponse")
        
        # Valider la réponse
        try:
            self.validate_response(parsed)
            return parsed
        except ResponseValidationError as e:
            if allow_defaults:
                # Log l'erreur et retourner les defaults
                return self.handle_empty_response()
            else:
                raise
    
    def batch_process_responses(self, 
                                raw_responses: List[str]) -> List[Dict[str, Any]]:
        """
        Traite plusieurs réponses en batch
        
        Args:
            raw_responses: Liste de réponses brutes
            
        Returns:
            Liste de réponses traitées
        """
        return [
            self.process_response(response, allow_defaults=True)
            for response in raw_responses
        ]
    
    def get_validation_report(self, 
                             responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Génère un rapport de validation pour un batch de réponses
        
        Args:
            responses: Liste de réponses à analyser
            
        Returns:
            Rapport avec statistiques
        """
        total = len(responses)
        defaults = sum(1 for r in responses if r.get('_is_default', False))
        valid = total - defaults
        
        return {
            'total_responses': total,
            'valid_responses': valid,
            'default_responses': defaults,
            'success_rate': (valid / total * 100) if total > 0 else 0.0
        }

