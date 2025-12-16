#!/bin/bash

# VarioSync.com Domain Setup Script
# This script automates the server setup portion of connecting varioSync.com

set -e

echo "=========================================="
echo "VarioSync.com Domain Setup Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

# Get server IP
SERVER_IP=$(curl -s ifconfig.me)
echo -e "${GREEN}Detected Server IP: ${SERVER_IP}${NC}"
echo ""

# Step 1: Update system
echo -e "${YELLOW}[1/8] Updating system packages...${NC}"
apt update && apt upgrade -y
echo -e "${GREEN}✓ System updated${NC}"
echo ""

# Step 2: Install Docker
echo -e "${YELLOW}[2/8] Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    echo -e "${GREEN}✓ Docker installed${NC}"
else
    echo -e "${GREEN}✓ Docker already installed${NC}"
fi
echo ""

# Step 3: Install Docker Compose
echo -e "${YELLOW}[3/8] Installing Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    apt install docker-compose-plugin -y
    echo -e "${GREEN}✓ Docker Compose installed${NC}"
else
    echo -e "${GREEN}✓ Docker Compose already installed${NC}"
fi
echo ""

# Step 4: Install Nginx
echo -e "${YELLOW}[4/8] Installing Nginx...${NC}"
if ! command -v nginx &> /dev/null; then
    apt install nginx -y
    systemctl enable nginx
    systemctl start nginx
    echo -e "${GREEN}✓ Nginx installed and started${NC}"
else
    echo -e "${GREEN}✓ Nginx already installed${NC}"
fi
echo ""

# Step 5: Install Certbot
echo -e "${YELLOW}[5/8] Installing Certbot for SSL...${NC}"
if ! command -v certbot &> /dev/null; then
    apt install certbot python3-certbot-nginx -y
    echo -e "${GREEN}✓ Certbot installed${NC}"
else
    echo -e "${GREEN}✓ Certbot already installed${NC}"
fi
echo ""

# Step 6: Configure Firewall
echo -e "${YELLOW}[6/8] Configuring firewall...${NC}"
if command -v ufw &> /dev/null; then
    ufw allow 22/tcp
    ufw allow 80/tcp
    ufw allow 443/tcp
    echo "y" | ufw enable
    echo -e "${GREEN}✓ Firewall configured${NC}"
else
    echo -e "${YELLOW}⚠ UFW not found, skipping firewall setup${NC}"
fi
echo ""

# Step 7: Create Nginx configuration template
echo -e "${YELLOW}[7/8] Creating Nginx configuration...${NC}"
cat > /etc/nginx/sites-available/variosync.com << 'EOF'
server {
    listen 80;
    server_name varioSync.com www.varioSync.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name varioSync.com www.varioSync.com;

    # SSL Certificate paths (will be configured by Certbot)
    # ssl_certificate /etc/letsencrypt/live/varioSync.com/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/varioSync.com/privkey.pem;

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
EOF

# Enable site
ln -sf /etc/nginx/sites-available/varioSync.com /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx config
if nginx -t; then
    systemctl reload nginx
    echo -e "${GREEN}✓ Nginx configuration created and enabled${NC}"
else
    echo -e "${RED}✗ Nginx configuration test failed${NC}"
    exit 1
fi
echo ""

# Step 8: Summary and next steps
echo -e "${YELLOW}[8/8] Setup Summary${NC}"
echo ""
echo "=========================================="
echo -e "${GREEN}Server Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Next Steps:"
echo ""
echo "1. Configure DNS Records:"
echo "   Add these records at your domain registrar:"
echo ""
echo "   Type: A"
echo "   Name: @"
echo "   Value: ${SERVER_IP}"
echo "   TTL: 3600"
echo ""
echo "   Type: A"
echo "   Name: www"
echo "   Value: ${SERVER_IP}"
echo "   TTL: 3600"
echo ""
echo "2. Deploy Your Application:"
echo "   cd /opt/redline"
echo "   docker compose -f docker-compose.yml up -d"
echo ""
echo "3. Get SSL Certificate:"
echo "   certbot --nginx -d varioSync.com -d www.varioSync.com"
echo ""
echo "4. Verify Setup:"
echo "   curl https://varioSync.com/health"
echo ""
echo "=========================================="
echo ""
echo -e "${GREEN}Setup script completed successfully!${NC}"
echo ""

