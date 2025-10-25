"""
FreeMobilaChat - Twitter Data Analysis Application
Modern user interface for sentiment analysis and classification
Developed as part of a Master's thesis in Data Science
"""

import streamlit as st

# Configuration
st.set_page_config(
    page_title="FreeMobilaChat - AI Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS styles loading
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
    """Main header display with navigation"""
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
    """Main section with application presentation"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #CC0000 0%, #8B0000 100%); padding: 3rem 2rem; text-align: center; min-height: 60vh; display: flex; flex-direction: column; justify-content: center;">
        <h1 style="color: white; font-size: 2.8rem; font-weight: 900; margin-bottom: 1rem; text-shadow: 3px 3px 6px rgba(0,0,0,0.3); letter-spacing: -1px;">Analyze Your Tweets with AI</h1>
        <p style="color: white; font-size: 1.1rem; opacity: 0.98; max-width: 700px; margin: 0 auto 2rem; text-shadow: 1px 1px 3px rgba(0,0,0,0.2); font-weight: 400; line-height: 1.6;">Transform your Twitter data into actionable insights with artificial intelligence.<br>Sentiment analysis, automatic categorization and real-time KPIs.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Start Now", type="primary", use_container_width=True):
            st.switch_page("pages/analyse_intelligente.py")
    
    # Scroll indicator
    st.markdown("""
    <div style="text-align: center; margin-top: 2rem;">
        <div style="color: white; font-size: 1rem; margin-bottom: 1rem; opacity: 0.8;">Discover our features</div>
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
    
    # 3 Cards with Font Awesome icons
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
                Fast
            </h3>
            <p style="color: #555; 
                      font-size: 1.1rem; 
                      line-height: 1.6;
                      font-weight: 400;">
                Results in less than 3 seconds
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
                Accurate
            </h3>
            <p style="color: #555; 
                      font-size: 1.1rem; 
                      line-height: 1.6;
                      font-weight: 400;">
                AI with 98.5% accuracy
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
                Complete
            </h3>
            <p style="color: #555; 
                      font-size: 1.1rem; 
                      line-height: 1.6;
                      font-weight: 400;">
                Interactive dashboard
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 5rem;'></div>", unsafe_allow_html=True)

def render_pricing():
    """Pricing section"""
    st.markdown("""
    <div id="offres" style="padding: 5rem 3rem; background: white;">
        <h2 style="text-align: center; 
                   font-size: 2.8rem; 
                   font-weight: 900; 
                   color: #333; 
                   margin-bottom: 1rem;
                   text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
                   letter-spacing: -0.5px;">
            Our Pricing Plans
        </h2>
        <div style="width: 100px; height: 4px; background: linear-gradient(90deg, #CC0000 0%, #8B0000 100%); 
                    margin: 0 auto 1rem; border-radius: 2px;"></div>
        <p style="text-align: center; 
                  font-size: 1.2rem; 
                  color: #666; 
                  margin-bottom: 4rem;
                  font-weight: 400;">
            Choose the plan that best fits your needs
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
                Perfect for beginners
            </p>
            <div style="margin-bottom: 2rem;">
                <span style="font-size: 3.5rem; 
                             font-weight: 900; 
                             color: #333;
                             text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">
                    Free
                </span>
            </div>
            <ul style="list-style: none; 
                       padding: 0; 
                       margin: 2rem 0; 
                       text-align: left;">
                <li style="padding: 0.8rem 0; color: #555; font-size: 1rem; font-weight: 400;">
                    <i class="fas fa-check" style="color: #4ade80; margin-right: 0.5rem;"></i> 1,000 tweets/month
                </li>
                <li style="padding: 0.8rem 0; color: #555; font-size: 1rem; font-weight: 400;">
                    <i class="fas fa-check" style="color: #4ade80; margin-right: 0.5rem;"></i> Sentiment analysis
                </li>
                <li style="padding: 0.8rem 0; color: #555; font-size: 1rem; font-weight: 400;">
                    <i class="fas fa-check" style="color: #4ade80; margin-right: 0.5rem;"></i> 3 categories
                </li>
                <li style="padding: 0.8rem 0; color: #555; font-size: 1rem; font-weight: 400;">
                    <i class="fas fa-check" style="color: #4ade80; margin-right: 0.5rem;"></i> Monthly reports
                </li>
                <li style="padding: 0.8rem 0; color: #555; font-size: 1rem; font-weight: 400;">
                    <i class="fas fa-check" style="color: #4ade80; margin-right: 0.5rem;"></i> Support email
                </li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Choose Starter", key="starter", use_container_width=True):
            st.success("Starter plan selected!")
    
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
                POPULAR
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
                For professionals
            </p>
            <div style="margin-bottom: 2rem;">
                <span style="font-size: 3.5rem; 
                             font-weight: 900; 
                             color: white;
                             text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                    €49
                </span>
                <span style="font-size: 1.2rem; 
                             color: rgba(255,255,255,0.9);
                             text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">
                    /month
                </span>
            </div>
            <ul style="list-style: none; 
                       padding: 0; 
                       margin: 2rem 0; 
                       text-align: left;">
                <li style="padding: 0.8rem 0; color: white; font-size: 1rem; font-weight: 400;">
                    <i class="fas fa-check" style="color: #FFD700; margin-right: 0.5rem;"></i> 100,000 tweets/month
                </li>
                <li style="padding: 0.8rem 0; color: white; font-size: 1rem; font-weight: 400;">
                    <i class="fas fa-check" style="color: #FFD700; margin-right: 0.5rem;"></i> Advanced AI analysis
                </li>
                <li style="padding: 0.8rem 0; color: white; font-size: 1rem; font-weight: 400;">
                    <i class="fas fa-check" style="color: #FFD700; margin-right: 0.5rem;"></i> Unlimited categories
                </li>
                <li style="padding: 0.8rem 0; color: white; font-size: 1rem; font-weight: 400;">
                    <i class="fas fa-check" style="color: #FFD700; margin-right: 0.5rem;"></i> Real-time reports
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
        if st.button("Choose Professional", key="pro", use_container_width=True):
            st.success("Professional plan selected!")
    
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
                Custom solution
            </p>
            <div style="margin-bottom: 2rem;">
                <span style="font-size: 2.5rem; 
                             font-weight: 900; 
                             color: #333;
                             text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">
                    On Quote
                </span>
            </div>
            <ul style="list-style: none; 
                       padding: 0; 
                       margin: 2rem 0; 
                       text-align: left;">
                <li style="padding: 0.8rem 0; color: #555; font-size: 1rem; font-weight: 400;">
                    <i class="fas fa-check" style="color: #4ade80; margin-right: 0.5rem;"></i> Unlimited volume
                </li>
                <li style="padding: 0.8rem 0; color: #555; font-size: 1rem; font-weight: 400;">
                    <i class="fas fa-check" style="color: #4ade80; margin-right: 0.5rem;"></i> Dedicated AI models
                </li>
                <li style="padding: 0.8rem 0; color: #555; font-size: 1rem; font-weight: 400;">
                    <i class="fas fa-check" style="color: #4ade80; margin-right: 0.5rem;"></i> Custom dashboards
                </li>
                <li style="padding: 0.8rem 0; color: #555; font-size: 1rem; font-weight: 400;">
                    <i class="fas fa-check" style="color: #4ade80; margin-right: 0.5rem;"></i> Integration complete
                </li>
                <li style="padding: 0.8rem 0; color: #555; font-size: 1rem; font-weight: 400;">
                    <i class="fas fa-check" style="color: #4ade80; margin-right: 0.5rem;"></i> Dedicated manager
                </li>
                <li style="padding: 0.8rem 0; color: #555; font-size: 1rem; font-weight: 400;">
                    <i class="fas fa-check" style="color: #4ade80; margin-right: 0.5rem;"></i> Guaranteed SLA
                </li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Contact Us", key="enterprise", use_container_width=True):
            st.info("Our team will contact you within 24h")
    
    st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)

def render_features():
    """Features section with Font Awesome icons"""
    # Quick navigation section to analysis pages
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 3rem; text-align: center; margin: 3rem 0; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
        <h2 style="color: #CC0000; font-size: 2.5rem; font-weight: 800; margin-bottom: 1.5rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">Quick Access to Analysis</h2>
        <p style="color: #666; font-size: 1.2rem; margin-bottom: 3rem; font-weight: 400; line-height: 1.6;">Choose your analysis type and start immediately</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation cards with native Streamlit components
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    
    with col1:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-left: 4px solid #CC0000; text-align: center;">
            <i class="fas fa-brain" style="font-size: 2.5rem; color: #CC0000; margin-bottom: 1rem;"></i>
            <h3 style="color: #333; font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem;">Intelligent Analysis</h3>
            <p style="color: #666; font-size: 1rem; margin-bottom: 1.5rem;">Advanced AI with LLM for unique insights</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Intelligent Analysis", type="primary", use_container_width=True):
            st.switch_page("pages/analyse_intelligente.py")
    
    with col2:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-left: 4px solid #28a745; text-align: center;">
            <i class="fas fa-chart-bar" style="font-size: 2.5rem; color: #28a745; margin-bottom: 1rem;"></i>
            <h3 style="color: #333; font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem;">Classic Analysis</h3>
            <p style="color: #666; font-size: 1rem; margin-bottom: 1.5rem;">Traditional analysis with visualizations</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Classic Analysis", type="secondary", use_container_width=True):
            st.switch_page("pages/analyse_old.py")
    
    with col3:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-left: 4px solid #17a2b8; text-align: center;">
            <i class="fas fa-chart-line" style="font-size: 2.5rem; color: #17a2b8; margin-bottom: 1rem;"></i>
            <h3 style="color: #333; font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem;">Results</h3>
            <p style="color: #666; font-size: 1rem; margin-bottom: 1.5rem;">View and explore your results</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View Results", type="secondary", use_container_width=True):
            st.switch_page("pages/resultat.py")
    
    with col4:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-left: 4px solid #6f42c1; text-align: center;">
            <i class="fas fa-robot" style="font-size: 2.5rem; color: #6f42c1; margin-bottom: 1rem;"></i>
            <h3 style="color: #333; font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem;">LLM Classification</h3>
            <p style="color: #666; font-size: 1rem; margin-bottom: 1.5rem;">Automatic classification results</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View LLM Classification", type="secondary", use_container_width=True):
            st.switch_page("pages/classification_llm.py")
    
    st.markdown("""
    <div id="fonctionnalites" style="padding: 5rem 3rem; background: #f8f9fa;">
        <h2 style="text-align: center; 
                   font-size: 2.8rem; 
                   font-weight: 900; 
                   color: #333; 
                   margin-bottom: 1rem;
                   text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
                   letter-spacing: -0.5px;">
            Main Features
        </h2>
        <div style="width: 100px; height: 4px; background: linear-gradient(90deg, #CC0000 0%, #8B0000 100%); 
                    margin: 0 auto 1rem; border-radius: 2px;"></div>
        <p style="text-align: center; 
                  font-size: 1.2rem; 
                  color: #666; 
                  margin-bottom: 4rem;
                  font-weight: 400;">
            Everything you need to analyze your tweets
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    features = [
        ("fas fa-robot", "Advanced AI Analysis", "Using state-of-the-art language models for precise analysis"),
        ("fas fa-chart-bar", "Interactive Dashboards", "Dynamic and customizable visualizations"),
        ("fas fa-clock", "Real Time", "Real-time tweet processing and analysis"),
        ("fas fa-tags", "Auto Categorization", "Automatic tweet classification"),
        ("fas fa-file-export", "Detailed Reports", "Automatic generation of exportable reports"),
        ("fas fa-shield-alt", "Maximum Security", "Data encryption and GDPR compliance")
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
    """Partners section"""
    st.markdown("""
    <div id="partenaires" style="padding: 5rem 3rem; background: white;">
        <h2 style="text-align: center; 
                   font-size: 2.8rem; 
                   font-weight: 900; 
                   color: #333; 
                   margin-bottom: 1rem;
                   text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
                   letter-spacing: -0.5px;">
            Our Technology Partners
        </h2>
        <div style="width: 100px; height: 4px; background: linear-gradient(90deg, #CC0000 0%, #8B0000 100%); 
                    margin: 0 auto 1rem; border-radius: 2px;"></div>
        <p style="text-align: center; 
                  font-size: 1.2rem; 
                  color: #666; 
                  margin-bottom: 4rem;
                  font-weight: 400;">
            We collaborate with AI leaders
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
    """Footer 4 columns with black text on light background"""
    st.markdown("""
    <div id="contact" style="background: #f8f9fa; padding: 4rem 3rem 2rem;">
        <h2 style="text-align: center; 
                   color: #222; 
                   font-size: 2.8rem; 
                   font-weight: 900; 
                   margin-bottom: 1rem;
                   text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
                   letter-spacing: -0.5px;">
            Contact Us
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
                Free Mobile Chat
            </h3>
            <p style="color: #333; 
                      line-height: 1.8; 
                      font-size: 1rem; 
                      margin-bottom: 2rem;
                      font-weight: 400;
                      text-shadow: none;">
                Twitter analysis solution powered by artificial intelligence.
                Transform your data into actionable insights.
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
                Quick Links
            </h3>
            <ul style="list-style: none; padding: 0;">
                <li style="margin-bottom: 1rem;">
                    <a href="#offres" style="color: #333; 
                                            text-decoration: none; 
                                            font-size: 1.1rem;
                                            font-weight: 500;
                                            text-shadow: none;
                                            transition: color 0.3s;">
                        <i class="fas fa-angle-right" style="color: #CC0000; margin-right: 0.5rem;"></i> Our Offers
                    </a>
                </li>
                <li style="margin-bottom: 1rem;">
                    <a href="#fonctionnalites" style="color: #333; 
                                                       text-decoration: none; 
                                                       font-size: 1.1rem;
                                                       font-weight: 500;
                                                       text-shadow: none;
                                                       transition: color 0.3s;">
                        <i class="fas fa-angle-right" style="color: #CC0000; margin-right: 0.5rem;"></i> Features
                    </a>
                </li>
                <li style="margin-bottom: 1rem;">
                    <a href="#partenaires" style="color: #333; 
                                                  text-decoration: none; 
                                                  font-size: 1.1rem;
                                                  font-weight: 500;
                                                  text-shadow: none;
                                                  transition: color 0.3s;">
                        <i class="fas fa-angle-right" style="color: #CC0000; margin-right: 0.5rem;"></i> Partners
                    </a>
                </li>
                <li style="margin-bottom: 1rem;">
                    <a href="/pages/analyse_intelligente.py" style="color: #333; 
                                                          text-decoration: none; 
                                                          font-size: 1.1rem;
                                                          font-weight: 500;
                                                          text-shadow: none;
                                                          transition: color 0.3s;">
                        <i class="fas fa-angle-right" style="color: #CC0000; margin-right: 0.5rem;"></i> Get Started
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
                Contact Information
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
                    Phone
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
                Contact Form
            </h3>
        """, unsafe_allow_html=True)
        
        with st.form(key="contact_form"):
            nom = st.text_input("Name", placeholder="John Doe", label_visibility="collapsed")
            email = st.text_input("Email", placeholder="john@email.com", label_visibility="collapsed")
            message = st.text_area("Message", placeholder="Your message...", height=100, label_visibility="collapsed")
            
            submit = st.form_submit_button("Send", use_container_width=True, type="primary")
            
            if submit:
                if nom and email and message:
                    st.success("Message sent!")
                else:
                    st.error("All fields required")
        
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
            &copy; 2025 FreeMobilaChat. All rights reserved. | 
            <a href="#" style="color: #CC0000; text-decoration: none; font-weight: 600;">Policy</a> | 
            <a href="#" style="color: #CC0000; text-decoration: none; font-weight: 600;">Terms</a> | 
            <a href="#" style="color: #CC0000; text-decoration: none; font-weight: 600;">Legal</a>
        </p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main function"""
    load_css()
    render_header()
    render_hero()
    render_pricing()
    render_features()
    render_partners()
    render_footer()

if __name__ == "__main__":
    main()
