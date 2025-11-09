"""
Script de Validation du Dataset d'Entraînement
"""
import pandas as pd
import os
from datetime import datetime

print("\n" + "="*80)
print("  VALIDATION DU DATASET D'ENTRAÎNEMENT")
print("="*80 + "\n")

dataset_path = "data/training/train_dataset.csv"

# Vérifier l'existence
if not os.path.exists(dataset_path):
    print(f"❌ Fichier non trouvé: {dataset_path}")
    print("   Le script de génération n'a pas encore terminé.\n")
    exit(1)

# Chargement
print(f"📂 Chargement: {dataset_path}")
df = pd.read_csv(dataset_path)

file_size = os.path.getsize(dataset_path) / 1024 / 1024
file_time = datetime.fromtimestamp(os.path.getmtime(dataset_path))

print(f"✅ Fichier chargé")
print(f"   Taille: {file_size:.2f} MB")
print(f"   Modifié: {file_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

# Colonnes requises
colonnes_requises = [
    'sentiment', 'catégorie', 'priority', 'urgent', 
    'besoin_reponse', 'estimation_resolution', 'réclamations'
]

colonnes_base = ['tweet_id', 'author', 'text', 'date', 'url']

print("="*80)
print("  RÉSULTATS DE VALIDATION")
print("="*80 + "\n")

# 1. Taille du dataset
print(f"📊 TAILLE DU DATASET")
taille_ok = 2600 <= len(df) <= 3500
status = "✅" if taille_ok else "❌"
print(f"   {status} Nombre de tweets: {len(df):,} (objectif: 2600-3500)")

if len(df) < 2600:
    print(f"   ⚠️  Moins de 2600 tweets - Génération incomplète")
elif len(df) > 3500:
    print(f"   ⚠️  Plus de 3500 tweets - Considérer un échantillonnage")
print()

# 2. Colonnes
print(f"📋 COLONNES")
print(f"   Total: {len(df.columns)}")
print(f"   Liste: {df.columns.tolist()}\n")

# Vérifier colonnes requises
colonnes_manquantes = [col for col in colonnes_requises if col not in df.columns]
colonnes_base_manquantes = [col for col in colonnes_base if col not in df.columns]

if colonnes_manquantes:
    print(f"   ❌ Colonnes KPIs manquantes: {colonnes_manquantes}")
else:
    print(f"   ✅ Toutes les colonnes KPIs présentes ({len(colonnes_requises)})")

if colonnes_base_manquantes:
    print(f"   ⚠️  Colonnes de base manquantes: {colonnes_base_manquantes}")
else:
    print(f"   ✅ Toutes les colonnes de base présentes ({len(colonnes_base)})")
print()

# 3. Valeurs nulles
print(f"🔍 VALEURS NULLES")
valeurs_nulles = df[colonnes_requises].isnull().sum()
has_nulls = valeurs_nulles.sum() > 0

if has_nulls:
    print(f"   ❌ Valeurs nulles détectées:")
    for col, count in valeurs_nulles.items():
        if count > 0:
            print(f"      - {col}: {count} ({count/len(df)*100:.1f}%)")
else:
    print(f"   ✅ Aucune valeur nulle dans les colonnes KPIs")
print()

# 4. Distribution
print(f"📈 DISTRIBUTION DES KPIs")

if 'sentiment' in df.columns:
    print(f"\n   Sentiment:")
    for val, count in df['sentiment'].value_counts().items():
        pct = count/len(df)*100
        print(f"      - {val}: {count:,} ({pct:.1f}%)")

if 'réclamations' in df.columns:
    print(f"\n   Réclamations:")
    for val, count in df['réclamations'].value_counts().items():
        pct = count/len(df)*100
        print(f"      - {val}: {count:,} ({pct:.1f}%)")

if 'priority' in df.columns:
    print(f"\n   Priority:")
    for val, count in df['priority'].value_counts().items():
        pct = count/len(df)*100
        print(f"      - {val}: {count:,} ({pct:.1f}%)")

if 'urgent' in df.columns:
    urgent_count = df['urgent'].sum()
    print(f"\n   Urgent:")
    print(f"      - True: {urgent_count:,} ({urgent_count/len(df)*100:.1f}%)")
    print(f"      - False: {len(df)-urgent_count:,} ({(len(df)-urgent_count)/len(df)*100:.1f}%)")

if 'besoin_reponse' in df.columns:
    besoin_count = df['besoin_reponse'].sum()
    print(f"\n   Besoin Réponse:")
    print(f"      - True: {besoin_count:,} ({besoin_count/len(df)*100:.1f}%)")
    print(f"      - False: {len(df)-besoin_count:,} ({(len(df)-besoin_count)/len(df)*100:.1f}%)")

if 'estimation_resolution' in df.columns:
    print(f"\n   Estimation Résolution:")
    print(f"      - Moyenne: {df['estimation_resolution'].mean():.1f}h")
    print(f"      - Min: {df['estimation_resolution'].min():.0f}h")
    print(f"      - Max: {df['estimation_resolution'].max():.0f}h")

print()

# 5. Verdict final
print("="*80)
print("  VERDICT FINAL")
print("="*80 + "\n")

checks = {
    "Taille du dataset (2600-3500)": taille_ok,
    "Toutes les colonnes KPIs présentes": not colonnes_manquantes,
    "Toutes les colonnes de base présentes": not colonnes_base_manquantes,
    "Aucune valeur nulle": not has_nulls
}

all_ok = all(checks.values())

for check, status in checks.items():
    symbol = "✅" if status else "❌"
    print(f"   {symbol} {check}")

print()
if all_ok:
    print("🎉 " + "="*76)
    print("   DATASET VALIDE - PRÊT POUR L'ENTRAÎNEMENT")
    print("="*80 + "\n")
else:
    print("⚠️  " + "="*76)
    print("   DATASET INCOMPLET - VÉRIFIER LES ERREURS CI-DESSUS")
    print("="*80 + "\n")

# Exemples
print("📝 EXEMPLES DE TWEETS:\n")
for i in range(min(3, len(df))):
    row = df.iloc[i]
    print(f"   Tweet {i+1}:")
    print(f"   Text: {row.get('text', '')[:100]}...")
    if 'sentiment' in df.columns:
        print(f"   Sentiment: {row.get('sentiment', 'N/A')}")
    if 'catégorie' in df.columns:
        print(f"   Catégorie: {row.get('catégorie', 'N/A')}")
    if 'réclamations' in df.columns:
        print(f"   Réclamation: {row.get('réclamations', 'N/A')}")
    print()

