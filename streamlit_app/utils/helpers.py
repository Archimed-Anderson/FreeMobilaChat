"""
Fonctions utilitaires pour l'application
Helpers génériques et fonctions communes
"""

import os
import time
import hashlib
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st

def format_file_size(size_bytes: int) -> str:
    """Formate une taille de fichier en format lisible"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024.0 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def get_file_extension(filename: str) -> str:
    """Extrait l'extension d'un fichier"""
    return os.path.splitext(filename)[1].lower()

def generate_batch_id() -> str:
    """Génère un ID de batch unique"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_suffix = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
    return f"batch_{timestamp}_{random_suffix}"

def format_duration(seconds: float) -> str:
    """Formate une durée en format lisible"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}min"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def format_percentage(value: float, decimals: int = 1) -> str:
    """Formate un pourcentage"""
    return f"{value:.{decimals}f}%"

def format_number(value: Union[int, float], decimals: int = 0) -> str:
    """Formate un nombre avec séparateurs de milliers"""
    if isinstance(value, float):
        return f"{value:,.{decimals}f}"
    else:
        return f"{value:,}"

def get_current_timestamp() -> str:
    """Retourne le timestamp actuel formaté"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_time_ago(timestamp: str) -> str:
    """Calcule le temps écoulé depuis un timestamp"""
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        diff = now - dt
        
        if diff.days > 0:
            return f"il y a {diff.days} jour{'s' if diff.days > 1 else ''}"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"il y a {hours} heure{'s' if hours > 1 else ''}"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"il y a {minutes} minute{'s' if minutes > 1 else ''}"
        else:
            return "à l'instant"
    except:
        return "inconnu"

def truncate_text(text: str, max_length: int = 100) -> str:
    """Tronque un texte à une longueur maximale"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def clean_filename(filename: str) -> str:
    """Nettoie un nom de fichier pour l'utilisation"""
    # Supprimer les caractères non autorisés
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limiter la longueur
    if len(filename) > 100:
        name, ext = os.path.splitext(filename)
        filename = name[:100-len(ext)] + ext
    
    return filename

def get_file_hash(file_content: bytes) -> str:
    """Calcule le hash d'un fichier"""
    return hashlib.md5(file_content).hexdigest()

def is_valid_email(email: str) -> bool:
    """Vérifie si un email est valide"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def safe_get(dictionary: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Récupère une valeur d'un dictionnaire de manière sécurisée"""
    try:
        return dictionary.get(key, default)
    except (AttributeError, TypeError):
        return default

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Divise une liste en chunks de taille donnée"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
    """Aplatit un dictionnaire imbriqué"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def create_progress_bar(progress: float, message: str = "") -> None:
    """Crée une barre de progression avec message"""
    st.progress(progress)
    if message:
        st.caption(message)

def show_loading_spinner(message: str = "Chargement..."):
    """Affiche un spinner de chargement"""
    with st.spinner(message):
        time.sleep(0.1)  # Petite pause pour afficher le spinner

def create_metric_card(title: str, value: str, delta: str = None, 
                      delta_color: str = "normal") -> str:
    """Crée une carte de métrique HTML"""
    
    delta_html = ""
    if delta:
        delta_class = f"delta-{delta_color}"
        delta_html = f'<div class="metric-delta {delta_class}">{delta}</div>'
    
    return f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """

def create_status_badge(status: str, color: str = "blue") -> str:
    """Crée un badge de statut"""
    return f'<span class="status-badge status-{color}">{status}</span>'

def format_currency(amount: float, currency: str = "€") -> str:
    """Formate un montant en devise"""
    return f"{amount:,.2f} {currency}"

def get_file_type_icon(extension: str) -> str:
    """Retourne l'icône pour un type de fichier"""
    icons = {
        '.csv': '',
        '.xlsx': '',
        '.xls': '',
        '.json': '',
        '.parquet': '',
        '.txt': '',
        '.pdf': ''
    }
    return icons.get(extension.lower(), '')

def create_tooltip(text: str, tooltip: str) -> str:
    """Crée un élément avec tooltip"""
    return f'<span title="{tooltip}">{text}</span>'

def validate_session_state() -> bool:
    """Valide l'état de la session"""
    required_keys = ['user_role']
    return all(key in st.session_state for key in required_keys)

def clear_session_data():
    """Nettoie les données de session"""
    keys_to_clear = [
        'uploaded_data', 'uploaded_filename', 'current_batch_id',
        'analysis_status', 'kpi_data', 'tweets_data', 'file_info'
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

def get_user_agent() -> str:
    """Retourne un User-Agent pour les requêtes HTTP"""
    return "FreeMobilaChat/2.0.0 (Streamlit App)"

def create_download_link(data: bytes, filename: str, mime_type: str) -> str:
    """Crée un lien de téléchargement"""
    import base64
    b64 = base64.b64encode(data).decode()
    return f'<a href="data:{mime_type};base64,{b64}" download="{filename}">Télécharger {filename}</a>'

def format_relative_time(timestamp: str) -> str:
    """Formate un timestamp en temps relatif"""
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        diff = now - dt
        
        if diff.days > 7:
            return dt.strftime("%d/%m/%Y")
        elif diff.days > 0:
            return f"il y a {diff.days}j"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"il y a {hours}h"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"il y a {minutes}min"
        else:
            return "maintenant"
    except:
        return "inconnu"

def create_emoji_icon(icon_name: str) -> str:
    """Retourne un emoji pour un nom d'icône"""
    icons = {
        'upload': '',
        'analysis': '',
        'dashboard': '',
        'settings': '',
        'success': '',
        'error': '',
        'warning': '',
        'info': 'ℹ',
        'loading': '',
        'download': '',
        'export': '',
        'chart': '',
        'table': '',
        'filter': '',
        'refresh': '',
        'delete': '',
        'edit': '',
        'save': '',
        'cancel': '',
        'confirm': ''
    }
    return icons.get(icon_name, '')
