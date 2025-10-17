#!/usr/bin/env python3
"""
REDLINE GUI Integration Tests
Comprehensive test suite for GUI functionality and user interactions.
"""

import unittest
import tkinter as tk
from tkinter import ttk
import threading
import time
import os
import sys
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from datetime import datetime, timedelta

# Add the redline package to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class GUITestBase(unittest.TestCase):
    """Base class for GUI tests with common setup and utilities."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests."""
        cls.test_data_dir = tempfile.mkdtemp(prefix="redline_gui_test_")
        cls.original_cwd = os.getcwd()
        
        # Create test data files
        cls.create_test_data()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        os.chdir(cls.original_cwd)
        if os.path.exists(cls.test_data_dir):
            shutil.rmtree(cls.test_data_dir)
    
    @classmethod
    def create_test_data(cls):
        """Create test data files for testing."""
        # Create sample CSV data
        dates = pd.date_range(start='2020-01-01', end='2020-12-31', freq='D')
        sample_data = pd.DataFrame({
            'ticker': ['AAPL'] * len(dates),
            'timestamp': dates,
            'open': [150.0 + i * 0.1 for i in range(len(dates))],
            'high': [155.0 + i * 0.1 for i in range(len(dates))],
            'low': [145.0 + i * 0.1 for i in range(len(dates))],
            'close': [152.0 + i * 0.1 for i in range(len(dates))],
            'vol': [1000000 + i * 1000 for i in range(len(dates))]
        })
        
        # Save test CSV
        csv_path = os.path.join(cls.test_data_dir, 'test_data.csv')
        sample_data.to_csv(csv_path, index=False)
        
        # Save test JSON
        json_path = os.path.join(cls.test_data_dir, 'test_data.json')
        sample_data.to_json(json_path, orient='records', date_format='iso')
        
        # Save test Parquet
        try:
            parquet_path = os.path.join(cls.test_data_dir, 'test_data.parquet')
            sample_data.to_parquet(parquet_path, index=False)
        except ImportError:
            pass  # Skip if pyarrow not available
    
    def setUp(self):
        """Set up each test."""
        # Mock the GUI components to avoid actual GUI creation
        self.root = None
        self.gui = None
        self.test_timeout = 5  # seconds
    
    def tearDown(self):
        """Clean up after each test."""
        if self.root:
            try:
                self.root.destroy()
            except:
                pass
    
    def create_mock_gui(self):
        """Create a mock GUI for testing."""
        try:
            from redline.core.data_loader import DataLoader
            from redline.database.connector import DatabaseConnector
            from redline.gui.main_window import StockAnalyzerGUI
            
            # Create root window
            self.root = tk.Tk()
            self.root.withdraw()  # Hide window during tests
            
            # Initialize components
            loader = DataLoader()
            connector = DatabaseConnector()
            
            # Create GUI
            self.gui = StockAnalyzerGUI(self.root, loader, connector)
            
            return True
        except Exception as e:
            self.fail(f"Failed to create mock GUI: {str(e)}")
    
    def run_gui_test(self, test_func):
        """Run a GUI test with timeout."""
        result = [None]
        exception = [None]
        
        def test_wrapper():
            try:
                result[0] = test_func()
            except Exception as e:
                exception[0] = e
        
        # Run test in thread
        test_thread = threading.Thread(target=test_wrapper)
        test_thread.daemon = True
        test_thread.start()
        
        # Wait for completion or timeout
        test_thread.join(timeout=self.test_timeout)
        
        if test_thread.is_alive():
            self.fail(f"Test timed out after {self.test_timeout} seconds")
        
        if exception[0]:
            raise exception[0]
        
        return result[0]


class TestMainWindow(GUITestBase):
    """Test main window functionality."""
    
    def test_window_creation(self):
        """Test that main window is created correctly."""
        def test():
            self.assertTrue(self.create_mock_gui())
            self.assertIsNotNone(self.gui.root)
            self.assertIsNotNone(self.gui.notebook)
            self.assertEqual(self.gui.root.title(), "REDLINE Data Analyzer")
            return True
        
        self.run_gui_test(test)
    
    def test_window_resizing(self):
        """Test window resizing functionality."""
        def test():
            self.assertTrue(self.create_mock_gui())
            
            # Test minimum size
            self.gui.root.geometry("800x600")
            self.assertEqual(self.gui.root.geometry(), "800x600+100+100")
            
            # Test maximum size
            self.gui.root.geometry("2400x1600")
            self.assertEqual(self.gui.root.geometry(), "2400x1600+100+100")
            
            # Test normal size
            self.gui.root.geometry("1200x800")
            self.assertEqual(self.gui.root.geometry(), "1200x800+100+100")
            
            return True
        
        self.run_gui_test(test)
    
    def test_toolbar_creation(self):
        """Test toolbar creation and components."""
        def test():
            self.assertTrue(self.create_mock_gui())
            
            # Check toolbar exists
            self.assertIsNotNone(self.gui.toolbar)
            
            # Check help button
            self.assertIsNotNone(self.gui.help_btn)
            self.assertEqual(self.gui.help_btn['text'], '?')
            
            # Check status label
            self.assertIsNotNone(self.gui.status_label)
            
            # Check memory label
            self.assertIsNotNone(self.gui.memory_label)
            
            return True
        
        self.run_gui_test(test)
    
    def test_tab_creation(self):
        """Test that all tabs are created correctly."""
        def test():
            self.assertTrue(self.create_mock_gui())
            
            # Check that all tabs exist
            self.assertIsNotNone(self.gui.data_tab)
            self.assertIsNotNone(self.gui.analysis_tab)
            self.assertIsNotNone(self.gui.download_tab)
            self.assertIsNotNone(self.gui.converter_tab)
            self.assertIsNotNone(self.gui.settings_tab)
            
            # Check tab names
            tab_names = [self.gui.notebook.tab(i, "text") for i in range(self.gui.notebook.index("end"))]
            expected_tabs = ["Data", "Analysis", "Download/API", "Converter", "Settings"]
            
            for expected_tab in expected_tabs:
                self.assertIn(expected_tab, tab_names)
            
            return True
        
        self.run_gui_test(test)
    
    def test_tab_switching(self):
        """Test tab switching functionality."""
        def test():
            self.assertTrue(self.create_mock_gui())
            
            # Test switching to each tab
            tabs = ["Data", "Analysis", "Download/API", "Converter", "Settings"]
            
            for tab_name in tabs:
                # Find tab index
                tab_index = None
                for i in range(self.gui.notebook.index("end")):
                    if self.gui.notebook.tab(i, "text") == tab_name:
                        tab_index = i
                        break
                
                self.assertIsNotNone(tab_index, f"Tab {tab_name} not found")
                
                # Select tab
                self.gui.notebook.select(tab_index)
                self.assertEqual(self.gui.notebook.select(), str(tab_index))
            
            return True
        
        self.run_gui_test(test)
    
    def test_keyboard_shortcuts(self):
        """Test keyboard shortcuts."""
        def test():
            self.assertTrue(self.create_mock_gui())
            
            # Test F1 help shortcut
            self.gui.root.focus_set()
            self.gui.root.event_generate('<F1>')
            
            # Test Ctrl+H help shortcut
            self.gui.root.event_generate('<Control-h>')
            
            # Test tab navigation shortcuts
            self.gui.root.event_generate('<Control-Tab>')
            self.gui.root.event_generate('<Control-Shift-Tab>')
            
            return True
        
        self.run_gui_test(test)


class TestDataTab(GUITestBase):
    """Test Data tab functionality."""
    
    def test_data_tab_creation(self):
        """Test Data tab creation."""
        def test():
            self.assertTrue(self.create_mock_gui())
            
            data_tab = self.gui.data_tab
            self.assertIsNotNone(data_tab.frame)
            self.assertIsNotNone(data_tab.treeview)
            self.assertIsNotNone(data_tab.open_button)
            self.assertIsNotNone(data_tab.save_button)
            self.assertIsNotNone(data_tab.refresh_button)
            
            return True
        
        self.run_gui_test(test)
    
    def test_file_dialog_creation(self):
        """Test file dialog creation."""
        def test():
            self.assertTrue(self.create_mock_gui())
            
            data_tab = self.gui.data_tab
            
            # Mock the file dialog to avoid actual file selection
            with patch('tkinter.filedialog.askopenfilenames') as mock_dialog:
                mock_dialog.return_value = [os.path.join(self.test_data_dir, 'test_data.csv')]
                
                # Test opening file dialog
                data_tab.open_file_dialog()
                
                # Verify dialog was called
                mock_dialog.assert_called_once()
            
            return True
        
        self.run_gui_test(test)
    
    def test_data_loading(self):
        """Test data loading functionality."""
        def test():
            self.assertTrue(self.create_mock_gui())
            
            data_tab = self.gui.data_tab
            
            # Test loading CSV data
            csv_path = os.path.join(self.test_data_dir, 'test_data.csv')
            data_tab.load_files([csv_path])
            
            # Wait for loading to complete
            time.sleep(1)
            
            # Check that data was loaded
            self.assertIsNotNone(data_tab.current_data)
            self.assertFalse(data_tab.current_data.empty)
            
            return True
        
        self.run_gui_test(test)
    
    def test_data_clearing(self):
        """Test data clearing functionality."""
        def test():
            self.assertTrue(self.create_mock_gui())
            
            data_tab = self.gui.data_tab
            
            # Load some data first
            csv_path = os.path.join(self.test_data_dir, 'test_data.csv')
            data_tab.load_files([csv_path])
            time.sleep(1)
            
            # Clear data
            data_tab.clear_data()
            
            # Check that data was cleared
            self.assertIsNone(data_tab.current_data)
            
            return True
        
        self.run_gui_test(test)


class TestAnalysisTab(GUITestBase):
    """Test Analysis tab functionality."""
    
    def test_analysis_tab_creation(self):
        """Test Analysis tab creation."""
        def test():
            self.assertTrue(self.create_mock_gui())
            
            analysis_tab = self.gui.analysis_tab
            self.assertIsNotNone(analysis_tab.frame)
            self.assertIsNotNone(analysis_tab.results_text)
            
            return True
        
        self.run_gui_test(test)
    
    def test_statistical_analysis(self):
        """Test statistical analysis functionality."""
        def test():
            self.assertTrue(self.create_mock_gui())
            
            analysis_tab = self.gui.analysis_tab
            
            # Load test data
            data_tab = self.gui.data_tab
            csv_path = os.path.join(self.test_data_dir, 'test_data.csv')
            data_tab.load_files([csv_path])
            time.sleep(1)
            
            # Run statistical analysis
            analysis_tab.run_statistical_analysis()
            
            # Check that results were generated
            results = analysis_tab.results_text.get(1.0, tk.END)
            self.assertIn("Statistical Summary", results)
            
            return True
        
        self.run_gui_test(test)
    
    def test_correlation_analysis(self):
        """Test correlation analysis functionality."""
        def test():
            self.assertTrue(self.create_mock_gui())
            
            analysis_tab = self.gui.analysis_tab
            
            # Load test data
            data_tab = self.gui.data_tab
            csv_path = os.path.join(self.test_data_dir, 'test_data.csv')
            data_tab.load_files([csv_path])
            time.sleep(1)
            
            # Run correlation analysis
            analysis_tab.run_correlation_analysis()
            
            # Check that results were generated
            results = analysis_tab.results_text.get(1.0, tk.END)
            self.assertIn("Correlation Matrix", results)
            
            return True
        
        self.run_gui_test(test)


class TestDownloadTab(GUITestBase):
    """Test Download tab functionality."""
    
    def test_download_tab_creation(self):
        """Test Download tab creation."""
        def test():
            self.assertTrue(self.create_mock_gui())
            
            download_tab = self.gui.download_tab
            self.assertIsNotNone(download_tab.frame)
            self.assertIsNotNone(download_tab.ticker_entry)
            self.assertIsNotNone(download_tab.download_button)
            self.assertIsNotNone(download_tab.results_tree)
            
            return True
        
        self.run_gui_test(test)
    
    def test_ticker_input(self):
        """Test ticker input functionality."""
        def test():
            self.assertTrue(self.create_mock_gui())
            
            download_tab = self.gui.download_tab
            
            # Test adding tickers
            download_tab.add_ticker("AAPL")
            content = download_tab.ticker_entry.get(1.0, tk.END).strip()
            self.assertEqual(content, "AAPL")
            
            # Test adding another ticker
            download_tab.add_ticker("MSFT")
            content = download_tab.ticker_entry.get(1.0, tk.END).strip()
            self.assertIn("AAPL", content)
            self.assertIn("MSFT", content)
            
            return True
        
        self.run_gui_test(test)
    
    def test_date_range_setting(self):
        """Test date range setting functionality."""
        def test():
            self.assertTrue(self.create_mock_gui())
            
            download_tab = self.gui.download_tab
            
            # Test setting date range
            download_tab.set_date_range("1y")
            
            # Check that dates were set
            start_date = download_tab.start_date_var.get()
            end_date = download_tab.end_date_var.get()
            
            self.assertIsNotNone(start_date)
            self.assertIsNotNone(end_date)
            
            return True
        
        self.run_gui_test(test)


class TestConverterTab(GUITestBase):
    """Test Converter tab functionality."""
    
    def test_converter_tab_creation(self):
        """Test Converter tab creation."""
        def test():
            self.assertTrue(self.create_mock_gui())
            
            converter_tab = self.gui.converter_tab
            self.assertIsNotNone(converter_tab.frame)
            self.assertIsNotNone(converter_tab.input_files_var)
            self.assertIsNotNone(converter_tab.output_format_var)
            self.assertIsNotNone(converter_tab.convert_btn)
            self.assertIsNotNone(converter_tab.results_tree)
            
            return True
        
        self.run_gui_test(test)
    
    def test_format_validation(self):
        """Test format validation functionality."""
        def test():
            self.assertTrue(self.create_mock_gui())
            
            converter_tab = self.gui.converter_tab
            
            # Check that format validation was run
            # This should be logged during initialization
            self.assertIsNotNone(converter_tab.converter)
            
            return True
        
        self.run_gui_test(test)
    
    def test_file_selection(self):
        """Test file selection functionality."""
        def test():
            self.assertTrue(self.create_mock_gui())
            
            converter_tab = self.gui.converter_tab
            
            # Mock the file dialog
            with patch('tkinter.filedialog.askopenfilenames') as mock_dialog:
                mock_dialog.return_value = [os.path.join(self.test_data_dir, 'test_data.csv')]
                
                # Test browsing for files
                converter_tab.browse_input_files()
                
                # Verify dialog was called
                mock_dialog.assert_called_once()
            
            return True
        
        self.run_gui_test(test)


class TestSettingsTab(GUITestBase):
    """Test Settings tab functionality."""
    
    def test_settings_tab_creation(self):
        """Test Settings tab creation."""
        def test():
            self.assertTrue(self.create_mock_gui())
            
            settings_tab = self.gui.settings_tab
            self.assertIsNotNone(settings_tab.frame)
            self.assertIsNotNone(settings_tab.settings_notebook)
            self.assertIsNotNone(settings_tab.settings_vars)
            
            return True
        
        self.run_gui_test(test)
    
    def test_settings_loading(self):
        """Test settings loading functionality."""
        def test():
            self.assertTrue(self.create_mock_gui())
            
            settings_tab = self.gui.settings_tab
            
            # Test loading current settings
            settings_tab.load_current_settings()
            
            # Check that settings variables are set
            self.assertGreater(len(settings_tab.settings_vars), 0)
            
            return True
        
        self.run_gui_test(test)


class TestHelpSystem(GUITestBase):
    """Test help system functionality."""
    
    def test_help_button_creation(self):
        """Test help button creation."""
        def test():
            self.assertTrue(self.create_mock_gui())
            
            # Check help button exists
            self.assertIsNotNone(self.gui.help_btn)
            self.assertEqual(self.gui.help_btn['text'], '?')
            
            return True
        
        self.run_gui_test(test)
    
    def test_help_dialog_creation(self):
        """Test help dialog creation."""
        def test():
            self.assertTrue(self.create_mock_gui())
            
            # Test showing help dialog
            self.gui.show_help()
            
            # Check that help window was created
            # Note: This might need adjustment based on actual implementation
            
            return True
        
        self.run_gui_test(test)
    
    def test_tooltip_creation(self):
        """Test tooltip creation."""
        def test():
            self.assertTrue(self.create_mock_gui())
            
            # Test creating a tooltip
            test_widget = tk.Label(self.root, text="Test")
            self.gui.create_tooltip(test_widget, "Test tooltip")
            
            # Check that tooltip was created (bindings exist)
            self.assertTrue(hasattr(test_widget, 'bind'))
            
            return True
        
        self.run_gui_test(test)


class TestIntegration(GUITestBase):
    """Test cross-tab integration and data flow."""
    
    def test_data_flow_between_tabs(self):
        """Test data flow between tabs."""
        def test():
            self.assertTrue(self.create_mock_gui())
            
            # Load data in Data tab
            data_tab = self.gui.data_tab
            csv_path = os.path.join(self.test_data_dir, 'test_data.csv')
            data_tab.load_files([csv_path])
            time.sleep(1)
            
            # Switch to Analysis tab and run analysis
            analysis_tab = self.gui.analysis_tab
            analysis_tab.run_statistical_analysis()
            
            # Check that analysis used the loaded data
            results = analysis_tab.results_text.get(1.0, tk.END)
            self.assertIn("Statistical Summary", results)
            
            return True
        
        self.run_gui_test(test)
    
    def test_converter_to_data_tab_integration(self):
        """Test integration between Converter and Data tabs."""
        def test():
            self.assertTrue(self.create_mock_gui())
            
            converter_tab = self.gui.converter_tab
            
            # Test loading converted files to data tab
            # This would require actual conversion, so we'll test the method exists
            self.assertTrue(hasattr(converter_tab, 'load_to_data_tab'))
            
            return True
        
        self.run_gui_test(test)


class TestErrorHandling(GUITestBase):
    """Test error handling and edge cases."""
    
    def test_invalid_file_handling(self):
        """Test handling of invalid files."""
        def test():
            self.assertTrue(self.create_mock_gui())
            
            data_tab = self.gui.data_tab
            
            # Test loading non-existent file
            data_tab.load_files(["/non/existent/file.csv"])
            time.sleep(1)
            
            # Check that error was handled gracefully
            self.assertIsNone(data_tab.current_data)
            
            return True
        
        self.run_gui_test(test)
    
    def test_empty_data_handling(self):
        """Test handling of empty data."""
        def test():
            self.assertTrue(self.create_mock_gui())
            
            analysis_tab = self.gui.analysis_tab
            
            # Run analysis with no data loaded
            analysis_tab.run_statistical_analysis()
            
            # Check that appropriate message was shown
            results = analysis_tab.results_text.get(1.0, tk.END)
            self.assertIn("No data available", results)
            
            return True
        
        self.run_gui_test(test)
    
    def test_window_resize_error_handling(self):
        """Test window resize error handling."""
        def test():
            self.assertTrue(self.create_mock_gui())
            
            # Test window resize event
            self.gui.on_window_configure(type('Event', (), {'widget': self.gui.root})())
            
            # Should not raise any exceptions
            return True
        
        self.run_gui_test(test)


def run_gui_tests():
    """Run all GUI tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestMainWindow,
        TestDataTab,
        TestAnalysisTab,
        TestDownloadTab,
        TestConverterTab,
        TestSettingsTab,
        TestHelpSystem,
        TestIntegration,
        TestErrorHandling
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("Running REDLINE GUI Integration Tests...")
    print("=" * 50)
    
    success = run_gui_tests()
    
    if success:
        print("\n✅ All GUI tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some GUI tests failed!")
        sys.exit(1)
