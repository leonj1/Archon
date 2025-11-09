# Railway Deployment Guide for Archon

This guide explains how to deploy the Archon application to Railway.app, including all 5 services.

## Overview

Archon consists of 5 services that will be deployed to Railway:

1. **archon-migrations** - Database migration service (runs once)
2. **archon-server** - Main FastAPI backend (port 8181)
3. **archon-mcp** - MCP server for IDE integration (port 8051)
4. **archon-agents** - AI agents service (optional, port 8052)
5. **archon-frontend** - React UI (port 3737)

## Prerequisites

1. **Railway Account**: Sign up at https://railway.app
2. **Railway CLI** (optional): Install via `npm install -g @railway/cli` or `brew install railway`
3. **Supabase Account**: You'll need a Supabase project for the database
4. **GitHub Repository**: Connect your repo to Railway for automatic deployments

## Deployment Methods

### Method 1: Railway Dashboard (Recommended for First-Time Setup)

#### Step 1: Create a New Project

1. Go to https://railway.app/dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Authorize Railway to access your GitHub account
5. Select the Archon repository

#### Step 2: Create Services

Railway will detect the configuration files. You need to create 5 separate services:

**Service 1: Database Migrations**
1. Click "New Service" → "Empty Service"
2. Name: `archon-migrations`
3. Go to Settings → Build:
   - Root Directory: `/`
   - Dockerfile Path: `Dockerfile.migrations`
4. Go to Variables and add:
   ```
   ARCHON_DB_BACKEND=sqlite
   ARCHON_SQLITE_PATH=/data/archon.db
   SUPABASE_URL=<your-supabase-url>
   SUPABASE_SERVICE_KEY=<your-service-key>
   ```
5. Deploy

**Service 2: Backend Server**
1. Click "New Service" → "Empty Service"
2. Name: `archon-server`
3. Go to Settings → Build:
   - Root Directory: `python`
   - Dockerfile Path: `Dockerfile.server`
4. Go to Variables and add:
   ```
   ARCHON_DB_BACKEND=sqlite
   ARCHON_SQLITE_PATH=/data/archon.db
   ARCHON_SKIP_DB_INIT=true
   SERVICE_DISCOVERY_MODE=railway
   LOG_LEVEL=INFO
   ARCHON_SERVER_PORT=$PORT
   ARCHON_MCP_PORT=8051
   ARCHON_AGENTS_PORT=8052
   AGENTS_ENABLED=false
   ARCHON_HOST=0.0.0.0
   SUPABASE_URL=<your-supabase-url>
   SUPABASE_SERVICE_KEY=<your-service-key>
   OPENAI_API_KEY=<optional>
   LOGFIRE_TOKEN=<optional>
   ```
5. Go to Settings → Networking:
   - Enable "Public Networking"
   - Note the public URL (e.g., `archon-server.up.railway.app`)
6. Deploy

**Service 3: MCP Server**
1. Click "New Service" → "Empty Service"
2. Name: `archon-mcp`
3. Go to Settings → Build:
   - Root Directory: `python`
   - Dockerfile Path: `Dockerfile.mcp`
4. Go to Variables and add:
   ```
   ARCHON_SQLITE_PATH=/data/archon.db
   SERVICE_DISCOVERY_MODE=railway
   TRANSPORT=sse
   LOG_LEVEL=INFO
   ARCHON_MCP_PORT=$PORT
   ARCHON_SERVER_PORT=8181
   ARCHON_AGENTS_PORT=8052
   AGENTS_ENABLED=false
   API_SERVICE_URL=${{archon-server.RAILWAY_PUBLIC_DOMAIN}}
   SUPABASE_URL=<your-supabase-url>
   SUPABASE_SERVICE_KEY=<your-service-key>
   LOGFIRE_TOKEN=<optional>
   ```
5. Go to Settings → Networking:
   - Enable "Public Networking"
6. Deploy

**Service 4: AI Agents (Optional)**
1. Click "New Service" → "Empty Service"
2. Name: `archon-agents`
3. Go to Settings → Build:
   - Root Directory: `python`
   - Dockerfile Path: `Dockerfile.agents`
4. Go to Variables and add:
   ```
   SERVICE_DISCOVERY_MODE=railway
   LOG_LEVEL=INFO
   ARCHON_AGENTS_PORT=$PORT
   ARCHON_SERVER_PORT=8181
   SUPABASE_URL=<your-supabase-url>
   SUPABASE_SERVICE_KEY=<your-service-key>
   OPENAI_API_KEY=<your-openai-key>
   LOGFIRE_TOKEN=<optional>
   ```
5. Go to Settings → Networking:
   - Enable "Public Networking"
6. Deploy

**Service 5: Frontend**
1. Click "New Service" → "Empty Service"
2. Name: `archon-frontend`
3. Go to Settings → Build:
   - Root Directory: `archon-ui-main`
   - Dockerfile Path: `Dockerfile`
4. Go to Variables and add:
   ```
   VITE_API_URL=${{archon-server.RAILWAY_PUBLIC_DOMAIN}}
   VITE_ARCHON_SERVER_PORT=8181
   ARCHON_SERVER_PORT=8181
   HOST=0.0.0.0
   PROD=true
   DOCKER_ENV=true
   VITE_SHOW_DEVTOOLS=false
   ```
5. Go to Settings → Networking:
   - Enable "Public Networking"
   - Note the public URL (this is your application URL!)
6. Deploy

#### Step 3: Configure Service Dependencies

To ensure services start in the correct order:

1. Go to each service's Settings → Deploy
2. Set up dependencies:
   - `archon-server` depends on `archon-migrations`
   - `archon-mcp` depends on `archon-server`
   - `archon-frontend` depends on `archon-server`
   - `archon-agents` has no dependencies (optional)

#### Step 4: Set Up Volumes (Optional)

If you want persistent data storage for SQLite:

1. Go to each service (server, mcp, migrations)
2. Click "Variables" → "New Volume"
3. Mount Path: `/data`
4. Redeploy the service

### Method 2: Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project (in repo root)
railway init

# Link to existing project or create new one
railway link

# Create and deploy services
railway up --service archon-migrations
railway up --service archon-server
railway up --service archon-mcp
railway up --service archon-agents
railway up --service archon-frontend

# Set environment variables
railway variables set SUPABASE_URL=<your-url> --service archon-server
railway variables set SUPABASE_SERVICE_KEY=<your-key> --service archon-server
# ... repeat for other services
```

### Method 3: GitHub Integration (Automatic Deployments)

1. Connect your GitHub repository to Railway
2. Railway will automatically detect changes and deploy
3. Each push to `main` or `master` branch triggers deployment
4. Configure branch deployments in Settings → Deployments

## Environment Variables Reference

### Required Variables (All Services)

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGc... # Use service_role key, NOT anon key!
```

### Backend Server Variables

```bash
ARCHON_DB_BACKEND=sqlite
ARCHON_SQLITE_PATH=/data/archon.db
ARCHON_SKIP_DB_INIT=true
SERVICE_DISCOVERY_MODE=railway
LOG_LEVEL=INFO
ARCHON_SERVER_PORT=$PORT  # Railway provides this
ARCHON_HOST=0.0.0.0
AGENTS_ENABLED=false  # Set to true if deploying agents

# Optional
OPENAI_API_KEY=sk-...  # For AI features
LOGFIRE_TOKEN=...  # For logging
```

### MCP Server Variables

```bash
ARCHON_MCP_PORT=$PORT
TRANSPORT=sse
API_SERVICE_URL=${{archon-server.RAILWAY_PUBLIC_DOMAIN}}
AGENTS_SERVICE_URL=${{archon-agents.RAILWAY_PUBLIC_DOMAIN}}  # If using agents
```

### Frontend Variables

```bash
VITE_API_URL=${{archon-server.RAILWAY_PUBLIC_DOMAIN}}
PROD=true
DOCKER_ENV=true
HOST=0.0.0.0
```

## Service Communication

Railway provides internal networking between services. Use these patterns:

**Reference another service's URL:**
```bash
API_SERVICE_URL=${{archon-server.RAILWAY_PUBLIC_DOMAIN}}
```

**Reference another service's private URL (faster):**
```bash
API_SERVICE_URL=${{archon-server.RAILWAY_PRIVATE_DOMAIN}}
```

## Port Configuration

Railway automatically assigns ports via the `$PORT` environment variable. Your services should:

1. Read `$PORT` from environment (Railway injects this)
2. Bind to `0.0.0.0:$PORT` (not `localhost`)
3. Configure health checks on the same port

## Health Checks

Railway will monitor these endpoints:

- **archon-server**: `GET /health`
- **archon-mcp**: `GET /health`
- **archon-agents**: `GET /health`
- **archon-frontend**: `GET /`

If health checks fail, Railway will restart the service.

## Volumes and Persistent Storage

### SQLite Database Storage

If using SQLite (default), you need persistent volumes:

1. Go to service Settings → Volumes
2. Create volume mounted at `/data`
3. This persists the `archon.db` file across deployments

### Alternative: Use Supabase PostgreSQL

Instead of SQLite, use Supabase's PostgreSQL:

```bash
ARCHON_DB_BACKEND=postgresql
SUPABASE_DB_URL=postgresql://postgres:[password]@[host]:5432/postgres
```

## Monitoring and Logs

### View Logs

**Dashboard:**
- Go to service → Logs tab
- Filter by time range
- Search for errors

**CLI:**
```bash
railway logs --service archon-server
railway logs --service archon-mcp --follow
```

### Metrics

Railway provides:
- CPU usage
- Memory usage
- Network traffic
- Deployment history

Access via service Dashboard → Metrics tab

## Scaling

### Horizontal Scaling

To run multiple instances:
1. Go to service Settings → Replicas
2. Set number of replicas (requires paid plan)
3. Railway handles load balancing

### Vertical Scaling

To increase resources:
1. Go to service Settings → Resources
2. Adjust CPU/Memory limits
3. Redeploy service

## Cost Optimization

1. **Use Private Networking**: Services communicate faster and cheaper via private URLs
2. **Disable Unused Services**: Don't deploy `archon-agents` if not needed
3. **Use Volumes Wisely**: Only persist data that needs to survive restarts
4. **Monitor Usage**: Check Railway dashboard for usage metrics

## Troubleshooting

### Service Won't Start

1. Check logs: `railway logs --service <name>`
2. Verify environment variables are set correctly
3. Ensure Dockerfile paths are correct in Settings → Build
4. Check health check endpoints are responding

### Services Can't Communicate

1. Verify service URLs use Railway variable syntax: `${{service-name.RAILWAY_PUBLIC_DOMAIN}}`
2. Check network settings: Services should be in same project
3. Use private URLs for internal communication

### Database Connection Issues

1. Verify `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` are correct
2. Ensure service_role key is used (not anon key)
3. Check Supabase project is accessible from Railway IPs

### Frontend Can't Reach Backend

1. Verify `VITE_API_URL` points to backend public URL
2. Check CORS settings in backend (`python/src/server/main.py`)
3. Ensure backend health check is passing

### Build Failures

1. Check Dockerfile paths in Settings → Build
2. Verify root directory is set correctly
3. Check `.railwayignore` isn't excluding needed files
4. Review build logs for specific errors

## Deployment Checklist

- [ ] Supabase project created and credentials ready
- [ ] All 5 services created in Railway project
- [ ] Environment variables set for each service
- [ ] Dockerfile paths configured correctly
- [ ] Public networking enabled for services that need it
- [ ] Service dependencies configured
- [ ] Volumes created for persistent data (if using SQLite)
- [ ] Health checks passing for all services
- [ ] Frontend can reach backend API
- [ ] MCP server accessible (if using IDE integration)
- [ ] Test a crawl operation to verify full functionality

## Support and Resources

- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **Archon Issues**: https://github.com/your-org/archon/issues
- **Supabase Docs**: https://supabase.com/docs

## Next Steps

After deployment:

1. Access your frontend at the Railway public URL
2. Go to Settings page and configure:
   - OpenAI API key (encrypted in database)
   - Model preferences
   - RAG strategy settings
   - Crawler configuration
3. Test knowledge base by crawling a website
4. Configure MCP in your IDE (Cursor/Windsurf)
5. Set up custom domain (optional, requires Railway paid plan)

## Security Notes

- Never commit `.env` files with real credentials
- Use Railway's encrypted environment variables for secrets
- Keep `SUPABASE_SERVICE_KEY` secure (it has admin access)
- Consider using Railway's private networking for internal services
- Enable Railway's automatic HTTPS for all public services
- Regularly update dependencies and redeploy

## Maintenance

### Updating Services

**Automatic (GitHub integration):**
- Push to main branch
- Railway auto-deploys

**Manual (CLI):**
```bash
railway up --service <service-name>
```

**Manual (Dashboard):**
- Go to service → Deployments
- Click "Deploy" → "Latest commit"

### Database Migrations

When schema changes:
1. Update migration files in `/migration`
2. Redeploy `archon-migrations` service
3. Redeploy dependent services

### Rollbacks

If deployment fails:
1. Go to service → Deployments
2. Find last working deployment
3. Click "Rollback"

---

**Note**: This guide assumes you're using Railway's free tier limits. For production deployments, consider Railway's paid plans for better performance, scaling, and custom domains.
