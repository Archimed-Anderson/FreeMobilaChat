"""
Analyse Académique des Tweets Free Mobile - Partie 2/2
KPIs et Visualisations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import squarify
import warnings

warnings.filterwarnings('ignore')
plt.rcParams['font.size'] = 11
sns.set_palette("Set2")

# Charger données nettoyées
df = pd.read_csv('data/processed/cleaned_data.csv')
df['created_at'] = pd.to_datetime(df.get('created_at', pd.date_range('2024-01-01', periods=len(df), freq='H')))
df['date'] = df['created_at'].dt.date
df['hour'] = df['created_at'].dt.hour

print("="*80)
print("GÉNÉRATION DES KPIs ET VISUALISATIONS")
print("="*80)

# KPIS
kpis = {
    'total_tweets': len(df),
    'pct_negatif': (df['sentiment'] == 'negatif').sum() / len(df) * 100,
    'pct_neutre': (df['sentiment'] == 'neutre').sum() / len(df) * 100,
    'pct_positif': (df['sentiment'] == 'positif').sum() / len(df) * 100,
    'pct_urgent': df['is_urgent'].sum() / len(df) * 100,
    'top_5_themes': df['theme'].value_counts().head(5).to_dict()
}

print(f"\n📊 KPIS PRINCIPAUX:")
print(f"   - Total tweets: {kpis['total_tweets']:,}")
print(f"   - Négatif: {kpis['pct_negatif']:.1f}%")
print(f"   - Neutre: {kpis['pct_neutre']:.1f}%")
print(f"   - Positif: {kpis['pct_positif']:.1f}%")
print(f"   - Urgent: {kpis['pct_urgent']:.1f}%")

# VISUALISATIONS (8-10 figures professionnelles)
print(f"\n🎨 Génération de 10 visualisations académiques...")

# Figure 1: Volume par jour
fig, ax = plt.subplots(figsize=(12, 5))
volume_daily = df.groupby('date').size()
volume_daily.plot(kind='bar', color='#CC0000', alpha=0.7, ax=ax)
ax.set_title('Volume de Tweets Free Mobile par Jour', fontsize=14, fontweight='bold')
ax.set_xlabel('Date', fontsize=11)
ax.set_ylabel('Nombre de Tweets', fontsize=11)
ax.axhline(y=volume_daily.mean(), color='blue', linestyle='--', label=f'Moyenne: {volume_daily.mean():.0f}')
ax.legend()
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('figures/01_volume_jour.png', dpi=300, bbox_inches='tight')
print("   ✓ Fig 1: Volume quotidien avec ligne de moyenne")
plt.close()

# Figure 2: Distribution sentiments (bar chart amélioré)
fig, ax = plt.subplots(figsize=(10, 6))
sentiment_counts = df['sentiment'].value_counts()
colors_sent = {'negatif': '#d32f2f', 'neutre': '#757575', 'positif': '#388e3c'}
bars = ax.bar(sentiment_counts.index, sentiment_counts.values, 
              color=[colors_sent.get(s, '#ccc') for s in sentiment_counts.index])
ax.set_title('Distribution des Sentiments', fontsize=14, fontweight='bold')
ax.set_ylabel('Nombre de Tweets', fontsize=11)
ax.set_xlabel('Sentiment', fontsize=11)
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height):,}\n({height/len(df)*100:.1f}%)',
            ha='center', va='bottom', fontweight='bold')
plt.tight_layout()
plt.savefig('figures/02_distribution_sentiments.png', dpi=300, bbox_inches='tight')
print("   ✓ Fig 2: Distribution des sentiments")
plt.close()

# Figure 3: Nuage de mots négatifs
df_neg = df[df['sentiment'] == 'negatif']
if len(df_neg) > 0:
    text_neg = ' '.join(df_neg['clean_text'].fillna(''))
    wordcloud = WordCloud(width=1200, height=700, background_color='white',
                         colormap='Reds', max_words=100, relative_scaling=0.5).generate(text_neg)
    plt.figure(figsize=(14, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Nuage de Mots - Tweets Négatifs (TF-IDF)', fontsize=16, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig('figures/03_wordcloud_negatifs.png', dpi=300, bbox_inches='tight')
    print("   ✓ Fig 3: Nuage de mots (tweets négatifs)")
    plt.close()

# Figure 4: Treemap thématique
theme_counts = df['theme'].value_counts()
fig, ax = plt.subplots(figsize=(12, 8))
squarify.plot(sizes=theme_counts.values,
              label=[f"{t.upper()}\n{c:,} tweets\n({c/len(df)*100:.1f}%)" 
                     for t, c in zip(theme_counts.index, theme_counts.values)],
              alpha=0.8, color=sns.color_palette("Set3", len(theme_counts)), 
              text_kwargs={'fontsize': 10, 'weight': 'bold'}, ax=ax)
ax.set_title('Répartition Thématique des Demandes SAV', fontsize=14, fontweight='bold')
ax.axis('off')
plt.tight_layout()
plt.savefig('figures/04_treemap_themes.png', dpi=300, bbox_inches='tight')
print("   ✓ Fig 4: Treemap thématique")
plt.close()

# Figure 5: Heatmap horaire (jour × heure)
heatmap_data = df.groupby(['date', 'hour']).size().unstack(fill_value=0)
plt.figure(figsize=(15, 6))
sns.heatmap(heatmap_data.T, cmap='YlOrRd', cbar_kws={'label': 'Tweets'}, 
            linewidths=0.5, linecolor='white')
plt.title('Heatmap Horaire: Volume de Tweets par Jour et Heure', fontsize=14, fontweight='bold')
plt.xlabel('Date', fontsize=11)
plt.ylabel('Heure (0-23h)', fontsize=11)
plt.tight_layout()
plt.savefig('figures/05_heatmap_horaire.png', dpi=300, bbox_inches='tight')
print("   ✓ Fig 5: Heatmap horaire")
plt.close()

# Figure 6: Évolution temporelle des sentiments (line chart)
fig, ax = plt.subplots(figsize=(14, 6))
sentiment_evolution = df.groupby(['date', 'sentiment']).size().unstack(fill_value=0)
sentiment_evolution.plot(kind='line', marker='o', linewidth=2.5, ax=ax,
                        color=['#d32f2f', '#757575', '#388e3c'])
ax.set_title('Évolution Temporelle des Sentiments', fontsize=14, fontweight='bold')
ax.set_xlabel('Date', fontsize=11)
ax.set_ylabel('Nombre de Tweets', fontsize=11)
ax.legend(title='Sentiment', labels=['Négatif', 'Neutre', 'Positif'], loc='best')
ax.grid(alpha=0.3, linestyle='--')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('figures/06_evolution_sentiments.png', dpi=300, bbox_inches='tight')
print("   ✓ Fig 6: Évolution temporelle des sentiments")
plt.close()

# Figure 7: Top 10 mots-clés (bar chart horizontal)
top_keywords = df['dominant_keyword'].value_counts().head(10)
fig, ax = plt.subplots(figsize=(10, 7))
top_keywords.plot(kind='barh', color='#CC0000', alpha=0.8, ax=ax)
ax.set_title('Top 10 Mots-Clés Dominants (TF-IDF)', fontsize=14, fontweight='bold')
ax.set_xlabel('Fréquence', fontsize=11)
ax.set_ylabel('Mot-clé', fontsize=11)
for i, v in enumerate(top_keywords.values):
    ax.text(v + 5, i, str(v), va='center', fontweight='bold')
plt.tight_layout()
plt.savefig('figures/07_top_keywords.png', dpi=300, bbox_inches='tight')
print("   ✓ Fig 7: Top 10 mots-clés")
plt.close()

# Figure 8: Comparaison thèmes par sentiment (stacked bar)
theme_sentiment = df.groupby(['theme', 'sentiment']).size().unstack(fill_value=0)
fig, ax = plt.subplots(figsize=(12, 7))
theme_sentiment.plot(kind='bar', stacked=True, ax=ax,
                    color=['#d32f2f', '#757575', '#388e3c'], alpha=0.8)
ax.set_title('Distribution des Sentiments par Thème', fontsize=14, fontweight='bold')
ax.set_xlabel('Thème', fontsize=11)
ax.set_ylabel('Nombre de Tweets', fontsize=11)
ax.legend(title='Sentiment', labels=['Négatif', 'Neutre', 'Positif'])
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('figures/08_themes_sentiments.png', dpi=300, bbox_inches='tight')
print("   ✓ Fig 8: Thèmes par sentiment (stacked)")
plt.close()

# Figure 9: Urgence par thème (pie chart)
urgent_by_theme = df[df['is_urgent']].groupby('theme').size()
fig, ax = plt.subplots(figsize=(10, 8))
colors_pie = sns.color_palette("Reds", len(urgent_by_theme))
wedges, texts, autotexts = ax.pie(urgent_by_theme.values, labels=urgent_by_theme.index,
                                    autopct='%1.1f%%', startangle=90, colors=colors_pie,
                                    textprops={'fontsize': 11, 'weight': 'bold'})
ax.set_title('Répartition des Tweets Urgents par Thème', fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('figures/09_urgence_themes.png', dpi=300, bbox_inches='tight')
print("   ✓ Fig 9: Urgence par thème (pie chart)")
plt.close()

# Figure 10: Distribution horaire globale (histogram)
hourly_dist = df.groupby('hour').size()
fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(hourly_dist.index, hourly_dist.values, color='#CC0000', alpha=0.7, edgecolor='black')
ax.set_title('Distribution Horaire des Tweets SAV (0h-23h)', fontsize=14, fontweight='bold')
ax.set_xlabel('Heure de la journée', fontsize=11)
ax.set_ylabel('Nombre de Tweets', fontsize=11)
ax.set_xticks(range(0, 24, 2))
ax.grid(axis='y', alpha=0.3, linestyle='--')
# Highlight peak hours
peak_hour = hourly_dist.idxmax()
ax.axvline(x=peak_hour, color='blue', linestyle='--', linewidth=2, 
          label=f'Heure de pointe: {peak_hour}h')
ax.legend()
plt.tight_layout()
plt.savefig('figures/10_distribution_horaire.png', dpi=300, bbox_inches='tight')
print("   ✓ Fig 10: Distribution horaire globale")
plt.close()

# Export KPIs
import json
with open('data/processed/kpis.json', 'w', encoding='utf-8') as f:
    json.dump(kpis, f, indent=2, ensure_ascii=False)
print(f"\n💾 KPIs sauvegardés: data/processed/kpis.json")

print(f"\n✅ ANALYSE TERMINÉE - 10 visualisations générées dans figures/")
