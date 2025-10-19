"""
FreeMobilaChat - Application FastAPI pour Vercel
Interface web statique avec redirection vers Streamlit Cloud
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(
    title="FreeMobilaChat",
    description="Application d'analyse de données Twitter avec IA",
    version="1.0.0"
)

# Configuration pour Vercel
STREAMLIT_CLOUD_URL = "https://freemobilachat.streamlit.app"

@app.get("/")
async def root():
    """Page d'accueil avec redirection vers Streamlit Cloud"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FreeMobilaChat - Analyse IA</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #CC0000 0%, #8B0000 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
            }
            .container {
                text-align: center;
                max-width: 800px;
                padding: 2rem;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                backdrop-filter: blur(10px);
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            }
            .logo {
                width: 100px;
                height: 100px;
                background: white;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 2rem;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            }
            .logo span {
                font-size: 3rem;
                font-weight: 900;
                color: #CC0000;
            }
            h1 {
                font-size: 3.5rem;
                font-weight: 800;
                margin-bottom: 1rem;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            }
            .subtitle {
                font-size: 1.5rem;
                margin-bottom: 2rem;
                opacity: 0.9;
            }
            .description {
                font-size: 1.1rem;
                margin-bottom: 3rem;
                line-height: 1.6;
                opacity: 0.8;
            }
            .btn {
                display: inline-block;
                background: white;
                color: #CC0000;
                padding: 1rem 2rem;
                border-radius: 50px;
                text-decoration: none;
                font-weight: 700;
                font-size: 1.2rem;
                margin: 0.5rem;
                transition: all 0.3s ease;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            }
            .btn:hover {
                transform: translateY(-3px);
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 2rem;
                margin-top: 3rem;
            }
            .feature {
                background: rgba(255, 255, 255, 0.1);
                padding: 1.5rem;
                border-radius: 15px;
                backdrop-filter: blur(5px);
            }
            .feature i {
                font-size: 2rem;
                margin-bottom: 1rem;
                display: block;
            }
            .loading {
                margin-top: 2rem;
                font-size: 1.1rem;
                opacity: 0.8;
            }
            .spinner {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                border-top-color: white;
                animation: spin 1s ease-in-out infinite;
                margin-right: 10px;
            }
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            @media (max-width: 768px) {
                h1 { font-size: 2.5rem; }
                .subtitle { font-size: 1.2rem; }
                .container { margin: 1rem; padding: 1.5rem; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">
                <span>FM</span>
            </div>
            <h1>FreeMobilaChat</h1>
            <p class="subtitle">Analyse Intelligente de Données Twitter</p>
            <p class="description">
                Application d'analyse de sentiment et de classification avec intelligence artificielle.<br>
                Développé dans le cadre d'un mémoire de master en Data Science.
            </p>
            
            <a href="https://freemobilachat.streamlit.app" class="btn" target="_blank">
                <i class="fas fa-rocket"></i> Lancer l'Application
            </a>
            <a href="https://github.com/Archimed-Anderson/FreeMobilaChat" class="btn" target="_blank">
                <i class="fab fa-github"></i> Code Source
            </a>
            
            <div class="features">
                <div class="feature">
                    <i class="fas fa-brain"></i>
                    <h3>IA Avancée</h3>
                    <p>Analyse intelligente avec LLM</p>
                </div>
                <div class="feature">
                    <i class="fas fa-chart-line"></i>
                    <h3>Visualisations</h3>
                    <p>Graphiques interactifs</p>
                </div>
                <div class="feature">
                    <i class="fas fa-upload"></i>
                    <h3>Upload Multiple</h3>
                    <p>Support CSV, Excel, JSON</p>
                </div>
                <div class="feature">
                    <i class="fas fa-shield-alt"></i>
                    <h3>Sécurisé</h3>
                    <p>Données protégées</p>
                </div>
            </div>
            
            <div class="loading">
                <div class="spinner"></div>
                Redirection automatique vers l'application...
            </div>
        </div>
        
        <script>
            // Redirection automatique après 3 secondes
            setTimeout(function() {
                window.open('https://freemobilachat.streamlit.app', '_blank');
            }, 3000);
        </script>
    </body>
    </html>
    """)

@app.get("/app")
async def app_redirect():
    """Redirection directe vers l'application Streamlit"""
    return RedirectResponse(url=STREAMLIT_CLOUD_URL, status_code=302)

@app.get("/streamlit")
async def streamlit_redirect():
    """Redirection vers Streamlit Cloud"""
    return RedirectResponse(url=STREAMLIT_CLOUD_URL, status_code=302)

@app.get("/health")
async def health_check():
    """Point de contrôle de santé de l'API"""
    return {
        "status": "healthy", 
        "message": "FreeMobilaChat API is running",
        "streamlit_url": STREAMLIT_CLOUD_URL,
        "version": "1.0.0"
    }

@app.get("/api/info")
async def api_info():
    """Informations sur l'API"""
    return {
        "name": "FreeMobilaChat",
        "description": "Application d'analyse de données Twitter avec IA",
        "version": "1.0.0",
        "author": "Archimed Anderson",
        "streamlit_url": STREAMLIT_CLOUD_URL,
        "github_url": "https://github.com/Archimed-Anderson/FreeMobilaChat",
        "features": [
            "Analyse intelligente avec LLM",
            "Visualisations interactives",
            "Upload multiple de fichiers",
            "Classification automatique",
            "Détection d'anomalies"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
