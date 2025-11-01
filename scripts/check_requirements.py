"""
Script de Vérification des Prérequis
Vérifie que toutes les dépendances sont installées
"""

import sys

print("="*70)
print("VÉRIFICATION DES PRÉREQUIS - ANALYSE TWEETS FREE MOBILE")
print("="*70)

# Liste des bibliothèques requises
required_libraries = {
    'pandas': 'Manipulation de données',
    'numpy': 'Calculs numériques',
    'matplotlib': 'Visualisations de base',
    'seaborn': 'Visualisations avancées',
    'wordcloud': 'Nuages de mots',
    'sklearn': 'Machine Learning (TF-IDF)',
    'reportlab': 'Génération PDF',
    'squarify': 'Treemaps'
}

missing = []
installed = []

print(f"\n📦 Vérification des bibliothèques...")
print("-" * 70)

for lib, description in required_libraries.items():
    try:
        __import__(lib)
        print(f"✅ {lib:15s} - {description}")
        installed.append(lib)
    except ImportError:
        print(f"❌ {lib:15s} - {description} [MANQUANT]")
        missing.append(lib)

print("-" * 70)

if missing:
    print(f"\n❌ {len(missing)} bibliothèque(s) manquante(s):")
    for lib in missing:
        print(f"   - {lib}")
    
    print(f"\n💡 Pour installer les bibliothèques manquantes:")
    print(f"   pip install {' '.join(missing)}")
    sys.exit(1)
else:
    print(f"\n✅ Toutes les bibliothèques sont installées ({len(installed)}/{ len(required_libraries)})")

# Vérifier la structure des dossiers
import os

print(f"\n📁 Vérification de la structure des dossiers...")
print("-" * 70)

folders = {
    'data/raw': 'Données sources (CSV)',
    'data/processed': 'Données nettoyées',
    'figures': 'Visualisations PNG',
    'scripts': 'Code Python'
}

for folder, description in folders.items():
    if os.path.exists(folder):
        print(f"✅ {folder:20s} - {description}")
    else:
        print(f"⚠️  {folder:20s} - {description} [SERA CRÉÉ]")
        os.makedirs(folder, exist_ok=True)
        print(f"   → Dossier créé")

# Vérifier le fichier CSV
csv_path = "data/raw/free_tweet_export.csv"
print(f"\n📄 Vérification du fichier de données...")
print("-" * 70)

if os.path.exists(csv_path):
    import pandas as pd
    try:
        df = pd.read_csv(csv_path)
        print(f"✅ {csv_path}")
        print(f"   - Lignes: {len(df):,}")
        print(f"   - Colonnes: {len(df.columns)}")
        print(f"   - Colonnes disponibles: {', '.join(df.columns[:5])}...")
    except Exception as e:
        print(f"⚠️  Erreur lors de la lecture du CSV: {e}")
else:
    print(f"⚠️  {csv_path} [NON TROUVÉ]")
    print(f"   → Un dataset de démonstration sera créé automatiquement")

print(f"\n" + "="*70)
print(f"✅ VÉRIFICATION TERMINÉE - SYSTÈME PRÊT")
print(f"="*70)
print(f"\n🚀 Pour lancer l'analyse complète:")
print(f"   python scripts/run_complete_analysis.py")
