"""
FreeMobilaChat - Application d'Analyse de Données Twitter
Interface utilisateur moderne pour l'analyse de sentiment et de classification
Développé dans le cadre d'un mémoire de master en Data Science
"""

import streamlit as st

# Configuration
st.set_page_config(
    page_title="FreeMobilaChat - Analyse IA",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Chargement des styles CSS personnalisés
def load_css():
    st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
    /* Reset */
    .main {padding: 0 !important; background: #f8f9fa;}
    .block-container {padding: 0 !important; max-width: 100% !important;}
    #MainMenu, footer, header {visibility: hidden;}
    
    * {-webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; text-rendering: optimizeLegibility;}
    .stButton > button {background: linear-gradient(135deg, #CC0000 0%, #8B0000 100%); color: white; font-weight: 700; font-size: 1.2rem; padding: 1rem 3rem; border-radius: 50px; border: none; box-shadow: 0 4px 15px rgba(204, 0, 0, 0.3); transition: all 0.3s; letter-spacing: 0.5px;}
    .stButton > button:hover {transform: translateY(-2px); box-shadow: 0 6px 20px rgba(204, 0, 0, 0.4);}
    .icon-box {width: 80px; height: 80px; background: linear-gradient(135deg, #CC0000 0%, #8B0000 100%); border-radius: 20px; display: flex; align-items: center; justify-content: center; margin: 0 auto 1.5rem; box-shadow: 0 8px 20px rgba(204, 0, 0, 0.3);}
    .icon-box i {font-size: 2.5rem; color: white;}
    h1, h2, h3 {text-shadow: 1px 1px 2px rgba(0,0,0,0.1);}
    </style>
    """, unsafe_allow_html=True)

def render_header():
    """Affichage de l'en-tête principal avec navigation"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #CC0000 0%, #8B0000 100%); padding: 1.5rem 3rem; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="width: 60px; height: 60px; background: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
                <span style="font-size: 2rem; font-weight: 900; color: #CC0000; text-shadow: none; letter-spacing: -1px;">FM</span>
            </div>
            <div style="display: flex; flex-direction: column;">
                <span style="font-size: 1.8rem; font-weight: 900; color: white; line-height: 1; letter-spacing: -1px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">FreeMobila</span>
                <span style="font-size: 1.3rem; font-weight: 700; color: white; line-height: 1; letter-spacing: 1px; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">CHAT</span>
            </div>
        </div>
        <div style="display: flex; gap: 2rem;">
            <a href="#offres" style="color: white; text-decoration: none; font-weight: 600; font-size: 1.1rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">Offres</a>
            <a href="#fonctionnalites" style="color: white; text-decoration: none; font-weight: 600; font-size: 1.1rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">Fonctionnalites</a>
            <a href="#partenaires" style="color: white; text-decoration: none; font-weight: 600; font-size: 1.1rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">Partenaires</a>
            <a href="#contact" style="color: white; text-decoration: none; font-weight: 600; font-size: 1.1rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">Contact</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_hero():
    """Section principale avec présentation de l'application"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #CC0000 0%, #8B0000 100%); padding: 3rem 2rem; text-align: center; min-height: 60vh; display: flex; flex-direction: column; justify-content: center;">
        <h1 style="color: white; font-size: 2.8rem; font-weight: 900; margin-bottom: 1rem; text-shadow: 3px 3px 6px rgba(0,0,0,0.3); letter-spacing: -1px;">Analysez vos Tweets avec l'IA</h1>
        <p style="color: white; font-size: 1.1rem; opacity: 0.98; max-width: 700px; margin: 0 auto 2rem; text-shadow: 1px 1px 3px rgba(0,0,0,0.2); font-weight: 400; line-height: 1.6;">Transformez vos donnees Twitter en insights actionnables grace a l'intelligence artificielle.<br>Analyse de sentiment, categorisation automatique et KPIs en temps reel.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Commencer Maintenant", type="primary", use_container_width=True):
            st.switch_page("pages/analyse_intelligente.py")
    
    # Indicateur de scroll
    st.markdown("""
    <div style="text-align: center; margin-top: 2rem;">
        <div style="color: white; font-size: 1rem; margin-bottom: 1rem; opacity: 0.8;">Découvrez nos fonctionnalités</div>
        <div style="color: white; font-size: 2rem; animation: bounce 2s infinite;">↓</div>
    </div>
    <style>
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-10px); }
        60% { transform: translateY(-5px); }
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    
    # 3 Cartes avec icônes Font Awesome
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.markdown("""
        <div style="text-align: center; 
                    padding: 3rem 2rem; 
                    background: white; 
                    border-radius: 20px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1); 
                    margin: 0 1rem;
                    transition: all 0.3s;">
            <div class="icon-box">
                <i class="fas fa-bolt"></i>
            </div>
            <h3 style="color: #CC0000; 
                       font-size: 1.8rem; 
                       font-weight: 700; 
                       margin-bottom: 1rem;
                       text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
                       letter-spacing: -0.5px;">
                Rapide
            </h3>
            <p style="color: #555; 
                      font-size: 1.1rem; 
                      line-height: 1.6;
                      font-weight: 400;">
                Resultats en moins de 3 secondes
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_b:
        st.markdown("""
        <div style="text-align: center; 
                    padding: 3rem 2rem; 
                    background: white; 
                    border-radius: 20px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1); 
                    margin: 0 1rem;">
            <div class="icon-box">
                <i class="fas fa-bullseye"></i>
            </div>
            <h3 style="color: #CC0000; 
                       font-size: 1.8rem; 
                       font-weight: 700; 
                       margin-bottom: 1rem;
                       text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
                       letter-spacing: -0.5px;">
                Precis
            </h3>
            <p style="color: #555; 
                      font-size: 1.1rem; 
                      line-height: 1.6;
                      font-weight: 400;">
                IA avec 98,5% de precision
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_c:
        st.markdown("""
        <div style="text-align: center; 
                    padding: 3rem 2rem; 
                    background: white; 
                    border-radius: 20px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1); 
                    margin: 0 1rem;">
            <div class="icon-box">
                <i class="fas fa-chart-line"></i>
            </div>
            <h3 style="color: #CC0000; 
                       font-size: 1.8rem; 
                       font-weight: 700; 
                       margin-bottom: 1rem;
                       text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
                       letter-spacing: -0.5px;">
                Complet
            </h3>
            <p style="color: #555; 
                      font-size: 1.1rem; 
                      line-height: 1.6;
                      font-weight: 400;">
                Tableau de bord interactif
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 5rem;'></div>", unsafe_allow_html=True)

def render_pricing():
    """Section tarification"""
    st.markdown("""
    <div id="offres" style="padding: 5rem 3rem; background: white;">
        <h2 style="text-align: center; 
                   font-size: 2.8rem; 
                   font-weight: 900; 
                   color: #333; 
                   margin-bottom: 1rem;
                   text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
                   letter-spacing: -0.5px;">
            Nos Offres Tarifaires
        </h2>
        <div style="width: 100px; height: 4px; background: linear-gradient(90deg, #CC0000 0%, #8B0000 100%); 
                    margin: 0 auto 1rem; border-radius: 2px;"></div>
        <p style="text-align: center; 
                  font-size: 1.2rem; 
                  color: #666; 
                  margin-bottom: 4rem;
                  font-weight: 400;">
            Choisissez le plan qui correspond le mieux a vos besoins
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        st.markdown("""
        <div style="background: white; 
                    padding: 3rem 2rem; 
                    border-radius: 20px; 
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1); 
                    text-align: center; 
                    height: 100%;
                    border: 2px solid #f0f0f0;">
            <h3 style="color: #CC0000; 
                       font-size: 2rem; 
                       font-weight: 700; 
                       margin-bottom: 1rem;
                       text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">
                Starter
            </h3>
            <p style="color: #666; 
                      font-size: 1rem; 
                      margin-bottom: 2rem;
                      font-weight: 400;">
                Parfait pour debuter
            </p>
            <div style="margin-bottom: 2rem;">
                <span style="font-size: 3.5rem; 
                             font-weight: 900; 
                             color: #333;
                             text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">
                    Gratuit
                </span>
            </div>
            <ul style="list-style: none; 
                       padding: 0; 
                       margin: 2rem 0; 
                       text-align: left;">
                <li style="padding: 0.8rem 0; color: #555; font-size: 1rem; font-weight: 400;">
                    <i class="fas fa-check" style="color: #4ade80; margin-right: 0.5rem;"></i> 1 000 tweets/mois
                </li>
                <li style="padding: 0.8rem 0; color: #555; font-size: 1rem; font-weight: 400;">
                    <i class="fas fa-check" style="color: #4ade80; margin-right: 0.5rem;"></i> Analyse de sentiment
                </li>
                <li style="padding: 0.8rem 0; color: #555; font-size: 1rem; font-weight: 400;">
                    <i class="fas fa-check" style="color: #4ade80; margin-right: 0.5rem;"></i> 3 categories
                </li>
                <li style="padding: 0.8rem 0; color: #555; font-size: 1rem; font-weight: 400;">
                    <i class="fas fa-check" style="color: #4ade80; margin-right: 0.5rem;"></i> Rapports mensuels
                </li>
                <li style="padding: 0.8rem 0; color: #555; font-size: 1rem; font-weight: 400;">
                    <i class="fas fa-check" style="color: #4ade80; margin-right: 0.5rem;"></i> Support email
                </li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Choisir Starter", key="starter", use_container_width=True):
            st.success("Plan Starter selectionne !")
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #CC0000 0%, #8B0000 100%); 
                    padding: 3rem 2rem; 
                    border-radius: 20px; 
                    box-shadow: 0 15px 40px rgba(204, 0, 0, 0.3); 
                    text-align: center; 
                    height: 100%;
                    border: 3px solid #CC0000; 
                    position: relative;">
            <div style="position: absolute; 
                        top: -15px; 
                        right: 20px; 
                        background: #FFD700; 
                        color: #333; 
                        padding: 0.5rem 1.5rem; 
                        border-radius: 25px; 
                        font-weight: 700; 
                        font-size: 0.9rem;
                        text-shadow: none;">
                POPULAIRE
            </div>
            <h3 style="color: white; 
                       font-size: 2rem; 
                       font-weight: 700; 
                       margin-bottom: 1rem;
                       text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                Professional
            </h3>
            <p style="color: rgba(255,255,255,0.95); 
                      font-size: 1rem; 
                      margin-bottom: 2rem;
                      font-weight: 400;
                      text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">
                Pour les pros
            </p>
            <div style="margin-bottom: 2rem;">
                <span style="font-size: 3.5rem; 
                             font-weight: 900; 
                             color: white;
                             text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                    49€
                </span>
                <span style="font-size: 1.2rem; 
                             color: rgba(255,255,255,0.9);
                             text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">
                    /mois
                </span>
            </div>
            <ul style="list-style: none; 
                       padding: 0; 
                       margin: 2rem 0; 
                       text-align: left;">
                <li style="padding: 0.8rem 0; color: white; font-size: 1rem; font-weight: 400;">
                    <i class="fas fa-check" style="color: #FFD700; margin-right: 0.5rem;"></i> 100 000 tweets/mois
                </li>
                <li style="padding: 0.8rem 0; color: white; font-size: 1rem; font-weight: 400;">
                    <i class="fas fa-check" style="color: #FFD700; margin-right: 0.5rem;"></i> Analyse IA avancee
                </li>
                <li style="padding: 0.8rem 0; color: white; font-size: 1rem; font-weight: 400;">
                    <i class="fas fa-check" style="color: #FFD700; margin-right: 0.5rem;"></i> Categories illimitees
                </li>
                <li style="padding: 0.8rem 0; color: white; font-size: 1rem; font-weight: 400;">
                    <i class="fas fa-check" style="color: #FFD700; margin-right: 0.5rem;"></i> Rapports temps reel
                </li>
                <li style="padding: 0.8rem 0; color: white; font-size: 1rem; font-weight: 400;">
                    <i class="fas fa-check" style="color: #FFD700; margin-right: 0.5rem;"></i> Support 24/7
                </li>
                <li style="padding: 0.8rem 0; color: white; font-size: 1rem; font-weight: 400;">
                    <i class="fas fa-check" style="color: #FFD700; margin-right: 0.5rem;"></i> API access
                </li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Choisir Professional", key="pro", use_container_width=True):
            st.success("Plan Professional selectionne !")
    
    with col3:
        st.markdown("""
        <div style="background: white; 
                    padding: 3rem 2rem; 
                    border-radius: 20px; 
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1); 
                    text-align: center; 
                    height: 100%;
                    border: 2px solid #f0f0f0;">
            <h3 style="color: #CC0000; 
                       font-size: 2rem; 
                       font-weight: 700; 
                       margin-bottom: 1rem;
                       text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">
                Enterprise
            </h3>
            <p style="color: #666; 
                      font-size: 1rem; 
                      margin-bottom: 2rem;
                      font-weight: 400;">
                Solution sur mesure
            </p>
            <div style="margin-bottom: 2rem;">
                <span style="font-size: 2.5rem; 
                             font-weight: 900; 
                             color: #333;
                             text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">
                    Sur Devis
                </span>
            </div>
            <ul style="list-style: none; 
                       padding: 0; 
                       margin: 2rem 0; 
                       text-align: left;">
                <li style="padding: 0.8rem 0; color: #555; font-size: 1rem; font-weight: 400;">
                    <i class="fas fa-check" style="color: #4ade80; margin-right: 0.5rem;"></i> Volume illimite
                </li>
                <li style="padding: 0.8rem 0; color: #555; font-size: 1rem; font-weight: 400;">
                    <i class="fas fa-check" style="color: #4ade80; margin-right: 0.5rem;"></i> Modeles IA dedies
                </li>
                <li style="padding: 0.8rem 0; color: #555; font-size: 1rem; font-weight: 400;">
                    <i class="fas fa-check" style="color: #4ade80; margin-right: 0.5rem;"></i> Dashboards custom
                </li>
                <li style="padding: 0.8rem 0; color: #555; font-size: 1rem; font-weight: 400;">
                    <i class="fas fa-check" style="color: #4ade80; margin-right: 0.5rem;"></i> Integration complete
                </li>
                <li style="padding: 0.8rem 0; color: #555; font-size: 1rem; font-weight: 400;">
                    <i class="fas fa-check" style="color: #4ade80; margin-right: 0.5rem;"></i> Gestionnaire dedie
                </li>
                <li style="padding: 0.8rem 0; color: #555; font-size: 1rem; font-weight: 400;">
                    <i class="fas fa-check" style="color: #4ade80; margin-right: 0.5rem;"></i> SLA garanti
                </li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Nous Contacter", key="enterprise", use_container_width=True):
            st.info("Notre equipe vous contactera sous 24h")
    
    st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)

def render_features():
    """Section fonctionnalités avec icônes Font Awesome"""
    # Section de navigation rapide vers les pages d'analyse
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 3rem; text-align: center; margin: 3rem 0; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
        <h2 style="color: #CC0000; font-size: 2.5rem; font-weight: 800; margin-bottom: 1.5rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">Accès Rapide aux Analyses</h2>
        <p style="color: #666; font-size: 1.2rem; margin-bottom: 3rem; font-weight: 400; line-height: 1.6;">Choisissez votre type d'analyse et commencez immédiatement</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Cartes de navigation avec composants Streamlit natifs
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-left: 4px solid #CC0000; text-align: center;">
            <i class="fas fa-brain" style="font-size: 2.5rem; color: #CC0000; margin-bottom: 1rem;"></i>
            <h3 style="color: #333; font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem;">Analyse Intelligente</h3>
            <p style="color: #666; font-size: 1rem; margin-bottom: 1.5rem;">IA avancée avec LLM pour des insights uniques</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Commencer l'Analyse Intelligente", type="primary", use_container_width=True):
            st.switch_page("pages/analyse_intelligente.py")
    
    with col2:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-left: 4px solid #28a745; text-align: center;">
            <i class="fas fa-chart-bar" style="font-size: 2.5rem; color: #28a745; margin-bottom: 1rem;"></i>
            <h3 style="color: #333; font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem;">Analyse Classique</h3>
            <p style="color: #666; font-size: 1rem; margin-bottom: 1.5rem;">Analyse traditionnelle avec visualisations</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Commencer l'Analyse Classique", type="secondary", use_container_width=True):
            st.switch_page("pages/analyse_old.py")
    
    with col3:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-left: 4px solid #17a2b8; text-align: center;">
            <i class="fas fa-chart-line" style="font-size: 2.5rem; color: #17a2b8; margin-bottom: 1rem;"></i>
            <h3 style="color: #333; font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem;">Résultats</h3>
            <p style="color: #666; font-size: 1rem; margin-bottom: 1.5rem;">Visualisez et explorez vos résultats</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Voir les Résultats", type="secondary", use_container_width=True):
            st.switch_page("pages/resultat.py")
    
    st.markdown("""
    <div id="fonctionnalites" style="padding: 5rem 3rem; background: #f8f9fa;">
        <h2 style="text-align: center; 
                   font-size: 2.8rem; 
                   font-weight: 900; 
                   color: #333; 
                   margin-bottom: 1rem;
                   text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
                   letter-spacing: -0.5px;">
            Fonctionnalites Principales
        </h2>
        <div style="width: 100px; height: 4px; background: linear-gradient(90deg, #CC0000 0%, #8B0000 100%); 
                    margin: 0 auto 1rem; border-radius: 2px;"></div>
        <p style="text-align: center; 
                  font-size: 1.2rem; 
                  color: #666; 
                  margin-bottom: 4rem;
                  font-weight: 400;">
            Tout ce dont vous avez besoin pour analyser vos tweets
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    features = [
        ("fas fa-robot", "Analyse IA Avancee", "Utilisation de modeles de langage de pointe pour une analyse precise"),
        ("fas fa-chart-bar", "Dashboards Interactifs", "Visualisations dynamiques et personnalisables"),
        ("fas fa-clock", "Temps Reel", "Traitement et analyse des tweets en temps reel"),
        ("fas fa-tags", "Categorisation Auto", "Classification automatique des tweets"),
        ("fas fa-file-export", "Rapports Detailles", "Generation automatique de rapports exportables"),
        ("fas fa-shield-alt", "Securite Maximale", "Chiffrement des donnees et conformite RGPD")
    ]
    
    for i in range(0, len(features), 3):
        col1, col2, col3 = st.columns(3, gap="large")
        
        for j, col in enumerate([col1, col2, col3]):
            if i + j < len(features):
                icon, title, desc = features[i + j]
                with col:
                    st.markdown(f"""
                    <div style="background: white; 
                                padding: 2.5rem 2rem; 
                                border-radius: 15px; 
                                box-shadow: 0 5px 20px rgba(0,0,0,0.08); 
                                text-align: center;
                                border: 1px solid #f0f0f0; 
                                height: 100%;">
                        <div class="icon-box" style="width: 70px; height: 70px;">
                            <i class="{icon}" style="font-size: 2rem;"></i>
                        </div>
                        <h3 style="color: #CC0000; 
                                   font-size: 1.5rem; 
                                   font-weight: 700; 
                                   margin-bottom: 1rem;
                                   text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
                                   letter-spacing: -0.3px;">
                            {title}
                        </h3>
                        <p style="color: #555; 
                                  font-size: 1rem; 
                                  line-height: 1.6;
                                  font-weight: 400;">
                            {desc}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)

def render_partners():
    """Section partenaires"""
    st.markdown("""
    <div id="partenaires" style="padding: 5rem 3rem; background: white;">
        <h2 style="text-align: center; 
                   font-size: 2.8rem; 
                   font-weight: 900; 
                   color: #333; 
                   margin-bottom: 1rem;
                   text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
                   letter-spacing: -0.5px;">
            Nos Partenaires Technologiques
        </h2>
        <div style="width: 100px; height: 4px; background: linear-gradient(90deg, #CC0000 0%, #8B0000 100%); 
                    margin: 0 auto 1rem; border-radius: 2px;"></div>
        <p style="text-align: center; 
                  font-size: 1.2rem; 
                  color: #666; 
                  margin-bottom: 4rem;
                  font-weight: 400;">
            Nous collaborons avec les leaders de l'IA
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5, gap="large")
    
    partners = [
        ("OpenAI", "#667eea"),
        ("Mistral AI", "#764ba2"),
        ("Ollama", "#4ade80"),
        ("Anthropic", "#f97316"),
        ("Streamlit", "#FF4B4B")
    ]
    
    for col, (name, color) in zip([col1, col2, col3, col4, col5], partners):
        with col:
            st.markdown(f"""
            <div style="text-align: center; 
                        padding: 2rem; 
                        background: white; 
                        border-radius: 15px;
                        box-shadow: 0 5px 15px rgba(0,0,0,0.08); 
                        border: 2px solid {color};">
                <h3 style="color: {color}; 
                           font-size: 1.5rem; 
                           font-weight: 700; 
                           margin: 0;
                           text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">
                    {name}
                </h3>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)

def render_footer():
    """Footer 4 colonnes avec texte noir sur fond clair"""
    st.markdown("""
    <div id="contact" style="background: #f8f9fa; padding: 4rem 3rem 2rem;">
        <h2 style="text-align: center; 
                   color: #222; 
                   font-size: 2.8rem; 
                   font-weight: 900; 
                   margin-bottom: 1rem;
                   text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
                   letter-spacing: -0.5px;">
            Contactez-nous
        </h2>
        <div style="width: 100px; height: 4px; background: linear-gradient(90deg, #CC0000 0%, #8B0000 100%); 
                    margin: 0 auto 3rem; border-radius: 2px;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4, gap="large")
    
    with col1:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); border: 1px solid #e0e0e0;">
            <h3 style="color: #CC0000; 
                       font-size: 1.5rem; 
                       font-weight: 700; 
                       margin-bottom: 1.5rem; 
                       border-bottom: 3px solid #CC0000; 
                       padding-bottom: 0.5rem;
                       text-shadow: none;">
                Chat Mobile Gratuit
            </h3>
            <p style="color: #333; 
                      line-height: 1.8; 
                      font-size: 1rem; 
                      margin-bottom: 2rem;
                      font-weight: 400;
                      text-shadow: none;">
                Solution d'analyse de tweets par intelligence artificielle.
                Transformez vos donnees en insights actionnables.
            </p>
            <div style="display: flex; gap: 1rem;">
                <a href="#" style="width: 50px; height: 50px; background: #CC0000; 
                                  border-radius: 50%; display: flex; align-items: center; 
                                  justify-content: center; color: white; font-size: 1.3rem;
                                  transition: all 0.3s;">
                    <i class="fab fa-facebook-f"></i>
                </a>
                <a href="#" style="width: 50px; height: 50px; background: #CC0000; 
                                  border-radius: 50%; display: flex; align-items: center; 
                                  justify-content: center; color: white; font-size: 1.3rem;
                                  transition: all 0.3s;">
                    <i class="fab fa-twitter"></i>
                </a>
                <a href="#" style="width: 50px; height: 50px; background: #CC0000; 
                                  border-radius: 50%; display: flex; align-items: center; 
                                  justify-content: center; color: white; font-size: 1.3rem;
                                  transition: all 0.3s;">
                    <i class="fab fa-linkedin-in"></i>
                </a>
                <a href="#" style="width: 50px; height: 50px; background: #CC0000; 
                                  border-radius: 50%; display: flex; align-items: center; 
                                  justify-content: center; color: white; font-size: 1.3rem;
                                  transition: all 0.3s;">
                    <i class="fas fa-envelope"></i>
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); border: 1px solid #e0e0e0;">
            <h3 style="color: #CC0000; 
                       font-size: 1.5rem; 
                       font-weight: 700; 
                       margin-bottom: 1.5rem; 
                       border-bottom: 3px solid #CC0000; 
                       padding-bottom: 0.5rem;
                       text-shadow: none;">
                Liens Rapides
            </h3>
            <ul style="list-style: none; padding: 0;">
                <li style="margin-bottom: 1rem;">
                    <a href="#offres" style="color: #333; 
                                            text-decoration: none; 
                                            font-size: 1.1rem;
                                            font-weight: 500;
                                            text-shadow: none;
                                            transition: color 0.3s;">
                        <i class="fas fa-angle-right" style="color: #CC0000; margin-right: 0.5rem;"></i> Nos Offres
                    </a>
                </li>
                <li style="margin-bottom: 1rem;">
                    <a href="#fonctionnalites" style="color: #333; 
                                                       text-decoration: none; 
                                                       font-size: 1.1rem;
                                                       font-weight: 500;
                                                       text-shadow: none;
                                                       transition: color 0.3s;">
                        <i class="fas fa-angle-right" style="color: #CC0000; margin-right: 0.5rem;"></i> Fonctionnalites
                    </a>
                </li>
                <li style="margin-bottom: 1rem;">
                    <a href="#partenaires" style="color: #333; 
                                                  text-decoration: none; 
                                                  font-size: 1.1rem;
                                                  font-weight: 500;
                                                  text-shadow: none;
                                                  transition: color 0.3s;">
                        <i class="fas fa-angle-right" style="color: #CC0000; margin-right: 0.5rem;"></i> Partenaires
                    </a>
                </li>
                <li style="margin-bottom: 1rem;">
                    <a href="/pages/01_analyse.py" style="color: #333; 
                                                          text-decoration: none; 
                                                          font-size: 1.1rem;
                                                          font-weight: 500;
                                                          text-shadow: none;
                                                          transition: color 0.3s;">
                        <i class="fas fa-angle-right" style="color: #CC0000; margin-right: 0.5rem;"></i> Commencer
                    </a>
                </li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); border: 1px solid #e0e0e0;">
            <h3 style="color: #CC0000; 
                       font-size: 1.5rem; 
                       font-weight: 700; 
                       margin-bottom: 1.5rem; 
                       border-bottom: 3px solid #CC0000; 
                       padding-bottom: 0.5rem;
                       text-shadow: none;">
                Coordonnees
            </h3>
            <div style="margin-bottom: 1.5rem; padding: 1.2rem; background: #f8f9fa; border-radius: 10px; border: 1px solid #e0e0e0;">
                <div style="color: #CC0000; font-size: 1.5rem; margin-bottom: 0.8rem;">
                    <i class="fas fa-envelope"></i>
                </div>
                <div style="font-size: 0.9rem; 
                           color: #666; 
                           margin-bottom: 0.5rem;
                           font-weight: 600;
                           text-shadow: none;
                           text-transform: uppercase;
                           letter-spacing: 0.5px;">
                    Email
                </div>
                <div style="font-size: 1.1rem; 
                           color: #222; 
                           font-weight: 600;
                           text-shadow: none;">
                    contact@freemobilachat.com
                </div>
            </div>
            <div style="padding: 1.2rem; background: #f8f9fa; border-radius: 10px; border: 1px solid #e0e0e0;">
                <div style="color: #CC0000; font-size: 1.5rem; margin-bottom: 0.8rem;">
                    <i class="fas fa-phone"></i>
                </div>
                <div style="font-size: 0.9rem; 
                           color: #666; 
                           margin-bottom: 0.5rem;
                           font-weight: 600;
                           text-shadow: none;
                           text-transform: uppercase;
                           letter-spacing: 0.5px;">
                    Telephone
                </div>
                <div style="font-size: 1.1rem; 
                           color: #222; 
                           font-weight: 600;
                           text-shadow: none;">
                    +33 1 23 45 67 89
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="background: white; 
                    padding: 2rem; 
                    border-radius: 15px; 
                    box-shadow: 0 2px 10px rgba(0,0,0,0.08); 
                    border: 2px solid #CC0000;">
            <h3 style="color: #CC0000; 
                       font-size: 1.5rem; 
                       font-weight: 700; 
                       margin-bottom: 1.5rem; 
                       border-bottom: 3px solid #CC0000; 
                       padding-bottom: 0.5rem;
                       text-shadow: none;">
                Formulaire Contact
            </h3>
        """, unsafe_allow_html=True)
        
        with st.form(key="contact_form"):
            nom = st.text_input("Nom", placeholder="Jean Dupont", label_visibility="collapsed")
            email = st.text_input("Email", placeholder="jean@email.com", label_visibility="collapsed")
            message = st.text_area("Message", placeholder="Votre message...", height=100, label_visibility="collapsed")
            
            submit = st.form_submit_button("Envoyer", use_container_width=True, type="primary")
            
            if submit:
                if nom and email and message:
                    st.success("Message envoye !")
                    st.balloons()
                else:
                    st.error("Tous les champs requis")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Copyright
    st.markdown("""
    <div style="background: #f8f9fa; 
                padding: 2rem 3rem; 
                text-align: center; 
                border-top: 2px solid #e0e0e0;
                margin-top: 3rem;">
        <p style="color: #333; 
                  font-size: 1rem; 
                  margin: 0;
                  font-weight: 500;
                  text-shadow: none;">
            &copy; 2025 FreeMobilaChat. Tous droits reserves. | 
            <a href="#" style="color: #CC0000; text-decoration: none; font-weight: 600;">Politique</a> | 
            <a href="#" style="color: #CC0000; text-decoration: none; font-weight: 600;">CGU</a> | 
            <a href="#" style="color: #CC0000; text-decoration: none; font-weight: 600;">Mentions</a>
        </p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Fonction principale"""
    load_css()
    render_header()
    render_hero()
    render_pricing()
    render_features()
    render_partners()
    render_footer()

if __name__ == "__main__":
    main()
