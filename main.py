#!/usr/bin/env python3
"""
REDLINE Main Application Entry Point
Updated to use the new modular library structure.
"""

import tkinter as tk
import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from redline.gui.main_window import StockAnalyzerGUI
from redline.core.data_loader import DataLoader
from redline.database.connector import DatabaseConnector
from redline.utils.logging_config import setup_logging, configure_third_party_logging

def main():
    """Main application entry point."""
    try:
        # Setup logging
        setup_logging(
            log_level="INFO",
            log_file="redline.log",
            console_output=True
        )
        configure_third_party_logging()
        
        # Create the root window
        root = tk.Tk()
        
        # Initialize components with proper configuration
        loader = DataLoader()
        connector = DatabaseConnector()
        
        # Create the main application
        app = StockAnalyzerGUI(root, loader, connector)
        
        # Start the application
        root.mainloop()
        
    except Exception as e:
        print(f"Error starting REDLINE application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 