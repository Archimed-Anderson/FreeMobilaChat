"""
Filter components for Streamlit dashboard
Reusable filter widgets for tweet analysis
"""

import streamlit as st
from typing import Dict, List, Any, Optional
from datetime import datetime, date, timedelta


class FilterManager:
    """Manages all filter components and state"""
    
    def __init__(self):
        """Initialize filter manager"""
        self.filters = {}
    
    def sentiment_filter(self, key: str = "sentiment_filter") -> Optional[str]:
        """
        Sentiment filter component
        
        Args:
            key: Unique key for the widget
            
        Returns:
            Selected sentiment or None for all
        """
        sentiment_options = {
            "Tous": None,
            "Positif": "positive",
            "Neutre": "neutral",
            "Négatif": "negative",
            "Inconnu": "unknown"
        }

        selected = st.selectbox(
            "Sentiment",
            options=list(sentiment_options.keys()),
            key=key,
            help="Filtrer par sentiment des tweets"
        )
        
        return sentiment_options[selected]
    
    def category_filter(self, key: str = "category_filter") -> Optional[str]:
        """
        Category filter component
        
        Args:
            key: Unique key for the widget
            
        Returns:
            Selected category or None for all
        """
        category_options = {
            "Toutes": None,
            "Facturation": "facturation",
            "Réseau": "réseau",
            "Technique": "technique",
            "Abonnement": "abonnement",
            "Réclamation": "réclamation",
            "Compliment": "compliment",
            "Question": "question",
            "Autre": "autre"
        }

        selected = st.selectbox(
            "Catégorie",
            options=list(category_options.keys()),
            key=key,
            help="Filtrer par catégorie de tweet"
        )
        
        return category_options[selected]
    
    def priority_filter(self, key: str = "priority_filter") -> Optional[str]:
        """
        Priority filter component
        
        Args:
            key: Unique key for the widget
            
        Returns:
            Selected priority or None for all
        """
        priority_options = {
            "Toutes": None,
            "Critique": "critique",
            "Haute": "haute",
            "Moyenne": "moyenne",
            "Basse": "basse"
        }

        selected = st.selectbox(
            "Priorité",
            options=list(priority_options.keys()),
            key=key,
            help="Filtrer par niveau de priorité"
        )
        
        return priority_options[selected]
    
    def date_range_filter(self, key: str = "date_filter") -> tuple[date, date]:
        """
        Date range filter component
        
        Args:
            key: Unique key for the widget
            
        Returns:
            Tuple of (start_date, end_date)
        """
        col1, col2 = st.columns(2)
        
        # Default to last 7 days
        default_end = date.today()
        default_start = default_end - timedelta(days=7)
        
        with col1:
            start_date = st.date_input(
                "📅 Date début",
                value=default_start,
                key=f"{key}_start",
                help="Date de début de la période"
            )
        
        with col2:
            end_date = st.date_input(
                "📅 Date fin",
                value=default_end,
                key=f"{key}_end",
                help="Date de fin de la période"
            )
        
        return start_date, end_date
    
    def urgency_filter(self, key: str = "urgency_filter") -> bool:
        """
        Urgency filter component
        
        Args:
            key: Unique key for the widget
            
        Returns:
            True if only urgent tweets should be shown
        """
        return st.checkbox(
            "Tweets urgents uniquement",
            key=key,
            help="Afficher seulement les tweets marqués comme urgents"
        )
    
    def response_needed_filter(self, key: str = "response_filter") -> bool:
        """
        Response needed filter component
        
        Args:
            key: Unique key for the widget
            
        Returns:
            True if only tweets needing response should be shown
        """
        return st.checkbox(
            "Nécessitent une réponse",
            key=key,
            help="Afficher seulement les tweets nécessitant une réponse"
        )
    
    def author_filter(self, authors: List[str], key: str = "author_filter") -> Optional[str]:
        """
        Author filter component
        
        Args:
            authors: List of available authors
            key: Unique key for the widget
            
        Returns:
            Selected author or None for all
        """
        if not authors:
            return None
        
        author_options = ["Tous"] + sorted(authors)
        
        selected = st.selectbox(
            "👤 Auteur",
            options=author_options,
            key=key,
            help="Filtrer par auteur du tweet"
        )
        
        return selected if selected != "Tous" else None
    
    def keyword_filter(self, key: str = "keyword_filter") -> Optional[str]:
        """
        Keyword search filter component
        
        Args:
            key: Unique key for the widget
            
        Returns:
            Search keyword or None
        """
        keyword = st.text_input(
            "🔍 Recherche par mot-clé",
            key=key,
            placeholder="Rechercher dans le texte des tweets...",
            help="Rechercher des tweets contenant ce mot-clé"
        )
        
        return keyword.strip() if keyword.strip() else None
    
    def create_filter_sidebar(self, available_authors: List[str] = None) -> Dict[str, Any]:
        """
        Create complete filter sidebar
        
        Args:
            available_authors: List of available authors for filtering
            
        Returns:
            Dictionary with all filter values
        """
        with st.sidebar:
            st.header("Filtres")
            
            # Basic filters
            filters = {
                'sentiment': self.sentiment_filter("sidebar_sentiment"),
                'category': self.category_filter("sidebar_category"),
                'priority': self.priority_filter("sidebar_priority"),
                'urgent_only': self.urgency_filter("sidebar_urgent"),
                'response_needed': self.response_needed_filter("sidebar_response"),
                'keyword': self.keyword_filter("sidebar_keyword")
            }
            
            # Date range
            start_date, end_date = self.date_range_filter("sidebar_date")
            filters['start_date'] = start_date
            filters['end_date'] = end_date
            
            # Author filter if authors provided
            if available_authors:
                filters['author'] = self.author_filter(available_authors, "sidebar_author")
            
            st.divider()
            
            # Filter summary
            active_filters = sum(1 for v in filters.values() if v is not None and v != False)
            if active_filters > 0:
                st.info(f"{active_filters} filtre(s) actif(s)")

            # Clear filters button
            if st.button("Effacer tous les filtres", key="clear_filters"):
                # Clear session state for all filter keys
                filter_keys = [
                    "sidebar_sentiment", "sidebar_category", "sidebar_priority",
                    "sidebar_urgent", "sidebar_response", "sidebar_keyword",
                    "sidebar_date_start", "sidebar_date_end", "sidebar_author"
                ]
                for key in filter_keys:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
            
            return filters
    
    def create_inline_filters(self, col_count: int = 4) -> Dict[str, Any]:
        """
        Create inline filters for main content area
        
        Args:
            col_count: Number of columns for layout
            
        Returns:
            Dictionary with filter values
        """
        cols = st.columns(col_count)
        
        filters = {}
        
        with cols[0]:
            filters['sentiment'] = self.sentiment_filter("inline_sentiment")
        
        with cols[1]:
            filters['category'] = self.category_filter("inline_category")
        
        with cols[2]:
            filters['priority'] = self.priority_filter("inline_priority")
        
        if col_count > 3:
            with cols[3]:
                filters['urgent_only'] = self.urgency_filter("inline_urgent")
        
        return filters
    
    def apply_filters_to_data(self, data: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """
        Apply filters to tweet data
        
        Args:
            data: List of tweet dictionaries
            filters: Filter criteria
            
        Returns:
            Filtered data
        """
        if not data:
            return data
        
        filtered_data = data.copy()
        
        # Apply sentiment filter
        if filters.get('sentiment'):
            filtered_data = [
                tweet for tweet in filtered_data 
                if tweet.get('sentiment') == filters['sentiment']
            ]
        
        # Apply category filter
        if filters.get('category'):
            filtered_data = [
                tweet for tweet in filtered_data 
                if tweet.get('category') == filters['category']
            ]
        
        # Apply priority filter
        if filters.get('priority'):
            filtered_data = [
                tweet for tweet in filtered_data 
                if tweet.get('priority') == filters['priority']
            ]
        
        # Apply urgency filter
        if filters.get('urgent_only'):
            filtered_data = [
                tweet for tweet in filtered_data 
                if tweet.get('is_urgent', False)
            ]
        
        # Apply response needed filter
        if filters.get('response_needed'):
            filtered_data = [
                tweet for tweet in filtered_data 
                if tweet.get('needs_response', False)
            ]
        
        # Apply author filter
        if filters.get('author'):
            filtered_data = [
                tweet for tweet in filtered_data 
                if tweet.get('author') == filters['author']
            ]
        
        # Apply keyword filter
        if filters.get('keyword'):
            keyword = filters['keyword'].lower()
            filtered_data = [
                tweet for tweet in filtered_data 
                if keyword in tweet.get('text', '').lower()
            ]
        
        # Apply date range filter
        if filters.get('start_date') and filters.get('end_date'):
            start_date = filters['start_date']
            end_date = filters['end_date']
            
            filtered_data = [
                tweet for tweet in filtered_data 
                if start_date <= datetime.fromisoformat(tweet.get('date', '')).date() <= end_date
            ]
        
        return filtered_data
    
    def get_filter_summary(self, filters: Dict[str, Any]) -> str:
        """
        Generate a summary of active filters
        
        Args:
            filters: Filter dictionary
            
        Returns:
            Human-readable filter summary
        """
        active_filters = []
        
        if filters.get('sentiment'):
            active_filters.append(f"Sentiment: {filters['sentiment']}")
        
        if filters.get('category'):
            active_filters.append(f"Catégorie: {filters['category']}")
        
        if filters.get('priority'):
            active_filters.append(f"Priorité: {filters['priority']}")
        
        if filters.get('urgent_only'):
            active_filters.append("Urgents uniquement")
        
        if filters.get('response_needed'):
            active_filters.append("Réponse nécessaire")
        
        if filters.get('author'):
            active_filters.append(f"Auteur: {filters['author']}")
        
        if filters.get('keyword'):
            active_filters.append(f"Mot-clé: '{filters['keyword']}'")
        
        if filters.get('start_date') and filters.get('end_date'):
            active_filters.append(f"Période: {filters['start_date']} - {filters['end_date']}")
        
        if not active_filters:
            return "Aucun filtre actif"
        
        return " | ".join(active_filters)
