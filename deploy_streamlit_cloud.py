"""
Script pour déployer l'application sur Streamlit Cloud
Alternative recommandée à Vercel pour les applications Streamlit
"""

import os
import subprocess
import sys

def deploy_to_streamlit_cloud():
    """Déploie l'application sur Streamlit Cloud"""
    
    print("🚀 Déploiement sur Streamlit Cloud...")
    
    # Vérifier que nous sommes dans le bon répertoire
    if not os.path.exists("streamlit_app/app.py"):
        print("❌ Erreur: streamlit_app/app.py non trouvé")
        return False
    
    # Créer un fichier de configuration pour Streamlit Cloud
    config_content = """
[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#CC0000"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
"""
    
    # Créer le dossier .streamlit s'il n'existe pas
    os.makedirs(".streamlit", exist_ok=True)
    
    # Écrire la configuration
    with open(".streamlit/config.toml", "w") as f:
        f.write(config_content)
    
    print("✅ Configuration Streamlit créée")
    
    # Instructions pour le déploiement manuel
    print("\n📋 Instructions pour déployer sur Streamlit Cloud:")
    print("1. Allez sur https://share.streamlit.io/")
    print("2. Connectez votre compte GitHub")
    print("3. Sélectionnez le repository: Archimed-Anderson/FreeMobilaChat")
    print("4. Définissez le chemin principal: streamlit_app/app.py")
    print("5. Cliquez sur 'Deploy'")
    
    return True

if __name__ == "__main__":
    deploy_to_streamlit_cloud()
