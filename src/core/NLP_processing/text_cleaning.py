"""
Module de nettoyage de texte pour NLP
Traitement robuste des tweets avec gestion des cas limites
"""

import re
import html
import unicodedata
from typing import List, Dict, Optional


class TextCleaner:
    """Nettoyeur de texte avancé pour analyse NLP"""
    
    def __init__(self):
        """Initialize text cleaner with patterns"""
        # Patterns regex pour différents éléments
        self.url_pattern = re.compile(r'http\S+|www\S+|https\S+', re.MULTILINE)
        self.mention_pattern = re.compile(r'@\w+')
        self.hashtag_pattern = re.compile(r'#\w+')
        self.emoji_pattern = re.compile(
            r'[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|'
            r'[\U0001F680-\U0001F6FF]|[\U0001F1E0-\U0001F1FF]'
        )
        self.whitespace_pattern = re.compile(r'\s+')
        
        # Stopwords français pour extraction de mots-clés
        self.french_stopwords = {
            'le', 'de', 'et', 'à', 'un', 'il', 'être', 'en', 'avoir', 'que', 'pour',
            'dans', 'ce', 'son', 'une', 'sur', 'avec', 'ne', 'se', 'pas', 'tout', 'plus',
            'par', 'du', 'elle', 'au', 'sont', 'ils', 'nous', 'sa', 'qui', 'des', 'les'
        }
    
    def clean_basic(self, text: str) -> str:
        """
        Nettoyage basique du texte
        
        Args:
            text: Texte brut à nettoyer
            
        Returns:
            Texte nettoyé
            
        Examples:
            >>> cleaner = TextCleaner()
            >>> cleaner.clean_basic("Hello&nbsp;World!")
            'Hello World!'
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Décoder les entités HTML
        text = html.unescape(text)
        
        # Supprimer les caractères de contrôle
        text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C')
        
        # Normaliser les espaces
        text = self.whitespace_pattern.sub(' ', text)
        
        return text.strip()
    
    def remove_urls(self, text: str) -> str:
        """Supprime les URLs du texte"""
        return self.url_pattern.sub('', text)
    
    def remove_mentions(self, text: str) -> str:
        """Supprime les @mentions du texte"""
        return self.mention_pattern.sub('', text)
    
    def remove_hashtags(self, text: str) -> str:
        """Supprime les #hashtags du texte"""
        return self.hashtag_pattern.sub('', text)
    
    def remove_emojis(self, text: str) -> str:
        """Supprime les emojis du texte"""
        return self.emoji_pattern.sub('', text)
    
    def extract_mentions(self, text: str) -> List[str]:
        """
        Extrait les @mentions du texte
        
        Args:
            text: Texte source
            
        Returns:
            Liste des mentions (sans le @)
        """
        matches = self.mention_pattern.findall(text)
        return [match[1:] for match in matches]
    
    def extract_hashtags(self, text: str) -> List[str]:
        """
        Extrait les #hashtags du texte
        
        Args:
            text: Texte source
            
        Returns:
            Liste des hashtags (sans le #)
        """
        matches = self.hashtag_pattern.findall(text)
        return [match[1:] for match in matches]
    
    def extract_urls(self, text: str) -> List[str]:
        """Extrait les URLs du texte"""
        return self.url_pattern.findall(text)
    
    def clean_for_analysis(self, 
                          text: str, 
                          preserve_mentions: bool = True,
                          preserve_hashtags: bool = True,
                          preserve_emojis: bool = True) -> str:
        """
        Nettoie le texte pour l'analyse NLP
        
        Args:
            text: Texte à nettoyer
            preserve_mentions: Conserver les @mentions
            preserve_hashtags: Conserver les #hashtags
            preserve_emojis: Conserver les emojis
            
        Returns:
            Texte nettoyé pour analyse
            
        Examples:
            >>> cleaner = TextCleaner()
            >>> text = "@Free le réseau est nul 😡 https://t.co/xxx"
            >>> cleaner.clean_for_analysis(text, preserve_emojis=False)
            '@Free le réseau est nul'
        """
        if not text:
            return ""
        
        # Nettoyage basique
        text = self.clean_basic(text)
        
        # Supprimer les URLs (généralement pas utiles pour l'analyse)
        text = self.remove_urls(text)
        
        # Supprimer optionnellement mentions, hashtags, emojis
        if not preserve_mentions:
            text = self.remove_mentions(text)
        if not preserve_hashtags:
            text = self.remove_hashtags(text)
        if not preserve_emojis:
            text = self.remove_emojis(text)
        
        # Normaliser les caractères répétés (ex: "nooooon" -> "nooon")
        text = re.sub(r'(.)\1{3,}', r'\1\1\1', text)
        
        # Nettoyer les espaces
        text = self.whitespace_pattern.sub(' ', text).strip()
        
        return text
    
    def handle_special_cases(self, text: str) -> Dict[str, any]:
        """
        Détecte et gère les cas spéciaux
        
        Args:
            text: Texte à analyser
            
        Returns:
            Dictionnaire avec les flags de cas spéciaux
        """
        if not text:
            return {
                'is_empty': True,
                'is_too_short': True,
                'is_too_long': False,
                'has_unicode_issues': False,
                'has_irony_markers': False
            }
        
        length = len(text)
        
        # Marqueurs d'ironie
        irony_markers = ['lol', 'mdr', '😂', '🙄', '/s', 'ironique']
        has_irony = any(marker in text.lower() for marker in irony_markers)
        
        # Problèmes Unicode
        try:
            text.encode('utf-8').decode('utf-8')
            has_unicode_issues = False
        except (UnicodeDecodeError, UnicodeEncodeError):
            has_unicode_issues = True
        
        return {
            'is_empty': length == 0,
            'is_too_short': length < 10,
            'is_too_long': length > 280,
            'has_unicode_issues': has_unicode_issues,
            'has_irony_markers': has_irony,
            'length': length
        }
    
    def normalize_text(self, text: str, lowercase: bool = True) -> str:
        """
        Normalise le texte (Unicode, casse)
        
        Args:
            text: Texte à normaliser
            lowercase: Convertir en minuscules
            
        Returns:
            Texte normalisé
        """
        if not text:
            return ""
        
        # Normalisation Unicode (NFKD pour décomposer les accents)
        text = unicodedata.normalize('NFKD', text)
        
        # Convertir en minuscules si demandé
        if lowercase:
            text = text.lower()
        
        # Nettoyer les espaces
        text = self.whitespace_pattern.sub(' ', text).strip()
        
        return text
    
    def extract_keywords(self, 
                        text: str, 
                        min_length: int = 3,
                        max_keywords: int = 10) -> List[str]:
        """
        Extrait les mots-clés potentiels du texte
        
        Args:
            text: Texte source
            min_length: Longueur minimale des mots
            max_keywords: Nombre maximum de mots-clés
            
        Returns:
            Liste des mots-clés les plus fréquents
        """
        if not text:
            return []
        
        # Nettoyer et normaliser
        clean_text = self.clean_for_analysis(
            text, 
            preserve_mentions=False, 
            preserve_hashtags=False,
            preserve_emojis=False
        )
        clean_text = clean_text.lower()
        
        # Extraire les mots
        words = re.findall(r'\b\w+\b', clean_text)
        
        # Filtrer les mots
        keywords = []
        for word in words:
            if (len(word) >= min_length and
                word not in self.french_stopwords and
                not word.isdigit() and
                word.isalpha()):
                keywords.append(word)
        
        # Compter les fréquences
        from collections import Counter
        word_counts = Counter(keywords)
        
        return [word for word, count in word_counts.most_common(max_keywords)]
    
    def is_spam_like(self, text: str) -> bool:
        """
        Détecte les caractéristiques de spam
        
        Args:
            text: Texte à analyser
            
        Returns:
            True si le texte ressemble à du spam
        """
        if not text or len(text) < 5:
            return True
        
        # Vérifier la répétition excessive
        words = text.lower().split()
        if len(words) > 0:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.3:
                return True
        
        # Vérifier les mentions excessives
        if len(self.extract_mentions(text)) > 5:
            return True
        
        # Vérifier les hashtags excessifs
        if len(self.extract_hashtags(text)) > 8:
            return True
        
        # Vérifier les URLs excessives
        if len(self.extract_urls(text)) > 3:
            return True
        
        # Vérifier les majuscules excessives
        if len(text) > 10:
            caps_ratio = sum(1 for c in text if c.isupper()) / len(text)
            if caps_ratio > 0.7:
                return True
        
        return False

