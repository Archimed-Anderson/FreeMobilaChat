"""
Wrapper FastAPI pour déployer l'application Streamlit sur Vercel
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import subprocess
import os
import sys

app = FastAPI(title="FreeMobilaChat API", version="1.0.0")

@app.get("/")
async def root():
    """Redirige vers l'application Streamlit"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>FreeMobilaChat - Redirection</title>
        <meta http-equiv="refresh" content="0; url=/streamlit">
    </head>
    <body>
        <h1>Redirection vers FreeMobilaChat...</h1>
        <p>Si la redirection ne fonctionne pas, <a href="/streamlit">cliquez ici</a>.</p>
    </body>
    </html>
    """)

@app.get("/streamlit")
async def streamlit_app():
    """Lance l'application Streamlit"""
    try:
        # Changer le répertoire de travail vers streamlit_app
        os.chdir("streamlit_app")
        
        # Lancer Streamlit
        result = subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py", 
            "--server.port", "8501", "--server.headless", "true"
        ], capture_output=True, text=True)
        
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>FreeMobilaChat</title>
        </head>
        <body>
            <h1>FreeMobilaChat - Application Streamlit</h1>
            <p>L'application Streamlit est en cours de démarrage...</p>
            <p>Output: {result.stdout}</p>
            <p>Erreurs: {result.stderr}</p>
        </body>
        </html>
        """)
    except Exception as e:
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>FreeMobilaChat - Erreur</title>
        </head>
        <body>
            <h1>Erreur lors du démarrage</h1>
            <p>Erreur: {str(e)}</p>
        </body>
        </html>
        """)

@app.get("/health")
async def health_check():
    """Point de contrôle de santé de l'API"""
    return {"status": "healthy", "message": "FreeMobilaChat API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
