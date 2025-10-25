# Additional context
See files in @railway-deployment folder.

## Project overview
This project is a deployment template for n8n with code runner. For more information about this concept of code runners, see [Task Runners](https://docs.n8n.io/hosting/configuration/task-runners/)

# Short description (75 symbols)
n8n with Task Runners - easily add custom Python/JavaScript dependencies 

# Sections: Template Overview (10000 symbols)
Template Overview section. It contains structure and content which should be present in the template overview section. Template start <Template Overview> and template end </Template Overview>.
<Template Overview>
# Deploy and Host n8n with Task Runners on Railway

n8n is a powerful workflow automation platform that lets you connect apps and automate tasks. This template deploys n8n with **Task Runners** - a game-changing feature that allows you to easily add custom Python and JavaScript dependencies to your Code nodes. Unlike traditional n8n deployments that require rebuilding entire Docker containers to add packages, Task Runners let you simply update environment variables and redeploy in seconds.

## About Hosting n8n with Task Runners

This template provides a complete n8n deployment with three services: PostgreSQL database, n8n main application, and Task Runners service. The Task Runners service executes Python and JavaScript code with your custom dependencies. Adding new packages is simple - just update Railway environment variables and trigger a redeploy. No Docker knowledge required. The multi-stage build system optimizes deployment speed, with lightweight packages deploying in approximately 2 minutes and scientific packages in approximately 5-10 minutes. Configuration is managed entirely through Railway's dashboard, making dependency management transparent and version-controlled.

## Common Use Cases

- **Data Processing Workflows** - Use pandas, BeautifulSoup, or other Python libraries to parse, transform, and analyze data from APIs and databases
- **Advanced Date/Time Operations** - Leverage moment.js or python-dateutil for complex timezone conversions, relative dates, and scheduling logic
- **HTTP API Integrations** - Use axios or requests with custom authentication libraries for advanced API integrations not available in standard n8n nodes
- **Scientific Computing** - Run statistical analysis, machine learning predictions, or mathematical computations with scipy, numpy, or similar packages
- **Custom Business Logic** - Implement complex algorithms using specialized JavaScript/Python libraries that aren't available in standard n8n

## Dependencies for n8n with Task Runners Hosting

This template requires three Railway services:

- **PostgreSQL** - Database for storing n8n workflows and execution history
- **n8n Main Service** - The n8n web UI and workflow execution engine (uses official n8n Docker image)
- **Task Runners Service** - Service that executes Python and JavaScript code with your dependencies

### Deployment Dependencies

- [n8n Official Documentation](https://docs.n8n.io/)
- [n8n Task Runners Guide](https://docs.n8n.io/hosting/configuration/task-runners/)
- [Railway Platform Documentation](https://docs.railway.com/)
- [GitHub Repository](https://github.com/n8n-io/n8n)

### Managing Custom Dependencies

This template's key feature is **easy custom dependency management** - the main differentiator from standard n8n deployments.

#### Configuration Variables

This template provides four environment variables for managing dependencies:

- **JS_PACKAGES** - JavaScript packages to install (with versions)
- **JS_ALLOW_LIST** - JavaScript packages available in Code nodes
- **PY_PACKAGES** - Python packages to install (with versions)
- **PY_ALLOW_LIST** - Python packages available in Code nodes

Learn more in the [official n8n documentation](https://docs.n8n.io/hosting/configuration/configuration-examples/modules-in-code-node/).

#### JavaScript Configuration Example

Go to Railway Dashboard → Runners Service → Variables:

```
JS_PACKAGES=moment,axios,lodash,uuid

JS_ALLOW_LIST=moment,axios,lodash,uuid
```

Click **Redeploy** and packages deploy in 2-3 minutes.

**Note:** JS_ALLOW_LIST requires package names listed explicitly (comma-separated). This ensures proper library initialization for packages like moment.js.

#### Python Configuration Example

Go to Railway Dashboard → Runners Service → Variables:

```
PY_PACKAGES=requests,python-dateutil,beautifulsoup4

PY_ALLOW_LIST=requests,dateutil,bs4
```

Click **Redeploy** and packages deploy in 2-10 minutes (scientific packages take longer).

**Note:** Package install names may differ from import names (python-dateutil imports as dateutil, beautifulsoup4 imports as bs4).

### Deploying Specific n8n Versions

By default, this template deploys the latest n8n version. To deploy a specific version:

**n8n Main Service:** Go to Railway Dashboard → n8n Service → Settings → Image

```
ghcr.io/n8n-io/n8n:1.75.0
```

**Task Runners Service:** Go to Railway Dashboard → Runners Service → Variables

```
N8N_VERSION=1.75.0
```

Click **Redeploy** on both services.

**Note:** Both services must use the same version number for compatibility.

### Package Compatibility

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

**Getting Help:**

For packages requiring additional system libraries, contact the template maintainer with:
- Package name
- Railway deployment log output
- Language (JavaScript or Python)

The template can be updated to include additional system dependencies as needed.

## Why Deploy n8n with Task Runners on Railway?

Railway is a singular platform to deploy your infrastructure stack. Railway will host your infrastructure so you don't have to deal with configuration, while allowing you to vertically and horizontally scale it.

This template is specifically optimized for Railway's platform:

- **Dashboard-Based Configuration** - All configuration managed through Railway environment variables with no manual file editing required
- **Automatic Build Optimization** - Railway's caching speeds up deployments after the initial setup
- **Internal Networking** - Task Runners and n8n communicate over Railway's private network
- **One-Click Dependency Updates** - Change environment variables and redeploy without code changes
- **Built-in Monitoring** - Railway's dashboard shows service health and resource usage
- **Seamless Scaling** - Add more resources to Task Runners as your workflow complexity grows

By deploying n8n with Task Runners on Railway, you get enterprise-grade workflow automation with the flexibility to add any Python or JavaScript library you need - all managed through a simple web dashboard. Perfect for data teams, automation engineers, and businesses that need custom integrations without technical overhead.
</Template Overview>