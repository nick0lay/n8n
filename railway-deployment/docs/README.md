# n8n Railway Deployment Documentation

Complete documentation for deploying n8n with custom task runners on Railway.

## 📚 Documentation Index

### Quick Start
- **[QUICK_START.md](./QUICK_START.md)** - 5-minute setup guide
  - Deploy n8n + runners in under 5 minutes
  - Minimal configuration
  - Perfect for getting started

### Complete Guides
- **[RAILWAY_DEPLOYMENT_GUIDE.md](./RAILWAY_DEPLOYMENT_GUIDE.md)** - Full deployment guide
  - All deployment options
  - Detailed configuration
  - Environment variables reference
  - Troubleshooting

- **[POC_FINDINGS.md](./POC_FINDINGS.md)** - ⚠️ **MUST READ** before production
  - Critical issues discovered
  - Python version requirements (3.13)
  - Security sandbox restrictions
  - Two-variable system explanation
  - Railway-specific considerations

- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - 🔧 Problem solving guide
  - Common errors and solutions
  - **moment.js prototype freezing issue** (CRITICAL)
  - Dependency configuration issues
  - Connection problems
  - Build errors

## 🚀 Recommended Reading Order

### First Time Setup
1. [QUICK_START.md](./QUICK_START.md) - Get it running quickly
2. [POC_FINDINGS.md](./POC_FINDINGS.md) - Understand limitations and security
3. [RAILWAY_DEPLOYMENT_GUIDE.md](./RAILWAY_DEPLOYMENT_GUIDE.md) - Deep dive when needed

### Adding Custom Dependencies
1. [POC_FINDINGS.md](./POC_FINDINGS.md) - Read "Two-Variable System" section
2. [RAILWAY_DEPLOYMENT_GUIDE.md](./RAILWAY_DEPLOYMENT_GUIDE.md) - Read "Adding Custom Dependencies" section
3. [../runners/README.md](../runners/README.md) - Runners service specific instructions

### Troubleshooting
1. [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - ⭐ **Start here** - Comprehensive troubleshooting guide
2. [RAILWAY_DEPLOYMENT_GUIDE.md](./RAILWAY_DEPLOYMENT_GUIDE.md) - Deployment troubleshooting section
3. [POC_FINDINGS.md](./POC_FINDINGS.md) - Common POC issues
4. [../runners/README.md](../runners/README.md) - Runners-specific troubleshooting

## 🔍 Find What You Need

### By Topic

**Setup & Deployment:**
- Quick setup → [QUICK_START.md](./QUICK_START.md)
- Complete setup → [RAILWAY_DEPLOYMENT_GUIDE.md](./RAILWAY_DEPLOYMENT_GUIDE.md)
- Service configs → [../n8n/](../n8n/) and [../runners/](../runners/)

**Dependencies:**
- Adding packages → [../runners/README.md](../runners/README.md#adding-dependencies)
- Two-variable system → [POC_FINDINGS.md](./POC_FINDINGS.md#3-two-variable-system-requirement-critical)
- Build args vs env vars → [../runners/railway.toml](../runners/railway.toml)

**Security:**
- Sandbox restrictions → [POC_FINDINGS.md](./POC_FINDINGS.md#2-security-sandbox-restrictions-important)
- Blocked imports → [POC_FINDINGS.md](./POC_FINDINGS.md#python-sandbox-restrictions)
- Best practices → [POC_FINDINGS.md](./POC_FINDINGS.md#security-best-practices)

**Troubleshooting:**
- **moment.js errors** → [TROUBLESHOOTING.md](./TROUBLESHOOTING.md#momentjs-cannot-assign-to-read-only-property-error) ⚠️
- All common issues → [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
- Module not found → [TROUBLESHOOTING.md](./TROUBLESHOOTING.md#import-errors-with-python-packages)
- Module disallowed → [POC_FINDINGS.md](./POC_FINDINGS.md#issue-module-x-is-disallowed)
- Connection issues → [TROUBLESHOOTING.md](./TROUBLESHOOTING.md#runner-cannot-connect-to-n8n-broker)
- Build errors → [TROUBLESHOOTING.md](./TROUBLESHOOTING.md#build-issues)

**Technical Details:**
- Python version requirement → [POC_FINDINGS.md](./POC_FINDINGS.md#1-python-version-mismatch-high-priority)
- Architecture decisions → [POC_FINDINGS.md](./POC_FINDINGS.md#architecture-decisions--rationale)
- Build dependencies → [POC_FINDINGS.md](./POC_FINDINGS.md#4-alpine-linux-build-dependencies-medium)

## 📋 Quick Reference

### Essential Commands

**Generate Secrets:**
```bash
# Encryption key
openssl rand -base64 32

# Runners auth token
openssl rand -base64 32
```

**Railway CLI:**
```bash
# Install
npm i -g @railway/cli

# Login
railway login

# View logs
railway logs -s n8n
railway logs -s runners
```

**Check Service Health:**
```bash
railway domain -s n8n
curl https://<your-domain>/healthz
```

### Environment Variables Quick Reference

**n8n Service:**
- Database: Use `${{Postgres.*}}` references
- Domain: Use `${{RAILWAY_PUBLIC_DOMAIN}}`
- Secrets: Generate `N8N_ENCRYPTION_KEY`, `N8N_RUNNERS_AUTH_TOKEN`

**Runners Service:**
- Connection: `N8N_RUNNERS_TASK_BROKER_URI`, `N8N_RUNNERS_AUTH_TOKEN`
- Allow-lists: `JS_ALLOW_LIST`, `PY_ALLOW_LIST`, `PY_STDLIB_ALLOW`
- Apply: `NODE_FUNCTION_ALLOW_EXTERNAL=${{JS_ALLOW_LIST}}`

### Two-Variable System

**Install (in railway.toml):**
```toml
JS_PACKAGES = "moment@2.30.1,axios@^1.7.0"
PY_PACKAGES = "requests==2.31.0,python-dateutil==2.8.2"
```

**Enable (in Railway Dashboard):**
```bash
JS_ALLOW_LIST=moment,axios
PY_ALLOW_LIST=requests,dateutil
```

## 🎯 Common Tasks

### Deploy New Instance
→ [QUICK_START.md](./QUICK_START.md)

### Add JavaScript Package
1. Edit `runners/railway.toml` → add to `JS_PACKAGES`
2. Railway Dashboard → add to `JS_ALLOW_LIST`
3. Commit and push

### Add Python Package
1. Edit `runners/railway.toml` → add to `PY_PACKAGES`
2. Railway Dashboard → add to `PY_ALLOW_LIST` (use import name!)
3. Commit and push

### Update n8n Version
Railway Dashboard → n8n service → Redeploy

### Debug Connection Issues
```bash
railway logs -s n8n | grep -i "task broker"
railway logs -s runners | grep -i "connection"
```

## ⚠️ Critical Information

### Before Production Deployment

**MUST READ:** [POC_FINDINGS.md](./POC_FINDINGS.md)

Key points:
- ✅ Python 3.13 required (not 3.14)
- ✅ Security sandbox blocks sys, subprocess, os
- ✅ Two-variable system for dependencies
- ✅ Package name vs import name differences
- ✅ Build dependencies for scientific packages

### Security Restrictions

Blocked by design (cannot override):
- **Python:** `sys`, `subprocess`, `os`, `__import__`
- **JavaScript:** `process` object, code generation

Design workflows around these restrictions.

### Support

- **n8n Issues:** https://github.com/n8n-io/n8n/issues
- **n8n Community:** https://community.n8n.io
- **Railway Help:** https://railway.app/help

## 📦 Repository Structure

```
railway-deployment/
├── docs/                    ← You are here
│   ├── README.md           ← This file
│   ├── QUICK_START.md
│   ├── RAILWAY_DEPLOYMENT_GUIDE.md
│   └── POC_FINDINGS.md
├── n8n/                    ← n8n service config
│   ├── railway.toml
│   └── README.md
├── runners/                ← Runners service config
│   ├── Dockerfile
│   ├── railway.toml
│   ├── .env.example
│   └── README.md
└── local-poc/             ← Local testing
    ├── docker-compose.yml
    └── ...
```

## 🔄 Updates

This documentation is maintained alongside the deployment code. If you find issues or have improvements:

1. Test changes locally in `local-poc/`
2. Update relevant documentation
3. Test on Railway
4. Submit pull request

---

**Last Updated:** 2025-10-22
**Tested With:** n8n latest, runners latest
**Railway Deployment:** Production Ready
