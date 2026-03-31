#!/bin/bash

# =============================================================================
# VarioSync Bytecode Docker Build Script
# Builds production-ready bytecode images for Render, Modal, Supabase, Wasabi
# Supports dynamic image naming at each docker buildx command
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default configuration
DEFAULT_REGISTRY="keepdevops"
DEFAULT_IMAGE_NAME="variosync"
DEFAULT_VERSION="v3.0.0-bytecode"
DEFAULT_PLATFORMS="linux/amd64,linux/arm64"
DOCKERFILE="Dockerfile.webgui.bytecode"
BUILDER_NAME="variosync-builder"
# Remove all stopped containers, unused images, dangling build cache, networks
docker system prune --all --force

# Also remove unused volumes (can reclaim a lot)
docker system prune --all --force --volumes

# Specifically clean BuildKit cache (very effective for repeated build failures)
docker builder prune --all --force

# If using buildx
docker buildx prune --all --force
# Script usage
usage() {
    echo -e "${CYAN}VarioSync Bytecode Docker Build Script${NC}"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -n, --name NAME       Image name (default: ${DEFAULT_IMAGE_NAME})"
    echo "  -r, --registry REG    Registry/namespace (default: ${DEFAULT_REGISTRY})"
    echo "  -v, --version VER     Version tag (default: ${DEFAULT_VERSION})"
    echo "  -p, --platforms PLAT  Platforms to build (default: ${DEFAULT_PLATFORMS})"
    echo "  -t, --target TARGET   Deployment target: render|modal|supabase|wasabi|all"
    echo "  -f, --dockerfile FILE Dockerfile to use (default: ${DOCKERFILE})"
    echo "  --push                Push to registry after build"
    echo "  --load                Load image locally (single platform only)"
    echo "  --no-cache            Build without cache"
    echo "  --dry-run             Show what would be built without building"
    echo "  -i, --interactive     Force interactive mode"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  # Build with custom image name"
    echo "  $0 -n myvariosync -r myregistry --push"
    echo ""
    echo "  # Build for specific target"
    echo "  $0 -t render -n variosync-render --push"
    echo ""
    echo "  # Build for Wasabi S3 storage optimized"
    echo "  $0 -t wasabi -n variosync-wasabi -v v3.0.0-wasabi --push"
    echo ""
    echo "  # Local build for testing"
    echo "  $0 -n test-image --load -p linux/arm64"
    echo ""
    exit 0
}

# Parse command line arguments
REGISTRY="${DEFAULT_REGISTRY}"
IMAGE_NAME="${DEFAULT_IMAGE_NAME}"
VERSION="${DEFAULT_VERSION}"
PLATFORMS="${DEFAULT_PLATFORMS}"
TARGET=""
PUSH_FLAG=""
LOAD_FLAG=""
NO_CACHE=""
DRY_RUN=false
FORCE_INTERACTIVE=false

# Track if arguments were provided (before parsing consumes them)
ARGS_PROVIDED=false
if [[ $# -gt 0 ]]; then
    ARGS_PROVIDED=true
fi

while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--name)
            IMAGE_NAME="$2"
            shift 2
            ;;
        -r|--registry)
            REGISTRY="$2"
            shift 2
            ;;
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        -p|--platforms)
            PLATFORMS="$2"
            shift 2
            ;;
        -t|--target)
            TARGET="$2"
            shift 2
            ;;
        -f|--dockerfile)
            DOCKERFILE="$2"
            shift 2
            ;;
        --push)
            PUSH_FLAG="--push"
            shift
            ;;
        --load)
            LOAD_FLAG="--load"
            shift
            ;;
        --no-cache)
            NO_CACHE="--no-cache"
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -i|--interactive)
            FORCE_INTERACTIVE=true
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

# Construct full image name
FULL_IMAGE="${REGISTRY}/${IMAGE_NAME}"

# Target-specific configurations
configure_target() {
    local target=$1
    case $target in
        render)
            echo -e "${BLUE}Configuring for Render.com deployment...${NC}"
            BUILD_ARGS="--build-arg DEPLOY_TARGET=render"
            EXTRA_TAGS="-t ${FULL_IMAGE}:render -t ${FULL_IMAGE}:render-latest"
            ;;
        modal)
            echo -e "${BLUE}Configuring for Modal serverless deployment...${NC}"
            BUILD_ARGS="--build-arg DEPLOY_TARGET=modal"
            EXTRA_TAGS="-t ${FULL_IMAGE}:modal -t ${FULL_IMAGE}:modal-latest"
            ;;
        supabase)
            echo -e "${BLUE}Configuring for Supabase integration...${NC}"
            BUILD_ARGS="--build-arg DEPLOY_TARGET=supabase"
            EXTRA_TAGS="-t ${FULL_IMAGE}:supabase -t ${FULL_IMAGE}:supabase-latest"
            ;;
        wasabi)
            echo -e "${BLUE}Configuring for Wasabi S3 storage...${NC}"
            BUILD_ARGS="--build-arg DEPLOY_TARGET=wasabi"
            EXTRA_TAGS="-t ${FULL_IMAGE}:wasabi -t ${FULL_IMAGE}:wasabi-latest"
            ;;
        all)
            echo -e "${BLUE}Building for all targets...${NC}"
            BUILD_ARGS=""
            EXTRA_TAGS="-t ${FULL_IMAGE}:render -t ${FULL_IMAGE}:modal -t ${FULL_IMAGE}:supabase -t ${FULL_IMAGE}:wasabi -t ${FULL_IMAGE}:all"
            ;;
        "")
            BUILD_ARGS=""
            EXTRA_TAGS=""
            ;;
        *)
            echo -e "${RED}Unknown target: $target${NC}"
            echo "Valid targets: render, modal, supabase, wasabi, all"
            exit 1
            ;;
    esac
}

# Setup buildx builder
setup_builder() {
    echo -e "${CYAN}Setting up Docker Buildx builder...${NC}"

    # Check if builder exists
    if ! docker buildx inspect ${BUILDER_NAME} &>/dev/null; then
        echo -e "${YELLOW}Creating new builder: ${BUILDER_NAME}${NC}"
        docker buildx create --name ${BUILDER_NAME} --bootstrap --use
    else
        echo -e "${GREEN}Using existing builder: ${BUILDER_NAME}${NC}"
        docker buildx use ${BUILDER_NAME}
    fi

    # Bootstrap the builder
    docker buildx inspect --bootstrap >/dev/null 2>&1
}

# Validate configuration
validate_config() {
    # Check if Dockerfile exists
    if [[ ! -f "${DOCKERFILE}" ]]; then
        echo -e "${RED}Error: Dockerfile not found: ${DOCKERFILE}${NC}"
        exit 1
    fi

    # Cannot use --load with multiple platforms
    if [[ -n "${LOAD_FLAG}" && "${PLATFORMS}" == *","* ]]; then
        echo -e "${YELLOW}Warning: --load only works with single platform${NC}"
        echo -e "${YELLOW}Using first platform: ${PLATFORMS%%,*}${NC}"
        PLATFORMS="${PLATFORMS%%,*}"
    fi

    # Must specify --push or --load
    if [[ -z "${PUSH_FLAG}" && -z "${LOAD_FLAG}" ]]; then
        echo -e "${YELLOW}Note: Neither --push nor --load specified${NC}"
        echo -e "${YELLOW}Image will be built but not stored locally or pushed${NC}"
    fi
}

# Build the image
build_image() {
    echo ""
    echo -e "${GREEN}=============================================${NC}"
    echo -e "${GREEN}  VARIOSYNC BYTECODE DOCKER BUILD${NC}"
    echo -e "${GREEN}=============================================${NC}"
    echo ""
    echo -e "${CYAN}Configuration:${NC}"
    echo -e "  Registry:    ${REGISTRY}"
    echo -e "  Image Name:  ${IMAGE_NAME}"
    echo -e "  Full Image:  ${FULL_IMAGE}"
    echo -e "  Version:     ${VERSION}"
    echo -e "  Platforms:   ${PLATFORMS}"
    echo -e "  Dockerfile:  ${DOCKERFILE}"
    echo -e "  Target:      ${TARGET:-default}"
    echo -e "  Push:        ${PUSH_FLAG:-no}"
    echo -e "  Load:        ${LOAD_FLAG:-no}"
    echo -e "  No Cache:    ${NO_CACHE:-no}"
    echo ""

    # Configure target-specific settings
    configure_target "${TARGET}"

    # Build command
    BUILD_CMD="docker buildx build \
        --platform ${PLATFORMS} \
        -f ${DOCKERFILE} \
        -t ${FULL_IMAGE}:${VERSION} \
        -t ${FULL_IMAGE}:latest \
        -t ${FULL_IMAGE}:bytecode \
        ${EXTRA_TAGS} \
        ${BUILD_ARGS} \
        ${PUSH_FLAG} \
        ${LOAD_FLAG} \
        ${NO_CACHE} \
        ."

    echo -e "${CYAN}Build command:${NC}"
    echo "${BUILD_CMD}"
    echo ""

    if [[ "${DRY_RUN}" == true ]]; then
        echo -e "${YELLOW}DRY RUN - Not executing build${NC}"
        return 0
    fi

    echo -e "${BLUE}Starting build...${NC}"
    echo ""

    eval ${BUILD_CMD}

    echo ""
    echo -e "${GREEN}=============================================${NC}"
    echo -e "${GREEN}  BUILD COMPLETE!${NC}"
    echo -e "${GREEN}=============================================${NC}"
    echo ""
}

# Print deployment instructions
print_instructions() {
    echo -e "${CYAN}Available Images:${NC}"
    echo "  - ${FULL_IMAGE}:${VERSION}"
    echo "  - ${FULL_IMAGE}:latest"
    echo "  - ${FULL_IMAGE}:bytecode"

    if [[ -n "${TARGET}" && "${TARGET}" != "" ]]; then
        echo "  - ${FULL_IMAGE}:${TARGET}"
        echo "  - ${FULL_IMAGE}:${TARGET}-latest"
    fi

    echo ""
    echo -e "${CYAN}Deployment Examples:${NC}"
    echo ""

    echo -e "${YELLOW}Render.com:${NC}"
    echo "  # Set in render.yaml or dashboard:"
    echo "  image: ${FULL_IMAGE}:${VERSION}"
    echo "  envVars:"
    echo "    - key: SUPABASE_URL"
    echo "      sync: false"
    echo "    - key: SUPABASE_SERVICE_KEY"
    echo "      sync: false"
    echo "    - key: S3_ENDPOINT_URL"
    echo "      value: https://s3.wasabisys.com"
    echo ""

    echo -e "${YELLOW}Modal:${NC}"
    echo "  # In your Modal app:"
    echo "  image = modal.Image.from_registry('${FULL_IMAGE}:${VERSION}')"
    echo ""

    echo -e "${YELLOW}Supabase Functions:${NC}"
    echo "  # Deploy as edge function with container"
    echo "  supabase functions deploy --image ${FULL_IMAGE}:${VERSION}"
    echo ""

    echo -e "${YELLOW}Local Docker Run:${NC}"
    echo "  docker run -d -p 8080:8080 \\"
    echo "    -e SUPABASE_URL=\$SUPABASE_URL \\"
    echo "    -e SUPABASE_SERVICE_KEY=\$SUPABASE_SERVICE_KEY \\"
    echo "    -e S3_ENDPOINT_URL=https://s3.wasabisys.com \\"
    echo "    -e S3_BUCKET=\$S3_BUCKET \\"
    echo "    -e S3_ACCESS_KEY=\$S3_ACCESS_KEY \\"
    echo "    -e S3_SECRET_KEY=\$S3_SECRET_KEY \\"
    echo "    -v variosync-data:/app/data \\"
    echo "    ${FULL_IMAGE}:${VERSION}"
    echo ""

    echo -e "${GREEN}Build Features:${NC}"
    echo "  - Pre-compiled Python bytecode (faster startup)"
    echo "  - Minified JavaScript and CSS assets"
    echo "  - Multi-platform: AMD64 + ARM64"
    echo "  - Production-optimized Gunicorn settings"
    echo "  - Cloud-native: Render, Modal, Supabase, Wasabi ready"
    echo ""
}

# Interactive mode for full configuration
interactive_mode() {
    if [[ ! -t 0 ]]; then
        echo -e "${YELLOW}Not running in interactive terminal, using defaults${NC}"
        return
    fi

    echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║     VarioSync Bytecode Build - Interactive Mode        ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Registry
    echo -e "${YELLOW}Registry/Namespace${NC}"
    read -p "  Enter registry [${REGISTRY}]: " input_registry
    if [[ -n "${input_registry}" ]]; then
        REGISTRY="${input_registry}"
    fi

    # Image name
    echo ""
    echo -e "${YELLOW}Image Name${NC}"
    read -p "  Enter image name [${IMAGE_NAME}]: " input_name
    if [[ -n "${input_name}" ]]; then
        IMAGE_NAME="${input_name}"
    fi
    FULL_IMAGE="${REGISTRY}/${IMAGE_NAME}"

    # Version with suggestions
    echo ""
    echo -e "${YELLOW}Version Tag${NC}"
    echo -e "  ${BLUE}Suggestions:${NC}"
    echo "    1) v3.0.0-bytecode (current default)"
    echo "    2) v3.0.1-bytecode"
    echo "    3) v3.1.0-bytecode"
    echo "    4) latest"
    echo "    5) Custom"
    read -p "  Select version [1-5] or enter custom [${VERSION}]: " version_choice
    case ${version_choice} in
        1) VERSION="v3.0.0-bytecode" ;;
        2) VERSION="v3.0.1-bytecode" ;;
        3) VERSION="v3.1.0-bytecode" ;;
        4) VERSION="latest" ;;
        5)
            read -p "  Enter custom version: " custom_version
            if [[ -n "${custom_version}" ]]; then
                VERSION="${custom_version}"
            fi
            ;;
        "")
            # Keep default
            ;;
        *)
            # Treat as custom version input
            VERSION="${version_choice}"
            ;;
    esac

    # Deployment target
    echo ""
    echo -e "${YELLOW}Deployment Target${NC}"
    echo "  1) render      - Render.com deployment"
    echo "  2) modal       - Modal serverless"
    echo "  3) supabase    - Supabase integration"
    echo "  4) wasabi      - Wasabi S3 storage"
    echo "  5) all         - All targets"
    echo "  6) none        - Generic build (default)"
    read -p "  Select target [1-6]: " target_choice
    case ${target_choice} in
        1) TARGET="render" ;;
        2) TARGET="modal" ;;
        3) TARGET="supabase" ;;
        4) TARGET="wasabi" ;;
        5) TARGET="all" ;;
        6|"") TARGET="" ;;
        *) TARGET="" ;;
    esac

    # Build mode (push/load/local)
    echo ""
    echo -e "${YELLOW}Build Mode${NC}"
    echo "  1) ${GREEN}push${NC}   - Build and push to registry (multi-platform)"
    echo "  2) ${GREEN}load${NC}   - Build and load locally (single platform)"
    echo "  3) ${GREEN}local${NC}  - Build only, don't push or load (cache build)"
    read -p "  Select build mode [1-3]: " build_mode
    case ${build_mode} in
        1)
            PUSH_FLAG="--push"
            LOAD_FLAG=""
            ;;
        2)
            PUSH_FLAG=""
            LOAD_FLAG="--load"
            ;;
        3|"")
            PUSH_FLAG=""
            LOAD_FLAG=""
            ;;
        *)
            PUSH_FLAG=""
            LOAD_FLAG=""
            ;;
    esac

    # Platform selection
    echo ""
    echo -e "${YELLOW}Platform Selection${NC}"
    echo "  1) linux/amd64,linux/arm64 (multi-platform, default)"
    echo "  2) linux/amd64 only"
    echo "  3) linux/arm64 only"
    echo "  4) Custom"
    read -p "  Select platform [1-4]: " platform_choice
    case ${platform_choice} in
        1|"") PLATFORMS="linux/amd64,linux/arm64" ;;
        2) PLATFORMS="linux/amd64" ;;
        3) PLATFORMS="linux/arm64" ;;
        4)
            read -p "  Enter custom platforms: " custom_platforms
            if [[ -n "${custom_platforms}" ]]; then
                PLATFORMS="${custom_platforms}"
            fi
            ;;
    esac

    # No cache option
    echo ""
    echo -e "${YELLOW}Build Options${NC}"
    read -p "  Use --no-cache (fresh build)? [y/N]: " cache_choice
    if [[ "${cache_choice}" =~ ^[Yy]$ ]]; then
        NO_CACHE="--no-cache"
    fi

    # Dry run option
    read -p "  Dry run (show command without executing)? [y/N]: " dry_choice
    if [[ "${dry_choice}" =~ ^[Yy]$ ]]; then
        DRY_RUN=true
    fi

    # Confirmation
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}Configuration Summary:${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "  Full Image:   ${GREEN}${FULL_IMAGE}:${VERSION}${NC}"
    echo -e "  Platforms:    ${PLATFORMS}"
    echo -e "  Target:       ${TARGET:-generic}"
    echo -e "  Build Mode:   $([ -n "${PUSH_FLAG}" ] && echo "push" || ([ -n "${LOAD_FLAG}" ] && echo "load" || echo "local"))"
    echo -e "  No Cache:     $([ -n "${NO_CACHE}" ] && echo "yes" || echo "no")"
    echo -e "  Dry Run:      $([ "${DRY_RUN}" == true ] && echo "yes" || echo "no")"
    echo ""
    read -p "Proceed with build? [Y/n]: " confirm
    if [[ "${confirm}" =~ ^[Nn]$ ]]; then
        echo -e "${YELLOW}Build cancelled.${NC}"
        exit 0
    fi
    echo ""
}

# Main execution
main() {
    echo ""
    echo -e "${GREEN}====================================================${NC}"
    echo -e "${GREEN}  VarioSync Bytecode Docker Build${NC}"
    echo -e "${GREEN}  For Render, Modal, Supabase, Wasabi${NC}"
    echo -e "${GREEN}====================================================${NC}"
    echo ""

    # Run interactive mode if no arguments provided or forced
    if [[ "${ARGS_PROVIDED}" == false || "${FORCE_INTERACTIVE}" == true ]]; then
        interactive_mode
    fi

    # Validate configuration
    validate_config

    # Setup builder
    setup_builder

    # Build the image
    build_image

    # Print deployment instructions
    print_instructions
}

# Run main function
main
