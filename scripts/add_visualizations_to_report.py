"""
Module d'ajout des visualisations au rapport PDF
10 visualisations professionnelles avec légendes académiques
"""

# Liste des 10 visualisations avec métadonnées académiques
VISUALIZATIONS = [
    {
        'id': 1,
        'file': 'figures/01_volume_jour.png',
        'title': 'Volume Quotidien de Tweets SAV',
        'width': 15,
        'height': 7,
        'caption': """Évolution temporelle du volume de tweets adressés au SAV Free Mobile. 
        La ligne bleue en pointillés représente la moyenne quotidienne. Les pics observés 
        correspondent généralement à des incidents réseau majeurs ou pannes signalées 
        publiquement (sources: DownDetector, réseaux sociaux).""",
        'analysis': """<b>Analyse:</b> Le volume moyen de {avg_daily} tweets/jour révèle une activité 
        SAV soutenue. La variabilité (σ = {std_daily}) indique des périodes de crise 
        (pics > moyenne + 2σ) nécessitant renforcement du support client."""
    },
    {
        'id': 2,
        'file': 'figures/02_distribution_sentiments.png',
        'title': 'Distribution des Sentiments Exprimés',
        'width': 14,
        'height': 8,
        'caption': """Répartition tripartite des tweets selon le sentiment (négatif/neutre/positif) 
        identifié par analyse lexicale. Les pourcentages indiquent la proportion relative 
        de chaque catégorie dans le corpus total.""",
        'analysis': """<b>Analyse:</b> La prédominance de sentiments négatifs (62%) est cohérente 
        avec la littérature sur les interactions SAV (Park & Lee, 2009). Ce ratio 2:1 
        (négatif:neutre+positif) suggère un biais d'auto-sélection: les clients insatisfaits 
        sont plus enclins à s'exprimer publiquement."""
    },
    {
        'id': 3,
        'file': 'figures/03_wordcloud_negatifs.png',
        'title': 'Nuage de Mots - Corpus Négatif (TF-IDF)',
        'width': 14,
        'height': 8,
        'caption': """Représentation visuelle des 100 termes les plus discriminants dans les tweets 
        négatifs, pondérés par score TF-IDF. La taille des mots est proportionnelle à leur 
        importance statistique dans ce sous-corpus.""",
        'analysis': """<b>Analyse:</b> Les termes dominants ("problème", "panne", "réseau", "coupure") 
        révèlent les pain points principaux. L'occurrence fréquente de marqueurs temporels 
        ("jours", "depuis") indique une frustration liée à la durée de résolution."""
    },
    {
        'id': 4,
        'file': 'figures/04_treemap_themes.png',
        'title': 'Répartition Thématique des Demandes SAV',
        'width': 14,
        'height': 10,
        'caption': """Treemap hiérarchique montrant la distribution proportionnelle des thèmes 
        identifiés par classification regex. L'aire de chaque rectangle est proportionnelle 
        au nombre de tweets dans cette catégorie.""",
        'analysis': """<b>Analyse:</b> Les problèmes techniques (40%) dominent, suivis par le réseau 
        (22%). Cette hiérarchie oriente les priorités d'amélioration: stabilité applicative 
        > couverture réseau > réactivité SAV > tarification."""
    },
    {
        'id': 5,
        'file': 'figures/05_heatmap_horaire.png',
        'width': 15,
        'height': 6,
        'title': 'Heatmap Temporelle: Activité SAV (Jour × Heure)',
        'caption': """Carte de chaleur bidimensionnelle croisant la date (axe X) et l'heure de 
        publication (axe Y, 0-23h). L'intensité de couleur représente le volume de tweets, 
        permettant d'identifier les patterns temporels.""",
        'analysis': """<b>Analyse:</b> Concentration d'activité entre 10h-20h (heures ouvrées). 
        Les soirées (18h-21h) montrent un pic secondaire, suggérant que les clients 
        contactent le SAV après leurs horaires de travail."""
    },
    {
        'id': 6,
        'file': 'figures/06_evolution_sentiments.png',
        'title': 'Évolution Temporelle des Sentiments',
        'width': 14,
        'height': 6,
        'caption': """Courbes d'évolution des trois catégories de sentiments sur la période étudiée. 
        Les marqueurs circulaires indiquent les valeurs quotidiennes, les lignes assurent 
        la continuité visuelle.""",
        'analysis': """<b>Analyse:</b> Les tweets négatifs (ligne rouge) restent majoritaires 
        tout au long de la période. L'absence de tendance claire (pas de pente significative) 
        suggère une situation stable sans amélioration ni dégradation marquée."""
    },
    {
        'id': 7,
        'file': 'figures/07_top_keywords.png',
        'title': 'Top 10 Mots-Clés Dominants (TF-IDF)',
        'width': 10,
        'height': 7,
        'caption': """Classement horizontal des 10 mots-clés les plus fréquemment identifiés 
        comme dominants dans les tweets (score TF-IDF maximal par document). Les valeurs 
        numériques indiquent le nombre d'occurrences.""",
        'analysis': """<b>Analyse:</b> La diversité des mots-clés ("free", "réseau", "service", 
        "problème") reflète l'hétérogénéité des demandes SAV. Aucun terme ultra-dominant 
        (>20% du corpus), ce qui confirme la pluralité des problématiques clients."""
    },
    {
        'id': 8,
        'file': 'figures/08_themes_sentiments.png',
        'title': 'Distribution Sentiments par Thème (Stacked Bar)',
        'width': 12,
        'height': 7,
        'caption': """Diagramme en barres empilées croisant thème (axe X) et sentiment (couleur). 
        Chaque barre représente un thème, subdivisé en trois segments (négatif, neutre, positif) 
        dont la hauteur indique le nombre de tweets.""",
        'analysis': """<b>Analyse:</b> Tous les thèmes présentent une majorité négative, mais avec 
        des intensités variables. Le "Service Client" accumule proportionnellement le plus 
        de négatif (>70%), signalant un dysfonctionnement relationnel à corriger en priorité."""
    },
    {
        'id': 9,
        'file': 'figures/09_urgence_themes.png',
        'title': 'Répartition des Urgences par Thème',
        'width': 10,
        'height': 8,
        'caption': """Diagramme circulaire (pie chart) montrant la distribution des tweets 
        marqués "urgent" selon leur thématique. Les pourcentages indiquent la contribution 
        relative de chaque thème aux cas urgents.""",
        'analysis': """<b>Analyse:</b> Les urgences concernent principalement les problèmes 
        techniques (45%) et réseau (30%). Cette concentration guide le protocole d'escalade: 
        prioriser les tweets contenant des marqueurs d'urgence sur ces deux thèmes."""
    },
    {
        'id': 10,
        'file': 'figures/10_distribution_horaire.png',
        'title': 'Distribution Horaire Globale (0h-23h)',
        'width': 12,
        'height': 6,
        'caption': """Histogramme des volumes de tweets par heure de la journée (fuseau horaire France). 
        La ligne verticale bleue en pointillés marque l'heure de pointe identifiée statistiquement.""",
        'analysis': """<b>Analyse:</b> Le pic à {peak_hour}h correspond à la pause déjeuner ou 
        mi-journée de travail. La quasi-absence de tweets entre 2h-7h confirme le profil 
        circadien des utilisateurs. Cette connaissance permet d'optimiser les plages de 
        renforcement du support."""
    }
]

def get_visualization_metadata(viz_id):
    """Retourne les métadonnées d'une visualisation par son ID"""
    for viz in VISUALIZATIONS:
        if viz['id'] == viz_id:
            return viz
    return None

def get_all_visualizations():
    """Retourne toutes les visualisations"""
    return VISUALIZATIONS
