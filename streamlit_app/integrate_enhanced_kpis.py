"""
Script d'intégration des KPIs avancés dans 1_Analyse_Intelligente.py
À exécuter pour ajouter automatiquement les nouveaux KPIs
"""

def generate_integration_code():
    """
    Génère le code d'intégration à ajouter dans 1_Analyse_Intelligente.py
    """
    
    integration_instructions = """
    
╔══════════════════════════════════════════════════════════════════════════╗
║    INSTRUCTIONS D'INTÉGRATION - KPIs AVANCÉS                            ║
╚══════════════════════════════════════════════════════════════════════════╝

ÉTAPE 1: Ajouter l'import en haut du fichier (après ligne 27)
──────────────────────────────────────────────────────────────────────────

Ajouter cette ligne après les autres imports de services:

try:
    from services.enhanced_kpis_vizualizations import (
        compute_business_kpis,
        render_business_kpis,
        render_enhanced_visualizations,
        render_complete_dashboard
    )
    ENHANCED_KPIS_AVAILABLE = True
except ImportError as e:
    print(f"Enhanced KPIs module not available: {e}")
    ENHANCED_KPIS_AVAILABLE = False


ÉTAPE 2: Intégrer dans la fonction _handle_multiple_file_analysis
──────────────────────────────────────────────────────────────────────────

Remplacer la section (lignes 493-496) qui dit:

            # Affichage des résultats pour ce fichier
            _render_file_analysis_result(result, df_clean, uploaded_file.name)
            
            # VISUALISATIONS DYNAMIQUES
            _render_enhanced_visualizations(df_clean, uploaded_file.name)

PAR:

            # Affichage des résultats pour ce fichier
            _render_file_analysis_result(result, df_clean, uploaded_file.name)
            
            # ═══════════════════════════════════════════════════════════
            # NOUVEAUX KPIs BUSINESS ET VISUALISATIONS AVANCÉES
            # ═══════════════════════════════════════════════════════════
            if ENHANCED_KPIS_AVAILABLE:
                st.markdown("---")
                st.markdown("""
                <div style="background: linear-gradient(135deg, #CC0000 0%, #8B0000 100%); 
                            padding: 2rem; border-radius: 12px; margin: 2rem 0; text-align: center;">
                    <h2 style="color: white; margin: 0; font-size: 2rem;">
                        <i class="fas fa-chart-line"></i>
                        TABLEAU DE BORD BUSINESS
                    </h2>
                    <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;">
                        Indicateurs clés de performance et analyses avancées
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Utiliser df_classified si disponible, sinon df_clean
                analysis_df = df_classified if 'df_classified' in locals() else df_clean
                
                # Rendre le dashboard complet
                render_complete_dashboard(analysis_df)
            
            # VISUALISATIONS DYNAMIQUES (anciennes - toujours disponibles)
            _render_enhanced_visualizations(df_clean, uploaded_file.name)


ÉTAPE 3: ALTERNATIVE - Intégration minimaliste
──────────────────────────────────────────────────────────────────────────

Si vous voulez juste afficher les nouveaux KPIs sans remplacer, 
ajoutez APRÈS la ligne 496:

            # VISUALISATIONS DYNAMIQUES
            _render_enhanced_visualizations(df_clean, uploaded_file.name)
            
            # NOUVEAUX KPIs BUSINESS (ajouté)
            if ENHANCED_KPIS_AVAILABLE:
                st.markdown("---")
                st.markdown("## 📊 Dashboard Business")
                analysis_df = df_classified if 'df_classified' in locals() else df_clean
                render_complete_dashboard(analysis_df)


ÉTAPE 4: Vérification
──────────────────────────────────────────────────────────────────────────

1. Relancer l'application: streamlit run streamlit_app/pages/1_Analyse_Intelligente.py
2. Uploader un fichier CSV avec des tweets
3. Vérifier que les nouveaux KPIs s'affichent:
   - ✅ Taux de Réclamations
   - ✅ Indice Satisfaction
   - ✅ Taux d'Urgence
   - ✅ Confiance Moyenne
   - ✅ Thèmes Identifiés
   
4. Vérifier les nouvelles visualisations:
   - ✅ Distribution des sentiments (pie chart)
   - ✅ Évolution temporelle (line chart)
   - ✅ Heatmap d'activité
   - ✅ Top 10 catégories
   - ✅ Distribution urgence
   - ✅ Radar chart performance


COLONNES REQUISES DANS LE CSV
──────────────────────────────────────────────────────────────────────────

Pour profiter de tous les KPIs, votre CSV devrait contenir:

✅ OBLIGATOIRES:
   - text (ou content): Texte du tweet
   - date (ou created_at/timestamp): Date du tweet
   
📊 RECOMMANDÉES (générées par classification):
   - sentiment: positive/neutral/negative
   - category: catégorie du tweet
   - priority: critique/haute/moyenne/basse
   - is_claim: 0 ou 1
   - confidence: score de confiance (0-1)
   - is_urgent: True/False


EXEMPLE DE MAPPING
──────────────────────────────────────────────────────────────────────────

Si vos colonnes ont des noms différents, le module essaiera de les détecter
automatiquement, mais vous pouvez les renommer:

df = df.rename(columns={
    'Tweet': 'text',
    'Created_At': 'date',
    'Polarity': 'sentiment',
    'Topic': 'category',
    'Importance': 'priority'
})


PERSONNALISATION DES COULEURS
──────────────────────────────────────────────────────────────────────────

Les couleurs sont définies dans enhanced_kpis_vizualizations.py:

COLORS = {
    'primary': '#CC0000',      # Rouge Free
    'secondary': '#8B0000',    # Rouge foncé
    'positive': '#28a745',     # Vert
    'neutral': '#6c757d',      # Gris
    'negative': '#dc3545'      # Rouge danger
}

Modifiez ces valeurs pour adapter aux couleurs de votre marque.


DÉPANNAGE
──────────────────────────────────────────────────────────────────────────

❌ "Enhanced KPIs module not available"
   → Vérifier que enhanced_kpis_vizualizations.py est dans streamlit_app/services/

❌ "KeyError: 'sentiment'"
   → Votre CSV n'a pas de colonne sentiment. Le module utilisera des fallbacks.

❌ Les graphiques ne s'affichent pas
   → Vérifier que plotly est installé: pip install plotly

❌ Erreur de date
   → Le module essaie de parser automatiquement. Vérifier le format de votre
     colonne date (ISO 8601 recommandé: 2024-11-06 12:30:00)


SUPPORT
──────────────────────────────────────────────────────────────────────────

Pour toute question ou problème, consulter:
- README_TESTS.md pour les exemples
- FINAL_REPORT.md pour la documentation complète
- streamlit_app/services/enhanced_kpis_vizualizations.py pour le code source

"""
    
    return integration_instructions


if __name__ == "__main__":
    print(generate_integration_code())

