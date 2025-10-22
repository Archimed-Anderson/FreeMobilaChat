"""
Module d'Analyse Intelligente et Dynamique
==========================================

Ce module combine:
- Classification LLM des tweets
- Analyse automatique avec ydata-profiling
- Génération d'insights personnalisés
- Calcul de KPI dynamiques
- Détection d'anomalies

Auteur: Archimed Anderson
Date: Octobre 2024
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import json
import logging
from pathlib import Path
from datetime import datetime
import hashlib

# Imports pour analyse de données
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.decomposition import PCA

# Import conditionnel pour ydata-profiling
try:
    from ydata_profiling import ProfileReport
    PROFILING_AVAILABLE = True
except ImportError:
    PROFILING_AVAILABLE = False

# Import du classificateur de tweets
try:
    from .tweet_classifier import TweetClassifier, ClassificationResult
    CLASSIFIER_AVAILABLE = True
except ImportError:
    CLASSIFIER_AVAILABLE = False

# Logger
logger = logging.getLogger(__name__)


class IntelligentDataInspector:
    """
    Inspecteur intelligent pour analyse automatique et contextuelle des données.
    
    Identifie automatiquement:
    - Types de colonnes (numériques, catégorielles, temporelles, textuelles)
    - Domaine métier (tweets, ventes, clients, etc.)
    - Période temporelle
    - Granularité des données
    - Entités principales
    - Relations entre colonnes
    - Anomalies et patterns
    """
    
    def __init__(self, df: pd.DataFrame, file_name: str = "dataset"):
        """
        Initialise l'inspecteur.
        
        Args:
            df: DataFrame à analyser
            file_name: Nom du fichier pour contexte
        """
        self.df = df
        self.file_name = file_name
        self.context = {}
        self.column_types = {}
        self.kpis = {}
        
    def analyze(self) -> Dict[str, Any]:
        """
        Analyse complète du dataset.
        
        Returns:
            Dictionnaire avec tous les résultats d'analyse
        """
        logger.info(f"Début analyse intelligente de {self.file_name}")
        
        # 1. Identification du domaine métier
        self.context['domain'] = self._identify_domain()
        
        # 2. Classification des colonnes
        self.column_types = self._classify_columns()
        
        # 3. Analyse temporelle
        self.context['temporal'] = self._analyze_temporal_context()
        
        # 4. Identification des entités principales
        self.context['entities'] = self._identify_main_entities()
        
        # 5. Calcul des KPI dynamiques
        self.kpis = self._calculate_dynamic_kpis()
        
        # 6. Détection d'anomalies
        self.context['anomalies'] = self._detect_anomalies()
        
        # 7. Analyse de qualité des données
        self.context['quality'] = self._assess_data_quality()
        
        # 8. Relations entre colonnes
        self.context['relationships'] = self._analyze_relationships()
        
        return {
            'context': self.context,
            'column_types': self.column_types,
            'kpis': self.kpis,
            'shape': {'rows': len(self.df), 'columns': len(self.df.columns)},
            'file_name': self.file_name
        }
    
    def _identify_domain(self) -> str:
        """Identifie le domaine métier à partir des noms de colonnes et du contenu"""
        columns_lower = [col.lower() for col in self.df.columns]
        
        # Détection tweets/social media
        if any(kw in columns_lower for kw in ['tweet', 'author', 'text', 'retweet', 'hashtag']):
            return "social_media_tweets"
        
        # Détection e-commerce/ventes
        if any(kw in columns_lower for kw in ['price', 'product', 'order', 'customer', 'quantity']):
            return "ecommerce_sales"
        
        # Détection finance
        if any(kw in columns_lower for kw in ['amount', 'transaction', 'balance', 'account']):
            return "finance_transactions"
        
        # Détection CRM/clients
        if any(kw in columns_lower for kw in ['customer', 'client', 'contact', 'lead']):
            return "crm_customers"
        
        # Détection logistique
        if any(kw in columns_lower for kw in ['delivery', 'shipment', 'warehouse', 'stock']):
            return "logistics_supply_chain"
        
        return "general_business_data"
    
    def _classify_columns(self) -> Dict[str, List[str]]:
        """Classifie automatiquement chaque colonne par type"""
        classification = {
            'numeric': [],
            'categorical': [],
            'temporal': [],
            'textual': [],
            'identifier': [],
            'boolean': []
        }
        
        for col in self.df.columns:
            dtype = self.df[col].dtype
            unique_ratio = self.df[col].nunique() / len(self.df)
            
            # Identifiants (ID, tweet_id, etc.)
            if 'id' in col.lower() or unique_ratio > 0.95:
                classification['identifier'].append(col)
            
            # Booléens
            elif dtype == bool or self.df[col].nunique() == 2:
                classification['boolean'].append(col)
            
            # Numériques
            elif pd.api.types.is_numeric_dtype(dtype):
                classification['numeric'].append(col)
            
            # Temporels
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                classification['temporal'].append(col)
            elif 'date' in col.lower() or 'time' in col.lower():
                try:
                    pd.to_datetime(self.df[col].dropna().iloc[0])
                    classification['temporal'].append(col)
                except:
                    pass
            
            # Textuels (longueur moyenne > 50 caractères)
            elif dtype == object:
                if self.df[col].dropna().astype(str).str.len().mean() > 50:
                    classification['textual'].append(col)
                else:
                    # Catégorielles (peu de valeurs uniques)
                    if unique_ratio < 0.05 or self.df[col].nunique() < 50:
                        classification['categorical'].append(col)
                    else:
                        classification['textual'].append(col)
        
        return classification
    
    def _analyze_temporal_context(self) -> Dict[str, Any]:
        """Analyse le contexte temporel des données"""
        temporal_cols = self.column_types.get('temporal', [])
        
        if not temporal_cols:
            return {'has_temporal': False}
        
        # Prendre la première colonne temporelle
        col = temporal_cols[0]
        dates = pd.to_datetime(self.df[col], errors='coerce').dropna()
        
        if len(dates) == 0:
            return {'has_temporal': False}
        
        return {
            'has_temporal': True,
            'main_column': col,
            'start_date': dates.min().isoformat(),
            'end_date': dates.max().isoformat(),
            'duration_days': (dates.max() - dates.min()).days,
            'granularity': self._detect_granularity(dates)
        }
    
    def _detect_granularity(self, dates: pd.Series) -> str:
        """Détecte la granularité temporelle (quotidien, hebdomadaire, etc.)"""
        if len(dates) < 2:
            return "unknown"
        
        # Calculer les différences entre dates consécutives
        sorted_dates = dates.sort_values()
        diffs = sorted_dates.diff().dt.total_seconds() / 3600  # en heures
        median_diff = diffs.median()
        
        if median_diff < 1:
            return "hourly_or_realtime"
        elif median_diff < 24:
            return "hourly"
        elif median_diff < 168:  # 7 jours
            return "daily"
        elif median_diff < 730:  # 30 jours
            return "weekly"
        else:
            return "monthly_or_more"
    
    def _identify_main_entities(self) -> List[str]:
        """Identifie les entités principales (colonnes importantes)"""
        entities = []
        
        # Colonnes de texte (contenu principal)
        textual = self.column_types.get('textual', [])
        if textual:
            entities.extend(textual[:2])  # Top 2
        
        # Colonnes catégorielles importantes
        categorical = self.column_types.get('categorical', [])
        for col in categorical:
            if self.df[col].nunique() < 20:  # Pas trop de catégories
                entities.append(col)
        
        # Colonnes numériques avec variance significative
        numeric = self.column_types.get('numeric', [])
        for col in numeric:
            if self.df[col].std() > 0:  # Variance non nulle
                entities.append(col)
        
        return entities[:5]  # Top 5 entités
    
    def _calculate_dynamic_kpis(self) -> Dict[str, Any]:
        """Calcule des KPI dynamiques selon le type de données"""
        kpis = {
            'global': {
                'total_rows': len(self.df),
                'total_columns': len(self.df.columns),
                'memory_usage_mb': self.df.memory_usage(deep=True).sum() / 1024**2,
                'missing_values_pct': (self.df.isnull().sum().sum() / (len(self.df) * len(self.df.columns))) * 100
            },
            'numeric': {},
            'categorical': {},
            'textual': {}
        }
        
        # KPI numériques
        for col in self.column_types.get('numeric', []):
            kpis['numeric'][col] = {
                'mean': float(self.df[col].mean()),
                'median': float(self.df[col].median()),
                'std': float(self.df[col].std()),
                'min': float(self.df[col].min()),
                'max': float(self.df[col].max()),
                'missing_count': int(self.df[col].isnull().sum())
            }
        
        # KPI catégoriels
        for col in self.column_types.get('categorical', []):
            value_counts = self.df[col].value_counts()
            kpis['categorical'][col] = {
                'unique_count': int(self.df[col].nunique()),
                'most_common': str(value_counts.index[0]) if len(value_counts) > 0 else None,
                'most_common_count': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                'missing_count': int(self.df[col].isnull().sum())
            }
        
        # KPI textuels
        for col in self.column_types.get('textual', []):
            texts = self.df[col].dropna().astype(str)
            kpis['textual'][col] = {
                'avg_length': float(texts.str.len().mean()),
                'max_length': int(texts.str.len().max()),
                'min_length': int(texts.str.len().min()),
                'total_texts': int(len(texts))
            }
        
        return kpis
    
    def _detect_anomalies(self) -> Dict[str, Any]:
        """Détecte les anomalies dans les données numériques"""
        anomalies = {}
        numeric_cols = self.column_types.get('numeric', [])
        
        if not numeric_cols:
            return {'has_anomalies': False}
        
        # Utiliser Isolation Forest pour détection d'anomalies
        for col in numeric_cols[:3]:  # Limiter aux 3 premières colonnes numériques
            data = self.df[[col]].dropna()
            
            if len(data) < 10:
                continue
            
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            predictions = iso_forest.fit_predict(data)
            
            anomaly_count = (predictions == -1).sum()
            anomaly_indices = data.index[predictions == -1].tolist()
            
            if anomaly_count > 0:
                anomalies[col] = {
                    'count': int(anomaly_count),
                    'percentage': float((anomaly_count / len(data)) * 100),
                    'sample_indices': anomaly_indices[:5]  # Top 5
                }
        
        return {
            'has_anomalies': len(anomalies) > 0,
            'details': anomalies
        }
    
    def _assess_data_quality(self) -> Dict[str, float]:
        """Évalue la qualité globale des données"""
        # Score de complétude (0-100)
        completeness = ((1 - (self.df.isnull().sum().sum() / (len(self.df) * len(self.df.columns)))) * 100)
        
        # Score d'unicité (pour éviter duplicatas)
        uniqueness = (len(self.df.drop_duplicates()) / len(self.df)) * 100 if len(self.df) > 0 else 100
        
        # Score de consistance (types de données cohérents)
        consistency = 100.0  # Simplifié pour l'instant
        
        # Score global
        overall = (completeness + uniqueness + consistency) / 3
        
        return {
            'completeness': round(completeness, 2),
            'uniqueness': round(uniqueness, 2),
            'consistency': round(consistency, 2),
            'overall': round(overall, 2)
        }
    
    def _analyze_relationships(self) -> Dict[str, Any]:
        """Analyse les relations entre colonnes numériques"""
        numeric_cols = self.column_types.get('numeric', [])
        
        if len(numeric_cols) < 2:
            return {'has_correlations': False}
        
        # Calculer la matrice de corrélation
        corr_matrix = self.df[numeric_cols].corr()
        
        # Trouver les corrélations fortes (> 0.7 ou < -0.7)
        strong_correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:
                    strong_correlations.append({
                        'col1': corr_matrix.columns[i],
                        'col2': corr_matrix.columns[j],
                        'correlation': round(float(corr_value), 3)
                    })
        
        return {
            'has_correlations': len(strong_correlations) > 0,
            'strong_correlations': strong_correlations[:5]  # Top 5
        }


class DynamicPromptGenerator:
    """
    Générateur de prompts dynamiques pour LLM basé sur le contexte des données.
    """
    
    @staticmethod
    def generate_analysis_prompt(inspection_results: Dict[str, Any], df_sample: pd.DataFrame) -> str:
        """
        Génère un prompt personnalisé pour l'analyse LLM.
        
        Args:
            inspection_results: Résultats de l'inspection intelligente
            df_sample: Échantillon du DataFrame (premières lignes)
            
        Returns:
            Prompt formaté pour le LLM
        """
        context = inspection_results['context']
        column_types = inspection_results['column_types']
        kpis = inspection_results['kpis']
        
        prompt = f"""Tu es un expert en analyse de données. Analyse ce dataset et génère des insights uniques et personnalisés.

# CONTEXTE DU DATASET

**Fichier**: {inspection_results['file_name']}
**Domaine**: {context['domain']}
**Taille**: {inspection_results['shape']['rows']} lignes, {inspection_results['shape']['columns']} colonnes

# STRUCTURE DES DONNÉES

**Colonnes numériques**: {', '.join(column_types.get('numeric', []))}
**Colonnes catégorielles**: {', '.join(column_types.get('categorical', []))}
**Colonnes textuelles**: {', '.join(column_types.get('textual', []))}

# CONTEXTE TEMPOREL

{json.dumps(context.get('temporal', {}), indent=2)}

# KPI CLÉS

**Score de qualité global**: {context['quality']['overall']}/100
**Valeurs manquantes**: {kpis['global']['missing_values_pct']:.1f}%
**Anomalies détectées**: {"Oui" if context['anomalies']['has_anomalies'] else "Non"}

# ÉCHANTILLON DE DONNÉES

```
{df_sample.head(3).to_string()}
```

# MISSION

Génère une analyse structurée en JSON avec:

1. **resume_executif**: Résumé de 2-3 phrases sur ce dataset
2. **insights_cles**: Liste de 3-5 insights uniques et actionnables
3. **tendances**: Tendances identifiées dans les données
4. **recommandations**: 2-3 recommandations concrètes
5. **alertes**: Points d'attention ou anomalies importantes
6. **score_pertinence**: Score de pertinence des données (0-100)

**FORMAT DE RÉPONSE**: JSON uniquement, pas de texte supplémentaire.
"""
        
        return prompt


class AdaptiveAnalysisEngine:
    """
    Moteur d'analyse adaptatif qui orchestre l'analyse complète.
    """
    
    def __init__(
        self,
        llm_provider: str = "openai",
        api_key: Optional[str] = None,
        use_profiling: bool = True
    ):
        """
        Initialise le moteur d'analyse.
        
        Args:
            llm_provider: Provider LLM (openai, anthropic, ollama, fallback)
            api_key: Clé API pour le LLM
            use_profiling: Utiliser ydata-profiling si disponible
        """
        self.llm_provider = llm_provider
        self.api_key = api_key
        self.use_profiling = use_profiling and PROFILING_AVAILABLE
        
        # Initialiser le classificateur de tweets si disponible
        if CLASSIFIER_AVAILABLE:
            self.tweet_classifier = TweetClassifier(
                model_name=llm_provider if llm_provider != "fallback" else "fallback",
                api_key=api_key
            )
        else:
            self.tweet_classifier = None
    
    def analyze_file(
        self,
        df: pd.DataFrame,
        file_name: str,
        generate_profiling: bool = False
    ) -> Dict[str, Any]:
        """
        Analyse complète d'un fichier.
        
        Args:
            df: DataFrame à analyser
            file_name: Nom du fichier
            generate_profiling: Générer un rapport ydata-profiling
            
        Returns:
            Résultats complets de l'analyse
        """
        results = {
            'file_name': file_name,
            'timestamp': datetime.now().isoformat(),
            'file_hash': self._compute_file_hash(df)
        }
        
        # 1. Inspection intelligente
        logger.info("Étape 1/4: Inspection intelligente")
        inspector = IntelligentDataInspector(df, file_name)
        inspection = inspector.analyze()
        results['inspection'] = inspection
        
        # 2. Classification des tweets si applicable
        if self.tweet_classifier and inspection['context']['domain'] == 'social_media_tweets':
            logger.info("Étape 2/4: Classification des tweets")
            results['tweet_classification'] = self._classify_tweets(df, inspection)
        else:
            results['tweet_classification'] = None
        
        # 3. Génération d'insights LLM
        logger.info("Étape 3/4: Génération insights LLM")
        results['llm_insights'] = self._generate_llm_insights(df, inspection)
        
        # 4. Profiling ydata (optionnel)
        if generate_profiling and self.use_profiling:
            logger.info("Étape 4/4: Génération rapport profiling")
            results['profiling_report_path'] = self._generate_profiling_report(df, file_name)
        else:
            results['profiling_report_path'] = None
        
        return results
    
    def _compute_file_hash(self, df: pd.DataFrame) -> str:
        """Calcule un hash unique pour le fichier"""
        # Hash basé sur shape et colonnes
        content = f"{df.shape}_{list(df.columns)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _classify_tweets(self, df: pd.DataFrame, inspection: Dict) -> Dict[str, Any]:
        """Classifie les tweets du dataset"""
        textual_cols = inspection['column_types'].get('textual', [])
        
        if not textual_cols or not self.tweet_classifier:
            return None
        
        # Prendre la première colonne textuelle (probablement 'text')
        text_col = textual_cols[0]
        tweets = df[text_col].dropna().tolist()[:100]  # Limiter à 100 pour l'instant
        
        # Classifier
        results = self.tweet_classifier.batch_classify(tweets)
        
        # Agréger les résultats
        classifications = [r.dict() for r in results]
        
        return {
            'total_classified': len(classifications),
            'reclamations_count': sum(1 for c in classifications if c['is_reclamation'] == 'OUI'),
            'avg_confidence': np.mean([c['confidence'] for c in classifications]),
            'sentiment_distribution': pd.Series([c['sentiment'] for c in classifications]).value_counts().to_dict(),
            'theme_distribution': pd.Series([c['theme'] for c in classifications]).value_counts().to_dict(),
            'sample_classifications': classifications[:5]
        }
    
    def _generate_llm_insights(self, df: pd.DataFrame, inspection: Dict) -> Dict[str, Any]:
        """Génère des insights via LLM"""
        # Générer le prompt
        prompt = DynamicPromptGenerator.generate_analysis_prompt(
            inspection,
            df.sample(min(5, len(df)))
        )
        
        # Simuler une réponse LLM (fallback)
        # TODO: Implémenter appel LLM réel
        return {
            'resume_executif': f"Dataset de {inspection['shape']['rows']} entrées dans le domaine {inspection['context']['domain']}",
            'insights_cles': [
                f"Qualité globale des données: {inspection['context']['quality']['overall']}/100",
                f"Taux de complétude: {inspection['context']['quality']['completeness']}%",
                f"Présence d'anomalies: {'Oui' if inspection['context']['anomalies']['has_anomalies'] else 'Non'}"
            ],
            'tendances': ["Analyse en cours"],
            'recommandations': ["Nettoyer les valeurs manquantes", "Vérifier les anomalies détectées"],
            'alertes': [],
            'score_pertinence': inspection['context']['quality']['overall']
        }
    
    def _generate_profiling_report(self, df: pd.DataFrame, file_name: str) -> str:
        """Génère un rapport ydata-profiling"""
        if not PROFILING_AVAILABLE:
            return None
        
        output_dir = Path("backend/data/profiling")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / f"{file_name}_profile.html"
        
        profile = ProfileReport(df, title=f"Profiling Report - {file_name}", explorative=True)
        profile.to_file(output_path)
        
        return str(output_path)


class IntelligentAnalyzer:
    """
    Analyseur intelligent simplifié pour le pipeline d'entraînement.
    """
    
    def __init__(self, llm_provider: str = "fallback", api_key: Optional[str] = None):
        self.llm_provider = llm_provider
        self.api_key = api_key
        self.engine = AdaptiveAnalysisEngine(
            llm_provider=llm_provider,
            api_key=api_key,
            use_profiling=False
        )
    
    def analyze_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyse un DataFrame et retourne les résultats.
        
        Args:
            df: DataFrame à analyser
            
        Returns:
            Résultats de l'analyse
        """
        try:
            # Analyse basique avec l'inspecteur
            inspector = IntelligentDataInspector(df, "dataset")
            inspection = inspector.inspect_dataframe(df)
            
            # Analyse avec le moteur adaptatif
            results = self.engine.analyze_dataframe(df, "dataset")
            
            # Combinaison des résultats
            combined_results = {
                "inspection": inspection,
                "analysis": results,
                "quality_score": inspection.get("quality_score", 85),
                "executive_summary": results.get("executive_summary", "Analyse automatique des données"),
                "insights": results.get("insights", []),
                "recommendations": results.get("recommendations", []),
                "completeness_score": inspection.get("completeness_score", 90),
                "uniqueness_score": inspection.get("uniqueness_score", 95),
                "consistency_score": inspection.get("consistency_score", 88),
                "column_types": inspection.get("column_types", {})
            }
            
            return combined_results
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse: {e}")
            return {
                "error": str(e),
                "quality_score": 50,
                "executive_summary": "Erreur lors de l'analyse",
                "insights": ["Erreur détectée dans l'analyse"],
                "recommendations": ["Vérifier les données d'entrée"],
                "completeness_score": 0,
                "uniqueness_score": 0,
                "consistency_score": 0,
                "column_types": {}
            }


def analyze_dataset(
    file_path: str,
    llm_provider: str = "fallback",
    api_key: Optional[str] = None,
    generate_profiling: bool = False
) -> Dict[str, Any]:
    """
    Fonction utilitaire pour analyser un dataset complet.
    
    Args:
        file_path: Chemin vers le fichier CSV/Excel
        llm_provider: Provider LLM à utiliser
        api_key: Clé API
        generate_profiling: Générer rapport profiling
        
    Returns:
        Résultats complets de l'analyse
        
    Example:
        >>> results = analyze_dataset("data/raw/free_tweet_export.csv")
        >>> print(results['inspection']['context']['domain'])
        social_media_tweets
    """
    # Charger le fichier
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path)
    else:
        raise ValueError("Format non supporté. Utilisez CSV ou Excel.")
    
    # Analyser
    engine = AdaptiveAnalysisEngine(
        llm_provider=llm_provider,
        api_key=api_key,
        use_profiling=generate_profiling
    )
    
    file_name = Path(file_path).stem
    results = engine.analyze_file(df, file_name, generate_profiling)
    
    return results

