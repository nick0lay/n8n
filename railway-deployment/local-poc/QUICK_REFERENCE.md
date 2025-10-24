# Quick Reference: Adding Packages

## Two-Variable System

When adding packages, you must update **TWO** environment variables:

| Variable | Purpose | Format | Example |
|----------|---------|--------|---------|
| `JS_PACKAGES` | **Install** packages (build time) | `package@version` | `moment@2.30.1,uuid@^9.0.0` |
| `JS_ALLOW_LIST` | **Enable** packages (runtime) | `package` (no version) | `moment,uuid` |
| `PY_PACKAGES` | **Install** packages (build time) | `package==version` | `numpy==2.3.2,pandas==2.0.0` |
| `PY_ALLOW_LIST` | **Enable** packages (runtime) | `package` (no version) | `numpy,pandas` |

## Why Two Variables?

1. **Build Args** (`*_PACKAGES`) - Tell Docker **what to install** during image build
2. **Allow-List** (`*_ALLOW_LIST`) - Tell n8n runners **what can be used** at runtime

This separation provides:
- ✅ **Security** - Install a package for testing but don't allow it in production
- ✅ **Flexibility** - Allow packages from base image without rebuilding
- ✅ **Control** - Explicit list of what code nodes can import

## Step-by-Step: Adding a Package

### Example: Adding `uuid` package to JavaScript

#### 1. Edit `.env` file

```bash
# BEFORE
JS_PACKAGES=moment@2.30.1,axios@^1.7.0,lodash@^4.17.21
JS_ALLOW_LIST=moment,axios,lodash

# AFTER
JS_PACKAGES=moment@2.30.1,axios@^1.7.0,lodash@^4.17.21,uuid@^9.0.0
JS_ALLOW_LIST=moment,axios,lodash,uuid
```

#### 2. Rebuild runner image

```bash
docker-compose build runners
```

#### 3. Restart runners service

```bash
docker-compose up -d runners
```

#### 4. Test in n8n Code node

```javascript
const uuid = require('uuid');
return [{ json: { id: uuid.v4() } }];
```

## Common Package Name Differences

Some Python packages have different **install names** vs **import names**:

| Install Name (use in `PY_PACKAGES`) | Import Name (use in `PY_ALLOW_LIST`) |
|--------------------------------------|--------------------------------------|
| `python-dateutil==2.8.2` | `dateutil` |
| `beautifulsoup4==4.12.3` | `bs4` |
| `Pillow==10.2.0` | `PIL` |
| `scikit-learn==1.4.0` | `sklearn` |

**Rule:** Use the name that appears in `import` statements for the allow-list.

## Quick Commands

### Check what's installed
```bash
# JavaScript packages
docker exec local-poc-runners-1 ls /opt/runners/task-runner-javascript/node_modules

# Python packages
docker exec local-poc-runners-1 /opt/runners/task-runner-python/.venv/bin/pip list
```

### Check allow-list configuration
```bash
# Check environment variables
docker exec local-poc-runners-1 printenv | grep ALLOW

# Check config file
docker exec local-poc-runners-1 cat /etc/n8n-task-runners.json | grep -A 3 "env-overrides"
```

### Check runner logs
```bash
docker-compose logs runners | tail -50
```

## Troubleshooting

### Error: "Module 'xxx' is disallowed"

**Cause:** Package is installed but not in allow-list

**Solution:** Add package name to `*_ALLOW_LIST` variable and restart:
```bash
# Edit .env: add 'xxx' to JS_ALLOW_LIST or PY_ALLOW_LIST
docker-compose up -d runners
```

### Error: "Cannot find module 'xxx'"

**Cause:** Package is in allow-list but not installed

**Solution:** Add package to `*_PACKAGES` and rebuild:
```bash
# Edit .env: add 'xxx@version' to JS_PACKAGES or PY_PACKAGES
docker-compose build runners
docker-compose up -d runners
```

## Example: Complete Workflow

Let's add `jsonwebtoken` (JavaScript) and `pyjwt` (Python):

### 1. Edit `.env`

```bash
# JavaScript
JS_PACKAGES=moment@2.30.1,axios@^1.7.0,lodash@^4.17.21,jsonwebtoken@^9.0.2
JS_ALLOW_LIST=moment,axios,lodash,jsonwebtoken

# Python
PY_PACKAGES=requests==2.31.0,python-dateutil==2.8.2,pyjwt==2.8.0
PY_ALLOW_LIST=requests,dateutil,pyjwt
```

### 2. Rebuild

```bash
docker-compose build runners
```

### 3. Restart

```bash
docker-compose up -d runners
```

### 4. Test JavaScript JWT

```javascript
const jwt = require('jsonwebtoken');

const token = jwt.sign(
  { userId: 123, email: 'user@example.com' },
  'secret-key',
  { expiresIn: '1h' }
);

return [{ json: { token } }];
```

### 5. Test Python JWT

```python
import jwt
from datetime import datetime, timedelta

payload = {
    'userId': 123,
    'email': 'user@example.com',
    'exp': datetime.utcnow() + timedelta(hours=1)
}

token = jwt.encode(payload, 'secret-key', algorithm='HS256')

return [{'json': {'token': token}}]
```

## Best Practices

1. **Start Small** - Begin with lightweight packages, add heavy ones (numpy/pandas) only if needed
2. **Keep in Sync** - Always update both `*_PACKAGES` and `*_ALLOW_LIST` together
3. **Test Locally** - Verify packages work locally before deploying to Railway
4. **Document** - Keep a list of why each package is needed
5. **Security** - Only allow packages you actually use

## Quick Copy-Paste Examples

### Lightweight Data Processing

```bash
JS_PACKAGES=moment@2.30.1,axios@^1.7.0,lodash@^4.17.21
JS_ALLOW_LIST=moment,axios,lodash

PY_PACKAGES=requests==2.31.0,python-dateutil==2.8.2
PY_ALLOW_LIST=requests,dateutil
```

### With Authentication/Security

```bash
JS_PACKAGES=moment@2.30.1,axios@^1.7.0,lodash@^4.17.21,jsonwebtoken@^9.0.2,crypto-js@^4.2.0
JS_ALLOW_LIST=moment,axios,lodash,jsonwebtoken,crypto-js

PY_PACKAGES=requests==2.31.0,python-dateutil==2.8.2,pyjwt==2.8.0,cryptography==42.0.0
PY_ALLOW_LIST=requests,dateutil,pyjwt,cryptography
```

### Scientific Computing (Heavy Build!)

```bash
JS_PACKAGES=moment@2.30.1,axios@^1.7.0,lodash@^4.17.21
JS_ALLOW_LIST=moment,axios,lodash

PY_PACKAGES=numpy==2.3.2,pandas==2.0.0,scipy==1.12.0,matplotlib==3.8.2
PY_ALLOW_LIST=numpy,pandas,scipy,matplotlib
```

**Note:** Scientific packages take 5-10 minutes to build!

---

**Need help?** Check the full documentation in `README.md` or use `code-test.js`/`code-test.py` for dependency verification
