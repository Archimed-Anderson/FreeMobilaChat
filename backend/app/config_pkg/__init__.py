"""
Configuration package for FreeMobilaChat
"""

# Export GPU training config for model_training.py
from .config import config as gpu_config, AppConfig, GPUTrainingConfig, DatabaseConfig, LLMConfig
from .fast_graphrag_config import FastGraphRAGConfig, get_config

# For backward compatibility, also export gpu_config as config
config = gpu_config

__all__ = [
    'config',
    'gpu_config',
    'AppConfig',
    'GPUTrainingConfig',
    'DatabaseConfig',
    'LLMConfig',
    'FastGraphRAGConfig',
    'get_config'
]
