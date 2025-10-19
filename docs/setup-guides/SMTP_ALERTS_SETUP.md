# 📧 SMTP Email Alerts Setup Guide

## Overview
This guide walks you through configuring email alerts for the FreeMobilaChat monitoring system.

## 🚨 Security Warning
- **NEVER** commit SMTP credentials to version control
- Use app-specific passwords when available
- Consider using environment variables for credentials
- Enable 2FA on email accounts used for alerts

## 📋 SMTP Provider Configuration

### Gmail (Recommended for Testing)
**Setup Steps**:
1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. Use these settings:
   ```json
   {
     "smtp": {
       "host": "smtp.gmail.com",
       "port": 587,
       "useTLS": true,
       "username": "your-email@gmail.com",
       "password": "your-16-char-app-password",
       "from": "your-email@gmail.com"
     }
   }
   ```

### Outlook/Hotmail
```json
{
  "smtp": {
    "host": "smtp-mail.outlook.com",
    "port": 587,
    "useTLS": true,
    "username": "your-email@outlook.com",
    "password": "your-password",
    "from": "your-email@outlook.com"
  }
}
```

### SendGrid (Production Recommended)
```json
{
  "smtp": {
    "host": "smtp.sendgrid.net",
    "port": 587,
    "useTLS": true,
    "username": "apikey",
    "password": "your-sendgrid-api-key",
    "from": "alerts@yourdomain.com"
  }
}
```

### Amazon SES
```json
{
  "smtp": {
    "host": "email-smtp.us-east-1.amazonaws.com",
    "port": 587,
    "useTLS": true,
    "username": "your-ses-username",
    "password": "your-ses-password",
    "from": "alerts@yourdomain.com"
  }
}
```

## 🔧 Configuration Process

### Step 1: Update alerting_config.json
```json
{
  "smtp": {
    "host": "smtp.gmail.com",
    "port": 587,
    "useTLS": true,
    "username": "your-email@gmail.com",
    "password": "your-app-password",
    "from": "freemobilachat-alerts@gmail.com",
    "enabled": true
  },
  "recipients": {
    "email": [
      "admin@yourdomain.com",
      "ops@yourdomain.com",
      "alerts@yourdomain.com"
    ]
  }
}
```

### Step 2: Test Email Configuration
```powershell
# Test SMTP settings
.\advanced_alerting.ps1 -TestAlerts

# Expected output:
# ✅ SMTP connection successful
# ✅ Test email sent to all recipients
```

### Step 3: Configure Alert Thresholds
```json
{
  "thresholds": {
    "cpu": 80,           # CPU usage percentage
    "memory": 85,        # Memory usage percentage  
    "disk": 90,          # Disk usage percentage
    "responseTime": 5000, # Response time in ms
    "errorRate": 5       # Error rate percentage
  }
}
```

### Step 4: Set Up Alert Recipients
```json
{
  "recipients": {
    "email": [
      "admin@company.com",      # Primary admin
      "devops@company.com",     # DevOps team
      "oncall@company.com"      # On-call engineer
    ],
    "sms": [
      "+1234567890",            # Primary contact
      "+0987654321"             # Secondary contact
    ]
  }
}
```

## 📱 SMS Alerts (Optional)

### Twilio Configuration
1. Sign up at https://www.twilio.com/
2. Get Account SID, Auth Token, and phone number
3. Update configuration:
```json
{
  "twilio": {
    "accountSid": "your-account-sid",
    "authToken": "your-auth-token", 
    "fromPhone": "+1234567890",
    "enabled": true
  }
}
```

## 🔔 Alert Types and Escalation

### Alert Levels
- **INFO**: System information, low priority
- **WARNING**: Potential issues, medium priority
- **CRITICAL**: Immediate attention required, high priority

### Escalation Policy
```json
{
  "escalation": {
    "enabled": true,
    "levels": [
      {
        "delay": 0,           # Immediate
        "channels": ["email"]
      },
      {
        "delay": 900,         # 15 minutes later
        "channels": ["email", "sms"]
      },
      {
        "delay": 3600,        # 1 hour later
        "channels": ["email", "sms"]
      }
    ]
  }
}
```

### Cooldown Periods
```json
{
  "cooldown": {
    "info": 1800,      # 30 minutes
    "warning": 900,    # 15 minutes
    "critical": 300    # 5 minutes
  }
}
```

## 🧪 Testing Procedures

### Test SMTP Connection
```powershell
# Test basic SMTP connectivity
.\advanced_alerting.ps1 -TestAlerts

# Test with specific configuration
.\configure_smtp_alerts.ps1 -TestOnly
```

### Test Alert Generation
```powershell
# Generate test alerts
.\advanced_alerting.ps1 -GenerateTestAlert -Level Critical

# Monitor alert logs
Get-Content alerts.log -Tail 10 -Wait
```

### Verify Email Delivery
1. Check recipient inboxes
2. Verify sender reputation
3. Check spam folders
4. Confirm email formatting

## 🛡️ Security Best Practices

### Credential Management
- Use app-specific passwords
- Store credentials in environment variables
- Rotate passwords regularly
- Monitor for unauthorized access

### Email Security
- Use TLS encryption (port 587)
- Verify SMTP server certificates
- Implement rate limiting
- Monitor bounce rates

### Access Control
- Limit alert recipients to authorized personnel
- Use role-based email distribution lists
- Implement approval process for changes
- Audit alert configurations regularly

## 🔍 Troubleshooting

### Common Issues

#### 1. Authentication Failed
```
Error: SMTP authentication failed
```
**Solutions**:
- Verify username/password
- Check if 2FA is enabled (use app password)
- Confirm SMTP server settings

#### 2. Connection Timeout
```
Error: Connection timeout
```
**Solutions**:
- Check firewall settings
- Verify SMTP server and port
- Test network connectivity

#### 3. Emails Not Delivered
**Solutions**:
- Check spam folders
- Verify recipient addresses
- Check sender reputation
- Review SMTP logs

### Debug Commands
```powershell
# Test SMTP connection
Test-NetConnection smtp.gmail.com -Port 587

# Check alert logs
Get-Content alerts.log | Select-String "ERROR"

# Verify configuration
Get-Content alerting_config.json | ConvertFrom-Json
```

## 📊 Monitoring Alert System

### Key Metrics
- Alert delivery rate
- Response times
- False positive rate
- Escalation frequency

### Log Analysis
```powershell
# Alert statistics
Get-Content alerts.log | Group-Object {($_ -split " ")[2]} | Sort-Object Count -Descending

# Recent alerts
Get-Content alerts.log -Tail 50 | Where-Object {$_ -match "CRITICAL|WARNING"}
```

## 📋 Production Checklist

- [ ] SMTP provider configured (SendGrid/SES recommended)
- [ ] App-specific passwords generated
- [ ] Alert recipients configured
- [ ] Test emails sent and received
- [ ] Escalation policy defined
- [ ] Cooldown periods set
- [ ] SMS alerts configured (optional)
- [ ] Alert thresholds tuned
- [ ] Monitoring system tested
- [ ] Documentation updated

---
**Status**: Ready for SMTP configuration
**Next Steps**: Configure SMTP credentials and test alerts
**Last Updated**: October 12, 2025
