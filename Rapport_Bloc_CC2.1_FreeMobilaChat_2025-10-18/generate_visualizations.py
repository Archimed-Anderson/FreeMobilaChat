"""
Script de génération des visualisations pour le Rapport Bloc CC2.1
Génère tous les graphiques mentionnés dans le rapport
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
from pathlib import Path
import numpy as np
from collections import Counter
from wordcloud import WordCloud

# Configuration de style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Créer le répertoire de sortie
output_dir = Path("visualizations")
output_dir.mkdir(exist_ok=True)

print("📊 Génération des visualisations pour le Rapport Bloc CC2.1")
print("=" * 60)

# Charger les données
print("\n1️⃣ Chargement des données...")
train_df = pd.read_csv("data/training/train_dataset.csv")
val_df = pd.read_csv("data/training/validation_dataset.csv")
test_df = pd.read_csv("data/training/test_dataset.csv")

with open("data/training/dataset_statistics.json", 'r', encoding='utf-8') as f:
    stats = json.load(f)

print(f"   ✅ Training: {len(train_df)} échantillons")
print(f"   ✅ Validation: {len(val_df)} échantillons")
print(f"   ✅ Test: {len(test_df)} échantillons")

# 1. Distribution des Sentiments
print("\n2️⃣ Génération: Distribution des Sentiments...")
fig, ax = plt.subplots(figsize=(12, 6))

splits = ['Training', 'Validation', 'Test']
sentiments = ['neutral', 'negative', 'positive']
colors = ['#3498db', '#e74c3c', '#2ecc71']

data = {
    'Training': [stats['train']['sentiment_percentages'][s] for s in sentiments],
    'Validation': [stats['validation']['sentiment_percentages'][s] for s in sentiments],
    'Test': [stats['test']['sentiment_percentages'][s] for s in sentiments]
}

x = np.arange(len(splits))
width = 0.25

for i, sentiment in enumerate(sentiments):
    values = [data[split][i] for split in splits]
    ax.bar(x + i * width, values, width, label=sentiment.capitalize(), color=colors[i])

ax.set_xlabel('Dataset Split', fontsize=12, fontweight='bold')
ax.set_ylabel('Pourcentage (%)', fontsize=12, fontweight='bold')
ax.set_title('Distribution des Sentiments par Split', fontsize=14, fontweight='bold')
ax.set_xticks(x + width)
ax.set_xticklabels(splits)
ax.legend()
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(output_dir / "1_distribution_sentiments.png", dpi=300, bbox_inches='tight')
plt.close()
print("   ✅ Sauvegardé: 1_distribution_sentiments.png")

# 2. Distribution des Catégories
print("\n3️⃣ Génération: Distribution des Catégories...")
fig, ax = plt.subplots(figsize=(12, 8))

categories = list(stats['train']['category_distribution'].keys())
counts = list(stats['train']['category_distribution'].values())

# Trier par ordre décroissant
sorted_data = sorted(zip(categories, counts), key=lambda x: x[1], reverse=True)
categories, counts = zip(*sorted_data)

colors_cat = sns.color_palette("husl", len(categories))
bars = ax.barh(categories, counts, color=colors_cat)

# Ajouter les pourcentages
for i, (cat, count) in enumerate(zip(categories, counts)):
    percentage = (count / sum(counts)) * 100
    ax.text(count + 20, i, f'{count} ({percentage:.1f}%)', 
            va='center', fontsize=10, fontweight='bold')

ax.set_xlabel('Nombre de Tweets', fontsize=12, fontweight='bold')
ax.set_ylabel('Catégorie', fontsize=12, fontweight='bold')
ax.set_title('Distribution des Catégories (Training Set)', fontsize=14, fontweight='bold')
ax.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig(output_dir / "2_distribution_categories.png", dpi=300, bbox_inches='tight')
plt.close()
print("   ✅ Sauvegardé: 2_distribution_categories.png")

# 3. Distribution des Priorités
print("\n4️⃣ Génération: Distribution des Priorités...")
fig, ax = plt.subplots(figsize=(10, 10))

priorities = list(stats['train']['priority_distribution'].keys())
counts_prio = list(stats['train']['priority_distribution'].values())

colors_prio = ['#2ecc71', '#f39c12', '#e67e22', '#e74c3c']
explode = (0.05, 0.05, 0.05, 0.1)  # Explode la priorité critique

wedges, texts, autotexts = ax.pie(counts_prio, labels=priorities, autopct='%1.1f%%',
                                    colors=colors_prio, explode=explode,
                                    startangle=90, textprops={'fontsize': 12, 'fontweight': 'bold'})

ax.set_title('Distribution des Priorités (Training Set)', fontsize=14, fontweight='bold', pad=20)

# Légende avec les counts
legend_labels = [f'{p.capitalize()}: {c} tweets' for p, c in zip(priorities, counts_prio)]
ax.legend(legend_labels, loc='upper left', bbox_to_anchor=(1, 1))

plt.tight_layout()
plt.savefig(output_dir / "3_distribution_priorites.png", dpi=300, bbox_inches='tight')
plt.close()
print("   ✅ Sauvegardé: 3_distribution_priorites.png")

# 4. Matrice de Corrélation Sentiment-Catégorie
print("\n5️⃣ Génération: Matrice de Corrélation Sentiment-Catégorie...")
fig, ax = plt.subplots(figsize=(12, 8))

# Créer une matrice de contingence
contingency = pd.crosstab(train_df['category'], train_df['sentiment'], normalize='index') * 100

sns.heatmap(contingency, annot=True, fmt='.1f', cmap='YlOrRd', 
            cbar_kws={'label': 'Pourcentage (%)'}, ax=ax)

ax.set_xlabel('Sentiment', fontsize=12, fontweight='bold')
ax.set_ylabel('Catégorie', fontsize=12, fontweight='bold')
ax.set_title('Matrice de Corrélation Sentiment-Catégorie (%)', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig(output_dir / "4_correlation_sentiment_categorie.png", dpi=300, bbox_inches='tight')
plt.close()
print("   ✅ Sauvegardé: 4_correlation_sentiment_categorie.png")

# 5. Distribution de la Longueur des Textes
print("\n6️⃣ Génération: Distribution de la Longueur des Textes...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Histogramme
train_lengths = train_df['text'].str.len()
val_lengths = val_df['text'].str.len()
test_lengths = test_df['text'].str.len()

ax1.hist([train_lengths, val_lengths, test_lengths], bins=50, 
         label=['Training', 'Validation', 'Test'], alpha=0.7, color=['#3498db', '#e74c3c', '#2ecc71'])
ax1.set_xlabel('Longueur du Texte (caractères)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Fréquence', fontsize=12, fontweight='bold')
ax1.set_title('Distribution de la Longueur des Textes', fontsize=14, fontweight='bold')
ax1.legend()
ax1.grid(alpha=0.3)

# Boxplot
data_box = [train_lengths, val_lengths, test_lengths]
bp = ax2.boxplot(data_box, labels=['Training', 'Validation', 'Test'], patch_artist=True)

colors_box = ['#3498db', '#e74c3c', '#2ecc71']
for patch, color in zip(bp['boxes'], colors_box):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

ax2.set_ylabel('Longueur du Texte (caractères)', fontsize=12, fontweight='bold')
ax2.set_title('Boxplot de la Longueur des Textes', fontsize=14, fontweight='bold')
ax2.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(output_dir / "5_distribution_longueur_textes.png", dpi=300, bbox_inches='tight')
plt.close()
print("   ✅ Sauvegardé: 5_distribution_longueur_textes.png")

# 6. Évolution Temporelle
print("\n7️⃣ Génération: Évolution Temporelle...")
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10))

# Convertir les dates
train_df['date'] = pd.to_datetime(train_df['date'])
train_df['date_only'] = train_df['date'].dt.date

# Volume par jour
daily_counts = train_df.groupby('date_only').size()
ax1.plot(daily_counts.index, daily_counts.values, linewidth=2, color='#3498db')
ax1.fill_between(daily_counts.index, daily_counts.values, alpha=0.3, color='#3498db')
ax1.set_xlabel('Date', fontsize=12, fontweight='bold')
ax1.set_ylabel('Nombre de Tweets', fontsize=12, fontweight='bold')
ax1.set_title('Volume de Tweets par Jour (Training Set)', fontsize=14, fontweight='bold')
ax1.grid(alpha=0.3)
ax1.tick_params(axis='x', rotation=45)

# Sentiment par semaine
train_df['week'] = train_df['date'].dt.to_period('W')
sentiment_weekly = train_df.groupby(['week', 'sentiment']).size().unstack(fill_value=0)

sentiment_weekly.plot(kind='area', stacked=True, ax=ax2, 
                      color=['#2ecc71', '#e74c3c', '#3498db'], alpha=0.7)
ax2.set_xlabel('Semaine', fontsize=12, fontweight='bold')
ax2.set_ylabel('Nombre de Tweets', fontsize=12, fontweight='bold')
ax2.set_title('Distribution des Sentiments par Semaine', fontsize=14, fontweight='bold')
ax2.legend(title='Sentiment', labels=['Positive', 'Negative', 'Neutral'])
ax2.grid(alpha=0.3)
ax2.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig(output_dir / "6_evolution_temporelle.png", dpi=300, bbox_inches='tight')
plt.close()
print("   ✅ Sauvegardé: 6_evolution_temporelle.png")

# 7. Nuages de Mots par Sentiment
print("\n8️⃣ Génération: Nuages de Mots par Sentiment...")
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

sentiments_wc = ['positive', 'negative', 'neutral']
colors_wc = ['Greens', 'Reds', 'Blues']  # Corrected colormap names

for ax, sentiment, color in zip(axes, sentiments_wc, colors_wc):
    # Filtrer les textes par sentiment
    texts = train_df[train_df['sentiment'] == sentiment]['text']
    all_text = ' '.join(texts.astype(str))

    # Créer le nuage de mots
    wordcloud = WordCloud(width=800, height=400, background_color='white',
                          colormap=color, max_words=100,
                          stopwords={'le', 'la', 'les', 'de', 'et', 'à', 'un', 'une', 'pour', 'dans', 'sur'}).generate(all_text)

    ax.imshow(wordcloud, interpolation='bilinear')
    ax.set_title(f'Sentiment: {sentiment.capitalize()}', fontsize=14, fontweight='bold')
    ax.axis('off')

plt.tight_layout()
plt.savefig(output_dir / "7_nuages_mots_sentiments.png", dpi=300, bbox_inches='tight')
plt.close()
print("   ✅ Sauvegardé: 7_nuages_mots_sentiments.png")

# 8. KPI Opérationnels
print("\n9️⃣ Génération: KPI Opérationnels...")
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

# KPI 1: Tweets nécessitant une réponse
needs_response_data = {
    'Training': [int(stats['train']['needs_response_tweets']),
                 stats['train']['total_samples'] - int(stats['train']['needs_response_tweets'])],
    'Validation': [int(stats['validation']['needs_response_tweets']),
                   stats['validation']['total_samples'] - int(stats['validation']['needs_response_tweets'])],
    'Test': [int(stats['test']['needs_response_tweets']),
             stats['test']['total_samples'] - int(stats['test']['needs_response_tweets'])]
}

x_pos = np.arange(len(needs_response_data))
needs_yes = [needs_response_data[k][0] for k in needs_response_data.keys()]
needs_no = [needs_response_data[k][1] for k in needs_response_data.keys()]

ax1.bar(x_pos, needs_yes, label='Nécessite réponse', color='#e74c3c', alpha=0.8)
ax1.bar(x_pos, needs_no, bottom=needs_yes, label='Ne nécessite pas', color='#2ecc71', alpha=0.8)
ax1.set_xticks(x_pos)
ax1.set_xticklabels(needs_response_data.keys())
ax1.set_ylabel('Nombre de Tweets', fontsize=12, fontweight='bold')
ax1.set_title('Tweets Nécessitant une Réponse', fontsize=14, fontweight='bold')
ax1.legend()
ax1.grid(axis='y', alpha=0.3)

# KPI 2: Tweets urgents
urgent_data = {
    'Training': [int(stats['train']['urgent_tweets']),
                 stats['train']['total_samples'] - int(stats['train']['urgent_tweets'])],
    'Validation': [int(stats['validation']['urgent_tweets']),
                   stats['validation']['total_samples'] - int(stats['validation']['urgent_tweets'])],
    'Test': [int(stats['test']['urgent_tweets']),
             stats['test']['total_samples'] - int(stats['test']['urgent_tweets'])]
}

urgent_yes = [urgent_data[k][0] for k in urgent_data.keys()]
urgent_no = [urgent_data[k][1] for k in urgent_data.keys()]

ax2.bar(x_pos, urgent_yes, label='Urgent', color='#e67e22', alpha=0.8)
ax2.bar(x_pos, urgent_no, bottom=urgent_yes, label='Non urgent', color='#3498db', alpha=0.8)
ax2.set_xticks(x_pos)
ax2.set_xticklabels(urgent_data.keys())
ax2.set_ylabel('Nombre de Tweets', fontsize=12, fontweight='bold')
ax2.set_title('Tweets Urgents', fontsize=14, fontweight='bold')
ax2.legend()
ax2.grid(axis='y', alpha=0.3)

# KPI 3: Temps de résolution moyen par catégorie
categories_time = train_df.groupby('category')['estimated_resolution_time'].mean().sort_values(ascending=True)
colors_time = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(categories_time)))

ax3.barh(categories_time.index, categories_time.values, color=colors_time)
ax3.set_xlabel('Temps Moyen (minutes)', fontsize=12, fontweight='bold')
ax3.set_ylabel('Catégorie', fontsize=12, fontweight='bold')
ax3.set_title('Temps de Résolution Moyen par Catégorie', fontsize=14, fontweight='bold')
ax3.grid(axis='x', alpha=0.3)

# KPI 4: Diversité des auteurs
authors_data = {
    'Training': [stats['train']['unique_authors'], stats['train']['total_samples']],
    'Validation': [stats['validation']['unique_authors'], stats['validation']['total_samples']],
    'Test': [stats['test']['unique_authors'], stats['test']['total_samples']]
}

splits_names = list(authors_data.keys())
unique_authors = [authors_data[k][0] for k in splits_names]
total_tweets = [authors_data[k][1] for k in splits_names]
ratios = [u/t for u, t in zip(unique_authors, total_tweets)]

x_pos_auth = np.arange(len(splits_names))
width = 0.35

ax4_twin = ax4.twinx()
bars1 = ax4.bar(x_pos_auth - width/2, unique_authors, width, label='Auteurs Uniques', color='#3498db', alpha=0.8)
bars2 = ax4.bar(x_pos_auth + width/2, total_tweets, width, label='Total Tweets', color='#e74c3c', alpha=0.8)
line = ax4_twin.plot(x_pos_auth, ratios, 'go-', linewidth=2, markersize=10, label='Ratio Auteurs/Tweets')

ax4.set_xticks(x_pos_auth)
ax4.set_xticklabels(splits_names)
ax4.set_ylabel('Nombre', fontsize=12, fontweight='bold')
ax4_twin.set_ylabel('Ratio', fontsize=12, fontweight='bold', color='green')
ax4.set_title('Diversité des Auteurs', fontsize=14, fontweight='bold')
ax4.legend(loc='upper left')
ax4_twin.legend(loc='upper right')
ax4.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(output_dir / "8_kpi_operationnels.png", dpi=300, bbox_inches='tight')
plt.close()
print("   ✅ Sauvegardé: 8_kpi_operationnels.png")

# Résumé final
print("\n" + "=" * 60)
print("✅ Génération terminée avec succès!")
print(f"📁 Toutes les visualisations sont sauvegardées dans: {output_dir.absolute()}")
print("\nFichiers générés:")
print("  1. 1_distribution_sentiments.png")
print("  2. 2_distribution_categories.png")
print("  3. 3_distribution_priorites.png")
print("  4. 4_correlation_sentiment_categorie.png")
print("  5. 5_distribution_longueur_textes.png")
print("  6. 6_evolution_temporelle.png")
print("  7. 7_nuages_mots_sentiments.png")
print("  8. 8_kpi_operationnels.png")
print("=" * 60)

