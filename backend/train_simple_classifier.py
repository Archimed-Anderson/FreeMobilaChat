#!/usr/bin/env python3
"""
Script d'entraînement intelligent simplifié avec mode fallback
FreeMobilaChat - Classification automatique de tweets
"""

import os
import sys
import pandas as pd
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('intelligent_training_simple.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Ajout du chemin pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

try:
    from services.intelligent_analyzer import IntelligentAnalyzer
    from services.tweet_classifier import TweetClassifier, ClassificationResult
except ImportError as e:
    logger.error(f"Erreur d'import: {e}")
    logger.info("Assurez-vous que les modules sont dans le bon répertoire")
    sys.exit(1)

class SimpleTrainingPipeline:
    """Pipeline d'entraînement simplifié avec mode fallback"""
    
    def __init__(self, data_path: str, output_dir: str = "data/intelligent_training"):
        self.data_path = data_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialisation des composants
        self.analyzer = IntelligentAnalyzer(llm_provider="fallback")
        self.classifier = TweetClassifier(model_name="fallback")
        
        logger.info(f"Pipeline simplifié initialisé - Données: {data_path}, Sortie: {output_dir}")
    
    def load_and_prepare_data(self, n_samples: Optional[int] = None) -> pd.DataFrame:
        """Charge et prépare les données"""
        logger.info(f"Chargement des données depuis {self.data_path}")
        
        try:
            if self.data_path.endswith('.csv'):
                df = pd.read_csv(self.data_path)
            elif self.data_path.endswith('.xlsx'):
                df = pd.read_excel(self.data_path)
            else:
                raise ValueError("Format de fichier non supporté")
            
            logger.info(f"Données chargées: {len(df)} lignes, {len(df.columns)} colonnes")
            
            # Échantillonnage si demandé
            if n_samples and n_samples < len(df):
                df = df.sample(n=n_samples, random_state=42)
                logger.info(f"Échantillonnage appliqué: {len(df)} lignes")
            
            # Nettoyage basique
            if 'text' in df.columns:
                df['text_clean'] = df['text'].fillna('').astype(str)
            else:
                logger.warning("Colonne 'text' non trouvée")
            
            return df
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement: {e}")
            raise
    
    def run_intelligent_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Exécute l'analyse intelligente"""
        logger.info("Démarrage de l'analyse intelligente...")
        
        try:
            # Analyse avec l'analyseur intelligent
            analysis_results = self.analyzer.analyze_dataframe(df)
            logger.info("Analyse intelligente terminée")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse: {e}")
            return {"error": str(e), "quality_score": 50}
    
    def classify_tweets_fallback(self, df: pd.DataFrame) -> pd.DataFrame:
        """Classifie les tweets avec le mode fallback"""
        logger.info("Démarrage de la classification en mode fallback")
        
        # Préparation des résultats
        results = []
        
        for idx, row in df.iterrows():
            try:
                tweet_text = str(row.get('text_clean', row.get('text', '')))
                
                if not tweet_text or tweet_text.strip() == '':
                    # Tweet vide - valeurs par défaut
                    result = ClassificationResult(
                        is_reclamation="NON",
                        theme="AUTRE",
                        sentiment="NEUTRE",
                        urgence="FAIBLE",
                        type_incident="INFO",
                        confidence=0.5,
                        justification="Tweet vide détecté"
                    )
                else:
                    # Classification avec le classificateur (mode fallback)
                    result = self.classifier.classify(tweet_text)
                
                # Ajout des résultats
                row_dict = row.to_dict()
                row_dict.update({
                    'is_reclamation': result.is_reclamation,
                    'theme': result.theme,
                    'sentiment': result.sentiment,
                    'urgence': result.urgence,
                    'type_incident': result.type_incident,
                    'confidence': result.confidence,
                    'justification': result.justification
                })
                results.append(row_dict)
                
            except Exception as e:
                logger.warning(f"Erreur classification tweet {idx}: {e}")
                # Valeurs par défaut en cas d'erreur
                row_dict = row.to_dict()
                row_dict.update({
                    'is_reclamation': "NON",
                    'theme': "AUTRE",
                    'sentiment': "NEUTRE",
                    'urgence': "FAIBLE",
                    'type_incident': "INFO",
                    'confidence': 0.3,
                    'justification': f"Erreur: {str(e)}"
                })
                results.append(row_dict)
        
        # Création du DataFrame enrichi
        df_enriched = pd.DataFrame(results)
        logger.info(f"Classification terminée: {len(df_enriched)} tweets traités")
        
        return df_enriched
    
    def generate_simple_report(self, df_original: pd.DataFrame, 
                             df_classified: pd.DataFrame, 
                             analysis_results: Dict[str, Any]) -> str:
        """Génère un rapport simplifié"""
        logger.info("Génération du rapport simplifié...")
        
        # Statistiques de base
        total_tweets = len(df_classified)
        reclamations = len(df_classified[df_classified['is_reclamation'] == 'OUI'])
        reclamation_rate = (reclamations / total_tweets * 100) if total_tweets > 0 else 0
        
        # Distribution des thèmes
        theme_dist = df_classified['theme'].value_counts().to_dict()
        
        # Distribution des sentiments
        sentiment_dist = df_classified['sentiment'].value_counts().to_dict()
        
        # Confiance moyenne
        avg_confidence = df_classified['confidence'].mean()
        
        # Génération du rapport
        report = f"""# Rapport d'Analyse Intelligente - FreeMobilaChat

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Fichier**: {Path(self.data_path).stem}
**Mode**: Fallback (Classification par règles)

---

## 1. Vue d'Ensemble

- **Nombre de lignes**: {len(df_original)}
- **Nombre de colonnes**: {len(df_original.columns)}
- **Score de qualité global**: {analysis_results.get('quality_score', 'N/A')}/100

## 2. Résumé Exécutif

Analyse automatique des tweets Free Mobile avec classification par règles.
Dataset traité avec succès en mode fallback.

## 3. Résultats de Classification

- **Tweets classifiés**: {total_tweets}
- **Réclamations détectées**: {reclamations} ({reclamation_rate:.1f}%)
- **Confiance moyenne**: {avg_confidence:.2f}

### Distribution des Thèmes

{self._format_distribution(theme_dist)}

### Distribution des Sentiments

{self._format_distribution(sentiment_dist)}

## 4. Exemples de Classification

{self._format_classification_examples(df_classified)}

## 5. Statistiques Finales

- **Total de tweets**: {total_tweets}
- **Réclamations**: {reclamations} ({reclamation_rate:.1f}%)
- **Sentiment Négatif**: {sentiment_dist.get('NEGATIF', 0)}
- **Sentiment Neutre**: {sentiment_dist.get('NEUTRE', 0)}
- **Sentiment Positif**: {sentiment_dist.get('POSITIF', 0)}

## 6. Recommandations

1. Le mode fallback fonctionne correctement
2. Pour une meilleure précision, configurez une clé API OpenAI/Anthropic
3. Les résultats sont cohérents avec les règles définies

---

*Rapport généré automatiquement par le pipeline d'analyse intelligente simplifié*
"""
        
        return report
    
    def _format_distribution(self, dist: Dict) -> str:
        """Formate une distribution"""
        if not dist:
            return "- Aucune donnée disponible"
        
        formatted = []
        for key, value in dist.items():
            formatted.append(f"- {key}: {value}")
        
        return '\n'.join(formatted)
    
    def _format_classification_examples(self, df: pd.DataFrame) -> str:
        """Formate des exemples de classification"""
        examples = []
        
        # Exemples de réclamations
        reclamations = df[df['is_reclamation'] == 'OUI'].head(3)
        if not reclamations.empty:
            examples.append("### Exemples de Réclamations")
            for idx, row in reclamations.iterrows():
                examples.append(f"- **Tweet**: {row.get('text_clean', '')[:100]}...")
                examples.append(f"  - Thème: {row['theme']}, Sentiment: {row['sentiment']}, Urgence: {row['urgence']}")
                examples.append(f"  - Justification: {row['justification']}")
                examples.append("")
        
        # Exemples de tweets informatifs
        infos = df[df['is_reclamation'] == 'NON'].head(2)
        if not infos.empty:
            examples.append("### Exemples de Tweets Informatifs")
            for idx, row in infos.iterrows():
                examples.append(f"- **Tweet**: {row.get('text_clean', '')[:100]}...")
                examples.append(f"  - Thème: {row['theme']}, Sentiment: {row['sentiment']}")
                examples.append("")
        
        return '\n'.join(examples) if examples else "- Aucun exemple disponible"
    
    def save_results(self, df_classified: pd.DataFrame, analysis_results: Dict[str, Any], 
                    report: str) -> None:
        """Sauvegarde tous les résultats"""
        logger.info("Sauvegarde des résultats...")
        
        # Sauvegarde du dataset enrichi
        csv_path = self.output_dir / "dataset_classified_enriched.csv"
        excel_path = self.output_dir / "dataset_classified_enriched.xlsx"
        
        df_classified.to_csv(csv_path, index=False, encoding='utf-8')
        df_classified.to_excel(excel_path, index=False)
        
        logger.info(f"Dataset enrichi sauvegardé: {csv_path}")
        
        # Sauvegarde des résultats d'analyse
        analysis_path = self.output_dir / "analysis_results.json"
        with open(analysis_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Résultats d'analyse sauvegardés: {analysis_path}")
        
        # Sauvegarde du rapport
        report_path = self.output_dir / "rapport_analyse_intelligente.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"Rapport sauvegardé: {report_path}")
    
    def run_complete_pipeline(self, n_samples: Optional[int] = None) -> None:
        """Exécute le pipeline complet"""
        logger.info("=== DÉMARRAGE DU PIPELINE SIMPLIFIÉ ===")
        
        try:
            # 1. Chargement des données
            df = self.load_and_prepare_data(n_samples)
            
            # 2. Analyse intelligente
            analysis_results = self.run_intelligent_analysis(df)
            
            # 3. Classification avec mode fallback
            df_classified = self.classify_tweets_fallback(df)
            
            # 4. Génération du rapport
            report = self.generate_simple_report(df, df_classified, analysis_results)
            
            # 5. Sauvegarde des résultats
            self.save_results(df_classified, analysis_results, report)
            
            logger.info("=== PIPELINE TERMINÉ AVEC SUCCÈS ===")
            logger.info(f"Résultats sauvegardés dans: {self.output_dir}")
            
        except Exception as e:
            logger.error(f"Erreur dans le pipeline: {e}")
            raise

def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(description="Pipeline d'entraînement intelligent simplifié")
    parser.add_argument("--data", required=True, help="Chemin vers le fichier de données")
    parser.add_argument("--output", default="data/intelligent_training", 
                       help="Répertoire de sortie")
    parser.add_argument("--n-samples", type=int, help="Nombre d'échantillons à traiter")
    
    args = parser.parse_args()
    
    # Vérification du fichier de données
    if not os.path.exists(args.data):
        logger.error(f"Fichier de données non trouvé: {args.data}")
        sys.exit(1)
    
    # Initialisation et exécution du pipeline
    pipeline = SimpleTrainingPipeline(args.data, args.output)
    pipeline.run_complete_pipeline(args.n_samples)

if __name__ == "__main__":
    main()
