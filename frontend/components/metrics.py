"""
Metrics Display Component
Professional metrics cards and status indicators
"""

import streamlit as st
from typing import Dict, Any, List, Optional, Union


def render_metric_card(
    title: str,
    value: Union[str, int, float],
    delta: Optional[Union[str, int, float]] = None,
    delta_color: str = "normal",
    help_text: Optional[str] = None,
    icon: Optional[str] = None,
    color: str = "#DC143C"
):
    """Render a professional metric card"""
    
    # Format value
    if isinstance(value, (int, float)):
        if value >= 1000000:
            formatted_value = f"{value/1000000:.1f}M"
        elif value >= 1000:
            formatted_value = f"{value/1000:.1f}K"
        else:
            formatted_value = f"{value:,.0f}" if isinstance(value, int) else f"{value:.1f}"
    else:
        formatted_value = str(value)
    
    # Format delta
    delta_html = ""
    if delta is not None:
        delta_symbol = "▲" if delta > 0 else "▼" if delta < 0 else "●"
        delta_color_code = "#28a745" if delta_color == "normal" and delta > 0 else "#dc3545" if delta_color == "normal" and delta < 0 else "#6c757d"
        if delta_color == "inverse":
            delta_color_code = "#dc3545" if delta > 0 else "#28a745" if delta < 0 else "#6c757d"
        
        delta_html = f"""
        <div style="
            color: {delta_color_code};
            font-size: 0.8rem;
            font-weight: 600;
            margin-top: 0.25rem;
        ">
            {delta_symbol} {delta}
        </div>
        """
    
    # Icon HTML
    icon_html = f'<div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{icon}</div>' if icon else ""
    
    # Help text
    help_html = f'<div style="color: #666; font-size: 0.7rem; margin-top: 0.5rem;">{help_text}</div>' if help_text else ""
    
    card_html = f"""
    <div style="
        background: white;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border-left: 4px solid {color};
        height: 100%;
    ">
        {icon_html}
        <div style="
            color: #666;
            font-size: 0.8rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.5rem;
        ">
            {title}
        </div>
        <div style="
            color: #333;
            font-size: 2rem;
            font-weight: 700;
            line-height: 1;
        ">
            {formatted_value}
        </div>
        {delta_html}
        {help_html}
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)


def render_status_badge(
    status: str,
    text: Optional[str] = None,
    size: str = "normal"
) -> str:
    """Render a status badge"""
    
    status_colors = {
        'success': '#28a745',
        'warning': '#ffc107',
        'error': '#dc3545',
        'info': '#17a2b8',
        'processing': '#007bff',
        'completed': '#28a745',
        'failed': '#dc3545',
        'pending': '#6c757d'
    }
    
    status_icons = {
        'success': '✅',
        'warning': '⚠️',
        'error': '❌',
        'info': 'ℹ️',
        'processing': '🔄',
        'completed': '✅',
        'failed': '❌',
        'pending': '⏳'
    }
    
    color = status_colors.get(status, '#6c757d')
    icon = status_icons.get(status, '●')
    display_text = text or status.title()
    
    font_size = "0.8rem" if size == "small" else "0.9rem"
    padding = "0.25rem 0.5rem" if size == "small" else "0.4rem 0.8rem"
    
    badge_html = f"""
    <span style="
        background: {color};
        color: white;
        padding: {padding};
        border-radius: 15px;
        font-size: {font_size};
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
    ">
        {icon} {display_text}
    </span>
    """
    
    return badge_html


def render_progress_bar(
    current: int,
    total: int,
    label: Optional[str] = None,
    show_percentage: bool = True,
    color: str = "#DC143C"
):
    """Render a professional progress bar"""
    
    if total == 0:
        percentage = 0
    else:
        percentage = min(100, (current / total) * 100)
    
    label_html = f'<div style="margin-bottom: 0.5rem; font-weight: 600; color: #333;">{label}</div>' if label else ""
    
    percentage_html = f'<span style="font-weight: 600; color: {color};">{percentage:.1f}%</span>' if show_percentage else ""
    
    progress_html = f"""
    <div style="margin: 1rem 0;">
        {label_html}
        <div style="
            background: #e9ecef;
            border-radius: 10px;
            height: 8px;
            overflow: hidden;
            margin-bottom: 0.5rem;
        ">
            <div style="
                background: linear-gradient(90deg, {color} 0%, {color}CC 100%);
                height: 100%;
                width: {percentage}%;
                transition: width 0.3s ease;
                border-radius: 10px;
            "></div>
        </div>
        <div style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.8rem;
            color: #666;
        ">
            <span>{current:,} / {total:,}</span>
            {percentage_html}
        </div>
    </div>
    """
    
    st.markdown(progress_html, unsafe_allow_html=True)


def render_kpi_grid(kpis: Dict[str, Any], user_role: str = "manager"):
    """Render a grid of KPI cards based on user role"""
    
    # Define KPIs by role
    role_kpis = {
        'agent_sav': [
            {'key': 'critical_count', 'title': 'Tweets Critiques', 'icon': '🚨', 'color': '#dc3545'},
            {'key': 'negative_percentage', 'title': 'Sentiment Négatif', 'icon': '😞', 'color': '#dc3545'},
            {'key': 'avg_resolution_time', 'title': 'Temps Résolution', 'icon': '⏱️', 'color': '#ffc107'},
            {'key': 'total_tweets', 'title': 'Total Tweets', 'icon': '📊', 'color': '#17a2b8'}
        ],
        'manager': [
            {'key': 'total_tweets', 'title': 'Total Tweets', 'icon': '📊', 'color': '#17a2b8'},
            {'key': 'sentiment_score', 'title': 'Score Sentiment', 'icon': '😊', 'color': '#28a745'},
            {'key': 'engagement_rate', 'title': 'Taux Engagement', 'icon': '👥', 'color': '#007bff'},
            {'key': 'response_rate', 'title': 'Taux Réponse', 'icon': '💬', 'color': '#DC143C'}
        ],
        'analyste': [
            {'key': 'total_tweets', 'title': 'Total Tweets', 'icon': '📊', 'color': '#17a2b8'},
            {'key': 'sentiment_distribution', 'title': 'Distribution Sentiment', 'icon': '📈', 'color': '#28a745'},
            {'key': 'category_breakdown', 'title': 'Répartition Catégories', 'icon': '🏷️', 'color': '#6f42c1'},
            {'key': 'temporal_trends', 'title': 'Tendances Temporelles', 'icon': '📅', 'color': '#fd7e14'}
        ],
        'admin': [
            {'key': 'total_tweets', 'title': 'Total Tweets', 'icon': '📊', 'color': '#17a2b8'},
            {'key': 'processing_time', 'title': 'Temps Traitement', 'icon': '⚡', 'color': '#20c997'},
            {'key': 'api_calls', 'title': 'Appels API', 'icon': '🔌', 'color': '#6c757d'},
            {'key': 'estimated_cost', 'title': 'Coût Estimé', 'icon': '💰', 'color': '#ffc107'}
        ]
    }
    
    selected_kpis = role_kpis.get(user_role, role_kpis['manager'])
    
    # Create columns
    cols = st.columns(len(selected_kpis))
    
    for i, kpi_config in enumerate(selected_kpis):
        with cols[i]:
            key = kpi_config['key']
            value = kpis.get(key, 0)
            
            # Format specific values
            if key == 'sentiment_score':
                value = f"{value:.1f}/5.0"
            elif key == 'engagement_rate' or key == 'response_rate':
                value = f"{value:.1f}%"
            elif key == 'processing_time':
                value = f"{value:.1f}s"
            elif key == 'estimated_cost':
                value = f"${value:.4f}"
            elif key == 'avg_resolution_time':
                value = f"{value:.0f} min"
            
            render_metric_card(
                title=kpi_config['title'],
                value=value,
                icon=kpi_config['icon'],
                color=kpi_config['color']
            )


def render_analysis_summary(
    batch_id: str,
    status: Dict[str, Any],
    start_time: Optional[str] = None
):
    """Render analysis summary with status and progress"""
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #DC143C;
    ">
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"**Analyse ID:** `{batch_id}`")
        if start_time:
            st.markdown(f"**Démarré:** {start_time}")
        
        # Status badge
        status_name = status.get('status', 'unknown')
        status_badge = render_status_badge(status_name)
        st.markdown(status_badge, unsafe_allow_html=True)
    
    with col2:
        total_tweets = status.get('total_tweets', 0)
        analyzed_tweets = status.get('analyzed_tweets', 0)
        
        if total_tweets > 0:
            render_progress_bar(
                current=analyzed_tweets,
                total=total_tweets,
                label="Progression",
                show_percentage=True
            )
    
    with col3:
        failed_tweets = status.get('failed_tweets', 0)
        cost = status.get('estimated_cost', 0)
        
        st.metric("Échecs", failed_tweets)
        st.metric("Coût", f"${cost:.4f}")
    
    st.markdown("</div>", unsafe_allow_html=True)


def render_quick_stats(data: Dict[str, Any]):
    """Render quick statistics in a compact format"""
    
    stats_html = """
    <div style="
        display: flex;
        gap: 2rem;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 8px;
        margin: 1rem 0;
        flex-wrap: wrap;
    ">
    """
    
    for key, value in data.items():
        stats_html += f"""
        <div style="text-align: center;">
            <div style="font-size: 1.5rem; font-weight: 700; color: #DC143C;">{value}</div>
            <div style="font-size: 0.8rem; color: #666; text-transform: uppercase;">{key.replace('_', ' ')}</div>
        </div>
        """
    
    stats_html += "</div>"
    
    st.markdown(stats_html, unsafe_allow_html=True)
