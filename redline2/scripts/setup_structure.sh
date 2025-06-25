#!/bin/bash
# setup_structure.sh - Auto-create modular directory structure for redline2
# Run from the redline2 directory: bash scripts/setup_structure.sh

set -e

# Create main directories
mkdir -p app/modules
mkdir -p app/gui
mkdir -p app/api
mkdir -p app/plugins
mkdir -p data
mkdir -p tests
mkdir -p config
mkdir -p scripts

# Create __init__.py for Python packages
for d in app app/modules app/gui app/api app/plugins tests; do
  touch "$d/__init__.py"
done

# Create placeholder files
[ -f README.md ] || echo "# REDLINE2 - Enhanced Data Conversion Utility" > README.md
[ -f requirements.txt ] || echo "# See Dockerfile for full requirements" > requirements.txt

# Example main application files
[ -f app/main.py ] || echo "# Entrypoint for REDLINE2" > app/main.py
[ -f app/config.py ] || echo "# Configuration management" > app/config.py
[ -f app/controller.py ] || echo "# Core orchestration logic" > app/controller.py

# Example module files
for m in file_format schema preprocessing ml_integration batch visualization performance documentation plugin_manager; do
  [ -f app/modules/$m.py ] || echo "# $m module" > app/modules/$m.py
done

# Example GUI files
[ -f app/gui/gui_main.py ] || echo "# GUI main" > app/gui/gui_main.py
[ -f app/gui/widgets.py ] || echo "# GUI widgets" > app/gui/widgets.py

# Example API files
[ -f app/api/api_main.py ] || echo "# API main" > app/api/api_main.py

# Example plugin
[ -f app/plugins/example_plugin.py ] || echo "# Example plugin" > app/plugins/example_plugin.py

# Example test files
for t in test_file_format test_schema test_preprocessing; do
  [ -f tests/$t.py ] || echo "# $t unit test" > tests/$t.py
done

# Example config and template files
[ -f config/data_config.ini ] || echo -e "[Data]\ndb_path = /app/redline_data.duckdb\ncsv_dir = /app/data\njson_dir = /app/data/json\nparquet_dir = /app/data/parquet" > config/data_config.ini
[ -f config/redline_template.json ] || echo '{\n  "example": "See documentation for full template"\n}' > config/redline_template.json
[ -f config/example_schema.json ] || echo '{\n  "columns": []\n}' > config/example_schema.json

# Example utility scripts
[ -f scripts/run_docker.sh ] || echo "#!/bin/bash\necho 'Run docker build and run commands here'" > scripts/run_docker.sh
[ -f scripts/setup_dev_env.sh ] || echo "#!/bin/bash\necho 'Setup local dev environment here'" > scripts/setup_dev_env.sh

chmod +x scripts/*.sh

echo "redline2 modular structure created successfully." 