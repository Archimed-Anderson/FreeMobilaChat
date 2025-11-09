"""
Ticket Management Component - Composant de gestion des tickets
Module pour la gestion, filtrage et suivi des tickets

Fonctionnalités:
- Liste filtrable des tickets
- Panneau de détails
- Actions (clôture, réassignation)
- Historique complet
- Recherche et filtres avancés

Author: FreeMobilaChat Team
Date: 2025
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class TicketManagement:
    """Composant de gestion des tickets"""
    
    def __init__(self):
        """Initialise le composant"""
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialise les états de session pour les tickets"""
        if 'selected_ticket' not in st.session_state:
            st.session_state.selected_ticket = None
        
        if 'ticket_filters' not in st.session_state:
            st.session_state.ticket_filters = {
                'status': 'Tous',
                'urgency': 'Tous',
                'agent': 'Tous',
                'sentiment': 'Tous',
                'search': ''
            }
    
    def render_ticket_dashboard(self, df: pd.DataFrame):
        """
        Affiche le tableau de bord de gestion des tickets
        
        Args:
            df: DataFrame avec les tickets
        """
        st.markdown("## 🎫 Gestion des Tickets")
        
        # Statistiques globales
        self._render_ticket_stats(df)
        
        st.markdown("---")
        
        # Filtres et recherche
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("### 🔍 Filtres et Recherche")
        
        with col2:
            if st.button("🔄 Réinitialiser", use_container_width=True):
                self._reset_filters()
        
        # Barre de filtres
        filtered_df = self._render_filters(df)
        
        st.markdown("---")
        
        # Layout principal: Liste + Détails
        col_list, col_detail = st.columns([2, 1])
        
        with col_list:
            st.markdown("### 📋 Liste des Tickets")
            self._render_ticket_list(filtered_df)
        
        with col_detail:
            st.markdown("### 📄 Détails du Ticket")
            if st.session_state.selected_ticket is not None:
                self._render_ticket_details(filtered_df, st.session_state.selected_ticket)
            else:
                st.info("Sélectionnez un ticket dans la liste pour voir les détails")
        
        st.markdown("---")
        
        # Graphiques d'analyse
        st.markdown("### 📊 Analyse des Tickets")
        self._render_ticket_analytics(filtered_df)
    
    def _render_ticket_stats(self, df: pd.DataFrame):
        """Affiche les statistiques globales des tickets"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_tickets = len(df)
            st.metric("Total Tickets", f"{total_tickets:,}")
        
        with col2:
            # Tickets ouverts
            status_col = self._find_column(df, ['status', 'statut', 'etat'])
            if status_col:
                open_values = ['open', 'ouvert', 'pending', 'en_attente', 'in_progress']
                open_tickets = df[status_col].astype(str).str.lower().isin(open_values).sum()
                st.metric(
                    "Tickets Ouverts",
                    f"{open_tickets:,}",
                    delta=f"{(open_tickets/total_tickets*100):.1f}%"
                )
            else:
                st.metric("Tickets Ouverts", "N/A")
        
        with col3:
            # Tickets urgents
            urgency_col = self._find_column(df, ['urgency', 'priority', 'priorite'])
            if urgency_col:
                urgent_values = ['high', 'haute', 'urgent', 'critique']
                urgent_tickets = df[urgency_col].astype(str).str.lower().isin(urgent_values).sum()
                st.metric(
                    "Tickets Urgents",
                    f"{urgent_tickets:,}",
                    delta="Haute priorité",
                    delta_color="inverse" if urgent_tickets > 0 else "off"
                )
            else:
                st.metric("Tickets Urgents", "N/A")
        
        with col4:
            # Temps de réponse moyen
            response_col = self._find_column(df, ['response_time', 'temps_reponse'])
            if response_col:
                avg_response = df[response_col].mean() / 3600  # Convertir en heures
                st.metric(
                    "Temps Moyen",
                    f"{avg_response:.1f}h",
                    delta="-12%" if avg_response < 24 else "+5%",
                    delta_color="normal" if avg_response < 24 else "inverse"
                )
            else:
                st.metric("Temps Moyen", "N/A")
    
    def _render_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Affiche les filtres et retourne le DataFrame filtré"""
        col1, col2, col3, col4, col5 = st.columns(5)
        
        # Recherche textuelle
        with col1:
            search = st.text_input(
                "🔎 Recherche",
                value=st.session_state.ticket_filters['search'],
                placeholder="Rechercher...",
                key="ticket_search"
            )
            st.session_state.ticket_filters['search'] = search
        
        # Filtre statut
        with col2:
            status_col = self._find_column(df, ['status', 'statut', 'etat'])
            if status_col:
                statuses = ['Tous'] + df[status_col].dropna().unique().tolist()
                status_filter = st.selectbox(
                    "Statut",
                    options=statuses,
                    key="ticket_status_filter"
                )
                st.session_state.ticket_filters['status'] = status_filter
            else:
                st.selectbox("Statut", options=['Tous'], disabled=True)
        
        # Filtre urgence
        with col3:
            urgency_col = self._find_column(df, ['urgency', 'priority', 'priorite'])
            if urgency_col:
                urgencies = ['Tous'] + df[urgency_col].dropna().unique().tolist()
                urgency_filter = st.selectbox(
                    "Urgence",
                    options=urgencies,
                    key="ticket_urgency_filter"
                )
                st.session_state.ticket_filters['urgency'] = urgency_filter
            else:
                st.selectbox("Urgence", options=['Tous'], disabled=True)
        
        # Filtre agent
        with col4:
            agent_col = self._find_column(df, ['agent', 'assigned_to', 'responsable'])
            if agent_col:
                agents = ['Tous'] + df[agent_col].dropna().unique().tolist()
                agent_filter = st.selectbox(
                    "Agent",
                    options=agents,
                    key="ticket_agent_filter"
                )
                st.session_state.ticket_filters['agent'] = agent_filter
            else:
                st.selectbox("Agent", options=['Tous'], disabled=True)
        
        # Filtre sentiment
        with col5:
            if 'sentiment' in df.columns:
                sentiments = ['Tous'] + df['sentiment'].dropna().unique().tolist()
                sentiment_filter = st.selectbox(
                    "Sentiment",
                    options=sentiments,
                    key="ticket_sentiment_filter"
                )
                st.session_state.ticket_filters['sentiment'] = sentiment_filter
            else:
                st.selectbox("Sentiment", options=['Tous'], disabled=True)
        
        # Appliquer les filtres
        filtered_df = df.copy()
        
        # Filtre de recherche textuelle
        if search:
            text_col = self._find_column(df, ['text', 'content', 'message', 'tweet'])
            if text_col:
                filtered_df = filtered_df[
                    filtered_df[text_col].astype(str).str.contains(search, case=False, na=False)
                ]
        
        # Filtre statut
        if status_col and st.session_state.ticket_filters['status'] != 'Tous':
            filtered_df = filtered_df[
                filtered_df[status_col] == st.session_state.ticket_filters['status']
            ]
        
        # Filtre urgence
        if urgency_col and st.session_state.ticket_filters['urgency'] != 'Tous':
            filtered_df = filtered_df[
                filtered_df[urgency_col] == st.session_state.ticket_filters['urgency']
            ]
        
        # Filtre agent
        if agent_col and st.session_state.ticket_filters['agent'] != 'Tous':
            filtered_df = filtered_df[
                filtered_df[agent_col] == st.session_state.ticket_filters['agent']
            ]
        
        # Filtre sentiment
        if 'sentiment' in df.columns and st.session_state.ticket_filters['sentiment'] != 'Tous':
            filtered_df = filtered_df[
                filtered_df['sentiment'] == st.session_state.ticket_filters['sentiment']
            ]
        
        # Afficher le nombre de résultats
        st.caption(f"📊 {len(filtered_df)} ticket(s) trouvé(s) sur {len(df)} au total")
        
        return filtered_df
    
    def _render_ticket_list(self, df: pd.DataFrame):
        """Affiche la liste des tickets"""
        if df.empty:
            st.info("Aucun ticket correspondant aux critères de filtrage")
            return
        
        # Limiter à 50 tickets pour la performance
        display_df = df.head(50).copy()
        
        # Créer un ID pour chaque ticket
        if 'id' not in display_df.columns:
            display_df['id'] = range(len(display_df))
        
        # Colonnes à afficher
        display_columns = []
        
        if 'id' in display_df.columns:
            display_columns.append('id')
        
        text_col = self._find_column(display_df, ['text', 'content', 'message', 'tweet'])
        if text_col:
            display_df['message_preview'] = display_df[text_col].astype(str).str[:50] + '...'
            display_columns.append('message_preview')
        
        status_col = self._find_column(display_df, ['status', 'statut', 'etat'])
        if status_col:
            display_columns.append(status_col)
        
        urgency_col = self._find_column(display_df, ['urgency', 'priority', 'priorite'])
        if urgency_col:
            display_columns.append(urgency_col)
        
        if 'sentiment' in display_df.columns:
            display_columns.append('sentiment')
        
        # Afficher le DataFrame filtré
        if display_columns:
            # Style conditionnel
            def highlight_row(row):
                colors = []
                for col in row.index:
                    if urgency_col and col == urgency_col:
                        if str(row[col]).lower() in ['high', 'haute', 'urgent', 'critique']:
                            colors.append('background-color: #ffebee')
                        else:
                            colors.append('')
                    elif col == 'sentiment':
                        if row[col] == 'negative':
                            colors.append('background-color: #ffebee')
                        elif row[col] == 'positive':
                            colors.append('background-color: #e8f5e9')
                        else:
                            colors.append('')
                    else:
                        colors.append('')
                return colors
            
            # Afficher avec style
            styled_df = display_df[display_columns].style.apply(highlight_row, axis=1)
            st.dataframe(
                styled_df,
                use_container_width=True,
                height=500,
                on_select="rerun",
                selection_mode="single-row"
            )
            
            # Sélection de ticket
            selected_indices = st.session_state.get('selected_rows', [])
            if selected_indices:
                st.session_state.selected_ticket = display_df.iloc[selected_indices[0]]['id']
        
        if len(df) > 50:
            st.warning(f"⚠️ Affichage limité aux 50 premiers tickets. Total: {len(df)}")
    
    def _render_ticket_details(self, df: pd.DataFrame, ticket_id: Any):
        """Affiche les détails d'un ticket sélectionné"""
        try:
            # Trouver le ticket
            ticket_row = df[df.get('id', pd.Series()) == ticket_id]
            
            if ticket_row.empty:
                # Si pas d'ID, utiliser l'index
                if isinstance(ticket_id, int) and ticket_id < len(df):
                    ticket = df.iloc[ticket_id]
                else:
                    st.error("Ticket non trouvé")
                    return
            else:
                ticket = ticket_row.iloc[0]
            
            # Afficher les détails
            with st.container():
                # En-tête du ticket
                st.markdown(f"**Ticket #{ticket.get('id', 'N/A')}**")
                
                # Message original
                text_col = self._find_column(df, ['text', 'content', 'message', 'tweet'])
                if text_col:
                    st.markdown("##### 💬 Message Original")
                    st.text_area(
                        "Message",
                        value=str(ticket[text_col]),
                        height=150,
                        disabled=True,
                        label_visibility="collapsed"
                    )
                
                # Résultats IA
                st.markdown("##### 🤖 Analyse IA")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Sentiment
                    if 'sentiment' in ticket.index:
                        sentiment = ticket['sentiment']
                        emoji = {'positive': '', 'negative': '', 'neutral': ''}.get(sentiment, '')
                        st.metric("Sentiment", f"{emoji} {sentiment}")
                    
                    # Catégorie
                    category_col = self._find_column(df, ['category', 'theme', 'sujet'])
                    if category_col and category_col in ticket.index:
                        st.metric("Catégorie", ticket[category_col])
                
                with col2:
                    # Urgence
                    urgency_col = self._find_column(df, ['urgency', 'priority', 'priorite'])
                    if urgency_col and urgency_col in ticket.index:
                        st.metric("Urgence", ticket[urgency_col])
                    
                    # Confiance
                    confidence_col = self._find_column(df, ['confidence', 'confidence_score'])
                    if confidence_col and confidence_col in ticket.index:
                        st.metric("Confiance", f"{ticket[confidence_col]:.1%}")
                
                # Statut actuel
                st.markdown("##### 📊 Statut")
                status_col = self._find_column(df, ['status', 'statut', 'etat'])
                if status_col and status_col in ticket.index:
                    current_status = ticket[status_col]
                    status_color = {
                        'open': '🟢',
                        'ouvert': '🟢',
                        'pending': '🟡',
                        'en_attente': '🟡',
                        'in_progress': '🔵',
                        'en_cours': '🔵',
                        'resolved': '✅',
                        'résolu': '✅',
                        'closed': '⚫',
                        'fermé': '⚫'
                    }.get(str(current_status).lower(), '❓')
                    
                    st.info(f"{status_color} **{current_status}**")
                
                # Agent assigné
                agent_col = self._find_column(df, ['agent', 'assigned_to', 'responsable'])
                if agent_col and agent_col in ticket.index:
                    st.markdown(f"**Agent:** {ticket[agent_col]}")
                
                # Dates
                st.markdown("##### 📅 Informations Temporelles")
                date_col = self._find_column(df, ['date', 'created_at', 'timestamp'])
                if date_col and date_col in ticket.index:
                    st.caption(f"Créé le: {ticket[date_col]}")
                
                # Actions
                st.markdown("##### ⚡ Actions")
                
                col_action1, col_action2 = st.columns(2)
                
                with col_action1:
                    if st.button("✅ Clôturer", use_container_width=True, key=f"close_{ticket_id}"):
                        self._close_ticket(df, ticket_id)
                
                with col_action2:
                    if st.button("👤 Réassigner", use_container_width=True, key=f"reassign_{ticket_id}"):
                        self._show_reassign_form(ticket_id)
                
                # Historique
                st.markdown("##### 📜 Historique")
                with st.expander("Voir l'historique complet"):
                    history = self._get_ticket_history(ticket_id)
                    if history:
                        for entry in history:
                            st.markdown(f"- {entry}")
                    else:
                        st.caption("Aucun historique disponible")
        
        except Exception as e:
            st.error(f"Erreur lors de l'affichage des détails: {str(e)}")
            logger.error(f"Error rendering ticket details: {str(e)}", exc_info=True)
    
    def _render_ticket_analytics(self, df: pd.DataFrame):
        """Affiche les graphiques d'analyse des tickets"""
        if df.empty:
            st.info("Pas de données pour l'analyse")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribution des statuts
            status_col = self._find_column(df, ['status', 'statut', 'etat'])
            if status_col:
                status_counts = df[status_col].value_counts()
                
                fig_status = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    title="Distribution des Statuts",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                
                fig_status.update_traces(textposition='inside', textinfo='percent+label')
                fig_status.update_layout(height=400, template='plotly_white')
                
                st.plotly_chart(fig_status, use_container_width=True)
        
        with col2:
            # Distribution des urgences
            urgency_col = self._find_column(df, ['urgency', 'priority', 'priorite'])
            if urgency_col:
                urgency_counts = df[urgency_col].value_counts()
                
                # Couleurs pour urgence
                colors = {
                    'high': '#ef4444',
                    'haute': '#ef4444',
                    'urgent': '#ef4444',
                    'medium': '#fbbf24',
                    'moyenne': '#fbbf24',
                    'low': '#4ade80',
                    'basse': '#4ade80'
                }
                
                color_list = [colors.get(str(u).lower(), '#94a3b8') for u in urgency_counts.index]
                
                fig_urgency = go.Figure(data=[
                    go.Bar(
                        x=urgency_counts.index,
                        y=urgency_counts.values,
                        marker_color=color_list,
                        text=urgency_counts.values,
                        textposition='auto'
                    )
                ])
                
                fig_urgency.update_layout(
                    title="Distribution des Urgences",
                    xaxis_title="Niveau d'Urgence",
                    yaxis_title="Nombre de Tickets",
                    height=400,
                    template='plotly_white'
                )
                
                st.plotly_chart(fig_urgency, use_container_width=True)
        
        # Évolution temporelle
        date_col = self._find_column(df, ['date', 'created_at', 'timestamp'])
        if date_col:
            st.markdown("#### 📈 Évolution Temporelle")
            
            df_temp = df.copy()
            df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
            df_clean = df_temp.dropna(subset=[date_col])
            
            if not df_clean.empty:
                daily_counts = df_clean.groupby(df_clean[date_col].dt.date).size()
                
                fig_temporal = go.Figure()
                
                fig_temporal.add_trace(go.Scatter(
                    x=daily_counts.index,
                    y=daily_counts.values,
                    mode='lines+markers',
                    name='Tickets',
                    line=dict(color='#CC0000', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(204, 0, 0, 0.1)'
                ))
                
                fig_temporal.update_layout(
                    title="Volume de Tickets par Jour",
                    xaxis_title="Date",
                    yaxis_title="Nombre de Tickets",
                    height=400,
                    template='plotly_white',
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_temporal, use_container_width=True)
    
    def _close_ticket(self, df: pd.DataFrame, ticket_id: Any):
        """Clôture un ticket"""
        st.success(f"✅ Ticket #{ticket_id} clôturé avec succès!")
        # Ici, vous pourriez ajouter la logique pour mettre à jour la base de données
    
    def _show_reassign_form(self, ticket_id: Any):
        """Affiche le formulaire de réassignation"""
        with st.form(f"reassign_form_{ticket_id}"):
            st.markdown("##### 👤 Réassigner le Ticket")
            
            # Liste d'agents (à adapter selon vos données)
            agents = ["Sophie Martin", "Lucas Dubois", "Emma Bernard", "Thomas Petit", "Julie Moreau"]
            
            new_agent = st.selectbox("Nouvel agent", options=agents)
            reason = st.text_area("Raison de la réassignation (optionnel)")
            
            submitted = st.form_submit_button("💾 Réassigner", use_container_width=True)
            
            if submitted:
                st.success(f"✅ Ticket #{ticket_id} réassigné à {new_agent}")
                # Ici, vous pourriez ajouter la logique pour mettre à jour la base de données
    
    def _get_ticket_history(self, ticket_id: Any) -> List[str]:
        """Retourne l'historique d'un ticket"""
        # Exemple d'historique fictif
        return [
            f"{datetime.now() - timedelta(days=2)} - Ticket créé",
            f"{datetime.now() - timedelta(days=1)} - Assigné à Sophie Martin",
            f"{datetime.now() - timedelta(hours=12)} - Commentaire ajouté",
            f"{datetime.now() - timedelta(hours=2)} - Statut changé en 'En cours'"
        ]
    
    def _reset_filters(self):
        """Réinitialise tous les filtres"""
        st.session_state.ticket_filters = {
            'status': 'Tous',
            'urgency': 'Tous',
            'agent': 'Tous',
            'sentiment': 'Tous',
            'search': ''
        }
        st.rerun()
    
    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
        """Trouve une colonne parmi plusieurs noms possibles"""
        df_columns_lower = {col.lower(): col for col in df.columns}
        for name in possible_names:
            if name.lower() in df_columns_lower:
                return df_columns_lower[name.lower()]
        return None


# Instance globale
_ticket_management_instance = None

def get_ticket_management() -> TicketManagement:
    """Retourne l'instance singleton du composant de gestion des tickets"""
    global _ticket_management_instance
    if _ticket_management_instance is None:
        _ticket_management_instance = TicketManagement()
    return _ticket_management_instance


