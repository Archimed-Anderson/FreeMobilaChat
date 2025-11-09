"""
Team Management Component - Composant de gestion d'équipe
Module pour la gestion des collaborateurs et de leurs performances

Fonctionnalités:
- Tableau dynamique des collaborateurs
- Alertes de performance
- Graphiques comparatifs
- Ajout/modification de membres

Author: FreeMobilaChat Team
Date: 2025
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class TeamManagement:
    """Composant de gestion d'équipe"""
    
    def __init__(self):
        """Initialise le composant"""
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialise les états de session pour l'équipe"""
        if 'team_members' not in st.session_state:
            st.session_state.team_members = self._get_default_team()
        
        if 'team_history' not in st.session_state:
            st.session_state.team_history = []
    
    def render_team_dashboard(self, df: Optional[pd.DataFrame] = None):
        """
        Affiche le tableau de bord de gestion d'équipe
        
        Args:
            df: DataFrame avec les données pour calculer les performances
        """
        st.markdown("## 👥 Gestion d'Équipe")
        
        # Statistiques globales de l'équipe
        self._render_team_stats()
        
        st.markdown("---")
        
        # Tableau des membres
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("### 📋 Liste des Collaborateurs")
        
        with col2:
            if st.button("➕ Ajouter un membre", use_container_width=True):
                self._show_add_member_form()
        
        # Afficher le tableau
        self._render_team_table(df)
        
        st.markdown("---")
        
        # Graphiques de performance
        st.markdown("### 📊 Performance de l'Équipe")
        self._render_performance_charts(df)
        
        st.markdown("---")
        
        # Alertes
        self._render_team_alerts(df)
    
    def _render_team_stats(self):
        """Affiche les statistiques globales de l'équipe"""
        team = st.session_state.team_members
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_members = len(team)
            active_members = sum(1 for m in team if m.get('status') == 'Actif')
            st.metric(
                "Membres de l'équipe",
                total_members,
                delta=f"{active_members} actifs"
            )
        
        with col2:
            avg_satisfaction = sum(m.get('satisfaction', 0) for m in team) / len(team) if team else 0
            delta = "Bon" if avg_satisfaction >= 70 else "À améliorer"
            delta_color = "normal" if avg_satisfaction >= 70 else "inverse"
            st.metric(
                "Satisfaction moyenne",
                f"{avg_satisfaction:.1f}%",
                delta=delta,
                delta_color=delta_color
            )
        
        with col3:
            total_tickets = sum(m.get('tickets_traites', 0) for m in team)
            st.metric(
                "Total tickets traités",
                f"{total_tickets:,}",
                delta="Ce mois"
            )
        
        with col4:
            avg_resolution_time = sum(m.get('temps_moyen', 0) for m in team) / len(team) if team else 0
            st.metric(
                "Temps moyen",
                f"{avg_resolution_time:.1f}h",
                delta="-15%" if avg_resolution_time < 24 else "+5%",
                delta_color="normal" if avg_resolution_time < 24 else "inverse"
            )
    
    def _render_team_table(self, df: Optional[pd.DataFrame] = None):
        """Affiche le tableau des membres de l'équipe"""
        team = st.session_state.team_members
        
        if not team:
            st.info("Aucun membre dans l'équipe. Cliquez sur 'Ajouter un membre' pour commencer.")
            return
        
        # Créer DataFrame pour affichage
        team_df = pd.DataFrame(team)
        
        # Calculer les performances si données disponibles
        if df is not None and 'agent' in df.columns:
            team_df = self._calculate_team_performance(team_df, df)
        
        # Formatter pour l'affichage
        display_columns = {
            'nom': 'Nom',
            'role': 'Rôle',
            'satisfaction': 'Satisfaction (%)',
            'tickets_traites': 'Tickets Traités',
            'temps_moyen': 'Temps Moyen (h)',
            'status': 'Statut'
        }
        
        # Sélectionner et renommer les colonnes
        available_cols = [col for col in display_columns.keys() if col in team_df.columns]
        team_display = team_df[available_cols].copy()
        team_display.columns = [display_columns[col] for col in available_cols]
        
        # Style conditionnel pour satisfaction
        def highlight_satisfaction(row):
            if 'Satisfaction (%)' in row:
                satisfaction = row['Satisfaction (%)']
                if satisfaction < 70:
                    return ['background-color: #ffebee'] * len(row)
                elif satisfaction >= 85:
                    return ['background-color: #e8f5e9'] * len(row)
            return [''] * len(row)
        
        # Afficher le tableau
        styled_df = team_display.style.apply(highlight_satisfaction, axis=1)
        st.dataframe(styled_df, use_container_width=True, height=400)
        
        # Actions sur les membres
        st.markdown("#### Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_member = st.selectbox(
                "Sélectionner un membre",
                options=[m['nom'] for m in team],
                key="selected_member_action"
            )
        
        with col2:
            if st.button("✏️ Modifier", use_container_width=True):
                self._show_edit_member_form(selected_member)
        
        with col3:
            if st.button("🗑️ Supprimer", use_container_width=True):
                self._remove_member(selected_member)
    
    def _render_performance_charts(self, df: Optional[pd.DataFrame] = None):
        """Affiche les graphiques de performance de l'équipe"""
        team = st.session_state.team_members
        
        if not team:
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Graphique de satisfaction
            fig_satisfaction = go.Figure()
            
            names = [m['nom'] for m in team]
            satisfactions = [m.get('satisfaction', 0) for m in team]
            
            colors = ['#4ade80' if s >= 85 else '#fbbf24' if s >= 70 else '#ef4444' 
                     for s in satisfactions]
            
            fig_satisfaction.add_trace(go.Bar(
                x=names,
                y=satisfactions,
                marker_color=colors,
                text=satisfactions,
                texttemplate='%{text:.1f}%',
                textposition='outside'
            ))
            
            fig_satisfaction.add_hline(
                y=70,
                line_dash="dash",
                line_color="red",
                annotation_text="Seuil d'alerte (70%)"
            )
            
            fig_satisfaction.update_layout(
                title="Satisfaction Client par Agent",
                xaxis_title="Agent",
                yaxis_title="Satisfaction (%)",
                yaxis_range=[0, 100],
                height=400,
                template='plotly_white'
            )
            
            st.plotly_chart(fig_satisfaction, use_container_width=True)
        
        with col2:
            # Graphique de productivité
            fig_productivity = go.Figure()
            
            tickets = [m.get('tickets_traites', 0) for m in team]
            temps = [m.get('temps_moyen', 0) for m in team]
            
            fig_productivity.add_trace(go.Scatter(
                x=tickets,
                y=temps,
                mode='markers+text',
                marker=dict(
                    size=[m.get('satisfaction', 50) / 5 for m in team],
                    color=satisfactions,
                    colorscale='RdYlGn',
                    showscale=True,
                    colorbar=dict(title="Satisfaction")
                ),
                text=names,
                textposition='top center',
                hovertemplate='<b>%{text}</b><br>Tickets: %{x}<br>Temps moyen: %{y:.1f}h<extra></extra>'
            ))
            
            fig_productivity.update_layout(
                title="Productivité vs Temps de Traitement",
                xaxis_title="Nombre de Tickets Traités",
                yaxis_title="Temps Moyen de Traitement (h)",
                height=400,
                template='plotly_white'
            )
            
            st.plotly_chart(fig_productivity, use_container_width=True)
        
        # Graphique radar de compétences
        st.markdown("#### 🎯 Radar de Compétences")
        self._render_skills_radar()
    
    def _render_skills_radar(self):
        """Affiche un graphique radar des compétences de l'équipe"""
        team = st.session_state.team_members
        
        if not team:
            return
        
        # Compétences évaluées
        skills = ['Rapidité', 'Qualité', 'Communication', 'Technique', 'Satisfaction']
        
        fig = go.Figure()
        
        for member in team[:5]:  # Limiter à 5 membres pour la lisibilité
            # Calculer scores de compétences basés sur les métriques
            satisfaction = member.get('satisfaction', 70)
            tickets = min(100, member.get('tickets_traites', 50) * 2)
            temps = max(0, 100 - member.get('temps_moyen', 24) * 2)
            
            skill_values = [
                temps,  # Rapidité (inversement proportionnel au temps)
                satisfaction,  # Qualité
                satisfaction * 0.9,  # Communication (basé sur satisfaction)
                satisfaction * 0.85,  # Technique
                satisfaction  # Satisfaction
            ]
            
            fig.add_trace(go.Scatterpolar(
                r=skill_values,
                theta=skills,
                fill='toself',
                name=member['nom']
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=True,
            height=500,
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_team_alerts(self, df: Optional[pd.DataFrame] = None):
        """Affiche les alertes concernant l'équipe"""
        st.markdown("### ⚠️ Alertes et Recommandations")
        
        team = st.session_state.team_members
        alerts = []
        
        # Vérifier satisfaction < 70%
        for member in team:
            satisfaction = member.get('satisfaction', 0)
            if satisfaction < 70:
                alerts.append({
                    'level': 'error' if satisfaction < 50 else 'warning',
                    'member': member['nom'],
                    'type': 'satisfaction',
                    'message': f"Satisfaction faible pour {member['nom']}: {satisfaction:.1f}%",
                    'recommendation': "Entretien individuel recommandé pour identifier les problèmes"
                })
        
        # Vérifier temps de traitement élevé
        avg_time = sum(m.get('temps_moyen', 0) for m in team) / len(team) if team else 0
        for member in team:
            temps = member.get('temps_moyen', 0)
            if temps > avg_time * 1.5 and temps > 24:
                alerts.append({
                    'level': 'warning',
                    'member': member['nom'],
                    'type': 'performance',
                    'message': f"Temps de traitement élevé pour {member['nom']}: {temps:.1f}h",
                    'recommendation': "Formation complémentaire ou réorganisation des tâches recommandée"
                })
        
        # Vérifier surcharge de travail
        max_tickets = max((m.get('tickets_traites', 0) for m in team), default=0)
        for member in team:
            tickets = member.get('tickets_traites', 0)
            if tickets > max_tickets * 0.8 and tickets > 100:
                alerts.append({
                    'level': 'info',
                    'member': member['nom'],
                    'type': 'workload',
                    'message': f"Charge de travail élevée pour {member['nom']}: {tickets} tickets",
                    'recommendation': "Envisager une redistribution de la charge ou des ressources supplémentaires"
                })
        
        # Afficher les alertes
        if alerts:
            for alert in alerts:
                if alert['level'] == 'error':
                    st.error(f"🔴 **{alert['message']}**\n\n💡 {alert['recommendation']}")
                elif alert['level'] == 'warning':
                    st.warning(f"🟠 **{alert['message']}**\n\n💡 {alert['recommendation']}")
                else:
                    st.info(f"🔵 **{alert['message']}**\n\n💡 {alert['recommendation']}")
        else:
            st.success("✅ Aucune alerte. L'équipe performe bien!")
    
    def _show_add_member_form(self):
        """Affiche le formulaire d'ajout de membre"""
        with st.form("add_member_form"):
            st.markdown("### ➕ Ajouter un Membre")
            
            col1, col2 = st.columns(2)
            
            with col1:
                nom = st.text_input("Nom complet*", placeholder="Jean Dupont")
                email = st.text_input("Email*", placeholder="jean.dupont@example.com")
                role = st.selectbox(
                    "Rôle*",
                    ["Agent SAV", "Agent Technique", "Superviseur", "Manager", "Analyste"]
                )
            
            with col2:
                date_entree = st.date_input("Date d'entrée", value=datetime.now())
                status = st.selectbox("Statut", ["Actif", "En formation", "Inactif"])
                satisfaction_initiale = st.slider("Satisfaction initiale (%)", 0, 100, 75)
            
            submitted = st.form_submit_button("💾 Ajouter", use_container_width=True)
            
            if submitted:
                if nom and email and role:
                    new_member = {
                        'nom': nom,
                        'email': email,
                        'role': role,
                        'date_entree': date_entree.isoformat(),
                        'status': status,
                        'satisfaction': satisfaction_initiale,
                        'tickets_traites': 0,
                        'temps_moyen': 0,
                        'date_ajout': datetime.now().isoformat()
                    }
                    
                    st.session_state.team_members.append(new_member)
                    st.success(f"✅ Membre {nom} ajouté avec succès!")
                    st.rerun()
                else:
                    st.error("⚠️ Veuillez remplir tous les champs obligatoires (*)")
    
    def _show_edit_member_form(self, member_name: str):
        """Affiche le formulaire de modification de membre"""
        member = next((m for m in st.session_state.team_members if m['nom'] == member_name), None)
        
        if not member:
            st.error("Membre non trouvé")
            return
        
        with st.form("edit_member_form"):
            st.markdown(f"### ✏️ Modifier {member_name}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                email = st.text_input("Email", value=member.get('email', ''))
                role = st.selectbox(
                    "Rôle",
                    ["Agent SAV", "Agent Technique", "Superviseur", "Manager", "Analyste"],
                    index=["Agent SAV", "Agent Technique", "Superviseur", "Manager", "Analyste"].index(
                        member.get('role', 'Agent SAV')
                    )
                )
            
            with col2:
                status = st.selectbox(
                    "Statut",
                    ["Actif", "En formation", "Inactif"],
                    index=["Actif", "En formation", "Inactif"].index(member.get('status', 'Actif'))
                )
                satisfaction = st.slider(
                    "Satisfaction (%)",
                    0, 100,
                    int(member.get('satisfaction', 75))
                )
            
            col_submit1, col_submit2 = st.columns(2)
            
            with col_submit1:
                submitted = st.form_submit_button("💾 Enregistrer", use_container_width=True)
            
            with col_submit2:
                cancelled = st.form_submit_button("❌ Annuler", use_container_width=True)
            
            if submitted:
                member['email'] = email
                member['role'] = role
                member['status'] = status
                member['satisfaction'] = satisfaction
                member['date_modification'] = datetime.now().isoformat()
                
                st.success(f"✅ Membre {member_name} modifié avec succès!")
                st.rerun()
            
            if cancelled:
                st.rerun()
    
    def _remove_member(self, member_name: str):
        """Supprime un membre de l'équipe"""
        st.session_state.team_members = [
            m for m in st.session_state.team_members if m['nom'] != member_name
        ]
        st.success(f"✅ Membre {member_name} supprimé")
        st.rerun()
    
    def _calculate_team_performance(self, team_df: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
        """Calcule les performances réelles basées sur les données"""
        # Cette fonction peut être étendue pour calculer les vraies performances
        # à partir des données réelles du DataFrame
        return team_df
    
    def _get_default_team(self) -> List[Dict[str, Any]]:
        """Retourne une équipe par défaut pour la démonstration"""
        return [
            {
                'nom': 'Sophie Martin',
                'email': 'sophie.martin@example.com',
                'role': 'Agent SAV',
                'satisfaction': 87.5,
                'tickets_traites': 245,
                'temps_moyen': 18.5,
                'status': 'Actif',
                'date_entree': '2024-01-15'
            },
            {
                'nom': 'Lucas Dubois',
                'email': 'lucas.dubois@example.com',
                'role': 'Agent Technique',
                'satisfaction': 92.3,
                'tickets_traites': 198,
                'temps_moyen': 22.1,
                'status': 'Actif',
                'date_entree': '2023-11-20'
            },
            {
                'nom': 'Emma Bernard',
                'email': 'emma.bernard@example.com',
                'role': 'Superviseur',
                'satisfaction': 94.1,
                'tickets_traites': 156,
                'temps_moyen': 15.7,
                'status': 'Actif',
                'date_entree': '2023-09-01'
            },
            {
                'nom': 'Thomas Petit',
                'email': 'thomas.petit@example.com',
                'role': 'Agent SAV',
                'satisfaction': 65.8,
                'tickets_traites': 312,
                'temps_moyen': 28.3,
                'status': 'Actif',
                'date_entree': '2024-03-10'
            },
            {
                'nom': 'Julie Moreau',
                'email': 'julie.moreau@example.com',
                'role': 'Agent Technique',
                'satisfaction': 89.2,
                'tickets_traites': 221,
                'temps_moyen': 19.8,
                'status': 'Actif',
                'date_entree': '2023-12-05'
            }
        ]


# Instance globale
_team_management_instance = None

def get_team_management() -> TeamManagement:
    """Retourne l'instance singleton du composant de gestion d'équipe"""
    global _team_management_instance
    if _team_management_instance is None:
        _team_management_instance = TeamManagement()
    return _team_management_instance


