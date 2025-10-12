#!/bin/bash

# Script to validate test setup fixes

echo "=== Validating Test Setup Fixes ==="
echo ""

# Check if pytest.ini exists
echo "1. Checking pytest.ini..."
if [ -f "pytest.ini" ]; then
    echo "   ✅ pytest.ini exists"
else
    echo "   ❌ pytest.ini not found"
    exit 1
fi

# Check if pytest.ini is not in .dockerignore
echo "2. Checking .dockerignore..."
if grep -q "^pytest.ini$" .dockerignore; then
    echo "   ❌ pytest.ini is excluded in .dockerignore"
    exit 1
else
    echo "   ✅ pytest.ini is not excluded"
fi

# Check docker-compose.test.yml doesn't have version
echo "3. Checking docker-compose.test.yml..."
if grep -q "^version:" docker-compose.test.yml; then
    echo "   ❌ docker-compose.test.yml has obsolete version attribute"
    exit 1
else
    echo "   ✅ docker-compose.test.yml has no version attribute"
fi

# Check Dockerfile.test exists
echo "4. Checking Dockerfile.test..."
if [ -f "Dockerfile.test" ]; then
    echo "   ✅ Dockerfile.test exists"
    
    # Check if it has the COPY pytest.ini command
    if grep -q "COPY pytest.ini" Dockerfile.test; then
        echo "   ✅ Dockerfile.test copies pytest.ini"
    else
        echo "   ❌ Dockerfile.test doesn't copy pytest.ini"
        exit 1
    fi
else
    echo "   ❌ Dockerfile.test not found"
    exit 1
fi

# Check if repositories folder exists in src/server
echo "5. Checking repository pattern implementation..."
if [ -d "src/server/repositories" ]; then
    echo "   ✅ repositories folder exists"
    if [ -f "src/server/repositories/database_repository.py" ]; then
        echo "   ✅ database_repository.py exists"
    fi
    if [ -f "src/server/repositories/supabase_repository.py" ]; then
        echo "   ✅ supabase_repository.py exists"
    fi
else
    echo "   ⚠️  repositories folder not found (expected for new implementation)"
fi

echo ""
echo "=== All checks passed! ==="
echo ""
echo "The test setup should work correctly now."
echo "Note: First Docker build will take time to download all dependencies."
echo ""
echo "To run tests:"
echo "  make test-be          # Run all backend tests"
echo "  make test-be-unit     # Run unit tests only"
echo "  make test-be-coverage # Run with coverage report"
