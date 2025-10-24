# POC Findings & Railway Deployment Guide

## Executive Summary

This document captures critical findings from building a local POC for n8n with custom task runners and dynamic dependency management. These findings are essential for successful Railway deployment and avoiding common pitfalls.

---

## 🚨 CRITICAL ISSUES DISCOVERED

### 1. Python Version Mismatch (HIGH PRIORITY)

**Issue:** The n8n runners base image uses Python 3.13, NOT the latest Python version.

**Symptom:**
```
ModuleNotFoundError: No module named 'requests'
```

**Root Cause:**
- Dockerfile built packages with `FROM python:3.14-alpine`
- Packages installed to: `/usr/local/lib/python3.14/site-packages`
- Runner expected them at: `/opt/runners/task-runner-python/.venv/lib/python3.13/site-packages`

**Solution:**
```dockerfile
# ❌ WRONG - Will cause package import failures
FROM python:3.14-alpine AS python-extras

# ✅ CORRECT - Must match runner's Python version
FROM python:3.13-alpine AS python-extras
```

**COPY path must also match:**
```dockerfile
# Must use python3.13, not python3.14
COPY --from=python-extras \
  /usr/local/lib/python3.13/site-packages \
  /opt/runners/task-runner-python/.venv/lib/python3.13/site-packages/
```

**Verification Command:**
```bash
# Check what Python version the runner uses
docker exec <runners-container> /opt/runners/task-runner-python/.venv/bin/python --version
```

**Railway Deployment Impact:**
- ALWAYS check the n8n runners base image Python version before deployment
- Pin Python version in Dockerfile to match the base image
- Test package imports after every n8n version update

---

### 2. Security Sandbox Restrictions (IMPORTANT)

**Issue:** n8n task runners enforce strict security sandboxing that blocks certain imports.

#### Python Sandbox Restrictions

**Blocked Imports:**
```python
# ❌ These will FAIL with security violations
import sys
import subprocess
import os
import __import__

# Error message:
# "Import of standard library module 'sys' is disallowed"
```

**Allowed Standard Library (must be explicitly enabled):**
```python
# ✅ These work if added to PY_STDLIB_ALLOW
import json
import datetime
import math
import random
import re
from datetime import datetime, timedelta
```

**Configuration Required:**
```bash
# In .env file
PY_STDLIB_ALLOW=json,datetime,math,random,re
```

#### JavaScript Sandbox Restrictions

**Blocked Access:**
```javascript
// ❌ Will FAIL with "process is not defined"
const pid = process.pid;
const env = process.env;

// ❌ Code generation from strings is blocked
// Dynamic code execution is not allowed
```

**Allowed:**
```javascript
// ✅ Imported packages work fine
const moment = require('moment');
const axios = require('axios');
const _ = require('lodash');
```

**Why This Matters:**
- These are NOT bugs - they are SECURITY FEATURES
- Prevents malicious code from accessing system resources
- Cannot be disabled without forking n8n runners
- Must design workflows around these restrictions

**Railway Deployment Impact:**
- Document these restrictions for users
- Test code examples to ensure they don't use blocked imports
- Provide alternative solutions (use allowed packages instead)

---

### 3. Two-Variable System Requirement (CRITICAL)

**Issue:** Cannot mix package versions with allow-lists.

**Wrong Approach:**
```bash
# ❌ FAILS - Allow-list contains versions
NODE_FUNCTION_ALLOW_EXTERNAL=moment@2.30.1,axios@^1.7.0
```

**Correct Approach:**
```bash
# Build-time: Install packages WITH versions
JS_PACKAGES=moment@2.30.1,axios@^1.7.0,lodash@^4.17.21

# Runtime: Allow-list WITHOUT versions
JS_ALLOW_LIST=moment,axios,lodash
```

**Special Case - Package Name vs Import Name:**
```bash
# Python package python-dateutil imports as 'dateutil'
PY_PACKAGES=python-dateutil==2.8.2     # Install name
PY_ALLOW_LIST=dateutil                  # Import name ⚠️

# Must use import name in allow-list!
```

**Verification:**
```bash
# Check what name to use for allow-list
docker exec <container> python -c "import dateutil; print(dateutil.__name__)"
```

**Railway Deployment Impact:**
- Railway environment variables must follow this pattern
- Document the two-variable system clearly
- Provide examples for common packages with different install/import names

---

### 4. Alpine Linux Build Dependencies (MEDIUM)

**Issue:** Scientific Python packages fail to build without C/C++/Fortran compilers.

**Symptom:**
```
error: Failed building wheel for pandas
error: legacy-install-failure
```

**Root Cause:** Alpine Linux is minimal and doesn't include build tools by default.

**Required Build Dependencies:**
```dockerfile
# For scientific Python packages (numpy, pandas, scipy)
RUN apk add --no-cache \
    gcc \
    g++ \
    gfortran \
    musl-dev \
    linux-headers \
    openblas-dev \
    lapack-dev
```

**Build Time Impact:**
- Lightweight packages (requests, dateutil): ~1 minute
- Scientific packages (numpy, pandas): ~5-10 minutes
- Build dependencies add ~250MB to intermediate layer

**Railway Deployment Impact:**
- Longer build times = higher Railway build costs
- Consider using lightweight alternatives when possible:
  - Instead of pandas → use native Python with requests/json
  - Instead of numpy → use math module for simple operations
- Document expected build times for users

---

### 5. Docker Layer Caching Issues (MEDIUM)

**Issue:** Docker caches configuration layers, preventing updates from taking effect.

**Symptom:**
- Changed environment variables don't apply
- Old allow-lists still in effect
- Configuration file shows old values

**Solution:**
```bash
# Always rebuild with --no-cache when changing configuration
docker-compose build --no-cache runners

# Clear volumes if encryption key changed
docker-compose down -v
docker-compose up -d
```

**Railway Deployment Impact:**
- Railway auto-caching may cause similar issues
- Need to force rebuild after configuration changes
- Document cache clearing procedures

---

### 6. env-overrides Configuration Conflict (HIGH)

**Issue:** env-overrides in task runner configuration file overrides docker-compose environment variables.

**Symptom:**
```
Module 'moment' is disallowed
```
Even though `NODE_FUNCTION_ALLOW_EXTERNAL=moment,axios,lodash` is set in docker-compose.

**Root Cause:**
```dockerfile
# ❌ WRONG - This overrides docker-compose env vars with empty string
"env-overrides": {
    "NODE_FUNCTION_ALLOW_EXTERNAL": "${JS_ALLOW}",  # Empty at runtime!
    "N8N_RUNNERS_EXTERNAL_ALLOW": "${PY_ALLOW}"     # Empty at runtime!
}
```

**Solution:**
```dockerfile
# ✅ CORRECT - Only override what's necessary
"env-overrides": {
    "N8N_RUNNERS_HEALTH_CHECK_SERVER_HOST": "0.0.0.0",
    "PYTHONPATH": "/opt/runners/task-runner-python"
}
# Let docker-compose env vars be the single source of truth
```

**Why This Happens:**
- Build args (${JS_ALLOW}) are only available at Docker BUILD time
- env-overrides are evaluated at Docker RUN time
- Result: variables are empty/undefined at runtime
- Empty string overrides docker-compose environment variables

**Railway Deployment Impact:**
- DO NOT use env-overrides for allow-lists
- Only use env-overrides for static configuration
- Use Railway service environment variables for dynamic configuration

---

## 🏗️ Architecture Decisions & Rationale

### Multi-Stage Docker Build

**Why:** Separates concerns and reduces final image size
- Stage 1: Build JavaScript dependencies
- Stage 2: Build Python dependencies
- Stage 3: Generate configuration
- Stage 4: Assemble final image

**Benefits:**
- Build tools not included in final image
- Can build JS and Python in parallel
- Easy to update individual stages

### Single Source of Truth Pattern

**Principle:** Environment variables control BOTH installation and runtime behavior.

**Implementation:**
```bash
# .env file is the ONLY place to define dependencies
JS_PACKAGES=moment@2.30.1,axios@^1.7.0
JS_ALLOW_LIST=moment,axios

# Docker-compose.yml reads from .env
build:
  args:
    JS_PACKAGES: ${JS_PACKAGES}
environment:
  - NODE_FUNCTION_ALLOW_EXTERNAL=${JS_ALLOW_LIST}
```

**Benefits:**
- No configuration duplication
- Easy to update dependencies
- Clear dependency tracking

**Railway Migration:**
- Replace .env with Railway environment variables
- Same variable names, different source
- Zero code changes needed

---

## 🔒 Security Best Practices

### 1. Minimize Dependencies

**Principle:** Only install what you absolutely need.

```bash
# ❌ BAD - Installing everything "just in case"
JS_PACKAGES=moment,axios,lodash,date-fns,uuid,crypto-js,jsonwebtoken,bcrypt,...

# ✅ GOOD - Only what's needed for specific workflows
JS_PACKAGES=moment@2.30.1,axios@^1.7.0
```

**Why:**
- Smaller attack surface
- Faster builds
- Lower memory usage
- Easier security audits

### 2. Pin Versions

**Principle:** Always use specific versions, not "latest".

```bash
# ❌ RISKY - Could break on updates
PY_PACKAGES=requests,python-dateutil

# ✅ SAFE - Reproducible builds
PY_PACKAGES=requests==2.31.0,python-dateutil==2.8.2
```

**Why:**
- Reproducible builds
- Avoid breaking changes
- Security audit trail
- Controlled updates

### 3. Standard Library Allow-List

**Principle:** Explicitly enable standard library modules, don't use wildcards.

```bash
# ❌ RISKY - Allows ALL Python stdlib
PY_STDLIB_ALLOW=*

# ✅ SAFE - Only what's needed
PY_STDLIB_ALLOW=json,datetime,math,random
```

**Why:**
- Prevents accidental use of dangerous modules (sys, subprocess, os)
- Clear documentation of what code can do
- Easier security review

### 4. Regular Updates

**Principle:** Keep dependencies updated for security patches.

**Process:**
1. Monitor CVE databases for your dependencies
2. Test updates in local POC first
3. Update version numbers in .env
4. Rebuild with `--no-cache`
5. Run full test suite
6. Deploy to staging before production

---

## 🧪 Testing & Verification

### Build-Time Verification

**1. Check packages are installed:**
```bash
# JavaScript
docker exec <container> ls /opt/runners/task-runner-javascript/node_modules/

# Python
docker exec <container> ls /opt/runners/task-runner-python/.venv/lib/python3.13/site-packages/
```

**2. Check Python version match:**
```bash
# Base image Python version
docker run --rm ghcr.io/n8n-io/runners:latest \
  /opt/runners/task-runner-python/.venv/bin/python --version

# Build stage Python version
docker run --rm python:3.13-alpine python --version

# Must match!
```

**3. Verify configuration:**
```bash
docker exec <container> cat /etc/n8n-task-runners.json
```

### Runtime Verification

**1. Test package imports:**
```bash
# JavaScript
docker exec <container> node -e "const moment = require('moment'); console.log(moment.version)"

# Python
docker exec <container> /opt/runners/task-runner-python/.venv/bin/python -c \
  "import requests; print(requests.__version__)"
```

**2. Check allow-lists:**
```bash
docker exec <container> env | grep ALLOW
```

**3. Test n8n Code nodes:**
- Create workflow with Code node
- Test JavaScript code with allowed packages
- Test Python code with allowed packages
- Verify security restrictions work (try importing sys)

### End-to-End Testing

**JavaScript Test Script:**
```javascript
// Save as railway-deployment/local-poc/code-test.js
const moment = require('moment');
const axios = require('axios');
const _ = require('lodash');

const results = {
  moment: {
    version: moment.version,
    formatted: moment().format('YYYY-MM-DD HH:mm:ss'),
    relative: moment().subtract(7, 'days').fromNow()
  },
  axios: {
    tested: 'GitHub API',
    status: 'success'
  },
  lodash: {
    version: _.VERSION,
    sample: _.sample([1, 2, 3, 4, 5])
  }
};

return [{ json: results }];
```

**Python Test Script:**
```python
# Save as railway-deployment/local-poc/code-test.py
import requests
from dateutil import parser
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
import json
import math
import random

def verify_dependencies():
    results = {
        'status': '✅ ALL DEPENDENCIES WORKING',
        'packages': {},
        'tests': {}
    }

    # Test requests
    try:
        response = requests.get('https://api.github.com/repos/n8n-io/n8n', timeout=5)
        repo_data = response.json()
        results['packages']['requests'] = {
            'version': requests.__version__,
            'test': f'GitHub API status: {response.status_code}',
            'installed': '✅'
        }
    except Exception as e:
        results['packages']['requests'] = {'error': str(e), 'installed': '❌'}

    # Test dateutil
    try:
        iso_date = parser.parse("2025-10-22T14:30:00Z")
        future_date = datetime.now() + relativedelta(months=3)
        results['packages']['dateutil'] = {
            'test': 'Date parsing and manipulation',
            'parsed': iso_date.isoformat(),
            'installed': '✅'
        }
    except Exception as e:
        results['packages']['dateutil'] = {'error': str(e), 'installed': '❌'}

    return results

return [{'json': verify_dependencies()}]
```

---

## 🚀 Railway Deployment Considerations

### 1. Environment Variables

**Railway Service Variables Required:**

**n8n Service:**
```bash
# Database
DB_TYPE=postgresdb
DB_POSTGRESDB_DATABASE=n8n
DB_POSTGRESDB_HOST=${{Postgres.RAILWAY_PRIVATE_DOMAIN}}
DB_POSTGRESDB_PORT=5432
DB_POSTGRESDB_USER=postgres
DB_POSTGRESDB_PASSWORD=${{Postgres.POSTGRES_PASSWORD}}

# Security
N8N_ENCRYPTION_KEY=${{SECRET_ENCRYPTION_KEY}}

# Task Runners
N8N_RUNNERS_ENABLED=true
N8N_RUNNERS_MODE=external
N8N_RUNNERS_BROKER_LISTEN_ADDRESS=0.0.0.0
N8N_RUNNERS_BROKER_PORT=5679
N8N_RUNNERS_AUTH_TOKEN=${{SECRET_RUNNERS_TOKEN}}
N8N_NATIVE_PYTHON_RUNNER=true
```

**Runners Service:**
```bash
# Connection
N8N_RUNNERS_TASK_BROKER_URI=http://${{n8n.RAILWAY_PRIVATE_DOMAIN}}:5679
N8N_RUNNERS_AUTH_TOKEN=${{SECRET_RUNNERS_TOKEN}}

# JavaScript Dependencies (Build Args & Runtime)
JS_PACKAGES=moment@2.30.1,axios@^1.7.0,lodash@^4.17.21
JS_ALLOW_LIST=moment,axios,lodash

# Python Dependencies (Build Args & Runtime)
PY_PACKAGES=requests==2.31.0,python-dateutil==2.8.2
PY_ALLOW_LIST=requests,dateutil
PY_STDLIB_ALLOW=json,datetime,math,random

# Allow-lists (Runtime)
NODE_FUNCTION_ALLOW_BUILTIN=*
NODE_FUNCTION_ALLOW_EXTERNAL=${{JS_ALLOW_LIST}}
N8N_RUNNERS_EXTERNAL_ALLOW=${{PY_ALLOW_LIST}}
N8N_RUNNERS_STDLIB_ALLOW=${{PY_STDLIB_ALLOW}}
```

### 2. Build Configuration

**railway.toml for runners service:**
```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile.runners"

# ⚠️ WARNING: Railway does NOT support [build.buildArgs] in railway.toml
# This was tested during POC but doesn't work in production
# Instead: Set JS_PACKAGES, PY_PACKAGES, N8N_VERSION as environment variables
# Railway automatically passes them as --build-arg when they match ARG declarations

[deploy]
healthcheckPath = "/healthz"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

**How Railway handles build arguments (discovered post-POC):**

Railway automatically passes environment variables as Docker build arguments when they match `ARG` declarations in your Dockerfile. You do NOT need `[build.buildArgs]` in railway.toml.

**Correct approach:**
1. Set environment variables in Railway Dashboard:
   - `JS_PACKAGES=moment@2.30.1,axios@^1.7.0`
   - `PY_PACKAGES=requests==2.31.0`
   - `N8N_VERSION=latest`
2. Railway automatically runs: `docker build --build-arg JS_PACKAGES="..." --build-arg PY_PACKAGES="..." ...`

See `runners/railway.toml` and `runners/README.md` for the implemented solution.

### 3. Network Configuration

**Service Dependencies:**
```
postgres -> n8n -> runners
```

**Internal Communication:**
- n8n → Postgres: Uses Railway private network
- runners → n8n: Uses Railway private network on port 5679
- External → n8n: Public domain on port 5678

**Important:** All services must be in the same Railway project for private networking.

### 4. Resource Recommendations

**n8n Service:**
- Memory: 512MB minimum, 1GB recommended
- CPU: Shared OK for low volume, dedicated for high volume

**Runners Service:**
- Memory: 1GB minimum (Python packages need more memory)
- CPU: Shared OK for most use cases
- Note: Scientific packages (numpy, pandas) need more resources

**Postgres Service:**
- Use Railway's PostgreSQL template
- Memory: 256MB minimum
- Storage: 1GB minimum, scale based on workflow count

### 5. Deployment Workflow

**Initial Deployment:**
1. Create Railway project
2. Add PostgreSQL service (from template)
3. Add n8n service (point to your repo)
4. Add runners service (point to your repo, specify Dockerfile.runners)
5. Configure environment variables (copy from .env)
6. Use Railway's shared variables for secrets
7. Deploy all services
8. Wait for health checks to pass
9. Access n8n via Railway public domain

**Updating Dependencies:**
1. Update JS_PACKAGES or PY_PACKAGES in Railway environment variables
2. Trigger manual redeploy of runners service
3. Railway will rebuild with new dependencies
4. Wait for build to complete (check build logs)
5. Verify packages in new container
6. Test in n8n Code nodes

**Important:** Updating dependencies requires REBUILD, not just restart!

---

## 🐛 Troubleshooting Guide

### Issue: "Module 'X' is disallowed"

**Check:**
1. Package installed? `docker exec <container> ls <path>/node_modules/` or `<path>/site-packages/`
2. Allow-list correct? `docker exec <container> env | grep ALLOW`
3. Config file correct? `docker exec <container> cat /etc/n8n-task-runners.json`
4. No env-overrides conflict? Check Dockerfile doesn't override allow-lists

**Fix:**
- If not installed: Add to JS_PACKAGES/PY_PACKAGES, rebuild
- If not allowed: Add to JS_ALLOW_LIST/PY_ALLOW_LIST, restart
- If env-override conflict: Remove from Dockerfile, rebuild

### Issue: "No module named 'X'" (Python)

**Check:**
1. Python version match? Compare build stage vs runner
2. Package installed? `docker exec <container> ls .../site-packages/`
3. Import name correct? (e.g., python-dateutil → import dateutil)
4. Path correct? `docker exec <container> python -c "import sys; print(sys.path)"`

**Fix:**
- Version mismatch: Update Dockerfile to use python:3.13-alpine
- Wrong import name: Check package docs, update allow-list
- Wrong path: Update COPY command in Dockerfile

### Issue: "Import of standard library module 'sys' is disallowed"

**This is not a bug - it's a security feature!**

**Blocked modules:** sys, subprocess, os, __import__

**Workaround:**
- Use allowed packages instead (requests instead of urllib + sys)
- Use allowed stdlib modules (json, datetime, math, random)
- Redesign workflow to avoid system access

### Issue: Build takes 10+ minutes

**Cause:** Scientific Python packages (numpy, pandas, scipy)

**Solutions:**
1. Use lightweight alternatives if possible
2. Accept longer build time (Railway charges for build time)
3. Cache layers properly (Railway does this automatically)
4. Pre-build base image with scientific packages

### Issue: "Failed building wheel for pandas"

**Cause:** Missing build dependencies

**Fix:** Ensure Dockerfile includes:
```dockerfile
apk add --no-cache gcc g++ gfortran musl-dev linux-headers openblas-dev lapack-dev
```

### Issue: Old configuration still active after update

**Cause:** Docker layer caching

**Fix:**
```bash
# Local: Clear cache and rebuild
docker-compose build --no-cache runners
docker-compose up -d runners

# Railway: Trigger rebuild
# Go to service → Settings → Rebuild
```

### Issue: n8n won't start - encryption key error

**Cause:** Changed N8N_ENCRYPTION_KEY with existing data

**Fix:**
```bash
# Local: Clear volumes
docker-compose down -v
docker-compose up -d

# Railway: Delete database service and recreate
# WARNING: This deletes all workflows!
```

---

## 📋 Deployment Checklist

### Pre-Deployment

- [ ] Review Python version compatibility (use 3.13)
- [ ] List all required dependencies (JS and Python)
- [ ] Test dependencies locally with POC
- [ ] Document expected build time
- [ ] Review security sandbox restrictions
- [ ] Create deployment plan document

### Railway Configuration

- [ ] Create Railway project
- [ ] Add PostgreSQL service
- [ ] Add n8n service with correct environment variables
- [ ] Add runners service with Dockerfile.runners
- [ ] Configure all environment variables
- [ ] Set up shared variables for secrets
- [ ] Configure resource limits
- [ ] Set up health checks

### Testing

- [ ] Verify all services start successfully
- [ ] Check service logs for errors
- [ ] Verify runners connect to n8n
- [ ] Test JavaScript Code node with dependencies
- [ ] Test Python Code node with dependencies
- [ ] Verify security sandbox restrictions work
- [ ] Test workflow execution end-to-end

### Documentation

- [ ] Document environment variable setup
- [ ] Document dependency update process
- [ ] Document troubleshooting procedures
- [ ] Document security restrictions for users
- [ ] Document expected build times
- [ ] Create user guide for Code nodes

### Monitoring

- [ ] Set up Railway deployment notifications
- [ ] Monitor build times
- [ ] Monitor service health
- [ ] Monitor resource usage
- [ ] Set up error alerting

---

## 🎯 Key Takeaways for Railway Deployment

1. **Python Version is Critical** - Always use Python 3.13 to match n8n runners
2. **Two-Variable System is Required** - Separate install (with versions) from allow-lists (without versions)
3. **Security Sandbox is Not Optional** - Design workflows around restrictions, don't try to bypass them
4. **Build Time Varies Widely** - 1 minute for lightweight packages, 10+ for scientific packages
5. **env-overrides Can Cause Issues** - Don't use for allow-lists, let Railway env vars control them
6. **Testing is Essential** - Always test in local POC before Railway deployment
7. **Documentation is Critical** - Users need to understand limitations and restrictions

---

## 📚 Additional Resources

- [n8n Task Runners Documentation](https://docs.n8n.io/hosting/configuration/task-runners/)
- [Railway Documentation](https://docs.railway.app/)
- [Docker Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Python Packaging Guide](https://packaging.python.org/)
- [npm Package Versions](https://docs.npmjs.com/about-semantic-versioning)

---

**Document Version:** 1.0
**Last Updated:** 2025-10-22
**Tested With:** n8n:latest, runners:latest (Python 3.13)
**Author:** POC Local Testing Team
