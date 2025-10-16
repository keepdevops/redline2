#!/usr/bin/env python3
"""
REDLINE Analysis Tab
GUI tab for data analysis and visualization operations.
"""

import logging
import tkinter as tk
from tkinter import ttk
from typing import Optional

from ..core.data_loader import DataLoader
from ..database.connector import DatabaseConnector

logger = logging.getLogger(__name__)

class AnalysisTab:
    """Analysis tab for data analysis and visualization."""
    
    def __init__(self, parent, loader: DataLoader, connector: DatabaseConnector, main_window):
        """Initialize analysis tab."""
        self.parent = parent
        self.loader = loader
        self.connector = connector
        self.main_window = main_window
        self.logger = logging.getLogger(__name__)
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        
        # Create widgets
        self.create_widgets()
    
    def create_widgets(self):
        """Create the analysis tab widgets."""
        # Title
        title_label = ttk.Label(self.frame, text="Data Analysis", font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)
        
        # Analysis controls frame
        controls_frame = ttk.LabelFrame(self.frame, text="Analysis Options")
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Statistical analysis
        ttk.Button(controls_frame, text="Statistical Analysis", command=self.run_statistical_analysis).pack(pady=5)
        
        # Correlation analysis
        ttk.Button(controls_frame, text="Correlation Analysis", command=self.run_correlation_analysis).pack(pady=5)
        
        # Price trends
        ttk.Button(controls_frame, text="Price Trends", command=self.run_price_trends).pack(pady=5)
        
        # Volume analysis
        ttk.Button(controls_frame, text="Volume Analysis", command=self.run_volume_analysis).pack(pady=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(self.frame, text="Analysis Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Results text area
        self.results_text = tk.Text(results_frame, wrap=tk.WORD, height=15)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar for results
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.configure(yscrollcommand=results_scrollbar.set)
    
    def run_statistical_analysis(self):
        """Run statistical analysis on current data."""
        try:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "Running statistical analysis...\n")
            
            # Get current data from main window
            current_data = self.main_window.data_tab.current_data if hasattr(self.main_window, 'data_tab') else None
            
            if current_data is None or current_data.empty:
                self.results_text.insert(tk.END, "No data available for analysis.\n")
                return
            
            # Basic statistics
            stats = current_data.describe()
            self.results_text.insert(tk.END, "Statistical Summary:\n")
            self.results_text.insert(tk.END, str(stats) + "\n\n")
            
            # Additional analysis
            if 'close' in current_data.columns:
                close_stats = {
                    'Mean': current_data['close'].mean(),
                    'Median': current_data['close'].median(),
                    'Std Dev': current_data['close'].std(),
                    'Min': current_data['close'].min(),
                    'Max': current_data['close'].max()
                }
                
                self.results_text.insert(tk.END, "Close Price Statistics:\n")
                for key, value in close_stats.items():
                    self.results_text.insert(tk.END, f"{key}: {value:.2f}\n")
            
            self.results_text.insert(tk.END, "\nStatistical analysis completed.\n")
            
        except Exception as e:
            self.logger.error(f"Error in statistical analysis: {str(e)}")
            self.results_text.insert(tk.END, f"Error: {str(e)}\n")
    
    def run_correlation_analysis(self):
        """Run correlation analysis."""
        try:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "Running correlation analysis...\n")
            
            current_data = self.main_window.data_tab.current_data if hasattr(self.main_window, 'data_tab') else None
            
            if current_data is None or current_data.empty:
                self.results_text.insert(tk.END, "No data available for analysis.\n")
                return
            
            # Select numeric columns for correlation
            numeric_cols = current_data.select_dtypes(include=['number']).columns
            
            if len(numeric_cols) < 2:
                self.results_text.insert(tk.END, "Not enough numeric columns for correlation analysis.\n")
                return
            
            # Calculate correlation matrix
            correlation_matrix = current_data[numeric_cols].corr()
            
            self.results_text.insert(tk.END, "Correlation Matrix:\n")
            self.results_text.insert(tk.END, str(correlation_matrix) + "\n\n")
            
            self.results_text.insert(tk.END, "Correlation analysis completed.\n")
            
        except Exception as e:
            self.logger.error(f"Error in correlation analysis: {str(e)}")
            self.results_text.insert(tk.END, f"Error: {str(e)}\n")
    
    def run_price_trends(self):
        """Run price trend analysis."""
        try:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "Running price trend analysis...\n")
            
            current_data = self.main_window.data_tab.current_data if hasattr(self.main_window, 'data_tab') else None
            
            if current_data is None or current_data.empty:
                self.results_text.insert(tk.END, "No data available for analysis.\n")
                return
            
            if 'close' not in current_data.columns or 'timestamp' not in current_data.columns:
                self.results_text.insert(tk.END, "Required columns (close, timestamp) not found.\n")
                return
            
            # Sort by timestamp
            sorted_data = current_data.sort_values('timestamp')
            
            # Calculate price changes
            price_changes = sorted_data['close'].pct_change().dropna()
            
            self.results_text.insert(tk.END, "Price Trend Analysis:\n")
            self.results_text.insert(tk.END, f"Average daily change: {price_changes.mean():.4f}\n")
            self.results_text.insert(tk.END, f"Price volatility (std): {price_changes.std():.4f}\n")
            self.results_text.insert(tk.END, f"Largest gain: {price_changes.max():.4f}\n")
            self.results_text.insert(tk.END, f"Largest loss: {price_changes.min():.4f}\n")
            
            # Trend direction
            positive_days = (price_changes > 0).sum()
            negative_days = (price_changes < 0).sum()
            
            self.results_text.insert(tk.END, f"Positive days: {positive_days}\n")
            self.results_text.insert(tk.END, f"Negative days: {negative_days}\n")
            
            self.results_text.insert(tk.END, "\nPrice trend analysis completed.\n")
            
        except Exception as e:
            self.logger.error(f"Error in price trend analysis: {str(e)}")
            self.results_text.insert(tk.END, f"Error: {str(e)}\n")
    
    def run_volume_analysis(self):
        """Run volume analysis."""
        try:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "Running volume analysis...\n")
            
            current_data = self.main_window.data_tab.current_data if hasattr(self.main_window, 'data_tab') else None
            
            if current_data is None or current_data.empty:
                self.results_text.insert(tk.END, "No data available for analysis.\n")
                return
            
            if 'vol' not in current_data.columns:
                self.results_text.insert(tk.END, "Volume column not found.\n")
                return
            
            # Volume statistics
            volume_stats = {
                'Average Volume': current_data['vol'].mean(),
                'Median Volume': current_data['vol'].median(),
                'Max Volume': current_data['vol'].max(),
                'Min Volume': current_data['vol'].min(),
                'Volume Std Dev': current_data['vol'].std()
            }
            
            self.results_text.insert(tk.END, "Volume Analysis:\n")
            for key, value in volume_stats.items():
                self.results_text.insert(tk.END, f"{key}: {value:,.0f}\n")
            
            # High volume days
            avg_volume = current_data['vol'].mean()
            high_volume_days = (current_data['vol'] > avg_volume * 2).sum()
            
            self.results_text.insert(tk.END, f"\nHigh volume days (>2x average): {high_volume_days}\n")
            
            self.results_text.insert(tk.END, "\nVolume analysis completed.\n")
            
        except Exception as e:
            self.logger.error(f"Error in volume analysis: {str(e)}")
            self.results_text.insert(tk.END, f"Error: {str(e)}\n")
    
    def on_tab_activated(self):
        """Handle tab activation."""
        pass
    
    def refresh_data(self):
        """Refresh analysis data."""
        pass
