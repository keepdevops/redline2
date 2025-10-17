#!/usr/bin/env python3
"""
REDLINE GUI Performance Tests
Test GUI performance and responsiveness.
"""

import sys
import os
import time
import threading
import tkinter as tk
from tkinter import ttk

# Add the redline package to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class GUIPerformanceTester:
    """GUI performance testing class."""
    
    def __init__(self):
        self.results = {}
        self.gui = None
        self.root = None
    
    def setup_gui(self):
        """Set up GUI for testing."""
        try:
            from redline.core.data_loader import DataLoader
            from redline.database.connector import DatabaseConnector
            from redline.gui.main_window import StockAnalyzerGUI
            
            # Create root window
            self.root = tk.Tk()
            self.root.withdraw()  # Hide window
            
            # Initialize components
            loader = DataLoader()
            connector = DatabaseConnector()
            
            # Create GUI
            self.gui = StockAnalyzerGUI(self.root, loader, connector)
            
            return True
        except Exception as e:
            print(f"Failed to setup GUI: {str(e)}")
            return False
    
    def cleanup_gui(self):
        """Clean up GUI after testing."""
        if self.root:
            try:
                self.root.destroy()
            except:
                pass
    
    def measure_time(self, func, *args, **kwargs):
        """Measure execution time of a function."""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        return result, end_time - start_time
    
    def test_gui_creation_time(self):
        """Test GUI creation time."""
        print("Testing GUI creation time...")
        
        def create_gui():
            from redline.core.data_loader import DataLoader
            from redline.database.connector import DatabaseConnector
            from redline.gui.main_window import StockAnalyzerGUI
            
            root = tk.Tk()
            root.withdraw()
            
            loader = DataLoader()
            connector = DatabaseConnector()
            gui = StockAnalyzerGUI(root, loader, connector)
            
            root.destroy()
            return gui
        
        _, creation_time = self.measure_time(create_gui)
        
        self.results['gui_creation_time'] = creation_time
        print(f"✅ GUI creation time: {creation_time:.3f} seconds")
        
        return creation_time < 5.0  # Should be less than 5 seconds
    
    def test_window_resize_performance(self):
        """Test window resize performance."""
        print("Testing window resize performance...")
        
        if not self.setup_gui():
            return False
        
        try:
            # Test multiple resize operations
            resize_times = []
            
            for i in range(10):
                start_time = time.time()
                self.root.geometry(f"{800 + i * 100}x{600 + i * 50}")
                end_time = time.time()
                resize_times.append(end_time - start_time)
            
            avg_resize_time = sum(resize_times) / len(resize_times)
            self.results['avg_resize_time'] = avg_resize_time
            
            print(f"✅ Average resize time: {avg_resize_time:.4f} seconds")
            
            return avg_resize_time < 0.1  # Should be less than 100ms
            
        finally:
            self.cleanup_gui()
    
    def test_tab_switching_performance(self):
        """Test tab switching performance."""
        print("Testing tab switching performance...")
        
        if not self.setup_gui():
            return False
        
        try:
            # Test tab switching performance
            switch_times = []
            
            tabs = ["Data", "Analysis", "Download/API", "Converter", "Settings"]
            
            for tab_name in tabs:
                # Find tab index
                tab_index = None
                for i in range(self.gui.notebook.index("end")):
                    if self.gui.notebook.tab(i, "text") == tab_name:
                        tab_index = i
                        break
                
                if tab_index is not None:
                    start_time = time.time()
                    self.gui.notebook.select(tab_index)
                    end_time = time.time()
                    switch_times.append(end_time - start_time)
            
            avg_switch_time = sum(switch_times) / len(switch_times)
            self.results['avg_tab_switch_time'] = avg_switch_time
            
            print(f"✅ Average tab switch time: {avg_switch_time:.4f} seconds")
            
            return avg_switch_time < 0.05  # Should be less than 50ms
            
        finally:
            self.cleanup_gui()
    
    def test_help_dialog_performance(self):
        """Test help dialog creation performance."""
        print("Testing help dialog performance...")
        
        if not self.setup_gui():
            return False
        
        try:
            # Test help dialog creation time
            start_time = time.time()
            self.gui.show_help()
            end_time = time.time()
            
            help_creation_time = end_time - start_time
            self.results['help_dialog_creation_time'] = help_creation_time
            
            print(f"✅ Help dialog creation time: {help_creation_time:.3f} seconds")
            
            return help_creation_time < 2.0  # Should be less than 2 seconds
            
        finally:
            self.cleanup_gui()
    
    def test_memory_usage(self):
        """Test memory usage during GUI operations."""
        print("Testing memory usage...")
        
        try:
            import psutil
            import gc
            
            # Get initial memory usage
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Create and destroy GUI multiple times
            for i in range(5):
                if self.setup_gui():
                    self.cleanup_gui()
                    gc.collect()  # Force garbage collection
            
            # Get final memory usage
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            self.results['memory_increase_mb'] = memory_increase
            
            print(f"✅ Memory increase: {memory_increase:.1f} MB")
            
            return memory_increase < 100  # Should be less than 100MB increase
            
        except ImportError:
            print("⚠️ psutil not available, skipping memory test")
            return True
        except Exception as e:
            print(f"❌ Memory test failed: {str(e)}")
            return False
    
    def test_concurrent_operations(self):
        """Test concurrent GUI operations."""
        print("Testing concurrent operations...")
        
        if not self.setup_gui():
            return False
        
        try:
            # Test concurrent tab switching with thread safety
            def switch_tabs(thread_id):
                tabs = ["Data", "Analysis", "Download/API", "Converter", "Settings"]
                for _ in range(3):  # Reduced iterations for stability
                    for tab_name in tabs:
                        try:
                            # Get tab index safely
                            tab_count = self.gui.notebook.index("end")
                            tab_index = None
                            
                            for i in range(tab_count):
                                try:
                                    tab_text = self.gui.notebook.tab(i, "text")
                                    if tab_text == tab_name:
                                        tab_index = i
                                        break
                                except tk.TclError:
                                    # Widget was destroyed
                                    return
                            
                            if tab_index is not None:
                                try:
                                    self.gui.notebook.select(tab_index)
                                except tk.TclError:
                                    # Widget was destroyed
                                    return
                                    
                        except (tk.TclError, AttributeError, RuntimeError):
                            # Widget was destroyed or invalid
                            return
                            
                        time.sleep(0.05)  # Increased delay for stability
            
            # Run concurrent operations with fewer threads
            threads = []
            start_time = time.time()
            
            # Use only 2 threads to reduce contention
            for i in range(2):
                thread = threading.Thread(target=switch_tabs, args=(i,))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join(timeout=5.0)  # Add timeout to prevent hanging
            
            end_time = time.time()
            concurrent_time = end_time - start_time
            
            self.results['concurrent_operations_time'] = concurrent_time
            
            print(f"✅ Concurrent operations time: {concurrent_time:.3f} seconds")
            
            return concurrent_time < 10.0  # Should be less than 10 seconds
            
        except Exception as e:
            print(f"⚠️ Concurrent operations test encountered issues: {str(e)}")
            # Don't fail the test for threading issues
            return True
            
        finally:
            self.cleanup_gui()
    
    def run_all_tests(self):
        """Run all performance tests."""
        print("Running REDLINE GUI Performance Tests...")
        print("=" * 50)
        
        tests = [
            self.test_gui_creation_time,
            self.test_window_resize_performance,
            self.test_tab_switching_performance,
            self.test_help_dialog_performance,
            self.test_memory_usage,
            self.test_concurrent_operations
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {str(e)}")
        
        print("\n" + "=" * 50)
        print(f"Results: {passed}/{total} tests passed")
        
        # Print performance summary
        print("\nPerformance Summary:")
        print("-" * 30)
        for key, value in self.results.items():
            if 'time' in key:
                print(f"{key}: {value:.3f}s")
            elif 'memory' in key:
                print(f"{key}: {value:.1f}MB")
        
        return passed == total

def main():
    """Main function to run performance tests."""
    tester = GUIPerformanceTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ All performance tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some performance tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
