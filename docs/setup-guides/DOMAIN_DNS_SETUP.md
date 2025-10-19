# 🌐 Domain Name and DNS Setup Guide

## Overview
This guide walks you through setting up a custom domain name and DNS configuration for the FreeMobilaChat application.

## 🎯 Domain Setup Process

### Step 1: Domain Registration
Choose and register a domain name for your application.

#### Recommended Domain Registrars
- **Namecheap** - Good pricing, reliable service
- **Google Domains** - Easy integration with Google services
- **Cloudflare** - Excellent DNS management and security
- **GoDaddy** - Popular choice with good support

#### Domain Name Suggestions
- `freemobilachat.com`
- `mobilachat.io`
- `tweetanalysis.app`
- `yourcompany-analytics.com`

### Step 2: DNS Configuration
Configure DNS records to point to your server.

#### Required DNS Records
```dns
# A Records (IPv4)
@               A       YOUR_SERVER_IP
www             A       YOUR_SERVER_IP

# AAAA Records (IPv6) - Optional
@               AAAA    YOUR_SERVER_IPv6
www             AAAA    YOUR_SERVER_IPv6

# CNAME Records - Optional
api             CNAME   yourdomain.com
admin           CNAME   yourdomain.com
```

#### Example DNS Configuration
```dns
# For domain: freemobilachat.com
# Server IP: 203.0.113.10

freemobilachat.com.     A       203.0.113.10
www.freemobilachat.com. A       203.0.113.10
api.freemobilachat.com. CNAME   freemobilachat.com.
```

### Step 3: Update Application Configuration
Update nginx and application settings to use your domain.

#### Update nginx.conf
```nginx
server {
    listen 80;
    listen 443 ssl http2;
    server_name freemobilachat.com www.freemobilachat.com;
    
    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/freemobilachat.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/freemobilachat.com/privkey.pem;
    
    # Your existing configuration...
}
```

#### Update .env.production
```env
# Update CORS settings
ALLOWED_ORIGINS=https://freemobilachat.com,https://www.freemobilachat.com

# Update any domain-specific settings
APP_DOMAIN=freemobilachat.com
```

## 🔒 SSL Certificate Setup with Let's Encrypt

### Prerequisites
- Domain pointing to your server
- Ports 80 and 443 accessible
- Certbot installed

### Installation (Ubuntu/Debian)
```bash
# Install Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Generate certificates
sudo certbot --nginx -d freemobilachat.com -d www.freemobilachat.com

# Test auto-renewal
sudo certbot renew --dry-run
```

### Installation (CentOS/RHEL)
```bash
# Install EPEL and Certbot
sudo yum install epel-release
sudo yum install certbot python3-certbot-nginx

# Generate certificates
sudo certbot --nginx -d freemobilachat.com -d www.freemobilachat.com
```

### Manual Certificate Generation
```bash
# If nginx plugin doesn't work
sudo certbot certonly --standalone -d freemobilachat.com -d www.freemobilachat.com

# Then manually configure nginx
```

## 🌍 DNS Providers and Configuration

### Cloudflare (Recommended)
**Benefits**: Free SSL, DDoS protection, CDN, analytics

**Setup Steps**:
1. Transfer DNS to Cloudflare
2. Add A records pointing to your server
3. Enable "Proxy" for main domain records
4. Configure SSL/TLS settings to "Full (strict)"

**DNS Records**:
```
Type    Name    Content         Proxy
A       @       203.0.113.10    ✅ Proxied
A       www     203.0.113.10    ✅ Proxied
CNAME   api     freemobilachat.com    ❌ DNS only
```

### Route 53 (AWS)
**Benefits**: Integration with AWS services, high reliability

**Setup Steps**:
1. Create hosted zone for your domain
2. Update nameservers at registrar
3. Add required DNS records
4. Configure health checks (optional)

### Google Cloud DNS
**Benefits**: Integration with Google Cloud, global anycast

**Setup Steps**:
1. Create DNS zone in Google Cloud Console
2. Update nameservers at registrar
3. Add DNS records via console or CLI

## 🔧 Configuration Scripts

### Domain Configuration Script
```bash
#!/bin/bash
# domain_setup.sh - Configure domain for FreeMobilaChat

DOMAIN="$1"
SERVER_IP="$2"

if [ -z "$DOMAIN" ] || [ -z "$SERVER_IP" ]; then
    echo "Usage: $0 <domain> <server_ip>"
    echo "Example: $0 freemobilachat.com 203.0.113.10"
    exit 1
fi

echo "Configuring domain: $DOMAIN"
echo "Server IP: $SERVER_IP"

# Update nginx configuration
sed -i "s/localhost yourdomain.com www.yourdomain.com/$DOMAIN www.$DOMAIN/g" nginx.conf

# Update environment file
sed -i "s/yourdomain.com/$DOMAIN/g" .env.production

# Generate SSL certificates
sudo certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN"

echo "Domain configuration completed!"
echo "Test your domain: https://$DOMAIN"
```

### DNS Verification Script
```bash
#!/bin/bash
# dns_check.sh - Verify DNS configuration

DOMAIN="$1"

if [ -z "$DOMAIN" ]; then
    echo "Usage: $0 <domain>"
    exit 1
fi

echo "Checking DNS configuration for: $DOMAIN"

# Check A record
echo "A Record:"
dig +short A "$DOMAIN"

# Check WWW record
echo "WWW Record:"
dig +short A "www.$DOMAIN"

# Check nameservers
echo "Nameservers:"
dig +short NS "$DOMAIN"

# Check MX records (if any)
echo "MX Records:"
dig +short MX "$DOMAIN"
```

## 🧪 Testing and Verification

### DNS Propagation Check
```bash
# Check DNS propagation globally
nslookup freemobilachat.com 8.8.8.8
nslookup freemobilachat.com 1.1.1.1

# Online tools
# https://www.whatsmydns.net/
# https://dnschecker.org/
```

### SSL Certificate Verification
```bash
# Check SSL certificate
openssl s_client -connect freemobilachat.com:443 -servername freemobilachat.com

# Online SSL test
# https://www.ssllabs.com/ssltest/
```

### Application Testing
```bash
# Test HTTP (should redirect to HTTPS)
curl -I http://freemobilachat.com

# Test HTTPS
curl -I https://freemobilachat.com

# Test API endpoint
curl https://freemobilachat.com/api/health
```

## 🔍 Troubleshooting

### Common Issues

#### 1. DNS Not Propagating
**Symptoms**: Domain doesn't resolve to your server
**Solutions**:
- Wait 24-48 hours for full propagation
- Check nameservers are correctly set
- Verify DNS records at registrar
- Use different DNS servers for testing

#### 2. SSL Certificate Issues
**Symptoms**: Browser security warnings
**Solutions**:
- Verify domain ownership
- Check certificate validity dates
- Ensure proper certificate chain
- Restart nginx after certificate installation

#### 3. Mixed Content Warnings
**Symptoms**: HTTPS page loading HTTP resources
**Solutions**:
- Update all URLs to use HTTPS
- Configure proper CORS headers
- Check for hardcoded HTTP URLs

### Debug Commands
```bash
# Check DNS resolution
nslookup yourdomain.com
dig yourdomain.com

# Check HTTP response
curl -I http://yourdomain.com

# Check HTTPS response
curl -I https://yourdomain.com

# Check certificate details
openssl x509 -in /etc/letsencrypt/live/yourdomain.com/cert.pem -text -noout
```

## 📋 Production Checklist

- [ ] Domain name registered and configured
- [ ] DNS records pointing to server IP
- [ ] Nameservers updated at registrar
- [ ] DNS propagation completed (24-48 hours)
- [ ] SSL certificates generated and installed
- [ ] Nginx configuration updated with domain
- [ ] Application configuration updated
- [ ] HTTP to HTTPS redirect working
- [ ] All subdomains properly configured
- [ ] SSL certificate auto-renewal set up
- [ ] Domain tested from multiple locations
- [ ] SSL Labs test passed (A+ rating)

## 🔄 Maintenance

### Certificate Renewal
```bash
# Auto-renewal (add to crontab)
0 12 * * * /usr/bin/certbot renew --quiet

# Manual renewal
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run
```

### DNS Monitoring
- Set up DNS monitoring alerts
- Monitor certificate expiration
- Check domain registration expiration
- Monitor DNS propagation changes

## 💰 Cost Considerations

### Domain Registration
- **Basic domains**: $10-15/year
- **Premium domains**: $50-500/year
- **Renewal costs**: Usually same as registration

### DNS Services
- **Basic DNS**: Usually free with domain
- **Premium DNS**: $5-20/month (Cloudflare Pro, Route 53)
- **Enterprise DNS**: $50-200/month

### SSL Certificates
- **Let's Encrypt**: Free
- **Commercial SSL**: $50-200/year
- **Wildcard SSL**: $100-300/year

---
**Status**: Ready for domain configuration
**Next Steps**: Register domain and configure DNS
**Last Updated**: October 12, 2025
