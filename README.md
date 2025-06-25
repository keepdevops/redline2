# REDLINE - Stock Market Data Management Tool

REDLINE is a powerful tool for converting, cleaning, and managing financial market data with a user-friendly graphical interface.

## Quick Start (macOS GUI)

### Prerequisites
1. **XQuartz**: Required for GUI on macOS
   - Download from: https://www.xquartz.org/
   - Or check if installed: `ls /Applications/Utilities/XQuartz.app`

2. **Docker**: Make sure Docker Desktop is running

### Running the GUI
1. **Simple method** (recommended):
   ```bash
   ./run_gui.bash
   ```

2. **Test X11 forwarding first** (if you encounter issues):
   ```bash
   ./test_x11.bash
   ```

3. **Alternative method** (if the simple method fails):
   ```bash
   # Install socat first
   brew install socat
   # Then run
   ./run_gui_socat.bash
   ```

### Troubleshooting
- If you get display errors, see `GUI_TROUBLESHOOTING.md`
- Ensure XQuartz is running and "Allow connections from network clients" is enabled
- The scripts automatically handle X11 forwarding setup

## Command-Line Usage

You can run Redline in different modes using the `--task` argument:

- `gui` — Launches the graphical user interface (default)
- `load` — Loads data files into the DuckDB database
- `convert` — Converts data files between supported formats
- `preprocess` — Preprocesses data for machine learning or reinforcement learning

**Examples:**
```sh
python3 -m data_module --task=gui
python3 -m data_module --task=load
python3 -m data_module --task=convert
python3 -m data_module --task=preprocess
```

The `--task` argument is optional; if omitted, the GUI will launch by default.
