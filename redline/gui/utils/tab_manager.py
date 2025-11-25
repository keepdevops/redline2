#!/usr/bin/env python3
"""
Tab Manager Helper for StockAnalyzerGUI
Handles tab creation and navigation.
"""

import logging
import tkinter as tk
from tkinter import ttk

logger = logging.getLogger(__name__)


class TabManagerHelper:
    """Helper class for tab management in StockAnalyzerGUI."""
    
    def __init__(self, main_window):
        """Initialize with reference to StockAnalyzerGUI."""
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
    
    def create_tabs(self):
        """Create the main tabs."""
        from ..data_tab import DataTab
        from ..analysis_tab import AnalysisTab
        from ..download_tab import DownloadTab
        from ..converter_tab import ConverterTab
        from ..settings_tab import SettingsTab
        
        # Data tab
        self.main_window.data_tab = DataTab(self.main_window.notebook, self.main_window.loader, self.main_window.connector, self.main_window)
        self.main_window.notebook.add(self.main_window.data_tab.frame, text="Data")
        
        # Analysis tab
        self.main_window.analysis_tab = AnalysisTab(self.main_window.notebook, self.main_window.loader, self.main_window.connector, self.main_window)
        self.main_window.notebook.add(self.main_window.analysis_tab.frame, text="Analysis")

        # Download/API tab
        self.main_window.download_tab = DownloadTab(self.main_window.notebook, self.main_window.loader, self.main_window.connector, self.main_window)
        self.main_window.notebook.add(self.main_window.download_tab.frame, text="Download/API")
        
        # Converter tab
        self.main_window.converter_tab = ConverterTab(self.main_window.notebook, self.main_window.loader, self.main_window.connector, self.main_window)
        self.main_window.notebook.add(self.main_window.converter_tab.frame, text="Converter")

        # Settings tab
        self.main_window.settings_tab = SettingsTab(self.main_window.notebook, self.main_window.loader, self.main_window.connector, self.main_window)
        self.main_window.notebook.add(self.main_window.settings_tab.frame, text="Settings")
    
    def next_tab(self):
        """Go to next tab."""
        try:
            current_index = self.main_window.notebook.index(self.main_window.notebook.select())
            next_index = (current_index + 1) % self.main_window.notebook.index("end")
            self.main_window.notebook.select(next_index)
        except Exception as e:
            self.main_window.logger.error(f"Error switching to next tab: {str(e)}")
    
    def previous_tab(self):
        """Go to previous tab."""
        try:
            current_index = self.main_window.notebook.index(self.main_window.notebook.select())
            prev_index = (current_index - 1) % self.main_window.notebook.index("end")
            self.main_window.notebook.select(prev_index)
        except Exception as e:
            self.main_window.logger.error(f"Error switching to previous tab: {str(e)}")
    
    def on_tab_changed(self, event):
        """Handle tab change events."""
        try:
            current_tab = self.main_window.notebook.tab(self.main_window.notebook.select(), "text")
            self.main_window.logger.info(f"🔄 Switched to tab: {current_tab}")
            import traceback
            self.main_window.logger.debug(f"   Tab switch call stack:\n{''.join(traceback.format_stack()[-8:-1])}")
            
            # Update status label
            if hasattr(self.main_window, 'status_label'):
                self.main_window.status_label.config(text=f"Active: {current_tab}")
            
            # Update help button tooltip
            if hasattr(self.main_window, 'help_btn') and hasattr(self.main_window, 'setup_helper'):
                self.main_window.setup_helper.create_tooltip(self.main_window.help_btn, f"Help for {current_tab} tab")
            
            # Update status label
            if hasattr(self.main_window, 'status_label'):
                self.main_window.status_label.config(text=f"Active: {current_tab}")
            
            # Notify the active tab of the change
            if current_tab == "Data" and hasattr(self.main_window, 'data_tab'):
                self.main_window.logger.info(f"📊 Activating Data tab...")
                self.main_window.data_tab.on_tab_activated()
                self.main_window.logger.info(f"✅ Data tab activated")
            elif current_tab == "Analysis" and hasattr(self.main_window, 'analysis_tab'):
                self.main_window.logger.info(f"📈 Activating Analysis tab...")
                self.main_window.analysis_tab.on_tab_activated()
            elif current_tab == "Download/API" and hasattr(self.main_window, 'download_tab'):
                self.main_window.logger.info(f"⬇️ Activating Download tab...")
                self.main_window.download_tab.on_tab_activated()
            elif current_tab == "Converter" and hasattr(self.main_window, 'converter_tab'):
                self.main_window.logger.info(f"🔄 Activating Converter tab...")
                self.main_window.converter_tab.on_tab_activated()
            elif current_tab == "Settings" and hasattr(self.main_window, 'settings_tab'):
                self.main_window.logger.info(f"⚙️ Activating Settings tab...")
                self.main_window.settings_tab.on_tab_activated()
                
        except Exception as e:
            self.main_window.logger.error(f"Error handling tab change: {str(e)}")
    
    def notify_tabs_of_resize(self):
        """Notify all tabs of window resize event."""
        try:
            # Get current tab
            current_tab = self.main_window.notebook.select()
            tab_text = self.main_window.notebook.tab(current_tab, "text")
            
            # Notify the active tab
            if tab_text == "Data" and hasattr(self.main_window, 'data_tab'):
                self.main_window.data_tab.on_window_resize()
            elif tab_text == "Analysis" and hasattr(self.main_window, 'analysis_tab'):
                self.main_window.analysis_tab.on_window_resize()
            elif tab_text == "Download/API" and hasattr(self.main_window, 'download_tab'):
                self.main_window.download_tab.on_window_resize()
            elif tab_text == "Converter" and hasattr(self.main_window, 'converter_tab'):
                self.main_window.converter_tab.on_window_resize()
            elif tab_text == "Settings" and hasattr(self.main_window, 'settings_tab'):
                self.main_window.settings_tab.on_window_resize()
                
        except Exception as e:
            self.main_window.logger.error(f"Error notifying tabs of resize: {str(e)}")

