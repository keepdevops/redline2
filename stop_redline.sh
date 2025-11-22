#!/bin/bash
# REDLINE Complete Shutdown Script
# Stops all REDLINE services (Docker containers and local processes)

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  REDLINE Complete Shutdown${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to stop Docker containers
stop_docker_containers() {
    echo -e "${YELLOW}📦 Stopping Docker containers...${NC}"
    
    if ! command_exists docker; then
        echo -e "${YELLOW}  Docker not found, skipping...${NC}"
        return 0
    fi
    
    # Check for docker-compose files
    COMPOSE_FILES=(
        "docker-compose-full-dev.yml"
        "docker-compose.yml"
        "docker-compose-dev.yml"
        "docker-compose-webgui.yml"
    )
    
    STOPPED_ANY=false
    
    for compose_file in "${COMPOSE_FILES[@]}"; do
        if [ -f "$compose_file" ]; then
            echo -e "  Stopping services from ${compose_file}..."
            docker-compose -f "$compose_file" down 2>/dev/null && STOPPED_ANY=true || true
        fi
    done
    
    # Stop any remaining redline containers
    REDLINE_CONTAINERS=$(docker ps -q --filter "name=redline" 2>/dev/null || true)
    if [ ! -z "$REDLINE_CONTAINERS" ]; then
        echo -e "  Stopping remaining REDLINE containers..."
        docker stop $REDLINE_CONTAINERS 2>/dev/null || true
        docker rm $REDLINE_CONTAINERS 2>/dev/null || true
        STOPPED_ANY=true
    fi
    
    if [ "$STOPPED_ANY" = true ]; then
        echo -e "${GREEN}  ✅ Docker containers stopped${NC}"
    else
        echo -e "${YELLOW}  No Docker containers found${NC}"
    fi
}

# Function to stop local processes
stop_local_processes() {
    echo -e "${YELLOW}🖥️  Stopping local processes...${NC}"
    
    STOPPED_ANY=false
    
    # Stop license server (port 5001)
    LICENSE_PIDS=$(lsof -ti:5001 2>/dev/null || true)
    if [ ! -z "$LICENSE_PIDS" ]; then
        echo -e "  Stopping License Server (PID: $LICENSE_PIDS)..."
        kill $LICENSE_PIDS 2>/dev/null || true
        sleep 1
        STOPPED_ANY=true
    fi
    
    # Stop web app (port 8080)
    WEB_PIDS=$(lsof -ti:8080 2>/dev/null || true)
    if [ ! -z "$WEB_PIDS" ]; then
        echo -e "  Stopping Web App (PID: $WEB_PIDS)..."
        kill $WEB_PIDS 2>/dev/null || true
        sleep 1
        STOPPED_ANY=true
    fi
    
    # Kill by process name
    if pgrep -f "license_server.py" >/dev/null 2>&1; then
        echo -e "  Stopping license_server.py processes..."
        pkill -f "license_server.py" 2>/dev/null || true
        STOPPED_ANY=true
    fi
    
    if pgrep -f "web_app.py" >/dev/null 2>&1; then
        echo -e "  Stopping web_app.py processes..."
        pkill -f "web_app.py" 2>/dev/null || true
        STOPPED_ANY=true
    fi
    
    if pgrep -f "gunicorn" >/dev/null 2>&1; then
        echo -e "  Stopping gunicorn processes..."
        pkill -f "gunicorn" 2>/dev/null || true
        STOPPED_ANY=true
    fi
    
    if [ "$STOPPED_ANY" = true ]; then
        sleep 2
        echo -e "${GREEN}  ✅ Local processes stopped${NC}"
    else
        echo -e "${YELLOW}  No local processes found${NC}"
    fi
}

# Function to verify shutdown
verify_shutdown() {
    echo ""
    echo -e "${BLUE}🔍 Verifying shutdown...${NC}"
    
    ALL_CLEAR=true
    
    # Check ports
    if lsof -i:8080 >/dev/null 2>&1; then
        echo -e "${RED}  ⚠️  Port 8080 is still in use${NC}"
        ALL_CLEAR=false
    else
        echo -e "${GREEN}  ✅ Port 8080 is free${NC}"
    fi
    
    if lsof -i:5001 >/dev/null 2>&1; then
        echo -e "${RED}  ⚠️  Port 5001 is still in use${NC}"
        ALL_CLEAR=false
    else
        echo -e "${GREEN}  ✅ Port 5001 is free${NC}"
    fi
    
    if lsof -i:6379 >/dev/null 2>&1; then
        echo -e "${RED}  ⚠️  Port 6379 (Redis) is still in use${NC}"
        ALL_CLEAR=false
    else
        echo -e "${GREEN}  ✅ Port 6379 is free${NC}"
    fi
    
    # Check Docker containers
    REDLINE_CONTAINERS=$(docker ps -q --filter "name=redline" 2>/dev/null || true)
    if [ ! -z "$REDLINE_CONTAINERS" ]; then
        echo -e "${RED}  ⚠️  Some REDLINE containers are still running${NC}"
        docker ps --filter "name=redline" --format "    {{.Names}}: {{.Status}}"
        ALL_CLEAR=false
    else
        echo -e "${GREEN}  ✅ No REDLINE containers running${NC}"
    fi
    
    echo ""
    if [ "$ALL_CLEAR" = true ]; then
        echo -e "${GREEN}✅ All REDLINE services are stopped${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Some services may still be running${NC}"
        echo -e "${YELLOW}   Run this script again or check manually${NC}"
        return 1
    fi
}

# Main execution
main() {
    stop_docker_containers
    echo ""
    stop_local_processes
    verify_shutdown
    
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}  Shutdown Complete${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# Run main function
main





