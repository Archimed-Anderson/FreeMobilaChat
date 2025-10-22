"""
Pipeline d'Entraînement du Classificateur de Tweets Free
=========================================================

Ce script implémente le pipeline complet d'entraînement et d'évaluation
du modèle de classification de tweets.

Processus:
    1. Chargement et nettoyage du dataset
    2. Génération d'annotations avec le LLM
    3. Split train/validation/test
    4. Évaluation des performances
    5. Génération du rapport d'évaluation

Auteur: Archimed Anderson
Date: Octobre 2024
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    accuracy_score
)
import matplotlib.pyplot as plt
import seaborn as sns

# Ajouter le chemin du backend au sys.path
backend_path = Path(__file__).parent
if str(backend_path) not in sys.path:
    sys.path.append(str(backend_path))

from app.services.tweet_classifier import TweetClassifier, ClassificationResult

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DatasetPreparator:
    """
    Classe pour préparer le dataset à partir du fichier brut.
    """
    
    def __init__(self, raw_data_path: str):
        """
        Initialise le préparateur de dataset.
        
        Args:
            raw_data_path: Chemin vers le fichier de données brutes
        """
        self.raw_data_path = raw_data_path
        self.df = None
        
    def load_data(self) -> pd.DataFrame:
        """
        Charge les données brutes.
        
        Returns:
            DataFrame avec les données chargées
        """
        logger.info(f"Chargement des données depuis {self.raw_data_path}")
        
        # Supporter CSV et Excel
        if self.raw_data_path.endswith('.csv'):
            self.df = pd.read_csv(self.raw_data_path, encoding='utf-8')
        elif self.raw_data_path.endswith('.xlsx'):
            self.df = pd.read_excel(self.raw_data_path)
        else:
            raise ValueError(f"Format non supporté: {self.raw_data_path}")
        
        logger.info(f"Données chargées: {len(self.df)} lignes, {len(self.df.columns)} colonnes")
        logger.info(f"Colonnes: {list(self.df.columns)}")
        
        return self.df
    
    def clean_data(self) -> pd.DataFrame:
        """
        Nettoie les données (duplicatas, valeurs nulles, etc.).
        
        Returns:
            DataFrame nettoyé
        """
        logger.info("Nettoyage des données...")
        
        initial_count = len(self.df)
        
        # Supprimer les duplicatas basés sur le texte du tweet
        self.df = self.df.drop_duplicates(subset=['text'], keep='first')
        logger.info(f"Duplicatas supprimés: {initial_count - len(self.df)}")
        
        # Supprimer les lignes avec texte vide/null
        self.df = self.df.dropna(subset=['text'])
        self.df = self.df[self.df['text'].str.strip() != '']
        logger.info(f"Lignes vides supprimées: {initial_count - len(self.df)}")
        
        # Nettoyer le texte
        self.df['text_clean'] = self.df['text'].apply(self._clean_text)
        
        logger.info(f"Dataset final: {len(self.df)} lignes")
        
        return self.df
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Nettoie le texte d'un tweet.
        
        Args:
            text: Texte brut
            
        Returns:
            Texte nettoyé
        """
        if pd.isna(text):
            return ""
        
        # Convertir en string
        text = str(text)
        
        # Supprimer les RT au début
        if text.startswith('RT '):
            text = text[3:]
        
        # Supprimer les espaces multiples
        text = ' '.join(text.split())
        
        return text.strip()
    
    def sample_for_annotation(
        self,
        n_samples: int = 500,
        stratify_by: str = None
    ) -> pd.DataFrame:
        """
        Échantillonne les données pour annotation.
        
        Args:
            n_samples: Nombre d'échantillons à prendre
            stratify_by: Colonne pour stratification (optionnel)
            
        Returns:
            DataFrame échantillonné
        """
        if len(self.df) <= n_samples:
            logger.info(f"Dataset complet utilisé ({len(self.df)} lignes)")
            return self.df
        
        if stratify_by and stratify_by in self.df.columns:
            sample = self.df.groupby(stratify_by, group_keys=False).apply(
                lambda x: x.sample(min(len(x), n_samples // len(self.df[stratify_by].unique())))
            )
        else:
            sample = self.df.sample(n=n_samples, random_state=42)
        
        logger.info(f"Échantillon créé: {len(sample)} lignes")
        return sample


class ModelTrainer:
    """
    Classe pour entraîner et évaluer le modèle de classification.
    """
    
    def __init__(
        self,
        classifier: TweetClassifier,
        output_dir: str = "backend/data/training"
    ):
        """
        Initialise le trainer.
        
        Args:
            classifier: Instance du classificateur
            output_dir: Répertoire de sortie pour les résultats
        """
        self.classifier = classifier
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.results = []
        self.metrics = {}
    
    def annotate_dataset(
        self,
        df: pd.DataFrame,
        text_column: str = 'text_clean',
        id_column: str = 'tweet_id'
    ) -> pd.DataFrame:
        """
        Annote le dataset avec le classificateur LLM.
        
        Args:
            df: DataFrame à annoter
            text_column: Nom de la colonne contenant le texte
            id_column: Nom de la colonne contenant l'ID
            
        Returns:
            DataFrame avec annotations
        """
        logger.info(f"Début annotation de {len(df)} tweets...")
        
        tweets = df[text_column].tolist()
        tweet_ids = df[id_column].tolist() if id_column in df.columns else None
        
        # Classification batch
        results = self.classifier.batch_classify(tweets, tweet_ids)
        
        # Convertir en DataFrame
        results_df = pd.DataFrame([r.dict() for r in results])
        
        # Fusionner avec le DataFrame original
        df_annotated = pd.concat([df.reset_index(drop=True), results_df], axis=1)
        
        logger.info(f"Annotation terminée: {len(df_annotated)} tweets annotés")
        
        return df_annotated
    
    def split_dataset(
        self,
        df: pd.DataFrame,
        train_size: float = 0.7,
        val_size: float = 0.15,
        test_size: float = 0.15,
        random_state: int = 42
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Split le dataset en train/validation/test.
        
        Args:
            df: DataFrame complet
            train_size: Proportion de train
            val_size: Proportion de validation
            test_size: Proportion de test
            random_state: Seed pour reproductibilité
            
        Returns:
            Tuple (train_df, val_df, test_df)
        """
        # Vérifier que les proportions sont correctes
        assert abs(train_size + val_size + test_size - 1.0) < 0.01, \
            "Les proportions doivent totaliser 1.0"
        
        # Premier split: train vs (val+test)
        train_df, temp_df = train_test_split(
            df,
            train_size=train_size,
            random_state=random_state,
            stratify=df['is_reclamation'] if 'is_reclamation' in df.columns else None
        )
        
        # Deuxième split: val vs test
        relative_test_size = test_size / (val_size + test_size)
        val_df, test_df = train_test_split(
            temp_df,
            test_size=relative_test_size,
            random_state=random_state,
            stratify=temp_df['is_reclamation'] if 'is_reclamation' in temp_df.columns else None
        )
        
        logger.info(f"Dataset split: Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}")
        
        # Sauvegarder les splits
        train_df.to_csv(self.output_dir / 'train_dataset.csv', index=False)
        val_df.to_csv(self.output_dir / 'validation_dataset.csv', index=False)
        test_df.to_csv(self.output_dir / 'test_dataset.csv', index=False)
        
        logger.info(f"Datasets sauvegardés dans {self.output_dir}")
        
        return train_df, val_df, test_df
    
    def evaluate_model(
        self,
        test_df: pd.DataFrame,
        save_plots: bool = True
    ) -> Dict:
        """
        Évalue le modèle sur le set de test.
        
        Args:
            test_df: DataFrame de test avec annotations
            save_plots: Si True, sauvegarde les visualisations
            
        Returns:
            Dictionnaire de métriques
        """
        logger.info("Évaluation du modèle...")
        
        metrics = {}
        
        # Métriques pour chaque dimension
        dimensions = [
            'is_reclamation',
            'theme',
            'sentiment',
            'urgence',
            'type_incident'
        ]
        
        for dim in dimensions:
            if dim not in test_df.columns:
                continue
            
            y_true = test_df[dim].values
            y_pred = test_df[dim].values  # Déjà annoté
            
            # Calculer les métriques
            accuracy = accuracy_score(y_true, y_pred)
            
            # Rapport de classification
            report = classification_report(
                y_true,
                y_pred,
                output_dict=True,
                zero_division=0
            )
            
            # Matrice de confusion
            cm = confusion_matrix(y_true, y_pred)
            
            metrics[dim] = {
                'accuracy': accuracy,
                'classification_report': report,
                'confusion_matrix': cm.tolist()
            }
            
            logger.info(f"\n=== Métriques pour {dim} ===")
            logger.info(f"Accuracy: {accuracy:.3f}")
            logger.info(f"Macro F1: {report['macro avg']['f1-score']:.3f}")
            logger.info(f"Weighted F1: {report['weighted avg']['f1-score']:.3f}")
            
            # Visualisation de la matrice de confusion
            if save_plots:
                self._plot_confusion_matrix(
                    cm,
                    classes=sorted(test_df[dim].unique()),
                    title=f'Matrice de Confusion - {dim}',
                    filename=f'confusion_matrix_{dim}.png'
                )
        
        # Distribution des scores de confiance
        if 'confidence' in test_df.columns:
            metrics['confidence_stats'] = {
                'mean': float(test_df['confidence'].mean()),
                'median': float(test_df['confidence'].median()),
                'std': float(test_df['confidence'].std()),
                'min': float(test_df['confidence'].min()),
                'max': float(test_df['confidence'].max())
            }
            
            logger.info(f"\n=== Statistiques de Confiance ===")
            logger.info(f"Moyenne: {metrics['confidence_stats']['mean']:.3f}")
            logger.info(f"Médiane: {metrics['confidence_stats']['median']:.3f}")
            
            if save_plots:
                self._plot_confidence_distribution(test_df['confidence'])
        
        # Sauvegarder les métriques
        metrics_path = self.output_dir / 'evaluation_metrics.json'
        with open(metrics_path, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Métriques sauvegardées dans {metrics_path}")
        
        self.metrics = metrics
        return metrics
    
    def _plot_confusion_matrix(
        self,
        cm: np.ndarray,
        classes: List[str],
        title: str,
        filename: str
    ):
        """
        Plot et sauvegarde une matrice de confusion.
        """
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            cm,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=classes,
            yticklabels=classes
        )
        plt.title(title)
        plt.ylabel('Valeur Réelle')
        plt.xlabel('Valeur Prédite')
        plt.tight_layout()
        
        plot_path = self.output_dir / filename
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Matrice de confusion sauvegardée: {plot_path}")
    
    def _plot_confidence_distribution(self, confidence_scores: pd.Series):
        """
        Plot la distribution des scores de confiance.
        """
        plt.figure(figsize=(10, 6))
        plt.hist(confidence_scores, bins=20, edgecolor='black', alpha=0.7)
        plt.axvline(
            confidence_scores.mean(),
            color='red',
            linestyle='dashed',
            linewidth=2,
            label=f'Moyenne: {confidence_scores.mean():.2f}'
        )
        plt.xlabel('Score de Confiance')
        plt.ylabel('Fréquence')
        plt.title('Distribution des Scores de Confiance')
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()
        
        plot_path = self.output_dir / 'confidence_distribution.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Distribution de confiance sauvegardée: {plot_path}")
    
    def generate_report(self) -> str:
        """
        Génère un rapport d'évaluation détaillé.
        
        Returns:
            Chemin vers le rapport généré
        """
        report_path = self.output_dir / 'evaluation_report.md'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Rapport d'Évaluation du Classificateur de Tweets Free\n\n")
            f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Modèle**: {self.classifier.model_name}\n\n")
            f.write("---\n\n")
            
            f.write("## 1. Résumé des Performances\n\n")
            
            if self.metrics:
                for dim, metrics in self.metrics.items():
                    if dim == 'confidence_stats':
                        continue
                    
                    f.write(f"### {dim.upper()}\n\n")
                    f.write(f"- **Accuracy**: {metrics['accuracy']:.3f}\n")
                    
                    report = metrics['classification_report']
                    f.write(f"- **Macro F1-Score**: {report['macro avg']['f1-score']:.3f}\n")
                    f.write(f"- **Weighted F1-Score**: {report['weighted avg']['f1-score']:.3f}\n\n")
                    
                    # Détails par classe
                    f.write("#### Détails par Classe\n\n")
                    f.write("| Classe | Precision | Recall | F1-Score | Support |\n")
                    f.write("|--------|-----------|--------|----------|----------|\n")
                    
                    for class_name, class_metrics in report.items():
                        if class_name in ['accuracy', 'macro avg', 'weighted avg']:
                            continue
                        
                        f.write(
                            f"| {class_name} | "
                            f"{class_metrics['precision']:.3f} | "
                            f"{class_metrics['recall']:.3f} | "
                            f"{class_metrics['f1-score']:.3f} | "
                            f"{int(class_metrics['support'])} |\n"
                        )
                    
                    f.write("\n")
            
            if 'confidence_stats' in self.metrics:
                f.write("## 2. Analyse de Confiance\n\n")
                stats = self.metrics['confidence_stats']
                f.write(f"- **Moyenne**: {stats['mean']:.3f}\n")
                f.write(f"- **Médiane**: {stats['median']:.3f}\n")
                f.write(f"- **Écart-type**: {stats['std']:.3f}\n")
                f.write(f"- **Min/Max**: {stats['min']:.3f} / {stats['max']:.3f}\n\n")
            
            f.write("## 3. Visualisations\n\n")
            f.write("Les matrices de confusion et distributions sont disponibles dans le dossier de sortie.\n\n")
            
            f.write("## 4. Critères de Succès\n\n")
            if self.metrics and 'is_reclamation' in self.metrics:
                reclamation_f1 = self.metrics['is_reclamation']['classification_report']['weighted avg']['f1-score']
                success = "✅ SUCCÈS" if reclamation_f1 > 0.85 else "⚠️ À AMÉLIORER"
                f.write(f"- **F1-Score is_reclamation > 0.85**: {success} (actuel: {reclamation_f1:.3f})\n")
            
            f.write("\n---\n\n")
            f.write("*Rapport généré automatiquement par le pipeline d'entraînement*\n")
        
        logger.info(f"Rapport d'évaluation généré: {report_path}")
        return str(report_path)


def main():
    """
    Fonction principale du pipeline d'entraînement.
    """
    parser = argparse.ArgumentParser(description='Entraînement du classificateur de tweets Free')
    parser.add_argument(
        '--data',
        type=str,
        default='data/raw/free_tweet_export.csv',
        help='Chemin vers le fichier de données brutes'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='gpt-4',
        help='Nom du modèle LLM à utiliser'
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
        default=500,
        help='Nombre d\'échantillons à annoter (0 = tous)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='backend/data/training',
        help='Répertoire de sortie'
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("PIPELINE D'ENTRAÎNEMENT - Classificateur Tweets Free")
    logger.info("=" * 60)
    
    try:
        # Étape 1: Préparation du dataset
        logger.info("\n[ÉTAPE 1/5] Préparation du dataset")
        preparator = DatasetPreparator(args.data)
        df = preparator.load_data()
        df = preparator.clean_data()
        
        # Échantillonner si demandé
        if args.n_samples > 0 and args.n_samples < len(df):
            df = preparator.sample_for_annotation(n_samples=args.n_samples)
        
        # Étape 2: Initialisation du classificateur
        logger.info("\n[ÉTAPE 2/5] Initialisation du classificateur")
        classifier = TweetClassifier(
            model_name=args.model,
            api_key=args.api_key or os.getenv('OPENAI_API_KEY')
        )
        
        # Étape 3: Annotation du dataset
        logger.info("\n[ÉTAPE 3/5] Annotation du dataset avec LLM")
        trainer = ModelTrainer(classifier, output_dir=args.output_dir)
        df_annotated = trainer.annotate_dataset(df)
        
        # Étape 4: Split du dataset
        logger.info("\n[ÉTAPE 4/5] Split train/validation/test")
        train_df, val_df, test_df = trainer.split_dataset(df_annotated)
        
        # Étape 5: Évaluation
        logger.info("\n[ÉTAPE 5/5] Évaluation du modèle")
        metrics = trainer.evaluate_model(test_df, save_plots=True)
        
        # Génération du rapport
        report_path = trainer.generate_report()
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ ENTRAÎNEMENT TERMINÉ AVEC SUCCÈS !")
        logger.info(f"📊 Rapport: {report_path}")
        logger.info(f"📁 Outputs: {args.output_dir}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"\n❌ ERREUR: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

