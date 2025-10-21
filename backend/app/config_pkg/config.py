"""
Configuration module for FreeMobilaChat
Provides default configuration values for the application
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class GPUTrainingConfig:
    """Configuration for GPU training"""
    
    # Model configuration
    model_name: str = "camembert-base"
    cache_dir: str = "./models/cache"
    output_dir: str = "./models/trained"
    
    # Training hyperparameters
    num_epochs: int = 3
    batch_size: int = 8
    learning_rate: float = 2e-5
    weight_decay: float = 0.01
    warmup_steps: int = 500
    max_grad_norm: float = 1.0
    
    # Optimization
    gradient_accumulation_steps: int = 4
    use_mixed_precision: bool = True
    use_gradient_checkpointing: bool = True
    dataloader_num_workers: int = 4
    
    # LoRA configuration
    use_lora: bool = True
    lora_r: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.1
    
    # Quantization
    use_quantization: bool = False
    
    # Evaluation and logging
    eval_steps: int = 100
    save_steps: int = 100
    logging_steps: int = 50
    early_stopping_patience: int = 3

@dataclass
class DatabaseConfig:
    """Configuration for database"""
    
    database_type: str = field(default_factory=lambda: os.getenv("DATABASE_TYPE", "postgresql"))
    postgres_host: str = field(default_factory=lambda: os.getenv("POSTGRES_HOST", "localhost"))
    postgres_port: int = field(default_factory=lambda: int(os.getenv("POSTGRES_PORT", "5432")))
    postgres_db: str = field(default_factory=lambda: os.getenv("POSTGRES_DB", "freemobilachat"))
    postgres_user: str = field(default_factory=lambda: os.getenv("POSTGRES_USER", "postgres"))
    postgres_password: str = field(default_factory=lambda: os.getenv("POSTGRES_PASSWORD", ""))

@dataclass
class LLMConfig:
    """Configuration for LLM providers"""
    
    provider: str = field(default_factory=lambda: os.getenv("LLM_PROVIDER", "ollama"))
    ollama_base_url: str = field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434"))
    mistral_api_key: Optional[str] = field(default_factory=lambda: os.getenv("MISTRAL_API_KEY"))

@dataclass
class AppConfig:
    """Main application configuration"""
    
    # Sub-configurations
    gpu_training: GPUTrainingConfig = field(default_factory=GPUTrainingConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    
    # Application settings
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    
    # Paths
    data_dir: Path = Path("data")
    models_dir: Path = Path("models")
    logs_dir: Path = Path("logs")

# Global configuration instance
config = AppConfig()

