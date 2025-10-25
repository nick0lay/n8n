# n8n Railway Quick Start with Task Runners

## 🚀 5-Minute Setup

### Prerequisites
- Railway account (sign up at https://railway.com)
- GitHub account (optional, for custom images)

### Step 1: Create Project on Railway

1. Go to https://railway.com/dashboard
2. Click **"New Project"**
3. Select **"Provision PostgreSQL"**

### Step 2: Add n8n Service

1. Click **"+ New"** in the project
2. Select **"Docker Image"**
3. Enter image: `ghcr.io/n8n-io/n8n:latest`
4. Click **"Add Service"**

### Step 3: Configure n8n Environment

Click on the n8n service → **Variables** tab → Add:

```bash
# Database (click to select reference)
DB_TYPE=postgresdb
DB_POSTGRESDB_HOST=${{Postgres.PGHOST}}
DB_POSTGRESDB_PORT=${{Postgres.PGPORT}}
DB_POSTGRESDB_DATABASE=${{Postgres.PGDATABASE}}
DB_POSTGRESDB_USER=${{Postgres.PGUSER}}
DB_POSTGRESDB_PASSWORD=${{Postgres.PGPASSWORD}}

# Core Config
N8N_HOST=${{RAILWAY_PUBLIC_DOMAIN}}
N8N_PROTOCOL=https
WEBHOOK_URL=https://${{RAILWAY_PUBLIC_DOMAIN}}/

# Security (generate random values!)
N8N_ENCRYPTION_KEY=YOUR_RANDOM_32_CHAR_STRING_HERE

# Task Runners
N8N_RUNNERS_ENABLED=true
N8N_RUNNERS_MODE=external
N8N_RUNNERS_BROKER_LISTEN_ADDRESS=0.0.0.0
N8N_RUNNERS_AUTH_TOKEN=YOUR_SECURE_RANDOM_TOKEN_HERE
N8N_NATIVE_PYTHON_RUNNER=true
```

**Generate secure values:**
```bash
# Encryption key
openssl rand -base64 32

# Auth token
openssl rand -base64 24
```

### Step 4: Enable Public Access

1. Click **Settings** tab
2. Click **Networking**
3. Click **Generate Domain**
4. Note your URL: `xxx-yyy.railway.app`

### Step 5: Add Task Runners Service

1. Click **"+ New"** in the project
2. Select **"Docker Image"**
3. Enter image: `ghcr.io/n8n-io/runners:latest`
4. Click **"Add Service"**

### Step 6: Configure Runners Environment

Click on the runners service → **Variables** tab → Add:

```bash
# Connection (IMPORTANT: use .railway.internal!)
N8N_RUNNERS_TASK_BROKER_URI=http://n8n.railway.internal:5679

# Auth (MUST match n8n's token!)
N8N_RUNNERS_AUTH_TOKEN=SAME_TOKEN_AS_N8N_SERVICE

# Allowed packages (customize as needed)
NODE_FUNCTION_ALLOW_EXTERNAL=moment
N8N_RUNNERS_EXTERNAL_ALLOW=
```

**Keep this service PRIVATE** (no public domain needed)

### Step 7: Access n8n

1. Wait for both services to deploy (green status)
2. Open your n8n URL: `https://xxx-yyy.railway.app`
3. Create your admin account
4. You're done! 🎉

## 🧪 Test Task Runners

### Test JavaScript

1. Create new workflow
2. Add **Code** node
3. Paste this code:

```javascript
const moment = require('moment');
const now = moment();

return [{
  json: {
    message: 'JavaScript task runner works!',
    timestamp: now.format('YYYY-MM-DD HH:mm:ss'),
    unix: now.unix()
  }
}];
```

4. Click **"Execute Node"**
5. Should see output without errors

### Test Python

1. Add another **Code** node
2. Change language to **Python**
3. Paste this code:

```python
from datetime import datetime
import json

now = datetime.now()

return [{
    'json': {
        'message': 'Python task runner works!',
        'timestamp': now.isoformat(),
        'year': now.year
    }
}]
```

4. Click **"Execute Node"**
5. Should see output without errors

## ⚙️ Adding Custom Packages

### Quick Method (Pre-installed Only)

Update runners service environment variables:

```bash
# For JavaScript
NODE_FUNCTION_ALLOW_EXTERNAL=moment,axios,lodash

# For Python
N8N_RUNNERS_EXTERNAL_ALLOW=numpy,pandas
```

**Note:** Only works for packages already in the image!

### Full Method (Any Package)

See [RAILWAY_DEPLOYMENT_GUIDE.md](./RAILWAY_DEPLOYMENT_GUIDE.md) for building custom images.

## 🔧 Common Issues

### "Cannot find module 'xxx'"

**Solution:** Package not in official image. Either:
1. Check available packages: See [Option 2 in guide](./RAILWAY_DEPLOYMENT_GUIDE.md#option-2-custom-docker-image)
2. Build custom image with your packages

### Task runner not connecting

**Check:**
1. Auth token matches in both services
2. Broker URI uses `.railway.internal` (NOT public URL)
3. Both services are running (green status)

**View logs:**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# View n8n logs
railway logs -s n8n

# View runners logs
railway logs -s runners
```

### Version mismatch

**Solution:** Use same version for both:
```bash
# Instead of :latest
ghcr.io/n8n-io/n8n:1.75.0
ghcr.io/n8n-io/runners:1.75.0
```

## 📊 Cost Estimate

| Component | Monthly Cost |
|-----------|-------------|
| PostgreSQL | $5-8 |
| n8n Main | $3-7 |
| Task Runners | $2-5 |
| **Total** | **$10-20** |

Railway free tier: $5/month credit included

## 🎯 Next Steps

1. ✅ **Read full guide:** [RAILWAY_DEPLOYMENT_GUIDE.md](./RAILWAY_DEPLOYMENT_GUIDE.md)
2. 🔒 **Secure your instance:** Setup user authentication
3. 📦 **Add custom packages:** Build custom runner image
4. 🔗 **Connect integrations:** Add credentials for your tools
5. 🤖 **Build workflows:** Start automating!

## 📚 Resources

- [Full Deployment Guide](./RAILWAY_DEPLOYMENT_GUIDE.md)
- [Runners Service Setup](../runners/README.md)
- [Custom Dockerfile](../runners/Dockerfile)
- [Local Testing Guide](../local-poc/README.md)
- [n8n Documentation](https://docs.n8n.io)
- [Railway Documentation](https://docs.railway.com)

## 💡 Pro Tips

1. **Use version tags** instead of `latest` for stability
2. **Enable backups** for PostgreSQL in Railway settings
3. **Monitor usage** to stay within free tier
4. **Test locally** with docker-compose before deploying
5. **Keep secrets secure** - never commit tokens to git

## 🆘 Get Help

- **Railway:** https://station.railway.com
- **n8n Community:** https://community.n8n.io
- **GitHub Issues:** https://github.com/n8n-io/n8n/issues

---

**Setup Time:** ~5 minutes
**Difficulty:** Beginner
**Status:** Production Ready (JavaScript), Beta (Python)
