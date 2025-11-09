"""
🚀 ÉTAPE 1: ENTRAÎNEMENT DU PREMIER MODÈLE
==========================================
Entraînement d'un modèle baseline simple sur le dataset d'entraînement

Approche: Classification Multi-Tâche avec TF-IDF + Logistic Regression
- Simple et rapide
- Baseline pour comparaisons futures
- Pas de dépendances GPU

Date: 2025-11-08
"""

import sys
import os
sys.path.insert(0, 'streamlit_app')

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multioutput import MultiOutputClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import pickle
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("\n" + "╔" + "="*78 + "╗")
print("║" + " "*20 + "🚀 ÉTAPE 1: ENTRAÎNEMENT PREMIER MODÈLE" + " "*18 + "║")
print("║" + " "*25 + "Modèle Baseline Multi-Tâche" + " "*24 + "║")
print("╚" + "="*78 + "╝\n")

# ============================================================================
# CONFIGURATION
# ============================================================================
CONFIG = {
    'data_file': 'data/training/train_dataset.csv',
    'output_dir': 'models/baseline',
    'test_size': 0.2,
    'random_state': 42,
    'max_features': 5000,
    'ngram_range': (1, 2)
}

# Créer le dossier de sortie
os.makedirs(CONFIG['output_dir'], exist_ok=True)

# ============================================================================
# PHASE 1: CHARGEMENT DES DONNÉES
# ============================================================================
print("📂 [1/6] Chargement du dataset...")
df = pd.read_csv(CONFIG['data_file'])
print(f"   ✅ {len(df):,} tweets chargés")
print(f"   Colonnes: {list(df.columns)}\n")

# ============================================================================
# PHASE 2: PRÉPARATION DES DONNÉES
# ============================================================================
print("🔧 [2/6] Préparation des données pour l'entraînement...")

# Features (X)
X = df['text_cleaned'].fillna('')

# Labels (y) - Multiple outputs
y_sentiment = df['sentiment']
y_categorie = df['catégorie']
y_priority = df['priority']

print(f"   ✅ Features préparées: {len(X):,} échantillons")
print(f"   ✅ Labels sentiment: {y_sentiment.nunique()} classes")
print(f"   ✅ Labels catégorie: {y_categorie.nunique()} classes")
print(f"   ✅ Labels priorité: {y_priority.nunique()} classes\n")

# ============================================================================
# PHASE 3: SPLIT TRAIN/TEST
# ============================================================================
print(f"📊 [3/6] Split des données (train {100-CONFIG['test_size']*100:.0f}% / test {CONFIG['test_size']*100:.0f}%)...")

X_train, X_test, y_sent_train, y_sent_test = train_test_split(
    X, y_sentiment, test_size=CONFIG['test_size'], random_state=CONFIG['random_state'], stratify=y_sentiment
)

_, _, y_cat_train, y_cat_test = train_test_split(
    X, y_categorie, test_size=CONFIG['test_size'], random_state=CONFIG['random_state'], stratify=y_sentiment
)

_, _, y_pri_train, y_pri_test = train_test_split(
    X, y_priority, test_size=CONFIG['test_size'], random_state=CONFIG['random_state'], stratify=y_sentiment
)

print(f"   ✅ Train: {len(X_train):,} échantillons")
print(f"   ✅ Test:  {len(X_test):,} échantillons\n")

# ============================================================================
# PHASE 4: VECTORISATION (TF-IDF)
# ============================================================================
print("🔤 [4/6] Vectorisation TF-IDF...")

vectorizer = TfidfVectorizer(
    max_features=CONFIG['max_features'],
    ngram_range=CONFIG['ngram_range'],
    min_df=2,
    max_df=0.95,
    stop_words=None  # Pas de stop words pour le français
)

print(f"   Configuration:")
print(f"   • Max features: {CONFIG['max_features']}")
print(f"   • N-grams: {CONFIG['ngram_range']}")
print(f"   • Stop words: None (français)")

X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

print(f"   ✅ Matrice TF-IDF créée: {X_train_tfidf.shape}\n")

# ============================================================================
# PHASE 5: ENTRAÎNEMENT DES MODÈLES
# ============================================================================
print("🤖 [5/6] Entraînement des classificateurs...")

# Modèle 1: Sentiment
print("   [1/3] Entraînement du classificateur de SENTIMENT...")
model_sentiment = LogisticRegression(
    max_iter=1000,
    random_state=CONFIG['random_state'],
    class_weight='balanced'
)
model_sentiment.fit(X_train_tfidf, y_sent_train)
print(f"   ✅ Modèle sentiment entraîné")

# Modèle 2: Catégorie
print("   [2/3] Entraînement du classificateur de CATÉGORIE...")
model_categorie = LogisticRegression(
    max_iter=1000,
    random_state=CONFIG['random_state'],
    class_weight='balanced'
)
model_categorie.fit(X_train_tfidf, y_cat_train)
print(f"   ✅ Modèle catégorie entraîné")

# Modèle 3: Priorité
print("   [3/3] Entraînement du classificateur de PRIORITÉ...")
model_priority = LogisticRegression(
    max_iter=1000,
    random_state=CONFIG['random_state'],
    class_weight='balanced'
)
model_priority.fit(X_train_tfidf, y_pri_train)
print(f"   ✅ Modèle priorité entraîné\n")

# ============================================================================
# PHASE 6: ÉVALUATION
# ============================================================================
print("📊 [6/6] Évaluation des modèles...")

# Prédictions
y_sent_pred = model_sentiment.predict(X_test_tfidf)
y_cat_pred = model_categorie.predict(X_test_tfidf)
y_pri_pred = model_priority.predict(X_test_tfidf)

# Métriques Sentiment
print("\n" + "="*80)
print("📊 RÉSULTATS - SENTIMENT")
print("="*80)
acc_sent = accuracy_score(y_sent_test, y_sent_pred)
print(f"\n✅ Accuracy: {acc_sent:.4f} ({acc_sent*100:.2f}%)\n")
print("Classification Report:")
print(classification_report(y_sent_test, y_sent_pred, zero_division=0))

# Métriques Catégorie
print("\n" + "="*80)
print("📊 RÉSULTATS - CATÉGORIE")
print("="*80)
acc_cat = accuracy_score(y_cat_test, y_cat_pred)
print(f"\n✅ Accuracy: {acc_cat:.4f} ({acc_cat*100:.2f}%)\n")
print("Classification Report:")
print(classification_report(y_cat_test, y_cat_pred, zero_division=0))

# Métriques Priorité
print("\n" + "="*80)
print("📊 RÉSULTATS - PRIORITÉ")
print("="*80)
acc_pri = accuracy_score(y_pri_test, y_pri_pred)
print(f"\n✅ Accuracy: {acc_pri:.4f} ({acc_pri*100:.2f}%)\n")
print("Classification Report:")
print(classification_report(y_pri_test, y_pri_pred, zero_division=0))

# ============================================================================
# SAUVEGARDE DES MODÈLES
# ============================================================================
print("\n" + "="*80)
print("💾 SAUVEGARDE DES MODÈLES")
print("="*80 + "\n")

# Sauvegarder les modèles
models = {
    'vectorizer': vectorizer,
    'sentiment': model_sentiment,
    'categorie': model_categorie,
    'priority': model_priority
}

for name, model in models.items():
    filepath = os.path.join(CONFIG['output_dir'], f'{name}_model.pkl')
    with open(filepath, 'wb') as f:
        pickle.dump(model, f)
    print(f"   ✅ {name.capitalize()} sauvegardé: {filepath}")

# Sauvegarder les métriques
metrics = {
    'date': datetime.now().isoformat(),
    'dataset_size': len(df),
    'train_size': len(X_train),
    'test_size': len(X_test),
    'config': CONFIG,
    'results': {
        'sentiment': {
            'accuracy': float(acc_sent),
            'classes': list(y_sentiment.unique())
        },
        'categorie': {
            'accuracy': float(acc_cat),
            'classes': list(y_categorie.unique())
        },
        'priority': {
            'accuracy': float(acc_pri),
            'classes': list(y_priority.unique())
        }
    }
}

metrics_file = os.path.join(CONFIG['output_dir'], 'training_metrics.json')
with open(metrics_file, 'w', encoding='utf-8') as f:
    json.dump(metrics, f, indent=2, ensure_ascii=False)

print(f"   ✅ Métriques sauvegardées: {metrics_file}")

# ============================================================================
# RÉSUMÉ FINAL
# ============================================================================
print("\n" + "╔" + "="*78 + "╗")
print("║" + " "*25 + "✅ ENTRAÎNEMENT RÉUSSI!" + " "*26 + "║")
print("╚" + "="*78 + "╝\n")

print("📊 RÉSUMÉ DES PERFORMANCES:\n")
print(f"   • Sentiment:  {acc_sent*100:.2f}% accuracy")
print(f"   • Catégorie:  {acc_cat*100:.2f}% accuracy")
print(f"   • Priorité:   {acc_pri*100:.2f}% accuracy")
print(f"\n   Moyenne:     {(acc_sent + acc_cat + acc_pri)/3*100:.2f}% accuracy")

print(f"\n📁 MODÈLES SAUVEGARDÉS:")
print(f"   • Dossier: {CONFIG['output_dir']}/")
print(f"   • Fichiers: 4 modèles + métriques")

print(f"\n🎯 MODÈLE BASELINE CRÉÉ:")
print(f"   ✅ Prêt pour comparaisons futures")
print(f"   ✅ Peut être utilisé pour inférence")
print(f"   ✅ Benchmark établi pour fine-tuning")

print("\n" + "="*80)
print("  🎉 ÉTAPE 1 COMPLÉTÉE AVEC SUCCÈS!")
print("="*80 + "\n")

print("📖 PROCHAINE ÉTAPE:")
print("   → Étape 2: Générer les datasets de validation et test\n")

