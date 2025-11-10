"""
Service de Traitement des Données - FreeMobilaChat
===================================================

Module de prétraitement et validation de données pour l'analyse de tweets.
Assure la qualité des données avant classification et calcul des KPIs.

Fonctionnalités:
- Nettoyage multi-étapes des tweets (URLs, mentions, hashtags, caractères spéciaux)
- Validation de qualité avec scoring automatique
- Normalisation Unicode pour compatibilité multilingue
- Extraction de métadonnées et statistiques descriptives
"""

# Imports des bibliothèques de traitement de données
import pandas as pd  # Manipulation de DataFrames pour datasets structurés
import numpy as np  # Calculs numériques et opérations vectorisées
import logging  # Journalisation des opérations de nettoyage
from typing import Dict, Any, List, Optional, Tuple  # Typage statique pour robustesse
import re  # Expressions régulières pour nettoyage de texte
from datetime import datetime  # Gestion des timestamps
import unicodedata  # Normalisation des caractères Unicode (émojis, accents)

# Configuration du logger pour traçabilité des opérations
logger = logging.getLogger(__name__)

class DataProcessor:
    """
    Processeur de données avec nettoyage, validation et enrichissement
    
    Cette classe implémente un pipeline complet de prétraitement des données
    incluant nettoyage, normalisation, validation de qualité et extraction de métadonnées.
    """
    
    def __init__(self):
        """
        Initialise le processeur avec la configuration des colonnes attendues
        
        Définit les colonnes requises et optionnelles pour la validation de structure.
        """
        # Colonnes obligatoires pour le fonctionnement du système
        self.required_columns = ['text']  # Seul le texte est strictement nécessaire
        
        # Colonnes optionnelles qui enrichissent l'analyse si présentes
        self.optional_columns = ['author', 'date', 'retweet_count', 'favorite_count', 'id']
        
    def clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Exécute le pipeline complet de nettoyage des données
        
        Applique séquentiellement toutes les opérations de nettoyage:
        1. Nettoyage du texte (URLs, mentions, hashtags)
        2. Normalisation des auteurs
        3. Conversion et validation des dates
        4. Normalisation des métriques numériques
        5. Suppression des lignes vides
        6. Normalisation des types de données
        
        Args:
            data: DataFrame brut contenant les tweets à nettoyer
            
        Returns:
            DataFrame nettoyé et normalisé, prêt pour l'analyse
            
        Raises:
            Exception: En cas d'erreur critique lors du nettoyage
        """
        try:
            # Création d'une copie pour préserver les données originales
            cleaned_data = data.copy()  # Protection contre les modifications inattendues
            
            # Étape 1: Nettoyage du texte principal (le plus critique)
            if 'text' in cleaned_data.columns:
                # Application de la fonction de nettoyage à chaque tweet
                cleaned_data['text'] = cleaned_data['text'].apply(self._clean_text)
            
            # Étape 2: Nettoyage des noms d'auteurs (standardisation)
            if 'author' in cleaned_data.columns:
                cleaned_data['author'] = cleaned_data['author'].apply(self._clean_author)
            
            # Étape 3: Conversion et validation des dates
            if 'date' in cleaned_data.columns:
                cleaned_data['date'] = self._clean_dates(cleaned_data['date'])
            
            # Étape 4: Normalisation des colonnes numériques (métriques d'engagement)
            numeric_columns = ['retweet_count', 'favorite_count']  # Métriques sociales
            for col in numeric_columns:
                if col in cleaned_data.columns:
                    # Conversion en numérique avec gestion des valeurs invalides
                    cleaned_data[col] = self._clean_numeric(cleaned_data[col])
            
            # Étape 5: Suppression des lignes vides ou invalides
            cleaned_data = self._remove_empty_rows(cleaned_data)
            
            # Étape 6: Normalisation finale des types de données
            cleaned_data = self._normalize_types(cleaned_data)
            
            # Journalisation du résultat du nettoyage
            logger.info(f"Données nettoyées: {len(cleaned_data)} lignes, {len(cleaned_data.columns)} colonnes")
            
            return cleaned_data
            
        except Exception as e:
            # Capture et journalisation des erreurs critiques
            logger.error(f"Erreur lors du nettoyage des données: {str(e)}")
            raise  # Propagation de l'exception pour gestion en amont
    
    def _clean_text(self, text: str) -> str:
        """Nettoie le texte d'un tweet"""
        
        if pd.isna(text) or not isinstance(text, str):
            return ""
        
        # Normalisation Unicode
        text = unicodedata.normalize('NFKD', text)
        
        # Suppression des caractères de contrôle
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        
        # Suppression des URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Suppression des mentions (@username)
        text = re.sub(r'@\w+', '', text)
        
        # Suppression des hashtags (#hashtag)
        text = re.sub(r'#\w+', '', text)
        
        # Suppression des caractères spéciaux répétés
        text = re.sub(r'([.!?]){2,}', r'\1', text)
        text = re.sub(r'([a-zA-Z])\1{2,}', r'\1\1', text)
        
        # Nettoyage des espaces
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def _clean_author(self, author: str) -> str:
        """Nettoie le nom d'auteur"""
        
        if pd.isna(author) or not isinstance(author, str):
            return ""
        
        # Suppression des caractères spéciaux
        author = re.sub(r'[^\w\s.-]', '', author)
        
        # Nettoyage des espaces
        author = re.sub(r'\s+', ' ', author)
        author = author.strip()
        
        return author
    
    def _clean_dates(self, dates: pd.Series) -> pd.Series:
        """Nettoie et convertit les dates"""
        
        try:
            # Conversion en datetime
            cleaned_dates = pd.to_datetime(dates, errors='coerce')
            
            # Suppression des dates invalides
            cleaned_dates = cleaned_dates.dropna()
            
            return cleaned_dates
            
        except Exception as e:
            logger.warning(f"Erreur lors du nettoyage des dates: {str(e)}")
            return dates
    
    def _clean_numeric(self, series: pd.Series) -> pd.Series:
        """Nettoie les colonnes numériques"""
        
        try:
            # Conversion en numérique
            cleaned_series = pd.to_numeric(series, errors='coerce')
            
            # Remplacement des NaN par 0
            cleaned_series = cleaned_series.fillna(0)
            
            # Conversion en entier si possible
            if cleaned_series.dtype == 'float64' and (cleaned_series % 1 == 0).all():
                cleaned_series = cleaned_series.astype('int64')
            
            return cleaned_series
            
        except Exception as e:
            logger.warning(f"Erreur lors du nettoyage des données numériques: {str(e)}")
            return series
    
    def _remove_empty_rows(self, data: pd.DataFrame) -> pd.DataFrame:
        """Supprime les lignes vides"""
        
        # Suppression des lignes où toutes les colonnes sont NaN
        data = data.dropna(how='all')
        
        # Suppression des lignes où la colonne 'text' est vide
        if 'text' in data.columns:
            data = data[data['text'].str.len() > 0]
        
        return data
    
    def _normalize_types(self, data: pd.DataFrame) -> pd.DataFrame:
        """Normalise les types de données"""
        
        # Conversion des colonnes de texte en string
        text_columns = ['text', 'author']
        for col in text_columns:
            if col in data.columns:
                data[col] = data[col].astype('string')
        
        # Conversion des colonnes numériques
        numeric_columns = ['retweet_count', 'favorite_count']
        for col in numeric_columns:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0)
        
        return data
    
    def validate_data_quality(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Valide la qualité des données"""
        
        quality_report = {
            "total_rows": len(data),
            "total_columns": len(data.columns),
            "quality_score": 0,
            "issues": [],
            "warnings": [],
            "recommendations": []
        }
        
        try:
            # Vérification des colonnes requises
            missing_required = [col for col in self.required_columns if col not in data.columns]
            if missing_required:
                quality_report["issues"].append(f"Colonnes requises manquantes: {', '.join(missing_required)}")
            
            # Vérification des données nulles
            if 'text' in data.columns:
                null_count = data['text'].isnull().sum()
                if null_count > 0:
                    quality_report["warnings"].append(f"{null_count} tweets avec texte vide")
                
                # Vérification de la longueur des textes
                text_lengths = data['text'].str.len()
                avg_length = text_lengths.mean()
                min_length = text_lengths.min()
                max_length = text_lengths.max()
                
                if min_length < 5:
                    quality_report["warnings"].append("Textes très courts détectés")
                
                if max_length > 1000:
                    quality_report["warnings"].append("Textes très longs détectés")
                
                if avg_length < 10:
                    quality_report["issues"].append("Longueur moyenne des textes très faible")
            
            # Vérification des doublons
            if 'text' in data.columns:
                duplicate_count = data['text'].duplicated().sum()
                if duplicate_count > 0:
                    quality_report["warnings"].append(f"{duplicate_count} tweets en double")
            
            # Calcul du score de qualité
            quality_score = 100
            
            # Pénalités pour les problèmes
            quality_score -= len(quality_report["issues"]) * 20
            quality_score -= len(quality_report["warnings"]) * 5
            
            # Bonus pour les colonnes recommandées
            recommended_count = sum(1 for col in self.optional_columns if col in data.columns)
            quality_score += recommended_count * 5
            
            quality_report["quality_score"] = max(0, min(100, quality_score))
            
            # Recommandations
            if quality_report["quality_score"] < 70:
                quality_report["recommendations"].append("Considérez nettoyer davantage les données")
            
            if len(data) < 100:
                quality_report["recommendations"].append("Ajoutez plus de données pour une analyse significative")
            
            if recommended_count < 3:
                quality_report["recommendations"].append("Ajoutez des colonnes comme 'author', 'date' pour une meilleure analyse")
            
            logger.info(f"Score de qualité des données: {quality_report['quality_score']}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la validation de la qualité: {str(e)}")
            quality_report["issues"].append(f"Erreur de validation: {str(e)}")
        
        return quality_report
    
    def prepare_for_analysis(self, data: pd.DataFrame, max_tweets: int = 500) -> pd.DataFrame:
        """Prépare les données pour l'analyse"""
        
        try:
            # Limitation du nombre de tweets
            if len(data) > max_tweets:
                data = data.head(max_tweets)
                logger.info(f"Données limitées à {max_tweets} tweets")
            
            # Ajout d'un ID unique si absent
            if 'id' not in data.columns:
                data['id'] = range(len(data))
            
            # Ajout de colonnes par défaut si absentes
            if 'author' not in data.columns:
                data['author'] = 'Unknown'
            
            if 'date' not in data.columns:
                data['date'] = datetime.now()
            
            if 'retweet_count' not in data.columns:
                data['retweet_count'] = 0
            
            if 'favorite_count' not in data.columns:
                data['favorite_count'] = 0
            
            # Tri par date si disponible
            if 'date' in data.columns:
                data = data.sort_values('date', ascending=False)
            
            logger.info(f"Données préparées pour l'analyse: {len(data)} tweets")
            
            return data
            
        except Exception as e:
            logger.error(f"Erreur lors de la préparation des données: {str(e)}")
            raise
    
    def extract_metadata(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Extrait les métadonnées des données"""
        
        metadata = {
            "total_tweets": len(data),
            "date_range": None,
            "authors": [],
            "avg_text_length": 0,
            "total_retweets": 0,
            "total_favorites": 0
        }
        
        try:
            # Plage de dates
            if 'date' in data.columns:
                dates = pd.to_datetime(data['date'], errors='coerce').dropna()
                if not dates.empty:
                    metadata["date_range"] = {
                        "start": dates.min().isoformat(),
                        "end": dates.max().isoformat()
                    }
            
            # Auteurs uniques
            if 'author' in data.columns:
                metadata["authors"] = data['author'].unique().tolist()
            
            # Longueur moyenne des textes
            if 'text' in data.columns:
                text_lengths = data['text'].str.len()
                metadata["avg_text_length"] = text_lengths.mean()
            
            # Statistiques d'engagement
            if 'retweet_count' in data.columns:
                metadata["total_retweets"] = data['retweet_count'].sum()
            
            if 'favorite_count' in data.columns:
                metadata["total_favorites"] = data['favorite_count'].sum()
            
        except Exception as e:
            logger.warning(f"Erreur lors de l'extraction des métadonnées: {str(e)}")
        
        return metadata

# Instance globale
data_processor = DataProcessor()

def get_data_processor() -> DataProcessor:
    """Retourne l'instance du processeur de données"""
    return data_processor
