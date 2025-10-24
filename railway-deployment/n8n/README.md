# n8n Main Service

This service runs the main n8n instance using the official Docker image.

## Quick Setup

### 1. Prerequisites
- Railway account
- PostgreSQL service already created in your Railway project

### 2. Create Service in Railway

1. Go to your Railway project
2. Click "New Service" → "Docker Image"
3. Enter image: `ghcr.io/n8n-io/n8n:latest`
4. Service will be created and ready for configuration

**Why Docker Image deployment?**
- n8n uses official pre-built image (no custom build needed)
- All configuration done via environment variables
- Simpler to maintain and update
- No need for railway.toml file

### 3. Configure Environment Variables

Go to service **Variables** tab and add:

#### Database Configuration (use Railway references)

```bash
DB_TYPE=postgresdb
DB_POSTGRESDB_HOST=${{Postgres.RAILWAY_PRIVATE_DOMAIN}}
DB_POSTGRESDB_PORT=${{Postgres.PGPORT}}
DB_POSTGRESDB_DATABASE=${{Postgres.PGDATABASE}}
DB_POSTGRESDB_USER=${{Postgres.PGUSER}}
DB_POSTGRESDB_PASSWORD=${{Postgres.PGPASSWORD}}
```

#### n8n Core Configuration

```bash
N8N_HOST=${{RAILWAY_PUBLIC_DOMAIN}}
N8N_PROTOCOL=https
N8N_PORT=5678
WEBHOOK_URL=https://${{RAILWAY_PUBLIC_DOMAIN}}/
```

#### Security (generate secure values)

```bash
# Generate with: openssl rand -base64 32
N8N_ENCRYPTION_KEY=${{secret(32, "abcdef0123456789")}}

# Generate with: openssl rand -base64 32
# Use Railway "Shared Variable" to sync with runners service
N8N_RUNNERS_AUTH_TOKEN=${{secret(32, "abcdef0123456789")}}
```

#### Task Runners Configuration

```bash
N8N_RUNNERS_ENABLED=true
N8N_RUNNERS_MODE=external
N8N_RUNNERS_BROKER_LISTEN_ADDRESS=0.0.0.0
N8N_RUNNERS_BROKER_PORT=5679
N8N_NATIVE_PYTHON_RUNNER=true
```

#### Optional Configuration

```bash
N8N_LOG_LEVEL=info
GENERIC_TIMEZONE=America/New_York
```

### 4. Enable Public Domain

1. Go to service **Settings**
2. Enable **Public Networking**
3. Railway will generate a public URL

### 5. Deploy

Click "Deploy" - Railway will:
1. Pull official n8n Docker image
2. Configure with your environment variables
3. Connect to PostgreSQLб
4. Start n8n with task broker enabled

## Service Dependencies

This service requires:
1. **PostgreSQL** (create first) - For data persistence
2. **Task Runners** (create after n8n) - For code execution

## Files

- **`README.md`** - This file (service setup documentation)

## Environment Variables

### Required

| Variable | Purpose | Example |
|----------|---------|---------|
| `DB_TYPE` | Database type | `postgresdb` |
| `DB_POSTGRESDB_HOST` | Database host | `${{Postgres.RAILWAY_PRIVATE_DOMAIN}}` |
| `DB_POSTGRESDB_PORT` | Database port | `${{Postgres.PGPORT}}` |
| `DB_POSTGRESDB_DATABASE` | Database name | `${{Postgres.PGDATABASE}}` |
| `DB_POSTGRESDB_USER` | Database user | `${{Postgres.PGUSER}}` |
| `DB_POSTGRESDB_PASSWORD` | Database password | `${{Postgres.PGPASSWORD}}` |
| `N8N_HOST` | Public domain | `${{RAILWAY_PUBLIC_DOMAIN}}` |
| `N8N_PROTOCOL` | Protocol | `https` |
| `N8N_PORT` | Internal port | `5678` |
| `WEBHOOK_URL` | Webhook base URL | `https://${{RAILWAY_PUBLIC_DOMAIN}}/` |
| `N8N_ENCRYPTION_KEY` | Encryption key | Generate with `openssl rand -base64 32` |
| `N8N_RUNNERS_AUTH_TOKEN` | Runners auth token | Generate with `openssl rand -base64 32` |
| `N8N_RUNNERS_ENABLED` | Enable runners | `true` |
| `N8N_RUNNERS_MODE` | Runner mode | `external` |
| `N8N_RUNNERS_BROKER_LISTEN_ADDRESS` | Broker address | `0.0.0.0` |
| `N8N_RUNNERS_BROKER_PORT` | Broker port | `5679` |
| `N8N_NATIVE_PYTHON_RUNNER` | Enable Python | `true` |

### Optional

| Variable | Purpose | Default |
|----------|---------|---------|
| `N8N_LOG_LEVEL` | Logging level | `info` |
| `GENERIC_TIMEZONE` | Timezone | `America/New_York` |

## Networking

- **Public Domain**: Required for web UI access
- **Internal Port 5679**: Task broker for runners (Railway private network)
- **Internal Port 5678**: n8n web interface (exposed via public domain)

## Security Notes

### Encryption Key

⚠️ **CRITICAL**: Once set, never change `N8N_ENCRYPTION_KEY` if you have existing workflows. Changing it will make existing credentials unreadable.

**Generate new key:**
```bash
openssl rand -base64 32
```

### Runners Auth Token

This token authenticates the runners service. It must match between:
- n8n service: `N8N_RUNNERS_AUTH_TOKEN`
- Runners service: `N8N_RUNNERS_AUTH_TOKEN`

**Use Railway Shared Variables** to keep them in sync.

### Database

Railway automatically:
- Enables SSL for PostgreSQL connections
- Creates strong passwords
- Uses private networking

## Troubleshooting

### n8n won't start - encryption key error

**Cause:** Changed `N8N_ENCRYPTION_KEY` with existing data

**Fix:**
- If no important workflows: Delete and recreate PostgreSQL database
- If workflows exist: Restore original encryption key

### Task runners not connecting

**Cause:**
- Runners service not deployed yet
- Token mismatch
- Network configuration issue

**Fix:**
1. Deploy runners service
2. Verify `N8N_RUNNERS_AUTH_TOKEN` matches in both services
3. Check n8n logs: `railway logs -s n8n | grep -i "task broker"`
4. Verify runners service can reach `n8n.railway.internal:5679`

### Cannot access n8n web UI

**Cause:** Public networking not enabled

**Fix:**
1. Go to n8n service **Settings**
2. Enable **Public Networking**
3. Access via generated Railway domain

### Database connection errors

**Cause:** PostgreSQL not running or variables incorrect

**Fix:**
1. Verify PostgreSQL service is running
2. Check all `DB_POSTGRESDB_*` variables use correct Railway references
3. Check PostgreSQL logs: `railway logs -s postgres`

## Monitoring

### Check Service Health

```bash
# Railway CLI
railway logs -s n8n

# Check task broker
railway logs -s n8n | grep -i "task broker"
```

### Access n8n

```bash
# Get public URL
railway domain -s n8n
```

## Updating n8n Version

### Update to Latest

Railway automatically uses the `latest` tag by default. To update:

1. Go to service **Deployments**
2. Click **Redeploy**
3. Railway pulls latest n8n image

### Pin to Specific Version

To use a specific n8n version:

1. Go to service **Settings** → **Image**
2. Change Docker image to: `ghcr.io/n8n-io/n8n:1.75.0`
3. Click **Save** and redeploy

**Available versions:** https://github.com/n8n-io/n8n/releases

## Additional Resources

- [n8n Documentation](https://docs.n8n.io/)
- [Main Documentation](../docs/README.md)
- [Deployment Guide](../docs/DEPLOYMENT_GUIDE.md)
- [Task Runners Setup](../runners/README.md)
