"""
Analysis export routes for REDLINE Web GUI
Handles exporting analysis results to all supported formats
"""

from flask import Blueprint, request, jsonify, send_file
import logging
import pandas as pd
import os
import json
import numpy as np
from datetime import datetime
from ..utils.analysis_helpers import flatten_dict

analysis_export_bp = Blueprint('analysis_export', __name__)
logger = logging.getLogger(__name__)


def _convert_analysis_to_dataframe(analysis_result):
    """Convert analysis result to DataFrame for export."""
    flattened_data = []
    flatten_dict(analysis_result, flattened_data)
    if flattened_data:
        return pd.DataFrame(flattened_data)
    return None


@analysis_export_bp.route('/export-analysis', methods=['POST'])
def export_analysis():
    """Export analysis results to all supported formats."""
    try:
        data = request.get_json()
        analysis_result = data.get('analysis_result')
        filename = data.get('filename', 'analysis_results')
        export_format = data.get('format', 'json').lower()
        
        if not analysis_result:
            return jsonify({'error': 'No analysis result provided'}), 400
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_dir = os.path.join(os.getcwd(), 'data', 'analysis')
        os.makedirs(export_dir, exist_ok=True)
        
        # Format-specific extensions
        format_extensions = {
            'json': '.json', 'csv': '.csv', 'parquet': '.parquet',
            'feather': '.feather', 'duckdb': '.duckdb', 'txt': '.txt',
            'npz': '.npz', 'tensorflow': '.npz', 'arrow': '.arrow', 'pyarrow': '.arrow'
        }
        
        ext = format_extensions.get(export_format, '.json')
        export_filename = f"{filename}_{timestamp}{ext}"
        export_path = os.path.join(export_dir, export_filename)
        
        # Convert to DataFrame for structured formats
        df = _convert_analysis_to_dataframe(analysis_result)
        
        # Export based on format
        if export_format == 'json':
            with open(export_path, 'w') as f:
                json.dump(analysis_result, f, indent=2, default=str)
        
        elif export_format == 'csv':
            if df is not None:
                df.to_csv(export_path, index=False)
            else:
                return jsonify({'error': 'Cannot export analysis to CSV format'}), 400
        
        elif export_format == 'parquet':
            if df is not None:
                df.to_parquet(export_path, index=False)
            else:
                return jsonify({'error': 'Cannot export analysis to Parquet format'}), 400
        
        elif export_format == 'feather':
            if df is not None:
                df.to_feather(export_path)
            else:
                return jsonify({'error': 'Cannot export analysis to Feather format'}), 400
        
        elif export_format == 'duckdb':
            if df is not None:
                import duckdb
                conn = duckdb.connect(export_path)
                conn.register('analysis_data', df)
                conn.execute("CREATE TABLE IF NOT EXISTS analysis_results AS SELECT * FROM analysis_data")
                conn.unregister('analysis_data')
                conn.close()
            else:
                return jsonify({'error': 'Cannot export analysis to DuckDB format'}), 400
        
        elif export_format == 'txt':
            if df is not None:
                df.to_csv(export_path, sep='\t', index=False)
            else:
                return jsonify({'error': 'Cannot export analysis to TXT format'}), 400
        
        elif export_format in ('npz', 'tensorflow'):
            if df is not None:
                # Save with column names preserved
                np.savez(export_path,
                        data=df.to_numpy(),
                        columns=np.array(df.columns.tolist(), dtype=object))
            else:
                return jsonify({'error': 'Cannot export analysis to NPZ format'}), 400
        
        elif export_format in ('arrow', 'pyarrow'):
            if df is not None:
                try:
                    import pyarrow as pa
                    table = pa.Table.from_pandas(df)
                    with pa.OSFile(export_path, 'wb') as sink:
                        with pa.ipc.new_file(sink, table.schema) as writer:
                            writer.write_table(table)
                except ImportError:
                    return jsonify({'error': 'PyArrow is required for Arrow format'}), 400
            else:
                return jsonify({'error': 'Cannot export analysis to Arrow format'}), 400
        
        else:
            return jsonify({'error': f'Unsupported export format: {export_format}'}), 400
        
        file_stat = os.stat(export_path)
        
        return jsonify({
            'message': 'Analysis exported successfully',
            'export_filename': export_filename,
            'export_path': export_path,
            'file_size': file_stat.st_size,
            'format': export_format
        })
        
    except Exception as e:
        logger.error(f"Error exporting analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

