# Cloudflare DNS Setup for redfindat.com

## Overview

This guide covers setting up DNS records for `redfindat.com` in Cloudflare to point to your Render service.

## Prerequisites

1. **Domain registered with Cloudflare**
   - Domain: `redfindat.com`
   - DNS managed by Cloudflare
   - Nameservers pointing to Cloudflare

2. **Render Service Deployed**
   - Service URL: `redline-xxxx.onrender.com` (or your service name)
   - Service is running and accessible

## DNS Records Configuration

### Step 1: Access Cloudflare Dashboard

1. Go to https://dash.cloudflare.com
2. Select `redfindat.com` domain
3. Navigate to **DNS** → **Records**

### Step 2: Add Application DNS Record

**CNAME Record for Application:**

| Type | Name | Target | Proxy Status | TTL |
|------|------|--------|--------------|-----|
| CNAME | `app` | `redline-xxxx.onrender.com` | Proxied (orange cloud) | Auto |

**Configuration:**
- **Type**: CNAME
- **Name**: `app` (creates `app.redfindat.com`)
- **Target**: Your Render service URL (e.g., `redline-xxxx.onrender.com`)
- **Proxy status**: Proxied (orange cloud) ✅
- **TTL**: Auto

**Result**: `app.redfindat.com` will point to your Render service

### Step 3: Add WWW Record (Optional)

**CNAME Record for WWW:**

| Type | Name | Target | Proxy Status | TTL |
|------|------|--------|--------------|-----|
| CNAME | `www` | `redfindat.com` | Proxied (orange cloud) | Auto |

**Configuration:**
- **Type**: CNAME
- **Name**: `www`
- **Target**: `redfindat.com` (root domain)
- **Proxy status**: Proxied (orange cloud) ✅
- **TTL**: Auto

**Result**: `www.redfindat.com` will redirect to `redfindat.com`

### Step 4: Root Domain (A Record - If Needed)

If you want the root domain (`redfindat.com`) to point directly to Render:

**Option A: Use CNAME (Recommended)**
- Cloudflare allows CNAME on root for Proxied records
- Create CNAME: `@` → `redline-xxxx.onrender.com`
- Proxy: Enabled

**Option B: Use A Record (If Render provides IP)**
- Type: A
- Name: `@`
- IPv4 address: Render service IP (if available)
- Proxy: Proxied ✅

**Note**: Render services typically use hostnames, so CNAME is preferred.

## Standard DNS Records

### A Record (Root Domain - Optional)

| Type | Name | IPv4 Address | Proxy Status | TTL |
|------|------|--------------|--------------|-----|
| A | `@` | Render IP (if available) | Proxied | Auto |

**Note**: Usually not needed if using CNAME for root domain.

### AAAA Record (IPv6 - Optional)

| Type | Name | IPv6 Address | Proxy Status | TTL |
|------|------|--------------|--------------|-----|
| AAAA | `@` | Render IPv6 (if available) | Proxied | Auto |

**Note**: Only if Render provides IPv6 addresses.

## Email Records (If Sending Emails)

### MX Records (Mail Exchange)

| Type | Name | Mail Server | Priority | TTL |
|------|------|-------------|----------|-----|
| MX | `@` | `mail.provider.com` | 10 | Auto |

**Configuration:**
- **Type**: MX
- **Name**: `@` (root domain)
- **Mail server**: Your email provider's mail server
- **Priority**: 10 (lower = higher priority)
- **TTL**: Auto

**Common Email Providers:**
- **Gmail/Google Workspace**: `aspmx.l.google.com` (priority 1)
- **Microsoft 365**: `redfindat-com.mail.protection.outlook.com`
- **Cloudflare Email Routing**: Managed automatically

### TXT Records (Email Authentication)

**SPF Record (Sender Policy Framework):**

| Type | Name | Content | TTL |
|------|------|---------|-----|
| TXT | `@` | `v=spf1 include:_spf.google.com ~all` | Auto |

**DKIM Record (DomainKeys Identified Mail):**

| Type | Name | Content | TTL |
|------|------|---------|-----|
| TXT | `default._domainkey` | `v=DKIM1; k=rsa; p=...` | Auto |

**DMARC Record (Domain-based Message Authentication):**

| Type | Name | Content | TTL |
|------|------|---------|-----|
| TXT | `_dmarc` | `v=DMARC1; p=none; rua=mailto:admin@redfindat.com` | Auto |

**Note**: Get exact values from your email provider.

## SSL/TLS Configuration

### Automatic SSL (Recommended)

1. Go to **SSL/TLS** → **Overview**
2. Set encryption mode to **Full** or **Full (strict)**
3. Cloudflare automatically provisions SSL certificate
4. Wait 5-15 minutes for certificate to be active

### SSL/TLS Modes

- **Off**: No encryption (not recommended)
- **Flexible**: Encrypts traffic between visitor and Cloudflare only
- **Full**: Encrypts end-to-end (recommended)
- **Full (strict)**: Encrypts end-to-end with valid certificate required (most secure)

**Recommended**: **Full** or **Full (strict)**

## Verification Steps

### 1. Check DNS Propagation

```bash
# Check A record
dig app.redfindat.com

# Check CNAME
dig app.redfindat.com CNAME

# Check from different location
nslookup app.redfindat.com
```

**Expected**: Should resolve to Cloudflare IP (if proxied) or Render service

### 2. Test HTTPS Access

```bash
# Test HTTPS
curl -I https://app.redfindat.com/health

# Should return 200 OK with valid SSL
```

### 3. Verify SSL Certificate

```bash
# Check SSL certificate
openssl s_client -connect app.redfindat.com:443 -servername app.redfindat.com

# Or use online tool
# https://www.ssllabs.com/ssltest/analyze.html?d=app.redfindat.com
```

**Expected**: Valid SSL certificate issued by Cloudflare

### 4. Test Application

```bash
# Test health endpoint
curl https://app.redfindat.com/health

# Test in browser
open https://app.redfindat.com
```

## DNS Record Summary

### Required Records (Minimum)

| Record | Name | Target/Value | Purpose |
|--------|------|--------------|---------|
| CNAME | `app` | `redline-xxxx.onrender.com` | Main application |

### Recommended Records

| Record | Name | Target/Value | Purpose |
|--------|------|--------------|---------|
| CNAME | `www` | `redfindat.com` | WWW subdomain |
| CNAME | `@` | `redline-xxxx.onrender.com` | Root domain |

### Optional Records

| Record | Name | Target/Value | Purpose |
|--------|------|--------------|---------|
| A | `@` | Render IP | Root domain (if IP available) |
| AAAA | `@` | Render IPv6 | IPv6 support |
| MX | `@` | Mail server | Email delivery |
| TXT | `@` | SPF record | Email authentication |
| TXT | `_dmarc` | DMARC record | Email security |

## Troubleshooting

### DNS Not Resolving

1. **Check DNS propagation**
   ```bash
   dig app.redfindat.com
   ```

2. **Verify Cloudflare nameservers**
   - Go to Cloudflare Dashboard → Overview
   - Ensure nameservers match Cloudflare's

3. **Check proxy status**
   - Ensure proxy is enabled (orange cloud)
   - Disable proxy temporarily to test direct connection

### SSL Certificate Not Active

1. **Wait 5-15 minutes** after enabling SSL
2. **Check SSL/TLS mode** (should be Full or Full strict)
3. **Verify DNS is resolving** correctly
4. **Check Render service** is accessible via direct URL

### Application Not Accessible

1. **Test Render service directly**
   ```bash
   curl https://redline-xxxx.onrender.com/health
   ```

2. **Check Render logs** for errors
3. **Verify environment variables** are set correctly
4. **Check firewall/security settings** in Render

## Quick Reference

### Cloudflare Dashboard URLs

- **DNS Records**: https://dash.cloudflare.com → Select domain → DNS → Records
- **SSL/TLS**: https://dash.cloudflare.com → Select domain → SSL/TLS → Overview
- **Analytics**: https://dash.cloudflare.com → Select domain → Analytics

### Common Commands

```bash
# Check DNS
dig app.redfindat.com
nslookup app.redfindat.com

# Test HTTPS
curl -I https://app.redfindat.com/health

# Check SSL
openssl s_client -connect app.redfindat.com:443
```

## Next Steps

After DNS is configured:

1. ✅ Verify DNS propagation (5-15 minutes)
2. ✅ Test HTTPS access
3. ✅ Configure Stripe webhook (see STRIPE_WEBHOOK_PRODUCTION.md)
4. ✅ Test application functionality
5. ✅ Monitor Cloudflare Analytics

---

**Domain**: redfindat.com  
**Application URL**: https://app.redfindat.com  
**Render Service**: redline-xxxx.onrender.com

