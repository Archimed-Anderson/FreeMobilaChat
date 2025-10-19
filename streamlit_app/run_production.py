#!/usr/bin/env python3
"""
Script de démarrage en production pour FreeMobilaChat
Gestion des services et monitoring
"""

import os
import sys
import subprocess
import time
import signal
import psutil
from pathlib import Path
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class ProductionRunner:
    """Gestionnaire de production pour FreeMobilaChat"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.pid_file = self.project_root / "logs" / "app.pid"
        self.log_file = self.project_root / "logs" / "app.log"
        self.port = 8501
        self.host = "0.0.0.0"
        
    def start(self):
        """Démarre l'application en production"""
        
        print("Demarrage FreeMobilaChat en Production")
        print("=" * 50)
        
        # Vérification si déjà en cours d'exécution
        if self._is_running():
            print("L'application est deja en cours d'execution")
            self._show_status()
            return
        
        # Création des répertoires
        self._create_directories()
        
        # Configuration de l'environnement
        self._setup_environment()
        
        # Démarrage de l'application
        self._start_application()
        
        # Vérification du démarrage
        time.sleep(5)
        if self._is_running():
            print("Application demarree avec succes!")
            self._show_status()
        else:
            print("Echec du demarrage de l'application")
            self._show_logs()
    
    def stop(self):
        """Arrête l'application"""
        
        print("Arret de FreeMobilaChat")
        print("=" * 30)
        
        if not self._is_running():
            print("L'application n'est pas en cours d'execution")
            return
        
        try:
            # Lecture du PID
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Arrêt du processus
            process = psutil.Process(pid)
            process.terminate()
            
            # Attente de l'arrêt
            process.wait(timeout=10)
            
            # Suppression du fichier PID
            self.pid_file.unlink(missing_ok=True)
            
            print("Application arretee avec succes")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'arret: {str(e)}")
            print("Erreur lors de l'arret de l'application")
    
    def restart(self):
        """Redémarre l'application"""
        
        print("Redemarrage de FreeMobilaChat")
        print("=" * 35)
        
        self.stop()
        time.sleep(2)
        self.start()
    
    def status(self):
        """Affiche le statut de l'application"""
        
        print("Statut de FreeMobilaChat")
        print("=" * 30)
        
        self._show_status()
    
    def logs(self, lines=50):
        """Affiche les logs de l'application"""
        
        print(f"Logs de FreeMobilaChat (dernieres {lines} lignes)")
        print("=" * 50)
        
        self._show_logs(lines)
    
    def _is_running(self):
        """Vérifie si l'application est en cours d'exécution"""
        
        if not self.pid_file.exists():
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            return psutil.pid_exists(pid)
        except:
            return False
    
    def _create_directories(self):
        """Crée les répertoires nécessaires"""
        
        directories = [
            self.project_root / "logs",
            self.project_root / "data",
            self.project_root / "cache",
            self.project_root / "uploads"
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True)
            print(f"Repertoire cree: {directory}")
    
    def _setup_environment(self):
        """Configure l'environnement de production"""
        
        env_vars = {
            "STREAMLIT_ENV": "production",
            "STREAMLIT_SERVER_PORT": str(self.port),
            "STREAMLIT_SERVER_ADDRESS": self.host,
            "STREAMLIT_SERVER_HEADLESS": "true",
            "STREAMLIT_BROWSER_GATHER_USAGE_STATS": "false",
            "STREAMLIT_SERVER_ENABLE_CORS": "true",
            "STREAMLIT_SERVER_ENABLE_WEBSOCKET_COMPRESSION": "true",
            "STREAMLIT_SERVER_MAX_UPLOAD_SIZE": "50",
            "STREAMLIT_SERVER_TIMEOUT": "300",
            "STREAMLIT_LOGGER_LEVEL": "INFO"
        }
        
        for key, value in env_vars.items():
            os.environ[key] = value
        
        print("Variables d'environnement configurees")
    
    def _start_application(self):
        """Démarre l'application Streamlit"""
        
        try:
            # Commande de démarrage
            cmd = [
                sys.executable, "-m", "streamlit", "run", "app.py",
                "--server.port", str(self.port),
                "--server.address", self.host,
                "--server.headless", "true",
                "--browser.gatherUsageStats", "false"
            ]
            
            # Démarrage en arrière-plan
            with open(self.log_file, 'w') as log_file:
                process = subprocess.Popen(
                    cmd,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    cwd=str(self.project_root)
                )
            
            # Sauvegarde du PID
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))
            
            print(f"Application demarree (PID: {process.pid})")
            print(f"Dashboard: http://localhost:{self.port}")
            print(f"Logs: {self.log_file}")
            
        except Exception as e:
            logger.error(f"Erreur demarrage: {str(e)}")
            raise
    
    def _show_status(self):
        """Affiche le statut de l'application"""
        
        if self._is_running():
            try:
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                process = psutil.Process(pid)
                
                print(f"Statut: En cours d'execution")
                print(f"PID: {pid}")
                print(f"Demarrage: {datetime.fromtimestamp(process.create_time()).strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Memoire: {process.memory_info().rss / 1024 / 1024:.1f} MB")
                print(f"CPU: {process.cpu_percent():.1f}%")
                print(f"URL: http://localhost:{self.port}")
                
                # Test de connectivité
                try:
                    import requests
                    response = requests.get(f"http://localhost:{self.port}", timeout=5)
                    if response.status_code == 200:
                        print("Connectivite: OK")
                    else:
                        print(f"Connectivite: Code {response.status_code}")
                except:
                    print("Connectivite: Non accessible")
                
            except Exception as e:
                print(f"Erreur statut: {str(e)}")
        else:
            print("Statut: Arrete")
    
    def _show_logs(self, lines=50):
        """Affiche les logs de l'application"""
        
        if not self.log_file.exists():
            print("Fichier de logs non trouve")
            return
        
        try:
            with open(self.log_file, 'r') as f:
                log_lines = f.readlines()
            
            # Affichage des dernières lignes
            recent_lines = log_lines[-lines:] if len(log_lines) > lines else log_lines
            
            for line in recent_lines:
                print(line.rstrip())
                
        except Exception as e:
            print(f"Erreur lecture logs: {str(e)}")

def main():
    """Fonction principale"""
    
    if len(sys.argv) < 2:
        print("Usage: python run_production.py [start|stop|restart|status|logs]")
        print("  start   - Démarre l'application")
        print("  stop    - Arrête l'application")
        print("  restart - Redémarre l'application")
        print("  status  - Affiche le statut")
        print("  logs    - Affiche les logs")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    runner = ProductionRunner()
    
    if command == "start":
        runner.start()
    elif command == "stop":
        runner.stop()
    elif command == "restart":
        runner.restart()
    elif command == "status":
        runner.status()
    elif command == "logs":
        lines = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        runner.logs(lines)
    else:
        print(f"Commande inconnue: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
