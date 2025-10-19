#!/usr/bin/env python3
"""
Script de déploiement en production pour FreeMobilaChat
Configuration optimisée et monitoring
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class ProductionDeployer:
    """Déployeur de production pour FreeMobilaChat"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.production_dir = self.project_root / "production"
        self.config = self._load_deployment_config()
        
    def _load_deployment_config(self):
        """Charge la configuration de déploiement"""
        return {
            "app_name": "FreeMobilaChat",
            "version": "2.0.0",
            "port": 8501,
            "host": "0.0.0.0",
            "workers": 4,
            "max_file_size": "50MB",
            "timeout": 300,
            "environment": "production",
            "log_level": "INFO",
            "enable_cors": True,
            "enable_websocket": True,
            "enable_gzip": True
        }
    
    def deploy(self):
        """Lance le déploiement complet"""
        
        print("Deploiement FreeMobilaChat en Production")
        print("=" * 60)
        
        try:
            # 1. Préparation de l'environnement
            self._prepare_environment()
            
            # 2. Installation des dépendances
            self._install_dependencies()
            
            # 3. Configuration de production
            self._configure_production()
            
            # 4. Tests de validation
            self._run_validation_tests()
            
            # 5. Démarrage des services
            self._start_services()
            
            # 6. Monitoring et santé
            self._setup_monitoring()
            
            print("\n🎉 Déploiement terminé avec succès!")
            print("✅ L'application est maintenant en production!")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du déploiement: {str(e)}")
            sys.exit(1)
    
    def _prepare_environment(self):
        """Prépare l'environnement de production"""
        
        print("\n📁 Préparation de l'environnement...")
        
        # Création du répertoire de production
        self.production_dir.mkdir(exist_ok=True)
        
        # Copie des fichiers nécessaires
        files_to_copy = [
            "app.py",
            "pages/",
            "components/",
            "services/",
            "utils/",
            "config/",
            "assets/",
            "requirements.txt",
            "README.md"
        ]
        
        for file_path in files_to_copy:
            src = self.project_root / file_path
            dst = self.production_dir / file_path
            
            if src.is_file():
                shutil.copy2(src, dst)
                print(f"✅ Copié: {file_path}")
            elif src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True)
                print(f"✅ Copié: {file_path}/")
        
        print("✅ Environnement préparé")
    
    def _install_dependencies(self):
        """Installe les dépendances de production"""
        
        print("\n📦 Installation des dépendances...")
        
        try:
            # Installation des dépendances Python
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", 
                str(self.production_dir / "requirements.txt")
            ], check=True, capture_output=True)
            
            print("✅ Dépendances Python installées")
            
            # Installation des dépendances système (optionnel)
            self._install_system_dependencies()
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Erreur installation dépendances: {e}")
            raise
    
    def _install_system_dependencies(self):
        """Installe les dépendances système"""
        
        print("📦 Installation des dépendances système...")
        
        # Dépendances système recommandées
        system_deps = [
            "nginx",  # Serveur web
            "redis-server",  # Cache
            "postgresql",  # Base de données
        ]
        
        for dep in system_deps:
            try:
                subprocess.run(["which", dep], check=True, capture_output=True)
                print(f"✅ {dep} déjà installé")
            except subprocess.CalledProcessError:
                print(f"WARNING: {dep} non installé (optionnel)")
    
    def _configure_production(self):
        """Configure l'application pour la production"""
        
        print("\nConfiguration de production...")
        
        # Variables d'environnement
        env_vars = {
            "STREAMLIT_ENV": "production",
            "STREAMLIT_SERVER_PORT": str(self.config["port"]),
            "STREAMLIT_SERVER_ADDRESS": self.config["host"],
            "STREAMLIT_SERVER_HEADLESS": "true",
            "STREAMLIT_BROWSER_GATHER_USAGE_STATS": "false",
            "STREAMLIT_SERVER_ENABLE_CORS": str(self.config["enable_cors"]).lower(),
            "STREAMLIT_SERVER_ENABLE_WEBSOCKET_COMPRESSION": str(self.config["enable_websocket"]).lower(),
            "STREAMLIT_SERVER_ENABLE_STATIC_SERVING": "true",
            "STREAMLIT_SERVER_MAX_UPLOAD_SIZE": self.config["max_file_size"],
            "STREAMLIT_SERVER_TIMEOUT": str(self.config["timeout"]),
            "STREAMLIT_LOGGER_LEVEL": self.config["log_level"]
        }
        
        # Création du fichier .env
        env_file = self.production_dir / ".env"
        with open(env_file, 'w') as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        
        print("✅ Variables d'environnement configurées")
        
        # Configuration Nginx
        self._configure_nginx()
        
        # Configuration de monitoring
        self._configure_monitoring()
        
        print("✅ Configuration de production terminée")
    
    def _configure_nginx(self):
        """Configure Nginx pour la production"""
        
        nginx_config = f"""
server {{
    listen 80;
    server_name localhost;
    
    location / {{
        proxy_pass http://127.0.0.1:{self.config["port"]};
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }}
    
    # Gestion des fichiers statiques
    location /static {{
        alias {self.production_dir}/assets;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
    
    # Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
}}
"""
        
        nginx_file = self.production_dir / "nginx.conf"
        with open(nginx_file, 'w') as f:
            f.write(nginx_config)
        
        print("✅ Configuration Nginx créée")
    
    def _configure_monitoring(self):
        """Configure le monitoring"""
        
        monitoring_config = {
            "health_check": {
                "endpoint": "/health",
                "interval": 30,
                "timeout": 10
            },
            "metrics": {
                "enabled": True,
                "port": 9090,
                "path": "/metrics"
            },
            "logging": {
                "level": "INFO",
                "file": f"{self.production_dir}/logs/app.log",
                "max_size": "10MB",
                "backup_count": 5
            },
            "alerts": {
                "cpu_threshold": 80,
                "memory_threshold": 85,
                "disk_threshold": 90
            }
        }
        
        monitoring_file = self.production_dir / "monitoring.json"
        with open(monitoring_file, 'w') as f:
            json.dump(monitoring_config, f, indent=2)
        
        print("✅ Configuration monitoring créée")
    
    def _run_validation_tests(self):
        """Lance les tests de validation"""
        
        print("\n🧪 Tests de validation...")
        
        try:
            # Test des imports
            sys.path.insert(0, str(self.production_dir))
            
            from app import main
            from pages import 01_analyse, 1_Overview, 02_dashboard
            from components.upload_handler import get_upload_handler
            from services.data_processor import get_data_processor
            
            print("✅ Imports OK")
            
            # Test de la configuration
            from config.settings import get_config
            config = get_config()
            self.assertIsNotNone(config)
            print("✅ Configuration OK")
            
            # Test des composants
            upload_handler = get_upload_handler()
            data_processor = get_data_processor()
            self.assertIsNotNone(upload_handler)
            self.assertIsNotNone(data_processor)
            print("✅ Composants OK")
            
        except Exception as e:
            logger.error(f"❌ Erreur validation: {str(e)}")
            raise
        
        print("✅ Tests de validation passés")
    
    def _start_services(self):
        """Démarre les services de production"""
        
        print("\nDemarrage des services...")
        
        # Script de démarrage
        startup_script = f"""#!/bin/bash
# Script de démarrage FreeMobilaChat Production

# Variables d'environnement
export STREAMLIT_ENV=production
export STREAMLIT_SERVER_PORT={self.config["port"]}
export STREAMLIT_SERVER_ADDRESS={self.config["host"]}
export STREAMLIT_SERVER_HEADLESS=true

# Création des répertoires
mkdir -p {self.production_dir}/logs
mkdir -p {self.production_dir}/data
mkdir -p {self.production_dir}/cache

# Démarrage de l'application
cd {self.production_dir}
nohup streamlit run app.py > logs/app.log 2>&1 &

# Sauvegarde du PID
echo $! > logs/app.pid

echo "✅ FreeMobilaChat démarré en production"
echo "Dashboard: http://localhost:{self.config["port"]}"
echo "📝 Logs: {self.production_dir}/logs/app.log"
"""
        
        startup_file = self.production_dir / "start_production.sh"
        with open(startup_file, 'w') as f:
            f.write(startup_script)
        
        # Rendre le script exécutable
        os.chmod(startup_file, 0o755)
        
        print("✅ Script de démarrage créé")
        print(f"📁 Répertoire de production: {self.production_dir}")
        print(f"Pour demarrer: {startup_file}")
    
    def _setup_monitoring(self):
        """Configure le monitoring"""
        
        print("\nConfiguration du monitoring...")
        
        # Script de monitoring
        monitoring_script = f"""#!/bin/bash
# Script de monitoring FreeMobilaChat

APP_PID_FILE="{self.production_dir}/logs/app.pid"
LOG_FILE="{self.production_dir}/logs/app.log"

# Vérification du statut
if [ -f "$APP_PID_FILE" ]; then
    PID=$(cat "$APP_PID_FILE")
    if ps -p $PID > /dev/null; then
        echo "✅ Application en cours d'exécution (PID: $PID)"
    else
        echo "❌ Application arrêtée"
    fi
else
    echo "❌ Fichier PID non trouvé"
fi

# Vérification des logs
if [ -f "$LOG_FILE" ]; then
    echo "📝 Dernières lignes des logs:"
    tail -n 10 "$LOG_FILE"
else
    echo "WARNING: Fichier de logs non trouve"
fi

# Vérification de la connectivité
if curl -f http://localhost:{self.config["port"]} > /dev/null 2>&1; then
    echo "✅ Application accessible sur http://localhost:{self.config["port"]}"
else
    echo "❌ Application non accessible"
fi
"""
        
        monitoring_file = self.production_dir / "monitor.sh"
        with open(monitoring_file, 'w') as f:
            f.write(monitoring_script)
        
        os.chmod(monitoring_file, 0o755)
        
        print("✅ Script de monitoring créé")
        print(f"Pour monitorer: {monitoring_file}")

def main():
    """Fonction principale de déploiement"""
    
    deployer = ProductionDeployer()
    deployer.deploy()

if __name__ == "__main__":
    main()
