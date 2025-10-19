"""
Moteur d'inspection intelligente des données pour analyse contextuelle
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import re
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class IntelligentDataInspector:
    """
    Analyse automatique et contextuelle des données uploadées
    """
    
    def __init__(self):
        self.domain_keywords = {
            'finance': ['prix', 'montant', 'revenu', 'profit', 'coût', 'budget', 'finance', 'argent', 'euro', 'dollar', 'vente', 'achat', 'transaction'],
            'ecommerce': ['produit', 'commande', 'panier', 'client', 'livraison', 'catalogue', 'stock', 'inventaire', 'ecommerce', 'boutique'],
            'marketing': ['campagne', 'email', 'publicité', 'conversion', 'lead', 'prospect', 'marketing', 'promotion', 'offre', 'ciblage'],
            'rh': ['employé', 'salaire', 'département', 'poste', 'recrutement', 'performance', 'formation', 'congé', 'hr', 'ressources'],
            'ventes': ['vendeur', 'territoire', 'quota', 'prospect', 'devis', 'contrat', 'client', 'vente', 'commercial', 'chiffre'],
            'logistique': ['entrepôt', 'stock', 'livraison', 'transport', 'logistique', 'supply', 'inventaire', 'expédition', 'réception'],
            'santé': ['patient', 'médecin', 'diagnostic', 'traitement', 'symptôme', 'médicament', 'hôpital', 'clinique', 'santé', 'médical'],
            'éducation': ['étudiant', 'professeur', 'cours', 'note', 'examen', 'université', 'école', 'formation', 'éducation', 'apprentissage']
        }
        
        self.temporal_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # DD/MM/YYYY
            r'\d{2}-\d{2}-\d{4}',  # DD-MM-YYYY
            r'\d{4}\d{2}\d{2}',    # YYYYMMDD
        ]
        
        self.business_entities = {
            'customer': ['client', 'customer', 'acheteur', 'utilisateur', 'user', 'membre'],
            'product': ['produit', 'product', 'article', 'item', 'service', 'offre'],
            'transaction': ['transaction', 'commande', 'order', 'achat', 'vente', 'paiement'],
            'location': ['ville', 'pays', 'région', 'adresse', 'location', 'zone', 'territoire'],
            'employee': ['employé', 'employee', 'vendeur', 'agent', 'représentant', 'collaborateur']
        }

    def analyze_dataset_context(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyse automatique et contextuelle des données uploadées
        """
        try:
            logger.info(f"Analyse du dataset avec {len(df)} lignes et {len(df.columns)} colonnes")
            
            # Analyse de base
            basic_info = self._analyze_basic_info(df)
            
            # Détection du domaine métier
            domain_analysis = self._detect_business_domain(df)
            
            # Analyse temporelle
            temporal_analysis = self._analyze_temporal_patterns(df)
            
            # Analyse des entités
            entity_analysis = self._analyze_business_entities(df)
            
            # Détection des patterns et anomalies
            pattern_analysis = self._detect_patterns_and_anomalies(df)
            
            # Analyse des corrélations
            correlation_analysis = self._analyze_correlations(df)
            
            # Détection de la granularité
            granularity = self._detect_data_granularity(df, temporal_analysis)
            
            context = {
                'basic_info': basic_info,
                'domain_analysis': domain_analysis,
                'temporal_analysis': temporal_analysis,
                'entity_analysis': entity_analysis,
                'pattern_analysis': pattern_analysis,
                'correlation_analysis': correlation_analysis,
                'granularity': granularity,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Contexte généré avec domaine: {domain_analysis['detected_domain']}")
            return context
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse du contexte: {e}")
            return self._get_fallback_context(df)

    def _analyze_basic_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyse des informations de base du dataset"""
        return {
            'row_count': len(df),
            'column_count': len(df.columns),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'data_types': df.dtypes.to_dict(),
            'null_counts': df.isnull().sum().to_dict(),
            'duplicate_rows': df.duplicated().sum(),
            'columns': list(df.columns)
        }

    def _detect_business_domain(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Détection automatique du domaine métier"""
        domain_scores = {}
        column_text = ' '.join([str(col).lower() for col in df.columns])
        
        # Analyse des noms de colonnes
        for domain, keywords in self.domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in column_text)
            domain_scores[domain] = score
        
        # Analyse du contenu des colonnes textuelles
        text_columns = df.select_dtypes(include=['object']).columns
        for col in text_columns:
            sample_text = ' '.join(df[col].dropna().astype(str).head(100))
            for domain, keywords in self.domain_keywords.items():
                score = sum(1 for keyword in keywords if keyword in sample_text.lower())
                domain_scores[domain] = domain_scores.get(domain, 0) + score * 0.5
        
        # Détermination du domaine principal
        detected_domain = max(domain_scores, key=domain_scores.get) if domain_scores else 'general'
        confidence = domain_scores.get(detected_domain, 0) / max(sum(domain_scores.values()), 1)
        
        return {
            'detected_domain': detected_domain,
            'confidence_score': min(confidence, 1.0),
            'domain_scores': domain_scores,
            'business_context': self._get_business_context(detected_domain)
        }

    def _get_business_context(self, domain: str) -> str:
        """Retourne le contexte métier selon le domaine détecté"""
        contexts = {
            'finance': "Données financières avec focus sur les métriques de performance, rentabilité et analyse des coûts",
            'ecommerce': "Données e-commerce centrées sur les ventes, produits, clients et comportements d'achat",
            'marketing': "Données marketing axées sur les campagnes, conversions, leads et performance publicitaire",
            'rh': "Données RH couvrant les employés, performances, formations et gestion du personnel",
            'ventes': "Données commerciales avec focus sur les ventes, territoires, quotas et performance des vendeurs",
            'logistique': "Données logistiques couvrant la gestion des stocks, livraisons et chaîne d'approvisionnement",
            'santé': "Données médicales avec focus sur les patients, diagnostics, traitements et indicateurs de santé",
            'éducation': "Données éducatives couvrant les étudiants, cours, performances et indicateurs d'apprentissage",
            'general': "Dataset général nécessitant une analyse exploratoire approfondie"
        }
        return contexts.get(domain, contexts['general'])

    def _analyze_temporal_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyse des patterns temporels dans les données"""
        temporal_columns = []
        date_columns = []
        
        for col in df.columns:
            # Vérification des types datetime
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                date_columns.append(col)
                temporal_columns.append(col)
            else:
                # Vérification des patterns de date dans les strings
                sample_values = df[col].dropna().astype(str).head(10)
                for pattern in self.temporal_patterns:
                    if any(re.search(pattern, str(val)) for val in sample_values):
                        temporal_columns.append(col)
                        break
        
        # Analyse de la période temporelle
        time_period = "Non détectée"
        granularity = "Inconnue"
        
        if temporal_columns:
            try:
                # Conversion en datetime pour analyse
                for col in temporal_columns:
                    if col not in date_columns:
                        df_temp = pd.to_datetime(df[col], errors='coerce')
                    else:
                        df_temp = df[col]
                    
                    if not df_temp.isna().all():
                        min_date = df_temp.min()
                        max_date = df_temp.max()
                        time_period = f"{min_date.strftime('%Y-%m-%d')} à {max_date.strftime('%Y-%m-%d')}"
                        
                        # Détection de la granularité
                        if len(df_temp.dropna()) > 1:
                            time_diff = df_temp.dropna().diff().dropna()
                            if len(time_diff) > 0:
                                avg_diff = time_diff.mean()
                                if avg_diff <= timedelta(hours=1):
                                    granularity = "Horaire"
                                elif avg_diff <= timedelta(days=1):
                                    granularity = "Quotidienne"
                                elif avg_diff <= timedelta(days=7):
                                    granularity = "Hebdomadaire"
                                elif avg_diff <= timedelta(days=30):
                                    granularity = "Mensuelle"
                                else:
                                    granularity = "Annuelle"
                        break
            except Exception as e:
                logger.warning(f"Erreur lors de l'analyse temporelle: {e}")
        
        return {
            'temporal_columns': temporal_columns,
            'date_columns': date_columns,
            'time_period': time_period,
            'granularity': granularity,
            'has_temporal_data': len(temporal_columns) > 0
        }

    def _analyze_business_entities(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyse des entités métier dans les données"""
        detected_entities = {}
        
        for entity_type, keywords in self.business_entities.items():
            matching_columns = []
            for col in df.columns:
                col_lower = str(col).lower()
                if any(keyword in col_lower for keyword in keywords):
                    matching_columns.append(col)
            
            if matching_columns:
                detected_entities[entity_type] = {
                    'columns': matching_columns,
                    'confidence': len(matching_columns) / len(df.columns)
                }
        
        return {
            'detected_entities': detected_entities,
            'main_entities': list(detected_entities.keys()),
            'entity_columns': {entity: info['columns'] for entity, info in detected_entities.items()}
        }

    def _detect_patterns_and_anomalies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Détection des patterns et anomalies dans les données"""
        patterns = []
        anomalies = []
        
        # Analyse des colonnes numériques
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if not df[col].isna().all():
                # Détection d'outliers avec IQR
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                if len(outliers) > 0:
                    anomalies.append({
                        'column': col,
                        'type': 'outlier',
                        'count': len(outliers),
                        'percentage': len(outliers) / len(df) * 100,
                        'description': f"{len(outliers)} valeurs aberrantes détectées"
                    })
                
                # Détection de patterns de distribution
                if df[col].std() > 0:
                    cv = df[col].std() / df[col].mean()
                    if cv > 1:
                        patterns.append({
                            'column': col,
                            'type': 'high_variability',
                            'description': f"Variabilité élevée (CV={cv:.2f})"
                        })
                    elif cv < 0.1:
                        patterns.append({
                            'column': col,
                            'type': 'low_variability',
                            'description': f"Variabilité faible (CV={cv:.2f})"
                        })
        
        # Analyse des colonnes catégorielles
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        for col in categorical_cols:
            if not df[col].isna().all():
                value_counts = df[col].value_counts()
                
                # Détection de valeurs dominantes
                if len(value_counts) > 0:
                    most_common_pct = value_counts.iloc[0] / len(df) * 100
                    if most_common_pct > 80:
                        patterns.append({
                            'column': col,
                            'type': 'dominant_value',
                            'description': f"Valeur dominante: {value_counts.index[0]} ({most_common_pct:.1f}%)"
                        })
                
                # Détection de valeurs rares
                rare_values = value_counts[value_counts == 1]
                if len(rare_values) > 0:
                    patterns.append({
                        'column': col,
                        'type': 'rare_values',
                        'description': f"{len(rare_values)} valeurs uniques détectées"
                    })
        
        return {
            'patterns': patterns,
            'anomalies': anomalies,
            'pattern_count': len(patterns),
            'anomaly_count': len(anomalies)
        }

    def _analyze_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyse des corrélations entre variables numériques"""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if len(numeric_df.columns) < 2:
            return {'correlations': [], 'strong_correlations': [], 'correlation_matrix': None}
        
        # Calcul de la matrice de corrélation
        corr_matrix = numeric_df.corr()
        
        # Identification des corrélations fortes
        strong_correlations = []
        correlations = []
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                col1 = corr_matrix.columns[i]
                col2 = corr_matrix.columns[j]
                corr_value = corr_matrix.iloc[i, j]
                
                if not pd.isna(corr_value):
                    correlations.append({
                        'column1': col1,
                        'column2': col2,
                        'correlation': corr_value,
                        'strength': abs(corr_value)
                    })
                    
                    if abs(corr_value) > 0.7:
                        strong_correlations.append({
                            'column1': col1,
                            'column2': col2,
                            'correlation': corr_value,
                            'interpretation': self._interpret_correlation(corr_value)
                        })
        
        return {
            'correlations': correlations,
            'strong_correlations': strong_correlations,
            'correlation_matrix': corr_matrix.to_dict(),
            'max_correlation': max([abs(c['correlation']) for c in correlations]) if correlations else 0
        }

    def _interpret_correlation(self, corr_value: float) -> str:
        """Interprétation de la force de corrélation"""
        abs_corr = abs(corr_value)
        if abs_corr >= 0.9:
            return "Corrélation très forte"
        elif abs_corr >= 0.7:
            return "Corrélation forte"
        elif abs_corr >= 0.5:
            return "Corrélation modérée"
        elif abs_corr >= 0.3:
            return "Corrélation faible"
        else:
            return "Corrélation très faible"

    def _detect_data_granularity(self, df: pd.DataFrame, temporal_analysis: Dict) -> str:
        """Détection de la granularité des données"""
        if temporal_analysis['granularity'] != "Inconnue":
            return temporal_analysis['granularity']
        
        # Analyse basée sur le nombre de lignes et la distribution
        row_count = len(df)
        
        if row_count < 100:
            return "Échantillon"
        elif row_count < 1000:
            return "Granularité fine"
        elif row_count < 10000:
            return "Granularité moyenne"
        else:
            return "Granularité élevée"

    def _get_fallback_context(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Contexte de fallback en cas d'erreur"""
        return {
            'basic_info': {
                'row_count': len(df),
                'column_count': len(df.columns),
                'columns': list(df.columns)
            },
            'domain_analysis': {
                'detected_domain': 'general',
                'confidence_score': 0.5,
                'business_context': 'Dataset nécessitant une analyse exploratoire'
            },
            'temporal_analysis': {
                'has_temporal_data': False,
                'granularity': 'Inconnue'
            },
            'entity_analysis': {
                'detected_entities': {},
                'main_entities': []
            },
            'pattern_analysis': {
                'patterns': [],
                'anomalies': []
            },
            'correlation_analysis': {
                'correlations': [],
                'strong_correlations': []
            },
            'granularity': 'Moyenne',
            'analysis_timestamp': datetime.now().isoformat()
        }

    def generate_analysis_context(self, metadata: Dict[str, Any]) -> str:
        """
        Génère un contexte riche pour le LLM basé sur l'inspection
        """
        context_parts = []
        
        # Informations de base
        basic_info = metadata.get('basic_info', {})
        context_parts.append(f"Dataset de {basic_info.get('row_count', 0)} lignes et {basic_info.get('column_count', 0)} colonnes")
        
        # Domaine métier
        domain_info = metadata.get('domain_analysis', {})
        if domain_info.get('detected_domain'):
            context_parts.append(f"Domaine métier détecté: {domain_info['detected_domain']} (confiance: {domain_info.get('confidence_score', 0):.1%})")
            context_parts.append(f"Contexte: {domain_info.get('business_context', '')}")
        
        # Analyse temporelle
        temporal_info = metadata.get('temporal_analysis', {})
        if temporal_info.get('has_temporal_data'):
            context_parts.append(f"Données temporelles: {temporal_info.get('time_period', 'Période non spécifiée')} ({temporal_info.get('granularity', 'Inconnue')})")
        
        # Entités principales
        entity_info = metadata.get('entity_analysis', {})
        if entity_info.get('main_entities'):
            context_parts.append(f"Entités principales: {', '.join(entity_info['main_entities'])}")
        
        # Patterns et anomalies
        pattern_info = metadata.get('pattern_analysis', {})
        if pattern_info.get('patterns'):
            context_parts.append(f"Patterns détectés: {pattern_info['pattern_count']} patterns identifiés")
        if pattern_info.get('anomalies'):
            context_parts.append(f"Anomalies: {pattern_info['anomaly_count']} anomalies détectées")
        
        return ". ".join(context_parts) + "."

    def detect_analysis_opportunities(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Identifie automatiquement les analyses les plus pertinentes
        """
        opportunities = []
        
        # Analyse temporelle
        temporal_cols = df.select_dtypes(include=['datetime64']).columns
        if len(temporal_cols) > 0:
            opportunities.append({
                'type': 'temporal_analysis',
                'priority': 'high',
                'description': 'Analyse des tendances temporelles',
                'columns': list(temporal_cols)
            })
        
        # Analyse de corrélation
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) >= 2:
            opportunities.append({
                'type': 'correlation_analysis',
                'priority': 'medium',
                'description': 'Analyse des corrélations entre variables numériques',
                'columns': list(numeric_cols)
            })
        
        # Analyse de segmentation
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            opportunities.append({
                'type': 'segmentation_analysis',
                'priority': 'medium',
                'description': 'Analyse de segmentation des données catégorielles',
                'columns': list(categorical_cols)
            })
        
        # Analyse de distribution
        if len(numeric_cols) > 0:
            opportunities.append({
                'type': 'distribution_analysis',
                'priority': 'low',
                'description': 'Analyse des distributions statistiques',
                'columns': list(numeric_cols)
            })
        
        return opportunities
