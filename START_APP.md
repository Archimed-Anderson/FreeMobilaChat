# FreeMobilaChat - Manual Startup Guide

## 🚀 Quick Start Commands

### Windows (PowerShell)

#### 1. Start Application (Recommended)
```powershell
cd c:\Users\ander\Desktop\FreeMobilaChat
streamlit run streamlit_app/app.py --server.port 8502 --server.headless false
```

#### 2. Start with Cache Clearing (Fresh Start)
```powershell
# Stop existing processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Clear Streamlit cache
Remove-Item -Path "$env:USERPROFILE\.streamlit\cache" -Recurse -Force -ErrorAction SilentlyContinue

# Start application
cd c:\Users\ander\Desktop\FreeMobilaChat
streamlit run streamlit_app/app.py --server.port 8502 --server.headless false
```

#### 3. Background Mode (Production-like)
```powershell
cd c:\Users\ander\Desktop\FreeMobilaChat
Start-Process powershell -ArgumentList "-NoExit", "-Command", "streamlit run streamlit_app/app.py --server.port 8502"
```

---

## 🔧 Configuration Options

### Server Configuration
```powershell
streamlit run streamlit_app/app.py `
  --server.port 8502 `
  --server.headless false `
  --server.enableCORS true `
  --server.maxUploadSize 500
```

### Available Parameters:
- `--server.port` - Port number (default: 8501, recommended: 8502)
- `--server.headless` - Run without browser (true/false)
- `--server.enableCORS` - Enable CORS (true for local dev)
- `--server.maxUploadSize` - Max file upload size in MB

---

## 🛠️ Prerequisites

### 1. Python Environment
Ensure Python 3.12+ is installed and virtual environment activated:
```powershell
# Check Python version
python --version

# Activate virtual environment (if exists)
.\venv\Scripts\Activate.ps1
```

### 2. Dependencies Installed
```powershell
pip install -r requirements.txt
```

### 3. Ollama Server Running (Optional for LLM features)
```powershell
# Check if Ollama is running
curl http://127.0.0.1:11434/api/tags

# Start Ollama if needed
ollama serve
```

---

## 🌐 Access URLs

After starting the application, access it at:

- **Local Development:** http://localhost:8502
- **Network Access:** http://YOUR_IP:8502

### Default Credentials
- **Username:** admin
- **Password:** admin123

---

## 🧪 Testing & Validation

### Run Unit Tests
```powershell
cd c:\Users\ander\Desktop\FreeMobilaChat
python -m pytest tests/test_unit_preprocessing.py -v
```

### Run Playwright Validation
```powershell
python tests/test_html_validation_playwright.py
```

### Run Full Test Suite
```powershell
python -m pytest tests/ -v --tb=short --maxfail=5
```

---

## 🐛 Troubleshooting

### Port Already in Use
```powershell
# Stop existing Python processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Or use different port
streamlit run streamlit_app/app.py --server.port 8503
```

### Cache Issues
```powershell
# Clear all Streamlit cache
Remove-Item -Path "$env:USERPROFILE\.streamlit\cache" -Recurse -Force -ErrorAction SilentlyContinue
streamlit cache clear
```

### Module Import Errors
```powershell
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Database Connection Issues
```powershell
# Check if database files exist
ls streamlit_app/data/

# Reset database (if needed)
Remove-Item streamlit_app/data/freemobilachat.db -ErrorAction SilentlyContinue
```

---

## 📊 Application Status Check

### Verify App is Running
```powershell
# Check if port is listening
netstat -ano | findstr :8502

# Access health endpoint (if available)
curl http://localhost:8502
```

### View Logs
Logs are displayed in the terminal where Streamlit is running. Look for:
- ✅ `You can now view your Streamlit app in your browser`
- ✅ `INFO:httpx:HTTP Request: GET http://127.0.0.1:11434/api/tags`
- ⚠️ Any ERROR or WARNING messages

---

## 🔄 Restart Application

### Graceful Restart
```powershell
# In terminal running Streamlit, press: Ctrl + C
# Then restart:
streamlit run streamlit_app/app.py --server.port 8502
```

### Force Restart
```powershell
# Stop all Python processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Wait 2 seconds
Start-Sleep -Seconds 2

# Restart
cd c:\Users\ander\Desktop\FreeMobilaChat
streamlit run streamlit_app/app.py --server.port 8502 --server.headless false
```

---

## 📦 Production Deployment (Streamlit Cloud)

The application is also deployed on Streamlit Cloud:
- **URL:** https://freemobilachat-eozajommltzwhq6duedkct.streamlit.app
- **Configuration:** Automatically uses `streamlit_app/.streamlit/config.toml`
- **Auto-deploys:** On push to `main` branch

### Key Differences (Local vs Cloud):
| Setting | Local | Cloud |
|---------|-------|-------|
| Port | 8502 | 8501 |
| Headless | false | true |
| Address | localhost | 0.0.0.0 |
| CORS | true | false |

---

## 🎯 Feature-Specific Startup

### Classification with LLM (Ollama)
1. Start Ollama server first:
   ```powershell
   ollama serve
   ```

2. Pull required model:
   ```powershell
   ollama pull mistral
   ```

3. Start application:
   ```powershell
   streamlit run streamlit_app/app.py --server.port 8502
   ```

### Classification without LLM (Fallback Mode)
The app automatically falls back to rule-based classification if Ollama is unavailable.

---

## ✅ Verification Checklist

Before considering the app "running", verify:

- [ ] No error messages in terminal
- [ ] URL `http://localhost:8502` accessible in browser
- [ ] Login page loads correctly
- [ ] Can authenticate with default credentials
- [ ] Classification pages load without errors
- [ ] File upload works (test with CSV)
- [ ] Ollama connection successful (if using LLM)

---

## 📞 Support

For issues or questions:
- Check logs in terminal
- Review error messages in browser console (F12)
- Run validation tests to identify issues
- Check GitHub Issues: https://github.com/Archimed-Anderson-ChatbotRNCP/FreeMobilaChat/issues

---

**Last Updated:** 2025-11-11  
**Application Version:** 4.5  
**Streamlit Version:** 1.41  
**Python Version:** 3.12+
