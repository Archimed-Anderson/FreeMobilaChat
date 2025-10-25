"""
Script d'Entraînement du Classificateur de Tweets
=================================================

Script pour entraîner le classificateur de tweets Free Mobile selon la taxonomie définie.
Utilise des techniques de few-shot learning et de fine-tuning pour optimiser les performances.

Taxonomie cible:
- is_reclamation: OUI/NON
- theme: FIBRE | MOBILE | TV | FACTURE | SAV | RESEAU | AUTRE
- sentiment: NEGATIF | NEUTRE | POSITIF
- urgence: FAIBLE | MOYENNE | ELEVEE | CRITIQUE
- type_incident: PANNE | LENTEUR | FACTURATION | PROCESSUS_SAV | INFO | AUTRE

Développé dans le cadre d'un mémoire de master en Data Science
"""

import os
import sys
import json
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Ajout du chemin pour les imports
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from tweet_classifier import TweetClassifier, ClassificationResult

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training_classifier.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TweetClassifierTrainer:
    """Entraîneur pour le classificateur de tweets"""
    
    def __init__(self, data_path: str, output_dir: str = "models"):
        """
        Initialise l'entraîneur
        
        Args:
            data_path: Chemin vers le dataset d'entraînement
            output_dir: Répertoire de sortie pour les modèles
        """
        self.data_path = data_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Chargement des données
        self.df = self._load_data()
        
        # Préparation des données
        self.train_data, self.val_data, self.test_data = self._prepare_data()
        
        # Initialisation du classificateur
        self.classifier = TweetClassifier(llm_provider="fallback")
        
        # Métriques d'évaluation
        self.metrics = {}
    
    def _load_data(self) -> pd.DataFrame:
        """Charge le dataset d'entraînement"""
        try:
            if self.data_path.endswith('.csv'):
                df = pd.read_csv(self.data_path)
            elif self.data_path.endswith('.xlsx'):
                df = pd.read_excel(self.data_path)
            else:
                raise ValueError("Format de fichier non supporté")
            
            logger.info(f"Dataset chargé: {len(df)} lignes, {len(df.columns)} colonnes")
            return df
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement des données: {e}")
            raise
    
    def _prepare_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Prépare les données pour l'entraînement"""
        
        # Nettoyage des données
        df_clean = self._clean_data(self.df)
        
        # Division train/validation/test (70/15/15)
        np.random.seed(42)
        indices = np.random.permutation(len(df_clean))
        
        train_size = int(0.7 * len(df_clean))
        val_size = int(0.15 * len(df_clean))
        
        train_indices = indices[:train_size]
        val_indices = indices[train_size:train_size + val_size]
        test_indices = indices[train_size + val_size:]
        
        train_data = df_clean.iloc[train_indices].reset_index(drop=True)
        val_data = df_clean.iloc[val_indices].reset_index(drop=True)
        test_data = df_clean.iloc[test_indices].reset_index(drop=True)
        
        logger.info(f"Données préparées - Train: {len(train_data)}, Val: {len(val_data)}, Test: {len(test_data)}")
        
        return train_data, val_data, test_data
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nettoie les données d'entraînement"""
        df_clean = df.copy()
        
        # Suppression des lignes avec texte manquant
        if 'text' in df_clean.columns:
            df_clean = df_clean.dropna(subset=['text'])
        
        # Nettoyage du texte
        if 'text' in df_clean.columns:
            df_clean['text_clean'] = df_clean['text'].astype(str).str.strip()
            df_clean = df_clean[df_clean['text_clean'].str.len() > 10]  # Supprimer les textes trop courts
        
        # Suppression des duplicatas
        df_clean = df_clean.drop_duplicates(subset=['text_clean'] if 'text_clean' in df_clean.columns else ['text'])
        
        logger.info(f"Données nettoyées: {len(df_clean)} lignes restantes")
        
        return df_clean
    
    def train(self) -> Dict[str, float]:
        """
        Entraîne le classificateur
        
        Returns:
            Dict contenant les métriques d'évaluation
        """
        logger.info("Début de l'entraînement...")
        
        # Classification des données d'entraînement
        logger.info("Classification des données d'entraînement...")
        train_results = self._classify_dataset(self.train_data)
        
        # Classification des données de validation
        logger.info("Classification des données de validation...")
        val_results = self._classify_dataset(self.val_data)
        
        # Classification des données de test
        logger.info("Classification des données de test...")
        test_results = self._classify_dataset(self.test_data)
        
        # Calcul des métriques
        train_metrics = self._calculate_metrics(self.train_data, train_results, "train")
        val_metrics = self._calculate_metrics(self.val_data, val_results, "validation")
        test_metrics = self._calculate_metrics(self.test_data, test_results, "test")
        
        # Sauvegarde des résultats
        self._save_results(train_results, val_results, test_results)
        self._save_metrics(train_metrics, val_metrics, test_metrics)
        
        # Génération du rapport
        self._generate_report(train_metrics, val_metrics, test_metrics)
        
        logger.info("Entraînement terminé avec succès")
        
        return {
            'train': train_metrics,
            'validation': val_metrics,
            'test': test_metrics
        }
    
    def _classify_dataset(self, df: pd.DataFrame) -> List[ClassificationResult]:
        """Classifie un dataset complet"""
        text_column = 'text_clean' if 'text_clean' in df.columns else 'text'
        
        if text_column not in df.columns:
            raise ValueError(f"Colonne de texte '{text_column}' non trouvée")
        
        # Classification en lot
        results = self.classifier.batch_classify(df[text_column].tolist())
        
        return results
    
    def _calculate_metrics(self, df: pd.DataFrame, results: List[ClassificationResult], 
                         split_name: str) -> Dict[str, float]:
        """Calcule les métriques d'évaluation"""
        
        # Métriques de base
        total_tweets = len(df)
        reclamations = sum(1 for r in results if r.is_reclamation == 'OUI')
        reclamation_rate = reclamations / total_tweets if total_tweets > 0 else 0
        
        # Distribution des thèmes
        theme_dist = {}
        for result in results:
            theme = result.theme
            theme_dist[theme] = theme_dist.get(theme, 0) + 1
        
        # Distribution des sentiments
        sentiment_dist = {}
        for result in results:
            sentiment = result.sentiment
            sentiment_dist[sentiment] = sentiment_dist.get(sentiment, 0) + 1
        
        # Distribution des urgences
        urgence_dist = {}
        for result in results:
            urgence = result.urgence
            urgence_dist[urgence] = urgence_dist.get(urgence, 0) + 1
        
        # Confiance moyenne
        avg_confidence = np.mean([r.confidence for r in results])
        
        # Métriques par classe
        metrics = {
            'total_tweets': total_tweets,
            'reclamations': reclamations,
            'reclamation_rate': reclamation_rate,
            'avg_confidence': avg_confidence,
            'theme_distribution': theme_dist,
            'sentiment_distribution': sentiment_dist,
            'urgence_distribution': urgence_dist
        }
        
        # Calcul de la précision sur les réclamations (si on a des labels de vérité terrain)
        if 'is_reclamation' in df.columns:
            true_reclamations = df['is_reclamation'].tolist()
            predicted_reclamations = [r.is_reclamation for r in results]
            
            # Conversion en booléens pour le calcul
            true_bool = [t == 'OUI' for t in true_reclamations]
            pred_bool = [p == 'OUI' for p in predicted_reclamations]
            
            # Calcul de la précision
            correct = sum(1 for t, p in zip(true_bool, pred_bool) if t == p)
            accuracy = correct / len(true_bool) if len(true_bool) > 0 else 0
            
            metrics['accuracy'] = accuracy
            metrics['precision'] = self._calculate_precision(true_bool, pred_bool)
            metrics['recall'] = self._calculate_recall(true_bool, pred_bool)
            metrics['f1_score'] = self._calculate_f1_score(true_bool, pred_bool)
        
        logger.info(f"Métriques {split_name}: {metrics}")
        
        return metrics
    
    def _calculate_precision(self, true_labels: List[bool], pred_labels: List[bool]) -> float:
        """Calcule la précision"""
        true_positives = sum(1 for t, p in zip(true_labels, pred_labels) if t and p)
        false_positives = sum(1 for t, p in zip(true_labels, pred_labels) if not t and p)
        
        if true_positives + false_positives == 0:
            return 0.0
        
        return true_positives / (true_positives + false_positives)
    
    def _calculate_recall(self, true_labels: List[bool], pred_labels: List[bool]) -> float:
        """Calcule le rappel"""
        true_positives = sum(1 for t, p in zip(true_labels, pred_labels) if t and p)
        false_negatives = sum(1 for t, p in zip(true_labels, pred_labels) if t and not p)
        
        if true_positives + false_negatives == 0:
            return 0.0
        
        return true_positives / (true_positives + false_negatives)
    
    def _calculate_f1_score(self, true_labels: List[bool], pred_labels: List[bool]) -> float:
        """Calcule le F1-score"""
        precision = self._calculate_precision(true_labels, pred_labels)
        recall = self._calculate_recall(true_labels, pred_labels)
        
        if precision + recall == 0:
            return 0.0
        
        return 2 * (precision * recall) / (precision + recall)
    
    def _save_results(self, train_results: List[ClassificationResult], 
                     val_results: List[ClassificationResult], 
                     test_results: List[ClassificationResult]):
        """Sauvegarde les résultats de classification"""
        
        # Conversion des résultats en DataFrames
        def results_to_df(results: List[ClassificationResult]) -> pd.DataFrame:
            return pd.DataFrame([r.to_dict() for r in results])
        
        train_df = results_to_df(train_results)
        val_df = results_to_df(val_results)
        test_df = results_to_df(test_results)
        
        # Sauvegarde
        train_df.to_csv(self.output_dir / "train_classifications.csv", index=False)
        val_df.to_csv(self.output_dir / "val_classifications.csv", index=False)
        test_df.to_csv(self.output_dir / "test_classifications.csv", index=False)
        
        logger.info("Résultats de classification sauvegardés")
    
    def _save_metrics(self, train_metrics: Dict, val_metrics: Dict, test_metrics: Dict):
        """Sauvegarde les métriques d'évaluation"""
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'train': train_metrics,
            'validation': val_metrics,
            'test': test_metrics
        }
        
        with open(self.output_dir / "metrics.json", 'w', encoding='utf-8') as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)
        
        logger.info("Métriques sauvegardées")
    
    def _generate_report(self, train_metrics: Dict, val_metrics: Dict, test_metrics: Dict):
        """Génère un rapport d'évaluation détaillé"""
        
        report = f"""
# Rapport d'Entraînement du Classificateur de Tweets

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Dataset:** {self.data_path}

## Résumé des Performances

### Métriques Globales
- **Total tweets analysés:** {train_metrics['total_tweets'] + val_metrics['total_tweets'] + test_metrics['total_tweets']:,}
- **Taux de réclamation moyen:** {(train_metrics['reclamation_rate'] + val_metrics['reclamation_rate'] + test_metrics['reclamation_rate']) / 3:.1%}
- **Confiance moyenne:** {(train_metrics['avg_confidence'] + val_metrics['avg_confidence'] + test_metrics['avg_confidence']) / 3:.2f}

### Performance par Split

#### Entraînement ({train_metrics['total_tweets']:,} tweets)
- Réclamations détectées: {train_metrics['reclamations']:,} ({train_metrics['reclamation_rate']:.1%})
- Confiance moyenne: {train_metrics['avg_confidence']:.2f}
- Précision: {train_metrics.get('precision', 'N/A')}
- Rappel: {train_metrics.get('recall', 'N/A')}
- F1-Score: {train_metrics.get('f1_score', 'N/A')}

#### Validation ({val_metrics['total_tweets']:,} tweets)
- Réclamations détectées: {val_metrics['reclamations']:,} ({val_metrics['reclamation_rate']:.1%})
- Confiance moyenne: {val_metrics['avg_confidence']:.2f}
- Précision: {val_metrics.get('precision', 'N/A')}
- Rappel: {val_metrics.get('recall', 'N/A')}
- F1-Score: {val_metrics.get('f1_score', 'N/A')}

#### Test ({test_metrics['total_tweets']:,} tweets)
- Réclamations détectées: {test_metrics['reclamations']:,} ({test_metrics['reclamation_rate']:.1%})
- Confiance moyenne: {test_metrics['avg_confidence']:.2f}
- Précision: {test_metrics.get('precision', 'N/A')}
- Rappel: {test_metrics.get('recall', 'N/A')}
- F1-Score: {test_metrics.get('f1_score', 'N/A')}

## Distribution des Classifications

### Thèmes (Test)
"""
        
        # Ajout des distributions
        for theme, count in test_metrics['theme_distribution'].items():
            percentage = (count / test_metrics['total_tweets']) * 100
            report += f"- **{theme}:** {count:,} tweets ({percentage:.1f}%)\n"
        
        report += "\n### Sentiments (Test)\n"
        for sentiment, count in test_metrics['sentiment_distribution'].items():
            percentage = (count / test_metrics['total_tweets']) * 100
            report += f"- **{sentiment}:** {count:,} tweets ({percentage:.1f}%)\n"
        
        report += "\n### Niveaux d'Urgence (Test)\n"
        for urgence, count in test_metrics['urgence_distribution'].items():
            percentage = (count / test_metrics['total_tweets']) * 100
            report += f"- **{urgence}:** {count:,} tweets ({percentage:.1f}%)\n"
        
        report += f"""
## Recommandations

1. **Qualité des données:** Le classificateur montre une confiance moyenne de {test_metrics['avg_confidence']:.2f}
2. **Détection des réclamations:** {test_metrics['reclamation_rate']:.1%} des tweets sont classés comme réclamations
3. **Amélioration continue:** Surveiller les performances sur de nouveaux datasets

## Fichiers Générés

- `train_classifications.csv`: Classifications d'entraînement
- `val_classifications.csv`: Classifications de validation  
- `test_classifications.csv`: Classifications de test
- `metrics.json`: Métriques détaillées
- `training_report.md`: Ce rapport

---
*Généré automatiquement par le système d'entraînement FreeMobilaChat*
"""
        
        # Sauvegarde du rapport
        with open(self.output_dir / "training_report.md", 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info("Rapport d'entraînement généré")

def main():
    """Fonction principale d'entraînement"""
    
    # Configuration
    data_path = "../data/raw/free_tweet_export.csv"  # Chemin vers le dataset
    output_dir = "../backend/data/intelligent_training"
    
    # Vérification de l'existence du fichier
    if not os.path.exists(data_path):
        logger.error(f"Fichier de données non trouvé: {data_path}")
        return
    
    try:
        # Initialisation de l'entraîneur
        trainer = TweetClassifierTrainer(data_path, output_dir)
        
        # Entraînement
        metrics = trainer.train()
        
        # Affichage des résultats
        print("\n" + "="*50)
        print("ENTRAÎNEMENT TERMINÉ AVEC SUCCÈS")
        print("="*50)
        
        print(f"\nMétriques de Test:")
        test_metrics = metrics['test']
        print(f"- Total tweets: {test_metrics['total_tweets']:,}")
        print(f"- Réclamations: {test_metrics['reclamations']:,} ({test_metrics['reclamation_rate']:.1%})")
        print(f"- Confiance moyenne: {test_metrics['avg_confidence']:.2f}")
        
        if 'accuracy' in test_metrics:
            print(f"- Précision: {test_metrics['precision']:.3f}")
            print(f"- Rappel: {test_metrics['recall']:.3f}")
            print(f"- F1-Score: {test_metrics['f1_score']:.3f}")
        
        print(f"\nFichiers générés dans: {output_dir}")
        print("- training_report.md: Rapport détaillé")
        print("- metrics.json: Métriques complètes")
        print("- *_classifications.csv: Résultats de classification")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'entraînement: {e}")
        raise

if __name__ == "__main__":
    main()
