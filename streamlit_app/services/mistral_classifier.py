"""
Module de Classification Mistral - FreeMobilaChat
=================================================

Classification de tweets avec Mistral via Ollama (local).
Conforme aux spécifications techniques du projet.

Fonctionnalités:
- Classification par lots (batch processing)
- Retry logic (3 tentatives)
- Progress bar Streamlit
- Format JSON structuré
"""

from typing import List, Dict, Optional, Any
import pandas as pd
import json
import re
import time
import logging
import streamlit as st

logger = logging.getLogger(__name__)

# Configuration (conformes aux specs)
BATCH_SIZE = 50
MAX_RETRIES = 3
RETRY_DELAY = 2  # secondes

# Import conditionnel d'Ollama
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logger.warning("Module ollama non disponible. Installation requise: pip install ollama")


class MistralClassifier:
    """
    Classification de tweets avec Mistral via Ollama
    
    Cette classe implémente la classification par lots selon les
    spécifications techniques, avec gestion robuste des erreurs et
    retry logic.
    """
    
    def __init__(self, 
                 model_name: str = 'mistral',
                 batch_size: int = BATCH_SIZE,
                 temperature: float = 0.1,
                 max_retries: int = MAX_RETRIES):
        """
        Initialise le classificateur Mistral
        
        Args:
            model_name: Nom du modèle Ollama (mistral, llama2, etc.)
            batch_size: Nombre de tweets par lot
            temperature: Température du modèle (0.0-1.0)
            max_retries: Nombre de tentatives en cas d'échec
        """
        self.model_name = model_name
        self.batch_size = batch_size
        self.temperature = temperature
        self.max_retries = max_retries
        
        # Options Ollama (conformes aux specs)
        self.ollama_options = {
            'temperature': temperature,
            'num_predict': 2000,  # Tokens max pour réponse
            'top_p': 0.9          # Sampling
        }
        
        # Vérifier la disponibilité d'Ollama
        self._check_ollama_connection()
        
        logger.info(f"MistralClassifier initialisé: model={model_name}, batch_size={batch_size}")
    
    def _check_ollama_connection(self) -> bool:
        """
        Vérifie la connexion à Ollama
        
        Returns:
            True si Ollama est disponible et connecté
        """
        if not OLLAMA_AVAILABLE:
            logger.error("Module ollama non installé")
            return False
        
        try:
            # Tester la connexion
            ollama.list()
            logger.info("✅ Connexion Ollama OK")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur connexion Ollama: {e}")
            return False
    
    def build_classification_prompt(self, tweets: List[str]) -> str:
        """
        Construit le prompt de classification pour Mistral
        
        Format de sortie attendu (conforme aux specs):
        {
            "results": [
                {
                    "index": 0,
                    "sentiment": "positif|negatif|neutre",
                    "categorie": "produit|service|support|promotion|autre",
                    "score_confiance": 0.85
                }
            ]
        }
        
        Args:
            tweets: Liste de tweets à classifier
            
        Returns:
            Prompt formaté pour Mistral
        """
        # Construction de la liste des tweets avec indices
        tweets_text = ""
        for i, tweet in enumerate(tweets):
            tweets_text += f"{i}: {tweet}\n"
        
        prompt = f"""Tu es un expert en analyse de tweets pour Free Mobile (opérateur télécoms français).

Ta tâche: Classifier {len(tweets)} tweets selon ces critères:

**SENTIMENT:**
- positif: satisfaction, remerciements, compliments
- negatif: insatisfaction, plaintes, critiques
- neutre: questions, informations, demandes

**CATEGORIE:**
- produit: fibre, mobile, box, forfait, débit, qualité réseau
- service: SAV, support client, assistance, réponse
- support: aide technique, dépannage, installation
- promotion: offres, prix, réductions, nouveautés
- autre: autres sujets

**SCORE_CONFIANCE:** 0.0 à 1.0 selon la clarté du tweet

**TWEETS À CLASSIFIER:**
{tweets_text}

**IMPORTANT:** Réponds UNIQUEMENT avec un JSON valide (pas de texte avant/après) au format:
{{
    "results": [
        {{"index": 0, "sentiment": "positif", "categorie": "produit", "score_confiance": 0.95}},
        {{"index": 1, "sentiment": "negatif", "categorie": "service", "score_confiance": 0.88}},
        ...
    ]
}}

JSON:"""
        
        return prompt
    
    def classify_batch(self, tweets: List[str], retry: int = 0) -> List[Dict]:
        """
        Classifie un lot de tweets avec retry logic
        
        Gère les erreurs avec tentatives multiples (conformes aux specs: 3 tentatives)
        
        Args:
            tweets: Liste de tweets à classifier
            retry: Numéro de tentative actuelle
            
        Returns:
            Liste de dicts avec classifications
        """
        if not OLLAMA_AVAILABLE:
            logger.warning("Ollama non disponible, utilisation du fallback")
            return self._classify_batch_fallback(tweets)
        
        try:
            # Construire le prompt
            prompt = self.build_classification_prompt(tweets)
            
            # Appel à Ollama
            logger.info(f"Appel Ollama pour {len(tweets)} tweets (tentative {retry + 1}/{self.max_retries})")
            
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                options=self.ollama_options
            )
            
            # Extraction de la réponse
            response_text = response.get('response', '')
            
            # Parsing du JSON
            results = self._parse_ollama_response(response_text, len(tweets))
            
            if results:
                logger.info(f"✅ Classification réussie de {len(results)} tweets")
                return results
            else:
                raise ValueError("Réponse JSON invalide ou vide")
        
        except Exception as e:
            logger.error(f"❌ Erreur classification (tentative {retry + 1}): {e}")
            
            # Retry logic
            if retry < self.max_retries - 1:
                logger.info(f"Nouvelle tentative dans {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
                return self.classify_batch(tweets, retry + 1)
            else:
                logger.error(f"Échec après {self.max_retries} tentatives, fallback")
                return self._classify_batch_fallback(tweets)
    
    def _parse_ollama_response(self, response_text: str, expected_count: int) -> List[Dict]:
        """
        Parse la réponse JSON d'Ollama
        
        Args:
            response_text: Texte de réponse brut
            expected_count: Nombre de résultats attendus
            
        Returns:
            Liste de classifications ou None si erreur
        """
        try:
            # Extraire le JSON (parfois Ollama ajoute du texte avant/après)
            json_match = re.search(r'\{.*"results".*\}', response_text, re.DOTALL)
            
            if json_match:
                json_text = json_match.group(0)
                data = json.loads(json_text)
                
                if 'results' in data and isinstance(data['results'], list):
                    results = data['results']
                    
                    # Validation
                    if len(results) == expected_count:
                        return results
                    else:
                        logger.warning(f"Nombre de résultats incorrect: {len(results)} vs {expected_count}")
                        # Compléter ou tronquer si nécessaire
                        while len(results) < expected_count:
                            results.append({"index": len(results), "sentiment": "neutre", "categorie": "autre", "score_confiance": 0.5})
                        return results[:expected_count]
            
            return None
        
        except json.JSONDecodeError as e:
            logger.error(f"Erreur parsing JSON: {e}")
            return None
    
    def _classify_batch_fallback(self, tweets: List[str]) -> List[Dict]:
        """
        Classification fallback par règles si Ollama échoue
        
        Args:
            tweets: Liste de tweets
            
        Returns:
            Liste de classifications basiques
        """
        logger.info("Utilisation du classificateur fallback")
        
        results = []
        for i, tweet in enumerate(tweets):
            tweet_lower = tweet.lower()
            
            # Détection sentiment basique
            if any(w in tweet_lower for w in ['merci', 'super', 'génial', 'excellent', 'bravo']):
                sentiment = 'positif'
            elif any(w in tweet_lower for w in ['panne', 'nul', 'bug', 'problème', 'mauvais']):
                sentiment = 'negatif'
            else:
                sentiment = 'neutre'
            
            # Détection catégorie basique
            if any(w in tweet_lower for w in ['fibre', 'mobile', 'box', 'débit', '4g', '5g']):
                categorie = 'produit'
            elif any(w in tweet_lower for w in ['sav', 'service', 'support', 'assistance']):
                categorie = 'service'
            elif any(w in tweet_lower for w in ['aide', 'dépannage', 'installation', 'technicien']):
                categorie = 'support'
            elif any(w in tweet_lower for w in ['offre', 'promo', 'prix', 'réduction']):
                categorie = 'promotion'
            else:
                categorie = 'autre'
            
            # Confiance basée sur la clarté
            confidence = 0.75 if sentiment != 'neutre' or categorie != 'autre' else 0.50
            
            results.append({
                'index': i,
                'sentiment': sentiment,
                'categorie': categorie,
                'score_confiance': confidence
            })
        
        return results
    
    def classify_dataframe(self, 
                          df: pd.DataFrame, 
                          text_column: str = 'text_cleaned',
                          show_progress: bool = True) -> pd.DataFrame:
        """
        Classifie tous les tweets du DataFrame par lots avec progress bar
        
        Conforme aux specs: batch processing avec progress bar Streamlit
        
        Args:
            df: DataFrame avec tweets nettoyés
            text_column: Colonne à classifier
            show_progress: Afficher la progress bar Streamlit
            
        Returns:
            DataFrame enrichi avec sentiment, categorie, score_confiance
        """
        logger.info(f"Classification de {len(df)} tweets par lots de {self.batch_size}")
        
        if text_column not in df.columns:
            logger.error(f"Colonne '{text_column}' non trouvée")
            return df
        
        # Préparation
        tweets = df[text_column].tolist()
        total_batches = (len(tweets) + self.batch_size - 1) // self.batch_size
        all_results = []
        
        # Progress bar Streamlit
        if show_progress:
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        # Traitement par lots
        for batch_idx in range(total_batches):
            start_idx = batch_idx * self.batch_size
            end_idx = min(start_idx + self.batch_size, len(tweets))
            batch_tweets = tweets[start_idx:end_idx]
            
            # Mise à jour progress
            if show_progress:
                progress = (batch_idx + 1) / total_batches
                progress_bar.progress(progress)
                status_text.text(f"Classification: Lot {batch_idx + 1}/{total_batches} ({start_idx + 1}-{end_idx} tweets)")
            
            # Classification du lot
            batch_results = self.classify_batch(batch_tweets)
            all_results.extend(batch_results)
            
            # Petit délai entre les lots pour ne pas surcharger Ollama
            if batch_idx < total_batches - 1:
                time.sleep(0.5)
        
        # Nettoyage UI
        if show_progress:
            progress_bar.empty()
            status_text.empty()
        
        # Enrichissement du DataFrame
        df_classified = df.copy()
        
        # Ajout des colonnes de classification
        df_classified['sentiment'] = [r.get('sentiment', 'neutre') for r in all_results]
        df_classified['categorie'] = [r.get('categorie', 'autre') for r in all_results]
        df_classified['score_confiance'] = [r.get('score_confiance', 0.5) for r in all_results]
        
        # Ajout de métadonnées
        df_classified['classification_method'] = 'mistral'
        df_classified['model_name'] = self.model_name
        df_classified['classification_timestamp'] = pd.Timestamp.now().isoformat()
        
        logger.info(f"✅ Classification terminée: {len(df_classified)} tweets enrichis")
        
        return df_classified
    
    def get_classification_stats(self, df_classified: pd.DataFrame) -> Dict[str, Any]:
        """
        Calcule les statistiques de classification
        
        Args:
            df_classified: DataFrame avec classifications
            
        Returns:
            Dictionnaire de statistiques
        """
        if 'sentiment' not in df_classified.columns:
            return {}
        
        stats = {
            'total_classified': len(df_classified),
            'sentiment_distribution': df_classified['sentiment'].value_counts().to_dict(),
            'categorie_distribution': df_classified['categorie'].value_counts().to_dict() if 'categorie' in df_classified.columns else {},
            'avg_confidence': float(df_classified['score_confiance'].mean()) if 'score_confiance' in df_classified.columns else 0.0,
            'min_confidence': float(df_classified['score_confiance'].min()) if 'score_confiance' in df_classified.columns else 0.0,
            'max_confidence': float(df_classified['score_confiance'].max()) if 'score_confiance' in df_classified.columns else 0.0
        }
        
        return stats


# Fonctions utilitaires
def check_ollama_availability() -> bool:
    """
    Vérifie si Ollama est disponible et répond
    
    Returns:
        True si Ollama est accessible
    """
    if not OLLAMA_AVAILABLE:
        return False
    
    try:
        ollama.list()
        return True
    except:
        return False


def list_available_models() -> List[str]:
    """
    Liste les modèles Ollama disponibles
    
    Returns:
        Liste des noms de modèles
    """
    if not OLLAMA_AVAILABLE:
        return []
    
    try:
        models_response = ollama.list()
        if 'models' in models_response:
            return [model['name'] for model in models_response['models']]
        return []
    except:
        return []


def classify_single_tweet(tweet: str, model_name: str = 'mistral') -> Dict[str, Any]:
    """
    Classifie un tweet unique avec Mistral
    
    Args:
        tweet: Texte du tweet
        model_name: Nom du modèle Ollama
        
    Returns:
        Dictionnaire avec classification
    """
    classifier = MistralClassifier(model_name=model_name, batch_size=1)
    results = classifier.classify_batch([tweet])
    return results[0] if results else {
        'index': 0,
        'sentiment': 'neutre',
        'categorie': 'autre',
        'score_confiance': 0.5
    }

