#!/bin/bash

# Database Setup Script for Archon
# This script starts MySQL and PostgreSQL containers for testing

set -e

echo "=" 
echo "🚀 Archon Database Setup"
echo "="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    # Try docker compose (newer syntax)
    if ! docker compose version &> /dev/null; then
        echo -e "${RED}❌ Docker Compose is not installed${NC}"
        echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# Navigate to the python directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

# Check if docker-compose.dev.yml exists
if [ ! -f "docker-compose.dev.yml" ]; then
    echo -e "${RED}❌ docker-compose.dev.yml not found${NC}"
    echo "Please run this script from the python directory"
    exit 1
fi

# Parse arguments
DB_TYPE="${1:-all}"
ACTION="${2:-up}"

case $ACTION in
    up|start)
        echo "Starting databases..."
        
        if [ "$DB_TYPE" = "mysql" ]; then
            echo -e "${YELLOW}Starting MySQL...${NC}"
            $DOCKER_COMPOSE -f docker-compose.dev.yml up -d mysql
        elif [ "$DB_TYPE" = "postgres" ]; then
            echo -e "${YELLOW}Starting PostgreSQL...${NC}"
            $DOCKER_COMPOSE -f docker-compose.dev.yml up -d postgres
        else
            echo -e "${YELLOW}Starting all databases...${NC}"
            $DOCKER_COMPOSE -f docker-compose.dev.yml up -d
        fi
        
        echo ""
        echo -e "${GREEN}✓ Databases started${NC}"
        echo ""
        echo "Waiting for databases to be ready..."
        
        # Wait for MySQL
        if [ "$DB_TYPE" = "mysql" ] || [ "$DB_TYPE" = "all" ]; then
            echo -n "  MySQL: "
            for i in {1..30}; do
                if docker exec archon-mysql mysqladmin ping -h localhost -u root -proot_secure_password &> /dev/null; then
                    echo -e "${GREEN}Ready${NC}"
                    break
                fi
                echo -n "."
                sleep 1
            done
        fi
        
        # Wait for PostgreSQL
        if [ "$DB_TYPE" = "postgres" ] || [ "$DB_TYPE" = "all" ]; then
            echo -n "  PostgreSQL: "
            for i in {1..30}; do
                if docker exec archon-postgres pg_isready -U archon &> /dev/null; then
                    echo -e "${GREEN}Ready${NC}"
                    break
                fi
                echo -n "."
                sleep 1
            done
        fi
        
        echo ""
        echo -e "${GREEN}✅ All databases are ready!${NC}"
        echo ""
        echo "Connection details:"
        
        if [ "$DB_TYPE" = "mysql" ] || [ "$DB_TYPE" = "all" ]; then
            echo "  MySQL:"
            echo "    Host: localhost"
            echo "    Port: 3306"
            echo "    Database: archon_db"
            echo "    User: archon"
            echo "    Password: archon_secure_password"
        fi
        
        if [ "$DB_TYPE" = "postgres" ] || [ "$DB_TYPE" = "all" ]; then
            echo "  PostgreSQL:"
            echo "    Host: localhost"
            echo "    Port: 5432"
            echo "    Database: archon_db"
            echo "    User: archon"
            echo "    Password: archon_secure_password"
        fi
        
        echo ""
        echo "Adminer (Database UI): http://localhost:8080"
        ;;
        
    down|stop)
        echo "Stopping databases..."
        
        if [ "$DB_TYPE" = "mysql" ]; then
            $DOCKER_COMPOSE -f docker-compose.dev.yml stop mysql
        elif [ "$DB_TYPE" = "postgres" ]; then
            $DOCKER_COMPOSE -f docker-compose.dev.yml stop postgres
        else
            $DOCKER_COMPOSE -f docker-compose.dev.yml down
        fi
        
        echo -e "${GREEN}✓ Databases stopped${NC}"
        ;;
        
    clean)
        echo -e "${YELLOW}⚠️  This will delete all database data!${NC}"
        read -p "Are you sure? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            $DOCKER_COMPOSE -f docker-compose.dev.yml down -v
            echo -e "${GREEN}✓ Databases and volumes removed${NC}"
        else
            echo "Cancelled"
        fi
        ;;
        
    logs)
        if [ "$DB_TYPE" = "mysql" ]; then
            $DOCKER_COMPOSE -f docker-compose.dev.yml logs -f mysql
        elif [ "$DB_TYPE" = "postgres" ]; then
            $DOCKER_COMPOSE -f docker-compose.dev.yml logs -f postgres
        else
            $DOCKER_COMPOSE -f docker-compose.dev.yml logs -f
        fi
        ;;
        
    status)
        echo "Database Status:"
        $DOCKER_COMPOSE -f docker-compose.dev.yml ps
        ;;
        
    *)
        echo "Usage: $0 [mysql|postgres|all] [up|down|clean|logs|status]"
        echo ""
        echo "Commands:"
        echo "  up/start  - Start databases"
        echo "  down/stop - Stop databases"
        echo "  clean     - Remove databases and volumes"
        echo "  logs      - Show database logs"
        echo "  status    - Show container status"
        echo ""
        echo "Examples:"
        echo "  $0              # Start all databases"
        echo "  $0 mysql        # Start only MySQL"
        echo "  $0 postgres     # Start only PostgreSQL"
        echo "  $0 all down     # Stop all databases"
        echo "  $0 mysql logs   # Show MySQL logs"
        exit 1
        ;;
esac