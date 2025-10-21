#!/bin/bash

# REDLINE Web GUI - BuildKit-Free Build Wrapper
# This script can be run from anywhere and will find the correct paths

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌${NC} $1"
}

# Find the project root directory
find_project_root() {
    local current_dir="$(pwd)"
    local search_dir="$current_dir"
    
    # Look for the project root by finding dockerfiles/ directory
    while [ "$search_dir" != "/" ]; do
        if [ -d "$search_dir/dockerfiles" ] && [ -f "$search_dir/dockerfiles/Dockerfile.simple" ]; then
            echo "$search_dir"
            return 0
        fi
        search_dir="$(dirname "$search_dir")"
    done
    
    log_error "Could not find REDLINE project root directory"
    log "Please run this script from within the REDLINE project directory"
    log "or ensure dockerfiles/Dockerfile.simple exists"
    exit 1
}

# Main function
main() {
    log "REDLINE Web GUI - BuildKit-Free Build Wrapper"
    log "============================================="
    
    # Find project root
    PROJECT_ROOT="$(find_project_root)"
    log "Found project root: $PROJECT_ROOT"
    
    # Change to project root
    cd "$PROJECT_ROOT"
    
    # Run the actual build script
    log "Running build script from project root..."
    ./scripts/build/buildkit_free_build.sh "$@"
}

# Run main function
main "$@"
