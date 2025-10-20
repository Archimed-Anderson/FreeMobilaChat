#!/usr/bin/env python3
"""
Instructions de déploiement pour FreeMobilaChat
"""

import subprocess
import sys

def show_deployment_instructions():
    """Affiche les instructions de déploiement"""
    print("=" * 60)
    print("    INSTRUCTIONS DE DEPLOIEMENT")
    print("=" * 60)
    
    print("\n[1/3] Verification du repository GitHub...")
    try:
        result = subprocess.run(["git", "remote", "-v"], capture_output=True, text=True)
        if "github.com" in result.stdout:
            print("[OK] Repository GitHub configure")
        else:
            print("[ERREUR] Repository GitHub non trouve")
            return False
    except Exception as e:
        print(f"[ERREUR] {e}")
        return False
    
    print("\n[2/3] Verification de la structure du projet...")
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
                print(f"[OK] {file}")
        except FileNotFoundError:
            print(f"[ERREUR] {file} manquant")
            return False
    
    print("\n[3/3] Instructions de deploiement...")
    print("\n" + "=" * 60)
    print("    STREAMLIT CLOUD")
    print("=" * 60)
    print("\n1. Aller sur https://share.streamlit.io")
    print("2. Se connecter avec votre compte GitHub")
    print("3. Cliquer sur 'New app'")
    print("4. Selectionner le repository: Archimed-Anderson/FreeMobilaChat")
    print("5. Selectionner la branche: main")
    print("6. Chemin principal: streamlit_app/app.py")
    print("7. Cliquer sur 'Deploy'")
    print("\nURL de deploiement: https://freemobilachat.streamlit.app")
    
    print("\n" + "=" * 60)
    print("    VERCEL")
    print("=" * 60)
    print("\n1. Aller sur https://vercel.com")
    print("2. Se connecter avec votre compte GitHub")
    print("3. Cliquer sur 'New Project'")
    print("4. Selectionner le repository: Archimed-Anderson/FreeMobilaChat")
    print("5. Framework Preset: Other")
    print("6. Build Command: (laisser vide)")
    print("7. Output Directory: (laisser vide)")
    print("8. Cliquer sur 'Deploy'")
    print("\nURL de deploiement: https://freemobilachat.vercel.app")
    
    print("\n[SUCCES] Instructions de deploiement generees !")
    return True

if __name__ == "__main__":
    show_deployment_instructions()
