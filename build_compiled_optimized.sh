#!/bin/bash

# Build Optimized Compiled Docker Images (Smaller Size)
# Fixes the size issues in the previous compiled version

set -e

IMAGE_NAME="redline-webgui-compiled-optimized"
VERSION="v1.0.0"

echo "🚀 Building Optimized Compiled Docker Images for $IMAGE_NAME:$VERSION"
echo "📦 This version removes Node.js and optimizes bytecode for minimal size"
echo ""

# Ensure Buildx is available
if ! docker buildx ls | grep -q "multiplatform"; then
    echo "Creating multiplatform builder..."
    docker buildx create --name multiplatform --bootstrap --use
else
    echo "Using existing multiplatform builder."
    docker buildx use multiplatform
fi

echo "📊 Size Comparison Prediction:"
echo "  Previous compiled: ~1.7GB (AMD64), ~1.6GB (ARM64)"
echo "  Optimized compiled: ~400-500MB (estimated)"
echo "  Uncompiled:        ~332MB (AMD64), ~652MB (ARM64)"
echo ""

# Build AMD64 image
echo "💾 Building AMD64 optimized compiled image..."
docker buildx build \
    --platform linux/amd64 \
    -f Dockerfile.webgui.compiled-optimized \
    -t ${IMAGE_NAME}:amd64 \
    --output "type=docker,dest=redline-webgui-compiled-optimized-amd64.tar" \
    .
echo "✅ Saved: redline-webgui-compiled-optimized-amd64.tar"

# Build ARM64 image
echo "💾 Building ARM64 optimized compiled image..."
docker buildx build \
    --platform linux/arm64 \
    -f Dockerfile.webgui.compiled-optimized \
    -t ${IMAGE_NAME}:arm64 \
    --output "type=docker,dest=redline-webgui-compiled-optimized-arm64.tar" \
    .
echo "✅ Saved: redline-webgui-compiled-optimized-arm64.tar"

echo ""
echo "📊 Final File Sizes:"
ls -lh redline-webgui-compiled-optimized-*.tar

echo ""
echo "🎯 Optimizations Applied:"
echo "  ❌ Removed Node.js installation (~300MB saved)"
echo "  ❌ Removed npm and terser/cssnano (~50MB saved)"
echo "  ✅ Added BuildKit cache mounts for faster builds"
echo "  ✅ Simple Python-based CSS/JS minification"
echo "  ✅ Removed source .py files after compilation"
echo "  ✅ Multi-stage build with minimal runtime dependencies"

echo ""
echo "📋 Usage Instructions:"
echo ""
echo "For Dell Machine (AMD64):"
echo "  docker load -i redline-webgui-compiled-optimized-amd64.tar"
echo "  docker tag ${IMAGE_NAME}:amd64 ${IMAGE_NAME}:latest"
echo "  docker run -d --name redline-webgui -p 8080:8080 ${IMAGE_NAME}:latest"
echo ""
echo "For Apple Silicon (ARM64):"
echo "  docker load -i redline-webgui-compiled-optimized-arm64.tar"
echo "  docker tag ${IMAGE_NAME}:arm64 ${IMAGE_NAME}:latest"
echo "  docker run -d --name redline-webgui -p 8080:8080 ${IMAGE_NAME}:latest"

echo ""
echo "🎉 Optimized Compiled Images Built Successfully!"
echo "Expected: 60-70% smaller than previous compiled version"
