#!/bin/bash

# Test script to verify Docker build scripts work correctly

echo "🧪 Testing REDLINE Docker Build Scripts"
echo "========================================="

# Test 1: Check if scripts exist and are executable
echo "📋 Test 1: Checking build script files..."
scripts=("quick_build_web.sh" "build_web_docker.sh" "build_web_docker.bat")

for script in "${scripts[@]}"; do
    if [ -f "$script" ]; then
        if [ -x "$script" ]; then
            echo "✅ $script exists and is executable"
        else
            echo "⚠️  $script exists but is not executable"
            chmod +x "$script"
            echo "✅ Made $script executable"
        fi
    else
        echo "❌ $script not found"
    fi
done

echo ""

# Test 2: Check if Docker is available
echo "📋 Test 2: Checking Docker availability..."
if command -v docker >/dev/null 2>&1; then
    echo "✅ Docker is installed"
    
    # Check if Docker daemon is running
    if docker info >/dev/null 2>&1; then
        echo "✅ Docker daemon is running"
        
        # Check Docker version
        docker_version=$(docker --version)
        echo "✅ Docker version: $docker_version"
        
        # Check if buildx is available
        if docker buildx version >/dev/null 2>&1; then
            echo "✅ Docker buildx is available"
        else
            echo "⚠️  Docker buildx is not available (update Docker to 19.03+)"
        fi
    else
        echo "❌ Docker daemon is not running"
        echo "   Please start Docker Desktop or Docker daemon"
    fi
else
    echo "❌ Docker is not installed"
    echo "   Please install Docker and try again"
fi

echo ""

# Test 3: Check required files
echo "📋 Test 3: Checking required build files..."
required_files=("Dockerfile.web" "requirements_docker.txt" "web_app.py" "redline")

for file in "${required_files[@]}"; do
    if [ -f "$file" ] || [ -d "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file not found"
    fi
done

echo ""

# Test 4: Check help functionality
echo "📋 Test 4: Testing help functionality..."
echo "Testing quick_build_web.sh --help:"
if ./quick_build_web.sh --help >/dev/null 2>&1; then
    echo "✅ quick_build_web.sh help works"
else
    echo "❌ quick_build_web.sh help failed"
fi

echo "Testing build_web_docker.sh --help:"
if ./build_web_docker.sh --help >/dev/null 2>&1; then
    echo "✅ build_web_docker.sh help works"
else
    echo "❌ build_web_docker.sh help failed"
fi

echo ""

# Test 5: Check Dockerfile content
echo "📋 Test 5: Checking Dockerfile.web content..."
if [ -f "Dockerfile.web" ]; then
    if grep -q "FROM python:" Dockerfile.web; then
        echo "✅ Dockerfile.web has Python base image"
    else
        echo "⚠️  Dockerfile.web may not have proper base image"
    fi
    
    if grep -q "COPY web_app.py" Dockerfile.web; then
        echo "✅ Dockerfile.web copies web_app.py"
    else
        echo "⚠️  Dockerfile.web may not copy web_app.py"
    fi
    
    if grep -q "EXPOSE" Dockerfile.web; then
        echo "✅ Dockerfile.web exposes port"
    else
        echo "⚠️  Dockerfile.web may not expose port"
    fi
else
    echo "❌ Dockerfile.web not found"
fi

echo ""

# Test 6: Check requirements file
echo "📋 Test 6: Checking requirements_docker.txt..."
if [ -f "requirements_docker.txt" ]; then
    if grep -q "flask" requirements_docker.txt; then
        echo "✅ requirements_docker.txt includes Flask"
    else
        echo "⚠️  requirements_docker.txt may not include Flask"
    fi
    
    if grep -q "pandas" requirements_docker.txt; then
        echo "✅ requirements_docker.txt includes pandas"
    else
        echo "⚠️  requirements_docker.txt may not include pandas"
    fi
else
    echo "❌ requirements_docker.txt not found"
fi

echo ""

# Summary
echo "🎉 Docker build script testing completed!"
echo ""
echo "To build the Docker image, use one of these commands:"
echo "  ./quick_build_web.sh                    # Quick build with defaults"
echo "  ./quick_build_web.sh my-redline v1.0.0  # Custom name and tag"
echo "  ./build_web_docker.sh                   # Full-featured build"
echo "  ./build_web_docker.sh -p linux/arm64    # Build for ARM64"
echo "  ./build_web_docker.sh --push --test     # Build, push, and test"
echo ""
echo "For Windows users:"
echo "  build_web_docker.bat                    # Windows batch file"
