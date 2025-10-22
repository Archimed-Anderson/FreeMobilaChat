"""
Module de Classification Intelligente des Tweets Free
======================================================

Ce module implémente un système de classification multi-label pour les tweets
adressés à @Free, basé sur un modèle LLM fine-tuné.

Architecture:
    - Détection de réclamation (OUI/NON)
    - Classification thématique (FIBRE, MOBILE, TV, etc.)
    - Analyse de sentiment (NEGATIF, NEUTRE, POSITIF)
    - Niveau d'urgence (FAIBLE, MOYENNE, ELEVEE, CRITIQUE)
    - Type d'incident (PANNE, LENTEUR, FACTURATION, etc.)

Auteur: Archimed Anderson
Date: Octobre 2024
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
import pandas as pd
import numpy as np
from pathlib import Path

# Imports pour LLM
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# Logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ClassificationResult(BaseModel):
    """
    Résultat structuré de la classification d'un tweet.
    
    Attributes:
        is_reclamation: Indique si le tweet est une réclamation (OUI/NON)
        theme: Thématique principale (FIBRE, MOBILE, TV, FACTURE, SAV, RESEAU, AUTRE)
        sentiment: Sentiment exprimé (NEGATIF, NEUTRE, POSITIF)
        urgence: Niveau d'urgence (FAIBLE, MOYENNE, ELEVEE, CRITIQUE)
        type_incident: Type d'incident (PANNE, LENTEUR, FACTURATION, PROCESSUS_SAV, INFO, AUTRE)
        confidence: Score de confiance de la classification (0-1)
        justification: Explication textuelle de la classification
        tweet_id: Identifiant du tweet classifié
        timestamp: Horodatage de la classification
    """
    is_reclamation: str = Field(..., description="OUI ou NON")
    theme: str = Field(..., description="FIBRE, MOBILE, TV, FACTURE, SAV, RESEAU, AUTRE")
    sentiment: str = Field(..., description="NEGATIF, NEUTRE, POSITIF")
    urgence: str = Field(..., description="FAIBLE, MOYENNE, ELEVEE, CRITIQUE")
    type_incident: str = Field(..., description="PANNE, LENTEUR, FACTURATION, PROCESSUS_SAV, INFO, AUTRE")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Score de confiance")
    justification: str = Field(..., description="Explication de la classification")
    tweet_id: Optional[str] = Field(None, description="ID du tweet")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    @validator('is_reclamation')
    def validate_reclamation(cls, v):
        """Valide que is_reclamation est OUI ou NON"""
        if v not in ["OUI", "NON"]:
            raise ValueError(f"is_reclamation doit être 'OUI' ou 'NON', pas '{v}'")
        return v
    
    @validator('theme')
    def validate_theme(cls, v):
        """Valide le thème"""
        valid_themes = ["FIBRE", "MOBILE", "TV", "FACTURE", "SAV", "RESEAU", "AUTRE"]
        if v not in valid_themes:
            raise ValueError(f"theme doit être parmi {valid_themes}, pas '{v}'")
        return v
    
    @validator('sentiment')
    def validate_sentiment(cls, v):
        """Valide le sentiment"""
        valid_sentiments = ["NEGATIF", "NEUTRE", "POSITIF"]
        if v not in valid_sentiments:
            raise ValueError(f"sentiment doit être parmi {valid_sentiments}, pas '{v}'")
        return v
    
    @validator('urgence')
    def validate_urgence(cls, v):
        """Valide le niveau d'urgence"""
        valid_urgence = ["FAIBLE", "MOYENNE", "ELEVEE", "CRITIQUE"]
        if v not in valid_urgence:
            raise ValueError(f"urgence doit être parmi {valid_urgence}, pas '{v}'")
        return v
    
    @validator('type_incident')
    def validate_type_incident(cls, v):
        """Valide le type d'incident"""
        valid_types = ["PANNE", "LENTEUR", "FACTURATION", "PROCESSUS_SAV", "INFO", "AUTRE"]
        if v not in valid_types:
            raise ValueError(f"type_incident doit être parmi {valid_types}, pas '{v}'")
        return v


class TweetClassifier:
    """
    Classificateur de tweets basé sur LLM avec few-shot learning.
    
    Ce classificateur utilise un prompt engineering avancé avec des exemples
    few-shot pour guider le modèle LLM dans la classification multi-label
    des tweets Free.
    
    Attributes:
        model_name: Nom du modèle LLM à utiliser
        api_key: Clé API pour le service LLM
        temperature: Température pour la génération (0 = déterministe)
        max_tokens: Nombre maximum de tokens dans la réponse
    """
    
    # Exemples few-shot pour ancrage logique
    FEW_SHOT_EXAMPLES = [
        {
            "tweet": "📢 Free annonce le déploiement de la fibre dans 200 nouvelles communes ! #Free #Fibre",
            "classification": {
                "is_reclamation": "NON",
                "theme": "FIBRE",
                "sentiment": "POSITIF",
                "urgence": "FAIBLE",
                "type_incident": "INFO"
            },
            "justification": "Annonce officielle, aucun problème exprimé"
        },
        {
            "tweet": "@Free Ça fait 3h que la fibre est coupée à Lyon 3, c'est prévu pour quand la réparation ? #PanneFibre",
            "classification": {
                "is_reclamation": "OUI",
                "theme": "FIBRE",
                "sentiment": "NEGATIF",
                "urgence": "ELEVEE",
                "type_incident": "PANNE"
            },
            "justification": "Panne déclarée, durée précisée, demande de résolution urgente"
        },
        {
            "tweet": "@Free J'attends depuis 2 semaines une réponse du SAV pour ma box, toujours rien ! C'est une blague ?",
            "classification": {
                "is_reclamation": "OUI",
                "theme": "SAV",
                "sentiment": "NEGATIF",
                "urgence": "MOYENNE",
                "type_incident": "PROCESSUS_SAV"
            },
            "justification": "Insatisfaction envers le délai de traitement du service client"
        },
        {
            "tweet": "@Free Mon mobile Free a un débit 4G très lent depuis hier, c'est normal ?",
            "classification": {
                "is_reclamation": "OUI",
                "theme": "MOBILE",
                "sentiment": "NEGATIF",
                "urgence": "MOYENNE",
                "type_incident": "LENTEUR"
            },
            "justification": "Problème de performance réseau mobile signalé"
        },
        {
            "tweet": "@Free Ma facture de ce mois est anormalement élevée, pouvez-vous vérifier ?",
            "classification": {
                "is_reclamation": "OUI",
                "theme": "FACTURE",
                "sentiment": "NEGATIF",
                "urgence": "MOYENNE",
                "type_incident": "FACTURATION"
            },
            "justification": "Contestation de facturation, demande de vérification"
        }
    ]
    
    # Prompt système avec taxonomie détaillée
    SYSTEM_PROMPT = """Tu es un expert en analyse de tweets du service client Free.
Ta mission est de classifier chaque tweet selon une taxonomie multi-label précise.

# TAXONOMIE DE CLASSIFICATION

## 1. Détection Réclamation (is_reclamation)
- OUI : Le tweet exprime un problème, une insatisfaction ou demande une résolution
- NON : Tweet informatif, positif, ou simple question sans réclamation

## 2. Thématique Principale (theme)
- FIBRE : Connexion internet fibre optique
- MOBILE : Forfait mobile, réseau 4G/5G, téléphonie
- TV : Freebox TV, chaînes, décodeur
- FACTURE : Facturation, prix, prélèvements
- SAV : Service après-vente, support client
- RESEAU : Infrastructure réseau, couverture
- AUTRE : Autre thématique

## 3. Analyse Sentiment (sentiment)
- NEGATIF : Insatisfaction, colère, frustration
- NEUTRE : Question factuelle, demande d'information
- POSITIF : Satisfaction, remerciement, compliment

## 4. Niveau d'Urgence (urgence)
- FAIBLE : Information, question non urgente
- MOYENNE : Problème gênant mais pas bloquant
- ELEVEE : Problème impactant significativement le service
- CRITIQUE : Service totalement indisponible, impact majeur

## 5. Type d'Incident (type_incident)
- PANNE : Service totalement indisponible
- LENTEUR : Dégradation de performance
- FACTURATION : Problème de facturation ou paiement
- PROCESSUS_SAV : Problème avec le processus du service client
- INFO : Information ou annonce
- AUTRE : Autre type

# RÈGLES DE CLASSIFICATION

1. Un tweet peut être multi-thématique, mais tu dois identifier le thème PRINCIPAL
2. Pour is_reclamation=OUI, il faut une demande explicite ou implicite de résolution
3. L'urgence doit refléter l'impact réel du problème, pas seulement le ton
4. La justification doit être concise mais précise (1-2 phrases max)
5. Le score de confiance (confidence) doit refléter ta certitude :
   - 0.9-1.0 : Classification évidente
   - 0.7-0.9 : Classification probable
   - 0.5-0.7 : Classification incertaine (cas ambigu)
   - < 0.5 : Très incertain (à reviewer manuellement)

# FORMAT DE RÉPONSE

Tu dois TOUJOURS répondre en JSON valide strict avec cette structure :
{
    "is_reclamation": "OUI" ou "NON",
    "theme": "...",
    "sentiment": "...",
    "urgence": "...",
    "type_incident": "...",
    "confidence": 0.XX,
    "justification": "..."
}

AUCUN texte en dehors du JSON. Seulement le JSON brut."""
    
    def __init__(
        self,
        model_name: str = "gpt-4",
        api_key: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 300
    ):
        """
        Initialise le classificateur.
        
        Args:
            model_name: Nom du modèle (gpt-4, gpt-3.5-turbo, claude-3, etc.)
            api_key: Clé API pour le service LLM
            temperature: Température (0 = déterministe, 1 = créatif)
            max_tokens: Tokens max dans la réponse
        """
        self.model_name = model_name
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialiser le client LLM
        if model_name.lower() == "fallback":
            logger.warning("Mode fallback activé, utilisation des règles de classification")
            self.client = None
            self.provider = "fallback"
        elif "gpt" in model_name.lower():
            if not OPENAI_AVAILABLE:
                raise ImportError("openai package requis. Installez avec: pip install openai")
            self.client = openai.OpenAI(api_key=api_key)
            self.provider = "openai"
        elif "claude" in model_name.lower():
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("anthropic package requis. Installez avec: pip install anthropic")
            self.client = anthropic.Anthropic(api_key=api_key)
            self.provider = "anthropic"
        else:
            logger.warning(f"Modèle {model_name} non reconnu, utilisation mode fallback")
            self.client = None
            self.provider = "fallback"
        
        logger.info(f"TweetClassifier initialisé avec {model_name} (provider: {self.provider})")
    
    def _build_user_prompt(self, tweet: str) -> str:
        """
        Construit le prompt utilisateur avec few-shot examples.
        
        Args:
            tweet: Texte du tweet à classifier
            
        Returns:
            Prompt formaté avec exemples et tweet à classifier
        """
        prompt_parts = ["# EXEMPLES DE CLASSIFICATION\n"]
        
        # Ajouter les exemples few-shot
        for i, example in enumerate(self.FEW_SHOT_EXAMPLES, 1):
            prompt_parts.append(f"\n## Exemple {i}")
            prompt_parts.append(f"Tweet: {example['tweet']}")
            prompt_parts.append(f"Classification: {json.dumps(example['classification'], indent=2, ensure_ascii=False)}")
            prompt_parts.append(f"Justification: {example['justification']}\n")
        
        # Ajouter le tweet à classifier
        prompt_parts.append("\n# TWEET À CLASSIFIER\n")
        prompt_parts.append(f"Tweet: {tweet}")
        prompt_parts.append("\nClassification (JSON uniquement, pas de texte supplémentaire):")
        
        return "\n".join(prompt_parts)
    
    def _call_llm(self, tweet: str) -> Dict[str, Any]:
        """
        Appelle le LLM pour classifier le tweet.
        
        Args:
            tweet: Texte du tweet
            
        Returns:
            Réponse JSON du LLM parsée
            
        Raises:
            Exception: Si l'appel LLM échoue
        """
        user_prompt = self._build_user_prompt(tweet)
        
        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": self.SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    response_format={"type": "json_object"}  # Force JSON
                )
                content = response.choices[0].message.content
                
            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=self.SYSTEM_PROMPT,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ]
                )
                content = response.content[0].text
            
            else:
                # Fallback avec classification par règles
                return self._fallback_classification(tweet)
            
            # Parser le JSON
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError as e:
                logger.error(f"Erreur parsing JSON: {content[:200]}")
                # Tenter d'extraire le JSON du texte
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))
                raise
                
        except Exception as e:
            logger.error(f"Erreur appel LLM: {e}")
            # Fallback sur classification par règles
            return self._fallback_classification(tweet)
    
    def _fallback_classification(self, tweet: str) -> Dict[str, Any]:
        """
        Classification de fallback basée sur des règles simples.
        
        Utilisée si le LLM échoue ou n'est pas disponible.
        
        Args:
            tweet: Texte du tweet
            
        Returns:
            Classification basique par règles
        """
        tweet_lower = tweet.lower()
        
        # Détection réclamation (mots-clés négatifs)
        reclamation_keywords = ["problème", "panne", "coupé", "bug", "erreur", "nul", 
                                "lent", "ne fonctionne", "pas de", "toujours rien"]
        is_reclamation = any(kw in tweet_lower for kw in reclamation_keywords)
        
        # Thématique (premier match)
        theme = "AUTRE"
        if any(kw in tweet_lower for kw in ["fibre", "internet", "connexion", "box"]):
            theme = "FIBRE"
        elif any(kw in tweet_lower for kw in ["mobile", "4g", "5g", "forfait", "appel"]):
            theme = "MOBILE"
        elif any(kw in tweet_lower for kw in ["tv", "chaîne", "replay", "freebox tv"]):
            theme = "TV"
        elif any(kw in tweet_lower for kw in ["facture", "prix", "paiement", "prélèvement"]):
            theme = "FACTURE"
        elif any(kw in tweet_lower for kw in ["sav", "service client", "assistance"]):
            theme = "SAV"
        elif any(kw in tweet_lower for kw in ["réseau", "couverture", "antenne"]):
            theme = "RESEAU"
        
        # Sentiment
        sentiment = "NEUTRE"
        negative_words = ["nul", "mauvais", "problème", "bug", "colère", "marre"]
        positive_words = ["bien", "merci", "super", "excellent", "top"]
        if any(word in tweet_lower for word in negative_words):
            sentiment = "NEGATIF"
        elif any(word in tweet_lower for word in positive_words):
            sentiment = "POSITIF"
        
        # Urgence
        urgence = "FAIBLE"
        if any(kw in tweet_lower for kw in ["urgent", "critique", "coupé", "plus de"]):
            urgence = "ELEVEE" if is_reclamation else "MOYENNE"
        elif is_reclamation:
            urgence = "MOYENNE"
        
        # Type incident
        type_incident = "INFO"
        if "panne" in tweet_lower or "coupé" in tweet_lower:
            type_incident = "PANNE"
        elif "lent" in tweet_lower or "lenteur" in tweet_lower:
            type_incident = "LENTEUR"
        elif "facture" in tweet_lower or "prix" in tweet_lower:
            type_incident = "FACTURATION"
        elif "sav" in tweet_lower or "service" in tweet_lower:
            type_incident = "PROCESSUS_SAV"
        elif is_reclamation:
            type_incident = "AUTRE"
        
        return {
            "is_reclamation": "OUI" if is_reclamation else "NON",
            "theme": theme,
            "sentiment": sentiment,
            "urgence": urgence,
            "type_incident": type_incident,
            "confidence": 0.6,  # Confiance modérée pour fallback
            "justification": "Classification automatique par règles (fallback)"
        }
    
    def classify(self, tweet: str, tweet_id: Optional[str] = None) -> ClassificationResult:
        """
        Classifie un tweet unique.
        
        Args:
            tweet: Texte du tweet à classifier
            tweet_id: ID optionnel du tweet
            
        Returns:
            Résultat de classification structuré
            
        Raises:
            ValueError: Si la classification échoue
        """
        try:
            # Appeler le LLM
            raw_result = self._call_llm(tweet)
            
            # Créer l'objet ClassificationResult avec validation
            result = ClassificationResult(
                is_reclamation=raw_result["is_reclamation"],
                theme=raw_result["theme"],
                sentiment=raw_result["sentiment"],
                urgence=raw_result["urgence"],
                type_incident=raw_result["type_incident"],
                confidence=raw_result.get("confidence", 0.8),
                justification=raw_result.get("justification", "Classification automatique"),
                tweet_id=tweet_id
            )
            
            # Logger les classifications à faible confiance
            if result.confidence < 0.7:
                logger.warning(
                    f"Classification faible confiance ({result.confidence:.2f}) "
                    f"pour tweet: {tweet[:50]}..."
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur classification tweet: {e}")
            # En cas d'erreur totale, retourner un fallback
            fallback = self._fallback_classification(tweet)
            return ClassificationResult(
                tweet_id=tweet_id,
                **fallback
            )
    
    def batch_classify(
        self,
        tweets: List[str],
        tweet_ids: Optional[List[str]] = None
    ) -> List[ClassificationResult]:
        """
        Classifie un batch de tweets (optimisé pour performance).
        
        Args:
            tweets: Liste de tweets à classifier
            tweet_ids: Liste optionnelle d'IDs correspondants
            
        Returns:
            Liste de résultats de classification
        """
        if tweet_ids is None:
            tweet_ids = [None] * len(tweets)
        
        results = []
        total = len(tweets)
        
        logger.info(f"Début classification batch de {total} tweets")
        
        for i, (tweet, tweet_id) in enumerate(zip(tweets, tweet_ids), 1):
            try:
                result = self.classify(tweet, tweet_id)
                results.append(result)
                
                if i % 10 == 0:
                    logger.info(f"Progression: {i}/{total} tweets classifiés")
                    
            except Exception as e:
                logger.error(f"Erreur tweet {i}: {e}")
                # Ajouter un résultat de fallback
                fallback = self._fallback_classification(tweet)
                results.append(ClassificationResult(tweet_id=tweet_id, **fallback))
        
        logger.info(f"Classification batch terminée: {len(results)}/{total} réussis")
        return results
    
    def export_results(
        self,
        results: List[ClassificationResult],
        output_path: str,
        format: str = "json"
    ) -> None:
        """
        Exporte les résultats de classification.
        
        Args:
            results: Liste de résultats
            output_path: Chemin du fichier de sortie
            format: Format d'export (json, csv, excel)
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        if format == "json":
            data = [result.dict() for result in results]
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        elif format in ["csv", "excel"]:
            df = pd.DataFrame([result.dict() for result in results])
            if format == "csv":
                df.to_csv(output_path, index=False, encoding='utf-8')
            else:
                df.to_excel(output_path, index=False)
        
        else:
            raise ValueError(f"Format {format} non supporté. Utilisez json, csv ou excel")
        
        logger.info(f"Résultats exportés vers {output_path} (format: {format})")


# Fonction utilitaire pour usage simple
def classify_tweet(tweet: str, model_name: str = "gpt-4", api_key: Optional[str] = None) -> ClassificationResult:
    """
    Fonction utilitaire pour classifier un tweet rapidement.
    
    Args:
        tweet: Texte du tweet
        model_name: Nom du modèle LLM
        api_key: Clé API
        
    Returns:
        Résultat de classification
        
    Example:
        >>> result = classify_tweet("@Free Ma box ne fonctionne plus !")
        >>> print(result.is_reclamation)
        OUI
    """
    classifier = TweetClassifier(model_name=model_name, api_key=api_key)
    return classifier.classify(tweet)

