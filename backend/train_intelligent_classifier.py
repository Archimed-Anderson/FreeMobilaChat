"""
Pipeline d'Entraînement Intelligent avec Analyse Dynamique
==========================================================

Ce script combine:
- Analyse automatique du dataset avec ydata-profiling
- Classification LLM des tweets
- Génération d'insights personnalisés
- Calcul de KPI dynamiques
- Export du dataset nettoyé et classifié

Auteur: Archimed Anderson
Date: Octobre 2024
"""

import sys
import os
import logging
import argparse
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json

# Ajouter le chemin backend au sys.path
backend_path = Path(__file__).parent
if str(backend_path) not in sys.path:
    sys.path.append(str(backend_path))

from app.services.intelligent_analyzer import (
    IntelligentDataInspector,
    AdaptiveAnalysisEngine,
    analyze_dataset
)
from app.services.tweet_classifier import TweetClassifier

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training_intelligent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie le dataset de manière intelligente.
    
    Args:
        df: DataFrame brut
        
    Returns:
        DataFrame nettoyé
    """
    logger.info(f"Nettoyage du dataset: {len(df)} lignes initiales")
    
    # Supprimer duplicatas exacts
    df = df.drop_duplicates()
    logger.info(f"Après suppression duplicatas: {len(df)} lignes")
    
    # Supprimer lignes avec toutes valeurs nulles
    df = df.dropna(how='all')
    logger.info(f"Après suppression lignes vides: {len(df)} lignes")
    
    # Pour les tweets, nettoyer la colonne text
    if 'text' in df.columns:
        # Supprimer lignes avec text vide
        df = df[df['text'].notna()]
        df = df[df['text'].astype(str).str.strip() != '']
        logger.info(f"Après nettoyage colonne text: {len(df)} lignes")
        
        # Nettoyer les RT
        df['text_clean'] = df['text'].apply(lambda x: x[3:].strip() if str(x).startswith('RT ') else str(x))
    
    logger.info(f"Dataset nettoyé: {len(df)} lignes finales")
    return df


def enrich_with_classification(
    df: pd.DataFrame,
    classifier: TweetClassifier,
    text_column: str = 'text_clean'
) -> pd.DataFrame:
    """
    Enrichit le dataset avec les classifications LLM.
    
    Args:
        df: DataFrame à enrichir
        classifier: Classificateur initialisé
        text_column: Colonne contenant le texte
        
    Returns:
        DataFrame enrichi avec colonnes de classification
    """
    logger.info("Début enrichissement avec classification LLM...")
    
    if text_column not in df.columns:
        logger.warning(f"Colonne {text_column} non trouvée, utilisation de 'text'")
        text_column = 'text'
    
    tweets = df[text_column].tolist()
    tweet_ids = df['tweet_id'].tolist() if 'tweet_id' in df.columns else None
    
    # Classifier tous les tweets
    results = classifier.batch_classify(tweets, tweet_ids)
    
    # Créer DataFrame des résultats
    results_df = pd.DataFrame([r.dict() for r in results])
    
    # Fusionner avec le DataFrame original
    df_enriched = pd.concat([
        df.reset_index(drop=True),
        results_df[['is_reclamation', 'theme', 'sentiment', 'urgence', 'type_incident', 'confidence', 'justification']]
    ], axis=1)
    
    logger.info(f"Dataset enrichi: {len(df_enriched)} lignes avec {len(df_enriched.columns)} colonnes")
    
    return df_enriched


def generate_analysis_report(
    analysis_results: dict,
    df_classified: pd.DataFrame,
    output_dir: Path
) -> str:
    """
    Génère un rapport d'analyse complet.
    
    Args:
        analysis_results: Résultats de l'analyse intelligente
        df_classified: DataFrame classifié
        output_dir: Répertoire de sortie
        
    Returns:
        Chemin vers le rapport généré
    """
    report_path = output_dir / 'rapport_analyse_intelligente.md'
    
    inspection = analysis_results['inspection']
    tweet_class = analysis_results.get('tweet_classification')
    llm_insights = analysis_results.get('llm_insights', {})
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Rapport d'Analyse Intelligente - FreeMobilaChat\n\n")
        f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Fichier**: {analysis_results['file_name']}\n\n")
        f.write("---\n\n")
        
        # Vue d'ensemble
        f.write("## 1. Vue d'Ensemble\n\n")
        f.write(f"- **Domaine identifié**: {inspection['context']['domain']}\n")
        f.write(f"- **Nombre de lignes**: {inspection['shape']['rows']}\n")
        f.write(f"- **Nombre de colonnes**: {inspection['shape']['columns']}\n")
        f.write(f"- **Score de qualité global**: {inspection['context']['quality']['overall']}/100\n\n")
        
        # Résumé exécutif LLM
        f.write("## 2. Résumé Exécutif (Généré par IA)\n\n")
        f.write(f"{llm_insights.get('resume_executif', 'N/A')}\n\n")
        
        # Structure des données
        f.write("## 3. Structure des Données\n\n")
        f.write("### Types de Colonnes\n\n")
        for col_type, cols in inspection['column_types'].items():
            if cols:
                f.write(f"- **{col_type.capitalize()}**: {', '.join(cols)}\n")
        f.write("\n")
        
        # Contexte temporel
        if inspection['context']['temporal']['has_temporal']:
            f.write("### Contexte Temporel\n\n")
            temp = inspection['context']['temporal']
            f.write(f"- **Période**: {temp['start_date']} à {temp['end_date']}\n")
            f.write(f"- **Durée**: {temp['duration_days']} jours\n")
            f.write(f"- **Granularité**: {temp['granularity']}\n\n")
        
        # KPI dynamiques
        f.write("## 4. KPI Dynamiques\n\n")
        kpis = inspection['kpis']
        
        f.write(f"### KPI Globaux\n\n")
        f.write(f"- **Taille mémoire**: {kpis['global']['memory_usage_mb']:.2f} MB\n")
        f.write(f"- **Valeurs manquantes**: {kpis['global']['missing_values_pct']:.2f}%\n\n")
        
        if kpis['numeric']:
            f.write(f"### KPI Numériques (échantillon)\n\n")
            for col, stats in list(kpis['numeric'].items())[:3]:
                f.write(f"**{col}**:\n")
                f.write(f"- Moyenne: {stats['mean']:.2f}\n")
                f.write(f"- Min/Max: {stats['min']:.2f} / {stats['max']:.2f}\n")
                f.write(f"- Écart-type: {stats['std']:.2f}\n\n")
        
        # Classification des tweets
        if tweet_class:
            f.write("## 5. Résultats de Classification\n\n")
            f.write(f"- **Tweets classifiés**: {tweet_class['total_classified']}\n")
            f.write(f"- **Réclamations détectées**: {tweet_class['reclamations_count']} ")
            f.write(f"({(tweet_class['reclamations_count']/tweet_class['total_classified']*100):.1f}%)\n")
            f.write(f"- **Confiance moyenne**: {tweet_class['avg_confidence']:.2f}\n\n")
            
            f.write("### Distribution des Thèmes\n\n")
            for theme, count in tweet_class['theme_distribution'].items():
                f.write(f"- {theme}: {count}\n")
            f.write("\n")
            
            f.write("### Distribution des Sentiments\n\n")
            for sentiment, count in tweet_class['sentiment_distribution'].items():
                f.write(f"- {sentiment}: {count}\n")
            f.write("\n")
        
        # Insights IA
        f.write("## 6. Insights Clés (Générés par IA)\n\n")
        for i, insight in enumerate(llm_insights.get('insights_cles', []), 1):
            f.write(f"{i}. {insight}\n")
        f.write("\n")
        
        # Recommandations
        f.write("## 7. Recommandations\n\n")
        for i, reco in enumerate(llm_insights.get('recommandations', []), 1):
            f.write(f"{i}. {reco}\n")
        f.write("\n")
        
        # Qualité des données
        f.write("## 8. Qualité des Données\n\n")
        quality = inspection['context']['quality']
        f.write(f"- **Complétude**: {quality['completeness']}/100\n")
        f.write(f"- **Unicité**: {quality['uniqueness']}/100\n")
        f.write(f"- **Consistance**: {quality['consistency']}/100\n")
        f.write(f"- **Score global**: {quality['overall']}/100\n\n")
        
        # Anomalies
        if inspection['context']['anomalies']['has_anomalies']:
            f.write("## 9. Anomalies Détectées\n\n")
            for col, details in inspection['context']['anomalies']['details'].items():
                f.write(f"**{col}**: {details['count']} anomalies ({details['percentage']:.1f}%)\n")
            f.write("\n")
        
        # Statistiques du dataset final
        f.write("## 10. Statistiques du Dataset Final\n\n")
        if 'is_reclamation' in df_classified.columns:
            reclamations = (df_classified['is_reclamation'] == 'OUI').sum()
            f.write(f"- **Total de tweets**: {len(df_classified)}\n")
            f.write(f"- **Réclamations**: {reclamations} ({(reclamations/len(df_classified)*100):.1f}%)\n")
            
            if 'sentiment' in df_classified.columns:
                sentiment_counts = df_classified['sentiment'].value_counts()
                f.write(f"- **Sentiment Négatif**: {sentiment_counts.get('NEGATIF', 0)}\n")
                f.write(f"- **Sentiment Neutre**: {sentiment_counts.get('NEUTRE', 0)}\n")
                f.write(f"- **Sentiment Positif**: {sentiment_counts.get('POSITIF', 0)}\n")
        
        f.write("\n---\n\n")
        f.write("*Rapport généré automatiquement par le pipeline d'analyse intelligente*\n")
    
    logger.info(f"Rapport généré: {report_path}")
    return str(report_path)


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description='Entraînement intelligent avec analyse dynamique'
    )
    parser.add_argument(
        '--data',
        type=str,
        default='../data/raw/free_tweet_export.csv',
        help='Chemin vers le fichier de données brutes'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/intelligent_training',
        help='Répertoire de sortie'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='fallback',
        help='Modèle LLM (gpt-4, claude-3, fallback)'
    )
    parser.add_argument(
        '--api-key',
        type=str,
        default=None,
        help='Clé API pour le LLM'
    )
    parser.add_argument(
        '--n-samples',
        type=int,
        default=0,
        help='Nombre d\'échantillons (0=tous)'
    )
    parser.add_argument(
        '--generate-profiling',
        action='store_true',
        help='Générer rapport ydata-profiling'
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 70)
    logger.info("PIPELINE D'ENTRAÎNEMENT INTELLIGENT")
    logger.info("=" * 70)
    
    try:
        # Créer le répertoire de sortie
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Étape 1: Analyse intelligente du dataset
        logger.info("\n[ÉTAPE 1/5] Analyse intelligente du dataset")
        analysis_results = analyze_dataset(
            file_path=args.data,
            llm_provider=args.model,
            api_key=args.api_key or os.getenv('OPENAI_API_KEY'),
            generate_profiling=args.generate_profiling
        )
        
        # Sauvegarder les résultats d'analyse
        analysis_path = output_dir / 'analysis_results.json'
        with open(analysis_path, 'w', encoding='utf-8') as f:
            # Convertir les types numpy en types Python pour JSON
            def convert_numpy(obj):
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                return obj
            
            json.dump(analysis_results, f, indent=2, ensure_ascii=False, default=convert_numpy)
        logger.info(f"Résultats d'analyse sauvegardés: {analysis_path}")
        
        # Étape 2: Chargement et nettoyage
        logger.info("\n[ÉTAPE 2/5] Chargement et nettoyage du dataset")
        if args.data.endswith('.csv'):
            df = pd.read_csv(args.data)
        else:
            df = pd.read_excel(args.data)
        
        df_clean = clean_dataset(df)
        
        # Échantillonner si demandé
        if args.n_samples > 0 and args.n_samples < len(df_clean):
            df_clean = df_clean.sample(n=args.n_samples, random_state=42)
            logger.info(f"Échantillonnage: {len(df_clean)} lignes")
        
        # Étape 3: Classification LLM
        logger.info("\n[ÉTAPE 3/5] Classification LLM des tweets")
        classifier = TweetClassifier(
            model_name=args.model,
            api_key=args.api_key or os.getenv('OPENAI_API_KEY')
        )
        
        df_classified = enrich_with_classification(df_clean, classifier)
        
        # Étape 4: Export du dataset enrichi
        logger.info("\n[ÉTAPE 4/5] Export du dataset enrichi")
        output_csv = output_dir / 'dataset_classified_enriched.csv'
        df_classified.to_csv(output_csv, index=False, encoding='utf-8')
        logger.info(f"Dataset enrichi exporté: {output_csv}")
        
        # Export Excel pour meilleure lisibilité
        output_excel = output_dir / 'dataset_classified_enriched.xlsx'
        df_classified.to_excel(output_excel, index=False)
        logger.info(f"Dataset enrichi exporté (Excel): {output_excel}")
        
        # Étape 5: Génération du rapport
        logger.info("\n[ÉTAPE 5/5] Génération du rapport d'analyse")
        report_path = generate_analysis_report(analysis_results, df_classified, output_dir)
        
        # Résumé final
        logger.info("\n" + "=" * 70)
        logger.info("✅ ENTRAÎNEMENT INTELLIGENT TERMINÉ AVEC SUCCÈS !")
        logger.info("=" * 70)
        logger.info(f"\n📁 Outputs:")
        logger.info(f"   - Dataset enrichi (CSV): {output_csv}")
        logger.info(f"   - Dataset enrichi (Excel): {output_excel}")
        logger.info(f"   - Analyse JSON: {analysis_path}")
        logger.info(f"   - Rapport: {report_path}")
        
        if args.generate_profiling and analysis_results.get('profiling_report_path'):
            logger.info(f"   - Profiling: {analysis_results['profiling_report_path']}")
        
        logger.info(f"\n📊 Statistiques:")
        logger.info(f"   - Tweets traités: {len(df_classified)}")
        
        if 'is_reclamation' in df_classified.columns:
            reclamations = (df_classified['is_reclamation'] == 'OUI').sum()
            logger.info(f"   - Réclamations: {reclamations} ({(reclamations/len(df_classified)*100):.1f}%)")
        
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"\n❌ ERREUR: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

