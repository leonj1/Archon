#!/bin/bash

# Test Runner Script for Archon Backend
# Usage: ./run-tests.sh [options]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
TEST_TYPE="all"
VERBOSE=""
COVERAGE=""
BUILD_FLAG=""
INTERACTIVE=""

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -t, --type TYPE      Test type: all, unit, integration, specific (default: all)"
    echo "  -f, --file FILE      Specific test file to run (use with -t specific)"
    echo "  -v, --verbose        Run tests in verbose mode"
    echo "  -c, --coverage       Generate coverage report"
    echo "  -b, --build          Force rebuild of Docker image"
    echo "  -i, --interactive    Run container in interactive mode"
    echo "  -h, --help           Display this help message"
    echo ""
    echo "Examples:"
    echo "  $0                           # Run all tests"
    echo "  $0 -t unit                   # Run only unit tests"
    echo "  $0 -t specific -f test_api_essentials.py  # Run specific test file"
    echo "  $0 -v -c                     # Run all tests with verbose output and coverage"
    echo "  $0 -i                        # Start interactive shell in test container"
    exit 0
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            TEST_TYPE="$2"
            shift 2
            ;;
        -f|--file)
            TEST_FILE="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        -c|--coverage)
            COVERAGE="--cov=src --cov-report=term-missing --cov-report=html"
            shift
            ;;
        -b|--build)
            BUILD_FLAG="--build"
            shift
            ;;
        -i|--interactive)
            INTERACTIVE="yes"
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            ;;
    esac
done

# Check if .env.test exists
if [ ! -f ".env.test" ] && [ -f ".env.test.example" ]; then
    echo -e "${YELLOW}Warning: .env.test not found. Copy .env.test.example to .env.test and configure it.${NC}"
    echo -e "${YELLOW}Running with default environment variables...${NC}"
    ENV_FILE=""
else
    ENV_FILE="--env-file .env.test"
fi

# Build the Docker image if needed
if [ -n "$BUILD_FLAG" ]; then
    echo -e "${GREEN}Building test Docker image...${NC}"
    docker build -f Dockerfile.test -t archon-test .
fi

# Run interactive mode
if [ -n "$INTERACTIVE" ]; then
    echo -e "${GREEN}Starting interactive shell in test container...${NC}"
    docker-compose -f docker-compose.test.yml $ENV_FILE run --rm test bash
    exit 0
fi

# Construct the test command
case $TEST_TYPE in
    all)
        TEST_CMD="pytest $VERBOSE $COVERAGE"
        echo -e "${GREEN}Running all tests...${NC}"
        ;;
    unit)
        TEST_CMD="pytest -m unit $VERBOSE $COVERAGE"
        echo -e "${GREEN}Running unit tests only...${NC}"
        ;;
    integration)
        TEST_CMD="pytest -m integration $VERBOSE $COVERAGE"
        echo -e "${GREEN}Running integration tests only...${NC}"
        ;;
    specific)
        if [ -z "$TEST_FILE" ]; then
            echo -e "${RED}Error: Test file not specified. Use -f option.${NC}"
            exit 1
        fi
        TEST_CMD="pytest tests/$TEST_FILE $VERBOSE $COVERAGE"
        echo -e "${GREEN}Running specific test: $TEST_FILE${NC}"
        ;;
    *)
        echo -e "${RED}Invalid test type: $TEST_TYPE${NC}"
        usage
        ;;
esac

# Run the tests
echo -e "${GREEN}Executing: $TEST_CMD${NC}"
docker-compose -f docker-compose.test.yml $ENV_FILE run --rm test $TEST_CMD

# Check exit code
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    
    # Display coverage report location if generated
    if [ -n "$COVERAGE" ]; then
        echo -e "${GREEN}Coverage report generated in htmlcov/index.html${NC}"
    fi
else
    echo -e "${RED}❌ Tests failed!${NC}"
    exit 1
fi
