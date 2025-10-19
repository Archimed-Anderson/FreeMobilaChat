"""
Générateur de prompts dynamiques pour analyse LLM contextuelle
"""

import json
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DynamicPromptGenerator:
    """
    Génération de prompts personnalisés selon le contexte des données
    """
    
    def __init__(self):
        self.analysis_templates = {
            'general': self._get_general_template(),
            'finance': self._get_finance_template(),
            'ecommerce': self._get_ecommerce_template(),
            'marketing': self._get_marketing_template(),
            'rh': self._get_hr_template(),
            'ventes': self._get_sales_template(),
            'logistique': self._get_logistics_template(),
            'santé': self._get_healthcare_template(),
            'éducation': self._get_education_template()
        }
        
        self.visualization_rules = {
            'financial_data': ['line_chart', 'candlestick', 'correlation_heatmap', 'distribution_histogram'],
            'sales_data': ['bar_chart', 'funnel', 'geographic_map', 'time_series', 'scatter_plot'],
            'hr_data': ['demographics_pie', 'performance_scatter', 'tenure_histogram', 'heatmap'],
            'marketing_data': ['conversion_funnel', 'cohort_analysis', 'attribution_chart', 'trend_analysis'],
            'ecommerce_data': ['sales_timeline', 'category_performance', 'customer_segmentation', 'geographic_distribution'],
            'logistics_data': ['inventory_trends', 'delivery_performance', 'supply_chain_flow', 'cost_analysis'],
            'healthcare_data': ['patient_flow', 'treatment_outcomes', 'resource_utilization', 'quality_metrics'],
            'education_data': ['student_performance', 'course_analytics', 'engagement_metrics', 'progress_tracking']
        }

    def create_analysis_prompt(self, df: pd.DataFrame, context: Dict[str, Any], filename: str) -> str:
        """
        Crée un prompt personnalisé basé sur le contexte des données
        """
        try:
            # Sélection du template selon le domaine
            domain = context.get('domain_analysis', {}).get('detected_domain', 'general')
            template = self.analysis_templates.get(domain, self.analysis_templates['general'])
            
            # Préparation des données contextuelles
            prompt_data = self._prepare_prompt_data(df, context, filename)
            
            # Génération du prompt personnalisé
            custom_prompt = template.format(**prompt_data)
            
            logger.info(f"Prompt généré pour domaine: {domain}, fichier: {filename}")
            return custom_prompt
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du prompt: {e}")
            return self._get_fallback_prompt(df, filename)

    def _prepare_prompt_data(self, df: pd.DataFrame, context: Dict[str, Any], filename: str) -> Dict[str, Any]:
        """Prépare les données pour le template de prompt"""
        
        # Informations de base
        basic_info = context.get('basic_info', {})
        domain_info = context.get('domain_analysis', {})
        temporal_info = context.get('temporal_analysis', {})
        entity_info = context.get('entity_analysis', {})
        pattern_info = context.get('pattern_analysis', {})
        correlation_info = context.get('correlation_analysis', {})
        
        # Analyse des colonnes
        column_analysis = self._analyze_columns(df)
        
        # Échantillon de données
        data_sample = self._get_data_sample(df)
        
        # Métriques clés détectées
        key_metrics = self._detect_key_metrics(df, context)
        
        # Opportunités d'analyse
        analysis_opportunities = self._get_analysis_opportunities(context)
        
        return {
            'domain_type': domain_info.get('detected_domain', 'général'),
            'row_count': basic_info.get('row_count', 0),
            'business_domain': domain_info.get('detected_domain', 'général'),
            'time_period': temporal_info.get('time_period', 'Non spécifiée'),
            'main_entities': ', '.join(entity_info.get('main_entities', [])),
            'key_columns': ', '.join(column_analysis.get('important_columns', [])),
            'column_analysis': column_analysis.get('description', ''),
            'data_sample': data_sample,
            'key_metrics': key_metrics,
            'analysis_opportunities': analysis_opportunities,
            'patterns_detected': pattern_info.get('pattern_count', 0),
            'anomalies_detected': pattern_info.get('anomaly_count', 0),
            'strong_correlations': len(correlation_info.get('strong_correlations', [])),
            'filename': filename,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def _analyze_columns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyse détaillée des colonnes du dataset"""
        column_info = []
        important_columns = []
        
        for col in df.columns:
            col_info = {
                'name': col,
                'type': str(df[col].dtype),
                'null_count': df[col].isnull().sum(),
                'null_percentage': (df[col].isnull().sum() / len(df)) * 100,
                'unique_count': df[col].nunique(),
                'unique_percentage': (df[col].nunique() / len(df)) * 100
            }
            
            # Détection des colonnes importantes
            if col_info['null_percentage'] < 50 and col_info['unique_percentage'] > 1:
                important_columns.append(col)
            
            # Analyse spécifique selon le type
            if pd.api.types.is_numeric_dtype(df[col]):
                col_info['min'] = df[col].min()
                col_info['max'] = df[col].max()
                col_info['mean'] = df[col].mean()
                col_info['std'] = df[col].std()
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                col_info['date_range'] = f"{df[col].min()} à {df[col].max()}"
            else:
                col_info['most_common'] = df[col].value_counts().index[0] if len(df[col].value_counts()) > 0 else None
            
            column_info.append(col_info)
        
        return {
            'columns': column_info,
            'important_columns': important_columns,
            'description': f"Dataset avec {len(important_columns)} colonnes importantes sur {len(df.columns)} total"
        }

    def _get_data_sample(self, df: pd.DataFrame) -> str:
        """Génère un échantillon représentatif des données"""
        sample_size = min(5, len(df))
        sample_df = df.head(sample_size)
        
        # Formatage pour le prompt
        sample_text = "Aperçu des données:\n"
        for idx, row in sample_df.iterrows():
            sample_text += f"Ligne {idx + 1}: "
            sample_text += " | ".join([f"{col}={str(val)[:50]}" for col, val in row.items()])
            sample_text += "\n"
        
        return sample_text

    def _detect_key_metrics(self, df: pd.DataFrame, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Détecte les métriques clés selon le domaine"""
        domain = context.get('domain_analysis', {}).get('detected_domain', 'general')
        metrics = []
        
        # Métriques génériques
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        for col in numeric_cols:
            if not df[col].isna().all():
                metrics.append({
                    'name': f"Total {col}",
                    'column': col,
                    'type': 'sum',
                    'value': df[col].sum(),
                    'importance': 0.7
                })
                
                metrics.append({
                    'name': f"Moyenne {col}",
                    'column': col,
                    'type': 'mean',
                    'value': df[col].mean(),
                    'importance': 0.6
                })
        
        # Métriques spécifiques au domaine
        if domain == 'ecommerce':
            metrics.extend(self._get_ecommerce_metrics(df))
        elif domain == 'finance':
            metrics.extend(self._get_finance_metrics(df))
        elif domain == 'marketing':
            metrics.extend(self._get_marketing_metrics(df))
        
        return metrics[:10]  # Limiter à 10 métriques principales

    def _get_ecommerce_metrics(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Métriques spécifiques e-commerce"""
        metrics = []
        
        # Recherche de colonnes de prix/ventes
        price_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['prix', 'price', 'montant', 'amount', 'revenue', 'revenu'])]
        
        for col in price_cols:
            if pd.api.types.is_numeric_dtype(df[col]):
                metrics.append({
                    'name': f"Chiffre d'affaires total",
                    'column': col,
                    'type': 'sum',
                    'value': df[col].sum(),
                    'importance': 0.9
                })
                
                metrics.append({
                    'name': f"Panier moyen",
                    'column': col,
                    'type': 'mean',
                    'value': df[col].mean(),
                    'importance': 0.8
                })
        
        return metrics

    def _get_finance_metrics(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Métriques spécifiques finance"""
        metrics = []
        
        # Recherche de colonnes financières
        financial_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['profit', 'profit', 'coût', 'cost', 'budget', 'budget'])]
        
        for col in financial_cols:
            if pd.api.types.is_numeric_dtype(df[col]):
                metrics.append({
                    'name': f"Total {col}",
                    'column': col,
                    'type': 'sum',
                    'value': df[col].sum(),
                    'importance': 0.9
                })
        
        return metrics

    def _get_marketing_metrics(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Métriques spécifiques marketing"""
        metrics = []
        
        # Recherche de colonnes marketing
        marketing_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in ['conversion', 'conversion', 'click', 'click', 'impression', 'impression'])]
        
        for col in marketing_cols:
            if pd.api.types.is_numeric_dtype(df[col]):
                metrics.append({
                    'name': f"Total {col}",
                    'column': col,
                    'type': 'sum',
                    'value': df[col].sum(),
                    'importance': 0.8
                })
        
        return metrics

    def _get_analysis_opportunities(self, context: Dict[str, Any]) -> List[str]:
        """Identifie les opportunités d'analyse"""
        opportunities = []
        
        # Analyse temporelle
        if context.get('temporal_analysis', {}).get('has_temporal_data'):
            opportunities.append("Analyse des tendances temporelles et saisonnalité")
        
        # Analyse de corrélation
        if context.get('correlation_analysis', {}).get('strong_correlations'):
            opportunities.append("Analyse des corrélations entre variables")
        
        # Analyse de segmentation
        if context.get('entity_analysis', {}).get('main_entities'):
            opportunities.append("Segmentation et analyse des entités principales")
        
        # Analyse d'anomalies
        if context.get('pattern_analysis', {}).get('anomalies'):
            opportunities.append("Détection et analyse des anomalies")
        
        return opportunities

    def _get_general_template(self) -> str:
        """Template général pour l'analyse de données"""
        return """
Tu es un data scientist expert. Analyse ce dataset {domain_type} avec {row_count} entrées.

CONTEXTE DÉTECTÉ :
- Domaine : {business_domain}
- Période : {time_period}
- Entités principales : {main_entities}
- Colonnes clés : {key_columns}
- Patterns détectés : {patterns_detected}
- Anomalies détectées : {anomalies_detected}
- Corrélations fortes : {strong_correlations}

COLONNES DISPONIBLES :
{column_analysis}

APERÇU DONNÉES :
{data_sample}

MÉTRIQUES CLÉS DÉTECTÉES :
{key_metrics}

OPPORTUNITÉS D'ANALYSE :
{analysis_opportunities}

TÂCHES REQUISES :
1. CLASSIFICATION INTELLIGENTE :
   - Identifie le type de données métier
   - Classe les colonnes par importance business
   - Détermine les KPI les plus pertinents

2. ANALYSE APPROFONDIE :
   - Tendances temporelles si applicable
   - Corrélations significatives
   - Outliers et anomalies
   - Segmentation naturelle des données

3. INSIGHTS BUSINESS :
   - 5 insights clés spécifiques à ce dataset
   - Recommandations d'actions
   - Risques identifiés

4. VISUALISATIONS OPTIMALES :
   - Sélectionne les 6 meilleurs graphiques pour ce contexte
   - Justifie chaque choix de visualisation

RÉPONDS EN JSON STRUCTURÉ avec cette structure exacte :
{{
    "classification": {{
        "domain": "...",
        "data_type": "...",
        "business_context": "...",
        "confidence_score": 0.0-1.0
    }},
    "key_metrics": [
        {{"name": "...", "column": "...", "type": "...", "importance": 0.0-1.0, "value": 0.0}}
    ],
    "insights": [
        {{"title": "...", "description": "...", "impact": "high/medium/low", "evidence": "..."}}
    ],
    "visualizations": [
        {{"type": "...", "columns": [...], "title": "...", "rationale": "..."}}
    ],
    "correlations": [
        {{"columns": [...], "strength": 0.0-1.0, "interpretation": "..."}}
    ],
    "anomalies": [
        {{"description": "...", "location": "...", "severity": "..."}}
    ],
    "recommendations": [
        {{"action": "...", "priority": "...", "expected_impact": "..."}}
    ]
}}
"""

    def _get_finance_template(self) -> str:
        """Template spécialisé pour les données financières"""
        return """
Tu es un analyste financier expert. Analyse ce dataset financier avec {row_count} entrées.

CONTEXTE FINANCIER :
- Domaine : {business_domain}
- Période : {time_period}
- Métriques financières : {key_columns}
- Patterns détectés : {patterns_detected}

DONNÉES FINANCIÈRES :
{data_sample}

MÉTRIQUES FINANCIÈRES :
{key_metrics}

FOCUS ANALYSE FINANCIÈRE :
1. RENTABILITÉ : Analyse des marges, coûts, revenus
2. LIQUIDITÉ : Flux de trésorerie, ratios de liquidité
3. EFFICACITÉ : Rotation des actifs, productivité
4. RISQUES : Volatilité, concentration, exposition
5. TENDANCES : Évolution temporelle des indicateurs clés

RÉPONDS EN JSON STRUCTURÉ avec focus financier :
{{
    "classification": {{
        "domain": "Finance",
        "data_type": "Financial Data",
        "business_context": "Analyse financière et performance",
        "confidence_score": 0.0-1.0
    }},
    "financial_metrics": [
        {{"name": "...", "formula": "...", "value": 0.0, "benchmark": "...", "status": "good/warning/critical"}}
    ],
    "profitability_analysis": {{
        "gross_margin": 0.0,
        "net_margin": 0.0,
        "roi": 0.0,
        "trend": "increasing/stable/decreasing"
    }},
    "risk_indicators": [
        {{"risk_type": "...", "level": "low/medium/high", "description": "..."}}
    ],
    "insights": [
        {{"title": "...", "description": "...", "financial_impact": "...", "recommendation": "..."}}
    ],
    "visualizations": [
        {{"type": "financial_dashboard", "charts": [...], "rationale": "..."}}
    ]
}}
"""

    def _get_ecommerce_template(self) -> str:
        """Template spécialisé pour les données e-commerce"""
        return """
Tu es un analyste e-commerce expert. Analyse ce dataset e-commerce avec {row_count} entrées.

CONTEXTE E-COMMERCE :
- Domaine : {business_domain}
- Période : {time_period}
- Entités : {main_entities}
- Métriques e-commerce : {key_columns}

DONNÉES E-COMMERCE :
{data_sample}

MÉTRIQUES E-COMMERCE :
{key_metrics}

FOCUS ANALYSE E-COMMERCE :
1. PERFORMANCE VENTES : CA, panier moyen, conversion
2. COMPORTEMENT CLIENT : Segmentation, fidélité, parcours
3. PERFORMANCE PRODUIT : Top sellers, rotation, marges
4. GÉOGRAPHIE : Performance par région, livraison
5. TEMPOREL : Saisonnalité, tendances, pics

RÉPONDS EN JSON STRUCTURÉ avec focus e-commerce :
{{
    "classification": {{
        "domain": "E-commerce",
        "data_type": "Sales Data",
        "business_context": "Analyse e-commerce et performance commerciale",
        "confidence_score": 0.0-1.0
    }},
    "ecommerce_metrics": {{
        "total_revenue": 0.0,
        "average_order_value": 0.0,
        "conversion_rate": 0.0,
        "customer_acquisition_cost": 0.0,
        "lifetime_value": 0.0
    }},
    "customer_insights": [
        {{"segment": "...", "size": 0, "value": 0.0, "behavior": "..."}}
    ],
    "product_performance": [
        {{"product": "...", "revenue": 0.0, "units_sold": 0, "margin": 0.0}}
    ],
    "insights": [
        {{"title": "...", "description": "...", "business_impact": "...", "action_required": "..."}}
    ],
    "visualizations": [
        {{"type": "ecommerce_dashboard", "charts": [...], "rationale": "..."}}
    ]
}}
"""

    def _get_marketing_template(self) -> str:
        """Template spécialisé pour les données marketing"""
        return """
Tu es un analyste marketing expert. Analyse ce dataset marketing avec {row_count} entrées.

CONTEXTE MARKETING :
- Domaine : {business_domain}
- Période : {time_period}
- Campagnes : {key_columns}
- Métriques marketing : {key_metrics}

DONNÉES MARKETING :
{data_sample}

FOCUS ANALYSE MARKETING :
1. PERFORMANCE CAMPAGNES : ROI, CTR, conversion
2. CANAUX : Performance par canal, attribution
3. AUDIENCE : Segmentation, ciblage, engagement
4. CONTENU : Performance des contenus, formats
5. TEMPOREL : Timing optimal, saisonnalité

RÉPONDS EN JSON STRUCTURÉ avec focus marketing :
{{
    "classification": {{
        "domain": "Marketing",
        "data_type": "Marketing Data",
        "business_context": "Analyse marketing et performance des campagnes",
        "confidence_score": 0.0-1.0
    }},
    "marketing_metrics": {{
        "total_impressions": 0,
        "total_clicks": 0,
        "click_through_rate": 0.0,
        "conversion_rate": 0.0,
        "cost_per_acquisition": 0.0,
        "return_on_ad_spend": 0.0
    }},
    "campaign_performance": [
        {{"campaign": "...", "channel": "...", "roi": 0.0, "status": "..."}}
    ],
    "audience_insights": [
        {{"segment": "...", "size": 0, "engagement": 0.0, "conversion": 0.0}}
    ],
    "insights": [
        {{"title": "...", "description": "...", "marketing_impact": "...", "optimization": "..."}}
    ],
    "visualizations": [
        {{"type": "marketing_dashboard", "charts": [...], "rationale": "..."}}
    ]
}}
"""

    def _get_hr_template(self) -> str:
        """Template spécialisé pour les données RH"""
        return """
Tu es un analyste RH expert. Analyse ce dataset RH avec {row_count} entrées.

CONTEXTE RH :
- Domaine : {business_domain}
- Période : {time_period}
- Employés : {main_entities}
- Métriques RH : {key_columns}

DONNÉES RH :
{data_sample}

FOCUS ANALYSE RH :
1. DÉMOGRAPHIE : Âge, genre, ancienneté, départements
2. PERFORMANCE : Évaluations, objectifs, progression
3. ENGAGEMENT : Satisfaction, turnover, rétention
4. FORMATION : Compétences, développement, certifications
5. DIVERSITÉ : Parité, inclusion, équité

RÉPONDS EN JSON STRUCTURÉ avec focus RH :
{{
    "classification": {{
        "domain": "Human Resources",
        "data_type": "HR Data",
        "business_context": "Analyse RH et gestion du personnel",
        "confidence_score": 0.0-1.0
    }},
    "hr_metrics": {{
        "total_employees": 0,
        "average_tenure": 0.0,
        "turnover_rate": 0.0,
        "satisfaction_score": 0.0,
        "diversity_index": 0.0
    }},
    "demographics": {{
        "age_distribution": {{"18-25": 0, "26-35": 0, "36-45": 0, "46-55": 0, "55+": 0}},
        "gender_distribution": {{"male": 0, "female": 0, "other": 0}},
        "department_distribution": {{}}
    }},
    "performance_insights": [
        {{"metric": "...", "value": 0.0, "trend": "...", "recommendation": "..."}}
    ],
    "insights": [
        {{"title": "...", "description": "...", "hr_impact": "...", "action_required": "..."}}
    ],
    "visualizations": [
        {{"type": "hr_dashboard", "charts": [...], "rationale": "..."}}
    ]
}}
"""

    def _get_sales_template(self) -> str:
        """Template spécialisé pour les données ventes"""
        return """
Tu es un analyste commercial expert. Analyse ce dataset ventes avec {row_count} entrées.

CONTEXTE VENTES :
- Domaine : {business_domain}
- Période : {time_period}
- Vendeurs : {main_entities}
- Métriques ventes : {key_columns}

DONNÉES VENTES :
{data_sample}

FOCUS ANALYSE VENTES :
1. PERFORMANCE VENDEURS : Quotas, réalisations, classements
2. TERRITOIRES : Performance géographique, potentiel
3. PRODUITS : Top sellers, marges, rotation
4. CLIENTS : Segmentation, fidélité, potentiel
5. TEMPOREL : Saisonnalité, objectifs, tendances

RÉPONDS EN JSON STRUCTURÉ avec focus ventes :
{{
    "classification": {{
        "domain": "Sales",
        "data_type": "Sales Data",
        "business_context": "Analyse commerciale et performance des ventes",
        "confidence_score": 0.0-1.0
    }},
    "sales_metrics": {{
        "total_revenue": 0.0,
        "quota_achievement": 0.0,
        "average_deal_size": 0.0,
        "sales_cycle_length": 0.0,
        "win_rate": 0.0
    }},
    "sales_performance": [
        {{"rep": "...", "revenue": 0.0, "quota": 0.0, "achievement": 0.0, "rank": 0}}
    ],
    "territory_analysis": [
        {{"territory": "...", "potential": 0.0, "realized": 0.0, "gap": 0.0}}
    ],
    "insights": [
        {{"title": "...", "description": "...", "sales_impact": "...", "action_required": "..."}}
    ],
    "visualizations": [
        {{"type": "sales_dashboard", "charts": [...], "rationale": "..."}}
    ]
}}
"""

    def _get_logistics_template(self) -> str:
        """Template spécialisé pour les données logistiques"""
        return """
Tu es un analyste logistique expert. Analyse ce dataset logistique avec {row_count} entrées.

CONTEXTE LOGISTIQUE :
- Domaine : {business_domain}
- Période : {time_period}
- Entrepôts : {main_entities}
- Métriques logistiques : {key_columns}

DONNÉES LOGISTIQUES :
{data_sample}

FOCUS ANALYSE LOGISTIQUE :
1. STOCK : Niveaux, rotation, obsolescence
2. LIVRAISONS : Délais, coûts, performance
3. TRANSPORT : Optimisation, coûts, émissions
4. ENTREPÔTS : Utilisation, efficacité, coûts
5. CHAÎNE : Visibilité, risques, opportunités

RÉPONDS EN JSON STRUCTURÉ avec focus logistique :
{{
    "classification": {{
        "domain": "Logistics",
        "data_type": "Supply Chain Data",
        "business_context": "Analyse logistique et chaîne d'approvisionnement",
        "confidence_score": 0.0-1.0
    }},
    "logistics_metrics": {{
        "inventory_turnover": 0.0,
        "delivery_performance": 0.0,
        "cost_per_unit": 0.0,
        "warehouse_utilization": 0.0,
        "on_time_delivery": 0.0
    }},
    "supply_chain_insights": [
        {{"metric": "...", "value": 0.0, "benchmark": 0.0, "status": "..."}}
    ],
    "optimization_opportunities": [
        {{"area": "...", "potential_savings": 0.0, "implementation": "..."}}
    ],
    "insights": [
        {{"title": "...", "description": "...", "logistics_impact": "...", "action_required": "..."}}
    ],
    "visualizations": [
        {{"type": "logistics_dashboard", "charts": [...], "rationale": "..."}}
    ]
}}
"""

    def _get_healthcare_template(self) -> str:
        """Template spécialisé pour les données santé"""
        return """
Tu es un analyste santé expert. Analyse ce dataset médical avec {row_count} entrées.

CONTEXTE SANTÉ :
- Domaine : {business_domain}
- Période : {time_period}
- Patients : {main_entities}
- Métriques médicales : {key_columns}

DONNÉES MÉDICALES :
{data_sample}

FOCUS ANALYSE SANTÉ :
1. PATIENTS : Démographie, pathologies, parcours
2. SOINS : Qualité, efficacité, coûts
3. RESSOURCES : Utilisation, optimisation, planning
4. OUTCOMES : Résultats, satisfaction, sécurité
5. TEMPOREL : Tendances, saisonnalité, épidémies

RÉPONDS EN JSON STRUCTURÉ avec focus santé :
{{
    "classification": {{
        "domain": "Healthcare",
        "data_type": "Medical Data",
        "business_context": "Analyse médicale et performance des soins",
        "confidence_score": 0.0-1.0
    }},
    "healthcare_metrics": {{
        "patient_volume": 0,
        "average_length_stay": 0.0,
        "readmission_rate": 0.0,
        "patient_satisfaction": 0.0,
        "cost_per_patient": 0.0
    }},
    "clinical_insights": [
        {{"condition": "...", "prevalence": 0.0, "outcomes": "...", "trend": "..."}}
    ],
    "resource_utilization": [
        {{"resource": "...", "utilization": 0.0, "efficiency": 0.0, "optimization": "..."}}
    ],
    "insights": [
        {{"title": "...", "description": "...", "clinical_impact": "...", "recommendation": "..."}}
    ],
    "visualizations": [
        {{"type": "healthcare_dashboard", "charts": [...], "rationale": "..."}}
    ]
}}
"""

    def _get_education_template(self) -> str:
        """Template spécialisé pour les données éducation"""
        return """
Tu es un analyste éducation expert. Analyse ce dataset éducatif avec {row_count} entrées.

CONTEXTE ÉDUCATION :
- Domaine : {business_domain}
- Période : {time_period}
- Étudiants : {main_entities}
- Métriques éducatives : {key_columns}

DONNÉES ÉDUCATIVES :
{data_sample}

FOCUS ANALYSE ÉDUCATION :
1. ÉTUDIANTS : Performance, progression, engagement
2. COURS : Popularité, difficulté, satisfaction
3. ENSEIGNANTS : Efficacité, charge, évaluations
4. RÉSULTATS : Diplômes, emploi, satisfaction
5. TEMPOREL : Évolutions, saisonnalité, tendances

RÉPONDS EN JSON STRUCTURÉ avec focus éducation :
{{
    "classification": {{
        "domain": "Education",
        "data_type": "Educational Data",
        "business_context": "Analyse éducative et performance académique",
        "confidence_score": 0.0-1.0
    }},
    "education_metrics": {{
        "student_count": 0,
        "average_grade": 0.0,
        "graduation_rate": 0.0,
        "course_completion": 0.0,
        "satisfaction_score": 0.0
    }},
    "academic_insights": [
        {{"subject": "...", "performance": 0.0, "trend": "...", "recommendation": "..."}}
    ],
    "student_segmentation": [
        {{"segment": "...", "size": 0, "performance": 0.0, "characteristics": "..."}}
    ],
    "insights": [
        {{"title": "...", "description": "...", "educational_impact": "...", "action_required": "..."}}
    ],
    "visualizations": [
        {{"type": "education_dashboard", "charts": [...], "rationale": "..."}}
    ]
}}
"""

    def _get_fallback_prompt(self, df: pd.DataFrame, filename: str) -> str:
        """Prompt de fallback en cas d'erreur"""
        return f"""
Analyse ce dataset avec {len(df)} lignes et {len(df.columns)} colonnes.

Colonnes disponibles : {', '.join(df.columns)}

Échantillon de données :
{df.head(3).to_string()}

Fournis une analyse JSON structurée avec classification, métriques clés, insights et recommandations.
"""

    def get_visualization_rules(self, domain: str) -> List[str]:
        """Retourne les règles de visualisation pour un domaine donné"""
        return self.visualization_rules.get(domain, self.visualization_rules['financial_data'])
