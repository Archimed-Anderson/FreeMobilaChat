"""
Module de Classification de Tweets Free Mobile
==============================================

Module principal pour la classification automatique des tweets selon la taxonomie définie:
- is_reclamation: OUI/NON
- theme: FIBRE | MOBILE | TV | FACTURE | SAV | RESEAU | AUTRE
- sentiment: NEGATIF | NEUTRE | POSITIF
- urgence: FAIBLE | MOYENNE | ELEVEE | CRITIQUE
- type_incident: PANNE | LENTEUR | FACTURATION | PROCESSUS_SAV | INFO | AUTRE

Développé dans le cadre d'un mémoire de master en Data Science
"""

import json
import logging
import re
from typing import Dict, List, Optional, Union
from datetime import datetime
import pandas as pd
import numpy as np

# Imports conditionnels pour LLM
try:
    from langchain.llms import Ollama
    from langchain.prompts import PromptTemplate
    from langchain.chains import LLMChain
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Configuration du logger
logger = logging.getLogger(__name__)

class ClassificationResult:
    """Résultat structuré de la classification d'un tweet"""
    
    def __init__(self, 
                 is_reclamation: str,
                 theme: str,
                 sentiment: str,
                 urgence: str,
                 type_incident: str,
                 confidence: float,
                 justification: str):
        self.is_reclamation = is_reclamation
        self.theme = theme
        self.sentiment = sentiment
        self.urgence = urgence
        self.type_incident = type_incident
        self.confidence = confidence
        self.justification = justification
    
    def to_dict(self) -> Dict[str, Union[str, float]]:
        """Convertit le résultat en dictionnaire"""
        return {
            'is_reclamation': self.is_reclamation,
            'theme': self.theme,
            'sentiment': self.sentiment,
            'urgence': self.urgence,
            'type_incident': self.type_incident,
            'confidence': self.confidence,
            'justification': self.justification
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convertit le résultat en JSON"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

class TweetClassifier:
    """Classificateur de tweets Free Mobile avec IA"""
    
    def __init__(self, model_path: Optional[str] = None, llm_provider: str = "fallback"):
        """
        Initialise le classificateur
        
        Args:
            model_path: Chemin vers le modèle fine-tuné (optionnel)
            llm_provider: Fournisseur LLM ("ollama", "openai", "fallback")
        """
        self.model_path = model_path
        self.llm_provider = llm_provider
        self.llm = None
        self.chain = None
        
        # Initialisation du LLM si disponible
        self._initialize_llm()
        
        # Patterns de détection pour le fallback
        self._initialize_patterns()
    
    def _initialize_llm(self):
        """Initialise le LLM selon le fournisseur choisi"""
        try:
            if self.llm_provider == "ollama" and LANGCHAIN_AVAILABLE:
                self.llm = Ollama(model="llama2", temperature=0.3)
                template = PromptTemplate(
                    input_variables=["tweet"],
                    template=self._get_classification_prompt()
                )
                self.chain = LLMChain(llm=self.llm, prompt=template)
                logger.info("LLM Ollama initialisé avec succès")
                
            elif self.llm_provider == "openai" and OPENAI_AVAILABLE:
                self.llm = openai.OpenAI()
                logger.info("LLM OpenAI initialisé avec succès")
                
            else:
                logger.info("Mode fallback activé - classification par règles")
                
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du LLM: {e}")
            self.llm_provider = "fallback"
    
    def _initialize_patterns(self):
        """Initialise les patterns de détection pour le mode fallback"""
        self.patterns = {
            'reclamation_keywords': [
                'problème', 'panne', 'coupé', 'lent', 'bug', 'erreur', 'dysfonctionnement',
                'insatisfait', 'mécontent', 'déçu', 'frustré', 'énervé', 'colère',
                'réclamation', 'plainte', 'insatisfaction', 'défaillance'
            ],
            'theme_fibre': [
                'fibre', 'internet', 'débit', 'connexion', 'wifi', 'box', 'freebox',
                'ligne', 'adsl', 'vdsl', 'fibre optique'
            ],
            'theme_mobile': [
                'mobile', 'téléphone', 'portable', 'smartphone', 'forfait', 'data',
                'sms', 'appel', 'réseau mobile', '4g', '5g'
            ],
            'theme_tv': [
                'télévision', 'tv', 'chaîne', 'canal', 'programme', 'replay',
                'streaming', 'netflix', 'prime', 'disney'
            ],
            'theme_facture': [
                'facture', 'facturation', 'prix', 'coût', 'tarif', 'abonnement',
                'paiement', 'prélèvement', 'montant'
            ],
            'theme_sav': [
                'sav', 'service client', 'support', 'assistance', 'aide',
                'technicien', 'intervention', 'rendez-vous'
            ],
            'theme_reseau': [
                'réseau', 'infrastructure', 'antenne', 'couverture', 'signal',
                'zone blanche', 'déploiement'
            ],
            'sentiment_negatif': [
                'nul', 'horrible', 'catastrophe', 'dégoûté', 'énervé', 'frustré',
                'déçu', 'insatisfait', 'mécontent', 'colère', 'rage'
            ],
            'sentiment_positif': [
                'super', 'excellent', 'génial', 'parfait', 'content', 'satisfait',
                'ravi', 'heureux', 'merci', 'bravo', 'félicitations'
            ],
            'urgence_critique': [
                'urgence', 'critique', 'grave', 'bloqué', 'impossible', 'catastrophe',
                'plus rien ne fonctionne', 'totalement coupé'
            ],
            'urgence_elevee': [
                'depuis longtemps', 'plusieurs heures', 'toute la journée',
                'depuis ce matin', 'depuis hier', 'urgent'
            ],
            'type_panne': [
                'panne', 'coupé', 'ne fonctionne plus', 'plus de service',
                'dysfonctionnement', 'arrêt'
            ],
            'type_lenteur': [
                'lent', 'lenteur', 'débit faible', 'ralentissement', 'performance'
            ],
            'type_facturation': [
                'facture', 'facturation', 'prix', 'coût', 'tarif', 'montant'
            ],
            'type_processus_sav': [
                'sav', 'service client', 'support', 'assistance', 'technicien'
            ]
        }
    
    def _get_classification_prompt(self) -> str:
        """Retourne le prompt de classification pour le LLM"""
        return """
        Vous êtes un expert en analyse de tweets Free Mobile. Analysez le tweet suivant et classifiez-le selon cette taxonomie:

        RÉCLAMATION: OUI si le tweet exprime un problème, une insatisfaction ou demande une résolution. NON sinon.

        THÈME: FIBRE | MOBILE | TV | FACTURE | SAV | RESEAU | AUTRE

        SENTIMENT: NEGATIF | NEUTRE | POSITIF

        URGENCE: FAIBLE | MOYENNE | ELEVEE | CRITIQUE

        TYPE_INCIDENT: PANNE | LENTEUR | FACTURATION | PROCESSUS_SAV | INFO | AUTRE

        Répondez UNIQUEMENT en JSON avec cette structure exacte:
        {{
            "is_reclamation": "OUI/NON",
            "theme": "FIBRE/MOBILE/TV/FACTURE/SAV/RESEAU/AUTRE",
            "sentiment": "NEGATIF/NEUTRE/POSITIF",
            "urgence": "FAIBLE/MOYENNE/ELEVEE/CRITIQUE",
            "type_incident": "PANNE/LENTEUR/FACTURATION/PROCESSUS_SAV/INFO/AUTRE",
            "confidence": 0.95,
            "justification": "Explication courte de la classification"
        }}

        Tweet à analyser: {tweet}
        """
    
    def classify(self, tweet: str) -> ClassificationResult:
        """
        Classifie un tweet selon la taxonomie définie
        
        Args:
            tweet: Texte du tweet à classifier
            
        Returns:
            ClassificationResult: Résultat de la classification
        """
        try:
            if self.llm_provider in ["ollama", "openai"] and self.llm:
                return self._classify_with_llm(tweet)
            else:
                return self._classify_with_fallback(tweet)
        except Exception as e:
            logger.error(f"Erreur lors de la classification: {e}")
            return self._get_default_classification(tweet)
    
    def _classify_with_llm(self, tweet: str) -> ClassificationResult:
        """Classification avec LLM (Ollama ou OpenAI)"""
        try:
            if self.llm_provider == "ollama" and self.chain:
                result = self.chain.run(tweet=tweet)
            elif self.llm_provider == "openai" and self.llm:
                response = self.llm.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Vous êtes un expert en analyse de tweets Free Mobile."},
                        {"role": "user", "content": self._get_classification_prompt().format(tweet=tweet)}
                    ],
                    temperature=0.3,
                    max_tokens=500
                )
                result = response.choices[0].message.content
            else:
                raise Exception("LLM non disponible")
            
            # Parse du résultat JSON
            result_dict = json.loads(result)
            
            return ClassificationResult(
                is_reclamation=result_dict.get('is_reclamation', 'NON'),
                theme=result_dict.get('theme', 'AUTRE'),
                sentiment=result_dict.get('sentiment', 'NEUTRE'),
                urgence=result_dict.get('urgence', 'FAIBLE'),
                type_incident=result_dict.get('type_incident', 'AUTRE'),
                confidence=float(result_dict.get('confidence', 0.8)),
                justification=result_dict.get('justification', 'Classification par LLM')
            )
            
        except Exception as e:
            logger.error(f"Erreur LLM: {e}")
            return self._classify_with_fallback(tweet)
    
    def _classify_with_fallback(self, tweet: str) -> ClassificationResult:
        """Classification par règles (mode fallback)"""
        tweet_lower = tweet.lower()
        
        # Détection réclamation
        is_reclamation = self._detect_reclamation(tweet_lower)
        
        # Détection thème
        theme = self._detect_theme(tweet_lower)
        
        # Détection sentiment
        sentiment = self._detect_sentiment(tweet_lower)
        
        # Détection urgence
        urgence = self._detect_urgence(tweet_lower)
        
        # Détection type d'incident
        type_incident = self._detect_type_incident(tweet_lower, theme)
        
        # Calcul de la confiance
        confidence = self._calculate_confidence(tweet_lower, is_reclamation, theme, sentiment)
        
        # Justification
        justification = self._generate_justification(is_reclamation, theme, sentiment, urgence)
        
        return ClassificationResult(
            is_reclamation=is_reclamation,
            theme=theme,
            sentiment=sentiment,
            urgence=urgence,
            type_incident=type_incident,
            confidence=confidence,
            justification=justification
        )
    
    def _detect_reclamation(self, tweet_lower: str) -> str:
        """Détecte si c'est une réclamation"""
        reclamation_score = sum(1 for keyword in self.patterns['reclamation_keywords'] 
                               if keyword in tweet_lower)
        
        # Patterns spécifiques de réclamation
        reclamation_patterns = [
            r'@free.*problème', r'@free.*panne', r'@free.*bug',
            r'pourquoi.*ne.*fonctionne', r'quand.*sera.*réparé',
            r'ça.*fait.*[0-9]+.*heures', r'depuis.*ce.*matin'
        ]
        
        pattern_matches = sum(1 for pattern in reclamation_patterns 
                             if re.search(pattern, tweet_lower))
        
        if reclamation_score >= 2 or pattern_matches >= 1:
            return "OUI"
        return "NON"
    
    def _detect_theme(self, tweet_lower: str) -> str:
        """Détecte le thème principal"""
        theme_scores = {}
        
        for theme, keywords in [
            ('FIBRE', self.patterns['theme_fibre']),
            ('MOBILE', self.patterns['theme_mobile']),
            ('TV', self.patterns['theme_tv']),
            ('FACTURE', self.patterns['theme_facture']),
            ('SAV', self.patterns['theme_sav']),
            ('RESEAU', self.patterns['theme_reseau'])
        ]:
            theme_scores[theme] = sum(1 for keyword in keywords if keyword in tweet_lower)
        
        if theme_scores:
            best_theme = max(theme_scores, key=theme_scores.get)
            if theme_scores[best_theme] > 0:
                return best_theme
        
        return "AUTRE"
    
    def _detect_sentiment(self, tweet_lower: str) -> str:
        """Détecte le sentiment"""
        neg_score = sum(1 for keyword in self.patterns['sentiment_negatif'] 
                        if keyword in tweet_lower)
        pos_score = sum(1 for keyword in self.patterns['sentiment_positif'] 
                       if keyword in tweet_lower)
        
        if neg_score > pos_score and neg_score > 0:
            return "NEGATIF"
        elif pos_score > neg_score and pos_score > 0:
            return "POSITIF"
        else:
            return "NEUTRE"
    
    def _detect_urgence(self, tweet_lower: str) -> str:
        """Détecte le niveau d'urgence"""
        if any(keyword in tweet_lower for keyword in self.patterns['urgence_critique']):
            return "CRITIQUE"
        elif any(keyword in tweet_lower for keyword in self.patterns['urgence_elevee']):
            return "ELEVEE"
        elif 'depuis' in tweet_lower or 'depuis ce matin' in tweet_lower:
            return "MOYENNE"
        else:
            return "FAIBLE"
    
    def _detect_type_incident(self, tweet_lower: str, theme: str) -> str:
        """Détecte le type d'incident"""
        if any(keyword in tweet_lower for keyword in self.patterns['type_panne']):
            return "PANNE"
        elif any(keyword in tweet_lower for keyword in self.patterns['type_lenteur']):
            return "LENTEUR"
        elif any(keyword in tweet_lower for keyword in self.patterns['type_facturation']):
            return "FACTURATION"
        elif any(keyword in tweet_lower for keyword in self.patterns['type_processus_sav']):
            return "PROCESSUS_SAV"
        elif theme in ['FIBRE', 'MOBILE', 'TV']:
            return "PANNE"  # Par défaut pour les thèmes techniques
        else:
            return "AUTRE"
    
    def _calculate_confidence(self, tweet_lower: str, is_reclamation: str, 
                            theme: str, sentiment: str) -> float:
        """Calcule le score de confiance"""
        confidence = 0.5  # Base
        
        # Bonus pour réclamation claire
        if is_reclamation == "OUI":
            confidence += 0.2
        
        # Bonus pour thème identifié
        if theme != "AUTRE":
            confidence += 0.1
        
        # Bonus pour sentiment clair
        if sentiment != "NEUTRE":
            confidence += 0.1
        
        # Bonus pour mots-clés spécifiques
        specific_keywords = ['@free', 'freebox', 'free mobile', 'problème', 'panne']
        keyword_count = sum(1 for keyword in specific_keywords if keyword in tweet_lower)
        confidence += min(keyword_count * 0.05, 0.2)
        
        return min(confidence, 0.95)
    
    def _generate_justification(self, is_reclamation: str, theme: str, 
                              sentiment: str, urgence: str) -> str:
        """Génère une justification de la classification"""
        justifications = []
        
        if is_reclamation == "OUI":
            justifications.append("Problème ou insatisfaction exprimé")
        else:
            justifications.append("Tweet informatif ou neutre")
        
        if theme != "AUTRE":
            justifications.append(f"Thème {theme} identifié")
        
        if sentiment != "NEUTRE":
            justifications.append(f"Sentiment {sentiment} détecté")
        
        if urgence in ["ELEVEE", "CRITIQUE"]:
            justifications.append(f"Urgence {urgence} détectée")
        
        return " | ".join(justifications) if justifications else "Classification automatique"
    
    def _get_default_classification(self, tweet: str) -> ClassificationResult:
        """Retourne une classification par défaut en cas d'erreur"""
        return ClassificationResult(
            is_reclamation="NON",
            theme="AUTRE",
            sentiment="NEUTRE",
            urgence="FAIBLE",
            type_incident="AUTRE",
            confidence=0.5,
            justification="Classification par défaut (erreur)"
        )
    
    def batch_classify(self, tweets: List[str]) -> List[ClassificationResult]:
        """
        Classification en lot pour de meilleures performances
        
        Args:
            tweets: Liste des tweets à classifier
            
        Returns:
            List[ClassificationResult]: Liste des résultats de classification
        """
        results = []
        
        for i, tweet in enumerate(tweets):
            try:
                result = self.classify(tweet)
                results.append(result)
                
                # Log du progrès
                if (i + 1) % 100 == 0:
                    logger.info(f"Classification: {i + 1}/{len(tweets)} tweets traités")
                    
            except Exception as e:
                logger.error(f"Erreur classification tweet {i}: {e}")
                results.append(self._get_default_classification(tweet))
        
        return results
    
    def classify_dataframe(self, df: pd.DataFrame, text_column: str = 'text') -> pd.DataFrame:
        """
        Classifie un DataFrame de tweets
        
        Args:
            df: DataFrame contenant les tweets
            text_column: Nom de la colonne contenant le texte
            
        Returns:
            pd.DataFrame: DataFrame enrichi avec les classifications
        """
        logger.info(f"Classification de {len(df)} tweets...")
        
        # Classification en lot
        results = self.batch_classify(df[text_column].tolist())
        
        # Ajout des colonnes de classification
        df_classified = df.copy()
        df_classified['is_reclamation'] = [r.is_reclamation for r in results]
        df_classified['theme'] = [r.theme for r in results]
        df_classified['sentiment'] = [r.sentiment for r in results]
        df_classified['urgence'] = [r.urgence for r in results]
        df_classified['type_incident'] = [r.type_incident for r in results]
        df_classified['confidence'] = [r.confidence for r in results]
        df_classified['justification'] = [r.justification for r in results]
        
        # Ajout de la date de classification
        df_classified['classification_date'] = datetime.now().isoformat()
        
        logger.info("Classification terminée avec succès")
        return df_classified

# Fonctions utilitaires
def load_classifier(model_path: Optional[str] = None, 
                   llm_provider: str = "fallback") -> TweetClassifier:
    """
    Charge un classificateur pré-entraîné
    
    Args:
        model_path: Chemin vers le modèle
        llm_provider: Fournisseur LLM
        
    Returns:
        TweetClassifier: Instance du classificateur
    """
    return TweetClassifier(model_path=model_path, llm_provider=llm_provider)

def save_classification_results(df: pd.DataFrame, output_path: str):
    """
    Sauvegarde les résultats de classification
    
    Args:
        df: DataFrame avec les classifications
        output_path: Chemin de sauvegarde
    """
    try:
        df.to_csv(output_path, index=False, encoding='utf-8')
        logger.info(f"Résultats sauvegardés: {output_path}")
    except Exception as e:
        logger.error(f"Erreur sauvegarde: {e}")

def get_classification_metrics(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calcule les métriques de classification
    
    Args:
        df: DataFrame avec les classifications
        
    Returns:
        Dict[str, float]: Métriques de performance
    """
    metrics = {}
    
    # Taux de réclamation
    reclamation_rate = (df['is_reclamation'] == 'OUI').mean()
    metrics['reclamation_rate'] = reclamation_rate
    
    # Confiance moyenne
    avg_confidence = df['confidence'].mean()
    metrics['avg_confidence'] = avg_confidence
    
    # Distribution des thèmes
    theme_dist = df['theme'].value_counts(normalize=True)
    metrics['theme_distribution'] = theme_dist.to_dict()
    
    # Distribution des sentiments
    sentiment_dist = df['sentiment'].value_counts(normalize=True)
    metrics['sentiment_distribution'] = sentiment_dist.to_dict()
    
    return metrics



