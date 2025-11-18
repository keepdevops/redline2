"""
Shared data helper functions for REDLINE Web GUI.
Extracted to avoid circular dependencies.
"""

import pandas as pd


def clean_dataframe_columns(df):
    """Clean up malformed CSV headers - remove unnamed/empty columns."""
    columns_to_drop = []
    cleaned_columns = []
    
    for i, col in enumerate(df.columns):
        # Drop columns with empty names or typical pandas unnamed column patterns
        if (col == '' or 
            str(col).strip() == '' or 
            str(col).startswith('Unnamed:') or
            (str(col) == '0' and i == 0 and len(df.columns) > 1)):  # First column named '0' usually indicates index issue
            columns_to_drop.append(col)
        else:
            # Clean column name
            clean_col = str(col).strip()
            # If still empty after cleaning, give it a meaningful name
            if clean_col == '':
                clean_col = f'Column_{i}'
            cleaned_columns.append(clean_col)
    
    # Drop the problematic columns
    if columns_to_drop:
        df = df.drop(columns=columns_to_drop)
        
    # Rename columns to cleaned versions
    if len(cleaned_columns) == len(df.columns):
        df.columns = cleaned_columns
        
    return df

