# UV Timeout Fix Summary

## Problem
The `uv pip install` command was failing with:
```
error: unexpected argument '--timeout' found
```

The `--timeout` flag is not a valid option for `uv pip install`.

## Solution

### Fixed in Dockerfile.server:

1. **Removed invalid `--timeout` flag** from `uv pip install` commands
2. **Kept `UV_HTTP_TIMEOUT` environment variable** - this is the correct way to set timeout for UV
3. **Added retry logic** with descriptive messages
4. **Added debug output** to show the timeout being used

### Key Changes:
```dockerfile
# WRONG - uv pip install doesn't accept --timeout
uv pip install --timeout 300 --group server

# CORRECT - timeout via environment variable
ENV UV_HTTP_TIMEOUT=300
uv pip install --group server
```

## How UV Timeout Works

UV uses environment variables for configuration:
- `UV_HTTP_TIMEOUT` - Controls HTTP request timeout (in seconds)
- `UV_INDEX_STRATEGY` - Controls package resolution strategy

These are set once and apply to all UV commands in that environment.

## Build Commands

### Standard build (5-minute timeout):
```bash
make start
# or
docker compose up --build
```

### Custom timeout for slow connections:
```bash
# 10-minute timeout
UV_TIMEOUT=600 make start

# or via docker-compose
UV_TIMEOUT=600 docker compose up --build
```

### Permanent configuration:
```bash
# Add to .env file
echo "UV_TIMEOUT=600" >> .env
```

## Features Added

1. **Configurable timeout** via `UV_TIMEOUT` build argument
2. **Automatic retry** on failure with 5-second delay
3. **Debug output** showing timeout value being used
4. **Better error messages** for troubleshooting

## Verification

The build now works correctly and will:
1. Show "Using UV_HTTP_TIMEOUT=300 seconds for package downloads"
2. Attempt installation
3. If it fails, wait 5 seconds and retry
4. Download large packages like PyTorch successfully

## Notes

- PyTorch packages can be 200-400MB
- Default 30-second timeout was insufficient
- 300 seconds (5 minutes) is usually enough
- Can increase to 600-900 seconds for very slow connections
