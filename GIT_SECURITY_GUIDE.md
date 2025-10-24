# 🔒 Git Security Guide for REDLINE

## Overview

This guide ensures that sensitive information is never accidentally committed to the REDLINE repository. It includes `.gitignore` rules, pre-commit hooks, and best practices for secure development.

## 🛡️ Security Measures Implemented

### 1. Enhanced `.gitignore` File

The `.gitignore` file has been updated to exclude:

```gitignore
# Environments and Secrets
.env
.env.*
!.env.template
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# API Keys and Secrets
api_keys.json
*_keys.json
*secrets*
*secret*
*.key
*.pem
*.crt
*.p12
*.pfx

# Configuration files with potential secrets
config.ini
*config*.ini
data_config.ini
*.conf
*.cfg

# Database files
*.db
*.sqlite
*.sqlite3
redline_data.duckdb
temp_data.duckdb

# Logs and temporary files
*.log
logs/
temp/
tmp/
```

### 2. Pre-commit Security Hook

A pre-commit hook has been installed that automatically checks for:

- **Forbidden files**: Files that should never be committed
- **Secret patterns**: Common patterns that indicate secrets
- **Hardcoded values**: Known insecure default values

**Hook location**: `.git/hooks/pre-commit`

### 3. Removed Sensitive Files from Tracking

The following files have been removed from git tracking:
- `api_keys.json` - May contain API keys
- `data_config.ini` - May contain configuration secrets

## 🚨 Files That Should NEVER Be Committed

### Environment Files
```
.env
.env.local
.env.production
.env.staging
.env.development
```

### API Keys and Secrets
```
api_keys.json
secrets.json
*.key
*.pem
*.crt
*.p12
*.pfx
```

### Configuration Files
```
data_config.ini
config.ini
settings.ini
*.conf
*.cfg
```

### Database Files
```
*.db
*.sqlite
*.sqlite3
redline_data.duckdb
temp_data.duckdb
```

### Log Files
```
*.log
logs/
access.log
error.log
```

## 🔧 Secure Development Workflow

### 1. Before Starting Development

```bash
# Copy environment template
cp env.template .env

# Edit with your secure values
nano .env

# Set proper permissions
chmod 600 .env
```

### 2. During Development

```bash
# Check what files are staged
git status

# Review changes before committing
git diff --cached

# Run security validator
python redline/utils/security_validator.py
```

### 3. Before Committing

The pre-commit hook will automatically run and check for:
- Forbidden files
- Secret patterns
- Hardcoded values

If the hook fails, fix the issues before committing.

### 4. If You Need to Bypass Security Checks

**⚠️ Only do this if you're absolutely sure:**

```bash
# Bypass pre-commit hook (NOT RECOMMENDED)
git commit --no-verify

# Or temporarily disable the hook
mv .git/hooks/pre-commit .git/hooks/pre-commit.disabled
git commit
mv .git/hooks/pre-commit.disabled .git/hooks/pre-commit
```

## 🔍 Security Checks

### Manual Security Check

```bash
# Run security validator
python redline/utils/security_validator.py

# Check for secrets in staged files
git diff --cached | grep -E "(password|secret|key|token)"

# Check file permissions
ls -la .env api_keys.json data_config.ini
```

### Automated Security Check

The pre-commit hook automatically checks for:

1. **Forbidden Files**:
   - `.env` files
   - `api_keys.json`
   - `data_config.ini`
   - Certificate files (`.pem`, `.crt`, etc.)

2. **Secret Patterns**:
   - `password = "value"`
   - `secret = "value"`
   - `key = "value"`
   - `token = "value"`
   - `api_key = "value"`
   - `SECRET_KEY = "value"`
   - `VNC_PASSWORD = "value"`

3. **Hardcoded Values**:
   - `redline123`
   - `redline-secret-key`
   - `demo`
   - `test-secret`
   - `default-password`

## 🚨 What to Do If Secrets Are Accidentally Committed

### 1. Immediate Actions

```bash
# Remove from git history (if recent)
git reset --soft HEAD~1

# Remove from tracking
git rm --cached sensitive_file

# Add to .gitignore
echo "sensitive_file" >> .gitignore

# Commit the .gitignore update
git add .gitignore
git commit -m "Add sensitive file to .gitignore"
```

### 2. If Already Pushed to Remote

```bash
# Remove from git history completely
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch sensitive_file' \
  --prune-empty --tag-name-filter cat -- --all

# Force push (WARNING: This rewrites history)
git push origin --force --all
```

### 3. Rotate All Secrets

- Change all passwords
- Regenerate all API keys
- Update all configuration files
- Notify team members

## 📋 Security Checklist

Before every commit, verify:

- [ ] No `.env` files are staged
- [ ] No `api_keys.json` files are staged
- [ ] No configuration files with secrets are staged
- [ ] No hardcoded passwords or keys in code
- [ ] All sensitive files are in `.gitignore`
- [ ] Pre-commit hook passes
- [ ] Security validator passes

## 🔄 Regular Security Maintenance

### Weekly
- Review recent commits for accidental secrets
- Check `.gitignore` for new patterns
- Update pre-commit hook if needed

### Monthly
- Rotate API keys and passwords
- Review team access to repository
- Audit git history for sensitive data

### Quarterly
- Review and update security policies
- Train team on secure git practices
- Update security tools and hooks

## 🛠️ Troubleshooting

### Pre-commit Hook Not Working

```bash
# Check if hook exists and is executable
ls -la .git/hooks/pre-commit

# Make executable if needed
chmod +x .git/hooks/pre-commit

# Test manually
.git/hooks/pre-commit
```

### False Positives

If the pre-commit hook flags legitimate code:

1. **Review the flagged content**
2. **Ensure it's not actually a secret**
3. **If it's a false positive, bypass with `--no-verify`**
4. **Consider updating the hook patterns**

### Hook Bypass

```bash
# Temporarily disable hook
mv .git/hooks/pre-commit .git/hooks/pre-commit.disabled

# Make your commit
git commit -m "Your commit message"

# Re-enable hook
mv .git/hooks/pre-commit.disabled .git/hooks/pre-commit
```

## 📞 Support

If you encounter security issues:

1. **Don't commit** until resolved
2. **Ask for help** from team members
3. **Document the issue** for future reference
4. **Update security measures** if needed

---

**Remember**: Security is everyone's responsibility. When in doubt, ask before committing!
