#!/usr/bin/env python3
"""
Test file loading functionality
"""

import sys
import os
import pandas as pd

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_file_loading():
    """Test loading the Yahoo to Stooq file."""
    print("Testing file loading...")
    
    # Test file path
    file_path = "./data/stooq_format/AAPL_yahoo_data_stooq_format.csv"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    try:
        # Test basic pandas loading
        print("1. Testing pandas loading...")
        df = pd.read_csv(file_path)
        print(f"   ✅ Loaded {len(df)} rows, {len(df.columns)} columns")
        print(f"   Columns: {list(df.columns)}")
        print(f"   First few rows:")
        print(df.head(3))
        
        # Test REDLINE DataLoader
        print("\n2. Testing REDLINE DataLoader...")
        from redline.core.data_loader import DataLoader
        loader = DataLoader()
        
        data = loader.load_file_by_type(file_path, "csv")
        print(f"   ✅ REDLINE loaded {len(data)} rows")
        
        # Test DataSource creation
        print("\n3. Testing DataSource creation...")
        from redline.gui.widgets.data_source import DataSource
        
        data_source = DataSource(None, "pandas")
        data_source.data = data
        data_source.total_rows = len(data)
        print(f"   ✅ DataSource created with {data_source.total_rows} rows")
        
        # Test getting a row
        print("\n4. Testing row access...")
        row = data_source.get_row(0)
        print(f"   ✅ First row: {row}")
        
        print("\n🎉 All tests passed! File loading is working correctly.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_file_loading()
