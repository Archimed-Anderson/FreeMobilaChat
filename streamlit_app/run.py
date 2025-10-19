#!/usr/bin/env python3
"""
Script de démarrage pour FreeMobilaChat
Gestion des environnements et configuration
"""

import os
import sys
import subprocess
import argparse
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Point d'entrée principal"""
    
    parser = argparse.ArgumentParser(description="FreeMobilaChat - Application Streamlit")
    parser.add_argument(
        "--env", 
        choices=["development", "production", "testing"],
        default="development",
        help="Environnement d'exécution"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8501,
        help="Port du serveur Streamlit"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Adresse du serveur Streamlit"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Mode debug"
    )
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Installer les dépendances"
    )
    parser.add_argument(
        "--check-config",
        action="store_true",
        help="Vérifier la configuration"
    )
    
    args = parser.parse_args()
    
    try:
        # Installation des dépendances
        if args.install_deps:
            install_dependencies()
            return
        
        # Vérification de la configuration
        if args.check_config:
            check_configuration()
            return
        
        # Démarrage de l'application
        start_application(args)
        
    except KeyboardInterrupt:
        logger.info("Arrêt de l'application par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur lors du démarrage: {str(e)}")
        sys.exit(1)

def install_dependencies():
    """Installe les dépendances Python"""
    
    logger.info("Installation des dépendances...")
    
    try:
        # Vérification de pip
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True)
        
        # Installation des dépendances
        requirements_file = Path(__file__).parent / "requirements.txt"
        
        if requirements_file.exists():
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True)
            logger.info("✅ Dépendances installées avec succès")
        else:
            logger.error("❌ Fichier requirements.txt non trouvé")
            sys.exit(1)
            
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erreur lors de l'installation: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erreur inattendue: {e}")
        sys.exit(1)

def check_configuration():
    """Vérifie la configuration de l'application"""
    
    logger.info("Vérification de la configuration...")
    
    # Vérification des modules requis
    required_modules = [
        'streamlit', 'pandas', 'plotly', 'requests', 
        'numpy', 'datetime', 'logging'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            logger.info(f"✅ {module}")
        except ImportError:
            missing_modules.append(module)
            logger.error(f"❌ {module}")
    
    if missing_modules:
        logger.error(f"Modules manquants: {', '.join(missing_modules)}")
        logger.info("Exécutez: python run.py --install-deps")
        sys.exit(1)
    
    # Vérification de la structure des dossiers
    required_dirs = [
        'config', 'components', 'pages', 'services', 
        'utils', 'assets'
    ]
    
    missing_dirs = []
    for dir_name in required_dirs:
        dir_path = Path(__file__).parent / dir_name
        if dir_path.exists():
            logger.info(f"✅ {dir_name}/")
        else:
            missing_dirs.append(dir_name)
            logger.error(f"❌ {dir_name}/")
    
    if missing_dirs:
        logger.error(f"Dossiers manquants: {', '.join(missing_dirs)}")
        sys.exit(1)
    
    # Vérification des fichiers requis
    required_files = [
        'app.py', 'requirements.txt', 'README.md'
    ]
    
    missing_files = []
    for file_name in required_files:
        file_path = Path(__file__).parent / file_name
        if file_path.exists():
            logger.info(f"✅ {file_name}")
        else:
            missing_files.append(file_name)
            logger.error(f"❌ {file_name}")
    
    if missing_files:
        logger.error(f"Fichiers manquants: {', '.join(missing_files)}")
        sys.exit(1)
    
    logger.info("✅ Configuration vérifiée avec succès")

def start_application(args):
    """Démarre l'application Streamlit"""
    
    logger.info(f"Démarrage de FreeMobilaChat en mode {args.env}")
    
    # Configuration des variables d'environnement
    os.environ["STREAMLIT_ENV"] = args.env
    
    if args.debug:
        os.environ["STREAMLIT_LOGGER_LEVEL"] = "debug"
    
    # Construction de la commande Streamlit
    cmd = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", str(args.port),
        "--server.address", args.host,
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ]
    
    # Options spécifiques à l'environnement
    if args.env == "development":
        cmd.extend(["--server.runOnSave", "true"])
    elif args.env == "production":
        cmd.extend(["--server.enableCORS", "false"])
    
    # Affichage des informations
    logger.info(f"URL: http://{args.host}:{args.port}")
    logger.info(f"Environnement: {args.env}")
    logger.info(f"Debug: {'Active' if args.debug else 'Desactive'}")
    
    # Démarrage de l'application
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erreur lors du démarrage de Streamlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Arrêt de l'application")

if __name__ == "__main__":
    main()
