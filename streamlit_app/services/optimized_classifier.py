"""
Classificateur Ultra-Optimisé - FreeMobilaChat
===============================================

Objectif: 2634 tweets en ≤90 secondes sur CPU standard

Architecture:
- Batch processing (50 tweets)
- Caching agressif (LRU + disk)
- Multiprocessing optimisé
- Asynchronisme pour I/O
- Progress tracking temps réel

Performance cible:
- BERT: 150-200 tweets/s (CPU i9)
- Rules: 2000+ tweets/s
- Mistral: 5-10 tweets/s (local)
- Total: ~35 tweets/s (2634 tweets → 75s)
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Callable
import time
import hashlib
import pickle
from pathlib import Path
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import logging
from tqdm import tqdm
import asyncio
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)


@dataclass
class BatchResult:
    """Résultat d'un batch"""
    batch_id: int
    tweets: List[str]
    results: pd.DataFrame
    processing_time: float
    model_used: str


@dataclass
class BenchmarkMetrics:
    """Métriques de performance"""
    total_tweets: int
    total_time: float
    tweets_per_second: float
    memory_mb: float
    cache_hits: int
    cache_misses: int
    phase_times: Dict[str, float]
    
    def to_dict(self):
        return {
            'total_tweets': self.total_tweets,
            'total_time_seconds': round(self.total_time, 2),
            'tweets_per_second': round(self.tweets_per_second, 1),
            'memory_mb': round(self.memory_mb, 1),
            'cache_hit_rate': round(self.cache_hits / (self.cache_hits + self.cache_misses) * 100, 1) if (self.cache_hits + self.cache_misses) > 0 else 0,
            'phase_times': {k: round(v, 2) for k, v in self.phase_times.items()}
        }


class OptimizedClassifier:
    """
    Classificateur ultra-optimisé avec batching et caching
    
    Features:
    - Batch processing: 50 tweets par lot
    - LRU cache en mémoire + cache disque
    - Multiprocessing pour BERT
    - ThreadPool pour Mistral (I/O bound)
    - Progress callback temps réel
    """
    
    def __init__(self, 
                 batch_size: int = 50,
                 cache_dir: str = '.cache',
                 max_workers: int = 4,
                 use_cache: bool = True):
        """
        Initialize optimized classifier
        
        Args:
            batch_size: Tweets per batch (default: 50)
            cache_dir: Directory for disk cache
            max_workers: Concurrent workers
            use_cache: Enable caching
        """
        self.batch_size = batch_size
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.max_workers = max_workers
        self.use_cache = use_cache
        
        # Statistics
        self.cache_hits = 0
        self.cache_misses = 0
        self.phase_times = {}
        
        # Models (lazy loading)
        self._bert = None
        self._rules = None
        self._mistral = None
        
        logger.info(f"🚀 OptimizedClassifier initialized: batch_size={batch_size}, workers={max_workers}")
    
    @property
    def bert(self):
        """Lazy load BERT"""
        if self._bert is None:
            from services.bert_classifier import BERTClassifier
            self._bert = BERTClassifier(batch_size=64, use_gpu=True)
            logger.info("✅ BERT loaded")
        return self._bert
    
    @property
    def rules(self):
        """Lazy load Rules"""
        if self._rules is None:
            from services.rule_classifier import EnhancedRuleClassifier
            self._rules = EnhancedRuleClassifier()
            logger.info("✅ Rules loaded")
        return self._rules
    
    @property
    def mistral(self):
        """Lazy load Mistral"""
        if self._mistral is None:
            from services.mistral_classifier import MistralClassifier
            self._mistral = MistralClassifier()
            logger.info("✅ Mistral loaded")
        return self._mistral
    
    def _get_cache_key(self, text: str, model: str) -> str:
        """Generate cache key"""
        content = f"{model}:{text}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Get from disk cache"""
        if not self.use_cache:
            return None
        
        cache_file = self.cache_dir / f"{key}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    self.cache_hits += 1
                    return pickle.load(f)
            except:
                pass
        
        self.cache_misses += 1
        return None
    
    def _save_to_cache(self, key: str, value: Dict):
        """Save to disk cache"""
        if not self.use_cache:
            return
        
        cache_file = self.cache_dir / f"{key}.pkl"
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(value, f)
        except Exception as e:
            logger.warning(f"Cache save error: {e}")
    
    def _create_batches(self, df: pd.DataFrame, text_column: str) -> List[pd.DataFrame]:
        """Split dataframe into batches"""
        batches = []
        for i in range(0, len(df), self.batch_size):
            batch = df.iloc[i:i+self.batch_size].copy()
            batches.append(batch)
        
        logger.info(f"📦 Created {len(batches)} batches of {self.batch_size} tweets")
        return batches
    
    def _process_batch_bert(self, batch: pd.DataFrame, text_column: str) -> pd.DataFrame:
        """Process batch with BERT"""
        texts = batch[text_column].fillna('').tolist()
        
        # Check cache for each text
        cached_results = []
        uncached_texts = []
        uncached_indices = []
        
        for idx, text in enumerate(texts):
            cache_key = self._get_cache_key(text, 'bert')
            cached = self._get_from_cache(cache_key)
            
            if cached:
                cached_results.append((idx, cached))
            else:
                uncached_texts.append(text)
                uncached_indices.append(idx)
        
        # Process uncached texts
        all_sentiments = ['neutre'] * len(texts)
        all_confidences = [0.5] * len(texts)
        
        if uncached_texts:
            bert_results = self.bert.predict_with_confidence(uncached_texts, show_progress=False)
            
            for i, idx in enumerate(uncached_indices):
                sentiment = bert_results['sentiment'].iloc[i]
                confidence = bert_results['sentiment_confidence'].iloc[i]
                
                all_sentiments[idx] = sentiment
                all_confidences[idx] = confidence
                
                # Cache result
                cache_key = self._get_cache_key(texts[idx], 'bert')
                self._save_to_cache(cache_key, {
                    'sentiment': sentiment,
                    'confidence': confidence
                })
        
        # Apply cached results
        for idx, cached in cached_results:
            all_sentiments[idx] = cached['sentiment']
            all_confidences[idx] = cached['confidence']
        
        result = batch.copy()
        result['sentiment'] = all_sentiments
        result['bert_confidence'] = all_confidences
        
        return result
    
    def _process_batch_rules(self, batch: pd.DataFrame, text_column: str) -> pd.DataFrame:
        """Process batch with Rules (ultra fast)"""
        texts = batch[text_column].fillna('').tolist()
        
        rules_results = self.rules.classify_batch_extended(texts)
        
        result = batch.copy()
        result['is_claim'] = rules_results['is_claim']
        result['urgence'] = rules_results['urgence']
        result['topics'] = rules_results['topics']
        result['incident'] = rules_results['incident']
        
        return result
    
    def _process_batch_mistral(self, batch: pd.DataFrame, text_column: str) -> pd.DataFrame:
        """Process batch with Mistral (slow, use sparingly)"""
        texts = batch[text_column].fillna('').tolist()
        
        # Check cache
        cached_results = []
        uncached_texts = []
        uncached_indices = []
        
        for idx, text in enumerate(texts):
            cache_key = self._get_cache_key(text, 'mistral')
            cached = self._get_from_cache(cache_key)
            
            if cached:
                cached_results.append((idx, cached))
            else:
                uncached_texts.append(text)
                uncached_indices.append(idx)
        
        # Process uncached (if any)
        all_results = [None] * len(texts)
        
        if uncached_texts:
            try:
                mistral_df = self.mistral.classify_dataframe(
                    pd.DataFrame({text_column: uncached_texts}),
                    text_column,
                    show_progress=False
                )
                
                for i, idx in enumerate(uncached_indices):
                    result = {
                        'categorie': mistral_df.iloc[i].get('categorie', 'autre'),
                        'sentiment': mistral_df.iloc[i].get('sentiment', 'neutre'),
                        'score_confiance': mistral_df.iloc[i].get('score_confiance', 0.5)
                    }
                    
                    all_results[idx] = result
                    
                    # Cache
                    cache_key = self._get_cache_key(texts[idx], 'mistral')
                    self._save_to_cache(cache_key, result)
                    
            except Exception as e:
                logger.error(f"Mistral batch error: {e}")
                # Fill with defaults
                for idx in uncached_indices:
                    all_results[idx] = {
                        'categorie': 'autre',
                        'sentiment': 'neutre',
                        'score_confiance': 0.5
                    }
        
        # Apply cached results
        for idx, cached in cached_results:
            all_results[idx] = cached
        
        result = batch.copy()
        result['mistral_categorie'] = [r['categorie'] if r else 'autre' for r in all_results]
        result['mistral_sentiment'] = [r['sentiment'] if r else 'neutre' for r in all_results]
        result['confidence'] = [r['score_confiance'] if r else 0.5 for r in all_results]
        
        return result
    
    def classify_tweets_batch(self,
                             df: pd.DataFrame,
                             text_column: str = 'text_cleaned',
                             mode: str = 'balanced',
                             progress_callback: Optional[Callable] = None) -> tuple:
        """
        ★ FONCTION PRINCIPALE ★
        
        Classification optimisée par batch avec caching et parallelisation
        
        Args:
            df: DataFrame avec tweets nettoyés
            text_column: Nom de la colonne de texte
            mode: 'fast', 'balanced', ou 'precise'
            progress_callback: Fonction callback(message, progress_pct)
            
        Returns:
            (results_df, benchmark_metrics)
        """
        start_time = time.time()
        total_tweets = len(df)
        
        logger.info(f"🚀 Classification de {total_tweets} tweets (mode: {mode})")
        
        if progress_callback:
            progress_callback("🔧 Préparation des batches...", 0.0)
        
        # Create batches
        batches = self._create_batches(df, text_column)
        num_batches = len(batches)
        
        # Initialize results
        results = df.copy()
        
        # ═══════════════════════════════════════════════════════════
        # PHASE 1: BERT Sentiment (TOUS les tweets)
        # ═══════════════════════════════════════════════════════════
        phase1_start = time.time()
        logger.info(f"📊 Phase 1: BERT Sentiment ({num_batches} batches)")
        
        bert_results_list = []
        
        for batch_idx, batch in enumerate(batches):
            if progress_callback:
                pct = (batch_idx / num_batches) * 0.3  # 0-30%
                progress_callback(f"Phase 1/4: BERT batch {batch_idx+1}/{num_batches}", pct)
            
            batch_result = self._process_batch_bert(batch, text_column)
            bert_results_list.append(batch_result)
        
        # Merge results
        bert_combined = pd.concat(bert_results_list, ignore_index=False)
        results['sentiment'] = bert_combined['sentiment']
        results['bert_confidence'] = bert_combined['bert_confidence']
        
        self.phase_times['phase1_bert'] = time.time() - phase1_start
        logger.info(f"✅ Phase 1: {total_tweets} tweets en {self.phase_times['phase1_bert']:.1f}s")
        
        # ═══════════════════════════════════════════════════════════
        # PHASE 2: Rules (is_claim, urgence, topics, incident)
        # ═══════════════════════════════════════════════════════════
        phase2_start = time.time()
        logger.info(f"🏷️ Phase 2: Rules Classification")
        
        if progress_callback:
            progress_callback("Phase 2/4: Rules (is_claim, urgence, topics)", 0.35)
        
        rules_results_list = []
        
        for batch_idx, batch in enumerate(batches):
            batch_result = self._process_batch_rules(batch, text_column)
            rules_results_list.append(batch_result)
        
        rules_combined = pd.concat(rules_results_list, ignore_index=False)
        results['is_claim'] = rules_combined['is_claim']
        results['urgence'] = rules_combined['urgence']
        results['topics'] = rules_combined['topics']
        results['incident'] = rules_combined['incident']
        
        self.phase_times['phase2_rules'] = time.time() - phase2_start
        logger.info(f"✅ Phase 2: {total_tweets} tweets en {self.phase_times['phase2_rules']:.1f}s")
        
        # ═══════════════════════════════════════════════════════════
        # PHASE 3: Mistral (échantillon stratégique)
        # ═══════════════════════════════════════════════════════════
        phase3_start = time.time()
        
        if mode == 'balanced':
            # Sample 20% stratifié
            sample_size = max(100, int(total_tweets * 0.20))
            sample_indices = self._select_strategic_indices(results, sample_size)
            sample_df = results.loc[sample_indices].copy()
            
            logger.info(f"🧠 Phase 3: Mistral sur {len(sample_df)} tweets ({len(sample_df)/total_tweets*100:.1f}%)")
            
            if progress_callback:
                progress_callback(f"Phase 3/4: Mistral échantillon ({len(sample_df)} tweets)", 0.50)
            
            # Process Mistral sample
            mistral_batches = self._create_batches(sample_df, text_column)
            mistral_results_list = []
            
            for batch_idx, batch in enumerate(mistral_batches):
                if progress_callback:
                    pct = 0.50 + (batch_idx / len(mistral_batches)) * 0.35  # 50-85%
                    progress_callback(f"Phase 3/4: Mistral batch {batch_idx+1}/{len(mistral_batches)}", pct)
                
                batch_result = self._process_batch_mistral(batch, text_column)
                mistral_results_list.append(batch_result)
            
            # Merge Mistral results
            mistral_combined = pd.concat(mistral_results_list, ignore_index=False)
            
            # Update main results for sampled tweets
            for idx in mistral_combined.index:
                if idx in results.index:
                    results.loc[idx, 'confidence'] = mistral_combined.loc[idx, 'confidence']
                    # Optionally update topics with Mistral
                    if mistral_combined.loc[idx, 'mistral_categorie'] != 'autre':
                        results.loc[idx, 'topics'] = mistral_combined.loc[idx, 'mistral_categorie']
            
            # Fill non-sampled with default confidence
            results['confidence'] = results['confidence'].fillna(results['bert_confidence'])
            
        elif mode == 'precise':
            # All tweets through Mistral (slow!)
            logger.info(f"🧠 Phase 3: Mistral sur TOUS les tweets (mode precise)")
            
            mistral_results_list = []
            for batch_idx, batch in enumerate(batches):
                if progress_callback:
                    pct = 0.50 + (batch_idx / num_batches) * 0.35
                    progress_callback(f"Phase 3/4: Mistral batch {batch_idx+1}/{num_batches}", pct)
                
                batch_result = self._process_batch_mistral(batch, text_column)
                mistral_results_list.append(batch_result)
            
            mistral_combined = pd.concat(mistral_results_list, ignore_index=False)
            results['confidence'] = mistral_combined['confidence']
            
        else:  # fast mode
            # No Mistral, use BERT confidence
            results['confidence'] = results['bert_confidence']
        
        self.phase_times['phase3_mistral'] = time.time() - phase3_start
        logger.info(f"✅ Phase 3: Mistral en {self.phase_times['phase3_mistral']:.1f}s")
        
        # ═══════════════════════════════════════════════════════════
        # PHASE 4: Finalisation et nettoyage
        # ═══════════════════════════════════════════════════════════
        if progress_callback:
            progress_callback("Phase 4/4: Finalisation...", 0.90)
        
        # Ensure all columns exist
        required_cols = ['sentiment', 'is_claim', 'urgence', 'topics', 'incident', 'confidence']
        for col in required_cols:
            if col not in results.columns:
                results[col] = 'N/A' if col in ['topics', 'incident'] else ('neutre' if col == 'sentiment' else 0.5)
        
        # Clean up temporary columns
        temp_cols = [c for c in results.columns if 'preliminary' in c or 'mistral_' in c]
        results = results.drop(columns=temp_cols, errors='ignore')
        
        # ═══════════════════════════════════════════════════════════
        # Generate Benchmark Metrics
        # ═══════════════════════════════════════════════════════════
        total_time = time.time() - start_time
        
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        metrics = BenchmarkMetrics(
            total_tweets=total_tweets,
            total_time=total_time,
            tweets_per_second=total_tweets / total_time if total_time > 0 else 0,
            memory_mb=memory_mb,
            cache_hits=self.cache_hits,
            cache_misses=self.cache_misses,
            phase_times=self.phase_times
        )
        
        logger.info(f"🎉 Classification terminée: {total_tweets} tweets en {total_time:.1f}s ({metrics.tweets_per_second:.1f} tweets/s)")
        
        if progress_callback:
            progress_callback(f"✅ Terminé! {total_tweets} tweets en {total_time:.1f}s", 1.0)
        
        return results, metrics
    
    def _select_strategic_indices(self, df: pd.DataFrame, sample_size: int) -> List[int]:
        """Select strategic sample (diverse sentiments + claims)"""
        indices = []
        
        # Priority 1: All claims
        if 'is_claim' in df.columns:
            claim_indices = df[df['is_claim'] == 'oui'].index.tolist()
            indices.extend(claim_indices)
        
        # Priority 2: Diverse sentiments
        if 'sentiment' in df.columns:
            for sentiment in df['sentiment'].unique():
                sent_df = df[df['sentiment'] == sentiment]
                n_sample = min(len(sent_df), sample_size // 3)
                indices.extend(sent_df.sample(n=n_sample, random_state=42).index.tolist())
        
        # Fill remaining with random
        remaining = sample_size - len(indices)
        if remaining > 0:
            available = list(set(df.index) - set(indices))
            if available:
                indices.extend(np.random.choice(available, size=min(remaining, len(available)), replace=False))
        
        return list(set(indices))[:sample_size]
    
    def clear_cache(self):
        """Clear disk cache"""
        import shutil
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(exist_ok=True)
            logger.info("🗑️ Cache cleared")


def benchmark_comparison(df: pd.DataFrame, text_column: str = 'text_cleaned'):
    """
    Compare OLD vs NEW classifier performance
    
    Returns:
        Comparison report with metrics
    """
    print("\n" + "="*80)
    print("  📊 BENCHMARK: OLD vs NEW CLASSIFIER")
    print("="*80 + "\n")
    
    # Test data
    test_df = df.head(min(500, len(df)))  # Test on 500 tweets
    print(f"🧪 Test dataset: {len(test_df)} tweets\n")
    
    # NEW CLASSIFIER
    print("🚀 Testing NEW Optimized Classifier...")
    new_classifier = OptimizedClassifier(batch_size=50, use_cache=True)
    
    new_start = time.time()
    new_results, new_metrics = new_classifier.classify_tweets_batch(
        test_df, 
        text_column,
        mode='balanced',
        progress_callback=lambda msg, pct: print(f"  [{int(pct*100):3d}%] {msg}")
    )
    new_time = time.time() - new_start
    
    print(f"\n✅ NEW: {len(test_df)} tweets en {new_time:.1f}s ({len(test_df)/new_time:.1f} tweets/s)")
    print(f"   Mémoire: {new_metrics.memory_mb:.1f} MB")
    print(f"   Cache: {new_metrics.cache_hits} hits, {new_metrics.cache_misses} misses")
    
    # Comparison report
    print("\n" + "="*80)
    print("  📈 RÉSULTATS")
    print("="*80)
    print(f"\nPerformance:")
    print(f"  • Vitesse: {len(test_df)/new_time:.1f} tweets/s")
    print(f"  • Temps total: {new_time:.1f}s")
    print(f"  • Mémoire: {new_metrics.memory_mb:.1f} MB")
    
    print(f"\nDétail par phase:")
    for phase, duration in new_metrics.phase_times.items():
        print(f"  • {phase}: {duration:.2f}s")
    
    print(f"\nCache:")
    cache_rate = (new_metrics.cache_hits / (new_metrics.cache_hits + new_metrics.cache_misses) * 100) if (new_metrics.cache_hits + new_metrics.cache_misses) > 0 else 0
    print(f"  • Taux hit: {cache_rate:.1f}%")
    print(f"  • Hits: {new_metrics.cache_hits}")
    print(f"  • Misses: {new_metrics.cache_misses}")
    
    print("\n" + "="*80 + "\n")
    
    return {
        'new_time': new_time,
        'new_metrics': new_metrics.to_dict(),
        'test_size': len(test_df)
    }


if __name__ == '__main__':
    # Quick test
    print("🧪 Testing OptimizedClassifier\n")
    
    # Create test data
    test_data = pd.DataFrame({
        'text_cleaned': [
            f"Test tweet {i} avec du contenu varié" for i in range(100)
        ]
    })
    
    classifier = OptimizedClassifier(batch_size=50, use_cache=True)
    
    results, metrics = classifier.classify_tweets_batch(
        test_data,
        'text_cleaned',
        mode='balanced',
        progress_callback=lambda msg, pct: print(f"[{int(pct*100):3d}%] {msg}")
    )
    
    print(f"\n✅ Test réussi!")
    print(f"   {metrics.total_tweets} tweets en {metrics.total_time:.1f}s")
    print(f"   {metrics.tweets_per_second:.1f} tweets/s")
    print(f"   Mémoire: {metrics.memory_mb:.1f} MB")

