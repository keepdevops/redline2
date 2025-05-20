import tkinter as tk
from tkinter import ttk

def show_user_manual_popup(parent):
    guide = (
        """
REDLINE DATA CONVERSION UTILITY - USER MANUAL

============================
GENERAL OVERVIEW
============================
REDLINE is a tool for converting, cleaning, and managing stock market and financial data. It works through a simple graphical interface, letting you load, preview, process, and save data in many formats.

============================
KEY TERMS & DEFINITIONS
============================
- **File Format:** The type of file you are working with (e.g., CSV, JSON, DuckDB, Parquet, Keras).
- **Data Loader Tab:** Where you import, preview, preprocess, and merge your data files.
- **Data View Tab:** Where you browse, view, and manage your data files.
- **Preprocess:** Clean and normalize your data (e.g., scale numbers to a standard range).
- **Merge/Consolidate:** Combine multiple files into one, removing duplicates and cleaning missing values.
- **DuckDB:** A database format for storing large datasets efficiently.
- **Keras/TensorFlow:** Formats for saving machine learning models.
- **Multiple File Merge/Consolidation:** The ability to select multiple files to go through the merge and consolidation process by clicking 'Merge/Consolidate Files'. This allows you to process several files together, combining them into a single dataset and cleaning them in one step.

============================
BASIC WORKFLOW
============================
1. **Go to the Data Loader Tab.**
2. **Browse Files:** Click 'Browse Files' and select one or more data files.
3. **Preview File:** Select a file and click 'Preview File' to check its contents.
4. **Choose Formats:** Use the dropdowns to set the input and output formats.
5. **Preprocess or Merge:**
   - To clean a single file, select it and click 'Preprocess File'.
   - To combine files, select multiple and click 'Merge/Consolidate Files'. You have the ability to select multiple files to go through the merge and consolidation process.
6. **Save:** Choose where and how to save your processed data.
7. **Go to the Data View Tab** to see, remove, or refresh your files.

**Tip:** Use the '?' and 'User Manual' buttons at any time for help.

============================
DATA LOADER TAB
============================
This tab is for importing, previewing, preprocessing, and merging data files.

**Step-by-step usage:**
1. **Browse Files:**
   - Click 'Browse Files' to select one or more data files from your system.
   - Supported formats: .csv, .txt, .json, .duckdb, .parquet, .feather, .h5 (Keras), .npz (TensorFlow).
   - Selected files will appear in the list. You can select multiple files for batch operations.
2. **Preview File:**
   - Select a file from the list and click 'Preview File' to view its contents in a popup table.
   - Use this to verify headers, data types, and sample values before processing.
3. **Preprocess File:**
   - Select a file and click 'Preprocess File' to apply normalization (MinMax scaling) to numeric columns.
   - You will be prompted to choose a save format (e.g., json, keras, tensorflow) and a filename.
   - The preprocessed file will be saved in the chosen format and directory.
4. **Input/Output Format:**
   - Use the dropdowns to specify the input format (should match your files) and the desired output format for conversion.
   - If unsure, preview the file to check its structure.
5. **Merge/Consolidate Files:**
   - Select multiple files and click 'Merge/Consolidate Files' to combine them into one dataset. You have the ability to select multiple files to go through the merge and consolidation process.
   - The tool will remove duplicate rows and prompt you to drop rows with missing values.
   - You will be prompted to choose a save location and format for the merged file.
6. **Progress Bar:**
   - Shows progress during batch operations. If an error occurs, check the log or error message.
7. **Help (?):**
   - Click the '?' button for a quick summary of the Data Loader tab's features.
8. **User Manual:**
   - Click 'User Manual' for this comprehensive guide.

**TIPS:**
- Always preview files before processing to avoid format or header issues.
- Use the correct input format to prevent loading errors.
- After merging, the new file will be auto-selected in Data View for inspection.
- For large files, use Parquet or Feather for better performance.

============================
DATA VIEW TAB
============================
This tab is for browsing, viewing, and managing your data files.

**Step-by-step usage:**
1. **Available Data Files:**
   - The left panel lists all supported data files in the 'data' directory and its subdirectories.
   - Supported extensions: .csv, .txt, .json, .duckdb, .parquet, .feather, .h5, .npz
2. **View File:**
   - Select a file and click 'View File' to display its contents in a scrollable table (up to 1000 rows).
   - For Keras model files (.h5), a summary of the model architecture will be shown.
3. **Remove File:**
   - Select one or more files and click 'Remove File' to delete them from disk. You will be prompted for confirmation.
   - Deleted files cannot be recovered. Use with caution.
4. **Refresh Data:**
   - Click 'Refresh Data' to update the file list and data table after adding or removing files.
5. **Help (?):**
   - Click the '?' button for a quick summary of the Data View tab's features.
6. **User Manual:**
   - Click 'User Manual' (top right) for this comprehensive guide.

**TIPS:**
- Use Refresh after adding or removing files to update the view.
- You can view Keras model summaries directly in the GUI.
- For large files, only the first 1000 rows are shown for performance.

============================
SUPPORTED FILE FORMATS
============================
- **CSV:** Standard comma-separated values. Must have headers. Example: ticker,timestamp,open,high,low,close,vol,openint
- **TXT:** Tab- or comma-delimited. Must have headers: <TICKER>,<PER>,<DATE>,<TIME>,<OPEN>,<HIGH>,<LOW>,<CLOSE>,<VOL>,<OPENINT> (case-insensitive, angle brackets optional). The loader will map and standardize columns automatically.
- **JSON:** Records/lines format preferred. Each line is a JSON object.
- **DuckDB:** Reads from the 'tickers_data' table by default. If the file is empty or missing the table, an error will be shown.
- **Parquet/Feather:** Efficient columnar formats for large datasets.
- **Keras (.h5):** Model files can be loaded and summarized.
- **TensorFlow (.npz):** Saved NumPy arrays.
- **Polars:** Parquet format preferred for compatibility.

**File Naming and Structure:**
- Use descriptive filenames for easy identification.
- Ensure all required columns are present: ticker, timestamp, open, high, low, close, vol, openint.
- The loader will attempt to fill missing columns with None, but missing critical columns may cause errors.

============================
PREPROCESSING & MERGING
============================
- **Preprocessing:**
   - Applies MinMax normalization to all numeric columns (open, high, low, close, vol, openint).
   - Prompts for output format and filename.
   - Saves the preprocessed file in the selected format.
- **Merging:**
   - Combines multiple files into one DataFrame.
   - Removes duplicate rows automatically.
   - Prompts to drop rows with missing values (recommended for clean datasets).
   - Output can be saved in any supported format.

**Advanced:**
- You can merge files of different formats as long as the columns match.
- The merged file will be auto-selected in Data View for review.

============================
DATABASE (DUCKDB)
============================
- **Purpose:**
   - Store and manage large datasets efficiently.
   - All data is saved to the 'tickers_data' table by default.
- **Schema:**
   - ticker (str), timestamp (str), open (float), high (float), low (float), close (float), vol (float), openint (float), format (str)
- **Usage:**
   - When saving to DuckDB, the table is dropped and recreated to avoid schema mismatches.
   - If you encounter schema errors, delete the DuckDB file and re-run the operation.
- **Tips:**
   - Use DuckDB for large or consolidated datasets.
   - You can open DuckDB files with external tools for advanced analysis.

============================
ERROR HANDLING & TROUBLESHOOTING
============================
- **Common Errors:**
   - "No data loaded from file(s)": Check file format, headers, and input format selection. Preview the file to diagnose.
   - "Is a directory" or "No such file or directory": Ensure the DuckDB path is a file, not a directory. Check your config.
   - "Binder Error: ... has N columns but M values were supplied": Schema mismatch; try deleting/recreating the DuckDB file.
   - "Conversion Error: Unimplemented type for cast (DOUBLE -> VARCHAR[])": Old DuckDB schema; delete the file and retry.
   - "Failed to load Keras model": The file may be corrupted or not a valid Keras model.
   - For other errors, check the redline.log file for details.
- **Diagnostics:**
   - The application prints column dtypes and sample values before saving to DuckDB. Use these diagnostics to spot issues.
   - All errors are logged to redline.log for further analysis.
- **General Tips:**
   - Always check the log file if you encounter unexpected behavior.
   - If a file fails to load, try opening it in a text editor to check for formatting issues.

============================
ADVANCED USAGE
============================
- **Multiple File Merge/Consolidation:** You have the ability to select multiple files to go through the merge and consolidation process by clicking 'Merge/Consolidate Files'. This allows you to process several files together, combining them into a single dataset and cleaning them in one step.
- **DataFrame Conversion:**
   - Convert between pandas, polars, and pyarrow DataFrames as needed.
- **Model Files:**
   - Keras (.h5) and TensorFlow (.npz) model files can be loaded and summarized in the GUI.
- **Command-Line Interface:**
   - You can run Redline from the command line with the following tasks:
     - `gui` — Launches the graphical user interface (default)
     - `load` — Loads data files into the DuckDB database
     - `convert` — Converts data files between supported formats
     - `preprocess` — Preprocesses data for machine learning or reinforcement learning
   - **Usage Example:**
     ```
     python3 -m data_module --task=gui
     python3 -m data_module --task=load
     python3 -m data_module --task=convert
     python3 -m data_module --task=preprocess
     ```
   - The `--task` argument is optional; if omitted, the GUI will launch by default.
- **Custom Data Directories:**
   - You can configure data directories in data_config.ini for advanced workflows.

============================
TIPS & BEST PRACTICES
============================
- Always back up your data before batch operations or deletions.
- Use Preview and Data View to verify data integrity after each operation.
- For large files, prefer Parquet or Feather formats for performance and efficiency.
- Use the User Manual and Help buttons for guidance at any time.
- Keep your DuckDB file in a safe location and back it up regularly.
- If you encounter persistent issues, try resetting the application or consulting the README.

For more help, see the README or contact support.
"""
    )
    popup = tk.Toplevel(parent)
    popup.title("User Manual")
    popup.geometry("800x700")
    text = tk.Text(popup, wrap='word')
    text.insert('1.0', guide)
    text.config(state='disabled')
    text.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
    scrollbar = ttk.Scrollbar(popup, command=text.yview)
    text['yscrollcommand'] = scrollbar.set
    scrollbar.grid(row=0, column=1, sticky='ns')
    popup.grid_rowconfigure(0, weight=1)
    popup.grid_columnconfigure(0, weight=1) 