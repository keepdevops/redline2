#!/usr/bin/env python3
"""
Conversion Logic Helper for ConverterTab
Handles the actual conversion process and data processing.
"""

import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd

from ...core.schema import FORMAT_DIALOG_INFO

logger = logging.getLogger(__name__)


class ConversionLogicHelper:
    """Helper class for conversion logic in ConverterTab."""
    
    def __init__(self, converter_tab):
        """Initialize with reference to ConverterTab."""
        self.converter_tab = converter_tab
        self.logger = logging.getLogger(__name__)
    
    def _single_conversion_worker(self):
        """Single file conversion worker."""
        total_files = len(self.converter_tab.input_files)
        
        for i, input_file in enumerate(self.converter_tab.input_files):
            if self.converter_tab.stop_event.is_set():
                break
                
            try:
                # Update progress
                progress = (i / total_files) * 100
                self.converter_tab.main_window.run_in_main_thread(
                    lambda p=progress: self.converter_tab.progress_var.set(p)
                )
                
                self.converter_tab.main_window.run_in_main_thread(
                    lambda f=input_file: self.converter_tab.status_label.config(text=f"Converting: {os.path.basename(f)}")
                )
                
                # Perform conversion
                output_file = self.convert_single_file(input_file)
                
                if output_file:
                    self.converter_tab.converted_files.append(output_file)
                    
                    # Add to results
                    self.converter_tab.main_window.run_in_main_thread(
                        lambda: self.add_conversion_result(
                            input_file, self.converter_tab.input_format_var.get(),
                            self.converter_tab.output_format_var.get(), "Success", output_file
                        )
                    )
                    
            except Exception as e:
                error_msg = str(e)
                self.logger.error(f"Error converting {input_file}: {error_msg}")
                self.converter_tab.main_window.run_in_main_thread(
                    lambda: self.add_conversion_result(
                        input_file, self.converter_tab.input_format_var.get(),
                        self.converter_tab.output_format_var.get(), f"Error: {error_msg}", ""
                    )
                )
    
    def _batch_conversion_worker(self):
        """Batch conversion worker with parallel processing."""
        import glob
        
        batch_dir = self.converter_tab.batch_dir_var.get()
        pattern = self.converter_tab.file_pattern_var.get()
        
        # Find files matching pattern
        search_pattern = os.path.join(batch_dir, pattern)
        files = glob.glob(search_pattern)
        
        if not files:
            raise ValueError(f"No files found matching pattern: {search_pattern}")
            
        total_files = len(files)
        
        # Use parallel processing for batch conversion
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all conversion tasks
            future_to_file = {
                executor.submit(self.convert_single_file, file): file
                for file in files
            }
            
            # Process completed conversions
            completed = 0
            for future in as_completed(future_to_file):
                if self.converter_tab.stop_event.is_set():
                    break
                    
                input_file = future_to_file[future]
                try:
                    output_file = future.result()
                    completed += 1
                    
                    # Update progress
                    progress = (completed / total_files) * 100
                    self.converter_tab.main_window.run_in_main_thread(
                        lambda p=progress: self.converter_tab.progress_var.set(p)
                    )
                
                    if output_file:
                        self.converter_tab.converted_files.append(output_file)
                        
                        # Add to results
                        self.converter_tab.main_window.run_in_main_thread(
                            lambda: self.add_conversion_result(
                                input_file, self.converter_tab.input_format_var.get(),
                                self.converter_tab.output_format_var.get(), "Success", output_file
                            )
                        )
                        
                except Exception as e:
                    error_msg = str(e)
                    self.logger.error(f"Error converting {input_file}: {error_msg}")
                    self.converter_tab.main_window.run_in_main_thread(
                        lambda: self.add_conversion_result(
                            input_file, self.converter_tab.input_format_var.get(),
                            self.converter_tab.output_format_var.get(), f"Error: {error_msg}", ""
                        )
                    )
    
    def convert_single_file(self, input_file: str, input_format: str = None) -> str:
        """Convert a single file."""
        if input_format is None:
            input_format = self.converter_tab.input_format_var.get()
            
        output_format = self.converter_tab.output_format_var.get()
        
        # Generate output filename
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_ext = FORMAT_DIALOG_INFO[output_format][0]  # First element is extension
        output_filename = f"{base_name}_converted{output_ext}"
        
        # Create output directory
        output_dir = self.converter_tab.output_dir_var.get()
        if self.converter_tab.create_subdir_var.get():
            output_dir = os.path.join(output_dir, output_format)
            
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, output_filename)
        
        # Check if file exists
        if os.path.exists(output_file) and not self.converter_tab.overwrite_var.get():
            # Instead of raising an error, skip the file and log a warning
            self.logger.warning(f"Skipping {input_file}: Output file already exists: {output_file}")
            return f"Skipped: File already exists"
            
        # Load input data
        data = self.converter_tab.loader.load_file_by_type(input_file, input_format)
        
        # Apply data cleaning options
        if self.converter_tab.remove_duplicates_var.get():
            data = data.drop_duplicates()
            
        if self.converter_tab.fill_missing_var.get():
            data = data.fillna(method='ffill').fillna(method='bfill')
            
        if self.converter_tab.normalize_dates_var.get():
            # Try to normalize date columns
            date_cols = ['date', 'timestamp', '<DATE>', '<TIME>']
            for col in date_cols:
                if col in data.columns:
                    try:
                        data[col] = pd.to_datetime(data[col], utc=True)
                    except:
                        pass
                        
        if self.converter_tab.standardize_columns_var.get():
            # Standardize column names
            data.columns = [col.strip().replace(' ', '_').replace('<', '').replace('>', '') 
                           for col in data.columns]
                           
        if self.converter_tab.validate_data_var.get():
            # Basic validation
            if data.empty:
                raise ValueError("Data is empty after processing")
                
        # Save output data
        self.converter_tab.converter.save_file_by_type(data, output_file, output_format)
        
        return output_file
    
    def add_conversion_result(self, input_file: str, input_format: str, 
                             output_format: str, status: str, output_file: str):
        """Add conversion result to results tree."""
        self.converter_tab.results_tree.insert('', 'end', values=(
            os.path.basename(input_file),
            input_format,
            output_format,
            status,
            os.path.basename(output_file) if output_file else ""
        ))


