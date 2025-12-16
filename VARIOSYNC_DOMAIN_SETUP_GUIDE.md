# VarioSync.com Domain Setup Guide

Complete step-by-step guide to connect your VarioSync application to the domain **varioSync.com**.

---

## 📋 Prerequisites

- Domain name: **varioSync.com** (registered and accessible)
- Server/VPS with Docker installed (or cloud hosting platform)
- SSH access to your server
- Basic knowledge of DNS and server administration

---

## 🎯 Step-by-Step Setup

### **Step 1: Choose Your Hosting Platform**

You have several options:

#### **Option A: VPS/Cloud Server (DigitalOcean, AWS, Linode, etc.)**
- Full control, scalable
- Requires server management
- Cost: $5-20/month

#### **Option B: Render.com (Recommended for simplicity)**
- Easy deployment, automatic SSL
- Free tier available
- Cost: Free tier or $7+/month

#### **Option C: Cloudflare Pages/Workers**
- CDN + edge computing
- Good for static + API
- Cost: Free tier available

#### **Option D: Railway.app / Fly.io**
- Modern PaaS platforms
- Easy Docker deployment
- Cost: Pay-as-you-go

**For this guide, we'll use Option A (VPS) as it's most flexible, with notes for other platforms.**

---

### **Step 2: Prepare Your Server**

#### **2.1. Set Up a VPS**

1. **Create a VPS instance:**
   - DigitalOcean: https://www.digitalocean.com/products/droplets
   - AWS EC2: https://aws.amazon.com/ec2/
   - Linode: https://www.linode.com/
   - Recommended: Ubuntu 22.04 LTS, 2GB RAM minimum

2. **SSH into your server:**
   ```bash
   ssh root@your-server-ip
   ```

3. **Update system:**
   ```bash
   apt update && apt upgrade -y
   ```

#### **2.2. Install Docker and Docker Compose**

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose-plugin -y

# Verify installation
docker --version
docker compose version
```

#### **2.3. Install Nginx (Reverse Proxy)**

```bash
apt install nginx -y
systemctl enable nginx
systemctl start nginx
```

---

### **Step 3: Deploy Your Application**

#### **3.1. Clone Your Repository**

```bash
cd /opt
git clone https://github.com/your-username/redline.git
cd redline
```

#### **3.2. Build and Start Docker Container**

```bash
# Build the production image
docker compose -f docker-compose.yml build

# Start the container
docker compose -f docker-compose.yml up -d

# Verify it's running
docker ps
docker logs variosync-web
```

#### **3.3. Test Local Access**

```bash
# Test that the app is running on port 8080
curl http://localhost:8080/health
```

---

### **Step 4: Configure DNS Records**

#### **4.1. Get Your Server IP Address**

```bash
# On your server, get the public IP
curl ifconfig.me
# Or
hostname -I
```

**Note this IP address** (e.g., `123.45.67.89`)

#### **4.2. Configure DNS at Your Domain Registrar**

Go to your domain registrar (GoDaddy, Namecheap, Cloudflare, etc.) and add DNS records:

**If using Cloudflare (Recommended):**

1. **Add your domain to Cloudflare:**
   - Go to https://dash.cloudflare.com
   - Click "Add a Site"
   - Enter `varioSync.com`
   - Follow the setup wizard

2. **Update Nameservers:**
   - Cloudflare will provide nameservers (e.g., `ns1.cloudflare.com`)
   - Update these at your domain registrar

3. **Add DNS Records:**

   | Type | Name | Content | Proxy | TTL |
   |------|------|---------|-------|-----|
   | A | @ | `your-server-ip` | ✅ Proxied | Auto |
   | A | www | `your-server-ip` | ✅ Proxied | Auto |

   **Or if using a subdomain:**
   
   | Type | Name | Content | Proxy | TTL |
   |------|------|---------|-------|-----|
   | A | app | `your-server-ip` | ✅ Proxied | Auto |

**If NOT using Cloudflare:**

Add these records at your registrar:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ | `your-server-ip` | 3600 |
| A | www | `your-server-ip` | 3600 |

#### **4.3. Verify DNS Propagation**

Wait 5-15 minutes, then check:

```bash
# Check DNS resolution
dig varioSync.com
nslookup varioSync.com

# Should return your server IP
```

---

### **Step 5: Configure Nginx Reverse Proxy**

#### **5.1. Create Nginx Configuration**

```bash
nano /etc/nginx/sites-available/variosync.com
```

**Add this configuration:**

```nginx
server {
    listen 80;
    server_name varioSync.com www.varioSync.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name varioSync.com www.varioSync.com;

    # SSL Certificate paths (will be configured in Step 6)
    ssl_certificate /etc/letsencrypt/live/varioSync.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/varioSync.com/privkey.pem;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy Settings
    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # WebSocket support
        proxy_set_header X-Forwarded-Host $server_name;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://localhost:8080/health;
        access_log off;
    }

    # Static files caching
    location /static/ {
        proxy_pass http://localhost:8080/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

#### **5.2. Enable the Site**

```bash
# Create symbolic link
ln -s /etc/nginx/sites-available/varioSync.com /etc/nginx/sites-enabled/

# Remove default site (optional)
rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# Reload Nginx
systemctl reload nginx
```

---

### **Step 6: Set Up SSL Certificate (HTTPS)**

#### **6.1. Install Certbot**

```bash
apt install certbot python3-certbot-nginx -y
```

#### **6.2. Obtain SSL Certificate**

```bash
# Get certificate (will automatically configure Nginx)
certbot --nginx -d varioSync.com -d www.varioSync.com

# Follow the prompts:
# - Enter your email address
# - Agree to terms
# - Choose whether to redirect HTTP to HTTPS (Yes)
```

#### **6.3. Set Up Auto-Renewal**

```bash
# Test renewal
certbot renew --dry-run

# Certbot automatically sets up a cron job for renewal
# Verify it exists:
systemctl status certbot.timer
```

---

### **Step 7: Configure Firewall**

#### **7.1. Set Up UFW (Uncomplicated Firewall)**

```bash
# Allow SSH
ufw allow 22/tcp

# Allow HTTP and HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Enable firewall
ufw enable

# Check status
ufw status
```

---

### **Step 8: Configure Cloudflare SSL (If Using Cloudflare)**

If you're using Cloudflare:

1. **Go to Cloudflare Dashboard:**
   - https://dash.cloudflare.com → Select `varioSync.com`

2. **SSL/TLS Settings:**
   - Go to SSL/TLS → Overview
   - Set encryption mode to: **Full (strict)**
   - This ensures end-to-end encryption

3. **Page Rules (Optional):**
   - Create rule: `*varioSync.com/*`
   - Settings: Always Use HTTPS, Cache Level: Standard

---

### **Step 9: Test Your Setup**

#### **9.1. Test DNS Resolution**

```bash
# From your local machine
ping varioSync.com
# Should return your server IP

# Check DNS
nslookup varioSync.com
```

#### **9.2. Test HTTP/HTTPS Access**

```bash
# Test HTTP (should redirect to HTTPS)
curl -I http://varioSync.com

# Test HTTPS
curl -I https://varioSync.com

# Test health endpoint
curl https://varioSync.com/health
```

#### **9.3. Test in Browser**

1. Open browser: `https://varioSync.com`
2. Should see VarioSync homepage
3. Check SSL certificate (lock icon in address bar)
4. Test all functionality

---

### **Step 10: Monitor and Maintain**

#### **10.1. Set Up Log Monitoring**

```bash
# View application logs
docker logs variosync-web -f

# View Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

#### **10.2. Set Up Automatic Updates**

```bash
# Create update script
nano /opt/redline/update.sh
```

```bash
#!/bin/bash
cd /opt/redline
git pull
docker compose -f docker-compose.yml build
docker compose -f docker-compose.yml up -d --force-recreate
docker system prune -f
```

```bash
chmod +x /opt/redline/update.sh
```

#### **10.3. Set Up Backups**

```bash
# Backup data directory
tar -czf /backup/variosync-$(date +%Y%m%d).tar.gz /opt/redline/data

# Set up cron job for daily backups
crontab -e
# Add: 0 2 * * * /path/to/backup-script.sh
```

---

## 🚀 Alternative: Deploy to Render.com (Easier Option)

If you prefer a simpler setup without server management:

### **Step 1: Push to Docker Hub**

```bash
# Build and tag
docker build -t keepdevops/variosync:latest -f Dockerfile.webgui.uncompiled .

# Push to Docker Hub
docker login
docker push keepdevops/variosync:latest
```

### **Step 2: Create Render Service**

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect your Docker Hub repository
4. Select `keepdevops/variosync:latest`
5. Set:
   - **Name:** variosync-web
   - **Region:** Choose closest to your users
   - **Instance Type:** Free or Starter
   - **Environment:** Production

### **Step 3: Configure Domain**

1. In Render dashboard → Settings → Custom Domain
2. Add: `varioSync.com`
3. Render will provide DNS instructions
4. Add CNAME record at your DNS provider:
   - **Type:** CNAME
   - **Name:** @
   - **Target:** `variosync-web.onrender.com`
   - **Proxy:** Enabled (if using Cloudflare)

### **Step 4: SSL (Automatic)**

- Render automatically provisions SSL certificates
- No additional configuration needed

---

## 🔧 Troubleshooting

### **Issue: DNS Not Resolving**

**Solution:**
- Wait 15-30 minutes for propagation
- Check DNS records are correct
- Verify nameservers point to Cloudflare/DNS provider
- Use `dig varioSync.com` to check

### **Issue: SSL Certificate Errors**

**Solution:**
- Ensure port 80 is open for Let's Encrypt validation
- Check Nginx configuration: `nginx -t`
- Verify domain ownership
- Try: `certbot renew --force-renewal`

### **Issue: Application Not Loading**

**Solution:**
- Check Docker container: `docker ps`
- Check logs: `docker logs variosync-web`
- Test local: `curl http://localhost:8080/health`
- Check Nginx: `systemctl status nginx`
- Check firewall: `ufw status`

### **Issue: 502 Bad Gateway**

**Solution:**
- Verify Docker container is running: `docker ps`
- Check application logs: `docker logs variosync-web`
- Verify proxy_pass URL in Nginx config
- Test backend: `curl http://localhost:8080`

---

## 📊 Quick Reference

### **Important Commands**

```bash
# Docker Management
docker compose -f docker-compose.yml up -d          # Start
docker compose -f docker-compose.yml down           # Stop
docker compose -f docker-compose.yml logs -f        # View logs
docker compose -f docker-compose.yml restart        # Restart

# Nginx Management
nginx -t                                             # Test config
systemctl reload nginx                              # Reload
systemctl restart nginx                             # Restart

# SSL Certificate
certbot renew                                       # Renew certificate
certbot certificates                                # List certificates

# Firewall
ufw status                                          # Check status
ufw allow 443/tcp                                  # Allow HTTPS
```

### **Important Files**

- **Docker Compose:** `/opt/redline/docker-compose.yml`
- **Nginx Config:** `/etc/nginx/sites-available/varioSync.com`
- **SSL Certs:** `/etc/letsencrypt/live/varioSync.com/`
- **App Logs:** `docker logs variosync-web`
- **Nginx Logs:** `/var/log/nginx/`

---

## ✅ Checklist

- [ ] Server/VPS created and accessible
- [ ] Docker and Docker Compose installed
- [ ] Application deployed and running on port 8080
- [ ] DNS records configured (A record pointing to server IP)
- [ ] Nginx installed and configured as reverse proxy
- [ ] SSL certificate obtained and configured
- [ ] Firewall configured (ports 80, 443 open)
- [ ] Domain resolves correctly (`dig varioSync.com`)
- [ ] HTTPS working (`https://varioSync.com`)
- [ ] Application accessible via domain
- [ ] SSL certificate auto-renewal configured
- [ ] Monitoring/logging set up
- [ ] Backups configured

---

## 🔗 Useful Links

- **Cloudflare Dashboard:** https://dash.cloudflare.com
- **Let's Encrypt:** https://letsencrypt.org
- **Render Dashboard:** https://dashboard.render.com
- **DigitalOcean:** https://www.digitalocean.com
- **Certbot Documentation:** https://certbot.eff.org

---

## 📝 Notes

- DNS changes can take 5-15 minutes to propagate globally
- SSL certificates auto-renew every 90 days
- Keep your server updated: `apt update && apt upgrade`
- Monitor application logs regularly
- Set up automated backups for data directory

---

**Last Updated:** December 2024  
**Domain:** varioSync.com  
**Application:** VarioSync Financial Data Analysis Platform

