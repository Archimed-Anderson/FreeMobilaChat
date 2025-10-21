"""
FastAPI main application for tweet analysis platform
Provides REST API endpoints for tweet processing and analysis
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime, UTC

# Import our models and services
from .models import (
    TweetRaw, TweetAnalyzed, KPIMetrics, UserRole,
    DEFAULT_DASHBOARD_CONFIGS, AnalysisLog, FeedbackType
)
from .services.csv_processor import CSVProcessor
from .services.llm_analyzer import LLMAnalyzer
from .services.kpi_calculator import KPICalculator
from .services.chatbot_service import ChatbotService

# Import new modernized components
from .config import config  # Import from backend/app/config.py (not config_pkg)
from .exceptions import FreeMobilaChatException, ValidationError
from .utils.validation import DataValidator
from .utils.health_check import health_checker
from .utils.database import get_database_manager

# Configure logging with proper level from config and rotation
# Create logs directory if it doesn't exist
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Configure root logger
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
log_level = getattr(logging, config.log_level)

# Create rotating file handler (10MB max, 5 backup files)
log_file = os.path.join(log_dir, 'app.log')
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setLevel(log_level)
file_handler.setFormatter(logging.Formatter(log_format))

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(log_level)
console_handler.setFormatter(logging.Formatter(log_format))

# Configure root logger
logging.basicConfig(
    level=log_level,
    format=log_format,
    handlers=[file_handler, console_handler]
)

logger = logging.getLogger(__name__)
logger.info(f" Logging configured: level={config.log_level}, file={log_file}")

# Initialize FastAPI app with configuration
app = FastAPI(
    title=config.app_name,
    description="Modern API for analyzing customer service tweets with LLM integration",
    version=config.app_version,
    docs_url="/docs" if config.debug_mode else None,
    redoc_url="/redoc" if config.debug_mode else None
)

# CORS middleware configuration from config
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.security.allowed_origins,
    allow_credentials=True,
    allow_methods=config.security.allowed_methods,
    allow_headers=config.security.allowed_headers,
)

# Global exception handler
@app.exception_handler(FreeMobilaChatException)
async def freemobilachat_exception_handler(request: Request, exc: FreeMobilaChatException):
    """Handle custom application exceptions"""
    logger.error(f"Application error: {exc.message}", extra={"error_code": exc.error_code, "details": exc.details})
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.message,
            "error_code": exc.error_code,
            "details": exc.details,
            "timestamp": datetime.now(UTC).isoformat()
        }
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle validation errors"""
    logger.warning(f"Validation error: {exc.message}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation failed",
            "message": exc.message,
            "timestamp": datetime.now(UTC).isoformat()
        }
    )

# Global instances
csv_processor = CSVProcessor()
kpi_calculator = KPICalculator()
db_manager = get_database_manager()

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and application components"""
    try:
        logger.info(" Initializing FreeMobilaChat Application")
        await db_manager.initialize_database()
        logger.info(" Database initialized successfully")

        # Create necessary directories
        config.data_raw_dir.mkdir(parents=True, exist_ok=True)
        config.data_processed_dir.mkdir(parents=True, exist_ok=True)
        config.upload_dir.mkdir(parents=True, exist_ok=True)

        logger.info(" Application startup completed")
    except Exception as e:
        logger.error(f" Application startup failed: {e}")
        raise

# Health check endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "version": config.app_version,
        "environment": config.environment.value
    }

@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check():
    """Comprehensive health check with system metrics"""
    try:
        health_status = await health_checker.get_health_status()
        return health_status
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat()
            }
        )

@app.get("/database/info", tags=["Debug"])
async def database_info():
    """Get database information for debugging"""
    try:
        # Get recent analysis logs to show active batches
        logs = await db_manager.get_analysis_logs(limit=10)
        batch_ids = [log.get('batch_id') for log in logs if log.get('batch_id')]

        return {
            "database_type": db_manager.database_type,
            "connection_string": db_manager.connection_string if db_manager.database_type == "sqlite" else "***",
            "recent_batches": len(batch_ids),
            "recent_batch_ids": batch_ids[:5],  # Show only first 5
            "total_analysis_logs": len(logs)
        }
    except Exception as e:
        logger.error(f"Error getting database info: {e}")
        return {"error": str(e)}

@app.get("/health/history", tags=["Health"])
async def health_check_history():
    """Get health check history"""
    return {
        "history": health_checker.get_health_history(),
        "timestamp": datetime.now(UTC).isoformat()
    }

# Pydantic models for API requests/responses
class AnalysisRequest(BaseModel):
    """Request model for tweet analysis"""
    llm_provider: str = Field(default_factory=lambda: os.getenv("DEFAULT_LLM_PROVIDER", "mistral"))
    max_tweets: int = 500
    batch_size: int = 10
    user_role: UserRole = UserRole.AGENT

class AnalysisResponse(BaseModel):
    """Response model for analysis results"""
    success: bool
    message: str
    batch_id: Optional[str] = None
    total_tweets: int = 0
    analyzed_tweets: int = 0
    failed_tweets: int = 0
    processing_time: float = 0.0
    estimated_cost: float = 0.0

class KPIResponse(BaseModel):
    """Response model for KPI data"""
    kpis: KPIMetrics
    advanced_metrics: Dict[str, Any]
    insights: List[str]
    generated_at: datetime

@app.get("/test-config", tags=["Testing"])
async def test_config():
    """
    Test configuration endpoint - shows current LLM provider configuration
    """
    return {
        "env_llm_provider": os.getenv("LLM_PROVIDER", "not_set"),
        "env_ollama_base_url": os.getenv("OLLAMA_BASE_URL", "not_set"),
        "env_ollama_model": os.getenv("OLLAMA_MODEL", "not_set"),
        "working_directory": os.getcwd(),
        "env_file_exists": os.path.exists(".env")
    }

@app.post("/test-analyze-single")
async def test_analyze_single(text: str = "Merci Free pour votre excellent service!", provider: str = "ollama"):
    """
    Test endpoint to analyze a single tweet with detailed debugging
    """
    # PRINT to console to verify endpoint is called
    print("=" * 80)
    print(f"🧪 ENDPOINT /test-analyze-single CALLED")
    print(f"   - text parameter: {text[:100] if len(text) > 100 else text}")
    print(f"   - provider parameter: {provider}")
    print(f"   - text length: {len(text)} characters")
    print("=" * 80)

    # LOG 1: Confirm endpoint is called
    logger.info("=" * 80)
    logger.info(f"🧪 ENDPOINT /test-analyze-single CALLED")
    logger.info(f"   - text parameter: {text[:100] if len(text) > 100 else text}")
    logger.info(f"   - provider parameter: {provider}")
    logger.info(f"   - text length: {len(text)} characters")
    logger.info("=" * 80)

    try:
        # LOG 2: Start analysis
        logger.info(f"🧪 Step 1: Starting single tweet analysis")
        logger.info(f"   - Provider requested: {provider}")

        # LOG 3: Create test tweet
        logger.info(f"🧪 Step 2: Creating test tweet object")
        test_tweet = TweetRaw(
            tweet_id="test_001",
            author="test_user",
            text=text,
            date=datetime.now(UTC),
            url="https://twitter.com/test/status/123"
        )
        logger.info(f" Test tweet created successfully")
        logger.info(f"   - Tweet ID: {test_tweet.tweet_id}")
        logger.info(f"   - Author: {test_tweet.author}")
        logger.info(f"   - Text: {test_tweet.text[:100]}...")

        # LOG 4: Initialize analyzer
        logger.info(f"🧪 Step 3: Initializing LLMAnalyzer")
        logger.info(f"   - Provider: {provider}")
        logger.info(f"   - Batch size: 1")

        analyzer = LLMAnalyzer(provider=provider, batch_size=1)

        logger.info(f" LLMAnalyzer initialized successfully")
        logger.info(f"   - Analyzer provider: {analyzer.provider}")
        logger.info(f"   - Analyzer provider type: {type(analyzer.provider)}")

        # LOG 5: Call analyze_tweet
        logger.info(f"🧪 Step 4: Calling analyzer.analyze_tweet()")
        logger.info(f"   - Tweet to analyze: {test_tweet.tweet_id}")

        result = await analyzer.analyze_tweet(test_tweet)

        logger.info(f"🧪 Step 5: analyze_tweet() returned")
        logger.info(f"   - Result type: {type(result)}")
        logger.info(f"   - Result is None: {result is None}")

        if result:
            logger.info(f" Analysis successful!")
            logger.info(f"   - Sentiment: {result.sentiment.value}")
            logger.info(f"   - Category: {result.category.value}")
            logger.info(f"   - Priority: {result.priority.value}")
            logger.info(f"   - Keywords: {result.keywords}")
            logger.info(f"   - Is urgent: {result.is_urgent}")
            logger.info(f"   - Needs response: {result.needs_response}")
            logger.info("=" * 80)

            return {
                "success": True,
                "result": {
                    "sentiment": result.sentiment.value,
                    "category": result.category.value,
                    "priority": result.priority.value,
                    "keywords": result.keywords,
                    "is_urgent": result.is_urgent,
                    "needs_response": result.needs_response
                }
            }
        else:
            logger.warning(f" Analysis returned None")
            logger.warning(f"   - This means the LLM call failed or returned invalid data")
            logger.warning(f"   - Check the logs above for Ollama API errors")
            logger.info("=" * 80)

            return {
                "success": False,
                "error": "Analysis returned None"
            }

    except Exception as e:
        logger.error("=" * 80)
        logger.error(f" EXCEPTION in /test-analyze-single")
        logger.error(f"   - Exception type: {type(e).__name__}")
        logger.error(f"   - Exception message: {str(e)}")
        logger.error(f"   - Full traceback:", exc_info=True)
        logger.error("=" * 80)

        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }

# File upload endpoint
@app.post("/upload-csv", response_model=AnalysisResponse)
async def upload_csv(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    llm_provider: str = Form(default=None),
    max_tweets: int = Form(default=500),
    batch_size: int = Form(default=10),
    user_role: str = Form(default="agent")
):
    """
    Upload CSV file and start analysis with comprehensive validation

    Args:
        file: CSV file with tweet data
        analysis_request: Analysis configuration

    Returns:
        Analysis response with batch ID
    """
    try:
        # Use environment variable if llm_provider not specified
        if llm_provider is None:
            llm_provider = os.getenv("LLM_PROVIDER", "mistral")
            logger.info(f"Using LLM provider from environment: {llm_provider}")

        # Comprehensive file validation
        if not file.filename:
            raise ValidationError("Filename is required")

        # Check file extension BEFORE sanitization
        original_filename = file.filename.lower()
        if not original_filename.endswith('.csv'):
            raise ValidationError("Only CSV files are supported")

        # Sanitize filename while preserving extension
        safe_filename = DataValidator.sanitize_filename(file.filename)

        # Check file size (limit to 50MB as per config)
        max_size = 50 * 1024 * 1024  # 50MB
        
        # Read file content in chunks to avoid memory issues
        content = await file.read()
        logger.info(f"File read: {len(content)} bytes")

        if len(content) > max_size:
            raise ValidationError(f"File too large. Maximum size is {max_size // (1024*1024)}MB")

        if len(content) == 0:
            raise ValidationError("File is empty")
        
        # Quick validation: just check if it's likely a CSV (basic check)
        # Don't do full CSV parsing here - that's done in background
        try:
            # Check first 1000 bytes for CSV-like content
            sample = content[:1000].decode('utf-8', errors='ignore')
            if ',' not in sample and '\t' not in sample:
                raise ValidationError("File does not appear to be a valid CSV")
        except Exception as decode_error:
            # Try other encodings
            try:
                sample = content[:1000].decode('latin-1', errors='ignore')
                if ',' not in sample and '\t' not in sample:
                    raise ValidationError("File does not appear to be a valid CSV")
            except:
                raise ValidationError("Unable to read file content. Please ensure it's a valid CSV file.")

        # Validate analysis request parameters
        DataValidator.validate_batch_size(batch_size)

        if max_tweets < 1 or max_tweets > config.performance.max_tweets_per_run:
            raise ValidationError(f"max_tweets must be between 1 and {config.performance.max_tweets_per_run}")

        # Save uploaded file securely (fast write)
        upload_dir = config.upload_dir
        upload_dir.mkdir(parents=True, exist_ok=True)

        temp_file_path = upload_dir / f"upload_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}_{safe_filename}"
        
        # Write file efficiently
        logger.info(f"Writing file to {temp_file_path}")
        with open(temp_file_path, 'wb') as f:
            f.write(content)
        logger.info(f"File written successfully ({len(content)} bytes)")

        # Generate batch ID
        batch_id = f"batch_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"Generated batch ID: {batch_id}")

        # Start background analysis (non-blocking)
        background_tasks.add_task(
            process_csv_analysis,
            str(temp_file_path),
            batch_id,
            llm_provider,
            max_tweets,
            batch_size,
            user_role
        )

        logger.info(f" CSV upload successful: {safe_filename}, batch_id: {batch_id}")
        logger.info(f" Background analysis task queued for {max_tweets} tweets")

        # Return immediately - analysis runs in background
        return AnalysisResponse(
            success=True,
            message="File uploaded successfully. Analysis started in background.",
            batch_id=batch_id
        )
        
    except ValidationError as ve:
        # Re-raise ValidationError to be handled by validation_exception_handler
        logger.warning(f"Validation error during CSV upload: {ve.message}")
        raise ve
        
    except Exception as e:
        logger.error(f"Error uploading CSV: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_csv_analysis(file_path: str, batch_id: str, llm_provider: str, max_tweets: int, batch_size: int, user_role: str):
    """
    Background task for processing CSV analysis

    Args:
        file_path: Path to uploaded CSV file
        batch_id: Unique batch identifier
        llm_provider: LLM provider to use
        max_tweets: Maximum number of tweets to analyze
        batch_size: Batch size for processing
        user_role: User role for analysis
    """
    start_time = datetime.now(UTC)

    try:
        logger.info(f" Starting analysis for batch {batch_id}")
        logger.info(f"📋 Configuration: provider={llm_provider}, max_tweets={max_tweets}, batch_size={batch_size}")

        # Load and clean CSV
        tweets_raw = csv_processor.load_and_clean_csv(file_path)
        logger.info(f"Loaded {len(tweets_raw)} tweets from CSV")

        # Limit tweets if specified
        if max_tweets and len(tweets_raw) > max_tweets:
            tweets_raw = tweets_raw[:max_tweets]
            logger.info(f"Limited to {len(tweets_raw)} tweets")

        # Initialize LLM analyzer
        logger.info(f" Initializing LLMAnalyzer with provider: {llm_provider}")
        llm_analyzer = LLMAnalyzer(
            provider=llm_provider,
            batch_size=batch_size
        )
        logger.info(f" LLMAnalyzer initialized successfully")
        
        # Analyze tweets
        analyzed_tweets = await llm_analyzer.analyze_batch(tweets_raw)

        # Store results in database
        saved_count = await db_manager.save_analyzed_tweets(analyzed_tweets, batch_id)
        logger.info(f"Saved {saved_count} analyzed tweets to database")
        
        # Calculate processing time
        end_time = datetime.now(UTC)
        processing_time = (end_time - start_time).total_seconds()
        
        # Get analysis stats
        stats = llm_analyzer.get_analysis_stats()
        
        # Create analysis log
        analysis_log = AnalysisLog(
            batch_id=batch_id,
            total_tweets=len(tweets_raw),
            successful_analysis=len(analyzed_tweets),
            failed_analysis=len(tweets_raw) - len(analyzed_tweets),
            llm_provider=llm_provider,
            total_cost=stats.get('total_cost', 0.0),
            processing_time=processing_time
        )
        
        # Save analysis log to database
        await db_manager.save_analysis_log(analysis_log)

        logger.info(f"Analysis completed for batch {batch_id}: {len(analyzed_tweets)} tweets analyzed")
        
    except Exception as e:
        logger.error(f"Error in background analysis for batch {batch_id}: {e}")
        
        # Create error log
        error_log = AnalysisLog(
            batch_id=batch_id,
            total_tweets=0,
            successful_analysis=0,
            failed_analysis=0,
            llm_provider=llm_provider,
            total_cost=0.0,
            processing_time=0.0
        )
        # Save error log to database
        await db_manager.save_analysis_log(error_log)
        
    finally:
        # Clean up temporary file
        try:
            os.unlink(file_path)
        except:
            pass

@app.get("/analysis-status/{batch_id}")
async def get_analysis_status(batch_id: str):
    """
    Get analysis status for a batch

    Args:
        batch_id: Batch identifier

    Returns:
        Analysis status and progress
    """
    try:
        # Get analysis log from database
        logs = await db_manager.get_analysis_logs(limit=100)
        analysis_log = next((log for log in logs if log.get('batch_id') == batch_id), None)

        if not analysis_log:
            raise HTTPException(status_code=404, detail="Batch not found")

        # Check if analysis is complete by querying tweets
        tweets = await db_manager.get_tweets(limit=1, filters={'batch_id': batch_id}) if hasattr(db_manager, 'get_tweets_by_batch') else []
        is_complete = len(tweets) > 0
        analyzed_count = analysis_log.get('successful_analysis', 0)
    
        return {
            "batch_id": batch_id,
            "status": "completed" if is_complete else "processing",
            "total_tweets": analysis_log.get('total_tweets', 0),
            "analyzed_tweets": analyzed_count,
            "failed_tweets": analysis_log.get('failed_analysis', 0),
            "llm_provider": analysis_log.get('llm_provider', 'unknown'),
            "processing_time": analysis_log.get('processing_time', 0.0),
            "estimated_cost": analysis_log.get('total_cost', 0.0),
            "created_at": analysis_log.get('created_at')
        }
    except Exception as e:
        logger.error(f"Error getting analysis status: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving analysis status: {str(e)}")

@app.get("/kpis/{batch_id}", response_model=KPIResponse)
async def get_kpis(batch_id: str, user_role: UserRole = UserRole.AGENT):
    """
    Get KPIs for analyzed tweets

    Args:
        batch_id: Batch identifier
        user_role: User role for filtering metrics

    Returns:
        KPI metrics and insights
    """
    try:
        # Get tweets from database
        tweet_dicts = await db_manager.get_tweets_by_batch(batch_id)

        if not tweet_dicts:
            raise HTTPException(status_code=404, detail="Analysis not found or not completed")

        # Convert dict tweets back to TweetAnalyzed objects
        tweets = []
        for tweet_dict in tweet_dicts:
            try:
                # Handle JSON fields
                import json
                if isinstance(tweet_dict.get('mentions'), str):
                    tweet_dict['mentions'] = json.loads(tweet_dict['mentions'])
                if isinstance(tweet_dict.get('hashtags'), str):
                    tweet_dict['hashtags'] = json.loads(tweet_dict['hashtags'])
                if isinstance(tweet_dict.get('urls'), str):
                    tweet_dict['urls'] = json.loads(tweet_dict['urls'])
                if isinstance(tweet_dict.get('keywords'), str):
                    tweet_dict['keywords'] = json.loads(tweet_dict['keywords'])

                tweet = TweetAnalyzed(**tweet_dict)
                tweets.append(tweet)
            except Exception as e:
                logger.warning(f"Error converting tweet dict to TweetAnalyzed: {e}")
                continue

        if not tweets:
            raise HTTPException(status_code=400, detail="No valid analyzed tweets found")

        # Calculate KPIs
        kpis = kpi_calculator.calculate_metrics(tweets)
        advanced_metrics = kpi_calculator.calculate_advanced_metrics(tweets)
        insights = kpi_calculator.generate_insights(tweets)

        # Filter metrics based on user role
        dashboard_config = DEFAULT_DASHBOARD_CONFIGS.get(user_role)
        if dashboard_config and not dashboard_config.can_filter_all:
            # Filter advanced metrics for restricted roles
            filtered_advanced = {
                key: value for key, value in advanced_metrics.items()
                if key in ['sentiment_statistics', 'top_keywords']
            }
            advanced_metrics = filtered_advanced

        return KPIResponse(
            kpis=kpis,
            advanced_metrics=advanced_metrics,
            insights=insights,
            generated_at=datetime.now(UTC)
        )

    except Exception as e:
        logger.error(f"Error retrieving tweets for KPIs: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving analysis data: {str(e)}")

@app.get("/tweets/{batch_id}")
async def get_analyzed_tweets(
    batch_id: str,
    limit: int = 100,
    offset: int = 0,
    sentiment: Optional[str] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    urgent_only: bool = False
):
    """
    Get analyzed tweets with filtering
    
    Args:
        batch_id: Batch identifier
        limit: Maximum number of tweets to return
        offset: Number of tweets to skip
        sentiment: Filter by sentiment
        category: Filter by category
        priority: Filter by priority
        urgent_only: Show only urgent tweets
        
    Returns:
        Filtered list of analyzed tweets
    """
    try:
        # Get tweets from database
        tweet_dicts = await db_manager.get_tweets_by_batch(batch_id)

        if not tweet_dicts:
            raise HTTPException(status_code=404, detail="Analysis not found")

        # Convert to TweetAnalyzed objects
        tweets = []
        for tweet_dict in tweet_dicts:
            try:
                # Handle JSON fields
                import json
                if isinstance(tweet_dict.get('mentions'), str):
                    tweet_dict['mentions'] = json.loads(tweet_dict['mentions'])
                if isinstance(tweet_dict.get('hashtags'), str):
                    tweet_dict['hashtags'] = json.loads(tweet_dict['hashtags'])
                if isinstance(tweet_dict.get('urls'), str):
                    tweet_dict['urls'] = json.loads(tweet_dict['urls'])
                if isinstance(tweet_dict.get('keywords'), str):
                    tweet_dict['keywords'] = json.loads(tweet_dict['keywords'])

                tweet = TweetAnalyzed(**tweet_dict)
                tweets.append(tweet)
            except Exception as e:
                logger.warning(f"Error converting tweet dict: {e}")
                continue

        # Apply filters
        filtered_tweets = tweets

        if sentiment:
            filtered_tweets = [t for t in filtered_tweets if t.sentiment.value == sentiment]

        if category:
            filtered_tweets = [t for t in filtered_tweets if t.category.value == category]

        if priority:
            filtered_tweets = [t for t in filtered_tweets if t.priority.value == priority]

        if urgent_only:
            filtered_tweets = [t for t in filtered_tweets if t.is_urgent]

        # Apply pagination
        total_count = len(filtered_tweets)
        paginated_tweets = filtered_tweets[offset:offset + limit]

        return {
            "tweets": paginated_tweets,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total_count
        }

    except Exception as e:
        logger.error(f"Error retrieving tweets: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving tweets: {str(e)}")

@app.get("/dashboard-config/{user_role}")
async def get_dashboard_config(user_role: UserRole):
    """
    Get dashboard configuration for user role
    
    Args:
        user_role: User role
        
    Returns:
        Dashboard configuration
    """
    config = DEFAULT_DASHBOARD_CONFIGS.get(user_role)
    if not config:
        raise HTTPException(status_code=404, detail="Role configuration not found")
    
    return config

@app.get("/analysis-logs")
async def get_analysis_logs(limit: int = 50):
    """
    Get analysis logs

    Args:
        limit: Maximum number of logs to return

    Returns:
        List of analysis logs
    """
    try:
        logs = await db_manager.get_analysis_logs(limit=limit)
        return logs
    except Exception as e:
        logger.error(f"Error retrieving analysis logs: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving analysis logs: {str(e)}")

@app.delete("/analysis/{batch_id}")
async def delete_analysis(batch_id: str):
    """
    Delete analysis results

    Args:
        batch_id: Batch identifier

    Returns:
        Deletion confirmation
    """
    try:
        # Check if analysis exists
        logs = await db_manager.get_analysis_logs(limit=100)
        analysis_log = next((log for log in logs if log.get('batch_id') == batch_id), None)

        if not analysis_log:
            raise HTTPException(status_code=404, detail="Analysis not found")

        # Delete tweets and analysis log from database
        deleted_count = await db_manager.delete_analysis(batch_id)

        return {"message": f"Analysis {batch_id} deleted successfully", "deleted_tweets": deleted_count}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting analysis: {str(e)}")

# CHATBOT SAV ENDPOINTS - Endpoints pour le chatbot SAV intelligent

# Modèles Pydantic pour les requêtes API
class ChatMessageRequest(BaseModel):
    """Requête pour envoyer un message au chatbot"""
    message: str = Field(min_length=1, max_length=4000, description="Message de l'utilisateur")
    conversation_id: Optional[str] = Field(None, description="ID de conversation existante")
    session_id: str = Field(description="ID de session utilisateur")
    llm_provider: str = Field(default="mistral", description="Fournisseur LLM à utiliser")
    user_id: Optional[str] = Field(None, description="ID utilisateur (optionnel)")

class ChatMessageResponse(BaseModel):
    """Réponse du chatbot"""
    success: bool
    response: Optional[str] = None
    conversation_id: str
    message_id: Optional[str] = None
    sources: List[str] = Field(default_factory=list)
    processing_time: float
    llm_provider: str
    intent_detected: Optional[str] = None
    documents_found: int = 0
    error: Optional[str] = None

class FeedbackRequest(BaseModel):
    """Requête pour enregistrer un feedback"""
    conversation_id: str
    message_id: str
    feedback_type: FeedbackType
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=1000)
    session_id: str

# Initialiser le service chatbot
chatbot_service = ChatbotService(db_manager=db_manager)

@app.post("/api/chatbot/message", response_model=ChatMessageResponse)
async def send_message(request: ChatMessageRequest):
    """
    Envoyer un message au chatbot et recevoir une réponse

    Args:
        request: Requête contenant le message et les métadonnées

    Returns:
        Réponse du chatbot avec sources et métadonnées
    """
    try:
        logger.info(f"💬 Nouveau message chatbot: '{request.message[:50]}...'")

        # Générer un ID de conversation si nécessaire
        conversation_id = request.conversation_id or f"conv_{request.session_id}_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"

        # Traiter le message avec le service chatbot
        result = await chatbot_service.process_message(
            message=request.message,
            conversation_id=conversation_id,
            llm_provider=request.llm_provider,
            conversation_history=await db_manager.get_conversation_messages(conversation_id, limit=10)
        )

        # Créer la réponse
        response = ChatMessageResponse(
            success=result['success'],
            response=result.get('response'),
            conversation_id=conversation_id,
            message_id=result.get('message_id'),
            sources=result.get('sources', []),
            processing_time=result.get('processing_time', 0.0),
            llm_provider=result.get('llm_provider', request.llm_provider),
            intent_detected=result.get('intent_detected'),
            documents_found=result.get('documents_found', 0),
            error=result.get('error')
        )

        logger.info(f" Réponse générée en {result.get('processing_time', 0):.2f}s")
        return response

    except Exception as e:
        logger.error(f" Erreur lors du traitement du message: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du traitement du message: {str(e)}"
        )

@app.get("/api/chatbot/conversations/{user_id}")
async def get_user_conversations(user_id: str, limit: int = 20):
    """
    Récupérer l'historique des conversations d'un utilisateur

    Args:
        user_id: ID de l'utilisateur
        limit: Nombre maximum de conversations à retourner

    Returns:
        Liste des conversations
    """
    try:
        # Récupérer les conversations depuis la base de données
        logger.info(f"📋 Récupération des conversations pour l'utilisateur: {user_id}")

        conversations = await db_manager.get_conversations_by_user(user_id=user_id, limit=20)

        return {
            "success": True,
            "conversations": conversations,
            "total": len(conversations),
            "user_id": user_id
        }

    except Exception as e:
        logger.error(f" Erreur lors de la récupération des conversations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des conversations: {str(e)}"
        )

@app.delete("/api/chatbot/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """
    Supprimer une conversation

    Args:
        conversation_id: ID de la conversation à supprimer

    Returns:
        Confirmation de suppression
    """
    try:
        # Marquer la conversation comme supprimée dans la base de données
        logger.info(f"🗑 Suppression de la conversation: {conversation_id}")

        # Mettre à jour le statut de la conversation à 'deleted'
        try:
            async with db_manager.get_connection() as conn:
                result = await conn.execute("""
                    UPDATE conversations
                    SET status = 'deleted', updated_at = CURRENT_TIMESTAMP
                    WHERE id = $1
                """, conversation_id)
                success = result == "UPDATE 1"
        except Exception as db_error:
            logger.error(f"Erreur lors de la suppression de la conversation: {db_error}")
            success = False

        return {
            "success": success,
            "message": f"Conversation {conversation_id} {'supprimée' if success else 'non trouvée'} avec succès",
            "conversation_id": conversation_id
        }

    except Exception as e:
        logger.error(f" Erreur lors de la suppression: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la suppression: {str(e)}"
        )

@app.post("/api/chatbot/feedback")
async def submit_feedback(request: FeedbackRequest):
    """
    Enregistrer le feedback utilisateur sur une réponse

    Args:
        request: Feedback de l'utilisateur

    Returns:
        Confirmation d'enregistrement
    """
    try:
        logger.info(f" Nouveau feedback: {request.feedback_type} pour message {request.message_id}")

        # Stocker le feedback dans la base de données
        feedback_data = {
            'conversation_id': request.conversation_id,
            'message_id': request.message_id,
            'feedback_type': request.feedback_type.value,
            'rating': request.rating,
            'comment': request.comment,
            'session_id': request.session_id,
            'user_id': None,  # Pas d'authentification pour l'instant
            'llm_provider_used': None,  # À récupérer du message si nécessaire
            'sources_used': [],  # À récupérer du message si nécessaire
            'response_time': None
        }

        feedback_id = await db_manager.store_feedback(feedback_data)
        success = feedback_id is not None

        return {
            "success": success,
            "message": "Feedback enregistré avec succès" if success else "Erreur lors de l'enregistrement",
            "feedback_id": feedback_id or f"feedback_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}",
            "conversation_id": request.conversation_id,
            "message_id": request.message_id
        }

    except Exception as e:
        logger.error(f" Erreur lors de l'enregistrement du feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'enregistrement du feedback: {str(e)}"
        )

@app.post("/api/chatbot/initialize")
async def initialize_chatbot():
    """
    Initialiser la base de connaissances du chatbot

    Returns:
        Résultat de l'initialisation
    """
    try:
        logger.info(" Initialisation de la base de connaissances du chatbot")

        result = await chatbot_service.initialize_knowledge_base()

        if result['success']:
            logger.info(" Base de connaissances initialisée avec succès")
        else:
            logger.error(f" Échec de l'initialisation: {result.get('error')}")

        return result

    except Exception as e:
        logger.error(f" Erreur lors de l'initialisation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'initialisation: {str(e)}"
        )

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "timestamp": datetime.now(UTC).isoformat()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "timestamp": datetime.now(UTC).isoformat()}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("DEBUG_MODE", "false").lower() == "true"
    )
