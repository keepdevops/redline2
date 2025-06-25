@echo off
REM setup_structure_windows.bat - Auto-create modular directory structure for redline2 (Windows)
REM Run from the redline2 directory: cmd /c scripts\setup_structure_windows.bat

REM Create main directories
mkdir app\modules 2>nul
mkdir app\gui 2>nul
mkdir app\api 2>nul
mkdir app\plugins 2>nul
mkdir data 2>nul
mkdir tests 2>nul
mkdir config 2>nul
mkdir scripts 2>nul

REM Create __init__.py for Python packages
(for %%d in (app app\modules app\gui app\api app\plugins tests) do (
    if not exist %%d\__init__.py echo.>%%d\__init__.py
))

REM Create placeholder files
if not exist README.md echo # REDLINE2 - Enhanced Data Conversion Utility > README.md
if not exist requirements.txt echo # See Dockerfile for full requirements > requirements.txt

REM Example main application files
if not exist app\main.py echo # Entrypoint for REDLINE2 > app\main.py
if not exist app\config.py echo # Configuration management > app\config.py
if not exist app\controller.py echo # Core orchestration logic > app\controller.py

REM Example module files
(for %%m in (file_format schema preprocessing ml_integration batch visualization performance documentation plugin_manager) do (
    if not exist app\modules\%%m.py echo # %%m module > app\modules\%%m.py
))

REM Example GUI files
if not exist app\gui\gui_main.py echo # GUI main > app\gui\gui_main.py
if not exist app\gui\widgets.py echo # GUI widgets > app\gui\widgets.py

REM Example API files
if not exist app\api\api_main.py echo # API main > app\api\api_main.py

REM Example plugin
if not exist app\plugins\example_plugin.py echo # Example plugin > app\plugins\example_plugin.py

REM Example test files
(for %%t in (test_file_format test_schema test_preprocessing) do (
    if not exist tests\%%t.py echo # %%t unit test > tests\%%t.py
))

REM Example config and template files
if not exist config\data_config.ini echo [Data]>config\data_config.ini && echo db_path = /app/redline_data.duckdb>>config\data_config.ini && echo csv_dir = /app/data>>config\data_config.ini && echo json_dir = /app/data/json>>config\data_config.ini && echo parquet_dir = /app/data/parquet>>config\data_config.ini
if not exist config\redline_template.json echo { "example": "See documentation for full template" } > config\redline_template.json
if not exist config\example_schema.json echo { "columns": [] } > config\example_schema.json

REM Example utility scripts
if not exist scripts\run_docker.bat echo @echo off & echo echo Run docker build and run commands here > scripts\run_docker.bat
if not exist scripts\setup_dev_env.bat echo @echo off & echo echo Setup local dev environment here > scripts\setup_dev_env.bat

REM Make scripts executable (not needed on Windows, but for parity)

@echo redline2 modular structure created successfully (Windows). 