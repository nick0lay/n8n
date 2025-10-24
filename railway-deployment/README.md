# Railway Deployment for n8n with Custom Task Runners

Deploy n8n with custom JavaScript and Python dependencies on Railway using config-as-code.

## 🚀 Quick Start

**New to Railway deployment?**
→ See [docs/QUICK_START.md](./docs/QUICK_START.md) for 5-minute setup

**Ready to deploy?**
1. Create Railway project with PostgreSQL
2. Deploy [n8n service](./n8n/) - uses official image
3. Deploy [runners service](./runners/) - builds custom image with your dependencies

## 📁 Repository Structure

```
railway-deployment/
├── docs/               # 📚 Complete documentation
│   ├── README.md      # Documentation index
│   ├── QUICK_START.md # 5-minute setup guide
│   ├── RAILWAY_DEPLOYMENT_GUIDE.md  # Full deployment guide
│   └── POC_FINDINGS.md  # ⚠️ Critical findings (MUST READ)
│
├── n8n/               # 🎯 n8n Main Service
│   ├── railway.toml   # Railway config (uses official image)
│   └── README.md      # n8n service setup
│
├── runners/           # ⚡ Task Runners Service
│   ├── Dockerfile     # Custom image with dynamic dependencies
│   ├── railway.toml   # Railway config (builds Dockerfile)
│   ├── .env.example   # Environment variables reference
│   └── README.md      # Runners service setup
│
├── local-poc/         # 🧪 Local Testing
│   ├── docker-compose.yml  # Test locally before deploying
│   └── ...
│
└── README.md          # ← You are here
```

## 📖 Documentation

### Essential Reading

1. **[docs/README.md](./docs/README.md)** - Documentation index
2. **[docs/QUICK_START.md](./docs/QUICK_START.md)** - Get started in 5 minutes
3. **[docs/POC_FINDINGS.md](./docs/POC_FINDINGS.md)** - ⚠️ **MUST READ** before production
   - Python 3.13 requirement
   - Security sandbox restrictions
   - Two-variable system
   - Critical issues and fixes

### Service Documentation

- **[n8n/README.md](./n8n/README.md)** - n8n main service setup
- **[runners/README.md](./runners/README.md)** - Task runners service setup
- **[local-poc/README.md](./local-poc/README.md)** - Local testing guide

## 🎯 What You Get

### Architecture

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTPS
       ▼
┌─────────────────────────────┐
│   n8n Main Service          │  ← Official Docker image
│   - Web UI                  │  ← Configured via railway.toml
│   - Task Broker             │  ← Environment vars in Dashboard
└────────┬───────────┬────────┘
         │           │
         │           │ WebSocket
         ▼           ▼
    ┌────────┐  ┌──────────────────┐
    │Postgres│  │ Runners Service  │  ← Custom Docker image
    │        │  │ - JS Runner      │  ← Built with your dependencies
    └────────┘  │ - Python Runner  │  ← Config-as-code via railway.toml
                └──────────────────┘
```

### Features

✅ **Config-as-Code** - Railway deployment via `railway.toml` files
✅ **Dynamic Dependencies** - Add npm/pip packages via build args
✅ **Two-Variable System** - Install (build) + Allow (runtime)
✅ **Security Sandbox** - Isolated code execution
✅ **Local Testing** - Test with docker-compose before deploying
✅ **POC Validated** - All critical issues fixed from local testing

## 🔧 Configuration

### Build-Time (Railway Dashboard Environment Variables)

Install packages with versions:

```bash
# Set in Railway Dashboard → Runners Service → Variables
# These are passed as --build-arg to Docker build
JS_PACKAGES=moment@2.30.1,axios@^1.7.0,lodash@^4.17.21
PY_PACKAGES=requests==2.31.0,python-dateutil==2.8.2
```

### Runtime (Railway Dashboard Environment Variables)

Enable packages for use in Code nodes:

```bash
# Set in Railway Dashboard → Runners Service → Variables

# JavaScript: Use explicit list (REQUIRED for moment.js and similar libraries)
JS_ALLOW_LIST=moment,axios,lodash
NODE_FUNCTION_ALLOW_EXTERNAL=${{JS_ALLOW_LIST}}

# Or use wildcard (NOT recommended - breaks moment.js and libraries with prototype modifications)
# NODE_FUNCTION_ALLOW_EXTERNAL=*

# Python: Use wildcard by default (no freeze issues)
NODE_FUNCTION_ALLOW_BUILTIN=*
N8N_RUNNERS_EXTERNAL_ALLOW=*
N8N_RUNNERS_STDLIB_ALLOW=*

# Or restrict explicitly if needed:
# PY_ALLOW_LIST=requests,dateutil
# N8N_RUNNERS_EXTERNAL_ALLOW=${{PY_ALLOW_LIST}}
```

⚠️ **JavaScript Allow-Lists:**
- **Explicit list** (recommended): Fixes freeze issues with moment.js and allows package restrictions
- **Wildcard (*)**: Allows all packages but breaks libraries that modify prototypes (moment.js, etc.)
- See: [docs/TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md#momentjs-cannot-assign-to-read-only-property-error)

✅ **Python Allow-Lists:**
- **Wildcard (*)** (recommended): No freeze issues, maximum flexibility
- **Explicit list**: Only needed if you want to restrict specific packages

**Why two variables?** See [docs/POC_FINDINGS.md](./docs/POC_FINDINGS.md#3-two-variable-system-requirement-critical)

**How it works:** Railway automatically passes environment variables as build arguments when they match `ARG` declarations in your Dockerfile.

## 🚦 Deployment Workflow

### 1. Initial Setup

**Via Railway Dashboard:**

1. **Create PostgreSQL Service**
   - New Service → Database → PostgreSQL
   - Wait for provisioning

2. **Create n8n Service**
   - New Service → Docker Image
   - Image: `ghcr.io/n8n-io/n8n:latest`
   - Enable public networking
   - Configure environment variables (see [n8n/README.md](./n8n/README.md))

3. **Create Runners Service**
   - New Service → GitHub Repo
   - Select this repository
   - Root Directory: `railway-deployment/runners`
   - Railway auto-detects railway.toml and Dockerfile
   - Configure environment variables (see [runners/README.md](./runners/README.md))

**Via Railway CLI:**

```bash
# Create project
railway init

# Create PostgreSQL
railway add -s postgres

# For n8n and runners, use Railway Dashboard (easier)
# CLI doesn't support Docker Image deployment type
```

### 2. Configure Variables

**n8n Service:**
- Database connection (use `${{Postgres.*}}` references)
- `N8N_ENCRYPTION_KEY`, `N8N_RUNNERS_AUTH_TOKEN` (generate secure values)
- Host and webhook URL
- See [n8n/README.md](./n8n/README.md) for complete list

**Runners Service:**
- Build-time: `JS_PACKAGES`, `PY_PACKAGES`, `N8N_VERSION`
- Runtime: `JS_ALLOW_LIST`, `PY_ALLOW_LIST`, connection variables
- See [runners/README.md](./runners/README.md) for complete list

### 3. Deploy

Railway automatically:
1. Pulls official n8n image (n8n service)
2. Builds custom image from Dockerfile (runners service)
3. Connects services via private network
4. Exposes n8n via public domain

### 4. Verify

```bash
# Check n8n
railway logs -s n8n

# Check runners
railway logs -s runners

# Get n8n URL
railway domain -s n8n

# Test in browser
open https://<your-domain>.up.railway.app
```

## 📦 Adding Dependencies

### Add JavaScript Package

Go to Railway Dashboard → Runners Service → Variables:

1. **Update build-time variable** (install package):
   ```bash
   JS_PACKAGES=moment@2.30.1,axios@^1.7.0,lodash@^4.17.21,uuid@^9.0.0
   ```

2. **Update runtime variable** (enable usage):

   **Option A: Explicit list** (✅ Recommended - fixes moment.js freeze issues)
   ```bash
   JS_ALLOW_LIST=moment,axios,lodash,uuid
   NODE_FUNCTION_ALLOW_EXTERNAL=${{JS_ALLOW_LIST}}
   ```

   **Option B: Wildcard** (⚠️ Not recommended - breaks moment.js)
   ```bash
   NODE_FUNCTION_ALLOW_EXTERNAL=*
   ```
   Use wildcard only if:
   - Not using moment.js or similar libraries that modify prototypes
   - Don't need package restrictions

3. **Redeploy** - Click "Redeploy" button in Railway Dashboard

### Add Python Package

Go to Railway Dashboard → Runners Service → Variables:

1. **Update build-time variable** (install package):
   ```bash
   PY_PACKAGES=requests==2.31.0,python-dateutil==2.8.2,beautifulsoup4==4.12.3
   ```

2. **Update runtime variable** (enable usage):

   **Option A: Wildcard** (✅ Recommended - allows all installed packages)
   ```bash
   N8N_RUNNERS_EXTERNAL_ALLOW=*
   N8N_RUNNERS_STDLIB_ALLOW=*
   ```

   **Option B: Explicit list** (only if restricting packages)
   ```bash
   PY_ALLOW_LIST=requests,dateutil,bs4
   N8N_RUNNERS_EXTERNAL_ALLOW=${{PY_ALLOW_LIST}}
   ```
   ⚠️ Note: `beautifulsoup4` installs as `beautifulsoup4` but imports as `bs4`

3. **Redeploy** - Click "Redeploy" button in Railway Dashboard

**No git commit needed** - all changes are in Railway Dashboard.

Full guide: [runners/README.md](./runners/README.md#adding-dependencies)

## ⚠️ Critical Information

### Before Deploying to Production

**MUST READ:** [docs/POC_FINDINGS.md](./docs/POC_FINDINGS.md)

Key requirements:
- ✅ Python 3.13 (not 3.14) - Version mismatch breaks imports
- ✅ Two-variable system - Install vs allow-list
- ✅ Security restrictions - sys, subprocess, os are blocked
- ✅ Package names - Install name may differ from import name

### Security Sandbox

n8n task runners block these imports (by design):
- **Python:** `sys`, `subprocess`, `os`, `__import__`
- **JavaScript:** `process` object, code generation

This is a **security feature**, not a bug. Design workflows accordingly.

## 🧪 Local Testing

Test your configuration locally before deploying to Railway:

```bash
cd local-poc/

# Copy environment template
cp .env.example .env

# Edit dependencies
vim .env

# Build and start
docker-compose up -d

# Test in browser
open http://localhost:5678
```

Full guide: [local-poc/README.md](./local-poc/README.md)

## 📚 Additional Resources

### Documentation
- [docs/README.md](./docs/README.md) - Documentation index
- [docs/QUICK_START.md](./docs/QUICK_START.md) - Quick setup
- [docs/RAILWAY_DEPLOYMENT_GUIDE.md](./docs/RAILWAY_DEPLOYMENT_GUIDE.md) - Complete guide
- [docs/POC_FINDINGS.md](./docs/POC_FINDINGS.md) - Critical findings

### Service Guides
- [n8n/README.md](./n8n/README.md) - n8n service
- [runners/README.md](./runners/README.md) - Runners service
- [runners/.env.example](./runners/.env.example) - Environment variables

### External Links
- [n8n Documentation](https://docs.n8n.io/)
- [Railway Documentation](https://docs.railway.app/)
- [n8n Task Runners Docs](https://docs.n8n.io/hosting/configuration/task-runners/)

## 🤝 Support

- **n8n Issues:** https://github.com/n8n-io/n8n/issues
- **n8n Community:** https://community.n8n.io
- **Railway Help:** https://railway.app/help

## ⚙️ Legacy Files

### Deprecated
- `Dockerfile.custom-runners` - See deprecation notice in file, use `runners/Dockerfile` instead
- `docker-compose.reference.yml` - Use `local-poc/docker-compose.yml` for local testing

---

**Version:** 2.0
**Last Updated:** 2025-10-22
**Status:** Production Ready
**Tested With:** n8n latest, Railway platform
