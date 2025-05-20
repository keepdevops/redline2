

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
