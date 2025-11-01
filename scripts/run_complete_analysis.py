"""
Script Principal - Analyse Complète des Tweets Free Mobile
Exécute le pipeline complet: nettoyage → analyse → visualisations → rapport PDF
"""

import subprocess
import sys
import os

print("="*80)
print("PIPELINE COMPLET D'ANALYSE DES TWEETS FREE MOBILE")
print("="*80)

# Vérifier que les dossiers existent
os.makedirs('data/raw', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)
os.makedirs('figures', exist_ok=True)

# Vérifier que le fichier CSV existe
csv_path = "data/raw/free_tweet_export.csv"
if not os.path.exists(csv_path):
    print(f"\n⚠️  ATTENTION: Fichier '{csv_path}' non trouvé!")
    print(f"   Veuillez placer votre fichier 'free_tweet_export.csv' dans le dossier 'data/raw/'")
    print(f"\n   Un dataset de démonstration sera créé automatiquement...")

print(f"\n📋 ÉTAPE 1/3: Nettoyage et enrichissement des données...")
print(f"-" * 80)
result1 = subprocess.run([sys.executable, 'scripts/part1_cleaning.py'], 
                        capture_output=False)
if result1.returncode != 0:
    print(f"❌ Erreur lors du nettoyage")
    sys.exit(1)

print(f"\n📊 ÉTAPE 2/3: Calcul des KPIs et génération des visualisations...")
print(f"-" * 80)
result2 = subprocess.run([sys.executable, 'scripts/part2_analysis_viz.py'], 
                        capture_output=False)
if result2.returncode != 0:
    print(f"❌ Erreur lors de l'analyse")
    sys.exit(1)

print(f"\n📄 ÉTAPE 3/3: Génération du rapport PDF...")
print(f"-" * 80)
result3 = subprocess.run([sys.executable, 'scripts/generate_report.py'], 
                        capture_output=False)
if result3.returncode != 0:
    print(f"❌ Erreur lors de la génération du rapport")
    sys.exit(1)

print(f"\n" + "="*80)
print(f"✅ ANALYSE COMPLÈTE TERMINÉE AVEC SUCCÈS!")
print(f"="*80)
print(f"\n📦 LIVRABLES GÉNÉRÉS:")
print(f"   1. data/processed/cleaned_data.csv - Données nettoyées et enrichies")
print(f"   2. data/processed/kpis.json - KPIs calculés")
print(f"   3. figures/ - 5 visualisations PNG (volume, sentiment, wordcloud, treemap, heatmap)")
print(f"   4. Rapport_Analyse_Tweets_FreeMobile.pdf - Rapport académique final (5+ pages)")
print(f"\n🎓 Prêt pour la soutenance de master!")
