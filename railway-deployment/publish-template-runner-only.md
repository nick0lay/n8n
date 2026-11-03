# Additional context
This is a task runner-only template for connecting to existing n8n deployments. For complete n8n deployment with task runners, see the full template.

## Project overview
This template deploys ONLY n8n Task Runners service to connect to your existing n8n instance. For more information about task runners, see [Task Runners](https://docs.n8n.io/hosting/configuration/task-runners/)

# Short description (75 symbols)
n8n Task Runners - add Python/JavaScript code execution to existing n8n

# Sections: Template Overview (10000 symbols)
Template Overview section. It contains structure and content which should be present in the template overview section. Template start <Template Overview> and template end </Template Overview>.
<Template Overview>
# Deploy and Host n8n Task Runners on Railway

n8n Task Runners execute Python and JavaScript code with custom dependencies. This template deploys **only the Task Runners service** to connect to your existing n8n instance, enabling Code nodes with custom packages like pandas, moment.js, requests, and hundreds of other libraries. Perfect for adding code execution to existing n8n Cloud or self-hosted deployments without redeployment.

## About Hosting n8n Task Runners

Hosting n8n Task Runners involves deploying a service that connects to your existing n8n instance to execute Python and JavaScript code. The deployment requires configuring two environment variables on both your n8n instance and the task runners service: an authentication token and broker URI. Once connected, you can manage custom dependencies through Railway's dashboard by updating environment variables and redeploying. The service executes code in isolated containers, with deployment times ranging from 2-3 minutes for lightweight packages to 5-10 minutes for scientific packages. No server management or Docker knowledge required.

## Common Use Cases

- **Extend n8n Cloud** - Add custom Python/JavaScript packages to n8n Cloud deployments without self-hosting the entire platform
- **Scale Code Execution** - Separate code execution from your main n8n instance for better resource management and scaling
- **Add Custom Dependencies** - Enable workflows to use specialized libraries like pandas, numpy, beautifulsoup4, or any npm package
- **Zero-Downtime Enhancement** - Add code execution capabilities to production n8n instances without redeployment or downtime
- **Test Before Migration** - Try task runners with your existing workflows before committing to a full deployment with task runners

## Dependencies for n8n Task Runners Hosting

- **Existing n8n instance** - Self-hosted or n8n Cloud with version 1.0.0 or higher
- **Network connectivity** - Your n8n instance must be able to connect to Railway services
- **Admin access** - Ability to modify environment variables on your n8n instance
- **Shared authentication token** - Generated secure token for communication between n8n and task runners

### Deployment Dependencies

- [n8n Task Runners Documentation](https://docs.n8n.io/hosting/configuration/task-runners/)
- [Enable Modules in Code Node](https://docs.n8n.io/hosting/configuration/configuration-examples/modules-in-code-node/)
- [Railway Platform Documentation](https://docs.railway.com/)
- [Complete n8n with Task Runners Template](https://railway.com/deploy/n8n-with-code-runner?referralCode=CG2P3Y&utm_medium=integration&utm_source=template&utm_campaign=generic) - Reference example showing full configuration

### Implementation Details

#### Configuration: Your Existing n8n Instance

To enable your existing n8n instance to use task runners, add these environment variables:

**Required Variables:**

```
N8N_RUNNERS_ENABLED=true
N8N_RUNNERS_MODE=external
N8N_RUNNERS_BROKER_LISTEN_ADDRESS=0.0.0.0
N8N_RUNNERS_BROKER_PORT=5679
N8N_RUNNERS_AUTH_TOKEN=your-secure-random-token-here
```

**Generate Auth Token:**

The AUTH_TOKEN is a shared secret between your n8n instance and task runners. Generate a secure random token:

```
openssl rand -base64 24
```

Use the same token on both your n8n instance and the task runners service.

**Network Configuration:**

Your n8n instance must expose the task broker port (5679) for task runners to connect. If your n8n runs on Railway, the task broker is accessible via Railway's internal network. If hosted elsewhere, ensure port 5679 is accessible.

#### Configuration: Task Runners Service

After deploying this template, configure the task runners service with these environment variables in Railway Dashboard:

**Required Connection Variables:**

```
N8N_RUNNERS_AUTH_TOKEN=your-secure-random-token-here
N8N_RUNNERS_TASK_BROKER_URI=http://your-n8n-instance:5679
```

**N8N_RUNNERS_AUTH_TOKEN**: Must match the token configured on your n8n instance

**N8N_RUNNERS_TASK_BROKER_URI**: Points to your n8n task broker endpoint
- Railway n8n: `http://n8n.railway.internal:5679`
- External n8n: `http://your-domain.com:5679` or `https://your-domain.com:5679`

**Dependency Management Variables:**

Configure which packages are available in Code nodes:

```
JS_PACKAGES=moment,axios,lodash,uuid
JS_ALLOW_LIST=moment,axios,lodash,uuid

PY_PACKAGES=requests,python-dateutil,beautifulsoup4
PY_ALLOW_LIST=requests,dateutil,bs4
```

These variables control which JavaScript and Python packages are installed and available for use in n8n Code nodes.

#### Managing Custom Dependencies

**Configuration Variables:**

This template provides four environment variables for managing dependencies:

- **JS_PACKAGES** - JavaScript packages to install
- **JS_ALLOW_LIST** - JavaScript packages available in Code nodes
- **PY_PACKAGES** - Python packages to install
- **PY_ALLOW_LIST** - Python packages available in Code nodes

Learn more in the [official n8n documentation](https://docs.n8n.io/hosting/configuration/configuration-examples/modules-in-code-node/).

**JavaScript Configuration Example:**

Go to Railway Dashboard → Task Runners Service → Variables:

```
JS_PACKAGES=moment,axios,lodash,uuid

JS_ALLOW_LIST=moment,axios,lodash,uuid
```

Click **Redeploy** and packages deploy in 2-3 minutes.

**Note:** JS_ALLOW_LIST requires package names listed explicitly (comma-separated). This ensures proper library initialization for packages like moment.js.

**Python Configuration Example:**

Go to Railway Dashboard → Task Runners Service → Variables:

```
PY_PACKAGES=requests,python-dateutil,beautifulsoup4

PY_ALLOW_LIST=requests,dateutil,bs4
```

Click **Redeploy** and packages deploy in 2-10 minutes (scientific packages take longer).

**Note:** Package install names may differ from import names (python-dateutil imports as dateutil, beautifulsoup4 imports as bs4).

#### Verifying Connection

After deploying and configuring both sides:

1. Check Railway logs for task runners service - should show "Connected to task broker"
2. Check your n8n logs - should show "Task runner connected"
3. Create a workflow with a Code node
4. Test JavaScript code with configured packages
5. Test Python code with configured packages

#### Deployment Steps Summary

1. **Deploy this template** - Click deploy button for task runners service
2. **Generate auth token** - Use `openssl rand -base64 24`
3. **Configure your n8n** - Add task runner environment variables and auth token
4. **Configure task runners** - Set connection variables in Railway Dashboard
5. **Add dependencies** - Configure JS_PACKAGES and PY_PACKAGES as needed
6. **Redeploy services** - Restart both n8n and task runners
7. **Test connection** - Create workflow with Code node

#### Package Compatibility

**Included Package Support:**

This template includes build dependencies for a wide range of packages:

- **JavaScript packages:** moment, axios, lodash, uuid, date-fns, and most npm packages work out-of-the-box
- **Python packages:** requests, python-dateutil, beautifulsoup4, and pure-Python packages work out-of-the-box
- **Scientific packages:** numpy, pandas, scipy supported (deployment takes approximately 5-10 minutes)
- **Build tools:** Included for packages with compiled extensions

**Deployment Times:**

- Lightweight packages: 2-3 minutes
- Scientific/numerical packages: 5-10 minutes
- First deployment includes initial setup time

#### Complete Configuration Example

For a complete working example of n8n with task runners, including all environment variables and configuration, see the [full n8n with Task Runners template](https://railway.com/deploy/n8n-with-code-runner?referralCode=CG2P3Y&utm_medium=integration&utm_source=template&utm_campaign=generic).

This complete template shows:
- How n8n and task runners are configured together
- All environment variables for both services
- Network configuration between services
- Complete dependency management setup

Use this as a reference when configuring your existing n8n instance.

## Why Deploy n8n Task Runners on Railway?

Railway provides the ideal infrastructure for task runners:

- **Dashboard-Based Configuration** - All configuration managed through Railway environment variables
- **Automatic Build Optimization** - Railway's caching speeds up deployments after the initial setup
- **Internal Networking** - Connect to n8n instances on Railway via private network
- **One-Click Dependency Updates** - Change environment variables and redeploy without code changes
- **Built-in Monitoring** - Railway's dashboard shows service health and resource usage
- **Seamless Scaling** - Add more resources as your workflow complexity grows

By deploying task runners on Railway, you can add custom Python and JavaScript packages to your existing n8n workflows without managing server infrastructure. Perfect for extending n8n Cloud or existing self-hosted deployments with code execution capabilities.
</Template Overview>
