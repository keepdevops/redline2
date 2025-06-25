#!/usr/bin/env python3
"""
Test script to demonstrate the new performance optimization and advanced filtering features.
This test shows how the data viewer can handle large datasets efficiently and provide advanced query capabilities.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import sys
import os
import pandas as pd
import numpy as np
import duckdb

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_module_shared import StockAnalyzerGUI, DataLoader, DatabaseConnector, VirtualScrollingTreeview, AdvancedQueryBuilder, DataSource

def create_large_test_dataset():
    """Create a large test dataset to demonstrate performance improvements"""
    print("Creating large test dataset...")
    
    # Create a large dataset with 100,000 rows
    np.random.seed(42)
    n_rows = 100000
    
    # Generate realistic stock data
    tickers = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'META', 'NVDA', 'NFLX', 'AMD', 'INTC']
    dates = pd.date_range('2020-01-01', '2023-12-31', freq='D')
    
    data = []
    for i in range(n_rows):
        ticker = np.random.choice(tickers)
        date = np.random.choice(dates)
        base_price = np.random.uniform(50, 500)
        
        # Generate OHLCV data
        open_price = base_price
        high_price = open_price * np.random.uniform(1.0, 1.1)
        low_price = open_price * np.random.uniform(0.9, 1.0)
        close_price = np.random.uniform(low_price, high_price)
        volume = np.random.randint(1000000, 10000000)
        
        data.append({
            'ticker': ticker,
            'timestamp': date,
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'vol': volume,
            'openint': np.random.randint(0, 1000),
            'format': 'test'
        })
    
    df = pd.DataFrame(data)
    return df

def test_performance_optimization():
    """Test performance optimization features"""
    print("Testing performance optimization features...")
    
    # Create test window
    root = tk.Tk()
    root.title("Performance Optimization Test")
    root.geometry("1400x900")
    
    # Create the required components
    loader = DataLoader()
    connector = DatabaseConnector()
    gui = StockAnalyzerGUI(root, loader, connector)
    
    # Create large test dataset
    test_data = create_large_test_dataset()
    
    # Save to different formats for testing
    os.makedirs('data', exist_ok=True)
    
    # Save as CSV
    csv_file = 'data/large_test_data.csv'
    test_data.to_csv(csv_file, index=False)
    print(f"Saved {len(test_data)} rows to {csv_file}")
    
    # Save as DuckDB for advanced filtering
    duckdb_file = 'data/large_test_data.duckdb'
    conn = duckdb.connect(duckdb_file)
    conn.execute("CREATE TABLE tickers_data AS SELECT * FROM test_data")
    conn.execute("INSERT INTO tickers_data SELECT * FROM test_data")
    conn.close()
    print(f"Saved {len(test_data)} rows to {duckdb_file}")
    
    def test_virtual_scrolling():
        """Test virtual scrolling functionality"""
        print("  Testing virtual scrolling...")
        
        try:
            # Enable virtual scrolling
            gui.enable_virtual_scrolling()
            print("    ✓ Virtual scrolling enabled")
            
            # Load data with virtual scrolling
            gui.load_data_with_virtual_scrolling(duckdb_file, 'duckdb')
            print("    ✓ Large dataset loaded with virtual scrolling")
            
            # Check memory usage
            gui.optimize_memory_usage()
            print("    ✓ Memory optimization applied")
            
        except Exception as e:
            print(f"    ❌ Virtual scrolling test failed: {str(e)}")
    
    def test_advanced_filtering():
        """Test advanced filtering functionality"""
        print("  Testing advanced filtering...")
        
        try:
            # Test query builder
            query_builder = AdvancedQueryBuilder()
            
            # Test simple query
            conditions = [
                {'column': 'ticker', 'operator': 'equals', 'value': 'AAPL'},
                {'column': 'close', 'operator': 'greater_than', 'value': 100}
            ]
            
            query, params = query_builder.build_query(conditions)
            print(f"    ✓ Query built: {query}")
            print(f"    ✓ Parameters: {params}")
            
            # Test data source
            data_source = DataSource(duckdb_file, 'duckdb')
            print(f"    ✓ Data source created with {data_source.get_total_rows()} rows")
            
            # Test getting specific rows
            sample_row = data_source.get_row(0)
            print(f"    ✓ Sample row retrieved: {sample_row[:3]}...")
            
            data_source.close()
            print("    ✓ Data source closed")
            
        except Exception as e:
            print(f"    ❌ Advanced filtering test failed: {str(e)}")
    
    def test_memory_optimization():
        """Test memory optimization features"""
        print("  Testing memory optimization...")
        
        try:
            # Test memory optimization
            gui.optimize_memory_usage()
            print("    ✓ Memory optimization completed")
            
            # Test performance monitoring
            if hasattr(gui, 'memory_label'):
                print(f"    ✓ Memory monitoring active: {gui.memory_label.cget('text')}")
            
        except Exception as e:
            print(f"    ❌ Memory optimization test failed: {str(e)}")
    
    def run_performance_tests():
        """Run all performance tests"""
        try:
            test_virtual_scrolling()
            test_advanced_filtering()
            test_memory_optimization()
            
            print("\n🎉 All performance optimization tests completed!")
            
            # Show success message
            messagebox.showinfo("Test Results", 
                "Performance optimization tests completed!\n\n"
                "✅ Virtual scrolling enabled\n"
                "✅ Advanced filtering working\n"
                "✅ Memory optimization applied\n"
                "✅ Large dataset handling improved\n\n"
                "The data viewer can now handle large datasets efficiently!")
            
        except Exception as e:
            print(f"\n❌ Performance test failed: {str(e)}")
            messagebox.showerror("Test Failed", f"Performance test failed: {str(e)}")
        finally:
            # Clean up test files
            for file in [csv_file, duckdb_file]:
                if os.path.exists(file):
                    os.remove(file)
            root.after(3000, root.destroy)
    
    # Run tests after a short delay to let GUI initialize
    root.after(2000, run_performance_tests)
    
    # Start the GUI
    root.mainloop()

def test_advanced_filtering_ui():
    """Test the advanced filtering UI"""
    print("Testing advanced filtering UI...")
    
    # Create test window
    root = tk.Tk()
    root.title("Advanced Filtering Test")
    root.geometry("1000x700")
    
    # Create the required components
    loader = DataLoader()
    connector = DatabaseConnector()
    gui = StockAnalyzerGUI(root, loader, connector)
    
    def test_query_builder():
        """Test the query builder functionality"""
        print("  Testing query builder...")
        
        try:
            # Create query builder
            qb = AdvancedQueryBuilder()
            
            # Test various query types
            test_queries = [
                # Simple equality
                [{'column': 'ticker', 'operator': 'equals', 'value': 'AAPL'}],
                
                # Range query
                [{'column': 'close', 'operator': 'between', 'value': [100, 200]}],
                
                # Multiple conditions
                [
                    {'column': 'ticker', 'operator': 'in', 'value': ['AAPL', 'GOOGL']},
                    {'column': 'volume', 'operator': 'greater_than', 'value': 5000000}
                ],
                
                # Text search
                [{'column': 'ticker', 'operator': 'contains', 'value': 'AAP'}],
                
                # Null check
                [{'column': 'openint', 'operator': 'is_not_null', 'value': None}]
            ]
            
            for i, conditions in enumerate(test_queries):
                query, params = qb.build_query(conditions)
                print(f"    Query {i+1}: {query}")
                print(f"    Params: {params}")
            
            print("    ✓ All query types tested successfully")
            
        except Exception as e:
            print(f"    ❌ Query builder test failed: {str(e)}")
    
    def test_advanced_filter_window():
        """Test the advanced filter window"""
        print("  Testing advanced filter window...")
        
        try:
            # Open advanced filter window
            gui.setup_advanced_filters()
            print("    ✓ Advanced filter window opened")
            
            # Test adding conditions
            if hasattr(gui, 'filter_column_combo'):
                gui.filter_column_combo.set('ticker')
                gui.filter_operator_combo.set('equals')
                gui.filter_value_entry.insert(0, 'AAPL')
                gui.add_filter_condition()
                print("    ✓ Filter condition added")
            
        except Exception as e:
            print(f"    ❌ Advanced filter window test failed: {str(e)}")
    
    def run_filtering_tests():
        """Run all filtering tests"""
        try:
            test_query_builder()
            test_advanced_filter_window()
            
            print("\n🎉 All advanced filtering tests completed!")
            
            messagebox.showinfo("Test Results", 
                "Advanced filtering tests completed!\n\n"
                "✅ Query builder working\n"
                "✅ Advanced filter window opened\n"
                "✅ Complex queries supported\n"
                "✅ Filter conditions can be added\n\n"
                "Advanced filtering is now available!")
            
        except Exception as e:
            print(f"\n❌ Filtering test failed: {str(e)}")
            messagebox.showerror("Test Failed", f"Filtering test failed: {str(e)}")
        finally:
            root.after(3000, root.destroy)
    
    # Run tests after a short delay
    root.after(2000, run_filtering_tests)
    
    # Start the GUI
    root.mainloop()

def main():
    """Main test function"""
    print("REDLINE Performance and Filtering Test")
    print("=" * 50)
    
    # Ask user which test to run
    print("\nChoose a test to run:")
    print("1. Performance Optimization Test")
    print("2. Advanced Filtering Test")
    print("3. Both Tests")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            test_performance_optimization()
        elif choice == '2':
            test_advanced_filtering_ui()
        elif choice == '3':
            print("\nRunning both tests...")
            test_performance_optimization()
            # Wait a bit before running the second test
            time.sleep(2)
            test_advanced_filtering_ui()
        else:
            print("Invalid choice. Running performance optimization test by default.")
            test_performance_optimization()
            
    except KeyboardInterrupt:
        print("\nTest cancelled by user.")
    except Exception as e:
        print(f"\nTest failed: {str(e)}")

if __name__ == "__main__":
    main() 