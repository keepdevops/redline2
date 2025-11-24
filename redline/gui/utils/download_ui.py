#!/usr/bin/env python3
"""
Download UI Helper for DownloadTab
Handles UI creation for the download tab.
"""

import logging
import tkinter as tk
from tkinter import ttk

logger = logging.getLogger(__name__)


class DownloadUIHelper:
    """Helper class for UI creation in DownloadTab."""
    
    def __init__(self, download_tab):
        """Initialize with reference to DownloadTab."""
        self.download_tab = download_tab
        self.logger = logging.getLogger(__name__)
    
    def create_widgets(self):
        """Create the download tab widgets."""
        # Main container
        main_container = ttk.Frame(self.download_tab.frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - API & Download controls with scrollbar
        left_panel_container = ttk.LabelFrame(main_container, text="API & Download Controls", padding=5)
        left_panel_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Create scrollable canvas for left panel
        self.download_tab.left_canvas = tk.Canvas(left_panel_container, highlightthickness=0)
        self.download_tab.left_scrollbar = ttk.Scrollbar(left_panel_container, orient="vertical", command=self.download_tab.left_canvas.yview)
        self.download_tab.scrollable_left_frame = ttk.Frame(self.download_tab.left_canvas)
        
        # Configure scrollable frame
        self.download_tab.scrollable_left_frame.bind(
            "<Configure>",
            self.download_tab._on_left_frame_configure
        )
        
        # Bind mouse wheel to canvas
        self.download_tab.left_canvas.bind("<MouseWheel>", self.download_tab._on_mousewheel)
        self.download_tab.left_canvas.bind("<Button-4>", self.download_tab._on_mousewheel)  # Linux scroll up
        self.download_tab.left_canvas.bind("<Button-5>", self.download_tab._on_mousewheel)  # Linux scroll down
        
        self.download_tab.left_canvas.create_window((0, 0), window=self.download_tab.scrollable_left_frame, anchor="nw", width=400)
        self.download_tab.left_canvas.configure(yscrollcommand=self.download_tab.left_scrollbar.set)
        
        # Pack canvas and scrollbar
        self.download_tab.left_canvas.pack(side="left", fill="both", expand=True)
        self.download_tab.left_scrollbar.pack(side="right", fill="y")
        
        # Right panel - Results display
        right_panel = ttk.LabelFrame(main_container, text="Download Results", padding=5)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Create widgets in the scrollable frame
        self.create_download_controls(self.download_tab.scrollable_left_frame)
        
        # Create results display
        self.create_results_display(right_panel)
    
    def create_download_controls(self, parent):
        """Create download control widgets."""
        # API Data source selection
        source_frame = ttk.LabelFrame(parent, text="API Data Sources", padding=2)
        source_frame.pack(fill=tk.X, pady=(0, 10))
        source_frame.grid_columnconfigure(0, weight=1)
        
        self.download_tab.source_var = tk.StringVar(value="yahoo")
        ttk.Radiobutton(source_frame, text="📊 Yahoo Finance API (Free, Reliable, No Auth)", 
                       variable=self.download_tab.source_var, value="yahoo").grid(row=0, column=0, sticky="ew", pady=1)
        ttk.Radiobutton(source_frame, text="🏢 Stooq.com API (High Quality, Manual Auth)", 
                       variable=self.download_tab.source_var, value="stooq").grid(row=1, column=0, sticky="ew", pady=1)
        ttk.Radiobutton(source_frame, text="🔄 Multi-Source API (Fallback System)", 
                       variable=self.download_tab.source_var, value="multi").grid(row=2, column=0, sticky="ew", pady=1)
        
        # API status info
        ttk.Label(source_frame, text="💡 Yahoo Finance is recommended for most users", 
                 font=("Arial", 8), foreground="blue").grid(row=3, column=0, sticky="ew")
        ttk.Label(source_frame, text="⚠️ Yahoo Finance: 2 second delay between requests (rate limited)", 
                 font=("Arial", 8), foreground="orange").grid(row=4, column=0, sticky="ew")
        ttk.Label(source_frame, text="📊 Bulk downloads use sequential processing to avoid rate limits", 
                 font=("Arial", 8), foreground="green").grid(row=5, column=0, sticky="ew")
        
        # Ticker input
        ticker_frame = ttk.LabelFrame(parent, text="Ticker Symbols", padding=5)
        ticker_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(ticker_frame, text="Enter ticker symbols (comma-separated):").pack(anchor=tk.W)
        self.download_tab.ticker_entry = tk.Text(ticker_frame, height=4, wrap=tk.WORD)
        self.download_tab.ticker_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Quick ticker buttons
        quick_frame = ttk.Frame(ticker_frame)
        quick_frame.pack(fill=tk.X, pady=(5, 0))
        
        quick_tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "AMZN", "META", "NFLX"]
        for i, ticker in enumerate(quick_tickers):
            btn = ttk.Button(quick_frame, text=ticker, width=8,
                           command=lambda t=ticker: self.download_tab.utils_helper.add_ticker(t))
            btn.grid(row=i//4, column=i%4, padx=2, pady=2, sticky='ew')
        
        # Configure grid columns for equal width
        for col in range(4):
            quick_frame.grid_columnconfigure(col, weight=1)
        
        # Date range
        date_frame = ttk.LabelFrame(parent, text="Date Range", padding=5)
        date_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Start date
        start_frame = ttk.Frame(date_frame)
        start_frame.pack(fill=tk.X, pady=2)
        ttk.Label(start_frame, text="Start Date:").pack(side=tk.LEFT)
        self.download_tab.start_date_var = tk.StringVar(value="2020-01-01")
        ttk.Entry(start_frame, textvariable=self.download_tab.start_date_var, width=12).pack(side=tk.RIGHT)
        
        # End date
        end_frame = ttk.Frame(date_frame)
        end_frame.pack(fill=tk.X, pady=2)
        ttk.Label(end_frame, text="End Date:").pack(side=tk.LEFT)
        self.download_tab.end_date_var = tk.StringVar(value="2024-12-31")
        ttk.Entry(end_frame, textvariable=self.download_tab.end_date_var, width=12).pack(side=tk.RIGHT)
        
        # Quick date buttons
        quick_date_frame = ttk.Frame(date_frame)
        quick_date_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(quick_date_frame, text="1Y", 
                  command=lambda: self.download_tab.utils_helper.set_date_range("1y")).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_date_frame, text="2Y", 
                  command=lambda: self.download_tab.utils_helper.set_date_range("2y")).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_date_frame, text="5Y", 
                  command=lambda: self.download_tab.utils_helper.set_date_range("5y")).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_date_frame, text="Max", 
                  command=lambda: self.download_tab.utils_helper.set_date_range("max")).pack(side=tk.LEFT, padx=2)
        
        # Output options
        output_frame = ttk.LabelFrame(parent, text="Output Options", padding=5)
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Output format
        format_frame = ttk.Frame(output_frame)
        format_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(format_frame, text="Output Format:").pack(side=tk.LEFT, padx=(0, 5))
        self.download_tab.output_format_var = tk.StringVar(value='csv')
        format_combo = ttk.Combobox(format_frame, textvariable=self.download_tab.output_format_var, 
                                   values=['csv', 'json', 'parquet', 'duckdb'], 
                                   state='readonly', width=10)
        format_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # Output directory
        ttk.Label(format_frame, text="Output Directory:").pack(side=tk.LEFT, padx=(0, 5))
        output_dir_entry = ttk.Entry(format_frame, textvariable=self.download_tab.output_dir_var, width=20)
        output_dir_entry.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(format_frame, text="Browse", 
                  command=self.download_tab.utils_helper.browse_output_dir).pack(side=tk.LEFT)
        
        # API Key input
        api_key_frame = ttk.Frame(output_frame)
        api_key_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(api_key_frame, text="API Key (if required):").pack(side=tk.LEFT, padx=(0, 5))
        api_key_entry = ttk.Entry(api_key_frame, textvariable=self.download_tab.api_key_var, 
                                 show="*", width=30)
        api_key_entry.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(api_key_frame, text="Clear", 
                  command=lambda: self.download_tab.api_key_var.set("")).pack(side=tk.LEFT)
        
        # Download mode options
        mode_frame = ttk.LabelFrame(parent, text="Download Mode", padding=5)
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Checkbutton(mode_frame, text="Bulk Download Mode (Parallel Processing)", 
                       variable=self.download_tab.bulk_mode_var).pack(anchor=tk.W)
        
        # Download buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.download_tab.download_button = ttk.Button(button_frame, text="Start Download", 
                                        command=self.download_tab.logic_helper.start_download, style="Accent.TButton")
        self.download_tab.download_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.download_tab.stop_button = ttk.Button(button_frame, text="Stop", 
                                    command=self.download_tab.logic_helper.stop_download, state='disabled')
        self.download_tab.stop_button.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame, text="Open Stooq Website", 
                  command=self.download_tab.utils_helper.open_stooq_website).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Open Browser", 
                  command=self.download_tab.utils_helper.open_browser_menu).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame, text="Test API", 
                  command=self.download_tab.utils_helper.test_api_connection).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Clear Results", 
                  command=self.download_tab.logic_helper.clear_results).pack(side=tk.RIGHT)
        
        # Progress bar
        self.download_tab.progress_var = tk.DoubleVar()
        self.download_tab.progress_bar = ttk.Progressbar(parent, variable=self.download_tab.progress_var, maximum=100)
        self.download_tab.progress_bar.pack(fill=tk.X, pady=(10, 0))
        
        self.download_tab.status_label = ttk.Label(parent, text="Ready to download")
        self.download_tab.status_label.pack(anchor=tk.W, pady=(5, 0))
    
    def create_results_display(self, parent):
        """Create results display widgets."""
        # Results treeview
        columns = ("Ticker", "Rows", "Date Range", "Source", "Status", "File")
        self.download_tab.results_tree = ttk.Treeview(parent, columns=columns, show='headings', height=15)
        
        # Configure columns
        for col in columns:
            self.download_tab.results_tree.heading(col, text=col)
            self.download_tab.results_tree.column(col, width=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.download_tab.results_tree.yview)
        h_scrollbar = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.download_tab.results_tree.xview)
        self.download_tab.results_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.download_tab.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Context menu
        self.create_context_menu()
    
    def create_context_menu(self):
        """Create context menu for results tree."""
        self.download_tab.context_menu = tk.Menu(self.download_tab.frame, tearoff=0)
        self.download_tab.context_menu.add_command(label="Open File", command=self.download_tab.file_ops_helper.open_selected_file)
        self.download_tab.context_menu.add_command(label="Load in REDLINE", command=self.download_tab.file_ops_helper.load_selected_data)
        self.download_tab.context_menu.add_separator()
        self.download_tab.context_menu.add_command(label="Delete File", command=self.download_tab.file_ops_helper.delete_selected_file)
        
        self.download_tab.results_tree.bind("<Button-3>", self.download_tab.events_helper.show_context_menu)

