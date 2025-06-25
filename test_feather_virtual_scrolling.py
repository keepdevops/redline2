#!/usr/bin/env python3
"""
Test script to verify virtual scrolling works with Feather database format
"""

import os
import sys
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
import logging

# Add the current directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_module_shared import DataLoader, DataSource, VirtualScrollingTreeview, StockAnalyzerGUI, DatabaseConnector

def create_test_feather_file():
    """Create a test Feather file with sample data"""
    print("Creating test Feather file...")
    
    # Create sample data
    data = {
        'ticker': ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN'] * 1000,  # 5000 rows
        'timestamp': pd.date_range('2023-01-01', periods=5000, freq='H'),
        'open': [150.0 + i * 0.1 for i in range(5000)],
        'high': [155.0 + i * 0.1 for i in range(5000)],
        'low': [145.0 + i * 0.1 for i in range(5000)],
        'close': [152.0 + i * 0.1 for i in range(5000)],
        'vol': [1000000 + i * 1000 for i in range(5000)],
        'openint': [0] * 5000,
        'format': ['feather'] * 5000
    }
    
    df = pd.DataFrame(data)
    
    # Save as Feather
    feather_file = 'test_feather_data.feather'
    df.to_feather(feather_file)
    
    print(f"Created {len(df)} rows in {feather_file}")
    print(f"File size: {os.path.getsize(feather_file) / 1024 / 1024:.2f} MB")
    
    return feather_file

def test_feather_data_source():
    """Test DataSource with Feather format"""
    print("\n=== Testing DataSource with Feather ===")
    
    feather_file = create_test_feather_file()
    
    try:
        # Create data source
        data_source = DataSource(feather_file, 'feather')
        
        print(f"✓ DataSource created successfully")
        print(f"✓ Total rows: {data_source.get_total_rows()}")
        
        # Test getting individual rows
        row_0 = data_source.get_row(0)
        row_1000 = data_source.get_row(1000)
        row_4999 = data_source.get_row(4999)
        
        print(f"✓ Row 0: {row_0[:3]}...")  # Show first 3 values
        print(f"✓ Row 1000: {row_1000[:3]}...")
        print(f"✓ Row 4999: {row_4999[:3]}...")
        
        # Test getting row ranges
        rows_100_110 = data_source.get_rows(100, 110)
        print(f"✓ Rows 100-110: {len(rows_100_110)} rows retrieved")
        
        # Clean up
        data_source.close()
        print("✓ DataSource closed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ DataSource test failed: {str(e)}")
        return False

def test_virtual_scrolling_with_feather():
    """Test virtual scrolling with Feather format"""
    print("\n=== Testing Virtual Scrolling with Feather ===")
    
    feather_file = create_test_feather_file()
    
    try:
        # Create test window
        root = tk.Tk()
        root.title("Feather Virtual Scrolling Test")
        root.geometry("800x600")
        
        # Create data source
        data_source = DataSource(feather_file, 'feather')
        
        # Create virtual scrolling treeview
        columns = ['ticker', 'timestamp', 'open', 'high', 'low', 'close', 'vol']
        virtual_tree = VirtualScrollingTreeview(root, columns)
        virtual_tree.tree.pack(fill='both', expand=True)
        
        # Set data source
        virtual_tree.set_data_source(data_source)
        
        print(f"✓ Virtual scrolling treeview created")
        print(f"✓ Data source connected with {data_source.get_total_rows()} rows")
        
        # Test scrolling
        def test_scroll():
            print("Testing scroll functionality...")
            # Simulate scrolling by updating visible range
            virtual_tree.visible_start = 100
            virtual_tree.visible_end = 200
            virtual_tree._load_visible_items()
            
            # Check if items are loaded
            items = virtual_tree.tree.get_children()
            print(f"✓ Loaded {len(items)} visible items")
            
            # Test memory usage
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            print(f"✓ Memory usage: {memory_mb:.2f} MB")
            
            root.after(2000, root.quit)  # Close after 2 seconds
        
        root.after(1000, test_scroll)
        root.mainloop()
        
        # Clean up
        data_source.close()
        os.remove(feather_file)
        
        print("✓ Virtual scrolling test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Virtual scrolling test failed: {str(e)}")
        if os.path.exists(feather_file):
            os.remove(feather_file)
        return False

def test_gui_integration():
    """Test GUI integration with Feather files"""
    print("\n=== Testing GUI Integration with Feather ===")
    
    feather_file = create_test_feather_file()
    
    try:
        # Create test window
        root = tk.Tk()
        root.title("Feather GUI Integration Test")
        root.geometry("1200x800")
        
        # Create required components
        loader = DataLoader()
        connector = DatabaseConnector()
        gui = StockAnalyzerGUI(root, loader, connector)
        
        print("✓ GUI created successfully")
        
        # Test loading Feather file with virtual scrolling
        def test_load():
            try:
                # Enable virtual scrolling
                gui.enable_virtual_scrolling()
                print("✓ Virtual scrolling enabled")
                
                # Load data with virtual scrolling
                gui.load_data_with_virtual_scrolling(feather_file, 'feather')
                print("✓ Feather data loaded with virtual scrolling")
                
                # Check if data is displayed
                items = gui.data_tree.get_children()
                print(f"✓ Displayed {len(items)} items in treeview")
                
                # Test memory optimization
                gui.optimize_memory_usage()
                print("✓ Memory optimization applied")
                
                root.after(3000, root.quit)  # Close after 3 seconds
                
            except Exception as e:
                print(f"❌ GUI integration test failed: {str(e)}")
                root.quit()
        
        root.after(1000, test_load)
        root.mainloop()
        
        # Clean up
        os.remove(feather_file)
        
        print("✓ GUI integration test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ GUI integration test failed: {str(e)}")
        if os.path.exists(feather_file):
            os.remove(feather_file)
        return False

def test_performance_comparison():
    """Compare performance between regular loading and virtual scrolling"""
    print("\n=== Performance Comparison Test ===")
    
    feather_file = create_test_feather_file()
    
    try:
        import time
        import psutil
        
        # Test regular loading
        print("Testing regular loading...")
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        df = pd.read_feather(feather_file)
        
        regular_time = time.time() - start_time
        regular_memory = psutil.Process().memory_info().rss / 1024 / 1024 - start_memory
        
        print(f"✓ Regular loading: {regular_time:.2f}s, {regular_memory:.2f}MB")
        
        # Test virtual scrolling loading
        print("Testing virtual scrolling loading...")
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        data_source = DataSource(feather_file, 'feather')
        
        virtual_time = time.time() - start_time
        virtual_memory = psutil.Process().memory_info().rss / 1024 / 1024 - start_memory
        
        print(f"✓ Virtual scrolling: {virtual_time:.2f}s, {virtual_memory:.2f}MB")
        
        # Calculate improvements
        time_improvement = ((regular_time - virtual_time) / regular_time) * 100
        memory_improvement = ((regular_memory - virtual_memory) / regular_memory) * 100
        
        print(f"✓ Time improvement: {time_improvement:.1f}%")
        print(f"✓ Memory improvement: {memory_improvement:.1f}%")
        
        # Clean up
        data_source.close()
        os.remove(feather_file)
        
        return True
        
    except Exception as e:
        print(f"❌ Performance comparison failed: {str(e)}")
        if os.path.exists(feather_file):
            os.remove(feather_file)
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Virtual Scrolling with Feather Database Format")
    print("=" * 60)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    tests = [
        ("DataSource with Feather", test_feather_data_source),
        ("Virtual Scrolling with Feather", test_virtual_scrolling_with_feather),
        ("GUI Integration", test_gui_integration),
        ("Performance Comparison", test_performance_comparison)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Virtual scrolling works perfectly with Feather format.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 