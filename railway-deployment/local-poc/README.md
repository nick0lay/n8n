# n8n Task Runners - Local POC

This directory contains everything you need to run n8n with custom task runners locally using Docker Compose with **dynamic dependency management**.

## ⚠️ IMPORTANT: Read This First

**Before deploying to Railway or production, read [POC_FINDINGS.md](../docs/POC_FINDINGS.md)**

This critical findings document contains:
- 🚨 **Critical issues discovered** (Python version mismatch, security restrictions)
- 🔒 **Security sandbox limitations** (blocked imports, restricted modules)
- 🏗️ **Architecture decisions** and rationale
- 🚀 **Railway deployment guide** with environment variables
- 🐛 **Comprehensive troubleshooting** guide

Key findings you must know:
- **Python 3.13 required** - Using 3.14 will cause package import failures
- **Security restrictions** - `sys`, `subprocess`, `os` imports are blocked
- **Two-variable system** - Separate variables for install vs runtime allow-lists
- **Build dependencies** - Scientific packages need additional tools (5-10 min build)

### 📚 Related Documentation

- **[Railway Deployment](../docs/QUICK_START.md)** - Deploy to Railway in 5 minutes
- **[Full Deployment Guide](../docs/RAILWAY_DEPLOYMENT_GUIDE.md)** - Complete Railway setup
- **[Troubleshooting](../docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[Documentation Index](../docs/README.md)** - All available documentation

## 🎯 What This Does

- ✅ Runs n8n with PostgreSQL database
- ✅ Custom task runners for JavaScript and Python
- ✅ Add npm/pip packages via environment variables
- ✅ Auto-generates allow-lists from dependencies
- ✅ Easy rebuild when dependencies change

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your values
vim .env
```

**Required Changes in .env:**
- `POSTGRES_PASSWORD` - Set a secure password
- `N8N_ENCRYPTION_KEY` - Generate: `openssl rand -base64 32`
- `N8N_RUNNERS_AUTH_TOKEN` - Generate: `openssl rand -base64 32`

**Optional Changes:**
- `JS_PACKAGES` - Add your JavaScript packages
- `PY_PACKAGES` - Add your Python packages

### 2. Build and Start

```bash
# Build the custom runner image
docker-compose build

# Start all services
docker-compose up -d

# Watch logs
docker-compose logs -f
```

### 3. Access n8n

Open your browser: **http://localhost:5678**

Create your account and start building workflows!

## ⏱️ Build Time Expectations

**Initial build with defaults (~2-3 minutes):**
- JavaScript: moment, axios, lodash
- Python: requests, python-dateutil

**Adding heavy packages like numpy/pandas (~5-10 minutes):**
- Requires compiling C/C++/Fortran code
- Needs additional build tools (g++, gfortran, BLAS, LAPACK)
- Only needed if you're doing scientific computing

💡 **Tip:** Start with lightweight packages to test the setup quickly, then add heavy packages if needed.

## 📦 Adding Dependencies

**IMPORTANT:** When adding packages, you need to update **TWO variables**:

1. **`*_PACKAGES`** - Build args with versions (installs the package)
2. **`*_ALLOW_LIST`** - Runtime allow-list with names only (enables usage)

### JavaScript Packages

Edit `.env` file:

```bash
# Build args - installs packages (WITH versions)
JS_PACKAGES=moment@2.30.1,axios@^1.7.0,lodash@^4.17.21,uuid@^9.0.0

# Allow-list - enables usage (WITHOUT versions)
JS_ALLOW_LIST=moment,axios,lodash,uuid
```

Then rebuild:

```bash
docker-compose build runners
docker-compose up -d runners
```

### Python Packages

Edit `.env` file:

```bash
# Example 1: Lightweight packages (fast build ~1 min)
PY_PACKAGES=requests==2.31.0,python-dateutil==2.8.2,pyjwt==2.8.0
PY_ALLOW_LIST=requests,dateutil,pyjwt

# Example 2: Heavy packages (slower build ~5-10 min)
PY_PACKAGES=numpy==2.3.2,pandas==2.0.0,scipy==1.12.0
PY_ALLOW_LIST=numpy,pandas,scipy
```

**Note:** Package name vs import name differences:
- `python-dateutil` → install name, but `dateutil` → import name (use `dateutil` in allow-list)
- `beautifulsoup4` → install name, but `bs4` → import name (use `bs4` in allow-list)

Then rebuild:

```bash
docker-compose build runners
docker-compose up -d runners
```

## 🧪 Testing

### Test JavaScript Code Node

1. Create a new workflow in n8n
2. Add a **Code** node
3. Select **JavaScript**
4. Test with this code:

```javascript
const moment = require('moment');
const axios = require('axios');
const _ = require('lodash');

const result = {
  currentTime: moment().format('YYYY-MM-DD HH:mm:ss'),
  message: 'JavaScript dependencies working!',
  lodashVersion: _.VERSION,
  packagesLoaded: ['moment', 'axios', 'lodash']
};

return [{ json: result }];
```

**Expected Output:**
```json
{
  "currentTime": "2025-10-22 14:30:45",
  "message": "JavaScript dependencies working!",
  "lodashVersion": "4.17.21",
  "packagesLoaded": ["moment", "axios", "lodash"]
}
```

### Test Python Code Node

1. Add another **Code** node
2. Select **Python**
3. Test with this code (using lightweight defaults):

```python
import requests
from dateutil import parser
import datetime

# Test HTTP request
response = requests.get('https://api.github.com/repos/n8n-io/n8n')

# Test date parsing
date_str = "2025-10-22T14:30:00Z"
parsed_date = parser.parse(date_str)

data = {
    'message': 'Python dependencies working!',
    'github_stars': response.json()['stargazers_count'],
    'parsed_date': parsed_date.isoformat(),
    'packages_loaded': ['requests', 'dateutil']
}

return [{'json': data}]
```

**Expected Output:**
```json
{
  "message": "Python dependencies working!",
  "github_stars": 45000,
  "parsed_date": "2025-10-22T14:30:00+00:00",
  "packages_loaded": ["requests", "dateutil"]
}
```

### Test HTTP Request with Axios

```javascript
const axios = require('axios');

async function fetchData() {
  const response = await axios.get('https://api.github.com/users/n8n-io');

  return [{
    json: {
      username: response.data.login,
      name: response.data.name,
      publicRepos: response.data.public_repos,
      followers: response.data.followers
    }
  }];
}

return await fetchData();
```

### Test Data Processing with Pandas (Optional)

**Note:** numpy and pandas require additional build dependencies and take 5-10 minutes to build.

First, add to `.env`:
```bash
PY_PACKAGES=numpy==2.3.2,pandas==2.0.0,requests==2.31.0
```

Then rebuild (this will take several minutes):
```bash
docker-compose build runners
docker-compose up -d runners
```

Once built, test with:
```python
import pandas as pd
import numpy as np

# Create sample data
df = pd.DataFrame({
    'product': ['A', 'B', 'C', 'D', 'E'],
    'sales': [100, 150, 80, 200, 120],
    'profit': [20, 30, 15, 45, 25]
})

# Calculate metrics
total_sales = int(df['sales'].sum())
avg_profit = float(df['profit'].mean())
top_product = df.loc[df['sales'].idxmax(), 'product']

result = {
    'total_sales': total_sales,
    'average_profit': avg_profit,
    'top_product': top_product,
    'data': df.to_dict('records')
}

return [{'json': result}]
```

## 🔧 Useful Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f runners
docker-compose logs -f n8n
docker-compose logs -f postgres

# Last 50 lines
docker-compose logs --tail=50 runners
```

### Check Runner Configuration

```bash
# View the generated config
docker exec local-poc-runners-1 cat /etc/n8n-task-runners.json

# Check installed JavaScript packages
docker exec local-poc-runners-1 ls /opt/runners/task-runner-javascript/node_modules

# Check installed Python packages
docker exec local-poc-runners-1 /opt/runners/task-runner-python/.venv/bin/pip list
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart runners
docker-compose restart n8n
```

### Rebuild

```bash
# Rebuild runners (after dependency changes)
docker-compose build runners

# Force rebuild (no cache)
docker-compose build --no-cache runners

# Rebuild and restart
docker-compose up -d --build runners
```

### Stop and Clean Up

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes all data!)
docker-compose down -v

# Remove custom runner image
docker rmi n8n-runners:custom
```

## 🐛 Troubleshooting

### Problem: "Cannot find module 'package-name'"

**Cause:** Package not installed or not in allow-list

**Solution:**
1. Check if package is in `.env` file
2. Rebuild: `docker-compose build runners`
3. Restart: `docker-compose up -d runners`
4. Check build logs: `docker-compose logs runners`

### Problem: "Runners not connecting to broker"

**Cause:** Auth token mismatch or n8n not started

**Solution:**
1. Check `N8N_RUNNERS_AUTH_TOKEN` matches in `.env`
2. Check n8n logs: `docker-compose logs n8n | grep -i "task broker"`
3. Restart runners: `docker-compose restart runners`

### Problem: Build fails with "Package not found"

**Cause:** Invalid package name or version

**Solution:**
1. Check package exists on npm or PyPI
2. Verify version syntax: npm uses `@^1.0.0`, pip uses `==1.0.0`
3. Check build logs: `docker-compose logs runners`

### Problem: Python import fails

**Cause:** Package name differs from import name

**Solution:**
- Package `python-dateutil` imports as `dateutil`
- Package `beautifulsoup4` imports as `bs4`
- Check package documentation for import name

### Problem: High memory usage

**Cause:** Too many concurrent tasks or large packages

**Solution:**
1. Reduce `N8N_RUNNERS_MAX_CONCURRENCY` in `.env`
2. Increase `N8N_RUNNERS_TASK_TIMEOUT` if tasks are complex
3. Monitor: `docker stats`

## 📊 Service Health Checks

```bash
# Check all services are healthy
docker-compose ps

# Expected output:
# NAME              STATUS
# postgres          Up (healthy)
# n8n               Up (healthy)
# runners           Up (healthy)
```

## 🔍 Debugging

### Enable Debug Logging

Edit `.env`:

```bash
# Add to n8n environment
N8N_LOG_LEVEL=debug

# Add to runners environment
N8N_RUNNERS_LAUNCHER_LOG_LEVEL=debug
```

Restart:

```bash
docker-compose up -d
docker-compose logs -f
```

### Inspect Runner Container

```bash
# Enter runner container
docker exec -it local-poc-runners-1 sh

# Inside container:
ls /opt/runners/task-runner-javascript/node_modules
ls /opt/runners/task-runner-python/.venv/lib/python3.14/site-packages
cat /etc/n8n-task-runners.json
```

### Test Package Installation

```bash
# Test JavaScript package
docker exec local-poc-runners-1 node -e "console.log(require('moment')().format())"

# Test Python package
docker exec local-poc-runners-1 /opt/runners/task-runner-python/.venv/bin/python -c "import numpy; print(numpy.__version__)"
```

## 📚 Popular Package Examples

### JavaScript

```bash
# Date/Time
JS_PACKAGES=moment@2.30.1,date-fns@^2.30.0,dayjs@^1.11.10

# HTTP/API
JS_PACKAGES=axios@^1.7.0,node-fetch@^3.3.2,got@^13.0.0

# Utilities
JS_PACKAGES=lodash@^4.17.21,ramda@^0.29.0,uuid@^9.0.0

# Cryptography
JS_PACKAGES=crypto-js@^4.2.0,bcryptjs@^2.4.3,jsonwebtoken@^9.0.2

# Data Processing
JS_PACKAGES=csv-parse@^5.5.3,xml2js@^0.6.2,cheerio@^1.0.0-rc.12
```

### Python

```bash
# Data Science
PY_PACKAGES=numpy==2.3.2,pandas==2.0.0,scipy==1.12.0

# HTTP/API
PY_PACKAGES=requests==2.31.0,httpx==0.26.0,aiohttp==3.9.1

# Data Processing
PY_PACKAGES=openpyxl==3.1.2,beautifulsoup4==4.12.3,lxml==5.1.0

# Cryptography
PY_PACKAGES=cryptography==42.0.0,pyjwt==2.8.0,bcrypt==4.1.2

# Date/Time
PY_PACKAGES=python-dateutil==2.8.2,pytz==2024.1,arrow==1.3.0
```

## 🚀 Next Steps

Once you've validated the POC locally:

1. ✅ Test all your custom packages
2. ✅ Verify performance and resource usage
3. ✅ Review security sandbox restrictions
4. ✅ Read [POC_FINDINGS.md](./POC_FINDINGS.md) thoroughly
5. 🚀 Deploy to Railway using the Railway deployment guide in POC_FINDINGS.md

## 📖 Reference

**Essential Documentation:**
- **[POC_FINDINGS.md](./POC_FINDINGS.md)** - Critical findings, security issues, Railway deployment guide
- **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - Two-variable system quick reference
- **[../local-deployment-plan.md](../local-deployment-plan.md)** - Original deployment strategy

**External Resources:**
- [n8n Task Runners Docs](https://docs.n8n.io/hosting/configuration/task-runners/)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [npm package search](https://www.npmjs.com/)
- [PyPI package search](https://pypi.org/)

---

**Last Updated:** 2025-10-22
**Status:** Ready for local testing
