"""
Composant de selection de roles pour le header du dashboard
Gere l'affichage du dropdown de roles et le filtrage du contenu
"""

import streamlit as st
from typing import Dict, Any, List, Optional


# ==============================================================================
# CONFIGURATION DES ROLES
# ==============================================================================

# Definition des roles disponibles dans l'application
# Chaque role a un niveau d'acces different et voit des dashboards specifiques
AVAILABLE_ROLES = {
    "Agent SAV": {
        "level": 1,
        "icon": "fa-headset",
        "color": "#3182ce",
        "description": "Agent du Service Apres-Vente",
        "permissions": ["view_tickets", "view_basic_stats", "reply_customers"],
        "dashboard_access": ["reclamations", "urgents", "sentiments", "basic_kpis"]
    },
    "Data Analyst": {
        "level": 2,
        "icon": "fa-chart-bar",
        "color": "#805ad5",
        "description": "Analyste de Donnees",
        "permissions": ["view_tickets", "view_all_stats", "export_data", "create_reports"],
        "dashboard_access": ["all_kpis", "visualizations", "trends", "analytics"]
    },
    "Manager": {
        "level": 3,
        "icon": "fa-users",
        "color": "#d69e2e",
        "description": "Manager d'Equipe",
        "permissions": ["view_tickets", "view_all_stats", "export_data", "manage_team", "view_performance"],
        "dashboard_access": ["all_kpis", "team_performance", "trends", "sla_metrics"]
    },
    "Director (admin)": {
        "level": 4,
        "icon": "fa-crown",
        "color": "#CC0000",
        "description": "Directeur (Administrateur)",
        "permissions": ["all", "view_tickets", "view_all_stats", "export_data", "manage_team", "view_performance", "create_reports"],
        "dashboard_access": ["all"]
    }
}

# Mapping des roles depuis le systeme d'authentification vers les roles du selecteur
# Le systeme d'authentification utilise des identifiants comme 'agent_sav'
# tandis que le selecteur utilise des noms affichables comme "Agent SAV"
ROLE_MAPPING = {
    "agent_sav": "Agent SAV",
    "data_analyst": "Data Analyst",
    "manager": "Manager",
    "admin": "Director (admin)",
    "director": "Director (admin)"
}

# Ordre d'affichage dans le dropdown
ROLE_ORDER = ["Agent SAV", "Data Analyst", "Manager", "Director (admin)"]


# ==============================================================================
# FONCTIONS DE GESTION DES ROLES
# ==============================================================================

def initialize_role_system():
    """
    Initialise le systeme de roles dans la session Streamlit
    
    Cette fonction doit etre appelee au debut de chaque page pour initialiser
    le role par defaut si ce n'est pas deja fait.
    
    Si aucun role n'est defini, le role par defaut "Agent SAV" est selectionne.
    """
    # Initialiser le role par defaut si non present dans session_state
    if 'current_role' not in st.session_state:
        st.session_state.current_role = "Agent SAV"  # Role par defaut
    
    # Initialiser l'historique des changements de roles
    if 'role_history' not in st.session_state:
        st.session_state.role_history = []


def get_current_role() -> str:
    """
    Retourne le role actuellement selectionne
    
    Returns:
        str: Nom du role actuel (ex: "Agent SAV", "Manager", etc.)
    """
    # S'assurer que le systeme est initialise
    initialize_role_system()
    
    # Retourner le role stocke dans session_state
    current_role = st.session_state.current_role
    
    # Si le role vient du systeme d'authentification, le convertir
    if current_role in ROLE_MAPPING:
        return ROLE_MAPPING[current_role]
    
    return current_role


def set_current_role(role: str):
    """
    Definit le role actuel et enregistre le changement
    
    Args:
        role: Nom du role a definir (doit exister dans AVAILABLE_ROLES)
    
    Raises:
        ValueError: Si le role n'existe pas
    """
    # Verification que le role existe
    # Convertir le role si necessaire
    display_role = role
    if role in ROLE_MAPPING:
        display_role = ROLE_MAPPING[role]
    
    if display_role not in AVAILABLE_ROLES:
        raise ValueError(f"Role invalide: {display_role}")
    
    # Enregistrer l'ancien role dans l'historique
    if 'current_role' in st.session_state:
        old_role = st.session_state.current_role
        st.session_state.role_history.append({
            'from': old_role,
            'to': role,  # Stocker le role d'origine, pas le converti
            'timestamp': st.session_state.get('_timestamp', '')
        })
    
    # Definir le nouveau role (stocker le role d'origine)
    st.session_state.current_role = role


def get_role_permissions(role: Optional[str] = None) -> List[str]:
    """
    Retourne les permissions du role specifie
    
    Args:
        role: Nom du role (optionnel, utilise le role actuel si non specifie)
        
    Returns:
        List[str]: Liste des permissions du role
    """
    # Utiliser le role actuel si non specifie
    if role is None:
        role = get_current_role()
    
    # Convertir le role si necessaire
    display_role = role
    if role in ROLE_MAPPING:
        display_role = ROLE_MAPPING[role]
    
    # Retourner les permissions du role
    if display_role in AVAILABLE_ROLES:
        return AVAILABLE_ROLES[display_role]['permissions']
    
    # Retourner permissions vides si role invalide
    return []


def has_permission(permission: str, role: Optional[str] = None) -> bool:
    """
    Verifie si un role a une permission specifique
    
    Args:
        permission: Permission a verifier (ex: "export_data")
        role: Nom du role (optionnel, utilise le role actuel si non specifie)
        
    Returns:
        bool: True si le role a la permission, False sinon
    """
    # Obtenir les permissions du role
    permissions = get_role_permissions(role)
    
    # Verifier si "all" est dans les permissions (admin total)
    if "all" in permissions:
        return True
    
    # Verifier si la permission specifique est presente
    return permission in permissions


def can_access_dashboard(dashboard_name: str, role: Optional[str] = None) -> bool:
    """
    Verifie si un role peut acceder a un dashboard specifique
    
    Args:
        dashboard_name: Nom du dashboard (ex: "all_kpis", "reclamations")
        role: Nom du role (optionnel, utilise le role actuel si non specifie)
        
    Returns:
        bool: True si le role peut acceder au dashboard, False sinon
    """
    # Utiliser le role actuel si non specifie
    if role is None:
        role = get_current_role()
    
    # Convertir le role si necessaire
    display_role = role
    if role in ROLE_MAPPING:
        display_role = ROLE_MAPPING[role]
    
    # Obtenir la configuration du role
    if display_role not in AVAILABLE_ROLES:
        return False
    
    role_config = AVAILABLE_ROLES[display_role]
    dashboard_access = role_config['dashboard_access']
    
    # Verifier si acces total ("all")
    if "all" in dashboard_access:
        return True
    
    # Verifier si le dashboard specifique est accessible
    return dashboard_name in dashboard_access


# ==============================================================================
# COMPOSANT UI: ROLE SELECTOR
# ==============================================================================

def render_role_selector():
    """
    Affiche le selecteur de roles dans le header
    
    Ce composant cree un dropdown elegant dans le style Free Mobile permettant
    de selectionner le role de l'utilisateur. Le changement de role declenche
    un rerun de la page pour appliquer les filtres correspondants.
    
    Le dropdown est style avec:
    - Couleurs Free Mobile (rouge #CC0000)
    - Icones Font Awesome pour chaque role
    - Indicateur visuel du role actuel
    - Animation smooth au hover
    
    Returns:
        str: Role selectionne
    """
    # Initialiser le systeme de roles
    initialize_role_system()
    
    # Obtenir le role actuel
    current_role = get_current_role()
    
    # CSS pour le selecteur de roles (style moderne Free Mobile)
    st.markdown("""
    <style>
    /* Conteneur du selecteur de roles */
    .role-selector-container {
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 9999;
        background: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        padding: 0.5rem;
    }
    
    /* Bouton principal */
    .role-selector-button {
        background: #2d3748;
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.95rem;
        cursor: pointer;
        border: none;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        transition: all 0.2s ease;
    }
    
    .role-selector-button:hover {
        background: #1a202c;
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Badge du role */
    .role-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.9rem;
        background: #f7fafc;
        border: 2px solid #e2e8f0;
        color: #2d3748;
    }
    
    .role-badge i {
        font-size: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Affichage du selecteur de roles dans la sidebar (meilleure UX pour Streamlit)
    with st.sidebar:
        # Separateur visuel
        st.markdown("---")
        
        # Titre de la section
        st.markdown("""
        <div style="text-align: center; margin: 1rem 0 0.5rem 0;">
            <h3 style="font-size: 1.2rem; font-weight: 700; color: #2d3748; margin: 0;">
                <i class="fas fa-user-circle" style="color: #CC0000; margin-right: 0.5rem;"></i>
                Selection du Role
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Affichage du role actuel avec icone
        # Convertir le role si necessaire pour l'affichage
        display_role = current_role
        if current_role in ROLE_MAPPING:
            display_role = ROLE_MAPPING[current_role]
        
        # Verifier que le role existe dans AVAILABLE_ROLES
        if display_role in AVAILABLE_ROLES:
            role_config = AVAILABLE_ROLES[display_role]
        else:
            # Fallback sur le role par defaut
            display_role = "Agent SAV"
            role_config = AVAILABLE_ROLES[display_role]
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {role_config['color']} 0%, {role_config['color']}dd 100%);
                    padding: 1rem; border-radius: 8px; text-align: center; margin-bottom: 1rem;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
            <i class="fas {role_config['icon']}" style="font-size: 2rem; color: white;"></i>
            <div style="color: white; font-size: 1.1rem; font-weight: 700; margin-top: 0.5rem;">
                {display_role}
            </div>
            <div style="color: rgba(255,255,255,0.9); font-size: 0.85rem; margin-top: 0.25rem;">
                {role_config['description']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Dropdown de selection de role
        selected_role = st.selectbox(
            "Changer de role:",
            options=ROLE_ORDER,
            index=ROLE_ORDER.index(display_role) if display_role in ROLE_ORDER else 0,
            key="role_selector_dropdown",
            help="Selectionnez votre role pour voir le dashboard adapte"
        )
        
        # Si le role change, mettre a jour et rerun
        if selected_role != display_role:
            # Convertir le role affiche vers le role d'origine si necessaire
            original_role = selected_role
            for orig, disp in ROLE_MAPPING.items():
                if disp == selected_role:
                    original_role = orig
                    break
            
            set_current_role(original_role)
            st.rerun()
        
        # Affichage des permissions du role actuel
        with st.expander("Permissions du role", expanded=False):
            permissions = get_role_permissions(current_role)
            
            if "all" in permissions:
                st.success("Acces total (Administrateur)")
            else:
                for perm in permissions:
                    # Formater le nom de la permission
                    perm_display = perm.replace('_', ' ').title()
                    st.markdown(f"- {perm_display}")
    
    # Retourner le role actuel (converti si necessaire)
    return current_role


def render_role_specific_header(role: str, page_title: str):
    """
    Affiche un header personnalise selon le role
    
    Le header change de couleur et d'icone selon le role pour une identification
    visuelle immediate du contexte utilisateur.
    
    Args:
        role: Role actuel de l'utilisateur
        page_title: Titre de la page a afficher
    """
    # Convertir le role si necessaire
    display_role = role
    if role in ROLE_MAPPING:
        display_role = ROLE_MAPPING[role]
    
    # Configuration visuelle selon le role
    role_config = AVAILABLE_ROLES.get(display_role, AVAILABLE_ROLES["Agent SAV"])
    
    # Header personnalise par role
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {role_config['color']} 0%, {role_config['color']}dd 100%); 
                padding: 2rem; border-radius: 12px; margin-bottom: 2rem; text-align: center;
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);">
        <div style="display: flex; align-items: center; justify-content: center; gap: 1rem; margin-bottom: 1rem;">
            <div style="background: white; padding: 1rem; border-radius: 50%; 
                        box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
                <i class="fas {role_config['icon']}" style="font-size: 2rem; color: {role_config['color']};"></i>
            </div>
            <div style="text-align: left;">
                <div style="color: white; font-size: 1.8rem; font-weight: 800; letter-spacing: -0.5px;">
                    {page_title}
                </div>
                <div style="color: rgba(255,255,255,0.9); font-size: 1rem; margin-top: 0.25rem;">
                    Vue: {role}
                </div>
            </div>
        </div>
        <div style="color: rgba(255,255,255,0.85); font-size: 0.9rem; padding-top: 1rem; 
                    border-top: 1px solid rgba(255,255,255,0.2);">
            {role_config['description']}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# FONCTIONS DE FILTRAGE PAR ROLE
# ==============================================================================

def filter_kpis_by_role(kpis: Dict[str, Any], role: str) -> Dict[str, Any]:
    """
    Filtre les KPIs selon le role de l'utilisateur
    
    Differents roles ont acces a differents niveaux de detail:
    - Agent SAV: KPIs basiques (reclamations, urgence)
    - Data Analyst: Tous les KPIs avec details
    - Manager: KPIs + metriques de performance equipe
    - Director: Acces complet a tout
    
    Args:
        kpis: Dictionnaire complet des KPIs calcules
        role: Role de l'utilisateur
        
    Returns:
        Dict[str, Any]: KPIs filtres selon le role
    """
    # Convertir le role si necessaire
    display_role = role
    if role in ROLE_MAPPING:
        display_role = ROLE_MAPPING[role]
    
    # Director a acces a tout
    if display_role == "Director (admin)":
        return kpis
    
    # Data Analyst et Manager ont acces a tous les KPIs
    if display_role in ["Data Analyst", "Manager"]:
        return kpis
    
    # Agent SAV: acces limite aux KPIs essentiels
    if display_role == "Agent SAV":
        # Filtrer pour ne garder que les KPIs pertinents pour un agent
        filtered_kpis = {}
        
        # Garder claim_rate (important pour traiter les reclamations)
        if 'claim_rate' in kpis:
            filtered_kpis['claim_rate'] = kpis['claim_rate']
        
        # Garder urgency_rate (important pour prioriser les taches)
        if 'urgency_rate' in kpis:
            filtered_kpis['urgency_rate'] = kpis['urgency_rate']
        
        # Garder satisfaction_index (feedback sur le service)
        if 'satisfaction_index' in kpis:
            filtered_kpis['satisfaction_index'] = kpis['satisfaction_index']
        
        # Masquer confidence_score (metrique technique)
        # Masquer thematic_distribution (vue management)
        
        return filtered_kpis
    
    # Par defaut, retourner tous les KPIs
    return kpis


def filter_dataframe_by_role(df, role: str):
    """
    Filtre le DataFrame selon le role (si necessaire)
    
    Certains roles peuvent avoir acces a un sous-ensemble des donnees seulement.
    Par exemple, un Agent SAV pourrait ne voir que les tweets non traites.
    
    Args:
        df: DataFrame complet
        role: Role de l'utilisateur
        
    Returns:
        DataFrame filtre selon le role
    """
    # Convertir le role si necessaire
    display_role = role
    if role in ROLE_MAPPING:
        display_role = ROLE_MAPPING[role]
    
    # Pour l'instant, tous les roles voient toutes les donnees
    # Cette fonction peut etre etendue pour filtrer selon le role
    
    # Director et Manager: acces complet
    if display_role in ["Director (admin)", "Manager", "Data Analyst"]:
        return df
    
    # Agent SAV: pourrait voir uniquement les tweets urgents ou non traites
    # (a implementer selon la logique business)
    if display_role == "Agent SAV":
        # Exemple de filtre (commente pour ne pas casser le workflow actuel):
        # if 'is_urgent' in df.columns:
        #     return df[df['is_urgent'] == True]
        # if 'status' in df.columns:
        #     return df[df['status'].isin(['nouveau', 'en_attente'])]
        
        # Pour l'instant, retourner tout
        return df
    
    # Par defaut, retourner le DataFrame complet
    return df


def get_dashboard_message_by_role(role: str) -> str:
    """
    Retourne un message personnalise selon le role
    
    Args:
        role: Role de l'utilisateur
        
    Returns:
        str: Message HTML personnalise
    """
    # Convertir le role si necessaire
    display_role = role
    if role in ROLE_MAPPING:
        display_role = ROLE_MAPPING[role]
    
    # Messages personnalises par role
    messages = {
        "Agent SAV": """
            <div style="background: #e6f7ff; border-left: 4px solid #3182ce; padding: 1rem; 
                        border-radius: 4px; margin: 1rem 0;">
                <strong>Vue Agent SAV</strong><br>
                Vous visualisez les metriques essentielles pour le traitement des tickets:
                reclamations, urgence et satisfaction client.
            </div>
        """,
        "Data Analyst": """
            <div style="background: #f3e8ff; border-left: 4px solid #805ad5; padding: 1rem; 
                        border-radius: 4px; margin: 1rem 0;">
                <strong>Vue Data Analyst</strong><br>
                Acces complet aux KPIs et visualisations pour analyses approfondies
                et creation de rapports detailles.
            </div>
        """,
        "Manager": """
            <div style="background: #fffbeb; border-left: 4px solid #d69e2e; padding: 1rem; 
                        border-radius: 4px; margin: 1rem 0;">
                <strong>Vue Manager</strong><br>
                Dashboard de pilotage avec KPIs de performance d'equipe et metriques SLA
                pour suivi operationnel.
            </div>
        """,
        "Director (admin)": """
            <div style="background: #fee; border-left: 4px solid #CC0000; padding: 1rem; 
                        border-radius: 4px; margin: 1rem 0;">
                <strong>Vue Directeur (Administrateur)</strong><br>
                Acces total a tous les KPIs, visualisations et donnees. Vue strategique
                et operationnelle complete.
            </div>
        """
    }
    
    # Retourner le message du role ou un message par defaut
    return messages.get(display_role, "")


# ==============================================================================
# FONCTIONS D'AFFICHAGE CONDITIONNEL
# ==============================================================================

def show_if_has_permission(permission: str, content_func, role: Optional[str] = None):
    """
    Affiche du contenu seulement si le role a la permission
    
    Utile pour cacher certaines sections du dashboard selon le role.
    
    Args:
        permission: Permission requise
        content_func: Fonction a executer pour afficher le contenu
        role: Role a verifier (optionnel, utilise le role actuel)
    
    Example:
        show_if_has_permission(
            "export_data",
            lambda: st.download_button("Export CSV", data)
        )
    """
    # Verifier la permission
    if has_permission(permission, role):
        # Executer la fonction de contenu
        content_func()
    else:
        # Afficher un message d'acces refuse (optionnel)
        # st.warning(f"Permission '{permission}' requise pour acceder a cette section")
        pass


def get_kpi_labels_by_role(role: str) -> Dict[str, str]:
    """
    Retourne des labels de KPIs personnalises selon le role
    
    Args:
        role: Role de l'utilisateur
        
    Returns:
        Dict: Mapping des KPIs vers leurs labels personnalises
    """
    # Convertir le role si necessaire
    display_role = role
    if role in ROLE_MAPPING:
        display_role = ROLE_MAPPING[role]
    
    # Labels par defaut
    default_labels = {
        'claim_rate': "Taux de Reclamations",
        'satisfaction_index': "Indice Satisfaction",
        'urgency_rate': "Taux d'Urgence",
        'confidence_score': "Confiance Moyenne",
        'thematic_distribution': "Themes Identifies"
    }
    
    # Labels personnalises pour Agent SAV (focus operationnel)
    if display_role == "Agent SAV":
        return {
            'claim_rate': "Reclamations a Traiter",
            'satisfaction_index': "Satisfaction Client",
            'urgency_rate': "Tickets Urgents",
            'confidence_score': "Confiance",
            'thematic_distribution': "Categories"
        }
    
    # Labels pour Manager (focus performance)
    if display_role == "Manager":
        return {
            'claim_rate': "Taux de Reclamations",
            'satisfaction_index': "Performance Satisfaction",
            'urgency_rate': "Taux Criticite",
            'confidence_score': "Qualite Classification",
            'thematic_distribution': "Repartition Thematique"
        }
    
    # Par defaut (Data Analyst, Director)
    return default_labels


# ==============================================================================
# COMPOSANT: INDICATEUR DE ROLE
# ==============================================================================

def render_role_indicator():
    """
    Affiche un petit indicateur du role actuel en haut de page
    
    Badge discret mais visible montrant le role actif et permettant
    un changement rapide.
    """
    # Obtenir le role actuel et le convertir si necessaire
    current_role = get_current_role()
    display_role = current_role
    if current_role in ROLE_MAPPING:
        display_role = ROLE_MAPPING[current_role]
    
    role_config = AVAILABLE_ROLES[display_role]
    
    # Badge compact en haut de page
    st.markdown(f"""
    <div style="position: fixed; top: 1rem; right: 1rem; z-index: 999; 
                background: {role_config['color']}; color: white; 
                padding: 0.5rem 1rem; border-radius: 20px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                font-size: 0.85rem; font-weight: 600;">
        <i class="fas {role_config['icon']}" style="margin-right: 0.5rem;"></i>
        {current_role}
    </div>
    """, unsafe_allow_html=True)

