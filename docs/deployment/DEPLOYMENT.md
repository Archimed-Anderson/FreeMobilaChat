# FreeMobilaChat Production Deployment Guide

This guide provides comprehensive instructions for deploying FreeMobilaChat in a production environment.

## 📋 Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+ recommended), macOS, or Windows with WSL2
- **Memory**: Minimum 4GB RAM, 8GB+ recommended
- **Storage**: Minimum 20GB free space
- **CPU**: 2+ cores recommended

### Required Software
- **Docker**: Version 20.10+ and Docker Compose V2
- **Git**: For cloning the repository
- **Python**: 3.11+ (if running without Docker)
- **PostgreSQL**: 13+ (if running without Docker)

### Optional Software
- **Nginx**: For reverse proxy (if not using Docker)
- **Redis**: For advanced caching (optional)

## 🚀 Quick Start with Docker (Recommended)

### 1. Clone and Setup
```bash
# Clone the repository
git clone <repository-url>
cd FreeMobilaChat

# Copy environment template
cp .env.example .env.production

# Edit environment variables (see Configuration section)
nano .env.production
```

### 2. Configure Environment Variables
Edit `.env.production` with your actual values:

```bash
# Required: Database password
POSTGRES_PASSWORD=your_secure_database_password_here

# Required: Secret key (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY=your_secret_key_here

# Required: LLM API key (choose one provider)
MISTRAL_API_KEY=your_mistral_api_key_here
# OR
OPENAI_API_KEY=your_openai_api_key_here
# OR
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional: Update CORS origins for your domain
CORS_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]
```

### 3. Deploy with Docker Compose
```bash
# Build and start all services
docker-compose --env-file .env.production up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Initialize Database
```bash
# The database will be automatically initialized on first startup
# Check initialization logs
docker-compose logs backend | grep "Database initialized"
```

### 5. Verify Deployment
```bash
# Check backend health
curl http://localhost/api/health

# Check frontend (open in browser)
open http://localhost
```

## 🔧 Manual Deployment (Without Docker)

### 1. Database Setup
```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE freemobilachat_prod;
CREATE USER mobilachat_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE freemobilachat_prod TO mobilachat_user;
\q

# Initialize database schema
psql -U mobilachat_user -d freemobilachat_prod -f init-db.sql
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export $(cat ../.env.production | xargs)

# Start production server
python start_production.py
```

### 3. Frontend Setup
```bash
cd frontend

# Install Streamlit (if not in backend venv)
pip install streamlit

# Set API base URL
export API_BASE_URL=http://localhost:8000

# Start Streamlit
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

### 4. Nginx Setup (Optional)
```bash
# Install Nginx
sudo apt install nginx

# Copy configuration
sudo cp nginx.conf /etc/nginx/sites-available/freemobilachat
sudo ln -s /etc/nginx/sites-available/freemobilachat /etc/nginx/sites-enabled/

# Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

## ⚙️ Configuration Guide

### Environment Variables

#### Required Variables
- `POSTGRES_PASSWORD`: Database password
- `SECRET_KEY`: Application secret key
- `MISTRAL_API_KEY` or `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`: LLM provider API key

#### Important Optional Variables
- `CORS_ORIGINS`: Allowed frontend domains
- `MAX_FILE_SIZE_MB`: Maximum CSV file size (default: 200MB)
- `WORKERS`: Number of Gunicorn workers (default: 4)
- `LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING, ERROR)

### LLM Provider Configuration

#### Mistral AI (Recommended)
```bash
DEFAULT_LLM_PROVIDER=mistral
MISTRAL_API_KEY=your_api_key
MISTRAL_MODEL=mistral-large-latest
```

#### OpenAI
```bash
DEFAULT_LLM_PROVIDER=openai
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-4-turbo-preview
```

#### Anthropic Claude
```bash
DEFAULT_LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_api_key
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

#### Local Ollama
```bash
DEFAULT_LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
```

## 🔍 Health Checks and Monitoring

### Health Check Endpoints
- **Backend**: `http://localhost/api/health`
- **Database**: `http://localhost/api/database/info`
- **Nginx Status**: `http://localhost:8080/nginx_status`

### Monitoring Commands
```bash
# Check all services
docker-compose ps

# View real-time logs
docker-compose logs -f

# Check resource usage
docker stats

# Check database connection
docker-compose exec backend python -c "
from app.utils.database import get_database_manager
import asyncio
async def test():
    db = get_database_manager()
    await db.initialize_database()
    print('Database connection successful')
asyncio.run(test())
"
```

### Log Files
- **Backend logs**: `./logs/freemobilachat.log`
- **Nginx logs**: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`
- **PostgreSQL logs**: Check with `docker-compose logs postgres`

## 🧪 Testing the Deployment

### 1. Basic Functionality Test
```bash
# Test file upload
curl -X POST "http://localhost/api/upload-csv" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_data.csv" \
  -F "user_role=manager" \
  -F "llm_provider=mistral"

# Check analysis status (replace BATCH_ID with actual ID from upload response)
curl "http://localhost/api/analysis-status/BATCH_ID"

# Get KPIs (after analysis completes)
curl "http://localhost/api/kpis/BATCH_ID?user_role=manager"
```

### 2. Frontend Test
1. Open `http://localhost` in your browser
2. Upload a CSV file with tweet data
3. Wait for analysis to complete
4. View the results and KPIs

### 3. Load Testing (Optional)
```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test API endpoint
ab -n 100 -c 10 http://localhost/api/health
```

## 🔒 Security Considerations

### SSL/TLS Setup
1. Obtain SSL certificates (Let's Encrypt recommended)
2. Update `nginx.conf` to enable HTTPS
3. Update `CORS_ORIGINS` to use HTTPS URLs

### Firewall Configuration
```bash
# Allow only necessary ports
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### Database Security
- Use strong passwords
- Enable PostgreSQL SSL
- Restrict database access to application servers only
- Regular security updates

## 📊 Performance Optimization

### Database Optimization
```sql
-- Create additional indexes for better performance
CREATE INDEX CONCURRENTLY idx_tweets_composite ON tweets (sentiment, priority, is_urgent);
CREATE INDEX CONCURRENTLY idx_tweets_date_range ON tweets (date) WHERE date >= NOW() - INTERVAL '30 days';
```

### Application Optimization
- Increase worker count based on CPU cores
- Enable Redis for caching (optional)
- Configure connection pooling
- Monitor memory usage and adjust limits

## 🔄 Backup and Recovery

### Database Backup
```bash
# Create backup
docker-compose exec postgres pg_dump -U mobilachat_user freemobilachat_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
docker-compose exec -T postgres psql -U mobilachat_user freemobilachat_prod < backup_file.sql
```

### Application Data Backup
```bash
# Backup uploaded files and logs
tar -czf app_data_backup_$(date +%Y%m%d_%H%M%S).tar.gz uploads/ logs/
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Database Connection Failed
```bash
# Check PostgreSQL status
docker-compose logs postgres

# Verify credentials
docker-compose exec postgres psql -U mobilachat_user -d freemobilachat_prod -c "SELECT 1;"
```

#### 2. LLM API Errors
```bash
# Check API key configuration
docker-compose exec backend python -c "
import os
print('Mistral API Key:', os.getenv('MISTRAL_API_KEY', 'Not set'))
print('OpenAI API Key:', os.getenv('OPENAI_API_KEY', 'Not set'))
"

# Test API connection
curl -H "Authorization: Bearer YOUR_API_KEY" https://api.mistral.ai/v1/models
```

#### 3. File Upload Issues
- Check `MAX_FILE_SIZE_MB` setting
- Verify `uploads/` directory permissions
- Check Nginx client_max_body_size

#### 4. Frontend Not Loading
```bash
# Check Streamlit logs
docker-compose logs frontend

# Verify API connectivity from frontend
docker-compose exec frontend curl http://backend:8000/health
```

### Getting Help
- Check application logs: `docker-compose logs -f`
- Review error messages in browser console
- Verify environment variable configuration
- Check network connectivity between services

## 📈 Scaling Considerations

### Horizontal Scaling
- Use multiple backend instances behind load balancer
- Implement Redis for shared session storage
- Use external PostgreSQL cluster
- Consider container orchestration (Kubernetes)

### Vertical Scaling
- Increase worker count
- Allocate more memory to containers
- Use faster storage (SSD)
- Optimize database queries

## 🔄 Updates and Maintenance

### Application Updates
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose build
docker-compose up -d
```

### Database Migrations
```bash
# Run database migrations (if any)
docker-compose exec backend python -c "
from app.utils.database import get_database_manager
import asyncio
asyncio.run(get_database_manager().initialize_database())
"
```

### Regular Maintenance
- Monitor disk space and logs
- Update dependencies regularly
- Review and rotate API keys
- Backup database regularly
- Monitor performance metrics

---

## 📝 Service Management Commands

### Docker Compose Commands
```bash
# Start all services
docker-compose --env-file .env.production up -d

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart backend

# View service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Scale backend service
docker-compose up -d --scale backend=3

# Update and restart services
docker-compose pull
docker-compose up -d

# Clean up unused resources
docker system prune -f
```

### Systemd Service (Alternative to Docker)
Create `/etc/systemd/system/freemobilachat.service`:
```ini
[Unit]
Description=FreeMobilaChat Backend
After=network.target postgresql.service

[Service]
Type=exec
User=mobilachat
Group=mobilachat
WorkingDirectory=/opt/freemobilachat/backend
Environment=PATH=/opt/freemobilachat/backend/venv/bin
EnvironmentFile=/opt/freemobilachat/.env.production
ExecStart=/opt/freemobilachat/backend/venv/bin/python start_production.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable freemobilachat
sudo systemctl start freemobilachat
sudo systemctl status freemobilachat
```

## 🔐 Production Security Checklist

### Before Going Live
- [ ] Change all default passwords
- [ ] Generate secure SECRET_KEY
- [ ] Configure proper CORS origins
- [ ] Enable HTTPS with valid SSL certificates
- [ ] Set up firewall rules
- [ ] Disable debug endpoints (`ENABLE_DEBUG_ENDPOINTS=false`)
- [ ] Configure rate limiting
- [ ] Set up monitoring and alerting
- [ ] Create backup strategy
- [ ] Review and secure database access
- [ ] Update all dependencies to latest versions

### Ongoing Security
- [ ] Regular security updates
- [ ] Monitor access logs
- [ ] Rotate API keys periodically
- [ ] Review user access and permissions
- [ ] Monitor for suspicious activity
- [ ] Keep backups secure and tested

## 📊 Performance Benchmarks

### Expected Performance (4 CPU, 8GB RAM)
- **File Upload**: 200MB CSV in ~30 seconds
- **Tweet Analysis**: 1000 tweets in ~2-5 minutes (depending on LLM provider)
- **API Response Time**: <200ms for most endpoints
- **Concurrent Users**: 50+ simultaneous users
- **Database Queries**: <50ms for typical queries

### Optimization Tips
- Use SSD storage for database
- Enable PostgreSQL query caching
- Configure appropriate worker counts
- Monitor memory usage and adjust limits
- Use CDN for static assets (if applicable)

For additional support or questions, please refer to the project documentation or create an issue in the repository.
