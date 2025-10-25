"""
Moteur d'Analyse LLM Intelligent et Dynamique
==============================================

Moteur d'analyse adaptatif qui s'adapte automatiquement au type de données
et génère des insights personnalisés selon le contenu du dataset.

Fonctionnalités:
- Détection automatique du type de données
- Extraction de KPIs adaptatifs
- Génération d'insights narratifs personnalisés
- Recommandations exploitables
- Synthèse structurée adaptée au contenu

Développé dans le cadre d'un mémoire de master en Data Science
"""

import json
import logging
import re
from typing import Dict, List, Optional, Any, Union
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

class DatasetProfile:
    """Profil d'un dataset avec ses caractéristiques"""
    
    def __init__(self, df: pd.DataFrame, filename: str):
        self.df = df
        self.filename = filename
        self.data_type = self._detect_data_type()
        self.column_types = self._analyze_column_types()
        self.quality_score = self._calculate_quality_score()
        self.size_category = self._categorize_size()
        self.temporal_features = self._detect_temporal_features()
        self.text_features = self._detect_text_features()
        self.numeric_features = self._detect_numeric_features()
    
    def _detect_data_type(self) -> str:
        """Détecte le type de données principal"""
        # Recherche de patterns spécifiques dans les colonnes
        column_names = [col.lower() for col in self.df.columns]
        
        # Détection tweets/social media
        if any(keyword in ' '.join(column_names) for keyword in ['tweet', 'text', 'message', 'post']):
            return "SOCIAL_MEDIA"
        
        # Détection données e-commerce
        if any(keyword in ' '.join(column_names) for keyword in ['product', 'price', 'order', 'customer']):
            return "ECOMMERCE"
        
        # Détection données financières
        if any(keyword in ' '.join(column_names) for keyword in ['amount', 'balance', 'transaction', 'revenue']):
            return "FINANCIAL"
        
        # Détection données IoT/sensors
        if any(keyword in ' '.join(column_names) for keyword in ['sensor', 'measurement', 'value', 'reading']):
            return "IOT_SENSORS"
        
        # Détection données temporelles
        if any(keyword in ' '.join(column_names) for keyword in ['date', 'time', 'timestamp', 'hour']):
            return "TEMPORAL"
        
        return "GENERIC"
    
    def _analyze_column_types(self) -> Dict[str, List[str]]:
        """Analyse les types de colonnes"""
        column_types = {
            'numeric': [],
            'categorical': [],
            'textual': [],
            'temporal': [],
            'boolean': []
        }
        
        for col in self.df.columns:
            if self.df[col].dtype in ['int64', 'float64']:
                column_types['numeric'].append(col)
            elif self.df[col].dtype == 'bool':
                column_types['boolean'].append(col)
            elif self.df[col].dtype == 'object':
                # Test si c'est temporel
                if self._is_temporal_column(col):
                    column_types['temporal'].append(col)
                # Test si c'est textuel
                elif self._is_textual_column(col):
                    column_types['textual'].append(col)
                else:
                    column_types['categorical'].append(col)
        
        return column_types
    
    def _is_temporal_column(self, col: str) -> bool:
        """Détecte si une colonne est temporelle"""
        col_lower = col.lower()
        temporal_keywords = ['date', 'time', 'timestamp', 'created', 'updated', 'hour', 'day', 'month', 'year']
        
        if any(keyword in col_lower for keyword in temporal_keywords):
            return True
        
        # Test sur les valeurs
        try:
            pd.to_datetime(self.df[col].dropna().head(10))
            return True
        except:
            return False
    
    def _is_textual_column(self, col: str) -> bool:
        """Détecte si une colonne est textuelle"""
        if self.df[col].dtype != 'object':
            return False
        
        # Test sur la longueur moyenne des valeurs
        avg_length = self.df[col].astype(str).str.len().mean()
        return avg_length > 20
    
    def _calculate_quality_score(self) -> float:
        """Calcule un score de qualité du dataset"""
        score = 1.0
        
        # Pénalité pour les valeurs manquantes
        null_percentage = (self.df.isnull().sum().sum() / (len(self.df) * len(self.df.columns))) * 100
        score -= min(null_percentage / 100, 0.5)
        
        # Pénalité pour les duplicatas
        duplicate_percentage = (self.df.duplicated().sum() / len(self.df)) * 100
        score -= min(duplicate_percentage / 100, 0.3)
        
        # Bonus pour la diversité des types
        type_diversity = len([t for t in self.column_types.values() if t]) / len(self.column_types)
        score += type_diversity * 0.2
        
        return max(score, 0.0)
    
    def _categorize_size(self) -> str:
        """Catégorise la taille du dataset"""
        row_count = len(self.df)
        
        if row_count < 100:
            return "SMALL"
        elif row_count < 1000:
            return "MEDIUM"
        elif row_count < 10000:
            return "LARGE"
        else:
            return "VERY_LARGE"
    
    def _detect_temporal_features(self) -> Dict[str, Any]:
        """Détecte les caractéristiques temporelles"""
        temporal_cols = self.column_types['temporal']
        
        if not temporal_cols:
            return {'has_temporal': False}
        
        features = {'has_temporal': True, 'columns': temporal_cols}
        
        # Analyse de la première colonne temporelle
        first_temporal = temporal_cols[0]
        try:
            dates = pd.to_datetime(self.df[first_temporal].dropna())
            features['date_range'] = {
                'start': dates.min().isoformat(),
                'end': dates.max().isoformat(),
                'span_days': (dates.max() - dates.min()).days
            }
        except:
            pass
        
        return features
    
    def _detect_text_features(self) -> Dict[str, Any]:
        """Détecte les caractéristiques textuelles"""
        text_cols = self.column_types['textual']
        
        if not text_cols:
            return {'has_text': False}
        
        features = {'has_text': True, 'columns': text_cols}
        
        # Analyse de la première colonne textuelle
        first_text = text_cols[0]
        text_data = self.df[first_text].dropna().astype(str)
        
        features['text_stats'] = {
            'avg_length': text_data.str.len().mean(),
            'max_length': text_data.str.len().max(),
            'min_length': text_data.str.len().min(),
            'total_words': text_data.str.split().str.len().sum()
        }
        
        return features
    
    def _detect_numeric_features(self) -> Dict[str, Any]:
        """Détecte les caractéristiques numériques"""
        numeric_cols = self.column_types['numeric']
        
        if not numeric_cols:
            return {'has_numeric': False}
        
        features = {'has_numeric': True, 'columns': numeric_cols}
        
        # Statistiques sur les colonnes numériques
        numeric_data = self.df[numeric_cols]
        features['stats'] = {
            'mean_values': numeric_data.mean().to_dict(),
            'std_values': numeric_data.std().to_dict(),
            'correlations': numeric_data.corr().to_dict()
        }
        
        return features

class LLMAnalysisEngine:
    """Moteur d'analyse LLM intelligent et adaptatif"""
    
    def __init__(self, llm_provider: str = "fallback", model: str = "llama2"):
        """
        Initialise le moteur d'analyse
        
        Args:
            llm_provider: Fournisseur LLM ("ollama", "openai", "fallback")
            model: Modèle à utiliser
        """
        self.llm_provider = llm_provider
        self.model = model
        self.llm = None
        self.chain = None
        
        # Initialisation du LLM
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialise le LLM selon le fournisseur"""
        try:
            if self.llm_provider == "ollama" and LANGCHAIN_AVAILABLE:
                self.llm = Ollama(model=self.model, temperature=0.3)
                logger.info("LLM Ollama initialisé")
            elif self.llm_provider == "openai" and OPENAI_AVAILABLE:
                self.llm = openai.OpenAI()
                logger.info("LLM OpenAI initialisé")
            else:
                logger.info("Mode fallback activé")
        except Exception as e:
            logger.error(f"Erreur initialisation LLM: {e}")
            self.llm_provider = "fallback"
    
    def analyze_dataset(self, df: pd.DataFrame, filename: str) -> Dict[str, Any]:
        """
        Analyse complète d'un dataset avec insights personnalisés
        
        Args:
            df: DataFrame à analyser
            filename: Nom du fichier
            
        Returns:
            Dict contenant l'analyse complète
        """
        logger.info(f"Analyse du dataset: {filename}")
        
        # Création du profil du dataset
        profile = DatasetProfile(df, filename)
        
        # Calcul des KPIs adaptatifs
        kpis = self._calculate_adaptive_kpis(df, profile)
        
        # Génération d'insights narratifs
        insights = self._generate_narrative_insights(profile, kpis)
        
        # Génération de recommandations
        recommendations = self._generate_recommendations(profile, kpis)
        
        # Détection d'anomalies
        anomalies = self._detect_anomalies(df, profile)
        
        # Synthèse structurée
        synthesis = self._generate_synthesis(profile, kpis, insights, recommendations)
        
        return {
            'filename': filename,
            'timestamp': datetime.now().isoformat(),
            'profile': {
                'data_type': profile.data_type,
                'size_category': profile.size_category,
                'quality_score': profile.quality_score,
                'column_types': profile.column_types,
                'temporal_features': profile.temporal_features,
                'text_features': profile.text_features,
                'numeric_features': profile.numeric_features
            },
            'kpis': kpis,
            'insights': insights,
            'recommendations': recommendations,
            'anomalies': anomalies,
            'synthesis': synthesis
        }
    
    def _calculate_adaptive_kpis(self, df: pd.DataFrame, profile: DatasetProfile) -> Dict[str, Any]:
        """Calcule des KPIs adaptés au type de données"""
        kpis = {}
        
        # KPIs de base
        kpis['basic'] = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 * 1024),
            'null_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
            'duplicate_percentage': (df.duplicated().sum() / len(df)) * 100
        }
        
        # KPIs selon le type de données
        if profile.data_type == "SOCIAL_MEDIA":
            kpis.update(self._calculate_social_media_kpis(df, profile))
        elif profile.data_type == "ECOMMERCE":
            kpis.update(self._calculate_ecommerce_kpis(df, profile))
        elif profile.data_type == "FINANCIAL":
            kpis.update(self._calculate_financial_kpis(df, profile))
        elif profile.data_type == "IOT_SENSORS":
            kpis.update(self._calculate_iot_kpis(df, profile))
        else:
            kpis.update(self._calculate_generic_kpis(df, profile))
        
        return kpis
    
    def _calculate_social_media_kpis(self, df: pd.DataFrame, profile: DatasetProfile) -> Dict[str, Any]:
        """KPIs spécifiques aux réseaux sociaux"""
        kpis = {}
        
        if profile.text_features['has_text']:
            text_col = profile.text_features['columns'][0]
            text_data = df[text_col].dropna().astype(str)
            
            kpis['social_media'] = {
                'avg_text_length': text_data.str.len().mean(),
                'engagement_indicators': self._count_engagement_indicators(text_data),
                'hashtag_count': text_data.str.count('#').sum(),
                'mention_count': text_data.str.count('@').sum(),
                'url_count': text_data.str.count('http').sum()
            }
        
        return kpis
    
    def _calculate_ecommerce_kpis(self, df: pd.DataFrame, profile: DatasetProfile) -> Dict[str, Any]:
        """KPIs spécifiques à l'e-commerce"""
        kpis = {}
        
        if profile.numeric_features['has_numeric']:
            numeric_cols = profile.numeric_features['columns']
            
            # Recherche de colonnes de prix
            price_cols = [col for col in numeric_cols if 'price' in col.lower() or 'amount' in col.lower()]
            
            if price_cols:
                price_data = df[price_cols[0]].dropna()
                kpis['ecommerce'] = {
                    'total_revenue': price_data.sum(),
                    'avg_order_value': price_data.mean(),
                    'max_order_value': price_data.max(),
                    'min_order_value': price_data.min(),
                    'order_count': len(price_data)
                }
        
        return kpis
    
    def _calculate_financial_kpis(self, df: pd.DataFrame, profile: DatasetProfile) -> Dict[str, Any]:
        """KPIs spécifiques aux données financières"""
        kpis = {}
        
        if profile.numeric_features['has_numeric']:
            numeric_cols = profile.numeric_features['columns']
            
            # Analyse des colonnes numériques
            for col in numeric_cols:
                col_data = df[col].dropna()
                kpis[f'financial_{col}'] = {
                    'total': col_data.sum(),
                    'average': col_data.mean(),
                    'volatility': col_data.std(),
                    'trend': self._calculate_trend(col_data)
                }
        
        return kpis
    
    def _calculate_iot_kpis(self, df: pd.DataFrame, profile: DatasetProfile) -> Dict[str, Any]:
        """KPIs spécifiques aux données IoT"""
        kpis = {}
        
        if profile.numeric_features['has_numeric']:
            numeric_cols = profile.numeric_features['columns']
            
            kpis['iot'] = {
                'sensor_count': len(numeric_cols),
                'data_points': len(df),
                'sampling_rate': self._estimate_sampling_rate(df, profile),
                'data_quality': self._assess_iot_data_quality(df, numeric_cols)
            }
        
        return kpis
    
    def _calculate_generic_kpis(self, df: pd.DataFrame, profile: DatasetProfile) -> Dict[str, Any]:
        """KPIs génériques"""
        kpis = {}
        
        # KPIs numériques
        if profile.numeric_features['has_numeric']:
            numeric_data = df[profile.numeric_features['columns']]
            kpis['numeric'] = {
                'correlation_matrix': numeric_data.corr().to_dict(),
                'outlier_count': self._count_outliers(numeric_data),
                'data_range': self._calculate_data_range(numeric_data)
            }
        
        # KPIs catégoriels
        if profile.column_types['categorical']:
            categorical_data = df[profile.column_types['categorical']]
            kpis['categorical'] = {
                'unique_values_per_column': {col: df[col].nunique() for col in profile.column_types['categorical']},
                'most_common_values': {col: df[col].mode().iloc[0] if not df[col].mode().empty else None 
                                     for col in profile.column_types['categorical']}
            }
        
        return kpis
    
    def _generate_narrative_insights(self, profile: DatasetProfile, kpis: Dict[str, Any]) -> str:
        """Génère des insights narratifs personnalisés"""
        
        if self.llm_provider in ["ollama", "openai"] and self.llm:
            return self._generate_llm_insights(profile, kpis)
        else:
            return self._generate_fallback_insights(profile, kpis)
    
    def _generate_llm_insights(self, profile: DatasetProfile, kpis: Dict[str, Any]) -> str:
        """Génère des insights avec LLM"""
        try:
            prompt = self._create_insights_prompt(profile, kpis)
            
            if self.llm_provider == "ollama" and self.chain:
                # Créer une chaîne pour les insights
                template = PromptTemplate(
                    input_variables=["prompt"],
                    template="{prompt}"
                )
                chain = LLMChain(llm=self.llm, prompt=template)
                result = chain.run(prompt=prompt)
                return result
                
            elif self.llm_provider == "openai" and self.llm:
                response = self.llm.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Vous êtes un expert en analyse de données. Générez des insights clairs et actionnables."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=1000
                )
                return response.choices[0].message.content
                
        except Exception as e:
            logger.error(f"Erreur génération insights LLM: {e}")
            return self._generate_fallback_insights(profile, kpis)
    
    def _create_insights_prompt(self, profile: DatasetProfile, kpis: Dict[str, Any]) -> str:
        """Crée le prompt pour la génération d'insights"""
        return f"""
        Analysez ce dataset avec les caractéristiques suivantes:
        
        Type de données: {profile.data_type}
        Taille: {profile.size_category} ({len(profile.df)} lignes, {len(profile.df.columns)} colonnes)
        Score de qualité: {profile.quality_score:.2f}
        
        KPIs principaux:
        - Complétude: {100 - kpis['basic']['null_percentage']:.1f}%
        - Duplicatas: {kpis['basic']['duplicate_percentage']:.1f}%
        
        Générez des insights uniques et actionnables sur ce dataset. Concentrez-vous sur:
        1. La qualité des données et les points d'amélioration
        2. Les patterns intéressants détectés
        3. Les opportunités d'analyse avancée
        4. Les recommandations spécifiques pour ce type de données
        
        Répondez en français, de manière concise et professionnelle.
        """
    
    def _generate_fallback_insights(self, profile: DatasetProfile, kpis: Dict[str, Any]) -> str:
        """Génère des insights de fallback sans LLM"""
        insights = []
        
        # Insight sur la taille
        size_insight = self._generate_size_insight(profile)
        insights.append(size_insight)
        
        # Insight sur la qualité
        quality_insight = self._generate_quality_insight(kpis)
        insights.append(quality_insight)
        
        # Insight sur le type de données
        type_insight = self._generate_type_insight(profile)
        insights.append(type_insight)
        
        # Insight sur les colonnes
        column_insight = self._generate_column_insight(profile)
        insights.append(column_insight)
        
        return "\n\n".join(insights)
    
    def _generate_size_insight(self, profile: DatasetProfile) -> str:
        """Génère un insight sur la taille du dataset"""
        row_count = len(profile.df)
        
        if profile.size_category == "VERY_LARGE":
            return f"Dataset volumineux avec {row_count:,} lignes, offrant une puissance statistique exceptionnelle pour des analyses approfondies."
        elif profile.size_category == "LARGE":
            return f"Dataset de grande taille avec {row_count:,} lignes, idéal pour des analyses robustes et des modélisations avancées."
        elif profile.size_category == "MEDIUM":
            return f"Dataset de taille moyenne avec {row_count:,} lignes, suffisant pour des analyses statistiques significatives."
        else:
            return f"Dataset compact avec {row_count:,} lignes, parfait pour des analyses rapides et des prototypes."
    
    def _generate_quality_insight(self, kpis: Dict[str, Any]) -> str:
        """Génère un insight sur la qualité des données"""
        null_pct = kpis['basic']['null_percentage']
        duplicate_pct = kpis['basic']['duplicate_percentage']
        
        if null_pct < 5 and duplicate_pct < 5:
            return f"Excellente qualité des données avec seulement {null_pct:.1f}% de valeurs manquantes et {duplicate_pct:.1f}% de duplicatas."
        elif null_pct < 20 and duplicate_pct < 20:
            return f"Qualité acceptable des données avec {null_pct:.1f}% de valeurs manquantes et {duplicate_pct:.1f}% de duplicatas. Quelques améliorations possibles."
        else:
            return f"Qualité des données à améliorer avec {null_pct:.1f}% de valeurs manquantes et {duplicate_pct:.1f}% de duplicatas. Nettoyage recommandé."
    
    def _generate_type_insight(self, profile: DatasetProfile) -> str:
        """Génère un insight sur le type de données"""
        type_descriptions = {
            "SOCIAL_MEDIA": "Données de réseaux sociaux, idéales pour l'analyse de sentiment et l'engagement.",
            "ECOMMERCE": "Données e-commerce, parfaites pour l'analyse des ventes et du comportement client.",
            "FINANCIAL": "Données financières, adaptées aux analyses de risque et de performance.",
            "IOT_SENSORS": "Données IoT/capteurs, excellentes pour l'analyse temporelle et la détection d'anomalies.",
            "TEMPORAL": "Données temporelles, idéales pour l'analyse de tendances et de saisonnalité.",
            "GENERIC": "Dataset générique avec un potentiel d'analyse varié selon les colonnes présentes."
        }
        
        return type_descriptions.get(profile.data_type, "Dataset avec des caractéristiques uniques.")
    
    def _generate_column_insight(self, profile: DatasetProfile) -> str:
        """Génère un insight sur les colonnes"""
        column_info = []
        
        if profile.column_types['numeric']:
            column_info.append(f"{len(profile.column_types['numeric'])} colonnes numériques")
        if profile.column_types['textual']:
            column_info.append(f"{len(profile.column_types['textual'])} colonnes textuelles")
        if profile.column_types['categorical']:
            column_info.append(f"{len(profile.column_types['categorical'])} colonnes catégorielles")
        if profile.column_types['temporal']:
            column_info.append(f"{len(profile.column_types['temporal'])} colonnes temporelles")
        
        if column_info:
            return f"Diversité des types de données: {', '.join(column_info)}, permettant des analyses multi-dimensionnelles."
        else:
            return "Structure de données simple, adaptée aux analyses de base."
    
    def _generate_recommendations(self, profile: DatasetProfile, kpis: Dict[str, Any]) -> List[str]:
        """Génère des recommandations exploitables"""
        recommendations = []
        
        # Recommandations sur la qualité
        if kpis['basic']['null_percentage'] > 10:
            recommendations.append("Nettoyer les valeurs manquantes pour améliorer la qualité des analyses")
        
        if kpis['basic']['duplicate_percentage'] > 5:
            recommendations.append("Supprimer les duplicatas pour éviter les biais dans les analyses")
        
        # Recommandations selon le type de données
        if profile.data_type == "SOCIAL_MEDIA":
            recommendations.append("Analyser les sentiments et l'engagement des utilisateurs")
            recommendations.append("Identifier les influenceurs et les tendances")
        
        elif profile.data_type == "ECOMMERCE":
            recommendations.append("Analyser les patterns d'achat et la segmentation client")
            recommendations.append("Optimiser les recommandations produits")
        
        elif profile.data_type == "FINANCIAL":
            recommendations.append("Détecter les anomalies et les risques")
            recommendations.append("Analyser les corrélations entre variables financières")
        
        elif profile.data_type == "IOT_SENSORS":
            recommendations.append("Analyser les tendances temporelles et la saisonnalité")
            recommendations.append("Implémenter la détection d'anomalies en temps réel")
        
        # Recommandations générales
        if profile.column_types['temporal']:
            recommendations.append("Analyser l'évolution temporelle des données")
        
        if profile.column_types['textual']:
            recommendations.append("Extraire des insights des données textuelles avec NLP")
        
        if profile.column_types['numeric'] and len(profile.column_types['numeric']) > 1:
            recommendations.append("Analyser les corrélations entre variables numériques")
        
        return recommendations
    
    def _detect_anomalies(self, df: pd.DataFrame, profile: DatasetProfile) -> Dict[str, Any]:
        """Détecte les anomalies dans le dataset"""
        anomalies = {
            'outliers': [],
            'missing_patterns': [],
            'data_inconsistencies': []
        }
        
        # Détection d'outliers pour les colonnes numériques
        if profile.numeric_features['has_numeric']:
            for col in profile.numeric_features['columns']:
                outliers = self._detect_column_outliers(df[col])
                if outliers:
                    anomalies['outliers'].append({
                        'column': col,
                        'count': len(outliers),
                        'percentage': (len(outliers) / len(df)) * 100
                    })
        
        # Patterns de valeurs manquantes
        missing_data = df.isnull().sum()
        missing_cols = missing_data[missing_data > 0]
        
        if len(missing_cols) > 0:
            anomalies['missing_patterns'] = {
                'columns_affected': len(missing_cols),
                'most_affected_column': missing_cols.idxmax(),
                'missing_percentage': (missing_cols.max() / len(df)) * 100
            }
        
        # Incohérences de données
        inconsistencies = self._detect_data_inconsistencies(df, profile)
        if inconsistencies:
            anomalies['data_inconsistencies'] = inconsistencies
        
        return anomalies
    
    def _generate_synthesis(self, profile: DatasetProfile, kpis: Dict[str, Any], 
                          insights: str, recommendations: List[str]) -> str:
        """Génère une synthèse structurée"""
        
        synthesis_parts = [
            f"## Synthèse de l'Analyse - {profile.filename}",
            f"",
            f"**Type de données:** {profile.data_type}",
            f"**Taille:** {profile.size_category} ({len(profile.df)} lignes, {len(profile.df.columns)} colonnes)",
            f"**Score de qualité:** {profile.quality_score:.2f}/1.0",
            f"",
            f"### Insights Clés",
            insights,
            f"",
            f"### Recommandations Prioritaires",
        ]
        
        for i, rec in enumerate(recommendations[:5], 1):
            synthesis_parts.append(f"{i}. {rec}")
        
        synthesis_parts.extend([
            f"",
            f"### Métriques Principales",
            f"- Complétude: {100 - kpis['basic']['null_percentage']:.1f}%",
            f"- Duplicatas: {kpis['basic']['duplicate_percentage']:.1f}%",
            f"- Taille mémoire: {kpis['basic']['memory_usage_mb']:.1f} MB"
        ])
        
        return "\n".join(synthesis_parts)
    
    # Méthodes utilitaires
    def _count_engagement_indicators(self, text_data: pd.Series) -> Dict[str, int]:
        """Compte les indicateurs d'engagement dans les textes"""
        return {
            'hashtags': text_data.str.count('#').sum(),
            'mentions': text_data.str.count('@').sum(),
            'urls': text_data.str.count('http').sum(),
            'exclamations': text_data.str.count('!').sum()
        }
    
    def _calculate_trend(self, data: pd.Series) -> str:
        """Calcule la tendance d'une série temporelle"""
        if len(data) < 2:
            return "INSUFFICIENT_DATA"
        
        # Régression linéaire simple
        x = np.arange(len(data))
        y = data.values
        slope = np.polyfit(x, y, 1)[0]
        
        if slope > 0.1:
            return "INCREASING"
        elif slope < -0.1:
            return "DECREASING"
        else:
            return "STABLE"
    
    def _estimate_sampling_rate(self, df: pd.DataFrame, profile: DatasetProfile) -> Optional[float]:
        """Estime la fréquence d'échantillonnage pour les données IoT"""
        if not profile.temporal_features['has_temporal']:
            return None
        
        temporal_col = profile.temporal_features['columns'][0]
        try:
            dates = pd.to_datetime(df[temporal_col].dropna())
            if len(dates) > 1:
                time_diffs = dates.diff().dropna()
                avg_interval = time_diffs.mean().total_seconds()
                return 1.0 / avg_interval if avg_interval > 0 else None
        except:
            pass
        
        return None
    
    def _assess_iot_data_quality(self, df: pd.DataFrame, numeric_cols: List[str]) -> Dict[str, Any]:
        """Évalue la qualité des données IoT"""
        quality_metrics = {}
        
        for col in numeric_cols:
            col_data = df[col].dropna()
            if len(col_data) > 0:
                quality_metrics[col] = {
                    'completeness': len(col_data) / len(df),
                    'variance': col_data.var(),
                    'outlier_ratio': self._calculate_outlier_ratio(col_data)
                }
        
        return quality_metrics
    
    def _detect_column_outliers(self, series: pd.Series) -> List[int]:
        """Détecte les outliers dans une colonne"""
        if len(series.dropna()) < 4:
            return []
        
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = series[(series < lower_bound) | (series > upper_bound)]
        return outliers.index.tolist()
    
    def _calculate_outlier_ratio(self, series: pd.Series) -> float:
        """Calcule le ratio d'outliers dans une série"""
        outliers = self._detect_column_outliers(series)
        return len(outliers) / len(series) if len(series) > 0 else 0
    
    def _detect_data_inconsistencies(self, df: pd.DataFrame, profile: DatasetProfile) -> List[str]:
        """Détecte les incohérences dans les données"""
        inconsistencies = []
        
        # Vérification des types de données
        for col in df.columns:
            if df[col].dtype == 'object':
                # Vérifier si une colonne numérique est stockée comme texte
                try:
                    pd.to_numeric(df[col].dropna().head(100))
                    inconsistencies.append(f"Colonne '{col}' semble numérique mais stockée comme texte")
                except:
                    pass
        
        return inconsistencies
    
    def _count_outliers(self, numeric_data: pd.DataFrame) -> int:
        """Compte le nombre total d'outliers dans les données numériques"""
        total_outliers = 0
        for col in numeric_data.columns:
            outliers = self._detect_column_outliers(numeric_data[col])
            total_outliers += len(outliers)
        return total_outliers
    
    def _calculate_data_range(self, numeric_data: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Calcule la plage de données pour les colonnes numériques"""
        ranges = {}
        for col in numeric_data.columns:
            ranges[col] = {
                'min': float(numeric_data[col].min()),
                'max': float(numeric_data[col].max()),
                'range': float(numeric_data[col].max() - numeric_data[col].min())
            }
        return ranges



