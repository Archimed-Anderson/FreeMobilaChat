# FreeMobilaChat Production Deployment Guide

This comprehensive guide covers all aspects of deploying FreeMobilaChat in a production environment.

## 📋 Table of Contents

1. [API Keys Configuration](#1-api-keys-configuration)
2. [SSL/TLS Setup](#2-ssltls-setup)
3. [Backup Strategy](#3-backup-strategy)
4. [Scaling Configuration](#4-scaling-configuration)
5. [Monitoring and Alerting](#5-monitoring-and-alerting)
6. [Security Considerations](#6-security-considerations)
7. [Maintenance Procedures](#7-maintenance-procedures)

---

## 1. API Keys Configuration

### Overview
FreeMobilaChat requires at least one LLM provider API key to function. Multiple providers can be configured for redundancy.

### Required API Keys
- **MISTRAL_API_KEY** (Required): Primary LLM provider
- **SECRET_KEY** (Required): JWT token encryption
- **POSTGRES_PASSWORD** (Required): Database security

### Optional API Keys
- **OPENAI_API_KEY**: Alternative LLM provider
- **ANTHROPIC_API_KEY**: Alternative LLM provider
- **TWILIO_ACCOUNT_SID/AUTH_TOKEN**: SMS alerts
- **SMTP credentials**: Email alerts

### Setup Process

1. **Generate Secure Secrets**:
```powershell
.\api_keys_setup.ps1 -GenerateSecrets
```

2. **Configure API Keys**:
```powershell
# Copy template and edit
Copy-Item .env.production.template .env.production
# Edit .env.production with your API keys
```

3. **Test Configuration**:
```powershell
.\api_keys_setup.ps1 -TestKeys
```

### Security Best Practices
- Never commit API keys to version control
- Rotate keys every 90 days
- Use environment variables in production
- Monitor API usage and costs
- Implement rate limiting

---

## 2. SSL/TLS Setup

### Overview
HTTPS is essential for production deployment to secure data transmission and meet security standards.

### Certificate Options
1. **Self-Signed** (Development/Testing)
2. **Let's Encrypt** (Free, Production)
3. **Commercial Certificates** (Enterprise)

### Setup Process

1. **Generate SSL Certificate**:
```powershell
# For development/testing
.\simple_ssl_setup.ps1

# For production with real domain
.\ssl_setup.ps1 -LetsEncrypt -Domain yourdomain.com
```

2. **Update Configuration**:
- Nginx configuration automatically updated
- Docker Compose volumes configured
- HTTPS redirect enabled

3. **Test SSL Setup**:
```powershell
# Restart services
docker-compose down
docker-compose up -d

# Test endpoints
curl -k https://localhost:8443/api/health
```

### SSL Certificate Renewal
- **Let's Encrypt**: Auto-renewal with cron job
- **Commercial**: Manual renewal before expiration
- **Self-Signed**: Regenerate as needed

---

## 3. Backup Strategy

### Overview
Automated database backups with retention policy and optional cloud storage integration.

### Backup Types
- **Daily**: Automatic at 2:00 AM
- **Weekly**: Every Sunday at 3:00 AM
- **Monthly**: First Sunday at 4:00 AM

### Setup Process

1. **Test Backup System**:
```powershell
.\backup_system.ps1 -Test
```

2. **Create Manual Backup**:
```powershell
.\backup_system.ps1
```

3. **Setup Automated Schedule**:
```powershell
# Run as Administrator
.\setup_backup_schedule.ps1
```

4. **Test Restore Process**:
```powershell
.\backup_system.ps1 -Restore -RestoreFile "backups\daily\backup_file.sql.zip"
```

### Backup Features
- **Compression**: Automatic file compression
- **Encryption**: Optional backup encryption
- **Retention**: Configurable retention policy
- **Cloud Storage**: AWS S3, Azure Blob, Google Cloud
- **Verification**: Backup integrity checks

### Monitoring Backups
- Check logs: `backups\logs\backup.log`
- Windows Task Scheduler: Monitor scheduled tasks
- Alert on backup failures

---

## 4. Scaling Configuration

### Overview
Horizontal scaling support for handling increased load with multiple backend instances.

### Scaling Architecture
- **Load Balancer**: Nginx with least connections algorithm
- **Backend Scaling**: Multiple FastAPI instances
- **Database**: Single PostgreSQL instance (can be clustered)
- **Cache**: Redis for session management

### Setup Process

1. **Use Scalable Configuration**:
```powershell
# Start with 3 backend instances
.\scaling_manager.ps1 -Scale -BackendReplicas 3
```

2. **Monitor Scaling**:
```powershell
# Check status
.\scaling_manager.ps1 -Status

# Monitor resources
.\scaling_manager.ps1 -Monitor
```

3. **Scale Up/Down**:
```powershell
# Scale to 5 instances
.\scaling_manager.ps1 -Scale -BackendReplicas 5

# Scale down to 2 instances
.\scaling_manager.ps1 -Scale -BackendReplicas 2
```

### Load Balancing Features
- **Algorithm**: Least connections (configurable)
- **Health Checks**: Automatic unhealthy instance removal
- **Session Persistence**: Optional sticky sessions
- **SSL Termination**: HTTPS handling at load balancer
- **Rate Limiting**: Request throttling

### Resource Requirements
- **Minimum**: 2 CPU cores, 4GB RAM per backend instance
- **Recommended**: 4 CPU cores, 8GB RAM per backend instance
- **Database**: 4 CPU cores, 8GB RAM minimum
- **Load Balancer**: 1 CPU core, 1GB RAM

---

## 5. Monitoring and Alerting

### Overview
Comprehensive monitoring with email and SMS alerts for proactive issue detection.

### Monitoring Components
- **System Metrics**: CPU, Memory, Disk usage
- **Application Health**: Service status, response times
- **Database Monitoring**: Connection pool, query performance
- **Load Balancer**: Request distribution, backend health

### Setup Process

1. **Configure Alerting**:
```powershell
.\advanced_alerting.ps1 -Setup
# Edit alerting_config.json with SMTP/Twilio credentials
```

2. **Test Notifications**:
```powershell
.\advanced_alerting.ps1 -TestAlerts
```

3. **Start Monitoring**:
```powershell
.\advanced_alerting.ps1 -Monitor
```

### Alert Channels
- **Email**: SMTP-based notifications
- **SMS**: Twilio integration
- **Escalation**: Multi-level alert escalation
- **Cooldown**: Prevent alert spam

### Alert Thresholds
- **CPU**: Warning at 80%, Critical at 95%
- **Memory**: Warning at 85%, Critical at 95%
- **Disk**: Critical at 90%
- **Response Time**: Warning at 5 seconds
- **Error Rate**: Warning at 5%

### Monitoring Tools
- **Built-in**: Health check endpoints
- **Prometheus**: Metrics collection (optional)
- **Grafana**: Visualization dashboards (optional)
- **Nginx Status**: Load balancer metrics

---

## 6. Security Considerations

### Network Security
- **Firewall**: Restrict access to necessary ports only
- **VPN**: Use VPN for administrative access
- **SSL/TLS**: Encrypt all communications
- **Rate Limiting**: Prevent abuse and DDoS

### Application Security
- **Authentication**: Secure API endpoints
- **Authorization**: Role-based access control
- **Input Validation**: Sanitize all user inputs
- **CORS**: Configure allowed origins

### Data Security
- **Database Encryption**: Encrypt data at rest
- **Backup Encryption**: Encrypt backup files
- **API Key Security**: Secure key storage and rotation
- **Audit Logging**: Track all administrative actions

### Infrastructure Security
- **Container Security**: Regular image updates
- **Host Security**: OS patches and hardening
- **Access Control**: Principle of least privilege
- **Monitoring**: Security event logging

---

## 7. Maintenance Procedures

### Regular Maintenance Tasks

#### Daily
- Monitor system health and alerts
- Check backup completion
- Review error logs
- Monitor resource usage

#### Weekly
- Review security logs
- Update container images
- Test backup restore process
- Performance optimization review

#### Monthly
- Rotate API keys
- Update SSL certificates (if needed)
- Security vulnerability assessment
- Capacity planning review

#### Quarterly
- Full system backup test
- Disaster recovery drill
- Security audit
- Performance benchmarking

### Troubleshooting

#### Common Issues
1. **High CPU Usage**: Scale backend instances
2. **Memory Leaks**: Restart services, investigate logs
3. **Database Locks**: Optimize queries, increase connections
4. **SSL Certificate Expiry**: Renew certificates
5. **Backup Failures**: Check disk space, permissions

#### Log Locations
- **Application**: `./logs/application.log`
- **Nginx**: `./logs/nginx/`
- **Database**: Docker logs
- **Backup**: `./backups/logs/backup.log`

#### Health Check Endpoints
- **Basic Health**: `GET /health`
- **Detailed Health**: `GET /health/detailed`
- **Nginx Status**: `GET /nginx_status`
- **Backend Status**: `GET /backend_status`

### Emergency Procedures

#### Service Outage
1. Check system health endpoints
2. Review recent logs for errors
3. Restart affected services
4. Scale up if needed
5. Notify stakeholders

#### Data Loss
1. Stop all services immediately
2. Assess extent of data loss
3. Restore from latest backup
4. Verify data integrity
5. Resume services gradually

#### Security Incident
1. Isolate affected systems
2. Preserve evidence
3. Rotate all API keys
4. Review access logs
5. Implement additional security measures

---

## 📞 Support and Resources

### Documentation
- [API Keys Setup Guide](API_KEYS_SETUP.md)
- [Backup and Restore Guide](BACKUP_RESTORE.md)
- [Scaling Guide](SCALING_GUIDE.md)
- [Monitoring Guide](MONITORING_GUIDE.md)

### Scripts and Tools
- `api_keys_setup.ps1` - API key management
- `simple_ssl_setup.ps1` - SSL certificate setup
- `backup_system.ps1` - Database backup management
- `scaling_manager.ps1` - Horizontal scaling management
- `advanced_alerting.ps1` - Monitoring and alerting

### Health Check Commands
```powershell
# Test all systems
.\api_keys_setup.ps1 -TestKeys
.\backup_system.ps1 -Test
.\advanced_alerting.ps1 -TestAlerts
.\scaling_manager.ps1 -Status
```

### Emergency Contacts
- **System Administrator**: admin@yourdomain.com
- **Operations Team**: ops@yourdomain.com
- **On-Call Engineer**: +1-XXX-XXX-XXXX

---

**Last Updated**: October 12, 2025  
**Version**: 1.0.0  
**Maintainer**: FreeMobilaChat Operations Team
