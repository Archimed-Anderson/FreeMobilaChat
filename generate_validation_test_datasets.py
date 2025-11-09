"""
📊 ÉTAPE 2: GÉNÉRATION DES DATASETS DE VALIDATION ET TEST
===========================================================
Création de datasets stratifiés pour validation et test

Splits:
- Train: 70% (2,100 tweets)
- Validation: 15% (450 tweets)  
- Test: 15% (450 tweets)

Stratification sur sentiment pour assurer la représentativité

Date: 2025-11-08
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import os
import json
from datetime import datetime

print("\n" + "╔" + "="*78 + "╗")
print("║" + " "*15 + "📊 ÉTAPE 2: GÉNÉRATION DATASETS VALIDATION & TEST" + " "*14 + "║")
print("║" + " "*25 + "Split Stratifié 70/15/15" + " "*26 + "║")
print("╚" + "="*78 + "╝\n")

# ============================================================================
# CONFIGURATION
# ============================================================================
CONFIG = {
    'source_file': 'data/training/train_dataset.csv',
    'output_dir': 'data/training',
    'train_ratio': 0.70,
    'val_ratio': 0.15,
    'test_ratio': 0.15,
    'random_state': 42,
    'stratify_on': 'sentiment'
}

print("⚙️  CONFIGURATION:")
print(f"   • Fichier source: {CONFIG['source_file']}")
print(f"   • Train:      {CONFIG['train_ratio']*100:.0f}%")
print(f"   • Validation: {CONFIG['val_ratio']*100:.0f}%")
print(f"   • Test:       {CONFIG['test_ratio']*100:.0f}%")
print(f"   • Stratification: {CONFIG['stratify_on']}\n")

# ============================================================================
# PHASE 1: CHARGEMENT
# ============================================================================
print("📂 [1/5] Chargement du dataset source...")
df = pd.read_csv(CONFIG['source_file'])
print(f"   ✅ {len(df):,} tweets chargés")
print(f"   Colonnes: {len(df.columns)}\n")

# ============================================================================
# PHASE 2: VÉRIFICATION DE LA DISTRIBUTION
# ============================================================================
print("📊 [2/5] Analyse de la distribution...")

print("\n   Distribution du SENTIMENT:")
for sent, count in df['sentiment'].value_counts().items():
    pct = count / len(df) * 100
    print(f"      • {sent:10s}: {count:4,} ({pct:5.1f}%)")

print("\n   Distribution de la CATÉGORIE (Top 5):")
for cat, count in df['catégorie'].value_counts().head(5).items():
    pct = count / len(df) * 100
    print(f"      • {cat:15s}: {count:4,} ({pct:5.1f}%)")

print("\n   Distribution de la PRIORITÉ:")
for pri, count in df['priority'].value_counts().items():
    pct = count / len(df) * 100
    print(f"      • {pri:10s}: {count:4,} ({pct:5.1f}%)")

print()

# ============================================================================
# PHASE 3: SPLIT STRATIFIÉ
# ============================================================================
print("🔀 [3/5] Split stratifié des données...")

# Premier split: Train vs (Val + Test)
train_df, temp_df = train_test_split(
    df,
    test_size=(CONFIG['val_ratio'] + CONFIG['test_ratio']),
    random_state=CONFIG['random_state'],
    stratify=df[CONFIG['stratify_on']]
)

# Deuxième split: Val vs Test
val_df, test_df = train_test_split(
    temp_df,
    test_size=0.5,  # 50% de temp = 15% du total
    random_state=CONFIG['random_state'],
    stratify=temp_df[CONFIG['stratify_on']]
)

print(f"   ✅ Train:      {len(train_df):4,} tweets ({len(train_df)/len(df)*100:.1f}%)")
print(f"   ✅ Validation: {len(val_df):4,} tweets ({len(val_df)/len(df)*100:.1f}%)")
print(f"   ✅ Test:       {len(test_df):4,} tweets ({len(test_df)/len(df)*100:.1f}%)")
print(f"   ✅ Total:      {len(train_df) + len(val_df) + len(test_df):4,} tweets\n")

# ============================================================================
# PHASE 4: VÉRIFICATION DE LA STRATIFICATION
# ============================================================================
print("✅ [4/5] Vérification de la stratification...")

def check_distribution(df_subset, name):
    print(f"\n   {name}:")
    for sent in df['sentiment'].unique():
        count = (df_subset['sentiment'] == sent).sum()
        pct = count / len(df_subset) * 100
        print(f"      • {sent:10s}: {count:4,} ({pct:5.1f}%)")

check_distribution(train_df, "Train")
check_distribution(val_df, "Validation")
check_distribution(test_df, "Test")

print()

# ============================================================================
# PHASE 5: SAUVEGARDE
# ============================================================================
print("💾 [5/5] Sauvegarde des datasets...")

# Sauvegarder les datasets
train_file = os.path.join(CONFIG['output_dir'], 'train_dataset_split.csv')
val_file = os.path.join(CONFIG['output_dir'], 'validation_dataset.csv')
test_file = os.path.join(CONFIG['output_dir'], 'test_dataset_split.csv')

train_df.to_csv(train_file, index=False, encoding='utf-8')
val_df.to_csv(val_file, index=False, encoding='utf-8')
test_df.to_csv(test_file, index=False, encoding='utf-8')

print(f"   ✅ Train sauvegardé:      {train_file}")
print(f"   ✅ Validation sauvegardé: {val_file}")
print(f"   ✅ Test sauvegardé:       {test_file}")

# Sauvegarder les métadonnées
metadata = {
    'date': datetime.now().isoformat(),
    'source_file': CONFIG['source_file'],
    'config': CONFIG,
    'splits': {
        'train': {
            'size': len(train_df),
            'percentage': round(len(train_df)/len(df)*100, 2),
            'sentiment_distribution': train_df['sentiment'].value_counts().to_dict()
        },
        'validation': {
            'size': len(val_df),
            'percentage': round(len(val_df)/len(df)*100, 2),
            'sentiment_distribution': val_df['sentiment'].value_counts().to_dict()
        },
        'test': {
            'size': len(test_df),
            'percentage': round(len(test_df)/len(df)*100, 2),
            'sentiment_distribution': test_df['sentiment'].value_counts().to_dict()
        }
    }
}

metadata_file = os.path.join(CONFIG['output_dir'], 'dataset_splits_metadata.json')
with open(metadata_file, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print(f"   ✅ Métadonnées sauvegardées: {metadata_file}\n")

# ============================================================================
# RÉSUMÉ FINAL
# ============================================================================
print("╔" + "="*78 + "╗")
print("║" + " "*25 + "✅ GÉNÉRATION RÉUSSIE!" + " "*27 + "║")
print("╚" + "="*78 + "╝\n")

print("📊 STATISTIQUES DES DATASETS:\n")

print("   TRAIN:")
print(f"      • Fichier: {os.path.basename(train_file)}")
print(f"      • Lignes:  {len(train_df):,}")
print(f"      • Taille:  {os.path.getsize(train_file) / 1024:.1f} KB")

print("\n   VALIDATION:")
print(f"      • Fichier: {os.path.basename(val_file)}")
print(f"      • Lignes:  {len(val_df):,}")
print(f"      • Taille:  {os.path.getsize(val_file) / 1024:.1f} KB")

print("\n   TEST:")
print(f"      • Fichier: {os.path.basename(test_file)}")
print(f"      • Lignes:  {len(test_df):,}")
print(f"      • Taille:  {os.path.getsize(test_file) / 1024:.1f} KB")

print("\n🎯 QUALITÉ DE LA STRATIFICATION:")

# Vérifier l'écart de distribution entre les datasets
train_dist = train_df['sentiment'].value_counts(normalize=True).sort_index()
val_dist = val_df['sentiment'].value_counts(normalize=True).sort_index()
test_dist = test_df['sentiment'].value_counts(normalize=True).sort_index()

print("\n   Écarts de distribution (Train vs Val vs Test):")
for sent in sorted(df['sentiment'].unique()):
    if sent in train_dist.index and sent in val_dist.index and sent in test_dist.index:
        train_pct = train_dist[sent] * 100
        val_pct = val_dist[sent] * 100
        test_pct = test_dist[sent] * 100
        max_diff = max(abs(train_pct - val_pct), abs(train_pct - test_pct), abs(val_pct - test_pct))
        status = "✅" if max_diff < 5 else "⚠️"
        print(f"      {status} {sent:10s}: Train={train_pct:.1f}% | Val={val_pct:.1f}% | Test={test_pct:.1f}% | Δmax={max_diff:.1f}%")

print("\n✅ DATASETS PRÊTS POUR:")
print("   • Entraînement du modèle")
print("   • Validation pendant l'entraînement")
print("   • Test final pour évaluation objective")
print("   • Comparaison de modèles")

print("\n" + "="*80)
print("  🎉 ÉTAPE 2 COMPLÉTÉE AVEC SUCCÈS!")
print("="*80 + "\n")

print("📖 PROCHAINE ÉTAPE:")
print("   → Étape 3: Créer des scénarios de test détaillés\n")

