"""
Configuration management for FreeMobilaChat application
Centralized configuration with validation and type safety
"""

import os
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path
from dotenv import load_dotenv

from .exceptions import ConfigurationError

# Configure logger first
logger = logging.getLogger(__name__)

# Load environment variables from .env file
# Support custom environment file via ENVIRONMENT_FILE variable
env_file = os.getenv('ENVIRONMENT_FILE', '.env')
if os.path.exists(env_file):
    load_dotenv(env_file)
    print(f"Loaded environment from: {env_file}")  # Use print since logger may not be configured yet
else:
    load_dotenv()  # Load default .env if exists


class Environment(str, Enum):
    """Application environments"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class DatabaseType(str, Enum):
    """Supported database types"""
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    MISTRAL = "mistral"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


@dataclass
class LLMConfig:
    """LLM provider configuration"""
    api_key: Optional[str]
    model: str
    max_tokens: int
    temperature: float
    rate_limit: int
    base_url: Optional[str] = None


@dataclass
class DatabaseConfig:
    """Database configuration"""
    type: DatabaseType
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    ssl_mode: Optional[str] = None
    sqlite_path: Optional[str] = None


@dataclass
class PerformanceConfig:
    """Performance and rate limiting configuration"""
    max_requests_per_minute: int
    max_concurrent_requests: int
    batch_processing_delay: float
    request_timeout_seconds: int
    default_batch_size: int
    max_tweets_per_batch: int
    max_tweets_per_run: int


@dataclass
class GPUTrainingConfig:
    """GPU training configuration for local fine-tuning"""
    # Model settings
    model_name: str
    use_quantization: bool
    quantization_bits: int
    use_lora: bool
    lora_r: int
    lora_alpha: int
    lora_dropout: float

    # Training hyperparameters
    learning_rate: float
    num_epochs: int
    batch_size: int
    gradient_accumulation_steps: int
    warmup_steps: int
    weight_decay: float
    max_grad_norm: float

    # Memory optimization
    use_gradient_checkpointing: bool
    use_mixed_precision: bool
    dataloader_num_workers: int

    # Monitoring
    eval_steps: int
    save_steps: int
    logging_steps: int
    early_stopping_patience: int

    # Paths
    output_dir: str
    cache_dir: str


@dataclass
class SecurityConfig:
    """Security configuration"""
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    allowed_origins: List[str]
    allowed_methods: List[str]
    allowed_headers: List[str]


class Config:
    """Centralized configuration management"""
    
    def __init__(self):
        self.environment = Environment(os.getenv("ENVIRONMENT", "development"))
        self.debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # Load configurations
        self.llm = self._load_llm_config()
        self.database = self._load_database_config()
        self.performance = self._load_performance_config()
        self.security = self._load_security_config()
        self.gpu_training = self._load_gpu_training_config()
        
        # Application settings
        self.app_name = os.getenv("APP_NAME", "FreeMobilaChat Tweet Analysis")
        self.app_version = os.getenv("APP_VERSION", "1.0.0")
        
        # File processing
        self.data_raw_dir = Path(os.getenv("DATA_RAW_DIR", "./data/raw"))
        self.data_processed_dir = Path(os.getenv("DATA_PROCESSED_DIR", "./data/processed"))
        self.upload_dir = Path(os.getenv("UPLOAD_DIR", "./uploads"))
        
        # Validate configuration
        self._validate_config()
    
    def _load_llm_config(self) -> Dict[str, LLMConfig]:
        """Load LLM provider configurations"""
        configs = {}
        
        # Mistral configuration
        configs["mistral"] = LLMConfig(
            api_key=os.getenv("MISTRAL_API_KEY"),
            model=os.getenv("MISTRAL_MODEL", "mistral-small-latest"),
            max_tokens=int(os.getenv("MISTRAL_MAX_TOKENS", "400")),
            temperature=float(os.getenv("MISTRAL_TEMPERATURE", "0.2")),
            rate_limit=int(os.getenv("MISTRAL_RATE_LIMIT", "30")),
            base_url=os.getenv("MISTRAL_BASE_URL", "https://api.mistral.ai/v1")
        )
        
        # OpenAI configuration
        configs["openai"] = LLMConfig(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "400")),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.2")),
            rate_limit=int(os.getenv("OPENAI_RATE_LIMIT", "60"))
        )
        
        # Anthropic configuration
        configs["anthropic"] = LLMConfig(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307"),
            max_tokens=int(os.getenv("ANTHROPIC_MAX_TOKENS", "400")),
            temperature=float(os.getenv("ANTHROPIC_TEMPERATURE", "0.2")),
            rate_limit=int(os.getenv("ANTHROPIC_RATE_LIMIT", "50"))
        )
        
        # Ollama configuration
        configs["ollama"] = LLMConfig(
            api_key=os.getenv("OLLAMA_API_KEY"),
            model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
            max_tokens=int(os.getenv("OLLAMA_MAX_TOKENS", "400")),
            temperature=float(os.getenv("OLLAMA_TEMPERATURE", "0.2")),
            rate_limit=int(os.getenv("OLLAMA_RATE_LIMIT", "20")),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        )
        
        return configs
    
    def _load_database_config(self) -> DatabaseConfig:
        """Load database configuration"""
        db_type = DatabaseType(os.getenv("DATABASE_TYPE", "sqlite"))
        
        if db_type == DatabaseType.POSTGRESQL:
            return DatabaseConfig(
                type=db_type,
                host=os.getenv("POSTGRES_HOST", "localhost"),
                port=int(os.getenv("POSTGRES_PORT", "5432")),
                database=os.getenv("POSTGRES_DB", "freemobilachatdb"),
                username=os.getenv("POSTGRES_USER", "mobilatchat"),
                password=os.getenv("POSTGRES_PASSWORD"),
                ssl_mode=os.getenv("POSTGRES_SSL_MODE", "prefer")
            )
        else:
            return DatabaseConfig(
                type=db_type,
                sqlite_path=os.getenv("SQLITE_DATABASE_PATH", "./data/tweets_analysis.db")
            )
    
    def _load_performance_config(self) -> PerformanceConfig:
        """Load performance configuration"""
        return PerformanceConfig(
            max_requests_per_minute=int(os.getenv("MAX_REQUESTS_PER_MINUTE", "30")),
            max_concurrent_requests=int(os.getenv("MAX_CONCURRENT_REQUESTS", "5")),
            batch_processing_delay=float(os.getenv("BATCH_PROCESSING_DELAY", "2")),
            request_timeout_seconds=int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30")),
            default_batch_size=int(os.getenv("DEFAULT_BATCH_SIZE", "10")),
            max_tweets_per_batch=int(os.getenv("MAX_TWEETS_PER_BATCH", "50")),
            max_tweets_per_run=int(os.getenv("MAX_TWEETS_PER_RUN", "1000"))
        )
    
    def _load_security_config(self) -> SecurityConfig:
        """Load security configuration"""
        return SecurityConfig(
            secret_key=os.getenv("SECRET_KEY", "change-this-in-production"),
            algorithm=os.getenv("ALGORITHM", "HS256"),
            access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
            allowed_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:8501").split(","),
            allowed_methods=os.getenv("ALLOWED_METHODS", "GET,POST,PUT,DELETE,OPTIONS").split(","),
            allowed_headers=os.getenv("ALLOWED_HEADERS", "*").split(",")
        )

    def _load_gpu_training_config(self) -> GPUTrainingConfig:
        """Load GPU training configuration"""
        return GPUTrainingConfig(
            # Model settings
            model_name=os.getenv("TRAINING_MODEL_NAME", "camembert-base"),
            use_quantization=os.getenv("USE_QUANTIZATION", "true").lower() == "true",
            quantization_bits=int(os.getenv("QUANTIZATION_BITS", "4")),
            use_lora=os.getenv("USE_LORA", "true").lower() == "true",
            lora_r=int(os.getenv("LORA_R", "16")),
            lora_alpha=int(os.getenv("LORA_ALPHA", "32")),
            lora_dropout=float(os.getenv("LORA_DROPOUT", "0.1")),

            # Training hyperparameters
            learning_rate=float(os.getenv("LEARNING_RATE", "2e-5")),
            num_epochs=int(os.getenv("NUM_EPOCHS", "3")),
            batch_size=int(os.getenv("TRAINING_BATCH_SIZE", "2")),
            gradient_accumulation_steps=int(os.getenv("GRADIENT_ACCUMULATION_STEPS", "4")),
            warmup_steps=int(os.getenv("WARMUP_STEPS", "100")),
            weight_decay=float(os.getenv("WEIGHT_DECAY", "0.01")),
            max_grad_norm=float(os.getenv("MAX_GRAD_NORM", "1.0")),

            # Memory optimization
            use_gradient_checkpointing=os.getenv("USE_GRADIENT_CHECKPOINTING", "true").lower() == "true",
            use_mixed_precision=os.getenv("USE_MIXED_PRECISION", "true").lower() == "true",
            dataloader_num_workers=int(os.getenv("DATALOADER_NUM_WORKERS", "0")),

            # Monitoring
            eval_steps=int(os.getenv("EVAL_STEPS", "100")),
            save_steps=int(os.getenv("SAVE_STEPS", "500")),
            logging_steps=int(os.getenv("LOGGING_STEPS", "10")),
            early_stopping_patience=int(os.getenv("EARLY_STOPPING_PATIENCE", "3")),

            # Paths
            output_dir=os.getenv("TRAINING_OUTPUT_DIR", "./models/fine_tuned"),
            cache_dir=os.getenv("TRAINING_CACHE_DIR", "./cache/huggingface")
        )

    def _validate_config(self) -> None:
        """Validate configuration"""
        errors = []

        # Check if at least one LLM provider is configured
        # Ollama doesn't require API key if base_url is configured
        configured_providers = [
            name for name, config in self.llm.items()
            if config.api_key is not None or (name == "ollama" and config.base_url)
        ]

        if not configured_providers:
            errors.append("No LLM providers are configured (need API key or Ollama base_url)")
        
        # Validate database configuration
        if self.database.type == DatabaseType.POSTGRESQL:
            if not all([self.database.host, self.database.database, 
                       self.database.username, self.database.password]):
                errors.append("PostgreSQL configuration is incomplete")
        
        # Validate security
        if self.security.secret_key == "change-this-in-production" and self.environment == Environment.PRODUCTION:
            errors.append("Secret key must be changed in production")
        
        if errors:
            raise ConfigurationError(f"Configuration validation failed: {'; '.join(errors)}")
        
        logger.info(f"Configuration loaded successfully for {self.environment} environment")
        logger.info(f"Configured LLM providers: {configured_providers}")
    
    def get_default_llm_provider(self) -> str:
        """Get the default LLM provider"""
        # Use LLM_PROVIDER instead of DEFAULT_LLM_PROVIDER
        default = os.getenv("LLM_PROVIDER", "mistral")

        # Check if the default provider is configured
        if default in self.llm:
            config = self.llm[default]
            # Ollama is configured if it has a base_url, others need api_key
            if default == "ollama" and config.base_url:
                logger.info(f"✅ Using configured provider: {default} (Ollama with base_url)")
                return default
            elif config.api_key:
                logger.info(f"✅ Using configured provider: {default} (with API key)")
                return default

        # Fall back to first configured provider
        for name, config in self.llm.items():
            # Ollama is configured if it has a base_url
            if name == "ollama" and config.base_url:
                logger.warning(f"Default provider {default} not configured, using {name} (Ollama)")
                return name
            elif config.api_key:
                logger.warning(f"Default provider {default} not configured, using {name}")
                return name

        raise ConfigurationError("No LLM providers are configured")


# Global configuration instance
config = Config()
