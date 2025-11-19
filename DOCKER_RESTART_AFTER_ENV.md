# Restart Docker After Updating .env File

## Quick Answer

**Yes, you need to restart Docker containers** after updating your `.env` file so the containers can load the new environment variables.

## Why?

The `docker-compose.yml` file reads environment variables from your `.env` file using syntax like:
```yaml
- STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY:-}
```

Docker Compose only reads the `.env` file when containers are **started**, not while they're running. So after updating `.env`, you need to restart.

## How to Restart

### Option 1: Restart (Recommended - Faster)

This restarts containers without rebuilding:

```bash
docker-compose restart
```

### Option 2: Down and Up (More Thorough)

This stops and starts containers fresh:

```bash
# Stop containers
docker-compose down

# Start containers (loads new .env)
docker-compose up -d
```

### Option 3: Recreate Containers

If you want to ensure a completely fresh start:

```bash
docker-compose down
docker-compose up -d --force-recreate
```

## Verify Environment Variables Are Loaded

After restarting, verify the Stripe keys are loaded:

```bash
# Check if Stripe keys are in the container
docker-compose exec redline-web env | grep STRIPE
```

You should see:
```
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

## Check Application Logs

After restart, check logs to see if Stripe is configured:

```bash
docker-compose logs -f redline-web | grep -i stripe
```

Look for messages like:
- "Stripe configured successfully"
- "Payment configuration valid"
- Or any errors about missing keys

## Quick Reference

**After updating .env:**
```bash
docker-compose restart
```

**Or:**
```bash
docker-compose down
docker-compose up -d
```

**Verify:**
```bash
docker-compose exec redline-web env | grep STRIPE
```

## Important Notes

1. **`.env` file location**: Must be in the same directory as `docker-compose.yml`
2. **No quotes needed**: In `.env`, don't use quotes around values:
   ```bash
   # ✅ Correct
   STRIPE_SECRET_KEY=sk_test_abc123
   
   # ❌ Wrong
   STRIPE_SECRET_KEY="sk_test_abc123"
   ```
3. **Restart required**: Environment variables are only loaded when containers start
4. **No rebuild needed**: You don't need to rebuild the image, just restart containers

## Troubleshooting

### Variables Not Loading?

1. **Check .env file location:**
   ```bash
   ls -la .env
   ```
   Should be in same directory as `docker-compose.yml`

2. **Check .env syntax:**
   ```bash
   cat .env | grep STRIPE
   ```
   Should show your keys without quotes

3. **Check docker-compose config:**
   ```bash
   docker-compose config | grep STRIPE
   ```
   Should show your keys being loaded

4. **Restart again:**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### Still Not Working?

Check if variables are being read:
```bash
# See what docker-compose sees
docker-compose config

# Check container environment
docker-compose exec redline-web printenv | grep STRIPE
```

