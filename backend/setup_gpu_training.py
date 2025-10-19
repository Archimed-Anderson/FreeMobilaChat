#!/usr/bin/env python3
"""
GPU Training Setup Script for FreeMobilaChat
Installs dependencies and verifies GPU setup for local LLM fine-tuning
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def run_command(command, description=""):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ SUCCESS")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ FAILED: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check Python version compatibility"""
    print("\n🐍 Checking Python version...")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major != 3 or version.minor < 8:
        print("❌ Python 3.8+ required for GPU training")
        return False
    
    print("✅ Python version compatible")
    return True

def check_cuda_installation():
    """Check CUDA installation"""
    print("\n🚀 Checking CUDA installation...")
    
    try:
        result = subprocess.run("nvcc --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ CUDA Toolkit found")
            print(result.stdout)
            return True
        else:
            print("❌ CUDA Toolkit not found")
            return False
    except:
        print("❌ CUDA Toolkit not found")
        return False

def check_gpu_availability():
    """Check GPU availability"""
    print("\n🎮 Checking GPU availability...")
    
    try:
        result = subprocess.run("nvidia-smi", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ NVIDIA GPU detected")
            print(result.stdout)
            return True
        else:
            print("❌ NVIDIA GPU not detected")
            return False
    except:
        print("❌ nvidia-smi not found")
        return False

def install_pytorch_cuda():
    """Install PyTorch with CUDA support"""
    print("\n🔥 Installing PyTorch with CUDA support...")
    
    # PyTorch with CUDA 12.1 support
    pytorch_command = (
        "pip install torch==2.1.2+cu121 torchvision==0.16.2+cu121 torchaudio==2.1.2+cu121 "
        "--index-url https://download.pytorch.org/whl/cu121"
    )
    
    return run_command(pytorch_command, "Installing PyTorch with CUDA 12.1")

def install_training_dependencies():
    """Install training dependencies"""
    print("\n📦 Installing training dependencies...")
    
    dependencies = [
        "transformers==4.36.2",
        "peft==0.7.1",
        "bitsandbytes==0.41.3",
        "accelerate==0.25.0",
        "datasets==2.16.1",
        "evaluate==0.4.1",
        "tensorboard==2.15.1",
        "gpustat==1.1.1",
        "tqdm==4.66.1"
    ]
    
    for dep in dependencies:
        success = run_command(f"pip install {dep}", f"Installing {dep}")
        if not success:
            print(f"⚠️ Failed to install {dep}, continuing...")

def install_optional_dependencies():
    """Install optional monitoring dependencies"""
    print("\n📊 Installing optional monitoring dependencies...")
    
    optional_deps = [
        "wandb==0.16.1",  # For experiment tracking
        "matplotlib==3.8.2",  # For plotting
        "seaborn==0.13.0"  # For advanced plotting
    ]
    
    for dep in optional_deps:
        success = run_command(f"pip install {dep}", f"Installing {dep} (optional)")
        if not success:
            print(f"⚠️ Failed to install {dep} (optional), continuing...")

def verify_installation():
    """Verify the installation"""
    print("\n🔍 Verifying installation...")
    
    verification_script = '''
import torch
import transformers
import peft
import bitsandbytes
import accelerate

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"GPU count: {torch.cuda.device_count()}")
    for i in range(torch.cuda.device_count()):
        print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
        props = torch.cuda.get_device_properties(i)
        print(f"  Memory: {props.total_memory / 1024**3:.1f} GB")

print(f"Transformers version: {transformers.__version__}")
print(f"PEFT version: {peft.__version__}")
print(f"Accelerate version: {accelerate.__version__}")

print("\\n✅ All dependencies installed successfully!")
'''
    
    try:
        exec(verification_script)
        return True
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def create_training_directories():
    """Create necessary directories for training"""
    print("\n📁 Creating training directories...")
    
    directories = [
        "models/fine_tuned",
        "cache/huggingface",
        "data/results",
        "logs/training"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {dir_path}")

def main():
    """Main setup function"""
    print("🚀 FreeMobilaChat GPU Training Setup")
    print("=" * 60)
    print("This script will set up your environment for GPU-accelerated LLM fine-tuning")
    print("Designed for RTX 4060 with 8GB VRAM")
    print("=" * 60)
    
    # System checks
    if not check_python_version():
        print("\n❌ Setup failed: Python version incompatible")
        return False
    
    if not check_cuda_installation():
        print("\n⚠️ CUDA not found. Please install CUDA Toolkit 12.1 first:")
        print("https://developer.nvidia.com/cuda-12-1-0-download-archive")
        return False
    
    if not check_gpu_availability():
        print("\n⚠️ GPU not detected. Training will use CPU (very slow)")
    
    # Install dependencies
    print("\n🔧 Installing dependencies...")
    
    if not install_pytorch_cuda():
        print("\n❌ Failed to install PyTorch with CUDA")
        return False
    
    install_training_dependencies()
    install_optional_dependencies()
    
    # Verify installation
    if not verify_installation():
        print("\n❌ Installation verification failed")
        return False
    
    # Create directories
    create_training_directories()
    
    # Final instructions
    print("\n" + "=" * 60)
    print("🎉 GPU Training Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Copy settings from backend/.env.gpu_training to your .env file")
    print("2. Run: python -c \"from app.services.model_training import GPUModelTrainer; trainer = GPUModelTrainer(); print(trainer.check_gpu_memory())\"")
    print("3. Start training: python backend/train_gpu_model.py")
    print("\nFor RTX 4060 (8GB VRAM), recommended settings:")
    print("- Model: camembert-base (fast) or mistralai/Mistral-7B-v0.1 (better quality)")
    print("- Use quantization + LoRA for memory efficiency")
    print("- Batch size: 1-2, Gradient accumulation: 4-8")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
