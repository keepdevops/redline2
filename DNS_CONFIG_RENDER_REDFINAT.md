# DNS Configuration: Render + redfindat.com

Quick reference for DNS records needed to point redfindat.com to Render services.

## 🎯 Quick Setup

### Option 1: Automated Script (Recommended)

**Bash Script:**
```bash
./add_dns_records.sh
```

**Python Script:**
```bash
python3 add_dns_records.py
```

**Environment Variables (optional):**
```bash
export CF_API_EMAIL="your-email@example.com"
export CF_API_KEY="your-cloudflare-api-key"
export CF_ZONE_ID="your-zone-id"  # Optional, will auto-detect
```

### Option 2: Manual Setup via Cloudflare Dashboard

1. Go to: https://dash.cloudflare.com → Select `redfindat.com` → DNS → Records
2. Add the following records:

## 📋 Required DNS Records

### Record 1: Main Application (app subdomain)

| Field | Value |
|-------|-------|
| **Type** | CNAME |
| **Name** | `app` |
| **Target** | `redline-xxxx.onrender.com` (your Render URL) |
| **Proxy** | ✅ Proxied (orange cloud ON) |
| **TTL** | Auto |

**Result:** `app.redfindat.com` → Points to Render service

### Record 2: Root Domain

| Field | Value |
|-------|-------|
| **Type** | CNAME |
| **Name** | `@` |
| **Target** | `redline-xxxx.onrender.com` (your Render URL) |
| **Proxy** | ✅ Proxied (orange cloud ON) |
| **TTL** | Auto |

**Result:** `redfindat.com` → Points to Render service

### Record 3: WWW Subdomain (Optional)

| Field | Value |
|-------|-------|
| **Type** | CNAME |
| **Name** | `www` |
| **Target** | `redfindat.com` |
| **Proxy** | ✅ Proxied (orange cloud ON) |
| **TTL** | Auto |

**Result:** `www.redfindat.com` → Redirects to `redfindat.com`

## 🔧 Configuration Details

### Render Service URL

Get your Render service URL from:
- Render Dashboard: https://dashboard.render.com
- Format: `https://redline-xxxx.onrender.com`
- Use just the hostname (without https://) for DNS records

### Cloudflare API Credentials

**Get API Key:**
1. Go to: https://dash.cloudflare.com/profile/api-tokens
2. Click "View" next to "Global API Key"
3. Copy the key

**Get Zone ID:**
1. Go to: https://dash.cloudflare.com → Select `redfindat.com`
2. Scroll down on Overview page
3. Copy "Zone ID" from right sidebar

## ✅ Verification

After adding DNS records:

1. **Check DNS Propagation** (5-15 minutes):
   ```bash
   dig app.redfindat.com
   nslookup app.redfindat.com
   ```

2. **Test HTTPS Access**:
   ```bash
   curl -I https://app.redfindat.com/health
   ```

3. **Configure SSL/TLS**:
   - Cloudflare Dashboard → SSL/TLS → Overview
   - Set to: **Full (strict)**

4. **Test in Browser**:
   - Visit: https://app.redfindat.com
   - Should see REDLINE web interface

## 📊 Complete DNS Setup Summary

```
Domain: redfindat.com
Render URL: redline-xxxx.onrender.com

DNS Records:
┌──────────┬──────────┬──────────────────────────────┬─────────┐
│ Type     │ Name     │ Target                       │ Proxy   │
├──────────┼──────────┼──────────────────────────────┼─────────┤
│ CNAME    │ app      │ redline-xxxx.onrender.com     │ ✅      │
│ CNAME    │ @        │ redline-xxxx.onrender.com     │ ✅      │
│ CNAME    │ www      │ redfindat.com                │ ✅      │
└──────────┴──────────┴──────────────────────────────┴─────────┘

Result URLs:
• https://app.redfindat.com → Render service
• https://redfindat.com → Render service
• https://www.redfindat.com → Redirects to redfindat.com
```

## 🚨 Troubleshooting

### DNS Not Resolving
- Wait 5-15 minutes for propagation
- Verify nameservers point to Cloudflare
- Check DNS records in Cloudflare Dashboard

### SSL Certificate Issues
- Set SSL/TLS mode to "Full (strict)"
- Wait 5-15 minutes for certificate provisioning
- Verify Render service has valid SSL

### Site Not Loading
- Test Render URL directly: `curl https://redline-xxxx.onrender.com/health`
- Check Render service is running
- Verify CNAME target is correct

## 🔗 Quick Links

- **Cloudflare Dashboard**: https://dash.cloudflare.com
- **DNS Records**: https://dash.cloudflare.com → Select domain → DNS → Records
- **SSL/TLS**: https://dash.cloudflare.com → Select domain → SSL/TLS → Overview
- **Render Dashboard**: https://dashboard.render.com
- **API Tokens**: https://dash.cloudflare.com/profile/api-tokens

## 📝 Notes

- DNS changes take 5-15 minutes to propagate globally
- Cloudflare proxy (orange cloud) provides DDoS protection and CDN
- SSL certificates are automatically provisioned by Cloudflare
- TTL set to "Auto" (1) for fastest updates

---

**Last Updated:** $(date)
**Domain:** redfindat.com
**Service:** Render

