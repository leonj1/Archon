# PyTorch Download Timeout Fix

## Problem
The Docker build was failing with:
```
Failed to download `torch==2.8.0+cpu`
Failed to download distribution due to network timeout. Try increasing UV_HTTP_TIMEOUT (current value: 30s)
```

PyTorch packages are very large (hundreds of MBs), and the default 30-second timeout was insufficient.

## Solution Applied

### 1. Dockerfile.server Changes
- Added configurable `UV_TIMEOUT` build argument (default: 300 seconds)
- Set `UV_HTTP_TIMEOUT` environment variable
- Added `UV_INDEX_STRATEGY=unsafe-best-match` for better package resolution
- Implemented retry logic with 5-second delay on failure
- Applied timeout to `uv pip install` command

### 2. docker-compose.yml Changes
- Added `UV_TIMEOUT` build argument support
- Defaults to 300 seconds (5 minutes)
- Can be overridden via environment variable

## Usage

### Default Build (5-minute timeout)
```bash
make start
# or
docker compose up --build
```

### Custom Timeout (for very slow connections)
```bash
# Set 10-minute timeout
UV_TIMEOUT=600 make start

# or
UV_TIMEOUT=600 docker compose up --build
```

### Add to .env file (permanent)
```bash
echo "UV_TIMEOUT=600" >> .env
```

## Additional Options

If you continue to have issues:

1. **Increase timeout further**:
   ```bash
   UV_TIMEOUT=900 make start  # 15 minutes
   ```

2. **Use pre-built images** (if available):
   ```bash
   docker pull ghcr.io/your-org/archon-server:latest
   ```

3. **Build with better network**:
   - Build on a server with better connectivity
   - Use Docker BuildKit cache mounts
   - Consider using a local PyPI mirror

4. **Alternative: Remove reranking** (if not needed):
   - Edit `Dockerfile.server` 
   - Remove `--group server-reranking` from the install command
   - This skips PyTorch installation entirely

## Verification

After successful build, verify the installation:
```bash
docker compose exec archon-server python -c "import torch; print(torch.__version__)"
```

## Network Optimization Tips

- Build during off-peak hours
- Use wired connection instead of WiFi
- Consider using a VPN to a region closer to PyPI servers
- Enable Docker BuildKit for better caching:
  ```bash
  DOCKER_BUILDKIT=1 docker compose build
  ```
