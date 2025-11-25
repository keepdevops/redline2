"""
ML Data Preparation routes for REDLINE Web GUI
Handles ML/RL training data preparation in numpy and tensorflow formats
"""

from flask import Blueprint, request, jsonify
import logging
from ..utils.data_helpers import clean_dataframe_columns
from ..utils.data_loaders import load_data_file
from ..utils.ml_data_prep import prepare_ml_features, prepare_ml_data_array, prepare_rl_state
from ..utils.ml_formats import convert_to_numpy_format, convert_to_tensorflow_dataset, convert_to_tensorflow_tensor

analysis_ml_bp = Blueprint('analysis_ml', __name__)
logger = logging.getLogger(__name__)


@analysis_ml_bp.route('/prepare-ml-data', methods=['POST'])
def prepare_ml_data():
    """Prepare data for ML/RL training in specified format."""
    try:
        data = request.get_json()
        filename = data.get('filename')
        format_type = data.get('format', 'numpy')  # numpy, tensorflow
        file_path_hint = data.get('file_path')
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        # Load data file
        try:
            df = load_data_file(filename, file_path_hint)
        except FileNotFoundError as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            logger.error(f"Error loading file: {str(e)}")
            return jsonify({'error': f'Error loading file: {str(e)}'}), 500
        
        # Prepare features
        selected_features = data.get('features', [])
        try:
            df = prepare_ml_features(df, selected_features if selected_features else None)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        
        # Prepare data array
        try:
            data_array = prepare_ml_data_array(df)
        except (ValueError, ImportError) as e:
            return jsonify({'error': str(e)}), 400
        
        # Convert to requested format
        try:
            if format_type == 'numpy':
                result = convert_to_numpy_format(data_array)
            elif format_type == 'tensorflow':
                result = convert_to_tensorflow_dataset(data_array)
            else:
                return jsonify({'error': f'Unsupported format: {format_type}'}), 400
        except ImportError as e:
            return jsonify({'error': str(e)}), 500
        except Exception as e:
            logger.error(f"Error converting to {format_type} format: {str(e)}")
            return jsonify({'error': f'Error converting to {format_type} format: {str(e)}'}), 500
        
        return jsonify({
            'filename': filename,
            'format': format_type,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Error preparing ML data: {str(e)}")
        return jsonify({'error': str(e)}), 500


@analysis_ml_bp.route('/prepare-rl-state', methods=['POST'])
def prepare_rl_state_route():
    """Prepare reinforcement learning state from data."""
    try:
        data = request.get_json()
        filename = data.get('filename')
        portfolio = data.get('portfolio', {})
        format_type = data.get('format', 'numpy')  # numpy, tensorflow
        file_path_hint = data.get('file_path')
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        # Load data file
        try:
            df = load_data_file(filename, file_path_hint)
        except FileNotFoundError as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            logger.error(f"Error loading file: {str(e)}")
            return jsonify({'error': f'Error loading file: {str(e)}'}), 500
        
        # Prepare RL state
        try:
            state_array = prepare_rl_state(df)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        
        # Convert to requested format
        try:
            if format_type == 'numpy':
                result = convert_to_numpy_format(state_array)
            elif format_type == 'tensorflow':
                result = convert_to_tensorflow_tensor(state_array)
            else:
                return jsonify({'error': f'Unsupported format: {format_type}'}), 400
        except ImportError as e:
            return jsonify({'error': str(e)}), 500
        except Exception as e:
            logger.error(f"Error converting to {format_type} format: {str(e)}")
            return jsonify({'error': f'Error converting to {format_type} format: {str(e)}'}), 500
        
        return jsonify({
            'filename': filename,
            'format': format_type,
            'portfolio': portfolio,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Error preparing RL state: {str(e)}")
        return jsonify({'error': str(e)}), 500



