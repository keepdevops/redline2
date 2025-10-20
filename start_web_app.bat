@echo off
REM REDLINE Flask Web Application Startup Script for Windows
REM This script handles the startup process for the REDLINE web application

setlocal enabledelayedexpansion

REM Configuration
set DEFAULT_PORT=8082
set DEFAULT_HOST=0.0.0.0
set DEFAULT_DEBUG=false

REM Parse command line arguments
set PORT=%DEFAULT_PORT%
set HOST=%DEFAULT_HOST%
set DEBUG=%DEFAULT_DEBUG%
set KILL_EXISTING=false

:parse_args
if "%~1"=="" goto :start_app
if "%~1"=="-p" (
    set PORT=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--port" (
    set PORT=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-h" (
    set HOST=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--host" (
    set HOST=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-d" (
    set DEBUG=true
    shift
    goto :parse_args
)
if "%~1"=="--debug" (
    set DEBUG=true
    shift
    goto :parse_args
)
if "%~1"=="-k" (
    set KILL_EXISTING=true
    shift
    goto :parse_args
)
if "%~1"=="--kill" (
    set KILL_EXISTING=true
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
echo   -p, --port PORT      Set the port number (default: %DEFAULT_PORT%)
echo   -h, --host HOST      Set the host address (default: %DEFAULT_HOST%)
echo   -d, --debug          Enable debug mode
echo   -k, --kill           Kill any existing process on the specified port
echo   --help               Show this help message
echo.
echo Examples:
echo   %0                           # Start with default settings
echo   %0 -p 8080                   # Start on port 8080
echo   %0 -p 8080 -d                # Start on port 8080 in debug mode
echo   %0 -k -p 8082                # Kill existing process and start on port 8082
goto :eof

:start_app
echo ==============================================
echo   REDLINE Flask Web Application Startup
echo ==============================================
echo.

REM Check if web_app.py exists
if not exist "web_app.py" (
    echo [ERROR] web_app.py not found in current directory
    echo [ERROR] Please run this script from the REDLINE project root directory
    pause
    exit /b 1
)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo [ERROR] Please install Python 3 and try again
    pause
    exit /b 1
)

REM Check if Flask is installed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Flask is not installed
    echo [INFO] Installing Flask and dependencies...
    pip install flask flask-socketio flask-compress
    if errorlevel 1 (
        echo [ERROR] Failed to install Flask dependencies
        pause
        exit /b 1
    )
    echo [INFO] Dependencies installed successfully
) else (
    echo [INFO] All Python dependencies are available
)

REM Kill existing process if requested
if "%KILL_EXISTING%"=="true" (
    echo [INFO] Checking for existing processes on port %PORT%...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%PORT%') do (
        echo [WARNING] Killing existing process %%a on port %PORT%
        taskkill /F /PID %%a >nul 2>&1
    )
)

REM Create necessary directories
echo [INFO] Creating necessary directories...
if not exist "data" mkdir data
if not exist "data\uploads" mkdir data\uploads
if not exist "data\converted" mkdir data\converted
if not exist "logs" mkdir logs

REM Set environment variables
set WEB_PORT=%PORT%
set HOST=%HOST%
set DEBUG=%DEBUG%
set FLASK_APP=web_app.py

echo [INFO] Environment variables set:
echo [INFO]   WEB_PORT=%PORT%
echo [INFO]   HOST=%HOST%
echo [INFO]   DEBUG=%DEBUG%
echo [INFO]   FLASK_APP=web_app.py
echo.

REM Start the Flask application
echo [INFO] Starting REDLINE Flask Web Application...
echo [INFO] Access the application at: http://%HOST%:%PORT%
echo [INFO] Press Ctrl+C to stop the application
echo.

python web_app.py

echo.
echo [INFO] REDLINE Flask Web Application stopped
pause
