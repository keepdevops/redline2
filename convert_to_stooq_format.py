#!/usr/bin/env python3
"""
Convert downloaded data to Stooq format for REDLINE compatibility
"""

import pandas as pd
import os
import sys
from datetime import datetime
import glob

def convert_to_stooq_format(input_file, output_file=None):
    """
    Convert downloaded data to Stooq format that REDLINE expects
    
    Args:
        input_file: Path to input CSV file
        output_file: Path to output file (optional)
    """
    try:
        # Read the input file
        df = pd.read_csv(input_file)
        
        # Convert to Stooq format
        df_stooq = convert_dataframe_to_stooq(df)
        
        # Generate output filename if not provided
        if output_file is None:
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}_stooq_format.csv"
        
        # Save in Stooq format
        df_stooq.to_csv(output_file, index=False)
        
        print(f"Converted {input_file} to Stooq format: {output_file}")
        return output_file
        
    except Exception as e:
        print(f"Error converting {input_file}: {str(e)}")
        return None

def convert_dataframe_to_stooq(df):
    """
    Convert a DataFrame to Stooq format
    """
    df_stooq = df.copy()
    
    # Handle different input formats
    if 'timestamp' in df.columns:
        # Convert timestamp to DATE and TIME columns
        try:
            # Handle timezone-aware timestamps
            df_stooq['timestamp'] = pd.to_datetime(df_stooq['timestamp'], utc=True)
            df_stooq['timestamp'] = df_stooq['timestamp'].dt.tz_localize(None)  # Remove timezone
            df_stooq['<DATE>'] = df_stooq['timestamp'].dt.strftime('%Y%m%d')
        except:
            # Fallback for timezone issues
            df_stooq['timestamp'] = pd.to_datetime(df_stooq['timestamp'], errors='coerce')
            df_stooq['<DATE>'] = df_stooq['timestamp'].dt.strftime('%Y%m%d')
        
        df_stooq['<TIME>'] = '000000'  # Default time for daily data
        
        # Map columns to Stooq format
        column_mapping = {
            'ticker': '<TICKER>',
            'open': '<OPEN>',
            'high': '<HIGH>',
            'low': '<LOW>',
            'close': '<CLOSE>',
            'vol': '<VOL>'
        }
        
        # Rename columns
        for old_col, new_col in column_mapping.items():
            if old_col in df_stooq.columns:
                df_stooq[new_col] = df_stooq[old_col]
        
        # Select and reorder Stooq columns
        stooq_columns = ['<TICKER>', '<DATE>', '<TIME>', '<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>', '<VOL>']
        df_stooq = df_stooq[stooq_columns]
        
        # Handle missing values
        df_stooq = df_stooq.dropna(subset=['<TICKER>', '<DATE>', '<CLOSE>'])
        
        # Ensure numeric columns are properly formatted
        numeric_cols = ['<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>', '<VOL>']
        for col in numeric_cols:
            if col in df_stooq.columns:
                df_stooq[col] = pd.to_numeric(df_stooq[col], errors='coerce')
        
        # Remove rows with invalid numeric data
        df_stooq = df_stooq.dropna(subset=numeric_cols)
        
    else:
        # Assume it's already in some Stooq-like format
        # Just ensure we have the required columns
        required_cols = ['<TICKER>', '<DATE>', '<TIME>', '<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>', '<VOL>']
        
        # If columns don't exist, try to map from common alternatives
        if '<TICKER>' not in df_stooq.columns:
            if 'ticker' in df_stooq.columns:
                df_stooq['<TICKER>'] = df_stooq['ticker']
            else:
                df_stooq['<TICKER>'] = 'UNKNOWN'
        
        if '<DATE>' not in df_stooq.columns:
            if 'Date' in df_stooq.columns:
                df_stooq['<DATE>'] = pd.to_datetime(df_stooq['Date']).dt.strftime('%Y%m%d')
            elif 'timestamp' in df_stooq.columns:
                df_stooq['<DATE>'] = pd.to_datetime(df_stooq['timestamp']).dt.strftime('%Y%m%d')
            else:
                df_stooq['<DATE>'] = datetime.now().strftime('%Y%m%d')
        
        if '<TIME>' not in df_stooq.columns:
            df_stooq['<TIME>'] = '000000'
        
        # Map price columns
        price_mapping = {
            'Open': '<OPEN>',
            'High': '<HIGH>',
            'Low': '<LOW>',
            'Close': '<CLOSE>',
            'Volume': '<VOL>',
            'open': '<OPEN>',
            'high': '<HIGH>',
            'low': '<LOW>',
            'close': '<CLOSE>',
            'vol': '<VOL>'
        }
        
        for old_col, new_col in price_mapping.items():
            if old_col in df_stooq.columns and new_col not in df_stooq.columns:
                df_stooq[new_col] = df_stooq[old_col]
        
        # Select required columns
        available_cols = [col for col in required_cols if col in df_stooq.columns]
        df_stooq = df_stooq[available_cols]
    
    return df_stooq

def batch_convert_directory(input_dir="data", output_dir="data/stooq_format"):
    """
    Convert all CSV files in a directory to Stooq format
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all CSV files
    csv_files = glob.glob(os.path.join(input_dir, "*.csv"))
    
    converted_files = []
    for csv_file in csv_files:
        # Skip already converted files
        if '_stooq_format' in csv_file:
            continue
            
        filename = os.path.basename(csv_file)
        output_file = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}_stooq_format.csv")
        
        result = convert_to_stooq_format(csv_file, output_file)
        if result:
            converted_files.append(result)
    
    print(f"Converted {len(converted_files)} files to Stooq format")
    return converted_files

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert data files to Stooq format for REDLINE")
    parser.add_argument("--input", "-i", help="Input CSV file")
    parser.add_argument("--output", "-o", help="Output CSV file")
    parser.add_argument("--batch", "-b", action="store_true", help="Convert all CSV files in data directory")
    
    args = parser.parse_args()
    
    if args.batch:
        batch_convert_directory()
    elif args.input:
        convert_to_stooq_format(args.input, args.output)
    else:
        print("Usage:")
        print("  python convert_to_stooq_format.py --input file.csv")
        print("  python convert_to_stooq_format.py --batch")

if __name__ == "__main__":
    main()
