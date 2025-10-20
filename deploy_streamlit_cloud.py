#!/usr/bin/env python3
"""
Script de déploiement sur Streamlit Cloud
"""

import subprocess
import sys
import time

def deploy_streamlit_cloud():
    """Déploiement sur Streamlit Cloud"""
    print("=" * 60)
    print("    DEPLOIEMENT STREAMLIT CLOUD")
    print("=" * 60)
    
    print("\n[1/3] Vérification du repository GitHub...")
    try:
        result = subprocess.run(["git", "remote", "-v"], capture_output=True, text=True)
        if "github.com" in result.stdout:
            print("✓ Repository GitHub configuré")
        else:
            print("✗ Repository GitHub non trouvé")
            return False
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False
    
    print("\n[2/3] Vérification de la structure du projet...")
    required_files = [
        "streamlit_app/app.py",
        "streamlit_app/pages/analyse_intelligente.py",
        "streamlit_app/pages/analyse_old.py",
        "streamlit_app/pages/resultat.py",
        "streamlit_app/.streamlit/config.toml"
    ]
    
    for file in required_files:
        try:
            with open(file, 'r') as f:
                print(f"✓ {file}")
        except FileNotFoundError:
            print(f"✗ {file} manquant")
            return False
    
    print("\n[3/3] Instructions de déploiement...")
    print("\n" + "=" * 60)
    print("    INSTRUCTIONS STREAMLIT CLOUD")
    print("=" * 60)
    print("\n1. Aller sur https://share.streamlit.io")
    print("2. Se connecter avec votre compte GitHub")
    print("3. Cliquer sur 'New app'")
    print("4. Sélectionner le repository: Archimed-Anderson/FreeMobilaChat")
    print("5. Sélectionner la branche: main")
    print("6. Chemin principal: streamlit_app/app.py")
    print("7. Cliquer sur 'Deploy'")
    print("\nURL de déploiement: https://freemobilachat.streamlit.app")
    
    print("\n✓ Déploiement Streamlit Cloud prêt !")
    return True

if __name__ == "__main__":
    deploy_streamlit_cloud()