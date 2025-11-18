#!/usr/bin/env python3
"""
REDLINE CLI Analysis Tool
Command-line interface for data analysis operations.
"""

import argparse
import sys
import os
import pandas as pd
from typing import List

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from redline.core.data_loader import DataLoader
from redline.database.connector import DatabaseConnector
from redline.database.operations import DatabaseOperations
from redline.utils.logging_config import setup_logging

def main():
    """Main CLI entry point for data analysis."""
    parser = argparse.ArgumentParser(description='REDLINE Data Analysis CLI')
    
    # Input options
    parser.add_argument('--input', type=str, required=True,
                       help='Input file or directory path')
    parser.add_argument('--format', choices=['csv', 'parquet', 'json', 'auto'],
                       default='auto', help='Input file format')
    
    # Analysis options
    parser.add_argument('--analysis', choices=['stats', 'correlation', 'trends', 'volume'],
                       default='stats', help='Type of analysis to perform')
    
    # Filtering options
    parser.add_argument('--tickers', nargs='+',
                       help='Filter by specific tickers')
    parser.add_argument('--start-date', type=str,
                       help='Start date filter (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str,
                       help='End date filter (YYYY-MM-DD)')
    
    # Output options
    parser.add_argument('--output', type=str,
                       help='Output file path (optional)')
    parser.add_argument('--format-out', choices=['csv', 'json', 'table'],
                       default='table', help='Output format')
    
    # Logging options
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='Logging level')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(
        log_level=args.log_level,
        log_file='analysis.log',
        console_output=True
    )
    
    try:
        # Load data
        data = _load_data(args)
        
        if data.empty:
            print("No data loaded")
            sys.exit(1)
        
        # Apply filters
        filtered_data = _apply_filters(data, args)
        
        if filtered_data.empty:
            print("No data remaining after filtering")
            sys.exit(1)
        
        # Perform analysis
        results = _perform_analysis(filtered_data, args)
        
        # Output results
        _output_results(results, args)
        
        print("Analysis completed successfully!")
        
    except Exception as e:
        print(f"Analysis failed: {str(e)}")
        sys.exit(1)

def _load_data(args):
    """Load data from input source."""
    loader = DataLoader()
    
    if os.path.isfile(args.input):
        # Single file
        format_type = args.format
        if format_type == 'auto':
            format_type = _detect_format(args.input)
        
        data = loader.load_file_by_type(args.input, format_type)
        return data
        
    elif os.path.isdir(args.input):
        # Directory - find files
        import glob
        files = []
        if args.format == 'auto' or not args.format:
            patterns = ['*.csv', '*.parquet', '*.json']
        else:
            patterns = [f'*.{args.format}']
        
        for pattern in patterns:
            files.extend(glob.glob(os.path.join(args.input, pattern)))
        
        if not files:
            raise ValueError(f"No files found in {args.input}")
        
        # Load all files
        all_data = []
        for file_path in files:
            format_type = args.format
            if format_type == 'auto':
                format_type = _detect_format(file_path)
            
            data = loader.load_file_by_type(file_path, format_type)
            if not data.empty:
                all_data.append(data)
        
        if all_data:
            return pd.concat(all_data, ignore_index=True)
        else:
            return pd.DataFrame()
    
    else:
        raise ValueError(f"Input path does not exist: {args.input}")

def _detect_format(file_path):
    """Detect file format from extension (uses centralized function)."""
    from redline.core.schema import detect_format_from_path
    return detect_format_from_path(file_path)

def _apply_filters(data, args):
    """Apply filters to data."""
    filtered_data = data.copy()
    
    # Filter by tickers
    if args.tickers and 'ticker' in filtered_data.columns:
        filtered_data = filtered_data[filtered_data['ticker'].isin(args.tickers)]
    
    # Filter by date range
    if args.start_date or args.end_date:
        if 'timestamp' in filtered_data.columns:
            filtered_data['timestamp'] = pd.to_datetime(filtered_data['timestamp'])
            
            if args.start_date:
                start_date = pd.to_datetime(args.start_date)
                filtered_data = filtered_data[filtered_data['timestamp'] >= start_date]
            
            if args.end_date:
                end_date = pd.to_datetime(args.end_date)
                filtered_data = filtered_data[filtered_data['timestamp'] <= end_date]
    
    return filtered_data

def _perform_analysis(data, args):
    """Perform the requested analysis."""
    if args.analysis == 'stats':
        return _statistical_analysis(data)
    elif args.analysis == 'correlation':
        return _correlation_analysis(data)
    elif args.analysis == 'trends':
        return _trend_analysis(data)
    elif args.analysis == 'volume':
        return _volume_analysis(data)
    else:
        raise ValueError(f"Unknown analysis type: {args.analysis}")

def _statistical_analysis(data):
    """Perform statistical analysis."""
    results = {}
    
    # Basic statistics
    results['basic_stats'] = data.describe()
    
    # Ticker statistics
    if 'ticker' in data.columns:
        ticker_stats = data.groupby('ticker').agg({
            'close': ['count', 'mean', 'std', 'min', 'max'],
            'vol': ['mean', 'sum'] if 'vol' in data.columns else []
        })
        results['ticker_stats'] = ticker_stats
    
    # Data quality
    results['data_quality'] = {
        'total_records': len(data),
        'missing_values': data.isnull().sum().to_dict(),
        'date_range': {
            'start': data['timestamp'].min() if 'timestamp' in data.columns else None,
            'end': data['timestamp'].max() if 'timestamp' in data.columns else None
        }
    }
    
    return results

def _correlation_analysis(data):
    """Perform correlation analysis."""
    numeric_columns = data.select_dtypes(include=['number']).columns
    correlation_matrix = data[numeric_columns].corr()
    
    return {
        'correlation_matrix': correlation_matrix,
        'high_correlations': _find_high_correlations(correlation_matrix)
    }

def _find_high_correlations(corr_matrix, threshold=0.7):
    """Find high correlations in the matrix."""
    high_corr = []
    
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            corr_value = corr_matrix.iloc[i, j]
            if abs(corr_value) >= threshold:
                high_corr.append({
                    'column1': corr_matrix.columns[i],
                    'column2': corr_matrix.columns[j],
                    'correlation': corr_value
                })
    
    return high_corr

def _trend_analysis(data):
    """Perform trend analysis."""
    results = {}
    
    if 'close' in data.columns and 'timestamp' in data.columns:
        # Sort by timestamp
        data_sorted = data.sort_values('timestamp')
        
        # Calculate price changes
        if 'ticker' in data.columns:
            for ticker in data['ticker'].unique():
                ticker_data = data_sorted[data_sorted['ticker'] == ticker]
                if len(ticker_data) > 1:
                    price_changes = ticker_data['close'].pct_change().dropna()
                    
                    results[ticker] = {
                        'avg_daily_change': price_changes.mean(),
                        'volatility': price_changes.std(),
                        'total_return': (ticker_data['close'].iloc[-1] / ticker_data['close'].iloc[0] - 1) * 100,
                        'positive_days': (price_changes > 0).sum(),
                        'negative_days': (price_changes < 0).sum()
                    }
        else:
            # Single ticker
            price_changes = data_sorted['close'].pct_change().dropna()
            results['overall'] = {
                'avg_daily_change': price_changes.mean(),
                'volatility': price_changes.std(),
                'total_return': (data_sorted['close'].iloc[-1] / data_sorted['close'].iloc[0] - 1) * 100,
                'positive_days': (price_changes > 0).sum(),
                'negative_days': (price_changes < 0).sum()
            }
    
    return results

def _volume_analysis(data):
    """Perform volume analysis."""
    results = {}
    
    if 'vol' in data.columns:
        results['volume_stats'] = {
            'total_volume': data['vol'].sum(),
            'average_volume': data['vol'].mean(),
            'median_volume': data['vol'].median(),
            'max_volume': data['vol'].max(),
            'min_volume': data['vol'].min()
        }
        
        # High volume days
        avg_volume = data['vol'].mean()
        high_volume_days = data[data['vol'] > avg_volume * 2]
        results['high_volume_days'] = {
            'count': len(high_volume_days),
            'percentage': (len(high_volume_days) / len(data)) * 100
        }
        
        # Volume by ticker
        if 'ticker' in data.columns:
            volume_by_ticker = data.groupby('ticker')['vol'].agg(['sum', 'mean', 'std'])
            results['volume_by_ticker'] = volume_by_ticker
    
    return results

def _output_results(results, args):
    """Output analysis results."""
    if args.output:
        # Save to file
        if args.format_out == 'csv':
            _save_results_csv(results, args.output)
        elif args.format_out == 'json':
            _save_results_json(results, args.output)
        else:
            _save_results_table(results, args.output)
    else:
        # Print to console
        _print_results_table(results)

def _save_results_csv(results, output_path):
    """Save results as CSV."""
    # This would need to be implemented based on the results structure
    print(f"CSV output not yet implemented for {output_path}")

def _save_results_json(results, output_path):
    """Save results as JSON."""
    import json
    
    # Convert results to JSON-serializable format
    json_results = {}
    for key, value in results.items():
        if isinstance(value, pd.DataFrame):
            json_results[key] = value.to_dict('records')
        else:
            json_results[key] = value
    
    with open(output_path, 'w') as f:
        json.dump(json_results, f, indent=2, default=str)
    
    print(f"Results saved to {output_path}")

def _save_results_table(results, output_path):
    """Save results as formatted table."""
    with open(output_path, 'w') as f:
        _print_results_table(results, file=f)
    
    print(f"Results saved to {output_path}")

def _print_results_table(results, file=None):
    """Print results in table format."""
    import sys
    output_file = file or sys.stdout
    
    for section_name, section_data in results.items():
        print(f"\n=== {section_name.upper()} ===", file=output_file)
        
        if isinstance(section_data, pd.DataFrame):
            print(section_data.to_string(), file=output_file)
        elif isinstance(section_data, dict):
            for key, value in section_data.items():
                if isinstance(value, pd.DataFrame):
                    print(f"\n{key}:", file=output_file)
                    print(value.to_string(), file=output_file)
                else:
                    print(f"{key}: {value}", file=output_file)
        else:
            print(str(section_data), file=output_file)

if __name__ == '__main__':
    main()
