# Railway Deployment - Troubleshooting Guide

This document covers common issues and their solutions for n8n Railway deployment with custom task runners.

---

## Table of Contents

- [JavaScript Dependencies Issues](#javascript-dependencies-issues)
  - [Moment.js "Cannot assign to read only property" Error](#momentjs-cannot-assign-to-read-only-property-error)
- [Python Dependencies Issues](#python-dependencies-issues)
- [Connection Issues](#connection-issues)
- [Build Issues](#build-issues)

---

## JavaScript Dependencies Issues

### Moment.js "Cannot assign to read only property" Error

**Symptom:**
```javascript
TypeError: Cannot assign to read only property 'toString' of object '#<Moment>'
    at /opt/runners/task-runner-javascript/node_modules/.pnpm/moment@2.30.1/node_modules/moment/moment.js:4949:20
```

**Root Cause:**

The n8n task runner implements prototype pollution protection by freezing all JavaScript prototypes. However, some libraries like **moment.js** need to modify their own prototypes during initialization (e.g., overriding `toString()`).

The runner includes a workaround: it **pre-loads** allowed external modules **before** freezing prototypes. This allows libraries to make their prototype modifications during import.

**Critical Detail:** This pre-loading mechanism **only works when modules are explicitly listed**. When `NODE_FUNCTION_ALLOW_EXTERNAL = *` (wildcard), the pre-loading is skipped, causing moment.js to fail when it tries to modify an already-frozen prototype.

**Code Reference:** `packages/@n8n/task-runner/src/js-task-runner/js-task-runner.ts:133-143`

```typescript
private preventPrototypePollution(allowedExternalModules: Set<string> | '*') {
    if (allowedExternalModules instanceof Set) {
        // Pre-load modules BEFORE freezing - ONLY runs with explicit list!
        for (const module of allowedExternalModules) {
            require(module);
        }
    }
    // Then freeze all prototypes
}
```

**Solution:**

Change `NODE_FUNCTION_ALLOW_EXTERNAL` from wildcard to an explicit list:

```bash
# ❌ WRONG - Causes moment.js to fail
railway variables --service n8n-runner --set "NODE_FUNCTION_ALLOW_EXTERNAL=*"

# ✅ CORRECT - Pre-loads modules before freezing
railway variables --service n8n-runner --set "NODE_FUNCTION_ALLOW_EXTERNAL=moment,axios,lodash"
```

After changing the variable, restart the runner service:
```bash
railway service # Select n8n-runner
railway up -d   # Redeploy
```

**Affected Libraries:**

This issue affects any JavaScript library that modifies prototypes during initialization:
- **moment.js** - Modifies `Moment.prototype.toString`
- **luxon** - May have similar issues
- Other date/time libraries with prototype extensions

**Best Practice:**

⚠️ **Always use explicit module lists instead of wildcard (`*`)** for `NODE_FUNCTION_ALLOW_EXTERNAL`:

```toml
# In Railway Dashboard - Runner Service Environment Variables
NODE_FUNCTION_ALLOW_EXTERNAL = moment,axios,lodash,<other-packages>
```

**Why Not Use Wildcard?**

1. **Security:** Explicit lists prevent accidental loading of malicious packages
2. **Compatibility:** Some libraries require pre-loading (like moment.js)
3. **Debugging:** Explicit lists make it clear which dependencies are allowed
4. **Performance:** Pre-loading is faster than dynamic discovery

**Verification:**

After applying the fix, test with this code in a Code node:

```javascript
const moment = require('moment');

// Should work without errors
const now = moment();
const formatted = now.format('YYYY-MM-DD HH:mm:ss');

return [{ json: { now: formatted } }];
```

---

## Python Dependencies Issues

### Import Errors with Python Packages

**Symptom:**
```python
ModuleNotFoundError: No module named 'requests'
```

**Solution:**

1. Verify `PY_PACKAGES` build argument includes the package with correct version:
   ```bash
   railway variables --service n8n-runner
   # Should show: PY_PACKAGES = requests==2.31.0,python-dateutil==2.8.2
   ```

2. Verify runtime allow-list includes the package name:
   ```bash
   # For python-dateutil, the import name is 'dateutil', not 'python-dateutil'
   railway variables --service n8n-runner --set "N8N_RUNNERS_EXTERNAL_ALLOW=requests,dateutil"
   ```

3. Rebuild the runner service to install packages:
   ```bash
   railway up --service n8n-runner -d
   ```

---

## Connection Issues

### Runner Cannot Connect to n8n Broker

**Symptom:**
```
Error: Failed to connect to task broker at http://n8n.railway.internal:5679
```

**Solutions:**

1. **Check IPv6 Configuration:**
   ```bash
   # n8n service must listen on IPv6
   railway variables --service n8n --set "N8N_RUNNERS_BROKER_LISTEN_ADDRESS=::"
   ```

2. **Verify Private Networking:**
   ```bash
   # Both services must have private networking enabled
   railway variables --service n8n
   railway variables --service n8n-runner
   # Should show: ENABLE_ALPINE_PRIVATE_NETWORKING = true
   ```

3. **Check Auth Token Match:**
   ```bash
   # Both services must use the same token
   railway variables --service n8n | grep AUTH_TOKEN
   railway variables --service n8n-runner | grep AUTH_TOKEN
   ```

---

## Build Issues

### Docker BuildKit Parse Error

**Symptom:**
```
ERROR: failed to solve: dockerfile parse error on line 125: unknown instruction: {
```

**Solution:**

This occurs with heredoc syntax issues. Ensure heredoc markers are properly quoted:

```dockerfile
# ✅ CORRECT
RUN cat > /etc/config.json <<'EOFCONFIG'
{
  "key": "value"
}
EOFCONFIG

# ❌ WRONG - Causes parse error
RUN cat > /etc/config.json << EOF
{
  "key": "value"
}
EOF
```

### Railway Using Nixpacks Instead of Dockerfile

**Symptom:**
```
Runner logs show full n8n instance starting instead of task runner launcher
```

**Solution:**

Explicitly set Dockerfile path in `railway.toml`:

```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "railway-deployment/runner/Dockerfile"
```

---

## Health Check Issues

### Railway Health Check Failures (Cosmetic)

**Symptom:**
```
Attempt #1 failed with service unavailable. Continuing to retry
```

**Context:**

Railway health checks may fail for internal-only services. This is usually cosmetic if:
1. Docker HEALTHCHECK passes (check logs: "healthcheck: healthy")
2. Service is functioning (runners connecting, code executing)
3. Service is internal-only (not exposed publicly)

**Solution:**

Comment out Railway health check in `railway.toml`:

```toml
[deploy]
numReplicas = 1
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
# healthcheckPath = "/healthz"
# healthcheckTimeout = 300
```

Docker's HEALTHCHECK in the Dockerfile is sufficient for internal services.

---

## Environment Variable Reference

### Critical Variables for Runner Service

| Variable | Required | Example | Notes |
|----------|----------|---------|-------|
| `NODE_FUNCTION_ALLOW_EXTERNAL` | Yes | `moment,axios,lodash` | **Must be explicit list**, not `*` |
| `NODE_FUNCTION_ALLOW_BUILTIN` | Optional | `crypto,fs,path` or `*` | Can use wildcard safely |
| `N8N_RUNNERS_EXTERNAL_ALLOW` | Yes | `requests,dateutil` | Python packages |
| `N8N_RUNNERS_STDLIB_ALLOW` | Optional | `*` | Python stdlib modules |
| `N8N_RUNNERS_TASK_BROKER_URI` | Yes | `http://n8n.railway.internal:5679` | Use private domain |
| `N8N_RUNNERS_AUTH_TOKEN` | Yes | `<secure-token>` | Must match n8n service |

### Build-Time Variables

| Variable | Required | Example | Notes |
|----------|----------|---------|-------|
| `JS_PACKAGES` | Yes | `moment@2.30.1,axios@^1.7.0` | With versions |
| `PY_PACKAGES` | Yes | `requests==2.31.0,python-dateutil==2.8.2` | With versions |
| `N8N_VERSION` | Optional | `latest` | Runner base image version |

---

## Getting Help

1. **Check logs:**
   ```bash
   railway logs --service n8n-runner
   railway logs --service n8n
   ```

2. **Verify environment variables:**
   ```bash
   railway variables --service n8n-runner
   ```

3. **Test locally first:**
   ```bash
   cd railway-deployment/local-poc
   docker-compose up -d
   ```

4. **Review documentation:**
   - `railway-deployment/docs/RAILWAY_DEPLOYMENT_GUIDE.md`
   - `railway-deployment/docs/QUICK_START.md`
   - `railway-deployment/docs/POC_FINDINGS.md`
