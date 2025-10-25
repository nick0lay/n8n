# n8n Task Runners Service

This service provides the custom task runners for n8n with dynamic dependency management.

## Quick Setup

### 1. Prerequisites
- Railway account
- n8n service already deployed
- PostgreSQL service running

### 2. Create Service in Railway

1. Go to your Railway project
2. Click "New Service" → "GitHub Repo"
3. Select this repository
4. Set **Root Directory**: `railway-deployment/runners`
5. Railway will auto-detect `railway.toml`

### 3. Configure Environment Variables

⚠️ **IMPORTANT:** Railway uses environment variables for BOTH build arguments and runtime configuration.

#### How Railway Handles Build Arguments

Railway automatically passes environment variables as Docker build arguments when they match `ARG` declarations in your Dockerfile.

**Example:**
1. Your Dockerfile has: `ARG JS_PACKAGES`
2. You set in Railway Dashboard: `JS_PACKAGES=moment@2.30.1,axios@^1.7.0`
3. Railway automatically runs: `docker build --build-arg JS_PACKAGES="moment@2.30.1,axios@^1.7.0" .`

**This means:** The same environment variable can serve dual purposes (build-time installation + runtime configuration).

#### Environment Variables to Set

Go to service **Variables** tab and add:

```bash
# BUILD-TIME (passed as Docker build args - REQUIRED)
N8N_VERSION=latest
JS_PACKAGES=moment@2.30.1,axios@^1.7.0,lodash@^4.17.21
PY_PACKAGES=requests==2.31.0,python-dateutil==2.8.2

# RUNTIME Connection (REQUIRED)
N8N_RUNNERS_TASK_BROKER_URI=http://n8n.railway.internal:5679
N8N_RUNNERS_AUTH_TOKEN=<use-shared-variable>

# JavaScript Allow-Lists (REQUIRED)
JS_ALLOW_LIST=moment,axios,lodash
NODE_FUNCTION_ALLOW_BUILTIN=crypto,fs,path
NODE_FUNCTION_ALLOW_EXTERNAL=${{JS_ALLOW_LIST}}

# Python Allow-Lists (REQUIRED)
PY_ALLOW_LIST=requests,dateutil
PY_STDLIB_ALLOW=json,datetime,math,random
N8N_RUNNERS_EXTERNAL_ALLOW=${{PY_ALLOW_LIST}}
N8N_RUNNERS_STDLIB_ALLOW=${{PY_STDLIB_ALLOW}}

# Performance (OPTIONAL)
N8N_RUNNERS_MAX_CONCURRENCY=5
N8N_RUNNERS_TASK_TIMEOUT=60
N8N_RUNNERS_LAUNCHER_LOG_LEVEL=info

# Timezone (OPTIONAL)
GENERIC_TIMEZONE=America/New_York
```

⚠️ **CRITICAL: Do NOT Use Wildcard for NODE_FUNCTION_ALLOW_EXTERNAL**

**WRONG:**
```bash
NODE_FUNCTION_ALLOW_EXTERNAL=*  # ❌ Breaks moment.js and other libraries!
```

**CORRECT:**
```bash
NODE_FUNCTION_ALLOW_EXTERNAL=moment,axios,lodash  # ✅ Explicit list required
```

**Why:** The runner pre-loads external modules to allow them to modify their prototypes before security freezing. This pre-loading **only works with explicit lists**, not wildcards. Libraries like moment.js will fail with wildcard configuration.

**Error if misconfigured:**
```
TypeError: Cannot assign to read only property 'toString' of object '#<Moment>'
```

**See:** `../docs/TROUBLESHOOTING.md#momentjs-cannot-assign-to-read-only-property-error` for detailed explanation.

### 4. Deploy

Click "Deploy" - Railway will:
1. Read `railway.toml` configuration
2. Build Docker image with dependencies from build args
3. Start the runners service
4. Connect to n8n task broker

## Adding Dependencies

### Two-Variable System

To add a new package, you must update **BOTH** variables in Railway Dashboard:

#### Step 1: Update BUILD-TIME Variables (Install Packages)

Go to Railway Dashboard → Runners Service → Variables:

```bash
# Add new packages to these variables (with versions)
JS_PACKAGES=moment@2.30.1,axios@^1.7.0,lodash@^4.17.21,uuid@^9.0.0
PY_PACKAGES=requests==2.31.0,python-dateutil==2.8.2,beautifulsoup4==4.12.3
```

#### Step 2: Update RUNTIME Variables (Enable Packages)

In the same Variables tab, update the allow-lists:

```bash
# Add package names to these variables (without versions)
JS_ALLOW_LIST=moment,axios,lodash,uuid
PY_ALLOW_LIST=requests,dateutil,bs4
```

**Note:** Package install names may differ from import names:
- `python-dateutil` → imports as `dateutil`
- `beautifulsoup4` → imports as `bs4`

#### Step 3: Trigger Rebuild

After updating variables:
1. Click "Redeploy" button in Railway Dashboard
2. Railway will rebuild with new dependencies
3. New packages will be installed AND allowed for use

**No git commit needed** - changes are in Railway Dashboard only.

## Files

- **`Dockerfile`** - Multi-stage build with POC fixes applied
  - ✅ Python 3.13 (not 3.14)
  - ✅ No env-overrides for allow-lists
  - ✅ Build dependencies for scientific packages
  - ✅ Proper path handling

- **`railway.toml`** - Railway configuration
  - Build arguments (packages with versions)
  - Deploy settings
  - Health checks

- **`.env.example`** - Environment variables template
  - Reference for required variables
  - Documentation of two-variable system
  - Security notes

## Build Args (in railway.toml)

| Argument | Purpose | Example |
|----------|---------|---------|
| `N8N_VERSION` | n8n runners version | `latest` or `1.75.0` |
| `JS_PACKAGES` | JavaScript packages to install | `moment@2.30.1,axios@^1.7.0` |
| `PY_PACKAGES` | Python packages to install | `requests==2.31.0,python-dateutil==2.8.2` |

## Environment Variables (in Railway Dashboard)

| Variable | Required | Purpose |
|----------|----------|---------|
| `N8N_RUNNERS_TASK_BROKER_URI` | ✅ | URL to n8n task broker |
| `N8N_RUNNERS_AUTH_TOKEN` | ✅ | Authentication token (shared with n8n) |
| `JS_ALLOW_LIST` | ✅ | Allowed JS packages (names only) |
| `PY_ALLOW_LIST` | ✅ | Allowed Python packages (import names) |
| `NODE_FUNCTION_ALLOW_EXTERNAL` | ✅ | Apply JS allow-list |
| `N8N_RUNNERS_EXTERNAL_ALLOW` | ✅ | Apply Python allow-list |
| `N8N_RUNNERS_MAX_CONCURRENCY` | ❌ | Max concurrent tasks (default: 5) |
| `N8N_RUNNERS_TASK_TIMEOUT` | ❌ | Task timeout in seconds (default: 60) |

## Troubleshooting

### "Module 'X' is disallowed"

**Cause:** Package not in runtime allow-list

**Fix:**
1. Check `railway.toml` has package in build args
2. Add package name to `JS_ALLOW_LIST` or `PY_ALLOW_LIST` in Dashboard
3. Make sure `NODE_FUNCTION_ALLOW_EXTERNAL` and `N8N_RUNNERS_EXTERNAL_ALLOW` reference the allow-lists

### "No module named 'X'" (Python)

**Cause:** Package not installed OR import name mismatch

**Fix:**
1. Check `railway.toml` has package in `PY_PACKAGES`
2. Verify import name matches allow-list (e.g., `python-dateutil` → `dateutil`)
3. Trigger rebuild

### Build takes 10+ minutes

**Cause:** Scientific packages (numpy, pandas) require compilation

**Expected:** Normal for packages with C extensions

**Options:**
- Use lightweight alternatives if possible
- Accept longer build time
- Use pre-built wheels (Railway auto-caches)

### Connection to task broker fails

**Cause:** n8n service not accessible OR token mismatch

**Fix:**
1. Verify n8n service is running
2. Check `N8N_RUNNERS_TASK_BROKER_URI` uses Railway internal domain
3. Verify `N8N_RUNNERS_AUTH_TOKEN` matches n8n service
4. Check n8n logs for broker errors

## Security

**Blocked Imports (by design):**
- Python: `sys`, `subprocess`, `os`, `__import__`
- JavaScript: `process` object, code generation functions

**Why:** Prevents malicious code from accessing system resources.

**Solution:** Use allowed packages for functionality:
- Use HTTP clients like `requests` instead of system commands
- Use workflow variables instead of environment access
- Use package-provided APIs for operations

See `../docs/POC_FINDINGS.md` for detailed security documentation.

## Monitoring

### Check Service Health

```bash
# Railway CLI
railway logs -s runners

# Check specific container
railway run -s runners wget --spider http://localhost:5680/healthz
```

### Verify Package Installation

```bash
# List installed packages
railway run -s runners ls /opt/runners/task-runner-javascript/node_modules
railway run -s runners ls /opt/runners/task-runner-python/.venv/lib/python3.13/site-packages
```

## Additional Resources

- [Main Documentation](../docs/README.md)
- [Deployment Guide](../docs/DEPLOYMENT_GUIDE.md)
- [POC Findings](../docs/POC_FINDINGS.md)
- [Local Testing](../local-poc/README.md)
