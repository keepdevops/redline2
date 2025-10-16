#!/usr/bin/env python3
"""
Quick script to use converted Stooq format data with REDLINE
"""

import os
import shutil
import glob

def setup_converted_data():
    """Set up converted Stooq format data for REDLINE"""
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Find all converted Stooq format files
    stooq_files = glob.glob("data/stooq_format/*_stooq_format.csv")
    
    if not stooq_files:
        print("❌ No converted Stooq format files found!")
        print("Run: python convert_to_stooq_format.py --batch")
        return False
    
    print(f"📁 Found {len(stooq_files)} converted files:")
    for file in stooq_files:
        print(f"   - {os.path.basename(file)}")
    
    # Copy the multi-ticker file as the main data source
    main_file = "data/stooq_format/custom_tickers_yahoo_stooq_format.csv"
    if os.path.exists(main_file):
        target_file = "data/stooq_data.csv"
        shutil.copy2(main_file, target_file)
        print(f"✅ Copied {main_file} to {target_file}")
        
        # Show sample of the data
        import pandas as pd
        df = pd.read_csv(target_file)
        print(f"\n📊 Data preview:")
        print(f"   - Records: {len(df)}")
        print(f"   - Tickers: {df['<TICKER>'].unique()}")
        print(f"   - Date range: {df['<DATE>'].min()} to {df['<DATE>'].max()}")
        print(f"   - Columns: {list(df.columns)}")
        
        return True
    else:
        print(f"❌ Main file not found: {main_file}")
        return False

def main():
    """Main function"""
    print("🚀 Setting up converted Stooq format data for REDLINE...")
    
    if setup_converted_data():
        print("\n✅ Setup complete! You can now run:")
        print("   python main.py")
        print("\n📝 The data is in Stooq format with required columns:")
        print("   <TICKER>, <DATE>, <TIME>, <OPEN>, <HIGH>, <LOW>, <CLOSE>, <VOL>")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
