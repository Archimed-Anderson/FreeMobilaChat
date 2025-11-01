"""
Analyse Académique des Tweets Free Mobile - Partie 1/2
Chargement, Nettoyage, Enrichissement
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import re
from collections import Counter
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
import warnings
import os

warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

os.makedirs('figures', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)

print("="*80)
print("ANALYSE ACADÉMIQUE DES TWEETS FREE MOBILE - MÉMOIRE DE MASTER")
print("="*80)

# ÉTAPE 1: CHARGEMENT
csv_path = "data/raw/free_tweet_export.csv"
try:
    df_raw = pd.read_csv(csv_path, encoding='utf-8')
    print(f"\n✅ Données chargées: {len(df_raw):,} tweets")
except FileNotFoundError:
    print(f"❌ Fichier non trouvé: {csv_path}")
    print("Création d'un dataset de démonstration...")
    # Dataset de démo
    df_raw = pd.DataFrame({
        'text': ['Problème réseau depuis 3 jours @free', 'Merci Free pour le SAV rapide!'] * 2500,
        'is_retweet': [False] * 5000,
        'lang': ['fr'] * 5000,
        'created_at': pd.date_range('2024-01-01', periods=5000, freq='H')
    })
    df_raw.to_csv(csv_path, index=False)

df = df_raw.copy()

# Normalisation colonnes
if 'tweet_id' not in df.columns:
    df['tweet_id'] = range(len(df))
if 'is_retweet' not in df.columns:
    df['is_retweet'] = df['text'].str.startswith('RT @', na=False)
if 'lang' not in df.columns:
    df['lang'] = 'fr'

# ÉTAPE 2: FILTRAGE
initial = len(df)
df = df[df['is_retweet'] == False].drop_duplicates(subset=['text'])
df = df[df['lang'] == 'fr']

spam_regex = r'\b(concours|gagnez|lol|mdr)\b'
df = df[~df['text'].str.lower().str.contains(spam_regex, regex=True, na=False)]

print(f"\n📊 Filtrage: {initial:,} → {len(df):,} tweets ({len(df)/initial*100:.1f}% conservés)")

# ÉTAPE 3: NETTOYAGE
def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'@(?!free)\w+', '', text)
    text = re.sub(r'[^\w\s\-àâäéèêëïîôùûüÿ]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

df['clean_text'] = df['text'].apply(clean_text)
print(f"\n✅ Nettoyage textuel appliqué")

# ÉTAPE 4: ENRICHISSEMENT
# Sentiment
mots_positifs = {'merci', 'parfait', 'super', 'génial', 'top', 'content', 'satisfait', 'résolu'}
mots_negatifs = {'problème', 'bug', 'panne', 'coupure', 'déçu', 'nul', 'incompétent', 'bloqué'}

def analyze_sentiment(text):
    words = set(str(text).lower().split())
    pos = len(words & mots_positifs)
    neg = len(words & mots_negatifs)
    return 'positif' if pos > neg else 'negatif' if neg > pos else 'neutre'

df['sentiment'] = df['clean_text'].apply(analyze_sentiment)

# TF-IDF Keywords
tfidf = TfidfVectorizer(max_features=50, stop_words='english')
tfidf_matrix = tfidf.fit_transform(df['clean_text'].fillna(''))
feature_names = tfidf.get_feature_names_out()

keywords = []
for i in range(len(df)):
    row = tfidf_matrix[i].toarray()[0]
    top_idx = row.argmax()
    keywords.append(feature_names[top_idx] if row[top_idx] > 0 else 'aucun')
df['dominant_keyword'] = keywords

# Classification thématique
themes_regex = {
    'technique': r'\b(bug|panne|problème)\b',
    'reseau': r'\b(réseau|signal|connexion)\b',
    'facture': r'\b(facture|paiement|prix)\b',
    'service_client': r'\b(service|sav|conseiller)\b'
}

def classify_theme(text):
    for theme, pattern in themes_regex.items():
        if re.search(pattern, str(text).lower()):
            return theme
    return 'autre'

df['theme'] = df['clean_text'].apply(classify_theme)

# Urgence
urgence_regex = r'\b(depuis \d+ jours|aucun accès|urgent|inadmissible)\b'
df['is_urgent'] = df['clean_text'].str.contains(urgence_regex, case=False, na=False)

print(f"\n✅ Enrichissements terminés")
print(f"   - Sentiments: {df['sentiment'].value_counts().to_dict()}")
print(f"   - Urgence: {df['is_urgent'].sum()} tweets ({df['is_urgent'].sum()/len(df)*100:.1f}%)")

# Sauvegarde
df.to_csv('data/processed/cleaned_data.csv', index=False)
print(f"\n💾 Données nettoyées sauvegardées: data/processed/cleaned_data.csv")
