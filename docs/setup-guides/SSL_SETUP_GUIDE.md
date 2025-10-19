# 🔒 SSL/HTTPS Setup Guide for FreeMobilaChat

## Overview
This guide provides comprehensive instructions for setting up SSL/HTTPS for the FreeMobilaChat application in production.

## 🚨 Current Status
- **HTTP**: ✅ Working on port 8080
- **HTTPS**: ⚠️ Temporarily disabled due to certificate issues
- **SSL Certificates**: Present but need proper configuration

## 🎯 SSL Setup Options

### Option 1: Let's Encrypt (Recommended for Production)
**Best for**: Production deployments with a real domain name
**Cost**: Free
**Validity**: 90 days (auto-renewable)

#### Prerequisites
- Domain name pointing to your server
- Port 80 and 443 accessible from internet
- Certbot installed

#### Setup Steps
```bash
# Install Certbot (Ubuntu/Debian)
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Generate certificates
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

#### Nginx Configuration
```nginx
server {
    listen 80;
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL Security Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000" always;
}
```

### Option 2: Self-Signed Certificates (Development/Testing)
**Best for**: Development, testing, internal networks
**Cost**: Free
**Validity**: Custom (typically 1 year)

#### Using OpenSSL (Recommended)
```bash
# Generate private key
openssl genrsa -out ssl/key.pem 2048

# Generate certificate signing request
openssl req -new -key ssl/key.pem -out ssl/cert.csr

# Generate self-signed certificate
openssl x509 -req -days 365 -in ssl/cert.csr -signkey ssl/key.pem -out ssl/cert.pem

# Clean up
rm ssl/cert.csr
```

#### Using PowerShell (Windows)
```powershell
# Run as Administrator
.\generate_ssl_certificates.ps1 -Domain localhost -ValidDays 365
```

### Option 3: Commercial SSL Certificate
**Best for**: Enterprise production deployments
**Cost**: $50-500/year depending on provider
**Validity**: 1-2 years

#### Popular Providers
- DigiCert
- GlobalSign
- Sectigo (formerly Comodo)
- GoDaddy

#### Setup Process
1. Generate Certificate Signing Request (CSR)
2. Purchase certificate from provider
3. Validate domain ownership
4. Download certificate files
5. Install on server

## 🔧 Configuration Steps

### Step 1: Prepare Certificate Files
Ensure you have these files in the `ssl/` directory:
- `cert.pem` - SSL certificate
- `key.pem` - Private key

### Step 2: Update Nginx Configuration
Edit `nginx.conf`:
```nginx
server {
    listen 80;
    listen 443 ssl http2;  # Enable HTTPS
    server_name your-domain.com;
    
    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # Security headers and settings...
}
```

### Step 3: Update Docker Compose
Ensure SSL certificates are mounted:
```yaml
nginx:
  volumes:
    - ./ssl:/etc/nginx/ssl:ro
  ports:
    - "8080:80"
    - "8443:443"
```

### Step 4: Restart Services
```bash
docker-compose restart nginx
```

### Step 5: Test HTTPS
```bash
# Test HTTPS endpoint
curl -k https://localhost:8443/api/health

# Check certificate details
openssl s_client -connect localhost:8443 -servername localhost
```

## 🛡️ Security Best Practices

### SSL/TLS Configuration
```nginx
# Use modern TLS versions only
ssl_protocols TLSv1.2 TLSv1.3;

# Strong cipher suites
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384;

# Prefer server ciphers
ssl_prefer_server_ciphers off;

# Session settings
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;

# OCSP Stapling
ssl_stapling on;
ssl_stapling_verify on;
```

### Security Headers
```nginx
# HSTS
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

# Other security headers
add_header X-Frame-Options DENY always;
add_header X-Content-Type-Options nosniff always;
add_header X-XSS-Protection "1; mode=block" always;
```

### HTTP to HTTPS Redirect
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Certificate Format Errors
```
Error: PEM_read_bio_PrivateKey() failed
```
**Solution**: Ensure private key is in correct PEM format

#### 2. Permission Errors
```
Error: cannot load certificate
```
**Solution**: Check file permissions and ownership

#### 3. Browser Security Warnings
**For self-signed certificates**: Normal behavior, click "Advanced" → "Proceed"
**For production**: Check certificate validity and chain

### Debug Commands
```bash
# Check certificate validity
openssl x509 -in ssl/cert.pem -text -noout

# Test SSL connection
openssl s_client -connect localhost:8443

# Check nginx configuration
docker exec freemobilachat_nginx nginx -t

# View nginx logs
docker-compose logs nginx
```

## 📋 Production Checklist

- [ ] Domain name configured and pointing to server
- [ ] SSL certificates obtained (Let's Encrypt recommended)
- [ ] Nginx configuration updated for HTTPS
- [ ] HTTP to HTTPS redirect configured
- [ ] Security headers implemented
- [ ] Certificate auto-renewal set up (for Let's Encrypt)
- [ ] HTTPS tested and working
- [ ] Browser security warnings resolved
- [ ] SSL Labs test passed (A+ rating)

## 🔄 Certificate Renewal

### Let's Encrypt Auto-Renewal
```bash
# Add to crontab
0 12 * * * /usr/bin/certbot renew --quiet
```

### Manual Renewal Process
1. Generate new certificates
2. Replace old certificate files
3. Restart nginx: `docker-compose restart nginx`
4. Test HTTPS functionality

## 📞 Support Resources
- Let's Encrypt: https://letsencrypt.org/docs/
- SSL Labs Test: https://www.ssllabs.com/ssltest/
- Mozilla SSL Config: https://ssl-config.mozilla.org/

---
**Status**: SSL temporarily disabled for development
**Next Steps**: Follow this guide to enable HTTPS in production
**Last Updated**: October 12, 2025
