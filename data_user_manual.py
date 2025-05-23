import tkinter as tk
from tkinter import ttk

def show_user_manual_popup(parent):
    guide = (
        """
REDLINE DATA CONVERSION UTILITY - USER MANUAL

============================
TABLE OF CONTENTS
============================
1. Introduction
2. Getting Started
3. Data Loader Tab
4. Data View Tab
5. Data Processing Features
6. File Formats & Standards
7. Advanced Features
8. Troubleshooting
9. Best Practices

============================
1. INTRODUCTION
============================
REDLINE is a powerful tool for converting, cleaning, and managing financial market data. It provides a user-friendly graphical interface for:
• Loading and viewing market data files
• Converting between different file formats
• Preprocessing and cleaning data
• Analyzing data quality and statistics
• Managing large datasets efficiently

============================
2. GETTING STARTED
============================
Key Concepts:
• Workspace: The main window with Data Loader and Data View tabs
• File Formats: Supported types (CSV, JSON, DuckDB, etc.)
• Data Processing: Converting, cleaning, and analyzing data
• Data View: Browsing and managing your data files

Basic Workflow:
1. Load data files using the Data Loader tab
2. Preview and verify data content
3. Process or convert data as needed
4. View and analyze results in Data View tab

============================
3. DATA LOADER TAB
============================
File Selection:
• Click 'Browse Files' to select input files
• Use Ctrl/Cmd+Click for multiple selections
• 'Select All' and 'Deselect All' for batch operations
• Selected files appear in the list with their format

Format Selection:
• Input Format: Choose format matching your files
• Output Format: Select desired conversion format
• Supported formats: CSV, TXT, JSON, DuckDB, Parquet, Feather, Keras, TensorFlow

Date Range Filtering:
• Optional: Filter data by date range
• Format: YYYY-MM-DD
• Leave blank to include all dates

Data Balancing:
• Target Records: Set desired records per ticker
• Minimum Records: Specify minimum required
• Auto-values: Leave blank for automatic calculation
  - Target = Median of available records
  - Minimum = Half of target

Actions:
• Preview File: View contents before processing
• Preprocess File: Clean and normalize data
• Merge/Consolidate: Combine multiple files
• Progress Bar: Shows operation status

============================
4. DATA VIEW TAB
============================
File Browser:
• Lists all supported files in data directory
• Shows file format for each entry
• Multiple selection for batch operations
• Hierarchical directory view

Data Display:
• View file contents in table format
• Sort columns by clicking headers
• Pagination controls for large datasets
• Customizable rows per page

Navigation:
• Ticker selection dropdown
• Previous/Next ticker buttons
• Page navigation controls
• Jump to specific page

Data Management:
• View: Display selected file contents
• Remove: Delete files from disk
• Refresh: Update file list and view
• Export: Save data in various formats

Analysis Features:
• Statistics display
• Data quality indicators
• Time series analysis
• Distribution reports

============================
5. DATA PROCESSING FEATURES
============================
Preprocessing:
• Normalization of numeric columns
• Missing value handling
• Date/time standardization
• Data type conversion

Merging/Consolidation:
• Combine multiple files
• Remove duplicates
• Handle missing values
• Standardize formats

Data Quality Checks:
• Timestamp continuity
• Price anomalies
• Volume consistency
• Ticker validation

Statistics Generation:
• Record counts
• Date range coverage
• Value distributions
• Ticker statistics

============================
6. FILE FORMATS & STANDARDS
============================
CSV Files:
• Headers required
• Standard columns: ticker, timestamp, open, high, low, close, vol, openint
• Comma-separated values

TXT Files (Stooq Format):
• Headers: <TICKER>,<DATE>,<TIME>,<OPEN>,<HIGH>,<LOW>,<CLOSE>,<VOL>
• Tab or comma-delimited
• Automatic column mapping

DuckDB Files:
• Efficient database storage
• 'tickers_data' table structure
• Schema: ticker, timestamp, open, high, low, close, vol, openint, format

Other Formats:
• JSON: Records/lines format
• Parquet/Feather: Columnar storage
• Keras (.h5): Model files
• TensorFlow (.npz): NumPy arrays

============================
7. ADVANCED FEATURES
============================
Multiple File Processing:
• Batch file selection
• Parallel processing
• Progress tracking
• Error handling

Data Analysis:
• Statistical summaries
• Time series analysis
• Distribution reports
• Quality metrics

Custom Processing:
• Format conversion
• Data normalization
• Column mapping
• Filter application

Performance Features:
• Efficient data loading
• Memory optimization
• Pagination support
• Background processing

============================
8. TROUBLESHOOTING
============================
Common Issues:
• "No data loaded": Check file format and headers
• "Directory error": Verify file paths
• "Schema mismatch": Check column names/types
• "Conversion error": Verify data compatibility

Error Messages:
• Check redline.log for detailed errors
• Review console output
• Verify file permissions
• Validate data formats

Recovery Steps:
• Refresh file list
• Restart application
• Check log files
• Verify file integrity

Performance Issues:
• Reduce page size
• Use efficient formats
• Close unused files
• Clear temporary data

============================
9. BEST PRACTICES
============================
Data Management:
• Regular backups
• Consistent naming
• Organized directory structure
• Version control

File Operations:
• Preview before processing
• Verify after conversion
• Regular cleanup
• Systematic organization

Performance:
• Use appropriate formats
• Optimize page sizes
• Regular maintenance
• Monitor resource usage

Security:
• Secure file storage
• Regular backups
• Access control
• Data validation

For additional support or questions, please refer to the README or contact technical support.
"""
    )
    popup = tk.Toplevel(parent)
    popup.title("User Manual")
    popup.geometry("800x700")
    
    # Create main frame
    main_frame = ttk.Frame(popup)
    main_frame.pack(fill='both', expand=True, padx=10, pady=10)
    
    # Add text widget with scrollbar
    text = tk.Text(main_frame, wrap='word', padx=10, pady=10)
    scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=text.yview)
    text.configure(yscrollcommand=scrollbar.set)
    
    # Pack the text and scrollbar
    text.pack(side='left', fill='both', expand=True)
    scrollbar.pack(side='right', fill='y')
    
    # Insert the guide text
    text.insert('1.0', guide)
    text.config(state='disabled')
    
    # Configure grid weights
    popup.grid_rowconfigure(0, weight=1)
    popup.grid_columnconfigure(0, weight=1) 