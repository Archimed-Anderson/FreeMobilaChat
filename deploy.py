"""
Script de déploiement automatisé pour FreeMobilaChat
Supporte Streamlit Cloud, Vercel et Heroku
"""

import os
import subprocess
import sys
import json

def check_requirements():
    """Vérifie que tous les fichiers requis sont présents"""
    required_files = [
        "streamlit_app/app.py",
        "requirements.txt",
        "vercel.json",
        "Procfile",
        "runtime.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"ERREUR: Fichiers manquants: {missing_files}")
        return False
    
    print("OK: Tous les fichiers requis sont presents")
    return True

def deploy_streamlit_cloud():
    """Instructions pour déployer sur Streamlit Cloud"""
    print("\nDeploiement sur Streamlit Cloud")
    print("=" * 50)
    print("1. Allez sur https://share.streamlit.io/")
    print("2. Connectez votre compte GitHub")
    print("3. Selectionnez le repository: Archimed-Anderson/FreeMobilaChat")
    print("4. Definissez le chemin principal: streamlit_app/app.py")
    print("5. Cliquez sur 'Deploy'")
    print("\nVotre application sera disponible a: https://freemobilachat.streamlit.app")

def deploy_vercel():
    """Instructions pour déployer sur Vercel"""
    print("\nDeploiement sur Vercel")
    print("=" * 50)
    print("1. Allez sur https://vercel.com/")
    print("2. Connectez votre compte GitHub")
    print("3. Importez le repository: Archimed-Anderson/FreeMobilaChat")
    print("4. Vercel detectera automatiquement la configuration")
    print("5. Cliquez sur 'Deploy'")
    print("\nVotre application sera disponible a: https://freemobilachat.vercel.app")

def deploy_heroku():
    """Instructions pour déployer sur Heroku"""
    print("\nDeploiement sur Heroku")
    print("=" * 50)
    print("1. Installez Heroku CLI")
    print("2. Connectez-vous: heroku login")
    print("3. Creez l'app: heroku create freemobilachat")
    print("4. Deployez: git push heroku main")
    print("\nVotre application sera disponible a: https://freemobilachat.herokuapp.com")

def show_deployment_status():
    """Affiche le statut des fichiers de deploiement"""
    print("\nStatut des Fichiers de Deploiement")
    print("=" * 50)
    
    files_status = {
        "streamlit_app/app.py": "OK: Application principale",
        "requirements.txt": "OK: Dependances Python",
        "vercel.json": "OK: Configuration Vercel",
        "Procfile": "OK: Configuration Heroku",
        "runtime.txt": "OK: Version Python Heroku",
        ".streamlit/config.toml": "OK: Configuration Streamlit"
    }
    
    for file, status in files_status.items():
        if os.path.exists(file):
            print(f"{status}: {file}")
        else:
            print(f"MANQUANT: {file}")

def main():
    """Fonction principale"""
    print("FreeMobilaChat - Script de Deploiement")
    print("=" * 50)
    
    # Verifier les prerequis
    if not check_requirements():
        print("\nERREUR: Deploiement impossible - Fichiers manquants")
        return
    
    # Afficher le statut
    show_deployment_status()
    
    # Afficher les options de déploiement
    print("\nOptions de Deploiement Disponibles")
    print("=" * 50)
    print("1. Streamlit Cloud (Recommandé)")
    print("2. Vercel")
    print("3. Heroku")
    print("4. Afficher toutes les instructions")
    
    choice = input("\nChoisissez une option (1-4): ").strip()
    
    if choice == "1":
        deploy_streamlit_cloud()
    elif choice == "2":
        deploy_vercel()
    elif choice == "3":
        deploy_heroku()
    elif choice == "4":
        deploy_streamlit_cloud()
        deploy_vercel()
        deploy_heroku()
    else:
        print("Option invalide")
    
    print("\nInstructions de deploiement affichees !")
    print("Consultez DEPLOYMENT_GUIDE.md pour plus de details.")

if __name__ == "__main__":
    main()
