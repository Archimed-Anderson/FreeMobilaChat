"""
Export Service - Service d'export des résultats et rapports
Module pour l'export des données et KPI en différents formats (CSV, PDF, Excel)

Fonctionnalités:
- Export CSV avec métriques détaillées
- Export PDF avec graphiques et visualisations
- Export Excel multi-feuilles
- Génération de rapports formatés

Author: FreeMobilaChat Team
Date: 2025
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import io
import json
import logging
from pathlib import Path

# Import conditionnel pour matplotlib et PDF
try:
    import matplotlib
    matplotlib.use('Agg')  # Backend non-interactif
    import matplotlib.pyplot as plt
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logging.warning("Matplotlib not available - PDF export with charts will be limited")

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logging.warning("ReportLab not available - PDF export will be limited")

logger = logging.getLogger(__name__)


class ExportService:
    """Service d'export des données et rapports"""
    
    def __init__(self):
        """Initialise le service d'export"""
        self.export_history = []
        
    def export_to_csv(self, df: pd.DataFrame, metrics: Dict[str, Any], 
                      filename: Optional[str] = None) -> bytes:
        """
        Exporte les données et métriques en CSV
        
        Args:
            df: DataFrame source
            metrics: Dictionnaire de métriques
            filename: Nom du fichier (optionnel)
            
        Returns:
            Contenu CSV en bytes
        """
        try:
            output = io.StringIO()
            
            # En-tête du rapport
            output.write("# FreeMobilaChat - Rapport d'Analyse\n")
            output.write(f"# Date de génération: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            output.write("#\n")
            
            # Métriques principales
            if 'core_metrics' in metrics:
                output.write("# MÉTRIQUES PRINCIPALES\n")
                core = metrics['core_metrics']
                output.write(f"# Total tweets: {core.get('total_tweets', 0)}\n")
                output.write(f"# Score de confiance: {core.get('confidence_score', 0)}\n")
                output.write("#\n")
            
            # Métriques d'engagement
            if 'engagement_metrics' in metrics:
                engagement = metrics['engagement_metrics']
                output.write("# ENGAGEMENT\n")
                output.write(f"# Score global: {engagement.get('global_score', 0)}\n")
                output.write(f"# Rating: {engagement.get('rating', 'N/A')}\n")
                output.write("#\n")
            
            # Alertes
            if 'alerts' in metrics and metrics['alerts']:
                output.write("# ALERTES\n")
                for alert in metrics['alerts']:
                    output.write(f"# [{alert.get('level', 'info').upper()}] {alert.get('title', '')}\n")
                output.write("#\n")
            
            output.write("#\n# DONNÉES DÉTAILLÉES\n#\n")
            
            # Données du DataFrame
            df.to_csv(output, index=False)
            
            # Métriques détaillées en fin de fichier
            output.write("\n\n# MÉTRIQUES DÉTAILLÉES (JSON)\n")
            output.write("# " + json.dumps(metrics, indent=2, default=str).replace('\n', '\n# '))
            
            content = output.getvalue()
            output.close()
            
            return content.encode('utf-8')
            
        except Exception as e:
            logger.error(f"Erreur lors de l'export CSV: {str(e)}", exc_info=True)
            raise
    
    def export_to_excel(self, df: pd.DataFrame, metrics: Dict[str, Any],
                        filename: Optional[str] = None) -> bytes:
        """
        Exporte les données en Excel multi-feuilles
        
        Args:
            df: DataFrame source
            metrics: Dictionnaire de métriques
            filename: Nom du fichier (optionnel)
            
        Returns:
            Contenu Excel en bytes
        """
        try:
            output = io.BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Feuille 1: Données principales
                df.to_excel(writer, sheet_name='Données', index=False)
                
                # Feuille 2: Métriques principales
                if 'core_metrics' in metrics:
                    core_metrics_df = self._metrics_to_dataframe(metrics['core_metrics'])
                    core_metrics_df.to_excel(writer, sheet_name='Métriques Principales', index=False)
                
                # Feuille 3: Métriques temporelles
                if 'temporal_metrics' in metrics:
                    temporal_df = self._temporal_metrics_to_dataframe(metrics['temporal_metrics'])
                    temporal_df.to_excel(writer, sheet_name='Analyse Temporelle', index=False)
                
                # Feuille 4: Engagement
                if 'engagement_metrics' in metrics:
                    engagement_df = self._metrics_to_dataframe(metrics['engagement_metrics'])
                    engagement_df.to_excel(writer, sheet_name='Engagement', index=False)
                
                # Feuille 5: Alertes
                if 'alerts' in metrics and metrics['alerts']:
                    alerts_df = pd.DataFrame(metrics['alerts'])
                    alerts_df.to_excel(writer, sheet_name='Alertes', index=False)
                
                # Feuille 6: Résumé
                summary_data = self._create_summary(df, metrics)
                summary_df = pd.DataFrame(list(summary_data.items()), columns=['Métrique', 'Valeur'])
                summary_df.to_excel(writer, sheet_name='Résumé', index=False)
            
            output.seek(0)
            return output.read()
            
        except Exception as e:
            logger.error(f"Erreur lors de l'export Excel: {str(e)}", exc_info=True)
            raise
    
    def export_to_pdf(self, df: pd.DataFrame, metrics: Dict[str, Any],
                      figures: Optional[List[Any]] = None,
                      filename: Optional[str] = None) -> bytes:
        """
        Exporte un rapport PDF complet avec graphiques
        
        Args:
            df: DataFrame source
            metrics: Dictionnaire de métriques
            figures: Liste de figures matplotlib/plotly (optionnel)
            filename: Nom du fichier (optionnel)
            
        Returns:
            Contenu PDF en bytes
        """
        if not REPORTLAB_AVAILABLE:
            logger.error("ReportLab n'est pas disponible")
            raise ImportError("ReportLab est requis pour l'export PDF")
        
        try:
            output = io.BytesIO()
            
            # Créer le document PDF
            doc = SimpleDocTemplate(
                output,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#CC0000'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#CC0000'),
                spaceAfter=12,
                spaceBefore=12
            )
            
            # Contenu du document
            story = []
            
            # Page de titre
            story.append(Paragraph("FreeMobilaChat", title_style))
            story.append(Paragraph("Rapport d'Analyse des Tweets", styles['Heading2']))
            story.append(Spacer(1, 12))
            story.append(Paragraph(
                f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                styles['Normal']
            ))
            story.append(Spacer(1, 20))
            
            # Résumé exécutif
            story.append(Paragraph("Résumé Exécutif", heading_style))
            summary = self._create_summary(df, metrics)
            summary_data = [[k, str(v)] for k, v in summary.items()]
            summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 20))
            
            # Métriques principales
            if 'core_metrics' in metrics:
                story.append(PageBreak())
                story.append(Paragraph("Métriques Principales", heading_style))
                
                core = metrics['core_metrics']
                core_data = [
                    ['Total de tweets', str(core.get('total_tweets', 0))],
                    ['Score de confiance', f"{core.get('confidence_score', 0):.2f}"],
                ]
                
                # Distribution des sentiments
                if 'sentiment_distribution' in core and 'percentages' in core['sentiment_distribution']:
                    story.append(Paragraph("Distribution des Sentiments", styles['Heading3']))
                    sent_dist = core['sentiment_distribution']['percentages']
                    sent_data = [[k.capitalize(), f"{v:.1f}%"] for k, v in sent_dist.items()]
                    sent_table = Table(sent_data, colWidths=[3*inch, 2*inch])
                    sent_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
                        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    story.append(sent_table)
                    story.append(Spacer(1, 12))
            
            # Engagement
            if 'engagement_metrics' in metrics:
                story.append(PageBreak())
                story.append(Paragraph("Métriques d'Engagement", heading_style))
                
                engagement = metrics['engagement_metrics']
                eng_data = [
                    ['Score Global', f"{engagement.get('global_score', 0):.1f}/100"],
                    ['Rating', engagement.get('rating', 'N/A')]
                ]
                
                if 'components' in engagement:
                    for comp_name, comp_value in engagement['components'].items():
                        eng_data.append([comp_name.replace('_', ' ').title(), f"{comp_value:.1f}"])
                
                eng_table = Table(eng_data, colWidths=[3*inch, 2*inch])
                eng_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#CC0000')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(eng_table)
                story.append(Spacer(1, 12))
            
            # Alertes
            if 'alerts' in metrics and metrics['alerts']:
                story.append(PageBreak())
                story.append(Paragraph("Alertes et Recommandations", heading_style))
                
                for alert in metrics['alerts']:
                    level = alert.get('level', 'info').upper()
                    title = alert.get('title', '')
                    message = alert.get('message', '')
                    recommendation = alert.get('recommendation', '')
                    
                    alert_text = f"<b>[{level}] {title}</b><br/>{message}<br/><i>Recommandation: {recommendation}</i>"
                    story.append(Paragraph(alert_text, styles['Normal']))
                    story.append(Spacer(1, 12))
            
            # Graphiques (si disponibles)
            if figures and MATPLOTLIB_AVAILABLE:
                story.append(PageBreak())
                story.append(Paragraph("Visualisations", heading_style))
                
                for i, fig in enumerate(figures[:5]):  # Limiter à 5 figures
                    try:
                        # Sauvegarder la figure en bytes
                        img_buffer = io.BytesIO()
                        fig.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
                        img_buffer.seek(0)
                        
                        # Ajouter au PDF
                        img = Image(img_buffer, width=5*inch, height=3*inch)
                        story.append(img)
                        story.append(Spacer(1, 12))
                        
                        plt.close(fig)
                    except Exception as e:
                        logger.warning(f"Impossible d'ajouter la figure {i}: {e}")
            
            # Données détaillées (échantillon)
            story.append(PageBreak())
            story.append(Paragraph("Échantillon de Données", heading_style))
            story.append(Paragraph(
                "Les 10 premières lignes du dataset:",
                styles['Normal']
            ))
            story.append(Spacer(1, 12))
            
            # Préparer les données pour le tableau
            df_sample = df.head(10)
            # Limiter aux 5 premières colonnes pour la lisibilité
            df_sample = df_sample.iloc[:, :min(5, len(df.columns))]
            
            # Convertir en liste pour le tableau
            data_table_content = [df_sample.columns.tolist()]
            for _, row in df_sample.iterrows():
                data_table_content.append([str(val)[:30] for val in row.values])
            
            data_table = Table(data_table_content)
            data_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(data_table)
            
            # Footer
            story.append(Spacer(1, 30))
            story.append(Paragraph(
                "Rapport généré par FreeMobilaChat - Plateforme d'Analyse IA",
                styles['Normal']
            ))
            
            # Construire le PDF
            doc.build(story)
            
            output.seek(0)
            return output.read()
            
        except Exception as e:
            logger.error(f"Erreur lors de l'export PDF: {str(e)}", exc_info=True)
            raise
    
    def create_downloadable_report(self, df: pd.DataFrame, metrics: Dict[str, Any],
                                   format: str = 'csv') -> Tuple[bytes, str, str]:
        """
        Crée un rapport téléchargeable
        
        Args:
            df: DataFrame source
            metrics: Dictionnaire de métriques
            format: Format d'export ('csv', 'excel', 'pdf')
            
        Returns:
            Tuple (contenu, nom_fichier, mime_type)
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format.lower() == 'csv':
            content = self.export_to_csv(df, metrics)
            filename = f"rapport_freemobilachat_{timestamp}.csv"
            mime_type = "text/csv"
            
        elif format.lower() in ['excel', 'xlsx']:
            content = self.export_to_excel(df, metrics)
            filename = f"rapport_freemobilachat_{timestamp}.xlsx"
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            
        elif format.lower() == 'pdf':
            content = self.export_to_pdf(df, metrics)
            filename = f"rapport_freemobilachat_{timestamp}.pdf"
            mime_type = "application/pdf"
            
        else:
            raise ValueError(f"Format non supporté: {format}")
        
        # Enregistrer dans l'historique
        self.export_history.append({
            'timestamp': datetime.now().isoformat(),
            'format': format,
            'filename': filename,
            'size_bytes': len(content)
        })
        
        return content, filename, mime_type
    
    # === Fonctions utilitaires ===
    
    def _metrics_to_dataframe(self, metrics_dict: Dict[str, Any]) -> pd.DataFrame:
        """Convertit un dictionnaire de métriques en DataFrame"""
        rows = []
        for key, value in metrics_dict.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    rows.append({'Métrique': f"{key}.{sub_key}", 'Valeur': sub_value})
            else:
                rows.append({'Métrique': key, 'Valeur': value})
        
        return pd.DataFrame(rows)
    
    def _temporal_metrics_to_dataframe(self, temporal_dict: Dict[str, Any]) -> pd.DataFrame:
        """Convertit les métriques temporelles en DataFrame"""
        rows = []
        
        # Volume horaire
        if 'hourly_volume' in temporal_dict and 'distribution' in temporal_dict['hourly_volume']:
            for hour, count in temporal_dict['hourly_volume']['distribution'].items():
                rows.append({
                    'Type': 'Volume Horaire',
                    'Période': f"{hour}h",
                    'Valeur': count
                })
        
        # Volume journalier
        if 'daily_volume' in temporal_dict and 'distribution' in temporal_dict['daily_volume']:
            for date, count in temporal_dict['daily_volume']['distribution'].items():
                rows.append({
                    'Type': 'Volume Journalier',
                    'Période': date,
                    'Valeur': count
                })
        
        # Pattern hebdomadaire
        if 'weekly_pattern' in temporal_dict:
            for day, count in temporal_dict['weekly_pattern'].items():
                rows.append({
                    'Type': 'Pattern Hebdomadaire',
                    'Période': day,
                    'Valeur': count
                })
        
        return pd.DataFrame(rows) if rows else pd.DataFrame()
    
    def _create_summary(self, df: pd.DataFrame, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un résumé des données et métriques"""
        summary = {
            'Date de génération': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Nombre de tweets': len(df),
            'Nombre de colonnes': len(df.columns),
        }
        
        if 'data_info' in metrics and 'date_range' in metrics['data_info']:
            date_range = metrics['data_info']['date_range']
            if date_range:
                summary['Période d\'analyse'] = f"{date_range.get('start', 'N/A')} - {date_range.get('end', 'N/A')}"
                summary['Durée (jours)'] = date_range.get('duration_days', 'N/A')
        
        if 'engagement_metrics' in metrics:
            engagement = metrics['engagement_metrics']
            summary['Score d\'engagement'] = f"{engagement.get('global_score', 0):.1f}/100"
            summary['Rating'] = engagement.get('rating', 'N/A')
        
        if 'quality_metrics' in metrics:
            quality = metrics['quality_metrics']
            summary['Score de qualité'] = f"{quality.get('quality_score', 0):.1f}/100"
        
        if 'alerts' in metrics:
            summary['Nombre d\'alertes'] = len(metrics['alerts'])
        
        return summary


# Instance globale
_export_service_instance = None

def get_export_service() -> ExportService:
    """Retourne l'instance singleton du service d'export"""
    global _export_service_instance
    if _export_service_instance is None:
        _export_service_instance = ExportService()
    return _export_service_instance


