"""
Module de Classification Dynamique et Relationnelle - FreeMobilaChat
====================================================================

Classification intelligente qui s'adapte automatiquement au contenu CSV:
- Classification d'intention (information, demande, réclamation, compliment, etc.)
- Catégorisation thématique dynamique
- Analyse de sentiment contextuelle
- Évaluation d'urgence adaptative

Le module détecte automatiquement les colonnes de texte et adapte ses modèles
de classification en fonction du contenu spécifique de chaque fichier.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import re
import logging
from collections import Counter

logger = logging.getLogger(__name__)


@dataclass
class DynamicClassificationResult:
    """Résultat de classification dynamique"""
    intention: str
    theme: str
    sentiment: str
    urgency: str
    confidence: float
    detected_keywords: List[str]
    metadata: Dict[str, Any]


class IntentionClassifier:
    """Classificateur d'intention adaptatif"""
    
    INTENTION_PATTERNS = {
        'reclamation': [
            r'\bproblème\b', r'\bpanne\b', r'\bbug\b', r'\berreur\b',
            r'\bne\s+fonctionne\s+pas\b', r'\bdysfonctionnement\b',
            r'\binsatisfait\b', r'\bmécontent\b'
        ],
        'demande_info': [
            r'\bcomment\b', r'\bpourquoi\b', r'\bquand\b', r'\bquel\b',
            r'\best-ce\s+que\b', r'\bpouvez-vous\b', r'\bje\s+voudrais\s+savoir\b'
        ],
        'demande_aide': [
            r'\baide\b', r'\baider\b', r'\bsupport\b', r'\bassistance\b',
            r'\bbesoin\b', r'\bje\s+ne\s+sais\s+pas\b', r'\bcomment\s+faire\b'
        ],
        'compliment': [
            r'\bmerci\b', r'\bsuper\b', r'\bexcellent\b', r'\bparfait\b',
            r'\bgénial\b', r'\bbravo\b', r'\bfélicitations\b'
        ],
        'suggestion': [
            r'\bdevrais\b', r'\bdevrait\b', r'\bpourrait\b', r'\bserait\s+bien\b',
            r'\bje\s+propose\b', r'\bsuggestion\b', r'\bidée\b'
        ],
        'information': [
            r'\bannonce\b', r'\binformation\b', r'\bnouveau\b', r'\bnouvelle\b',
            r'\bdécouvrez\b', r'\bdisponible\b'
        ]
    }
    
    def classify(self, text: str) -> Tuple[str, float, List[str]]:
        """Classifie l'intention d'un texte"""
        text_lower = text.lower()
        scores = {}
        matched_keywords = []
        
        for intention, patterns in self.INTENTION_PATTERNS.items():
            score = 0
            keywords = []
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                if matches:
                    score += len(matches)
                    keywords.extend(matches)
            scores[intention] = score
            if keywords:
                matched_keywords.extend(keywords)
        
        if not scores or all(s == 0 for s in scores.values()):
            return 'information', 0.5, []
        
        best_intention = max(scores, key=scores.get)
        total_score = sum(scores.values())
        confidence = min(scores[best_intention] / max(total_score, 1), 0.95)
        
        return best_intention, confidence, matched_keywords


class ThemeClassifier:
    """Classificateur thématique dynamique"""
    
    BASE_THEMES = {
        'fibre': ['fibre', 'ftth', 'internet', 'débit', 'connexion', 'adsl', 'vdsl'],
        'mobile': ['mobile', 'téléphone', 'forfait', '4g', '5g', 'data', 'appel', 'sms'],
        'tv': ['tv', 'télévision', 'chaîne', 'programme', 'replay', 'streaming'],
        'facture': ['facture', 'facturation', 'prix', 'coût', 'tarif', 'paiement', 'abonnement'],
        'wifi': ['wifi', 'wi-fi', 'réseau sans fil', 'point d\'accès'],
        'sav': ['sav', 'service client', 'support', 'assistance', 'technicien'],
        'activation': ['activation', 'activer', 'mise en service', 'installation'],
        'resiliation': ['résiliation', 'résilier', 'annulation', 'arrêt']
    }
    
    def __init__(self):
        """Initialise le classificateur avec les thèmes de base"""
        self.themes = self.BASE_THEMES.copy()
        self.custom_themes = {}
    
    def detect_custom_themes(self, texts: List[str], min_frequency: int = 5):
        """Détecte des thèmes personnalisés basés sur la fréquence des mots"""
        # Extraction des mots significatifs
        all_words = []
        for text in texts[:1000]:  # Limiter pour performance
            words = re.findall(r'\b[a-zàâäéèêëïîôùûü]{4,}\b', text.lower())
            all_words.extend(words)
        
        # Comptage des fréquences
        word_freq = Counter(all_words)
        
        # Filtrage des mots communs
        stop_words = {'dans', 'pour', 'avec', 'sans', 'plus', 'tout', 'tous', 'fait', 'être', 'avoir'}
        custom_keywords = {}
        
        for word, freq in word_freq.most_common(50):
            if freq >= min_frequency and word not in stop_words:
                # Vérifier si ce n'est pas déjà dans les thèmes de base
                is_base_theme = any(word in keywords for keywords in self.themes.values())
                if not is_base_theme:
                    theme_name = f"custom_{word}"
                    custom_keywords[theme_name] = [word]
        
        self.custom_themes = custom_keywords
        logger.info(f"Détecté {len(custom_keywords)} thèmes personnalisés")
    
    def classify(self, text: str, use_custom: bool = True) -> Tuple[List[str], float, List[str]]:
        """Classifie les thèmes d'un texte"""
        text_lower = text.lower()
        detected_themes = []
        matched_keywords = []
        scores = {}
        
        # Vérification des thèmes de base
        themes_to_check = self.themes.copy()
        if use_custom and self.custom_themes:
            themes_to_check.update(self.custom_themes)
        
        for theme, keywords in themes_to_check.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                scores[theme] = score
                detected_themes.append(theme)
                matched_keywords.extend([kw for kw in keywords if kw in text_lower])
        
        if not detected_themes:
            detected_themes = ['autre']
            confidence = 0.5
        else:
            total_score = sum(scores.values())
            max_score = max(scores.values())
            confidence = min(max_score / max(total_score, 1) * 1.2, 0.95)
        
        return detected_themes, confidence, matched_keywords


class SentimentClassifier:
    """Classificateur de sentiment contextuel"""
    
    SENTIMENT_LEXICON = {
        'positive': {
            'words': ['merci', 'super', 'excellent', 'génial', 'parfait', 'bravo', 
                     'content', 'satisfait', 'ravi', 'heureux', 'top'],
            'weight': 1.0
        },
        'negative': {
            'words': ['nul', 'mauvais', 'horrible', 'catastrophe', 'déçu', 'frustré',
                     'énervé', 'mécontent', 'insatisfait', 'problème', 'panne', 'bug'],
            'weight': 1.0
        },
        'intensifiers': {
            'words': ['très', 'vraiment', 'trop', 'extrêmement', 'totalement'],
            'weight': 1.5
        },
        'negators': {
            'words': ['pas', 'jamais', 'aucun', 'rien'],
            'weight': -1.0
        }
    }
    
    def classify(self, text: str) -> Tuple[str, float, Dict[str, int]]:
        """Classifie le sentiment d'un texte"""
        text_lower = text.lower()
        words = text_lower.split()
        
        positive_score = 0
        negative_score = 0
        
        for i, word in enumerate(words):
            # Vérifier les intensificateurs
            intensifier = 1.0
            if i > 0 and words[i-1] in self.SENTIMENT_LEXICON['intensifiers']['words']:
                intensifier = self.SENTIMENT_LEXICON['intensifiers']['weight']
            
            # Vérifier les négations
            negator = 1.0
            if i > 0 and words[i-1] in self.SENTIMENT_LEXICON['negators']['words']:
                negator = self.SENTIMENT_LEXICON['negators']['weight']
            
            # Scorer le sentiment
            if word in self.SENTIMENT_LEXICON['positive']['words']:
                positive_score += intensifier * negator
            elif word in self.SENTIMENT_LEXICON['negative']['words']:
                negative_score += intensifier * abs(negator)
        
        # Déterminer le sentiment final
        total_score = positive_score + negative_score
        
        if positive_score > negative_score * 1.5:
            sentiment = 'positif'
            confidence = min(positive_score / max(total_score, 1), 0.95)
        elif negative_score > positive_score * 1.5:
            sentiment = 'negatif'
            confidence = min(negative_score / max(total_score, 1), 0.95)
        else:
            sentiment = 'neutre'
            confidence = 0.7
        
        counts = {
            'positive': int(positive_score),
            'negative': int(negative_score)
        }
        
        return sentiment, confidence, counts


class UrgencyClassifier:
    """Classificateur d'urgence adaptatif"""
    
    URGENCY_INDICATORS = {
        'critique': [
            r'\burgent\b', r'\bcritique\b', r'\bimmédiat\b', r'\bimmédiatement\b',
            r'\btout\s+de\s+suite\b', r'\bimpossible\b', r'\bbloqué\b'
        ],
        'haute': [
            r'\bdepuis\s+\d+\s+heures?\b', r'\btoute\s+la\s+journée\b',
            r'\bce\s+matin\b', r'\bhier\b', r'\brapidement\b', r'\bvite\b'
        ],
        'moyenne': [
            r'\bproblème\b', r'\bbesoin\b', r'\baide\b', r'\bquestion\b'
        ],
        'basse': [
            r'\binformation\b', r'\bcurieux\b', r'\bje\s+me\s+demande\b'
        ]
    }
    
    def classify(self, text: str, intention: str) -> Tuple[str, float]:
        """Classifie l'urgence d'un texte"""
        text_lower = text.lower()
        scores = {level: 0 for level in self.URGENCY_INDICATORS}
        
        for level, patterns in self.URGENCY_INDICATORS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    scores[level] += 1
        
        # Ajustement basé sur l'intention
        if intention == 'reclamation':
            scores['haute'] += 1
        elif intention == 'compliment':
            scores['basse'] += 1
        
        # Détermination de l'urgence
        if scores['critique'] > 0:
            urgency = 'critique'
            confidence = 0.9
        elif scores['haute'] > 0:
            urgency = 'haute'
            confidence = 0.85
        elif scores['moyenne'] > scores['basse']:
            urgency = 'moyenne'
            confidence = 0.75
        else:
            urgency = 'basse'
            confidence = 0.7
        
        return urgency, confidence


class DynamicClassificationEngine:
    """Moteur de classification dynamique et adaptatif"""
    
    def __init__(self):
        """Initialise le moteur de classification"""
        self.intention_classifier = IntentionClassifier()
        self.theme_classifier = ThemeClassifier()
        self.sentiment_classifier = SentimentClassifier()
        self.urgency_classifier = UrgencyClassifier()
        self.is_trained = False
    
    def train_on_dataset(self, df: pd.DataFrame, text_column: str):
        """Entraîne les classificateurs sur un dataset spécifique"""
        logger.info("Entraînement des classificateurs dynamiques...")
        
        texts = df[text_column].dropna().astype(str).tolist()
        
        # Détection de thèmes personnalisés
        self.theme_classifier.detect_custom_themes(texts)
        
        self.is_trained = True
        logger.info("Entraînement terminé")
    
    def classify_text(self, text: str) -> DynamicClassificationResult:
        """Classifie un texte complet avec tous les classificateurs"""
        # Classification d'intention
        intention, intention_conf, intention_keywords = self.intention_classifier.classify(text)
        
        # Classification thématique
        themes, theme_conf, theme_keywords = self.theme_classifier.classify(text, use_custom=self.is_trained)
        
        # Analyse de sentiment
        sentiment, sentiment_conf, sentiment_counts = self.sentiment_classifier.classify(text)
        
        # Évaluation d'urgence
        urgency, urgency_conf = self.urgency_classifier.classify(text, intention)
        
        # Calcul de confiance globale
        overall_confidence = np.mean([intention_conf, theme_conf, sentiment_conf, urgency_conf])
        
        # Compilation des mots-clés détectés
        all_keywords = list(set(intention_keywords + theme_keywords))
        
        return DynamicClassificationResult(
            intention=intention,
            theme=themes[0] if themes else 'autre',
            sentiment=sentiment,
            urgency=urgency,
            confidence=float(overall_confidence),
            detected_keywords=all_keywords[:10],  # Limiter à 10
            metadata={
                'all_themes': themes,
                'sentiment_counts': sentiment_counts,
                'intention_confidence': intention_conf,
                'theme_confidence': theme_conf,
                'sentiment_confidence': sentiment_conf,
                'urgency_confidence': urgency_conf
            }
        )
    
    def classify_dataframe(self, df: pd.DataFrame, text_column: str) -> pd.DataFrame:
        """Classifie un DataFrame complet"""
        logger.info(f"Classification de {len(df)} lignes...")
        
        # Entraînement sur le dataset
        self.train_on_dataset(df, text_column)
        
        # Classification de chaque ligne
        results = []
        for text in df[text_column]:
            result = self.classify_text(str(text))
            results.append(result)
        
        # Enrichissement du DataFrame
        df_classified = df.copy()
        df_classified['intention'] = [r.intention for r in results]
        df_classified['theme'] = [r.theme for r in results]
        df_classified['sentiment'] = [r.sentiment for r in results]
        df_classified['urgency'] = [r.urgency for r in results]
        df_classified['confidence'] = [r.confidence for r in results]
        df_classified['keywords'] = [', '.join(r.detected_keywords) for r in results]
        
        # Métadonnées supplémentaires - Convert list to string to avoid unhashable type error
        df_classified['all_themes'] = [', '.join(r.metadata['all_themes']) for r in results]
        
        logger.info("Classification terminée")
        return df_classified
    
    def get_classification_summary(self, df_classified: pd.DataFrame) -> Dict[str, Any]:
        """Génère un résumé des classifications"""
        summary = {
            'total_rows': len(df_classified),
            'intention_distribution': df_classified['intention'].value_counts().to_dict(),
            'theme_distribution': df_classified['theme'].value_counts().to_dict(),
            'sentiment_distribution': df_classified['sentiment'].value_counts().to_dict(),
            'urgency_distribution': df_classified['urgency'].value_counts().to_dict(),
            'avg_confidence': float(df_classified['confidence'].mean()),
            'high_confidence_rate': float((df_classified['confidence'] >= 0.8).mean())
        }
        
        return summary
