# REDLINE Security Configuration Guide

## 🔒 Overview

This guide covers security best practices for REDLINE deployment and configuration. Following these guidelines will help protect your installation from common security vulnerabilities.

## 🚨 Critical Security Issues Fixed

### 1. Hardcoded Secret Keys
**Issue**: Flask applications were using hardcoded SECRET_KEY values
**Fix**: 
- Generate random SECRET_KEY using `secrets.token_hex(32)`
- Use environment variables for configuration
- No fallback to insecure defaults

### 2. CORS Wildcard Configuration
**Issue**: CORS was configured to allow all origins (`*`)
**Fix**:
- Restrict CORS to specific allowed origins
- Default to localhost only: `http://localhost:8080,http://127.0.0.1:8080`
- Configurable via `CORS_ORIGINS` environment variable

### 3. Hardcoded VNC Passwords
**Issue**: Docker configurations used hardcoded VNC password `redline123`
**Fix**:
- Generate random VNC passwords using `openssl rand -base64 32`
- Use environment variables for configuration
- No default insecure passwords

### 4. Demo API Keys
**Issue**: Downloaders used hardcoded "demo" API keys
**Fix**:
- Require explicit API key configuration
- Use environment variables for API keys
- Clear error messages when keys are missing

## 🛡️ Security Configuration

### Environment Variables

Create a `.env` file with secure values:

```bash
# Copy template
cp env.template .env

# Edit with secure values
nano .env
```

**Required Variables:**
```bash
# Flask Secret Key (REQUIRED)
SECRET_KEY=your-secure-secret-key-here

# VNC Password (REQUIRED for Docker GUI)
VNC_PASSWORD=your-secure-vnc-password-here

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:8080,http://127.0.0.1:8080
```

**Optional Variables:**
```bash
# API Keys for data sources
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
FINNHUB_API_KEY=your-finnhub-key
IEX_CLOUD_API_KEY=your-iex-cloud-key

# License Server
LICENSE_SECRET_KEY=your-license-secret-key

# Environment
FLASK_ENV=production
DEBUG=false
```

### Generate Secure Values

Use the security validator to generate secure configuration:

```bash
# Generate secure configuration
python redline/utils/security_validator.py --generate

# Validate current configuration
python redline/utils/security_validator.py
```

## 🔧 Quick Security Setup

### 1. Generate Secure Configuration
```bash
# Generate secure values
python redline/utils/security_validator.py --generate > secure_config.sh
source secure_config.sh
```

### 2. Create Environment File
```bash
# Copy template and edit
cp env.template .env
nano .env  # Add your secure values
```

### 3. Set File Permissions
```bash
# Secure sensitive files
chmod 600 .env
chmod 600 data/api_keys.json
chmod 600 data_config.ini
```

### 4. Validate Configuration
```bash
# Check security configuration
python redline/utils/security_validator.py
```

## 🐳 Docker Security

### Secure Docker Deployment

1. **Use Environment Variables:**
```bash
# Set secure environment variables
export VNC_PASSWORD=$(openssl rand -base64 32)
export SECRET_KEY=$(openssl rand -hex 32)

# Run with secure configuration
docker-compose up -d
```

2. **Docker Compose with .env:**
```yaml
# docker-compose.yml
services:
  redline:
    environment:
      - VNC_PASSWORD=${VNC_PASSWORD}
      - SECRET_KEY=${SECRET_KEY}
      - CORS_ORIGINS=${CORS_ORIGINS}
```

3. **Production Dockerfile:**
```dockerfile
# Use non-root user
USER redline

# Set secure defaults
ENV FLASK_ENV=production
ENV DEBUG=false
```

## 🌐 Web Application Security

### Flask Security Headers

Add security headers to your Flask application:

```python
from flask_talisman import Talisman

# Add security headers
Talisman(app, force_https=False)  # Set to True for HTTPS
```

### HTTPS Configuration

For production deployments, use HTTPS:

```python
# Enable HTTPS
app.config['PREFERRED_URL_SCHEME'] = 'https'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
```

### Rate Limiting

Implement rate limiting for API endpoints:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

## 📁 File Security

### Sensitive File Permissions

```bash
# Set restrictive permissions
chmod 600 .env                    # Environment variables
chmod 600 data/api_keys.json      # API keys
chmod 600 data_config.ini        # Configuration
chmod 600 *.log                   # Log files

# Data directories
chmod 755 data/                   # Data directory
chmod 755 data/downloaded/        # Downloaded data
```

### Backup Security

```bash
# Secure backup creation
tar -czf backup-$(date +%Y%m%d).tar.gz \
  --exclude='*.log' \
  --exclude='.env' \
  data/ config/
```

## 🔍 Security Monitoring

### Log Security Events

Monitor logs for security events:

```bash
# Monitor access logs
tail -f logs/access.log | grep -E "(401|403|404|500)"

# Monitor application logs
tail -f logs/redline.log | grep -E "(ERROR|WARNING|SECURITY)"
```

### Regular Security Checks

```bash
# Run security validation
python redline/utils/security_validator.py

# Check file permissions
find . -name "*.env" -o -name "*.json" -o -name "*.ini" | xargs ls -la

# Check for hardcoded secrets
grep -r "password.*=" . --exclude-dir=.git
grep -r "secret.*=" . --exclude-dir=.git
```

## 🚀 Production Deployment Checklist

### Pre-Deployment Security

- [ ] Generate secure SECRET_KEY
- [ ] Set strong VNC_PASSWORD
- [ ] Configure CORS_ORIGINS
- [ ] Set FLASK_ENV=production
- [ ] Disable DEBUG mode
- [ ] Set proper file permissions
- [ ] Configure HTTPS (if applicable)
- [ ] Set up rate limiting
- [ ] Configure logging
- [ ] Test security configuration

### Post-Deployment Security

- [ ] Run security validation
- [ ] Monitor logs for errors
- [ ] Test API endpoints
- [ ] Verify file permissions
- [ ] Check for exposed secrets
- [ ] Monitor resource usage
- [ ] Set up automated backups

## 🆘 Security Incident Response

### If Security Issues Are Detected

1. **Immediate Actions:**
   - Change all passwords and keys
   - Review access logs
   - Check for unauthorized access
   - Update security configuration

2. **Investigation:**
   - Analyze logs for suspicious activity
   - Check file modifications
   - Review network connections
   - Document findings

3. **Recovery:**
   - Restore from secure backup
   - Update all credentials
   - Implement additional security measures
   - Monitor for continued issues

## 📞 Support

For security-related questions or to report security issues:

- **Security Issues**: Create a private issue or contact maintainers
- **Configuration Help**: Check documentation or create public issue
- **Best Practices**: Review this guide and community discussions

## 🔄 Regular Security Updates

- **Monthly**: Review and rotate API keys
- **Quarterly**: Update dependencies and security patches
- **Annually**: Review and update security policies
- **As Needed**: Respond to security advisories

---

**Remember**: Security is an ongoing process, not a one-time setup. Regular monitoring and updates are essential for maintaining a secure REDLINE installation.
