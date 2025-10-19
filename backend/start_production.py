#!/usr/bin/env python3
"""
Production server startup script for FreeMobilaChat Backend
Uses Gunicorn with Uvicorn workers for production deployment
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.config import config
from app.utils.database import get_database_manager

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def initialize_application():
    """Initialize application components"""
    try:
        logger.info("🚀 Initializing FreeMobilaChat Backend for Production")
        logger.info(f"Environment: {config.environment}")
        logger.info(f"Database: {config.database.type}")
        
        # Initialize database
        db_manager = get_database_manager()
        await db_manager.initialize_database()
        logger.info("✅ Database initialized successfully")
        
        # Create necessary directories
        config.data_raw_dir.mkdir(parents=True, exist_ok=True)
        config.data_processed_dir.mkdir(parents=True, exist_ok=True)
        config.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Create logs directory
        logs_dir = Path("./logs")
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("✅ Application initialization completed")
        
    except Exception as e:
        logger.error(f"❌ Application initialization failed: {e}")
        raise


def run_production_server():
    """Run the production server with Gunicorn"""
    
    # Initialize application
    asyncio.run(initialize_application())
    
    # Production server configuration
    host = os.getenv("FASTAPI_HOST", "0.0.0.0")
    port = int(os.getenv("FASTAPI_PORT", "8000"))
    workers = int(os.getenv("FASTAPI_WORKERS", "4"))
    
    logger.info("🚀 Starting Production Server")
    logger.info(f"📡 Server will be available at: http://{host}:{port}")
    logger.info(f"👥 Workers: {workers}")
    logger.info(f"🔒 Environment: {config.environment}")
    logger.info("-" * 60)
    
    # Import and run with Gunicorn
    try:
        import gunicorn.app.wsgiapp as wsgi
        
        # Gunicorn configuration
        sys.argv = [
            "gunicorn",
            "--bind", f"{host}:{port}",
            "--workers", str(workers),
            "--worker-class", "uvicorn.workers.UvicornWorker",
            "--worker-connections", "1000",
            "--max-requests", "1000",
            "--max-requests-jitter", "100",
            "--timeout", "60",
            "--keep-alive", "5",
            "--log-level", config.log_level.lower(),
            "--access-logfile", "-",
            "--error-logfile", "-",
            "--preload",
            "app.main:app"
        ]
        
        wsgi.run()
        
    except ImportError:
        logger.warning("Gunicorn not available, falling back to Uvicorn")
        
        # Fallback to Uvicorn
        import uvicorn
        
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            workers=workers,
            log_level=config.log_level.lower(),
            access_log=True,
            reload=False,
            loop="asyncio"
        )


if __name__ == "__main__":
    run_production_server()
