# 🚀 GPU Training Guide for FreeMobilaChat

Complete guide to set up and run GPU-accelerated LLM fine-tuning on your RTX 4060.

## 📋 Prerequisites

### Hardware Requirements
- **GPU**: NVIDIA RTX 4060 (8GB VRAM) ✅
- **RAM**: 32GB (31.7GB usable) ✅
- **CPU**: Intel i9-13900H ✅
- **OS**: Windows 64-bit ✅

### Software Requirements
- Python 3.8+ (3.10 or 3.11 recommended)
- NVIDIA Drivers (latest)
- CUDA Toolkit 12.1
- cuDNN 8.9+

## 🔧 Phase 1: GPU Setup (1-2 hours)

### Step 1: Install NVIDIA Drivers
```powershell
# Download latest drivers from:
# https://www.nvidia.com/drivers
# Or use GeForce Experience for automatic updates
```

### Step 2: Install CUDA Toolkit 12.1
```powershell
# Download from: https://developer.nvidia.com/cuda-12-1-0-download-archive
# Choose: Windows > x86_64 > 11 > exe (local)
# Install with default settings
```

### Step 3: Install cuDNN 8.9
```powershell
# Download from: https://developer.nvidia.com/cudnn (requires NVIDIA account)
# Extract to C:\tools\cuda
# Add to PATH: C:\tools\cuda\bin
```

### Step 4: Verify Installation
```powershell
# Check CUDA
nvcc --version

# Check GPU
nvidia-smi
```

## 🐍 Phase 2: Python Environment Setup (30 minutes)

### Step 1: Run Automated Setup
```powershell
cd backend
python setup_gpu_training.py
```

### Step 2: Manual Installation (if automated setup fails)
```powershell
# Install PyTorch with CUDA 12.1
pip install torch==2.1.2+cu121 torchvision==0.16.2+cu121 torchaudio==2.1.2+cu121 --index-url https://download.pytorch.org/whl/cu121

# Install training dependencies
pip install transformers==4.36.2 peft==0.7.1 bitsandbytes==0.41.3 accelerate==0.25.0 datasets==2.16.1 evaluate==0.4.1 tensorboard==2.15.1 gpustat==1.1.1
```

### Step 3: Verify GPU Detection
```python
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"
```

## ⚙️ Phase 3: Configuration (15 minutes)

### Step 1: Copy GPU Training Configuration
```powershell
# Copy settings from backend/.env.gpu_training to your main .env file
# Or load the GPU training config file directly
```

### Step 2: Key Configuration for RTX 4060
```env
# Model Selection (choose one)
TRAINING_MODEL_NAME=camembert-base              # Recommended: Fast training, good results
# TRAINING_MODEL_NAME=mistralai/Mistral-7B-v0.1  # Advanced: Better quality, slower

# Memory Optimization
USE_QUANTIZATION=true
QUANTIZATION_BITS=4
USE_LORA=true
LORA_R=16
LORA_ALPHA=32

# Training Settings
LEARNING_RATE=2e-5
NUM_EPOCHS=3
TRAINING_BATCH_SIZE=2
GRADIENT_ACCUMULATION_STEPS=4
USE_MIXED_PRECISION=true
USE_GRADIENT_CHECKPOINTING=true
```

## 🏋️ Phase 4: Training (1-4 hours depending on model)

### Step 1: Check System Readiness
```powershell
cd backend
python train_gpu_model.py --check-only
```

### Step 2: Start Training
```powershell
# Basic training with CamemBERT (recommended first run)
python train_gpu_model.py

# Advanced training with Mistral-7B
python train_gpu_model.py --model mistralai/Mistral-7B-v0.1

# Custom output directory
python train_gpu_model.py --output ./models/my_custom_model
```

### Step 3: Monitor Training
```powershell
# Watch GPU usage
gpustat -i 1

# Monitor training logs
tensorboard --logdir ./models/fine_tuned/logs
```

## 📊 Expected Performance

### Training Times on RTX 4060
| Model | Parameters | Training Time | VRAM Usage |
|-------|------------|---------------|------------|
| CamemBERT | 110M | 30-60 min | ~3GB |
| Mistral-7B + QLoRA | 7B | 2-4 hours | ~7GB |

### Memory Usage Optimization
- **4-bit Quantization**: Reduces memory by ~75%
- **LoRA**: Only trains 0.1-1% of parameters
- **Gradient Checkpointing**: Trades compute for memory
- **Mixed Precision**: 2x speed improvement

## 🔍 Phase 5: Testing and Evaluation

### Step 1: Test Trained Model
```python
from app.services.model_training import GPUModelTrainer

trainer = GPUModelTrainer()
# Load and test your trained model
```

### Step 2: Compare Performance
```powershell
# Compare fine-tuned model vs API models
python compare_models.py
```

## 🚨 Troubleshooting

### Common Issues

#### CUDA Out of Memory
```
RuntimeError: CUDA out of memory
```
**Solutions:**
- Reduce `TRAINING_BATCH_SIZE` to 1
- Increase `GRADIENT_ACCUMULATION_STEPS` to 8
- Enable `USE_GRADIENT_CHECKPOINTING=true`
- Use smaller model (CamemBERT instead of Mistral-7B)

#### CUDA Not Detected
```
CUDA available: False
```
**Solutions:**
- Reinstall NVIDIA drivers
- Verify CUDA Toolkit installation
- Check PyTorch CUDA version compatibility

#### Slow Training
**Optimizations:**
- Enable `USE_MIXED_PRECISION=true`
- Increase `TRAINING_BATCH_SIZE` if memory allows
- Use `DATALOADER_NUM_WORKERS=2` (but 0 for Windows)

## 📈 Advanced Configurations

### For Maximum Quality (Mistral-7B)
```env
TRAINING_MODEL_NAME=mistralai/Mistral-7B-v0.1
USE_QUANTIZATION=true
QUANTIZATION_BITS=4
USE_LORA=true
LORA_R=64
LORA_ALPHA=128
TRAINING_BATCH_SIZE=1
GRADIENT_ACCUMULATION_STEPS=8
NUM_EPOCHS=5
```

### For Maximum Speed (CamemBERT)
```env
TRAINING_MODEL_NAME=camembert-base
USE_QUANTIZATION=false
USE_LORA=false
TRAINING_BATCH_SIZE=4
GRADIENT_ACCUMULATION_STEPS=2
NUM_EPOCHS=3
LEARNING_RATE=5e-5
```

## 🎯 Next Steps

1. **Integrate with API**: Modify `llm_analyzer.py` to use your fine-tuned model
2. **Deploy**: Set up model serving with FastAPI
3. **Monitor**: Track performance vs API models
4. **Iterate**: Collect more data and retrain

## 📞 Support

If you encounter issues:
1. Check the training logs: `training.log`
2. Monitor GPU usage: `gpustat`
3. Verify configuration: `python train_gpu_model.py --check-only`

## 🏆 Expected Results

After successful training, you should have:
- ✅ Fine-tuned model optimized for French customer service tweets
- ✅ Better accuracy than generic pre-trained models
- ✅ Faster inference (no API calls)
- ✅ Complete control over model behavior
- ✅ Cost savings (no API fees)

**Estimated improvement**: 10-20% better accuracy on your specific dataset compared to generic API models.
