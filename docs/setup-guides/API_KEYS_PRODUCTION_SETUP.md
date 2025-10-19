# 🔑 Production API Keys Setup Guide

## Overview
This guide walks you through configuring real API keys for the FreeMobilaChat application in production.

## 🚨 Security Warning
- **NEVER** commit API keys to version control
- Use environment variables or secure key management systems
- Rotate keys regularly (monthly recommended)
- Monitor API usage and set billing alerts
- Use least-privilege access when possible

## 📋 Required API Keys

### 1. Mistral AI (Required)
**Purpose**: Primary LLM provider for tweet analysis
**Cost**: ~$0.25 per 1M input tokens, ~$0.25 per 1M output tokens

**Setup Steps**:
1. Visit https://console.mistral.ai/
2. Create an account or sign in
3. Navigate to "API Keys" section
4. Click "Create new key"
5. Name it "FreeMobilaChat-Production"
6. Copy the key (starts with `mistral-...`)

**Configuration**:
```env
MISTRAL_API_KEY=mistral-your-actual-key-here
MISTRAL_MODEL=mistral-small-latest
MISTRAL_RATE_LIMIT=30
```

### 2. OpenAI (Optional)
**Purpose**: Alternative LLM provider
**Cost**: ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens

**Setup Steps**:
1. Visit https://platform.openai.com/
2. Create an account or sign in
3. Navigate to "API Keys"
4. Click "Create new secret key"
5. Name it "FreeMobilaChat-Production"
6. Copy the key (starts with `sk-...`)

**Configuration**:
```env
OPENAI_API_KEY=sk-your-actual-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_RATE_LIMIT=60
```

### 3. Anthropic Claude (Optional)
**Purpose**: Alternative LLM provider
**Cost**: ~$0.25 per 1M input tokens, ~$1.25 per 1M output tokens

**Setup Steps**:
1. Visit https://console.anthropic.com/
2. Create an account or sign in
3. Navigate to "API Keys"
4. Click "Create Key"
5. Name it "FreeMobilaChat-Production"
6. Copy the key (starts with `sk-ant-...`)

**Configuration**:
```env
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
ANTHROPIC_MODEL=claude-3-haiku-20240307
ANTHROPIC_RATE_LIMIT=50
```

## 🔧 Configuration Process

### Step 1: Update .env.production
```bash
# Edit the production environment file
nano .env.production

# Or use the setup script
.\api_keys_setup.ps1 -Help
```

### Step 2: Test API Keys
```powershell
# Test all configured API keys
.\api_keys_setup.ps1 -TestKeys

# Expected output:
# API Key Test Results:
# =====================
# Mistral : ✅ Valid
# OpenAI : ✅ Valid  
# Anthropic : ✅ Valid
```

### Step 3: Restart Backend
```bash
# Restart backend to load new keys
docker-compose restart backend

# Verify backend is healthy
docker-compose ps
```

### Step 4: Test LLM Functionality
```powershell
# Upload test CSV to verify LLM analysis works
.\test_upload.ps1

# Check analysis results
docker exec freemobilachat_postgres psql -U mobilachat_user -d freemobilachat_prod -c "SELECT * FROM analysis_logs ORDER BY created_at DESC LIMIT 1;"
```

## 💰 Cost Management

### Estimated Monthly Costs (1000 tweets/day)
- **Mistral Small**: ~$15-25/month
- **OpenAI GPT-4o-mini**: ~$20-35/month  
- **Anthropic Claude Haiku**: ~$25-40/month

### Cost Optimization Tips
1. Use smaller models for initial analysis
2. Implement caching for repeated queries
3. Set up billing alerts
4. Monitor token usage regularly
5. Use batch processing to reduce API calls

## 🔒 Security Best Practices

### Environment Variables
```bash
# Set as environment variables (recommended)
export MISTRAL_API_KEY="your-key-here"
export OPENAI_API_KEY="your-key-here"
export ANTHROPIC_API_KEY="your-key-here"
```

### Key Rotation Schedule
- **Monthly**: Rotate all API keys
- **Immediately**: If key is compromised
- **Quarterly**: Review and audit key usage

### Monitoring
- Set up billing alerts at 80% of budget
- Monitor unusual usage patterns
- Log all API calls for audit trail
- Implement rate limiting and quotas

## 🚨 Troubleshooting

### Common Issues
1. **"Invalid API Key"**: Check key format and expiration
2. **"Rate Limit Exceeded"**: Increase delays or upgrade plan
3. **"Insufficient Credits"**: Add billing information
4. **"Model Not Found"**: Update model name in config

### Debug Commands
```powershell
# Check backend logs
docker-compose logs backend --tail=50

# Test individual API
curl -H "Authorization: Bearer YOUR_KEY" https://api.mistral.ai/v1/models

# Verify environment variables
docker exec freemobilachat_backend env | grep API_KEY
```

## 📞 Support
- Mistral AI: https://docs.mistral.ai/
- OpenAI: https://help.openai.com/
- Anthropic: https://support.anthropic.com/

---
**Last Updated**: October 12, 2025
**Version**: 1.0.0
