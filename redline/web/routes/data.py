"""
Data tab routes for REDLINE Web GUI
Handles data viewing, filtering, and management
"""

from flask import Blueprint, render_template, request, jsonify
import logging
import os
import pandas as pd

data_bp = Blueprint('data', __name__)
logger = logging.getLogger(__name__)

@data_bp.route('/')
def data_tab():
    """Data tab main page."""
    return render_template('data_tab.html')

@data_bp.route('/load', methods=['POST'])
def load_data():
    """Load data from file."""
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        data_path = os.path.join(os.getcwd(), 'data', filename)
        
        if not os.path.exists(data_path):
            return jsonify({'error': 'File not found'}), 404
        
        from redline.core.format_converter import FormatConverter
        converter = FormatConverter()
        
        df = converter.load_file(data_path)
        
        if not isinstance(df, pd.DataFrame):
            return jsonify({'error': 'Invalid data format'}), 400
        
        # Convert to JSON-serializable format
        data_dict = {
            'columns': list(df.columns),
            'data': df.head(1000).to_dict('records'),  # Limit to 1000 rows for web display
            'total_rows': len(df),
            'dtypes': df.dtypes.astype(str).to_dict(),
            'filename': filename
        }
        
        return jsonify(data_dict)
        
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@data_bp.route('/filter', methods=['POST'])
def filter_data():
    """Apply filters to loaded data."""
    try:
        data = request.get_json()
        filename = data.get('filename')
        filters = data.get('filters', {})
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        data_path = os.path.join(os.getcwd(), 'data', filename)
        
        from redline.core.format_converter import FormatConverter
        converter = FormatConverter()
        
        df = converter.load_file(data_path)
        
        if not isinstance(df, pd.DataFrame):
            return jsonify({'error': 'Invalid data format'}), 400
        
        # Apply filters
        filtered_df = df.copy()
        
        for column, filter_config in filters.items():
            if column in filtered_df.columns:
                filter_type = filter_config.get('type')
                filter_value = filter_config.get('value')
                
                if filter_type == 'equals':
                    filtered_df = filtered_df[filtered_df[column] == filter_value]
                elif filter_type == 'contains':
                    filtered_df = filtered_df[filtered_df[column].astype(str).str.contains(str(filter_value), na=False)]
                elif filter_type == 'greater_than':
                    filtered_df = filtered_df[filtered_df[column] > filter_value]
                elif filter_type == 'less_than':
                    filtered_df = filtered_df[filtered_df[column] < filter_value]
                elif filter_type == 'date_range':
                    if 'start' in filter_value and 'end' in filter_value:
                        filtered_df = filtered_df[
                            (filtered_df[column] >= filter_value['start']) &
                            (filtered_df[column] <= filter_value['end'])
                        ]
        
        # Convert to JSON-serializable format
        data_dict = {
            'columns': list(filtered_df.columns),
            'data': filtered_df.head(1000).to_dict('records'),
            'total_rows': len(filtered_df),
            'original_rows': len(df),
            'filters_applied': len(filters)
        }
        
        return jsonify(data_dict)
        
    except Exception as e:
        logger.error(f"Error filtering data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@data_bp.route('/columns/<filename>')
def get_columns(filename):
    """Get column information for a file."""
    try:
        data_path = os.path.join(os.getcwd(), 'data', filename)
        
        if not os.path.exists(data_path):
            return jsonify({'error': 'File not found'}), 404
        
        from redline.core.format_converter import FormatConverter
        converter = FormatConverter()
        
        df = converter.load_file(data_path)
        
        if not isinstance(df, pd.DataFrame):
            return jsonify({'error': 'Invalid data format'}), 400
        
        columns_info = []
        for col in df.columns:
            col_info = {
                'name': col,
                'dtype': str(df[col].dtype),
                'non_null_count': df[col].count(),
                'null_count': df[col].isnull().sum(),
                'unique_count': df[col].nunique()
            }
            
            # Add sample values for preview
            sample_values = df[col].dropna().head(5).tolist()
            col_info['sample_values'] = sample_values
            
            columns_info.append(col_info)
        
        return jsonify({
            'columns': columns_info,
            'total_columns': len(df.columns),
            'total_rows': len(df)
        })
        
    except Exception as e:
        logger.error(f"Error getting columns for {filename}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@data_bp.route('/export', methods=['POST'])
def export_data():
    """Export filtered data to file."""
    try:
        data = request.get_json()
        filename = data.get('filename')
        export_format = data.get('format', 'csv')
        export_filename = data.get('export_filename')
        filters = data.get('filters', {})
        
        if not all([filename, export_filename]):
            return jsonify({'error': 'Missing required parameters'}), 400
        
        data_path = os.path.join(os.getcwd(), 'data', filename)
        export_path = os.path.join(os.getcwd(), 'data', export_filename)
        
        from redline.core.format_converter import FormatConverter
        converter = FormatConverter()
        
        df = converter.load_file(data_path)
        
        # Apply filters if provided
        if filters:
            filtered_df = df.copy()
            for column, filter_config in filters.items():
                if column in filtered_df.columns:
                    filter_type = filter_config.get('type')
                    filter_value = filter_config.get('value')
                    
                    if filter_type == 'equals':
                        filtered_df = filtered_df[filtered_df[column] == filter_value]
                    elif filter_type == 'contains':
                        filtered_df = filtered_df[filtered_df[column].astype(str).str.contains(str(filter_value), na=False)]
                    elif filter_type == 'greater_than':
                        filtered_df = filtered_df[filtered_df[column] > filter_value]
                    elif filter_type == 'less_than':
                        filtered_df = filtered_df[filtered_df[column] < filter_value]
            
            df = filtered_df
        
        # Save in requested format
        converter.save_file_by_type(df, export_path, export_format)
        
        return jsonify({
            'message': 'Data exported successfully',
            'export_filename': export_filename,
            'records_exported': len(df)
        })
        
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}")
        return jsonify({'error': str(e)}), 500
