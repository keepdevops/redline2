#!/usr/bin/env python3
"""
Filter Logic Helper for FilterDialog
Handles filter application and data processing logic.
"""

import logging
import pandas as pd
from typing import Optional
import tkinter as tk

logger = logging.getLogger(__name__)


class FilterLogicHelper:
    """Helper class for filter application logic in FilterDialog."""
    
    def __init__(self, filter_dialog):
        """Initialize with reference to FilterDialog."""
        self.filter_dialog = filter_dialog
        self.logger = logging.getLogger(__name__)
    
    def apply_filters_to_data(self, data: pd.DataFrame, preview: bool = False) -> Optional[pd.DataFrame]:
        """Apply all filters to data."""
        filtered_data = data.copy()
        
        try:
            # Date range filter - try multiple possible date column names
            date_cols = ['date', 'timestamp', '<DATE>', '<TIME>', 'Date', 'Timestamp', 'DATE', 'TIME']
            date_col = None
            for col in date_cols:
                if col in filtered_data.columns:
                    date_col = col
                    break
            
            # If no standard date column found, try to find any column that looks like dates
            if not date_col:
                for col in filtered_data.columns:
                    if any(keyword in col.lower() for keyword in ['date', 'time', 'timestamp']):
                        date_col = col
                        break
                    
            if date_col:
                start_date = self.filter_dialog.start_date_var.get().strip()
                end_date = self.filter_dialog.end_date_var.get().strip()
                
                self.logger.info(f"Using date column: {date_col}")
                self.logger.info(f"Date column type: {filtered_data[date_col].dtype}")
                
                if start_date:
                    try:
                        start_dt = pd.to_datetime(start_date)
                        
                        # Handle different date column formats
                        if date_col == '<DATE>' and pd.api.types.is_numeric_dtype(filtered_data[date_col]):
                            # Stooq format: YYYYMMDD as integer
                            start_str = start_dt.strftime('%Y%m%d')
                            start_int = int(start_str)
                            filtered_data = filtered_data[filtered_data[date_col] >= start_int]
                            self.logger.info(f"Applied start date filter (Stooq format): {start_date} -> {start_int}")
                        else:
                            # Standard format: convert to datetime if needed
                            if not pd.api.types.is_datetime64_any_dtype(filtered_data[date_col]):
                                filtered_data[date_col] = pd.to_datetime(filtered_data[date_col])
                            filtered_data = filtered_data[filtered_data[date_col] >= start_dt]
                            self.logger.info(f"Applied start date filter (standard format): {start_date}")
                    except Exception as e:
                        self.logger.warning(f"Failed to apply start date filter: {str(e)}")
                        
                if end_date:
                    try:
                        end_dt = pd.to_datetime(end_date)
                        
                        # Handle different date column formats
                        if date_col == '<DATE>' and pd.api.types.is_numeric_dtype(filtered_data[date_col]):
                            # Stooq format: YYYYMMDD as integer
                            end_str = end_dt.strftime('%Y%m%d')
                            end_int = int(end_str)
                            filtered_data = filtered_data[filtered_data[date_col] <= end_int]
                            self.logger.info(f"Applied end date filter (Stooq format): {end_date} -> {end_int}")
                        else:
                            # Standard format: convert to datetime if needed
                            if not pd.api.types.is_datetime64_any_dtype(filtered_data[date_col]):
                                filtered_data[date_col] = pd.to_datetime(filtered_data[date_col])
                            filtered_data = filtered_data[filtered_data[date_col] <= end_dt]
                            self.logger.info(f"Applied end date filter (standard format): {end_date}")
                    except Exception as e:
                        self.logger.warning(f"Failed to apply end date filter: {str(e)}")
            else:
                self.logger.warning("No date column found for filtering")
                        
            # Numeric filters
            numeric_columns = data.select_dtypes(include=['number']).columns
            for column in numeric_columns:
                min_val = self.filter_dialog.filters.get(f"{column}_min", tk.StringVar()).get().strip()
                max_val = self.filter_dialog.filters.get(f"{column}_max", tk.StringVar()).get().strip()
                
                if min_val:
                    try:
                        filtered_data = filtered_data[filtered_data[column] >= float(min_val)]
                    except:
                        pass
                        
                if max_val:
                    try:
                        filtered_data = filtered_data[filtered_data[column] <= float(max_val)]
                    except:
                        pass
                        
            # Text filters
            text_columns = data.select_dtypes(include=['object', 'string']).columns
            for column in text_columns:
                contains_val = self.filter_dialog.filters.get(f"{column}_contains", tk.StringVar()).get().strip()
                exact_val = self.filter_dialog.filters.get(f"{column}_exact", tk.StringVar()).get().strip()
                
                if contains_val:
                    filtered_data = filtered_data[filtered_data[column].astype(str).str.contains(contains_val, case=False, na=False)]
                    
                if exact_val:
                    filtered_data = filtered_data[filtered_data[column].astype(str) == exact_val]
                    
            # Custom filter
            try:
                custom_filter = self.filter_dialog.custom_filter_entry.get(1.0, tk.END).strip()
                if custom_filter and custom_filter.strip():
                    # Apply advanced custom filter
                    filtered_data = self._apply_custom_filter(filtered_data, custom_filter)
                    self.logger.info(f"Applied custom filter successfully")
                        
            except Exception as e:
                error_msg = f"Error applying custom filter: {str(e)}"
                self.logger.error(error_msg)
                if not preview:
                    raise Exception(error_msg)
                return None
                    
            # Row limit
            if not preview:
                try:
                    limit = int(self.filter_dialog.row_limit_var.get())
                    if limit > 0:
                        filtered_data = filtered_data.head(limit)
                except:
                    pass
                    
            return filtered_data
            
        except Exception as e:
            if preview:
                return None
            raise e
    
    def _apply_custom_filter(self, data: pd.DataFrame, filter_expression: str) -> pd.DataFrame:
        """
        Apply advanced custom filter with support for multi-line expressions and complex logic.
        
        Args:
            data: DataFrame to filter
            filter_expression: Multi-line filter expression
            
        Returns:
            Filtered DataFrame
        """
        try:
            # Create a copy of the data to work with
            df = data.copy()
            
            # Log the input data info
            self.logger.info(f"Custom filter input: {len(df)} rows, columns: {list(df.columns)}")
            self.logger.info(f"Filter expression: {repr(filter_expression)}")
            
            # Map standard column names to Stooq format if needed
            column_mapping = {
                'close': '<CLOSE>',
                'volume': '<VOL>',
                'vol': '<VOL>',  # Support both 'volume' and 'vol'
                'ticker': '<TICKER>',
                'high': '<HIGH>',
                'low': '<LOW>',
                'open': '<OPEN>',
                'date': '<DATE>',
                'time': '<TIME>'
            }
            
            # Create reverse mapping for display
            reverse_mapping = {v: k for k, v in column_mapping.items()}
            
            # Parse the filter expression line by line
            lines = [line.strip() for line in filter_expression.split('\n') if line.strip()]
            
            self.logger.info(f"Parsed {len(lines)} filter lines: {lines}")
            
            if not lines:
                return data
            
            # Initialize mask as all True
            mask = pd.Series([True] * len(df), index=df.index)
            
            # Process each line as a separate condition
            for i, line in enumerate(lines):
                # Translate column names in the expression
                translated_line = self._translate_column_names(line, df.columns, column_mapping)
                try:
                    # Use the translated line for evaluation
                    line_to_eval = translated_line
                    
                    # Try to evaluate the entire line as a single expression first
                    # This handles complex expressions like 'vol > vol.mean()' and '(high - low)/close > 0.05'
                    try:
                        # Special handling for expressions with method calls like .mean()
                        if '.mean()' in line_to_eval or '.median()' in line_to_eval or '.std()' in line_to_eval:
                            # These need to be evaluated as a single expression
                            line_mask = df.eval(line_to_eval)
                        else:
                            line_mask = df.eval(line_to_eval)
                        
                        mask = mask & line_mask
                        self.logger.info(f"Applied condition {i+1}: {line} -> {line_to_eval}")
                        continue
                    except Exception as eval_error:
                        self.logger.info(f"Complex eval failed for '{line}', trying simple parsing: {str(eval_error)}")
                    
                    # Fall back to simple condition parsing
                    if '==' in line_to_eval and '!=' not in line_to_eval:
                        # Equality condition
                        parts = line_to_eval.split('==')
                        if len(parts) == 2:
                            col = parts[0].strip()
                            value = parts[1].strip()
                            # Handle string values
                            if value.startswith("'") and value.endswith("'"):
                                value = value[1:-1]
                                line_mask = df[col] == value
                            elif value.replace('.', '').replace('-', '').isdigit():
                                value = float(value)
                                line_mask = df[col] == value
                            else:
                                # Try to evaluate as expression
                                line_mask = df.eval(f"{col} == {value}")
                            mask = mask & line_mask
                    
                    elif '>' in line_to_eval and '>=' not in line_to_eval:
                        # Greater than condition - try simple parsing
                        parts = line_to_eval.split('>')
                        if len(parts) == 2:
                            left = parts[0].strip()
                            right = parts[1].strip()
                            line_mask = df.eval(f"{left} > {right}")
                            mask = mask & line_mask
                    
                    elif '>=' in line_to_eval:
                        # Greater than or equal condition
                        line_mask = df.eval(line_to_eval)
                        mask = mask & line_mask
                    
                    elif '<' in line_to_eval and '<=' not in line_to_eval:
                        # Less than condition
                        line_mask = df.eval(line_to_eval)
                        mask = mask & line_mask
                    
                    elif '<=' in line_to_eval:
                        # Less than or equal condition
                        line_mask = df.eval(line_to_eval)
                        mask = mask & line_mask
                    
                    elif '!=' in line_to_eval:
                        # Not equal condition
                        line_mask = df.eval(line_to_eval)
                        mask = mask & line_mask
                    
                    else:
                        # Last resort: try to evaluate as a general expression
                        line_mask = df.eval(line_to_eval)
                        mask = mask & line_mask
                    
                    self.logger.info(f"Applied condition {i+1}: {line} -> {line_to_eval}")
                    
                except Exception as line_error:
                    self.logger.error(f"Error processing line '{line}': {str(line_error)}")
                    raise Exception(f"Invalid filter condition: {line}")
            
            # Apply the combined mask
            filtered_df = df[mask]
            
            self.logger.info(f"Custom filter applied: {len(data)} rows -> {len(filtered_df)} rows")
            return filtered_df
            
        except Exception as e:
            self.logger.error(f"Error in custom filter application: {str(e)}")
            raise Exception(f"Custom filter error: {str(e)}")
    
    def _translate_column_names(self, expression: str, available_columns: list, column_mapping: dict) -> str:
        """
        Translate standard column names to actual column names in the DataFrame.
        
        Args:
            expression: Filter expression
            available_columns: List of available columns in the DataFrame
            column_mapping: Mapping from standard names to actual names
            
        Returns:
            Translated expression
        """
        try:
            translated = expression
            
            # Check if we need to translate (i.e., if standard names are used but Stooq columns exist)
            has_stooq_columns = any(col.startswith('<') and col.endswith('>') for col in available_columns)
            uses_standard_names = any(std_name in expression for std_name in column_mapping.keys())
            
            if has_stooq_columns and uses_standard_names:
                # Translate standard column names to Stooq format
                for std_name, stooq_name in column_mapping.items():
                    if std_name in expression and stooq_name in available_columns:
                        # Replace column names in the expression
                        # Use word boundaries to avoid partial replacements
                        import re
                        pattern = r'\b' + re.escape(std_name) + r'\b'
                        translated = re.sub(pattern, stooq_name, translated)
                        self.logger.info(f"Translated '{std_name}' to '{stooq_name}' in expression")
            
            return translated
            
        except Exception as e:
            self.logger.warning(f"Error translating column names: {str(e)}")
            return expression

