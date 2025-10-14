# Vector Database Setup - Qdrant

## Overview

This project uses Qdrant as the vector database for storing document embeddings. We've set up docker-compose to make it easy to start, stop, and manage Qdrant locally.

## Quick Start

### Start Qdrant (Recommended)

```bash
./start_vectordb.sh
```

This script will:
- ✅ Check Docker is installed
- ✅ Create the `qdrant_storage` directory for data persistence
- ✅ Start Qdrant via docker-compose
- ✅ Wait for health check to pass
- ✅ Display connection information

### Stop Qdrant

```bash
./stop_vectordb.sh
```

This will stop the Qdrant container while **preserving your data** in `./qdrant_storage`.

## Manual Commands

If you prefer manual control:

### Start

```bash
docker compose -f docker-compose.vectordb.yml up -d
```

### Stop

```bash
docker compose -f docker-compose.vectordb.yml down
```

### View Logs

```bash
docker compose -f docker-compose.vectordb.yml logs -f
```

### Check Status

```bash
docker compose -f docker-compose.vectordb.yml ps
```

### Restart

```bash
docker compose -f docker-compose.vectordb.yml restart
```

## Accessing Qdrant

Once started, Qdrant is accessible at:

- **REST API**: http://localhost:6333
- **gRPC API**: localhost:6334
- **Web Dashboard**: http://localhost:6333/dashboard

### Test Connection

```bash
# Check API is responding
curl http://localhost:6333/

# List collections
curl http://localhost:6333/collections

# Get cluster info
curl http://localhost:6333/cluster
```

### Web Dashboard

Open http://localhost:6333/dashboard in your browser to:
- View collections
- Browse vectors
- Monitor performance
- Execute queries

## Data Persistence

### Storage Location

Vector data is persisted to:
```
./qdrant_storage/
```

This directory is:
- ✅ Created automatically
- ✅ Mounted as a Docker volume
- ✅ Persists across container restarts
- ✅ Excluded from git (via .gitignore.vectordb)

### Backup Data

```bash
# Backup
tar -czf qdrant_backup_$(date +%Y%m%d).tar.gz qdrant_storage/

# Restore
tar -xzf qdrant_backup_YYYYMMDD.tar.gz
```

### Clear All Data

```bash
# Stop Qdrant first
./stop_vectordb.sh

# Delete storage directory
rm -rf qdrant_storage/

# Restart (will create fresh storage)
./start_vectordb.sh
```

## Configuration

### Docker Compose File

Location: `docker-compose.vectordb.yml`

Key configuration:
```yaml
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"  # REST API
      - "6334:6334"  # gRPC API
    volumes:
      - ./qdrant_storage:/qdrant/storage
    environment:
      - QDRANT__LOG_LEVEL=INFO
    restart: unless-stopped
```

### Environment Variables

You can customize Qdrant by setting environment variables in `docker-compose.vectordb.yml`:

```yaml
environment:
  - QDRANT__LOG_LEVEL=DEBUG           # DEBUG, INFO, WARN, ERROR
  - QDRANT__SERVICE__GRPC_PORT=6334   # gRPC port
  - QDRANT__SERVICE__HTTP_PORT=6333   # HTTP port
```

See [Qdrant Configuration Docs](https://qdrant.tech/documentation/guides/configuration/) for all options.

## Troubleshooting

### Port Already in Use

**Error:** `Bind for 0.0.0.0:6333 failed: port is already allocated`

**Solution:**
```bash
# Find what's using port 6333
lsof -i :6333

# Kill the process or change the port in docker-compose.vectordb.yml
ports:
  - "6335:6333"  # Use port 6335 instead
```

Then update your code to use the new port:
```bash
export QDRANT_URL=http://localhost:6335
```

### Container Won't Start

**Check logs:**
```bash
docker compose -f docker-compose.vectordb.yml logs
```

**Common issues:**
- Docker daemon not running: `sudo systemctl start docker`
- Permissions issue: `sudo chown -R $USER:$USER qdrant_storage`
- Corrupted data: Stop container, rename `qdrant_storage` to backup, restart

### Health Check Failing

**Check container health:**
```bash
docker compose -f docker-compose.vectordb.yml ps
```

**If unhealthy:**
```bash
# View detailed logs
docker compose -f docker-compose.vectordb.yml logs qdrant

# Restart the service
docker compose -f docker-compose.vectordb.yml restart qdrant
```

### Can't Connect from Code

**Verify connectivity:**
```bash
# From host machine
curl http://localhost:6333/collections

# From Docker container (if your app is also in Docker)
curl http://host.docker.internal:6333/collections
```

**Update connection string in code:**
```python
# For host machine
QDRANT_URL = "http://localhost:6333"

# For Docker containers on same network
QDRANT_URL = "http://archon-vectordb-qdrant:6333"

# For Docker containers on host network
QDRANT_URL = "http://host.docker.internal:6333"
```

## Advanced Usage

### Custom Network

The docker-compose file creates a network called `archon-vectordb-network`. To connect other services:

```yaml
# In your docker-compose.yml
services:
  your-service:
    networks:
      - archon-vectordb-network

networks:
  archon-vectordb-network:
    external: true
```

### Resource Limits

Add resource limits to prevent Qdrant from consuming too much memory:

```yaml
services:
  qdrant:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

### Production Deployment

For production, consider:

1. **Use specific version tag:**
   ```yaml
   image: qdrant/qdrant:v1.7.4  # Instead of :latest
   ```

2. **Enable authentication:**
   ```yaml
   environment:
     - QDRANT__SERVICE__API_KEY=your-secret-key
   ```

3. **Use named volumes:**
   ```yaml
   volumes:
     - qdrant-data:/qdrant/storage

   volumes:
     qdrant-data:
       driver: local
   ```

4. **Set up monitoring:**
   - Prometheus metrics: http://localhost:6333/metrics
   - Health endpoint: http://localhost:6333/healthz

## Integration with Pipeline

The vector database pipeline automatically connects to Qdrant:

```python
# In SimpleVectorDBService
from qdrant_client import AsyncQdrantClient

client = AsyncQdrantClient(url="http://localhost:6333")
```

The services will:
1. Create collections automatically
2. Store document embeddings
3. Perform vector similarity search
4. Clean up test data after tests

## Useful Commands Cheatsheet

```bash
# Start
./start_vectordb.sh

# Stop
./stop_vectordb.sh

# View logs
docker compose -f docker-compose.vectordb.yml logs -f

# Status
docker compose -f docker-compose.vectordb.yml ps

# Restart
docker compose -f docker-compose.vectordb.yml restart

# Remove everything (including data)
docker compose -f docker-compose.vectordb.yml down -v
rm -rf qdrant_storage

# Update to latest version
docker compose -f docker-compose.vectordb.yml pull
docker compose -f docker-compose.vectordb.yml up -d
```

## References

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Qdrant Docker Setup](https://qdrant.tech/documentation/guides/installation/#docker)
- [Qdrant Python Client](https://github.com/qdrant/qdrant-client)
- [Qdrant Configuration](https://qdrant.tech/documentation/guides/configuration/)

## Support

**Issues?**
- Check logs: `docker compose -f docker-compose.vectordb.yml logs`
- Verify connectivity: `curl http://localhost:6333/`
- Check container: `docker compose -f docker-compose.vectordb.yml ps`

**Still stuck?**
- Review troubleshooting section above
- Check Qdrant documentation
- Ensure Docker daemon is running

---

**Quick Start:** Just run `./start_vectordb.sh` and you're ready to go! 🚀
