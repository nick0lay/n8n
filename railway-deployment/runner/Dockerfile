# Custom n8n Task Runners with Dynamic Dependencies via Build Args
# This Dockerfile installs dependencies based on build arguments for Railway deployment
#
# Railway Usage:
#   Set build args in railway.toml:
#     JS_PACKAGES = "moment@2.30.1,axios@^1.7.0"
#     PY_PACKAGES = "requests==2.31.0,python-dateutil==2.8.2"
#
# Critical Requirements (from POC):
#   - Python 3.13 required (not 3.14) - Runner compatibility
#   - No env-overrides for allow-lists - Set via Railway environment variables
#   - Two-variable system: *_PACKAGES (install) vs *_ALLOW_LIST (runtime)

ARG N8N_VERSION=latest

# ============================================================================
# Build Arguments: Single Source of Truth for Dependencies
# ============================================================================
# JavaScript packages: package@version,package@version,...
ARG JS_PACKAGES="moment@2.30.1,axios@^1.7.0,lodash@^4.17.21"

# Python packages: package==version,package==version,...
ARG PY_PACKAGES="requests==2.31.0,python-dateutil==2.8.2"

# ============================================================================
# Stage 1: Build JavaScript Dependencies
# ============================================================================
FROM node:22.18.0-alpine AS javascript-extras

ARG JS_PACKAGES

WORKDIR /extras

# Install jq for JSON manipulation
RUN apk add --no-cache jq

# Convert comma-separated packages to package.json
# Input:  "moment@2.30.1,axios@^1.7.0,lodash@^4.17.21"
# Output: {"moment": "2.30.1", "axios": "^1.7.0", "lodash": "^4.17.21"}
RUN echo "Installing JavaScript packages: ${JS_PACKAGES}" && \
    if [ -n "${JS_PACKAGES}" ] && [ "${JS_PACKAGES}" != "" ]; then \
      echo "${JS_PACKAGES}" | tr ',' '\n' | \
      awk -F'@' 'NF==2 {print "\""$1"\": \""$2"\""}' | \
      awk 'BEGIN{print "{"} {printf "%s%s", sep, $0; sep=",\n"} END{print "\n}"}' \
      > deps.json && \
      cat deps.json && \
      jq -n \
        --arg name "task-runner-runtime-extras" \
        --arg desc "Custom dependencies for JavaScript task runner" \
        --argjson deps "$(cat deps.json)" \
        '{name: $name, description: $desc, private: true, dependencies: $deps}' \
      > package.json && \
      cat package.json && \
      corepack enable pnpm && \
      pnpm install --prod --no-lockfile; \
    else \
      echo '{"name": "task-runner-runtime-extras", "description": "No custom dependencies", "private": true, "dependencies": {}}' > package.json && \
      mkdir -p node_modules; \
    fi

# ============================================================================
# Stage 2: Build Python Dependencies
# ============================================================================
# CRITICAL: Use Python 3.13 (not 3.14) to match n8n runners base image
FROM python:3.13-alpine AS python-extras

ARG PY_PACKAGES

WORKDIR /extras

# Convert comma-separated packages to requirements.txt
# Input:  "requests==2.31.0,python-dateutil==2.8.2"
# Output: requirements.txt with one package per line
RUN echo "Installing Python packages: ${PY_PACKAGES}" && \
    if [ -n "${PY_PACKAGES}" ] && [ "${PY_PACKAGES}" != "" ]; then \
      echo "${PY_PACKAGES}" | tr ',' '\n' > requirements.txt && \
      cat requirements.txt && \
      apk add --no-cache \
        gcc \
        g++ \
        gfortran \
        musl-dev \
        linux-headers \
        openblas-dev \
        lapack-dev && \
      pip install --no-cache-dir -r requirements.txt; \
    else \
      touch requirements.txt; \
    fi

# ============================================================================
# Stage 3: Generate Configuration and Allow-Lists
# ============================================================================
FROM alpine:latest AS config-generator

ARG JS_PACKAGES
ARG PY_PACKAGES

WORKDIR /config

# Extract package names (without versions) for allow-lists
# JavaScript: "moment@2.30.1,axios@^1.7.0" -> "moment,axios"
RUN if [ -n "${JS_PACKAGES}" ] && [ "${JS_PACKAGES}" != "" ]; then \
      echo "${JS_PACKAGES}" | tr ',' '\n' | cut -d'@' -f1 | tr '\n' ',' | sed 's/,$//' > js-allow-list.txt; \
    else \
      echo "" > js-allow-list.txt; \
    fi && \
    echo "JavaScript allow-list: $(cat js-allow-list.txt)"

# Python: "requests==2.31.0,python-dateutil==2.8.2" -> "requests,python-dateutil"
RUN if [ -n "${PY_PACKAGES}" ] && [ "${PY_PACKAGES}" != "" ]; then \
      echo "${PY_PACKAGES}" | tr ',' '\n' | sed 's/==.*//' | sed 's/>=.*//' | sed 's/<=.*//' | tr '\n' ',' | sed 's/,$//' > py-allow-list.txt; \
    else \
      echo "" > py-allow-list.txt; \
    fi && \
    echo "Python allow-list: $(cat py-allow-list.txt)"

# Generate the task runner configuration file
# IMPORTANT: Do NOT set allow-lists in env-overrides
# Allow-lists should be set via Railway environment variables for flexibility

# Write config file using shell script to avoid heredoc parsing issues
RUN cat > /etc/n8n-task-runners.json <<'EOFCONFIG'
{
	"task-runners": [
		{
			"runner-type": "javascript",
			"workdir": "/home/runner",
			"command": "/usr/local/bin/node",
			"args": [
				"--disallow-code-generation-from-strings",
				"--disable-proto=delete",
				"/opt/runners/task-runner-javascript/dist/start.js"
			],
			"health-check-server-port": "5681",
			"allowed-env": [
				"PATH",
				"GENERIC_TIMEZONE",
				"NODE_OPTIONS",
				"N8N_RUNNERS_AUTO_SHUTDOWN_TIMEOUT",
				"N8N_RUNNERS_TASK_TIMEOUT",
				"N8N_RUNNERS_MAX_CONCURRENCY",
				"N8N_SENTRY_DSN",
				"N8N_VERSION",
				"ENVIRONMENT",
				"DEPLOYMENT_NAME",
				"NODE_FUNCTION_ALLOW_EXTERNAL",
				"NODE_FUNCTION_ALLOW_BUILTIN"
			],
			"env-overrides": {
				"N8N_RUNNERS_HEALTH_CHECK_SERVER_HOST": "0.0.0.0"
			}
		},
		{
			"runner-type": "python",
			"workdir": "/home/runner",
			"command": "/opt/runners/task-runner-python/.venv/bin/python",
			"args": ["-m", "src.main"],
			"health-check-server-port": "5682",
			"allowed-env": [
				"PATH",
				"N8N_RUNNERS_LAUNCHER_LOG_LEVEL",
				"N8N_RUNNERS_AUTO_SHUTDOWN_TIMEOUT",
				"N8N_RUNNERS_TASK_TIMEOUT",
				"N8N_RUNNERS_MAX_CONCURRENCY",
				"N8N_SENTRY_DSN",
				"N8N_VERSION",
				"ENVIRONMENT",
				"DEPLOYMENT_NAME",
				"N8N_RUNNERS_EXTERNAL_ALLOW",
				"N8N_RUNNERS_STDLIB_ALLOW"
			],
			"env-overrides": {
				"PYTHONPATH": "/opt/runners/task-runner-python"
			}
		}
	]
}
EOFCONFIG

# Verify config was created
RUN cat /etc/n8n-task-runners.json

# ============================================================================
# Final Stage: Assemble Custom Runners Image
# ============================================================================
FROM ghcr.io/n8n-io/runners:${N8N_VERSION}

ARG JS_PACKAGES
ARG PY_PACKAGES

USER root

# Copy JavaScript extras
COPY --from=javascript-extras /extras/node_modules /opt/runners/task-runner-javascript/node_modules/

# Copy Python extras to virtual environment
# CRITICAL: Use python3.13 path to match runner's Python version
COPY --from=python-extras /usr/local/lib/python3.13/site-packages /opt/runners/task-runner-python/.venv/lib/python3.13/site-packages/

# Copy generated configuration
COPY --from=config-generator /etc/n8n-task-runners.json /etc/n8n-task-runners.json

# Verify config
RUN cat /etc/n8n-task-runners.json

USER runner

# Add metadata labels
LABEL org.opencontainers.image.title="n8n task runners (Railway custom)" \
      org.opencontainers.image.description="Custom n8n task runners with dynamic dependency management for Railway" \
      org.opencontainers.image.source="https://github.com/n8n-io/n8n" \
      n8n.custom.js-packages="${JS_PACKAGES}" \
      n8n.custom.py-packages="${PY_PACKAGES}"

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
  CMD wget --spider -q http://localhost:5680/healthz || exit 1
