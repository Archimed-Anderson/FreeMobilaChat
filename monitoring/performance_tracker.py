"""
Monitoring et Tracking de Performance - FreeMobilaChat
======================================================

Module de surveillance temps réel des métriques de performance,
qualité et business pour le système de classification.

Fonctionnalités:
- Tracking latence et throughput
- Surveillance qualité des prédictions
- Détection de drift des données
- Alertes automatiques
- Logs structurés pour analyse
"""

import time
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import deque
import statistics

import pandas as pd
import numpy as np
import psutil

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring/logs/performance.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PerformanceTracker:
    """
    Tracker de performance pour monitoring temps réel
    
    Mesure et stocke les métriques clés:
    - Latence classification (p50, p95, p99)
    - Throughput (tweets/seconde)
    - Utilisation ressources (CPU, RAM)
    - Taux d'erreur et fallback
    - Distribution de confiance
    """
    
    def __init__(self, window_size: int = 1000):
        """
        Initialise le tracker avec fenêtre glissante
        
        Args:
            window_size: Taille de la fenêtre pour calculs glissants
        """
        self.window_size = window_size
        
        # Fenêtres glissantes pour métriques
        self.latencies = deque(maxlen=window_size)
        self.confidences = deque(maxlen=window_size)
        self.errors = deque(maxlen=window_size)
        self.fallbacks = deque(maxlen=window_size)
        
        # Compteurs globaux
        self.total_requests = 0
        self.total_errors = 0
        self.total_fallbacks = 0
        self.start_time = time.time()
        
        # Stockage des métriques
        self.metrics_history = []
        
        # Création répertoire logs
        Path("monitoring/logs").mkdir(parents=True, exist_ok=True)
        Path("monitoring/metrics").mkdir(parents=True, exist_ok=True)
        
        logger.info("PerformanceTracker initialisé avec window_size=%d", window_size)
    
    def track_request(
        self,
        latency: float,
        confidence: float,
        error: bool = False,
        fallback: bool = False,
        metadata: Optional[Dict] = None
    ):
        """
        Enregistre une requête de classification
        
        Args:
            latency: Temps de traitement en secondes
            confidence: Score de confiance [0-1]
            error: Indique si erreur s'est produite
            fallback: Indique si fallback utilisé
            metadata: Données additionnelles (modèle, mode, etc.)
        """
        self.total_requests += 1
        
        # Mise à jour fenêtres glissantes
        self.latencies.append(latency)
        self.confidences.append(confidence)
        self.errors.append(1 if error else 0)
        self.fallbacks.append(1 if fallback else 0)
        
        # Compteurs globaux
        if error:
            self.total_errors += 1
        if fallback:
            self.total_fallbacks += 1
        
        # Log si latence anormale
        if latency > 5.0:
            logger.warning(
                "Latence élevée détectée: %.2fs (requête #%d)",
                latency,
                self.total_requests
            )
        
        # Log si erreur
        if error:
            logger.error(
                "Erreur classification (requête #%d): %s",
                self.total_requests,
                metadata.get('error_message', 'Unknown') if metadata else 'Unknown'
            )
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """
        Récupère les métriques actuelles
        
        Returns:
            Dictionnaire avec toutes les métriques courantes
        """
        uptime = time.time() - self.start_time
        
        # Calcul métriques latence
        latency_metrics = {}
        if self.latencies:
            latencies_sorted = sorted(self.latencies)
            latency_metrics = {
                'mean': statistics.mean(self.latencies),
                'median': statistics.median(self.latencies),
                'p95': np.percentile(latencies_sorted, 95),
                'p99': np.percentile(latencies_sorted, 99),
                'min': min(self.latencies),
                'max': max(self.latencies)
            }
        
        # Calcul métriques confiance
        confidence_metrics = {}
        if self.confidences:
            confidence_metrics = {
                'mean': statistics.mean(self.confidences),
                'median': statistics.median(self.confidences),
                'std': statistics.stdev(self.confidences) if len(self.confidences) > 1 else 0.0
            }
        
        # Taux d'erreur et fallback
        error_rate = (sum(self.errors) / len(self.errors) * 100) if self.errors else 0.0
        fallback_rate = (sum(self.fallbacks) / len(self.fallbacks) * 100) if self.fallbacks else 0.0
        
        # Throughput
        throughput = self.total_requests / uptime if uptime > 0 else 0.0
        
        # Utilisation ressources
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': uptime,
            'total_requests': self.total_requests,
            'throughput': throughput,
            'latency': latency_metrics,
            'confidence': confidence_metrics,
            'error_rate': error_rate,
            'fallback_rate': fallback_rate,
            'total_errors': self.total_errors,
            'total_fallbacks': self.total_fallbacks,
            'resources': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_mb': memory.available / (1024 ** 2)
            }
        }
        
        return metrics
    
    def save_metrics(self, filepath: Optional[str] = None):
        """
        Sauvegarde les métriques actuelles dans un fichier JSON
        
        Args:
            filepath: Chemin du fichier (auto-généré si None)
        """
        metrics = self.get_current_metrics()
        
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"monitoring/metrics/metrics_{timestamp}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
        
        logger.info("Métriques sauvegardées: %s", filepath)
        
        # Ajouter à l'historique
        self.metrics_history.append(metrics)
    
    def check_alerts(self) -> List[Dict[str, str]]:
        """
        Vérifie si des seuils d'alerte sont dépassés
        
        Returns:
            Liste des alertes actives
        """
        alerts = []
        metrics = self.get_current_metrics()
        
        # Alerte latence élevée (p95 > 4s)
        if metrics['latency'].get('p95', 0) > 4.0:
            alerts.append({
                'severity': 'warning',
                'metric': 'latency_p95',
                'value': metrics['latency']['p95'],
                'threshold': 4.0,
                'message': f"Latence P95 élevée: {metrics['latency']['p95']:.2f}s"
            })
        
        # Alerte taux d'erreur élevé (>5%)
        if metrics['error_rate'] > 5.0:
            alerts.append({
                'severity': 'critical',
                'metric': 'error_rate',
                'value': metrics['error_rate'],
                'threshold': 5.0,
                'message': f"Taux d'erreur critique: {metrics['error_rate']:.1f}%"
            })
        
        # Alerte fallback excessif (>20%)
        if metrics['fallback_rate'] > 20.0:
            alerts.append({
                'severity': 'warning',
                'metric': 'fallback_rate',
                'value': metrics['fallback_rate'],
                'threshold': 20.0,
                'message': f"Taux fallback élevé: {metrics['fallback_rate']:.1f}%"
            })
        
        # Alerte mémoire critique (<500MB disponible)
        if metrics['resources']['memory_available_mb'] < 500:
            alerts.append({
                'severity': 'critical',
                'metric': 'memory_available',
                'value': metrics['resources']['memory_available_mb'],
                'threshold': 500,
                'message': f"Mémoire faible: {metrics['resources']['memory_available_mb']:.0f}MB"
            })
        
        # Alerte CPU élevé (>90%)
        if metrics['resources']['cpu_percent'] > 90:
            alerts.append({
                'severity': 'warning',
                'metric': 'cpu_percent',
                'value': metrics['resources']['cpu_percent'],
                'threshold': 90,
                'message': f"CPU élevé: {metrics['resources']['cpu_percent']:.1f}%"
            })
        
        # Log les alertes
        for alert in alerts:
            if alert['severity'] == 'critical':
                logger.critical("ALERTE: %s", alert['message'])
            else:
                logger.warning("ALERTE: %s", alert['message'])
        
        return alerts
    
    def generate_report(self) -> str:
        """
        Génère un rapport de performance formaté
        
        Returns:
            Rapport texte multi-lignes
        """
        metrics = self.get_current_metrics()
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║          RAPPORT DE PERFORMANCE - FREEMOBILACHAT             ║
╠══════════════════════════════════════════════════════════════╣
║ Timestamp: {metrics['timestamp']}                    
║ Uptime: {metrics['uptime_seconds'] / 3600:.1f}h                                            
╠══════════════════════════════════════════════════════════════╣
║ TRAFIC                                                       ║
╠══════════════════════════════════════════════════════════════╣
║ Total requêtes: {metrics['total_requests']:,}                                  
║ Throughput: {metrics['throughput']:.2f} req/s                               
║ Taux erreur: {metrics['error_rate']:.2f}%                                    
║ Taux fallback: {metrics['fallback_rate']:.2f}%                                  
╠══════════════════════════════════════════════════════════════╣
║ LATENCE                                                      ║
╠══════════════════════════════════════════════════════════════╣
║ Moyenne: {metrics['latency'].get('mean', 0):.3f}s                                         
║ Médiane: {metrics['latency'].get('median', 0):.3f}s                                         
║ P95: {metrics['latency'].get('p95', 0):.3f}s                                             
║ P99: {metrics['latency'].get('p99', 0):.3f}s                                             
║ Min/Max: {metrics['latency'].get('min', 0):.3f}s / {metrics['latency'].get('max', 0):.3f}s                              
╠══════════════════════════════════════════════════════════════╣
║ CONFIANCE                                                    ║
╠══════════════════════════════════════════════════════════════╣
║ Moyenne: {metrics['confidence'].get('mean', 0):.3f}                                          
║ Médiane: {metrics['confidence'].get('median', 0):.3f}                                          
║ Écart-type: {metrics['confidence'].get('std', 0):.3f}                                       
╠══════════════════════════════════════════════════════════════╣
║ RESSOURCES                                                   ║
╠══════════════════════════════════════════════════════════════╣
║ CPU: {metrics['resources']['cpu_percent']:.1f}%                                                   
║ Mémoire: {metrics['resources']['memory_percent']:.1f}% ({metrics['resources']['memory_available_mb']:.0f}MB dispo)            
╚══════════════════════════════════════════════════════════════╝
"""
        return report
    
    def reset(self):
        """Réinitialise tous les compteurs et métriques"""
        self.latencies.clear()
        self.confidences.clear()
        self.errors.clear()
        self.fallbacks.clear()
        self.total_requests = 0
        self.total_errors = 0
        self.total_fallbacks = 0
        self.start_time = time.time()
        logger.info("PerformanceTracker réinitialisé")


class DataDriftDetector:
    """
    Détecteur de drift des données
    
    Surveille les changements dans la distribution des données
    pour détecter une dégradation potentielle du modèle
    """
    
    def __init__(self, baseline_data: pd.DataFrame):
        """
        Initialise le détecteur avec données de référence
        
        Args:
            baseline_data: DataFrame de référence pour comparaison
        """
        self.baseline_stats = self._compute_statistics(baseline_data)
        logger.info("DataDriftDetector initialisé avec %d échantillons baseline", len(baseline_data))
    
    def _compute_statistics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calcule statistiques de distribution"""
        stats = {}
        
        # Longueur moyenne des tweets
        if 'text_length' in data.columns:
            stats['text_length'] = {
                'mean': data['text_length'].mean(),
                'std': data['text_length'].std(),
                'median': data['text_length'].median()
            }
        
        # Distribution des sentiments
        if 'sentiment' in data.columns:
            stats['sentiment_dist'] = data['sentiment'].value_counts(normalize=True).to_dict()
        
        # Distribution des intentions
        if 'intention' in data.columns:
            stats['intention_dist'] = data['intention'].value_counts(normalize=True).to_dict()
        
        return stats
    
    def detect_drift(self, current_data: pd.DataFrame, threshold: float = 0.15) -> Dict[str, Any]:
        """
        Détecte le drift par rapport au baseline
        
        Args:
            current_data: Données actuelles à comparer
            threshold: Seuil de différence acceptable (15% par défaut)
            
        Returns:
            Rapport de drift avec alertes
        """
        current_stats = self._compute_statistics(current_data)
        drift_report = {'drift_detected': False, 'details': []}
        
        # Vérifier drift longueur texte
        if 'text_length' in current_stats and 'text_length' in self.baseline_stats:
            baseline_mean = self.baseline_stats['text_length']['mean']
            current_mean = current_stats['text_length']['mean']
            diff_pct = abs(current_mean - baseline_mean) / baseline_mean
            
            if diff_pct > threshold:
                drift_report['drift_detected'] = True
                drift_report['details'].append({
                    'feature': 'text_length',
                    'baseline': baseline_mean,
                    'current': current_mean,
                    'diff_pct': diff_pct * 100
                })
        
        # Vérifier drift distribution sentiments
        if 'sentiment_dist' in current_stats and 'sentiment_dist' in self.baseline_stats:
            for sentiment in self.baseline_stats['sentiment_dist']:
                baseline_pct = self.baseline_stats['sentiment_dist'].get(sentiment, 0)
                current_pct = current_stats['sentiment_dist'].get(sentiment, 0)
                diff = abs(current_pct - baseline_pct)
                
                if diff > threshold:
                    drift_report['drift_detected'] = True
                    drift_report['details'].append({
                        'feature': f'sentiment_{sentiment}',
                        'baseline': baseline_pct,
                        'current': current_pct,
                        'diff_pct': diff * 100
                    })
        
        if drift_report['drift_detected']:
            logger.warning("DRIFT DÉTECTÉ: %d anomalies", len(drift_report['details']))
        
        return drift_report


# Fonction utilitaire pour intégration Streamlit
def create_streamlit_dashboard(tracker: PerformanceTracker):
    """
    Crée un dashboard Streamlit avec métriques temps réel
    
    Args:
        tracker: Instance de PerformanceTracker
    """
    import streamlit as st
    
    st.header("📊 Performance Monitoring")
    
    metrics = tracker.get_current_metrics()
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Requêtes",
            f"{metrics['total_requests']:,}",
            f"{metrics['throughput']:.1f} req/s"
        )
    
    with col2:
        st.metric(
            "Latence P95",
            f"{metrics['latency'].get('p95', 0):.2f}s",
            delta=None
        )
    
    with col3:
        st.metric(
            "Taux Erreur",
            f"{metrics['error_rate']:.1f}%",
            delta=-metrics['error_rate'] if metrics['error_rate'] < 5 else metrics['error_rate'],
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            "Confiance Moy.",
            f"{metrics['confidence'].get('mean', 0):.2f}",
            delta=None
        )
    
    # Alertes
    alerts = tracker.check_alerts()
    if alerts:
        st.warning(f"⚠️ {len(alerts)} alertes actives")
        for alert in alerts:
            st.error(f"**{alert['metric']}**: {alert['message']}")
    else:
        st.success("✅ Aucune alerte")
    
    # Rapport détaillé
    with st.expander("📋 Rapport Détaillé"):
        st.code(tracker.generate_report())


if __name__ == "__main__":
    # Test du tracker
    tracker = PerformanceTracker(window_size=100)
    
    # Simulation de requêtes
    import random
    for i in range(50):
        tracker.track_request(
            latency=random.uniform(0.5, 3.0),
            confidence=random.uniform(0.7, 0.95),
            error=random.random() < 0.02,
            fallback=random.random() < 0.1
        )
    
    # Affichage rapport
    print(tracker.generate_report())
    
    # Vérification alertes
    alerts = tracker.check_alerts()
    print(f"\n{len(alerts)} alertes détectées")
    
    # Sauvegarde métriques
    tracker.save_metrics()
