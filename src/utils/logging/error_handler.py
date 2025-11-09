"""
Gestionnaire d'erreurs et logging avancé
Journalisation des erreurs, performances et rapports
"""

import logging
import sys
import json
import traceback
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from functools import wraps


class ErrorHandler:
    """Gestionnaire centralisé des erreurs et du logging"""
    
    def __init__(self, 
                 log_dir: str = "logs",
                 log_level: int = logging.INFO,
                 enable_console: bool = True):
        """
        Initialise le gestionnaire d'erreurs
        
        Args:
            log_dir: Répertoire pour les fichiers de logs
            log_level: Niveau de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            enable_console: Activer l'affichage console
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.log_level = log_level
        self.enable_console = enable_console
        
        # Créer le logger principal
        self.logger = self._setup_logger()
        
        # Statistiques d'erreurs
        self.error_stats = {
            'total_errors': 0,
            'by_type': {},
            'by_module': {},
            'last_error': None
        }
    
    def _setup_logger(self) -> logging.Logger:
        """Configure le logger avec handlers fichier et console"""
        logger = logging.getLogger('FreeMobilaChat')
        logger.setLevel(self.log_level)
        
        # Éviter les doublons de handlers
        if logger.handlers:
            logger.handlers.clear()
        
        # Format de log détaillé
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler fichier avec rotation
        log_file = self.log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Handler console
        if self.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def log_error(self, 
                  error: Exception, 
                  context: Optional[Dict[str, Any]] = None,
                  module_name: Optional[str] = None) -> None:
        """
        Enregistre une erreur avec contexte
        
        Args:
            error: Exception levée
            context: Contexte additionnel (paramètres, état, etc.)
            module_name: Nom du module où l'erreur s'est produite
        """
        error_type = type(error).__name__
        error_message = str(error)
        error_traceback = traceback.format_exc()
        
        # Mettre à jour les statistiques
        self.error_stats['total_errors'] += 1
        self.error_stats['by_type'][error_type] = \
            self.error_stats['by_type'].get(error_type, 0) + 1
        
        if module_name:
            self.error_stats['by_module'][module_name] = \
                self.error_stats['by_module'].get(module_name, 0) + 1
        
        self.error_stats['last_error'] = {
            'type': error_type,
            'message': error_message,
            'timestamp': datetime.now().isoformat(),
            'module': module_name
        }
        
        # Logger l'erreur
        log_entry = f"""
ERROR DETECTED:
  Type: {error_type}
  Message: {error_message}
  Module: {module_name or 'Unknown'}
  Context: {json.dumps(context or {}, indent=2, default=str)}
  Traceback:
{error_traceback}
"""
        self.logger.error(log_entry)
    
    def log_performance(self, 
                       operation: str, 
                       duration: float,
                       metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Enregistre les métriques de performance
        
        Args:
            operation: Nom de l'opération
            duration: Durée en secondes
            metadata: Métadonnées additionnelles
        """
        perf_data = {
            'operation': operation,
            'duration_seconds': round(duration, 3),
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self.logger.info(f"PERFORMANCE: {json.dumps(perf_data)}")
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques d'erreurs"""
        return self.error_stats.copy()
    
    def export_error_report(self, output_file: str = "error_report.json") -> None:
        """
        Exporte un rapport d'erreurs au format JSON
        
        Args:
            output_file: Chemin du fichier de sortie
        """
        report = {
            'generated_at': datetime.now().isoformat(),
            'statistics': self.error_stats,
            'log_directory': str(self.log_dir)
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Rapport d'erreurs exporté: {output_file}")
    
    def clear_stats(self) -> None:
        """Réinitialise les statistiques d'erreurs"""
        self.error_stats = {
            'total_errors': 0,
            'by_type': {},
            'by_module': {},
            'last_error': None
        }


def handle_errors(module_name: str = None):
    """
    Décorateur pour gérer automatiquement les erreurs
    
    Args:
        module_name: Nom du module pour le logging
        
    Example:
        @handle_errors(module_name="sentiment_analysis")
        def analyze_sentiment(text):
            # code here
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler = ErrorHandler()
                context = {
                    'function': func.__name__,
                    'args': str(args)[:200],  # Limiter la taille
                    'kwargs': str(kwargs)[:200]
                }
                error_handler.log_error(e, context, module_name or func.__module__)
                raise
        return wrapper
    return decorator


# Instance globale
_global_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Retourne l'instance globale du gestionnaire d'erreurs"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    return _global_error_handler

