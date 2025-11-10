"""
Processeur de Traitement par Lots - FreeMobilaChat
==================================================

Module spécialisé dans le traitement par lots (batch processing) de grands datasets
avec suivi de progression en temps réel et optimisation des performances.

Fonctionnalités:
- Traitement par lots configurable pour éviter la saturation mémoire
- Barre de progression interactive avec Streamlit
- Calcul automatique du temps estimé (ETA)
- Gestion robuste des erreurs avec nettoyage des ressources UI
"""

# Imports des bibliothèques essentielles
import pandas as pd  # Manipulation de DataFrames pour traitement de données massives
import streamlit as st  # Interface utilisateur et composants de progression
from typing import Callable, List, Dict, Any, Optional  # Typage statique pour validation
import logging  # Journalisation des événements et erreurs
from datetime import datetime  # Gestion des timestamps (non utilisé actuellement mais disponible)
import time  # Mesure des performances et calcul des débits de traitement

# Configuration du logger pour le suivi des opérations batch
logger = logging.getLogger(__name__)


class BatchProcessor:
    """
    Gestionnaire de traitement par lots pour grands datasets avec suivi de progression
    
    Cette classe optimise le traitement de datasets volumineux en les divisant en lots
    de taille configurable, évitant ainsi la saturation mémoire et permettant un suivi
    en temps réel via une interface Streamlit.
    """
    
    def __init__(self, batch_size: int = 50):
        """
        Initialise le processeur par lots avec une taille de batch configurable
        
        Args:
            batch_size: Nombre d'éléments à traiter simultanément dans chaque lot
                       Valeur recommandée: 50 pour équilibrer performance et mémoire
        """
        # Stockage de la taille de lot pour réutilisation dans toutes les méthodes
        self.batch_size = batch_size  # Configuration de la granularité du traitement
        
    def process_in_batches(
        self,
        df: pd.DataFrame,
        process_func: Callable,
        progress_callback: Optional[Callable] = None,
        show_progress: bool = True
    ) -> pd.DataFrame:
        """
        Process DataFrame in batches with progress tracking
        
        Args:
            df: DataFrame to process
            process_func: Function to apply to each batch
            progress_callback: Optional callback for progress updates
            show_progress: Whether to show Streamlit progress bar
            
        Returns:
            Processed DataFrame
        """
        if df.empty:
            logger.warning("Empty DataFrame provided to batch processor")
            return df
            
        total_rows = len(df)
        total_batches = (total_rows + self.batch_size - 1) // self.batch_size
        
        logger.info(f"Processing {total_rows:,} rows in {total_batches} batches of {self.batch_size}")
        
        # Initialize progress tracking
        progress_bar = None
        status_text = None
        
        if show_progress:
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        results = []
        start_time = time.time()
        
        try:
            for batch_idx in range(total_batches):
                start_idx = batch_idx * self.batch_size
                end_idx = min(start_idx + self.batch_size, total_rows)
                
                # Extract batch
                batch_df = df.iloc[start_idx:end_idx].copy()
                
                # Process batch
                batch_result = process_func(batch_df)
                results.append(batch_result)
                
                # Update progress
                progress = (batch_idx + 1) / total_batches
                processed_count = end_idx
                
                if show_progress and progress_bar and status_text:
                    progress_bar.progress(progress)
                    elapsed = time.time() - start_time
                    rate = processed_count / elapsed if elapsed > 0 else 0
                    eta = (total_rows - processed_count) / rate if rate > 0 else 0
                    
                    status_text.text(
                        f"📊 Traitement: {processed_count:,}/{total_rows:,} lignes "
                        f"({progress*100:.1f}%) | "
                        f"⚡ {rate:.1f} lignes/s | "
                        f"⏱️ ETA: {eta:.0f}s"
                    )
                
                if progress_callback:
                    progress_callback(
                        f"Batch {batch_idx + 1}/{total_batches}",
                        progress
                    )
                    
        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            if show_progress and progress_bar and status_text:
                # Add delay for DOM stability
                time.sleep(0.1)
                try:
                    progress_bar.empty()
                    status_text.empty()
                except Exception:
                    pass  # Ignore DOM errors
            raise
            
        finally:
            if show_progress and progress_bar and status_text:
                # Add delay for DOM stability
                time.sleep(0.1)
                try:
                    progress_bar.empty()
                    status_text.empty()
                except Exception:
                    pass  # Ignore DOM errors
        
        # Combine results
        result_df = pd.concat(results, ignore_index=True)
        
        total_time = time.time() - start_time
        logger.info(
            f"Batch processing complete: {total_rows:,} rows in {total_time:.2f}s "
            f"({total_rows/total_time:.1f} rows/s)"
        )
        
        return result_df
    
    def process_with_classification(
        self,
        df: pd.DataFrame,
        text_column: str,
        classifier: Any,
        show_progress: bool = True
    ) -> pd.DataFrame:
        """
        Specialized batch processing for classification tasks
        
        Args:
            df: DataFrame with texts to classify
            text_column: Name of column containing text
            classifier: Classifier object with classify_batch method
            show_progress: Whether to show progress bar
            
        Returns:
            DataFrame with classification results
        """
        def classify_batch(batch: pd.DataFrame) -> pd.DataFrame:
            """Classify a single batch"""
            texts = batch[text_column].tolist()
            results = classifier.classify_batch(texts)
            
            # Add results to batch
            for key, values in results.items():
                batch[key] = values
                
            return batch
        
        return self.process_in_batches(
            df,
            classify_batch,
            show_progress=show_progress
        )
    
    def estimate_processing_time(
        self,
        total_rows: int,
        time_per_item: float
    ) -> Dict[str, Any]:
        """
        Estimate processing time and batch configuration
        
        Args:
            total_rows: Total number of rows to process
            time_per_item: Estimated time per item in seconds
            
        Returns:
            Dictionary with time estimates and batch info
        """
        total_time = total_rows * time_per_item
        total_batches = (total_rows + self.batch_size - 1) // self.batch_size
        time_per_batch = self.batch_size * time_per_item
        
        return {
            'total_rows': total_rows,
            'batch_size': self.batch_size,
            'total_batches': total_batches,
            'estimated_total_time': total_time,
            'estimated_time_per_batch': time_per_batch,
            'estimated_rate': 1 / time_per_item if time_per_item > 0 else 0,
            'formatted_time': self._format_time(total_time)
        }
    
    @staticmethod
    def _format_time(seconds: float) -> str:
        """Format seconds into readable time string"""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}min"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"


def create_batch_processor(batch_size: int = 50) -> BatchProcessor:
    """Factory function to create a batch processor instance"""
    return BatchProcessor(batch_size=batch_size)


# Example usage for CSV classification
def process_csv_with_batches(
    df: pd.DataFrame,
    text_column: str,
    batch_size: int = 50
) -> pd.DataFrame:
    """
    Process CSV data in batches for classification
    
    Args:
        df: Input DataFrame
        text_column: Column containing text to classify
        batch_size: Size of each batch
        
    Returns:
        Classified DataFrame
    """
    processor = BatchProcessor(batch_size=batch_size)
    
    st.info(f"🔄 Configuration: Traitement par lots de {batch_size} lignes")
    
    # Estimate time
    estimates = processor.estimate_processing_time(
        total_rows=len(df),
        time_per_item=0.1  # Adjust based on actual classifier speed
    )
    
    st.caption(
        f"📊 {estimates['total_batches']} lots • "
        f"⏱️ Temps estimé: {estimates['formatted_time']}"
    )
    
    # Process (classifier would be provided in actual use)
    # result = processor.process_with_classification(df, text_column, classifier)
    
    return df
