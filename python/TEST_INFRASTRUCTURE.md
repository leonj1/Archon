# Backend Test Infrastructure

This document describes the Docker-based test infrastructure for running backend tests.

## Files Created

- **Dockerfile.test** - Multi-stage Docker container for running tests
- **docker-compose.test.yml** - Docker Compose configuration for test orchestration
- **.env.test.example** - Template for test environment variables
- **run-tests.sh** - Convenient bash script for running tests
- **validate-test-setup.sh** - Script to validate test setup

## Fixed Issues

1. **pytest.ini not found**: Removed pytest.ini from .dockerignore
2. **Obsolete version warning**: Removed version attribute from docker-compose.test.yml
3. **Repository pattern**: Included new repository pattern implementation

## Quick Start

1. Copy environment template (optional):
   ```bash
   cp .env.test.example .env.test
   # Edit .env.test with your credentials
   ```

2. Build test image (first time only):
   ```bash
   make test-be-build
   ```
   Note: First build takes 5-10 minutes to download all dependencies.

3. Run tests:
   ```bash
   make test-be              # All tests
   make test-be-unit         # Unit tests only
   make test-be-coverage     # With coverage report
   make test-be-interactive  # Interactive shell for debugging
   ```

## Makefile Targets

The Makefile has been updated with new test targets:

- `make test-be` - Run all backend tests in Docker
- `make test-be-unit` - Run only unit tests
- `make test-be-coverage` - Generate coverage report
- `make test-be-build` - Build/rebuild test image
- `make test-be-interactive` - Open shell in container

## Docker Commands

If you prefer direct Docker commands:

```bash
# Build image
docker build -f Dockerfile.test -t archon-test .

# Run all tests
docker run --rm archon-test

# Run specific test
docker run --rm archon-test pytest tests/test_api_essentials.py -v

# With environment file
docker run --rm --env-file .env.test archon-test

# Interactive debugging
docker run --rm -it archon-test bash
```

## Test Environment Variables

Tests can use these environment variables (via .env.test):

- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_SERVICE_KEY` - Supabase service key
- `OPENAI_API_KEY` - OpenAI API key (for embedding tests)
- `LOGFIRE_TOKEN` - Logfire token (usually disabled for tests)
- `LOGFIRE_ENABLED` - Set to false for tests

## Performance Notes

- First build takes 5-10 minutes (downloading dependencies)
- Subsequent runs use cached layers (much faster)
- Volume mounts cache pytest and playwright data
- Tests run in isolated environment (no local dependencies needed)

## Troubleshooting

If tests fail to build:

1. Run validation script:
   ```bash
   ./validate-test-setup.sh
   ```

2. Check Docker is running:
   ```bash
   docker --version
   docker compose version
   ```

3. Clear Docker cache and rebuild:
   ```bash
   docker system prune -a
   make test-be-build
   ```

## CI/CD Integration

See `.github/workflows/backend-tests.yml.example` for GitHub Actions integration.
