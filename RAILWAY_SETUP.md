# Railway Multi-Service Deployment Guide

This guide will help you set up all 5 Archon services in Railway.

## Prerequisites

- Railway account with access to project: https://railway.com/project/2eb8e3aa-8e65-4906-ab10-d10761d138a1
- GitHub repository connected to Railway
- Supabase account with `SUPABASE_URL` and `SUPABASE_SERVICE_KEY`

## Quick Setup (15 minutes)

### Step 1: Set Shared Environment Variables

1. Go to your Archon project: https://railway.com/project/2eb8e3aa-8e65-4906-ab10-d10761d138a1
2. Click on **"Shared Variables"** (or project Settings → Variables)
3. Add these variables that all services will use:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_KEY=eyJhbGc... (your service_role key)
   ```

### Step 2: Create Services

Click **"+ New Service"** five times to create these services. For each one:

---

#### Service 1: archon-migrations

**Basic Settings:**
- Name: `archon-migrations`
- Source: GitHub → Select your repository
- Branch: `master` (or your main branch)

**Build Settings** (Settings → Build):
- Root Directory: `/`
- Builder: `Dockerfile`
- Dockerfile Path: `Dockerfile.migrations`

**Environment Variables** (Settings → Variables):
```
ARCHON_DB_BACKEND=sqlite
ARCHON_SQLITE_PATH=/data/archon.db
```
(SUPABASE variables inherited from shared)

**Deploy Settings** (Settings → Deploy):
- Start Command: (leave empty, Dockerfile handles it)
- Restart Policy: On Failure
- Max Retries: 10

---

#### Service 2: archon-server

**Basic Settings:**
- Name: `archon-server`
- Source: GitHub → Select your repository
- Branch: `master`

**Build Settings:**
- Root Directory: `python`
- Builder: `Dockerfile`
- Dockerfile Path: `Dockerfile.server`

**Environment Variables:**
```
ARCHON_DB_BACKEND=sqlite
ARCHON_SQLITE_PATH=/data/archon.db
ARCHON_SKIP_DB_INIT=true
SERVICE_DISCOVERY_MODE=railway
LOG_LEVEL=INFO
ARCHON_SERVER_PORT=$PORT
ARCHON_MCP_URL=${{archon-mcp.RAILWAY_PRIVATE_DOMAIN}}
ARCHON_AGENTS_URL=${{archon-agents.RAILWAY_PRIVATE_DOMAIN}}
AGENTS_ENABLED=false
ARCHON_HOST=0.0.0.0
```

**Optional** (if using AI features):
```
OPENAI_API_KEY=sk-... (your OpenAI key)
```

**Deploy Settings:**
- Start Command: `python -m uvicorn src.server.main:app --host 0.0.0.0 --port $PORT`
- Health Check Path: `/health`
- Health Check Timeout: 10 seconds
- Health Check Interval: 30 seconds

**Networking:**
- Generate a public domain (this will be the main API endpoint)

---

#### Service 3: archon-mcp

**Basic Settings:**
- Name: `archon-mcp`
- Source: GitHub → Select your repository
- Branch: `master`

**Build Settings:**
- Root Directory: `python`
- Builder: `Dockerfile`
- Dockerfile Path: `Dockerfile.mcp`

**Environment Variables:**
```
ARCHON_SQLITE_PATH=/data/archon.db
SERVICE_DISCOVERY_MODE=railway
TRANSPORT=sse
LOG_LEVEL=INFO
ARCHON_MCP_PORT=$PORT
API_SERVICE_URL=${{archon-server.RAILWAY_PRIVATE_DOMAIN}}
AGENTS_SERVICE_URL=${{archon-agents.RAILWAY_PRIVATE_DOMAIN}}
AGENTS_ENABLED=false
```

**Deploy Settings:**
- Start Command: `python -m src.mcp_server.main`
- Health Check Path: `/health`
- Health Check Timeout: 10 seconds
- Health Check Interval: 30 seconds

**Networking:**
- Generate a public domain (for IDE integration)

---

#### Service 4: archon-agents

**Basic Settings:**
- Name: `archon-agents`
- Source: GitHub → Select your repository
- Branch: `master`

**Build Settings:**
- Root Directory: `python`
- Builder: `Dockerfile`
- Dockerfile Path: `Dockerfile.agents`

**Environment Variables:**
```
SERVICE_DISCOVERY_MODE=railway
LOG_LEVEL=INFO
ARCHON_AGENTS_PORT=$PORT
API_SERVICE_URL=${{archon-server.RAILWAY_PRIVATE_DOMAIN}}
```

**Required** (for agents to work):
```
OPENAI_API_KEY=sk-... (your OpenAI key)
```

**Deploy Settings:**
- Start Command: `python -m uvicorn src.agents.server:app --host 0.0.0.0 --port $PORT`
- Health Check Path: `/health`
- Health Check Timeout: 10 seconds
- Health Check Interval: 30 seconds

---

#### Service 5: archon-frontend

**Basic Settings:**
- Name: `archon-frontend`
- Source: GitHub → Select your repository
- Branch: `master`

**Build Settings:**
- Root Directory: `archon-ui-main`
- Builder: `Dockerfile`
- Dockerfile Path: `Dockerfile`

**Environment Variables:**
```
HOST=0.0.0.0
PROD=true
DOCKER_ENV=true
VITE_API_URL=${{archon-server.RAILWAY_PUBLIC_DOMAIN}}
```

**Optional:**
```
VITE_ALLOWED_HOSTS=example.com,*.yourdomain.com
VITE_SHOW_DEVTOOLS=false
```

**Deploy Settings:**
- Start Command: `npm run preview -- --host 0.0.0.0 --port $PORT`
- Health Check Path: `/`
- Health Check Timeout: 10 seconds
- Health Check Interval: 30 seconds

**Networking:**
- Generate a public domain (this will be your main UI URL)

---

### Step 3: Verify Service References

After creating all services, verify that the `${{service-name.RAILWAY_PRIVATE_DOMAIN}}` references work:

1. Go to `archon-server` → Settings → Variables
2. Check that `ARCHON_MCP_URL` shows an actual URL (not an error)
3. Do the same for `archon-frontend` → `VITE_API_URL`

If you see errors, the service names might not match exactly. Service names are case-sensitive!

### Step 4: Deploy Order

Deploy in this order to avoid dependency issues:

1. **First**: `archon-migrations` (sets up database)
2. **Second**: `archon-server` (core API)
3. **Third**: `archon-mcp` and `archon-agents` (depend on server)
4. **Last**: `archon-frontend` (depends on server being available)

You can trigger redeployment by going to each service → Deployments → Click on latest → Redeploy

### Step 5: Test the Deployment

1. **Check archon-server health**: `https://your-server-domain.railway.app/health`
2. **Check archon-mcp health**: `https://your-mcp-domain.railway.app/health`
3. **Check archon-agents health**: `https://your-agents-domain.railway.app/health`
4. **Open frontend**: `https://your-frontend-domain.railway.app`

## Troubleshooting

### Service Won't Build
- Check Dockerfile path matches the configuration
- Verify root directory is correct
- Check build logs for missing dependencies

### Service Crashes on Start
- Check that environment variables are set correctly
- Verify `$PORT` is being used in start command
- Check runtime logs for errors

### Service References Don't Work
- Ensure service names match exactly (case-sensitive)
- Services must be in the same project and environment
- Wait a few seconds after creating services for references to populate

### Database Connection Issues
- Verify `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` are set
- Check that you're using the service_role key, not anon key
- Test connection from archon-server logs

## Service Interdependencies

```
archon-migrations (runs once)
    ↓
archon-server (core API)
    ↓
    ├── archon-mcp (IDE integration)
    ├── archon-agents (AI features)
    └── archon-frontend (user interface)
```

## Performance & Scaling

- **archon-migrations**: Can be scaled to 0 after initial run
- **archon-server**: Should always run (core service)
- **archon-mcp**: Should always run if using IDE integration
- **archon-agents**: Can be scaled to 0 if not using AI features (set AGENTS_ENABLED=false)
- **archon-frontend**: Should always run (user-facing)

## Cost Optimization

To reduce Railway costs:
1. Scale unused services to 0 replicas
2. Use sleep mode for development environments
3. Set appropriate health check intervals
4. Consider disabling `archon-agents` if not using AI features

## Next Steps

After successful deployment:
1. Configure custom domains (optional)
2. Set up monitoring and alerts
3. Configure auto-scaling rules
4. Set up staging environment for testing

## Support

If you encounter issues:
1. Check Railway dashboard → Service → Deployments → Logs
2. Verify all environment variables are set
3. Check GitHub Actions for build errors
4. Review this repository's CLAUDE.md for development guidelines
