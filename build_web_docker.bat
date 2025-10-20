@echo off
REM REDLINE Web Application Docker Build Script for Windows
REM Uses Docker buildx for Linux container builds

setlocal enabledelayedexpansion

REM Configuration
set DEFAULT_IMAGE_NAME=redline-web
set DEFAULT_TAG=latest
set DEFAULT_PLATFORM=linux/amd64
set DEFAULT_DOCKERFILE=Dockerfile.web

REM Parse command line arguments
set IMAGE_NAME=%DEFAULT_IMAGE_NAME%
set TAG=%DEFAULT_TAG%
set PLATFORM=%DEFAULT_PLATFORM%
set DOCKERFILE=%DEFAULT_DOCKERFILE%
set PUSH=false
set NO_CACHE=false
set TEST=false

:parse_args
if "%~1"=="" goto :start_build
if "%~1"=="-i" (
    set IMAGE_NAME=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--image" (
    set IMAGE_NAME=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-t" (
    set TAG=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--tag" (
    set TAG=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-p" (
    set PLATFORM=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--platform" (
    set PLATFORM=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--push" (
    set PUSH=true
    shift
    goto :parse_args
)
if "%~1"=="--no-cache" (
    set NO_CACHE=true
    shift
    goto :parse_args
)
if "%~1"=="--test" (
    set TEST=true
    shift
    goto :parse_args
)
if "%~1"=="--help" (
    goto :show_help
)
shift
goto :parse_args

:show_help
echo Usage: %0 [OPTIONS]
echo.
echo Options:
echo   -i, --image NAME       Docker image name (default: %DEFAULT_IMAGE_NAME%)
echo   -t, --tag TAG          Docker image tag (default: %DEFAULT_TAG%)
echo   -p, --platform PLATFORM   Target platform (default: %DEFAULT_PLATFORM%)
echo   --push                 Push image to registry after build
echo   --no-cache             Build without using cache
echo   --test                 Test the built image
echo   --help                 Show this help message
echo.
echo Platform Options:
echo   linux/amd64            Intel/AMD 64-bit Linux
echo   linux/arm64            ARM 64-bit Linux
echo   linux/arm/v7           ARM v7 Linux
echo.
echo Examples:
echo   %0                                    # Build with defaults
echo   %0 -i redline-web -t v1.0.0         # Custom name and tag
echo   %0 -p linux/arm64                    # Build for ARM64
echo   %0 --push --test                     # Build, push, and test
goto :eof

:start_build
echo ==============================================
echo   REDLINE Web Application Docker Build
echo ==============================================
echo.

REM Check if Docker is available
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed or not in PATH
    echo [ERROR] Please install Docker Desktop and try again
    pause
    exit /b 1
)

REM Check if Docker daemon is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker daemon is not running
    echo [ERROR] Please start Docker Desktop and try again
    pause
    exit /b 1
)

echo [INFO] Docker is available and running

REM Check if buildx is available
docker buildx version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker buildx is not available
    echo [ERROR] Please update Docker to a version that supports buildx
    pause
    exit /b 1
)

echo [INFO] Docker buildx is available

REM Check if Dockerfile exists
if not exist "%DOCKERFILE%" (
    echo [ERROR] Dockerfile not found: %DOCKERFILE%
    pause
    exit /b 1
)

REM Check if requirements file exists
if not exist "requirements_docker.txt" (
    echo [ERROR] requirements_docker.txt not found
    pause
    exit /b 1
)

REM Check if web_app.py exists
if not exist "web_app.py" (
    echo [ERROR] web_app.py not found
    pause
    exit /b 1
)

echo [INFO] All required files validated

REM Setup buildx builder
echo [INFO] Setting up Docker buildx builder...
docker buildx create --name redline-builder --use >nul 2>&1
if errorlevel 1 (
    echo [INFO] Using existing buildx builder instance...
    docker buildx use redline-builder >nul 2>&1
)

REM Build the image
echo [INFO] Building Docker image...
echo [INFO] Image: %IMAGE_NAME%:%TAG%
echo [INFO] Platform: %PLATFORM%
echo [INFO] Dockerfile: %DOCKERFILE%

REM Build command
set BUILD_CMD=docker buildx build --platform %PLATFORM% --tag %IMAGE_NAME%:%TAG% --file %DOCKERFILE%

if "%PUSH%"=="true" (
    set BUILD_CMD=%BUILD_CMD% --push
    echo [INFO] Will push to registry after build
) else (
    set BUILD_CMD=%BUILD_CMD% --load
)

if "%NO_CACHE%"=="true" (
    set BUILD_CMD=%BUILD_CMD% --no-cache
)

REM Execute build command
%BUILD_CMD% .

if errorlevel 1 (
    echo [ERROR] Docker image build failed
    pause
    exit /b 1
)

echo [INFO] Docker image built successfully!

REM Test the image if requested and not pushing
if "%TEST%"=="true" if "%PUSH%"=="false" (
    echo [INFO] Testing built image...
    
    REM Start test container
    docker run -d -p 8080:8080 --name redline-test-temp %IMAGE_NAME%:%TAG% >nul 2>&1
    
    if errorlevel 1 (
        echo [ERROR] Failed to start test container
        goto :cleanup_test
    )
    
    REM Wait for container to be ready
    echo [INFO] Waiting for container to be ready...
    timeout /t 10 /nobreak >nul
    
    REM Test health endpoint
    curl -f http://localhost:8080/health >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Image test failed - container not responding
        docker logs redline-test-temp
        goto :cleanup_test
    )
    
    echo [INFO] Image test successful! Container is healthy.
    
    :cleanup_test
    docker stop redline-test-temp >nul 2>&1
    docker rm redline-test-temp >nul 2>&1
    echo [INFO] Test container cleaned up
)

echo.
echo [INFO] 🎉 Docker build completed successfully!
echo [INFO] Image: %IMAGE_NAME%:%TAG%
echo [INFO] Platform: %PLATFORM%

if "%PUSH%"=="false" (
    echo.
    echo [INFO] To run the container:
    echo [INFO]   docker run -p 8080:8080 %IMAGE_NAME%:%TAG%
    echo.
    echo [INFO] To push to registry:
    echo [INFO]   docker push %IMAGE_NAME%:%TAG%
)

if "%TEST%"=="false" if "%PUSH%"=="false" (
    echo.
    echo [INFO] To test the image:
    echo [INFO]   %0 --test -i %IMAGE_NAME% -t %TAG%
)

pause
