"""
Analysis export routes for REDLINE Web GUI
Handles exporting analysis results
"""

from flask import Blueprint, request, jsonify
import logging
import pandas as pd
import os
import json
from datetime import datetime
from ..utils.analysis_helpers import flatten_dict

analysis_export_bp = Blueprint('analysis_export', __name__)
logger = logging.getLogger(__name__)


@analysis_export_bp.route('/export-analysis', methods=['POST'])
def export_analysis():
    """Export analysis results to file."""
    try:
        data = request.get_json()
        analysis_result = data.get('analysis_result')
        filename = data.get('filename', 'analysis_results')
        export_format = data.get('format', 'json')
        
        if not analysis_result:
            return jsonify({'error': 'No analysis result provided'}), 400
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if export_format == 'json':
            export_filename = f"{filename}_{timestamp}.json"
            export_path = os.path.join(os.getcwd(), 'data', 'analysis', export_filename)
            os.makedirs(os.path.dirname(export_path), exist_ok=True)
            
            with open(export_path, 'w') as f:
                json.dump(analysis_result, f, indent=2, default=str)
        
        elif export_format == 'csv':
            # Try to convert analysis to DataFrame if possible
            export_filename = f"{filename}_{timestamp}.csv"
            export_path = os.path.join(os.getcwd(), 'data', 'analysis', export_filename)
            os.makedirs(os.path.dirname(export_path), exist_ok=True)
            
            # Create a flattened version of the analysis for CSV export
            flattened_data = []
            flatten_dict(analysis_result, flattened_data)
            
            if flattened_data:
                df = pd.DataFrame(flattened_data)
                df.to_csv(export_path, index=False)
            else:
                return jsonify({'error': 'Cannot export analysis to CSV format'}), 400
        
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

