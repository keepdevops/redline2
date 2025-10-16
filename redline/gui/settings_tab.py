#!/usr/bin/env python3
"""
REDLINE Settings Tab
GUI tab for application settings and configuration.
"""

import logging
import tkinter as tk
from tkinter import ttk, messagebox
import configparser
import os

from ..core.data_loader import DataLoader
from ..database.connector import DatabaseConnector

logger = logging.getLogger(__name__)

class SettingsTab:
    """Settings tab for application configuration."""
    
    def __init__(self, parent, loader: DataLoader, connector: DatabaseConnector, main_window):
        """Initialize settings tab."""
        self.parent = parent
        self.loader = loader
        self.connector = connector
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        
        # Settings variables
        self.settings_vars = {}
        
        # Create widgets
        self.create_widgets()
        self.load_current_settings()
    
    def create_widgets(self):
        """Create the settings tab widgets."""
        # Title
        title_label = ttk.Label(self.frame, text="Settings", font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)
        
        # Create notebook for different setting categories
        self.settings_notebook = ttk.Notebook(self.frame)
        self.settings_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Data settings tab
        self.create_data_settings_tab()
        
        # Display settings tab
        self.create_display_settings_tab()
        
        # Advanced settings tab
        self.create_advanced_settings_tab()
        
        # Buttons frame
        buttons_frame = ttk.Frame(self.frame)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Save button
        ttk.Button(buttons_frame, text="Save Settings", command=self.save_settings).pack(side=tk.LEFT, padx=5)
        
        # Reset button
        ttk.Button(buttons_frame, text="Reset to Defaults", command=self.reset_settings).pack(side=tk.LEFT, padx=5)
        
        # Apply button
        ttk.Button(buttons_frame, text="Apply", command=self.apply_settings).pack(side=tk.RIGHT, padx=5)
    
    def create_data_settings_tab(self):
        """Create data settings tab."""
        data_frame = ttk.Frame(self.settings_notebook)
        self.settings_notebook.add(data_frame, text="Data")
        
        # Database path
        ttk.Label(data_frame, text="Database Path:").pack(anchor=tk.W, padx=10, pady=5)
        self.settings_vars['db_path'] = tk.StringVar()
        db_entry = ttk.Entry(data_frame, textvariable=self.settings_vars['db_path'], width=50)
        db_entry.pack(fill=tk.X, padx=10, pady=5)
        
        # CSV directory
        ttk.Label(data_frame, text="CSV Directory:").pack(anchor=tk.W, padx=10, pady=5)
        self.settings_vars['csv_dir'] = tk.StringVar()
        csv_entry = ttk.Entry(data_frame, textvariable=self.settings_vars['csv_dir'], width=50)
        csv_entry.pack(fill=tk.X, padx=10, pady=5)
        
        # JSON directory
        ttk.Label(data_frame, text="JSON Directory:").pack(anchor=tk.W, padx=10, pady=5)
        self.settings_vars['json_dir'] = tk.StringVar()
        json_entry = ttk.Entry(data_frame, textvariable=self.settings_vars['json_dir'], width=50)
        json_entry.pack(fill=tk.X, padx=10, pady=5)
        
        # Parquet directory
        ttk.Label(data_frame, text="Parquet Directory:").pack(anchor=tk.W, padx=10, pady=5)
        self.settings_vars['parquet_dir'] = tk.StringVar()
        parquet_entry = ttk.Entry(data_frame, textvariable=self.settings_vars['parquet_dir'], width=50)
        parquet_entry.pack(fill=tk.X, padx=10, pady=5)
    
    def create_display_settings_tab(self):
        """Create display settings tab."""
        display_frame = ttk.Frame(self.settings_notebook)
        self.settings_notebook.add(display_frame, text="Display")
        
        # Rows per page
        ttk.Label(display_frame, text="Rows per page:").pack(anchor=tk.W, padx=10, pady=5)
        self.settings_vars['rows_per_page'] = tk.IntVar()
        rows_spinbox = ttk.Spinbox(display_frame, from_=10, to=1000, textvariable=self.settings_vars['rows_per_page'])
        rows_spinbox.pack(anchor=tk.W, padx=10, pady=5)
        
        # Auto-refresh interval
        ttk.Label(display_frame, text="Auto-refresh interval (seconds):").pack(anchor=tk.W, padx=10, pady=5)
        self.settings_vars['auto_refresh'] = tk.IntVar()
        refresh_spinbox = ttk.Spinbox(display_frame, from_=0, to=3600, textvariable=self.settings_vars['auto_refresh'])
        refresh_spinbox.pack(anchor=tk.W, padx=10, pady=5)
        
        # Theme selection
        ttk.Label(display_frame, text="Theme:").pack(anchor=tk.W, padx=10, pady=5)
        self.settings_vars['theme'] = tk.StringVar()
        theme_combo = ttk.Combobox(display_frame, textvariable=self.settings_vars['theme'], 
                                  values=['default', 'clam', 'alt', 'classic', 'vista', 'xpnative'])
        theme_combo.pack(anchor=tk.W, padx=10, pady=5)
        
        # Font size
        ttk.Label(display_frame, text="Font size:").pack(anchor=tk.W, padx=10, pady=5)
        self.settings_vars['font_size'] = tk.IntVar()
        font_spinbox = ttk.Spinbox(display_frame, from_=8, to=24, textvariable=self.settings_vars['font_size'])
        font_spinbox.pack(anchor=tk.W, padx=10, pady=5)
    
    def create_advanced_settings_tab(self):
        """Create advanced settings tab."""
        advanced_frame = ttk.Frame(self.settings_notebook)
        self.settings_notebook.add(advanced_frame, text="Advanced")
        
        # Cache size
        ttk.Label(advanced_frame, text="Cache size:").pack(anchor=tk.W, padx=10, pady=5)
        self.settings_vars['cache_size'] = tk.IntVar()
        cache_spinbox = ttk.Spinbox(advanced_frame, from_=100, to=10000, textvariable=self.settings_vars['cache_size'])
        cache_spinbox.pack(anchor=tk.W, padx=10, pady=5)
        
        # Thread count
        ttk.Label(advanced_frame, text="Thread count:").pack(anchor=tk.W, padx=10, pady=5)
        self.settings_vars['thread_count'] = tk.IntVar()
        thread_spinbox = ttk.Spinbox(advanced_frame, from_=1, to=16, textvariable=self.settings_vars['thread_count'])
        thread_spinbox.pack(anchor=tk.W, padx=10, pady=5)
        
        # Debug mode
        self.settings_vars['debug_mode'] = tk.BooleanVar()
        debug_check = ttk.Checkbutton(advanced_frame, text="Enable debug mode", 
                                     variable=self.settings_vars['debug_mode'])
        debug_check.pack(anchor=tk.W, padx=10, pady=5)
        
        # Performance monitoring
        self.settings_vars['perf_monitoring'] = tk.BooleanVar()
        perf_check = ttk.Checkbutton(advanced_frame, text="Enable performance monitoring", 
                                    variable=self.settings_vars['perf_monitoring'])
        perf_check.pack(anchor=tk.W, padx=10, pady=5)
    
    def load_current_settings(self):
        """Load current settings from config."""
        try:
            # Load from loader's config
            config = self.loader.config
            
            # Set default values
            defaults = {
                'db_path': '/app/redline_data.duckdb',
                'csv_dir': '/app/data',
                'json_dir': '/app/data/json',
                'parquet_dir': '/app/data/parquet',
                'rows_per_page': 100,
                'auto_refresh': 0,
                'theme': 'default',
                'font_size': 10,
                'cache_size': 1000,
                'thread_count': 4,
                'debug_mode': False,
                'perf_monitoring': True
            }
            
            # Load from config or use defaults
            for key, default_value in defaults.items():
                if key in config['Data']:
                    if isinstance(default_value, bool):
                        self.settings_vars[key].set(config['Data'].getboolean(key, default_value))
                    elif isinstance(default_value, int):
                        self.settings_vars[key].set(config['Data'].getint(key, default_value))
                    else:
                        self.settings_vars[key].set(config['Data'].get(key, default_value))
                else:
                    self.settings_vars[key].set(default_value)
                    
        except Exception as e:
            self.logger.error(f"Error loading settings: {str(e)}")
            # Set default values
            for key, var in self.settings_vars.items():
                if key == 'debug_mode' or key == 'perf_monitoring':
                    var.set(False)
                elif key in ['rows_per_page', 'auto_refresh', 'font_size', 'cache_size', 'thread_count']:
                    var.set(100 if key == 'rows_per_page' else 0 if key == 'auto_refresh' else 10 if key == 'font_size' else 1000 if key == 'cache_size' else 4)
                else:
                    var.set('/app/redline_data.duckdb' if key == 'db_path' else '/app/data')
    
    def save_settings(self):
        """Save settings to config file."""
        try:
            config = configparser.ConfigParser()
            config.read('data_config.ini')
            
            if 'Data' not in config:
                config.add_section('Data')
            
            # Save all settings
            for key, var in self.settings_vars.items():
                config.set('Data', key, str(var.get()))
            
            # Write to file
            with open('data_config.ini', 'w') as configfile:
                config.write(configfile)
            
            messagebox.showinfo("Success", "Settings saved successfully!")
            
        except Exception as e:
            self.logger.error(f"Error saving settings: {str(e)}")
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def reset_settings(self):
        """Reset settings to defaults."""
        try:
            result = messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all settings to defaults?")
            if result:
                self.load_current_settings()
                messagebox.showinfo("Success", "Settings reset to defaults!")
                
        except Exception as e:
            self.logger.error(f"Error resetting settings: {str(e)}")
            messagebox.showerror("Error", f"Failed to reset settings: {str(e)}")
    
    def apply_settings(self):
        """Apply current settings without saving."""
        try:
            # Apply settings to the application
            # This would update the loader and connector with new settings
            
            # Update database path
            new_db_path = self.settings_vars['db_path'].get()
            if new_db_path != self.connector.db_path:
                self.connector.db_path = new_db_path
            
            # Apply other settings as needed
            messagebox.showinfo("Success", "Settings applied!")
            
        except Exception as e:
            self.logger.error(f"Error applying settings: {str(e)}")
            messagebox.showerror("Error", f"Failed to apply settings: {str(e)}")
    
    def on_tab_activated(self):
        """Handle tab activation."""
        self.load_current_settings()
    
    def refresh_settings(self):
        """Refresh settings display."""
        self.load_current_settings()
