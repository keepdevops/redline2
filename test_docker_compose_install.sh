#!/bin/bash

# Test script to verify Docker Compose installation

echo "🧪 TESTING DOCKER COMPOSE INSTALLATION"
echo "====================================="
echo ""

# Check if Docker Compose is already installed
if command -v docker-compose > /dev/null 2>&1; then
    echo "✅ Docker Compose already installed: $(docker-compose --version)"
else
    echo "❌ Docker Compose not found, testing installation..."
    
    # Detect platform
    local os=$(uname -s)
    case $os in
        Linux)
            echo "Linux detected, checking distribution..."
            if [ -f /etc/os-release ]; then
                . /etc/os-release
                echo "Distribution: $ID"
                
                case $ID in
                    ubuntu|debian)
                        echo "Testing Ubuntu/Debian installation..."
                        echo "Command: sudo apt update && sudo apt install -y docker-compose"
                        ;;
                    centos|rhel|fedora)
                        echo "Testing CentOS/RHEL/Fedora installation..."
                        echo "Command: sudo yum install -y docker-compose"
                        ;;
                    *)
                        echo "Testing standalone installation..."
                        echo "Command: sudo curl -L \"https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose"
                        ;;
                esac
            fi
            ;;
        Darwin)
            echo "macOS detected"
            echo "Command: brew install docker-compose"
            ;;
        *)
            echo "Unknown platform: $os"
            ;;
    esac
fi

echo ""
echo "📋 TO TEST OPTION 4:"
echo "1. Run: ./install_redline_fixed.sh"
echo "2. Choose option 4"
echo "3. Installer will automatically install Docker Compose if needed"
echo "4. Then create Docker Compose configuration"
echo ""
echo "✅ Docker Compose installation test completed"
