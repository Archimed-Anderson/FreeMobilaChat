# Deployment Guide

This guide provides step-by-step instructions for deploying FreeMobilaChat on Streamlit Cloud and Vercel.

## Prerequisites

- GitHub repository with the latest code
- Streamlit Cloud account
- Vercel account
- API keys for LLM services (Mistral, OpenAI)

## Streamlit Cloud Deployment

### 1. Connect Repository

1. Go to [Streamlit Cloud](https://share.streamlit.io/)
2. Click "New app"
3. Connect your GitHub repository
4. Select the repository: `Archimed-Anderson/FreeMobilaChat`

### 2. Configure App Settings

**Main file path:** `streamlit_app/app.py`

**App URL:** `https://freemobilachat.streamlit.app`

### 3. Environment Variables

Add the following secrets in Streamlit Cloud:

```
[api]
backend_url = "https://freemobilachat-backend.vercel.app"

[llm]
mistral_api_key = "your-mistral-api-key"
openai_api_key = "your-openai-api-key"

[database]
database_url = "sqlite:///./data/freemobilachat.db"

[app]
environment = "production"
log_level = "INFO"
```

### 4. Deploy

Click "Deploy!" and wait for the deployment to complete.

## Vercel Deployment

### 1. Backend Deployment

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository
4. Configure the project:
   - **Framework Preset:** Other
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements-vercel.txt`
   - **Output Directory:** Leave empty

### 2. Environment Variables

Add the following environment variables in Vercel:

```
DATABASE_URL=sqlite:///./data/freemobilachat.db
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
MISTRAL_API_KEY=your-mistral-api-key
OPENAI_API_KEY=your-openai-api-key
```

### 3. Deploy

Click "Deploy" and wait for the deployment to complete.

### 4. Frontend Deployment (Alternative)

For the Streamlit frontend on Vercel:

1. Create a new Vercel project
2. Configure:
   - **Framework Preset:** Other
   - **Root Directory:** `streamlit_app`
   - **Build Command:** `pip install -r requirements.txt`
   - **Output Directory:** Leave empty

## Post-Deployment Configuration

### 1. Update Backend URL

After deploying the backend on Vercel, update the `backend_url` in Streamlit Cloud secrets to point to your Vercel backend URL.

### 2. Test Deployments

1. **Streamlit Cloud:** Visit your Streamlit app URL
2. **Vercel Backend:** Visit `https://your-project.vercel.app/docs` for API documentation
3. **Integration:** Test the connection between frontend and backend

### 3. Custom Domains (Optional)

- **Streamlit Cloud:** Configure custom domain in Streamlit Cloud settings
- **Vercel:** Configure custom domain in Vercel project settings

## Monitoring and Maintenance

### 1. Logs

- **Streamlit Cloud:** View logs in the Streamlit Cloud dashboard
- **Vercel:** View logs in the Vercel dashboard

### 2. Updates

- Push changes to the main branch
- Deployments will automatically update
- Monitor for any deployment errors

### 3. Performance

- Monitor response times
- Check for memory usage
- Optimize if necessary

## Troubleshooting

### Common Issues

1. **Import Errors:** Check Python path configuration
2. **API Connection:** Verify backend URL in secrets
3. **Memory Issues:** Optimize dependencies
4. **Timeout Errors:** Increase function timeout in Vercel

### Support

- Check deployment logs
- Verify environment variables
- Test locally before deploying
- Contact support if issues persist

## URLs

After successful deployment, you should have:

- **Frontend (Streamlit):** `https://freemobilachat.streamlit.app`
- **Backend (Vercel):** `https://freemobilachat-backend.vercel.app`
- **API Documentation:** `https://freemobilachat-backend.vercel.app/docs`

## Security Notes

- Keep API keys secure
- Use environment variables for sensitive data
- Enable CORS properly
- Monitor for security vulnerabilities
- Regular updates and patches
