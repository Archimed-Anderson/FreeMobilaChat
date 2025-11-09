"""
Module d'analyse de sentiment
Analyse de sentiment pour tweets avec support multi-classes
"""

import re
from typing import Dict, Tuple, Optional, List
from enum import Enum


class SentimentType(str, Enum):
    """Types de sentiment"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class SentimentAnalyzer:
    """Analyseur de sentiment basé sur des règles et lexiques"""
    
    def __init__(self):
        """Initialise l'analyseur avec des lexiques de sentiment"""
        
        # Lexique de mots positifs (français)
        self.positive_words = {
            'merci', 'super', 'excellent', 'parfait', 'génial', 'top', 'bravo',
            'satisfait', 'content', 'bien', 'bon', 'meilleur', 'rapide', 'efficace',
            'professionnel', 'qualité', 'recommande', 'félicitations', 'impressionnant',
            'agréable', 'sympathique', 'formidable', 'magnifique', 'fantastique'
        }
        
        # Lexique de mots négatifs (français)
        self.negative_words = {
            'nul', 'mauvais', 'horrible', 'catastrophe', 'honte', 'scandale',
            'incompétent', 'lent', 'cher', 'arnaque', 'problème', 'bug', 'panne',
            'déçu', 'mécontent', 'énervé', 'frustré', 'inacceptable', 'inadmissible',
            'désastreux', 'pourri', 'médiocre', 'décevant', 'honteux', 'ridicule'
        }
        
        # Intensificateurs
        self.intensifiers = {
            'très', 'vraiment', 'trop', 'super', 'hyper', 'extrêmement',
            'complètement', 'totalement', 'absolument'
        }
        
        # Négations
        self.negations = {
            'pas', 'plus', 'jamais', 'aucun', 'aucune', 'rien',
            'personne', 'ni', 'sans', 'ne'
        }
        
        # Emojis de sentiment
        self.positive_emojis = ['😊', '😃', '😄', '👍', '💪', '❤️', '😍', '🎉', '✨', '⭐']
        self.negative_emojis = ['😡', '😠', '😤', '😭', '😢', '👎', '💔', '😞', '😓', '🤬']
    
    def analyze_sentiment(self, text: str) -> Dict[str, any]:
        """
        Analyse le sentiment d'un texte
        
        Args:
            text: Texte à analyser
            
        Returns:
            Dictionnaire avec le sentiment, le score et la confiance
            
        Examples:
            >>> analyzer = SentimentAnalyzer()
            >>> result = analyzer.analyze_sentiment("Le service est excellent!")
            >>> result['sentiment']
            'positive'
        """
        if not text or not isinstance(text, str):
            return {
                'sentiment': SentimentType.NEUTRAL,
                'score': 0.0,
                'confidence': 0.0,
                'details': {'reason': 'empty_text'}
            }
        
        text_lower = text.lower()
        
        # Compter les mots de sentiment
        positive_count = sum(1 for word in self.positive_words if word in text_lower)
        negative_count = sum(1 for word in self.negative_words if word in text_lower)
        
        # Analyser les emojis
        emoji_score = self._analyze_emojis(text)
        
        # Détecter les négations
        has_negation = any(neg in text_lower for neg in self.negations)
        
        # Détecter les intensificateurs
        has_intensifier = any(intens in text_lower for intens in self.intensifiers)
        
        # Calculer le score brut
        raw_score = positive_count - negative_count + emoji_score
        
        # Ajuster pour les négations (inverse le sentiment)
        if has_negation:
            raw_score = -raw_score * 0.8  # Atténuer légèrement
        
        # Ajuster pour les intensificateurs
        if has_intensifier:
            raw_score *= 1.3
        
        # Normaliser le score entre -1 et 1
        max_possible = len(self.positive_words) + len(self.negative_words)
        normalized_score = max(min(raw_score / max(max_possible, 1), 1.0), -1.0)
        
        # Déterminer le sentiment (seuils abaissés pour plus de sensibilité)
        if normalized_score > 0.05:  # Abaissé de 0.15 à 0.05
            sentiment = SentimentType.POSITIVE
        elif normalized_score < -0.05:  # Abaissé de -0.15 à -0.05
            sentiment = SentimentType.NEGATIVE
        else:
            sentiment = SentimentType.NEUTRAL
        
        # Calculer la confiance
        confidence = min(abs(normalized_score) * 1.5, 1.0)
        
        return {
            'sentiment': sentiment,
            'score': round(normalized_score, 3),
            'confidence': round(confidence, 3),
            'details': {
                'positive_words': positive_count,
                'negative_words': negative_count,
                'emoji_score': emoji_score,
                'has_negation': has_negation,
                'has_intensifier': has_intensifier
            }
        }
    
    def _analyze_emojis(self, text: str) -> float:
        """
        Analyse les emojis pour le sentiment
        
        Args:
            text: Texte contenant des emojis
            
        Returns:
            Score de sentiment basé sur les emojis (-1 à 1)
        """
        positive_emoji_count = sum(1 for emoji in self.positive_emojis if emoji in text)
        negative_emoji_count = sum(1 for emoji in self.negative_emojis if emoji in text)
        
        if positive_emoji_count == 0 and negative_emoji_count == 0:
            return 0.0
        
        # Score normalisé
        emoji_score = (positive_emoji_count - negative_emoji_count) / \
                      max(positive_emoji_count + negative_emoji_count, 1)
        
        return emoji_score * 0.5  # Les emojis comptent pour 50% max
    
    def batch_analyze(self, texts: List[str]) -> List[Dict[str, any]]:
        """
        Analyse multiple textes en batch
        
        Args:
            texts: Liste de textes à analyser
            
        Returns:
            Liste des résultats d'analyse
        """
        return [self.analyze_sentiment(text) for text in texts]
    
    def get_sentiment_distribution(self, texts: List[str]) -> Dict[str, int]:
        """
        Calcule la distribution des sentiments dans une liste de textes
        
        Args:
            texts: Liste de textes
            
        Returns:
            Dictionnaire avec le compte par sentiment
        """
        results = self.batch_analyze(texts)
        
        distribution = {
            SentimentType.POSITIVE: 0,
            SentimentType.NEUTRAL: 0,
            SentimentType.NEGATIVE: 0
        }
        
        for result in results:
            distribution[result['sentiment']] += 1
        
        return distribution
    
    def detect_irony(self, text: str) -> bool:
        """
        Détecte les marqueurs d'ironie potentiels
        
        Args:
            text: Texte à analyser
            
        Returns:
            True si des marqueurs d'ironie sont détectés
        """
        irony_markers = [
            'lol', 'mdr', '/s', 'ironique', 'sarcasme',
            '😂', '🙄', '😏'
        ]
        
        text_lower = text.lower()
        return any(marker in text_lower for marker in irony_markers)
    
    def analyze_with_context(self, 
                            text: str,
                            consider_irony: bool = True) -> Dict[str, any]:
        """
        Analyse de sentiment avec contexte enrichi
        
        Args:
            text: Texte à analyser
            consider_irony: Prendre en compte l'ironie
            
        Returns:
            Analyse complète avec flags contextuels
        """
        base_analysis = self.analyze_sentiment(text)
        
        # Détecter l'ironie
        has_irony = self.detect_irony(text) if consider_irony else False
        
        # Si ironie détectée, inverser le sentiment
        if has_irony:
            if base_analysis['sentiment'] == SentimentType.POSITIVE:
                base_analysis['sentiment'] = SentimentType.NEGATIVE
            elif base_analysis['sentiment'] == SentimentType.NEGATIVE:
                base_analysis['sentiment'] = SentimentType.POSITIVE
            
            base_analysis['score'] = -base_analysis['score']
            base_analysis['confidence'] *= 0.7  # Réduire la confiance
        
        base_analysis['details']['has_irony'] = has_irony
        
        return base_analysis

