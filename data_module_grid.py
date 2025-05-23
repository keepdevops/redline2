import tkinter as tk
from tkinter import ttk
import pandas as pd

class StockAnalyzerGUI:
    def __init__(self, root, loader, connector):
        self.root = root
        self.loader = loader
        self.connector = connector
        
        # Configure root grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Setup notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        
        # Create tabs
        self.setup_tabs()
    
    def setup_tabs(self):
        # Data Loader Tab
        loader_frame = ttk.Frame(self.notebook)
        self.notebook.add(loader_frame, text='Data Loader')
        
        # Configure loader frame grid
        loader_frame.grid_rowconfigure(1, weight=1)  # File list gets extra space
        loader_frame.grid_columnconfigure(0, weight=1)
        
        # File selection group
        file_group = ttk.LabelFrame(loader_frame, text="File Selection")
        file_group.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        file_group.grid_rowconfigure(1, weight=1)
        file_group.grid_columnconfigure(0, weight=1)
        
        # Button frame
        button_frame = ttk.Frame(file_group)
        button_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        
        # Buttons
        ttk.Button(button_frame, text="Browse Files", 
                  command=self.browse_files).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Select All", 
                  command=self.select_all_files).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Deselect All", 
                  command=self.deselect_all_files).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Analyze Selected", 
                  command=self.analyze_selected_files).grid(row=0, column=3, padx=5)
        
        # Listbox with scrollbars
        listbox_frame = ttk.Frame(file_group)
        listbox_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        listbox_frame.grid_rowconfigure(0, weight=1)
        listbox_frame.grid_columnconfigure(0, weight=1)
        
        self.input_listbox = tk.Listbox(listbox_frame, selectmode='multiple')
        scrollbar_y = ttk.Scrollbar(listbox_frame, orient='vertical', command=self.input_listbox.yview)
        scrollbar_x = ttk.Scrollbar(listbox_frame, orient='horizontal', command=self.input_listbox.xview)
        
        self.input_listbox.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        
        self.input_listbox.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Selection info
        self.selection_info = ttk.Label(file_group, text="")
        self.selection_info.grid(row=2, column=0, sticky='ew', padx=5, pady=5)
        
        # Format controls group
        format_group = ttk.LabelFrame(loader_frame, text="Format Settings")
        format_group.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
        format_group.grid_columnconfigure(0, weight=1)
        
        # Input format frame
        input_format_frame = ttk.Frame(format_group)
        input_format_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        input_format_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(input_format_frame, text="Input Format:").grid(row=0, column=0, sticky='w')
        self.input_format = ttk.Combobox(input_format_frame, 
                                       values=['csv', 'json', 'duckdb', 'parquet', 'feather', 'keras'])
        self.input_format.grid(row=0, column=1, sticky='ew', padx=5)
        
        # Output format frame
        output_format_frame = ttk.Frame(format_group)
        output_format_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
        output_format_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(output_format_frame, text="Output Format:").grid(row=0, column=0, sticky='w')
        self.output_format = ttk.Combobox(output_format_frame,
                                        values=['csv', 'json', 'duckdb', 'parquet', 'feather', 'keras'])
        self.output_format.grid(row=0, column=1, sticky='ew', padx=5)
        
        # Date range frame
        date_frame = ttk.LabelFrame(format_group, text="Date Range")
        date_frame.grid(row=2, column=0, sticky='ew', padx=5, pady=5)
        date_frame.grid_columnconfigure(1, weight=1)
        
        # Start date
        start_date_frame = ttk.Frame(date_frame)
        start_date_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        start_date_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(start_date_frame, text="Start Date (YYYY-MM-DD):").grid(row=0, column=0, sticky='w')
        self.start_date_entry = ttk.Entry(start_date_frame)
        self.start_date_entry.grid(row=0, column=1, sticky='ew', padx=5)
        
        # End date
        end_date_frame = ttk.Frame(date_frame)
        end_date_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
        end_date_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(end_date_frame, text="End Date (YYYY-MM-DD):").grid(row=0, column=0, sticky='w')
        self.end_date_entry = ttk.Entry(end_date_frame)
        self.end_date_entry.grid(row=0, column=1, sticky='ew', padx=5)
        
        # Balance frame
        balance_frame = ttk.LabelFrame(format_group, text="Data Balance")
        balance_frame.grid(row=3, column=0, sticky='ew', padx=5, pady=5)
        balance_frame.grid_columnconfigure(1, weight=1)
        
        # Target records
        target_frame = ttk.Frame(balance_frame)
        target_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        target_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(target_frame, text="Target Records per Ticker:").grid(row=0, column=0, sticky='w')
        self.target_records_entry = ttk.Entry(target_frame)
        self.target_records_entry.grid(row=0, column=1, sticky='ew', padx=5)
        
        # Minimum records
        min_frame = ttk.Frame(balance_frame)
        min_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
        min_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(min_frame, text="Minimum Records Required:").grid(row=0, column=0, sticky='w')
        self.min_records_entry = ttk.Entry(min_frame)
        self.min_records_entry.grid(row=0, column=1, sticky='ew', padx=5)
        
        # Help text
        help_text = "Leave blank to use automatic values:\n" \
                   "- Target: Median of available records\n" \
                   "- Minimum: Half of target"
        help_label = ttk.Label(balance_frame, text=help_text, wraplength=400)
        help_label.grid(row=2, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        
        # Action buttons frame
        action_frame = ttk.Frame(loader_frame)
        action_frame.grid(row=2, column=0, sticky='ew', padx=5, pady=10)
        action_frame.grid_columnconfigure(0, weight=1)
        
        # Action buttons
        ttk.Button(action_frame, text="Preview Selected", 
                  command=self.preview_selected_loader_file).grid(row=0, column=0, padx=5)
        ttk.Button(action_frame, text="Preprocess Selected", 
                  command=self.preprocess_selected_loader_file).grid(row=0, column=1, padx=5)
        ttk.Button(action_frame, text="Load and Convert", 
                  command=self.load_and_convert).grid(row=0, column=2, padx=5)
        ttk.Button(action_frame, text="Show Manual", 
                  command=self.show_loader_manual).grid(row=0, column=3, padx=5)
        ttk.Button(action_frame, text="User Manual", 
                  command=lambda: show_user_manual_popup(self.root)).grid(row=0, column=4, padx=5)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(loader_frame, mode='indeterminate')
        self.progress_bar.grid(row=3, column=0, sticky='ew', padx=5, pady=10)
        self.progress_bar.grid_remove()  # Hide initially
        
        # Data View Tab
        view_frame = ttk.Frame(self.notebook)
        self.notebook.add(view_frame, text='Data View')
        
        # Configure view frame grid
        view_frame.grid_rowconfigure(1, weight=1)  # Tree view gets extra space
        view_frame.grid_columnconfigure(0, weight=1)
        
        # Ticker navigation frame
        ticker_nav_frame = ttk.Frame(view_frame)
        ticker_nav_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        ticker_nav_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(ticker_nav_frame, text="Current Ticker:").grid(row=0, column=0, padx=5)
        self.ticker_combo = ttk.Combobox(ticker_nav_frame, state='readonly')
        self.ticker_combo.grid(row=0, column=1, sticky='ew', padx=5)
        
        ttk.Button(ticker_nav_frame, text="<", 
                  command=self.previous_ticker).grid(row=0, column=2, padx=5)
        ttk.Button(ticker_nav_frame, text=">", 
                  command=self.next_ticker).grid(row=0, column=3, padx=5)
        
        # Tree view frame
        tree_frame = ttk.Frame(view_frame)
        tree_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        self.data_tree = ttk.Treeview(tree_frame)
        scrollbar_y = ttk.Scrollbar(tree_frame, orient='vertical', command=self.data_tree.yview)
        scrollbar_x = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.data_tree.xview)
        
        self.data_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        
        self.data_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Control frame
        control_frame = ttk.Frame(view_frame)
        control_frame.grid(row=2, column=0, sticky='ew', padx=5, pady=5)
        control_frame.grid_columnconfigure(1, weight=1)  # Center column gets extra space
        
        # Left controls
        left_controls = ttk.Frame(control_frame)
        left_controls.grid(row=0, column=0, sticky='w')
        
        # Page size frame
        page_size_frame = ttk.Frame(left_controls)
        page_size_frame.grid(row=0, column=0, padx=5)
        
        ttk.Label(page_size_frame, text="Rows per page:").grid(row=0, column=0)
        page_size_combo = ttk.Combobox(page_size_frame, values=['10', '25', '50', '100'], width=5)
        page_size_combo.grid(row=0, column=1, padx=2)
        page_size_combo.set('25')
        
        self.custom_page_size = ttk.Entry(page_size_frame, width=5)
        self.custom_page_size.grid(row=0, column=2, padx=2)
        
        ttk.Button(page_size_frame, text="Apply", 
                  command=self.apply_custom_page_size).grid(row=0, column=3, padx=2)
        
        # Navigation frame
        nav_frame = ttk.Frame(control_frame)
        nav_frame.grid(row=0, column=1, sticky='ew')
        nav_frame.grid_columnconfigure(4, weight=1)  # Center the navigation controls
        
        ttk.Button(nav_frame, text="<<", 
                  command=lambda: self.change_page(1)).grid(row=0, column=0, padx=2)
        ttk.Button(nav_frame, text="<", 
                  command=lambda: self.change_page(max(1, self.current_page - 1))).grid(row=0, column=1, padx=2)
        
        jump_entry = ttk.Entry(nav_frame, width=5)
        jump_entry.grid(row=0, column=2, padx=2)
        ttk.Button(nav_frame, text="Go", 
                  command=self.jump_to_page).grid(row=0, column=3, padx=2)
        
        self.page_label = ttk.Label(nav_frame, text="Page 1 of 1")
        self.page_label.grid(row=0, column=4, padx=10)
        
        ttk.Button(nav_frame, text=">", 
                  command=lambda: self.change_page(self.current_page + 1)).grid(row=0, column=5, padx=2)
        ttk.Button(nav_frame, text=">>", 
                  command=lambda: self.change_page(self.total_pages)).grid(row=0, column=6, padx=2)
        
        # Right controls
        right_controls = ttk.Frame(control_frame)
        right_controls.grid(row=0, column=2, sticky='e')
        
        # Export frame
        export_frame = ttk.Frame(right_controls)
        export_frame.grid(row=0, column=0, padx=5)
        
        ttk.Button(export_frame, text="Export Page", 
                  command=lambda: self.export_data(current_page_only=True)).grid(row=0, column=0, padx=2)
        ttk.Button(export_frame, text="Export All", 
                  command=lambda: self.export_data(current_page_only=False)).grid(row=0, column=1, padx=2)

    def show_dataframe_popup(self, df):
        popup = tk.Toplevel(self.root)
        popup.title("Data Preview")
        
        # Configure popup grid
        popup.grid_rowconfigure(0, weight=1)
        popup.grid_columnconfigure(0, weight=1)
        
        # Create frame for text and scrollbar
        frame = ttk.Frame(popup)
        frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Text widget with scrollbars
        text = tk.Text(frame, wrap=tk.NONE)
        scrollbar_y = ttk.Scrollbar(frame, orient='vertical', command=text.yview)
        scrollbar_x = ttk.Scrollbar(frame, orient='horizontal', command=text.xview)
        
        text.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        
        text.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Insert DataFrame content
        text.insert('1.0', df.to_string())
        text.configure(state='disabled')

    def show_progress(self):
        """Show the progress bar"""
        self.run_in_main_thread(lambda: self.progress_bar.grid())

    def hide_progress(self):
        """Hide the progress bar"""
        self.run_in_main_thread(lambda: self.progress_bar.grid_remove())

    def run_in_main_thread(self, func):
        """Run a function in the main thread"""
        if self.root:
            self.root.after(0, func) 