"""
Table components for Streamlit dashboard
Interactive data tables for tweet analysis
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
import io


class TableManager:
    """Manages all table components and data display"""
    
    def __init__(self):
        """Initialize table manager"""
        self.default_page_size = 20
    
    def tweets_data_table(self, tweets_data: List[Dict[str, Any]], 
                         show_columns: List[str] = None,
                         page_size: int = None) -> None:
        """
        Display tweets in an interactive data table
        
        Args:
            tweets_data: List of tweet dictionaries
            show_columns: Columns to display (None for default)
            page_size: Number of rows per page
        """
        if not tweets_data:
            st.info("📭 Aucun tweet à afficher avec les filtres actuels")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(tweets_data)
        
        # Default columns to show
        if show_columns is None:
            show_columns = [
                'author', 'text', 'sentiment', 'category', 
                'priority', 'is_urgent', 'needs_response', 'date'
            ]
        
        # Filter columns that exist in the data
        available_columns = [col for col in show_columns if col in df.columns]
        display_df = df[available_columns].copy()
        
        # Format columns for better display
        display_df = self._format_tweets_dataframe(display_df)
        
        # Display table with pagination
        page_size = page_size or self.default_page_size
        total_rows = len(display_df)
        
        if total_rows > page_size:
            # Pagination controls
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                page_number = st.number_input(
                    f"Page (1-{(total_rows-1)//page_size + 1})",
                    min_value=1,
                    max_value=(total_rows-1)//page_size + 1,
                    value=1,
                    key="tweets_table_page"
                )
            
            # Calculate slice indices
            start_idx = (page_number - 1) * page_size
            end_idx = min(start_idx + page_size, total_rows)
            
            # Display page info
            st.caption(f"Affichage des tweets {start_idx + 1}-{end_idx} sur {total_rows}")
            
            # Display paginated data
            st.dataframe(
                display_df.iloc[start_idx:end_idx],
                use_container_width=True,
                hide_index=True
            )
        else:
            # Display all data
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
        
        # Export button
        if st.button("💾 Exporter en CSV", key="export_tweets"):
            csv_data = self._prepare_csv_export(df)
            st.download_button(
                label="📥 Télécharger CSV",
                data=csv_data,
                file_name=f"tweets_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    def kpi_summary_table(self, kpi_data: Dict[str, Any]) -> None:
        """
        Display KPI summary table
        
        Args:
            kpi_data: KPI metrics dictionary
        """
        if not kpi_data:
            st.warning("Aucune donnée KPI disponible")
            return
        
        # Prepare KPI data for table
        kpi_rows = []
        
        # Basic metrics
        if 'total_tweets' in kpi_data:
            kpi_rows.append({
                'Métrique': 'Total Tweets',
                'Valeur': f"{kpi_data['total_tweets']:,}",
                'Description': 'Nombre total de tweets analysés'
            })
        
        # Sentiment metrics
        if 'sentiment_percentages' in kpi_data:
            sentiment_data = kpi_data['sentiment_percentages']
            for sentiment, percentage in sentiment_data.items():
                emoji = self._get_sentiment_emoji(sentiment)
                kpi_rows.append({
                    'Métrique': f'{emoji} {sentiment.title()}',
                    'Valeur': f"{percentage:.1f}%",
                    'Description': f'Pourcentage de tweets {sentiment}'
                })
        
        # Priority metrics
        if 'critical_count' in kpi_data:
            kpi_rows.append({
                'Métrique': 'Tweets Critiques',
                'Valeur': f"{kpi_data['critical_count']:,}",
                'Description': 'Tweets nécessitant une attention immédiate'
            })
        
        if 'high_priority_count' in kpi_data:
            kpi_rows.append({
                'Métrique': 'Haute Priorité',
                'Valeur': f"{kpi_data['high_priority_count']:,}",
                'Description': 'Tweets de haute priorité'
            })
        
        # Response metrics
        if 'tweets_needing_response' in kpi_data:
            kpi_rows.append({
                'Métrique': 'Réponse Requise',
                'Valeur': f"{kpi_data['tweets_needing_response']:,}",
                'Description': 'Tweets nécessitant une réponse'
            })
        
        if 'avg_estimated_resolution' in kpi_data:
            kpi_rows.append({
                'Métrique': '⏱️ Temps Résolution Moyen',
                'Valeur': f"{kpi_data['avg_estimated_resolution']:.0f} min",
                'Description': 'Temps moyen estimé de résolution'
            })
        
        # Temporal metrics
        if 'peak_hour' in kpi_data:
            kpi_rows.append({
                'Métrique': 'Heure de Pic',
                'Valeur': f"{kpi_data['peak_hour']:02d}h",
                'Description': 'Heure avec le plus d\'activité'
            })
        
        # Create and display DataFrame
        if kpi_rows:
            kpi_df = pd.DataFrame(kpi_rows)
            st.dataframe(
                kpi_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    'Métrique': st.column_config.TextColumn('Métrique', width='medium'),
                    'Valeur': st.column_config.TextColumn('Valeur', width='small'),
                    'Description': st.column_config.TextColumn('Description', width='large')
                }
            )
    
    def category_breakdown_table(self, category_data: Dict[str, int], 
                                sentiment_by_category: Dict[str, Dict[str, int]] = None) -> None:
        """
        Display category breakdown table
        
        Args:
            category_data: Category distribution data
            sentiment_by_category: Sentiment breakdown by category
        """
        if not category_data:
            st.info("Aucune donnée de catégorie disponible")
            return
        
        # Prepare category data
        category_rows = []
        total_tweets = sum(category_data.values())
        
        for category, count in sorted(category_data.items(), key=lambda x: x[1], reverse=True):
            if count == 0:
                continue
                
            row = {
                'Catégorie': self._format_category_display(category),
                'Nombre': f"{count:,}",
                'Pourcentage': f"{(count/total_tweets*100):.1f}%"
            }
            
            # Add sentiment breakdown if available
            if sentiment_by_category and category in sentiment_by_category:
                sentiment_data = sentiment_by_category[category]
                negative_pct = (sentiment_data.get('negative', 0) / count * 100) if count > 0 else 0
                row['% Négatif'] = f"{negative_pct:.1f}%"
            
            category_rows.append(row)
        
        if category_rows:
            category_df = pd.DataFrame(category_rows)
            st.dataframe(
                category_df,
                use_container_width=True,
                hide_index=True
            )
    
    def top_keywords_table(self, keywords_data: List[tuple], limit: int = 20) -> None:
        """
        Display top keywords table
        
        Args:
            keywords_data: List of (keyword, count) tuples
            limit: Maximum number of keywords to show
        """
        if not keywords_data:
            st.info("Aucun mot-clé disponible")
            return
        
        # Prepare keywords data
        keywords_rows = []
        for i, (keyword, count) in enumerate(keywords_data[:limit], 1):
            keywords_rows.append({
                'Rang': i,
                'Mot-clé': keyword,
                'Occurrences': count,
                'Fréquence': f"{(count/sum(c for _, c in keywords_data)*100):.1f}%"
            })
        
        if keywords_rows:
            keywords_df = pd.DataFrame(keywords_rows)
            st.dataframe(
                keywords_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    'Rang': st.column_config.NumberColumn('Rang', width='small'),
                    'Mot-clé': st.column_config.TextColumn('Mot-clé', width='medium'),
                    'Occurrences': st.column_config.NumberColumn('Occurrences', width='small'),
                    'Fréquence': st.column_config.TextColumn('Fréquence', width='small')
                }
            )
    
    def analysis_logs_table(self, logs_data: List[Dict[str, Any]]) -> None:
        """
        Display analysis logs table
        
        Args:
            logs_data: List of analysis log dictionaries
        """
        if not logs_data:
            st.info("Aucun log d'analyse disponible")
            return
        
        # Prepare logs data
        logs_df = pd.DataFrame(logs_data)
        
        # Format columns
        if 'created_at' in logs_df.columns:
            logs_df['created_at'] = pd.to_datetime(logs_df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        if 'total_cost' in logs_df.columns:
            logs_df['total_cost'] = logs_df['total_cost'].apply(lambda x: f"${x:.4f}")
        
        if 'processing_time' in logs_df.columns:
            logs_df['processing_time'] = logs_df['processing_time'].apply(lambda x: f"{x:.1f}s")
        
        # Rename columns for display
        column_mapping = {
            'batch_id': 'ID Batch',
            'total_tweets': 'Total Tweets',
            'successful_analysis': 'Succès',
            'failed_analysis': 'Échecs',
            'llm_provider': 'Fournisseur LLM',
            'total_cost': 'Coût Total',
            'processing_time': 'Temps Traitement',
            'created_at': 'Date Création'
        }
        
        display_df = logs_df.rename(columns=column_mapping)
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
    
    def _format_tweets_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Format tweets DataFrame for display"""
        display_df = df.copy()
        
        # Format text column (truncate long texts)
        if 'text' in display_df.columns:
            display_df['text'] = display_df['text'].apply(
                lambda x: x[:100] + "..." if len(str(x)) > 100 else x
            )
        
        # Format date column
        if 'date' in display_df.columns:
            display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%Y-%m-%d %H:%M')
        
        # Format boolean columns
        bool_columns = ['is_urgent', 'needs_response']
        for col in bool_columns:
            if col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: 'Yes' if x else 'No')
        
        # Format sentiment with emojis
        if 'sentiment' in display_df.columns:
            display_df['sentiment'] = display_df['sentiment'].apply(self._get_sentiment_emoji_text)
        
        # Format category with emojis
        if 'category' in display_df.columns:
            display_df['category'] = display_df['category'].apply(self._format_category_display)
        
        # Format priority with emojis
        if 'priority' in display_df.columns:
            display_df['priority'] = display_df['priority'].apply(self._format_priority_display)
        
        # Rename columns for better display
        column_mapping = {
            'author': 'Auteur',
            'text': 'Texte',
            'sentiment': 'Sentiment',
            'category': 'Catégorie',
            'priority': 'Priorité',
            'is_urgent': 'Urgent',
            'needs_response': 'Réponse Requise',
            'date': 'Date'
        }
        
        display_df = display_df.rename(columns=column_mapping)
        
        return display_df
    
    def _prepare_csv_export(self, df: pd.DataFrame) -> str:
        """Prepare CSV data for export"""
        # Create a copy for export (without formatting)
        export_df = df.copy()
        
        # Convert to CSV
        output = io.StringIO()
        export_df.to_csv(output, index=False, encoding='utf-8')
        return output.getvalue()
    
    def _get_sentiment_emoji(self, sentiment: str) -> str:
        """Get text for sentiment"""
        text_map = {
            'positive': 'POS',
            'neutral': 'NEU',
            'negative': 'NEG',
            'unknown': 'UNK'
        }
        return text_map.get(sentiment, 'UNK')
    
    def _get_sentiment_emoji_text(self, sentiment: str) -> str:
        """Get text for sentiment"""
        text_map = {
            'positive': 'Positif',
            'neutral': 'Neutre',
            'negative': 'Négatif',
            'unknown': 'Inconnu'
        }
        return text_map.get(sentiment, sentiment)
    
    def _format_category_display(self, category: str) -> str:
        """Format category for display"""
        text_map = {
            'facturation': 'Facturation',
            'réseau': 'Réseau',
            'technique': 'Technique',
            'abonnement': 'Abonnement',
            'réclamation': 'Réclamation',
            'compliment': 'Compliment',
            'question': 'Question',
            'autre': 'Autre'
        }
        return text_map.get(category, category.title())
    
    def _format_priority_display(self, priority: str) -> str:
        """Format priority for display"""
        text_map = {
            'critique': 'Critique',
            'haute': 'Haute',
            'moyenne': 'Moyenne',
            'basse': 'Basse'
        }
        return text_map.get(priority, priority.title())
