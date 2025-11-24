"""
ML Data Preparation routes for REDLINE Web GUI
Handles ML/RL training data preparation in numpy and tensorflow formats
"""

from flask import Blueprint, request, jsonify
import logging
import pandas as pd
import os
from ..utils.data_helpers import clean_dataframe_columns

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
        
        from redline.core.format_converter import FormatConverter
        from redline.core.schema import EXT_TO_FORMAT
        
        converter = FormatConverter()
        
        # Find file (same logic as analysis endpoint)
        data_dir = os.path.join(os.getcwd(), 'data')
        data_path = None
        
        if file_path_hint and os.path.exists(file_path_hint):
            data_path = file_path_hint
        else:
            search_paths = [
                os.path.join(data_dir, filename),
                os.path.join(data_dir, 'stooq', filename),
                os.path.join(data_dir, 'downloaded', filename),
                os.path.join(data_dir, 'uploads', filename)
            ]
            
            converted_dir = os.path.join(data_dir, 'converted')
            if os.path.exists(converted_dir):
                for root, dirs, files in os.walk(converted_dir):
                    if filename in files:
                        search_paths.append(os.path.join(root, filename))
            
            for path in search_paths:
                if os.path.exists(path):
                    data_path = path
                    break
        
        if not data_path or not os.path.exists(data_path):
            return jsonify({'error': f'File not found: {filename}'}), 404
        
        # Load data
        ext = os.path.splitext(data_path)[1].lower()
        format_type_file = EXT_TO_FORMAT.get(ext, 'csv')
        
        if format_type_file == 'csv':
            df = pd.read_csv(data_path)
        elif format_type_file == 'parquet':
            df = pd.read_parquet(data_path)
        elif format_type_file == 'feather':
            df = pd.read_feather(data_path)
        elif format_type_file == 'json':
            df = pd.read_json(data_path)
        elif format_type_file == 'duckdb':
            import duckdb
            conn = duckdb.connect(data_path)
            df = conn.execute("SELECT * FROM tickers_data").fetchdf()
            conn.close()
        elif format_type_file in ('tensorflow', 'npz'):
            import numpy as np
            # Use allow_pickle=True for .npz files that may contain object arrays
            loaded = np.load(data_path, allow_pickle=True)
            if 'data' in loaded:
                data_array = loaded['data']
                # Restore column names if they were saved
                if 'columns' in loaded:
                    columns = loaded['columns'].tolist()
                    df = pd.DataFrame(data_array, columns=columns)
                else:
                    # Fallback: create generic column names
                    df = pd.DataFrame(data_array, columns=[f'col_{i}' for i in range(data_array.shape[1])])
            else:
                first_key = list(loaded.keys())[0]
                df = pd.DataFrame(loaded[first_key])
        elif format_type_file == 'txt':
            # Handle TXT files (Stooq format or tab-separated)
            try:
                # Try reading as CSV first (Stooq format uses commas)
                df = pd.read_csv(data_path)
            except:
                # Try different separators for TXT files
                for sep in ['\t', ';', ' ', '|']:
                    try:
                        df = pd.read_csv(data_path, sep=sep)
                        break
                    except:
                        continue
                else:
                    # If all separators fail, try reading as fixed-width
                    df = pd.read_fwf(data_path)
        elif format_type_file in ('keras', 'h5'):
            return jsonify({'error': 'Keras model files (.h5) cannot be used for ML data preparation. Use the Analysis tab for model operations.'}), 400
        elif format_type_file in ('pyarrow', 'arrow'):
            try:
                import pyarrow as pa
                with pa.ipc.open_file(data_path) as reader:
                    df = reader.read_all().to_pandas()
            except ImportError:
                return jsonify({'error': 'PyArrow is required to load .arrow files'}), 400
            except Exception as e:
                return jsonify({'error': f'Error loading Arrow file: {str(e)}'}), 400
        else:
            df = converter.load_file_by_type(data_path, format_type_file)
        
        if not isinstance(df, pd.DataFrame):
            return jsonify({'error': 'Invalid data format'}), 400
        
        df = clean_dataframe_columns(df)
        
        # Get selected features if provided
        selected_features = data.get('features', [])
        if selected_features:
            # Validate that all selected features exist
            missing_features = [f for f in selected_features if f not in df.columns]
            if missing_features:
                return jsonify({'error': f'Features not found in data: {missing_features}'}), 400
            # Filter DataFrame to only selected features
            df = df[selected_features]
            logger.info(f"Using selected features: {selected_features}")
        else:
            # Default: use all numeric columns
            import numpy as np
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                df = df[numeric_cols]
                logger.info(f"Using all numeric columns: {numeric_cols}")
            else:
                return jsonify({'error': 'No numeric columns found for ML training'}), 400
        
        # Prepare training data
        import numpy as np
        if np is None:
            return jsonify({'error': 'NumPy is not available'}), 500
        
        try:
            # Convert DataFrame to numpy array
            prepared_data = [df.select_dtypes(include=[np.number]).to_numpy()]
            
            # Check if preparation was successful
            if not prepared_data or len(prepared_data) == 0:
                logger.warning("Data preparation returned empty result")
                return jsonify({'error': 'No numeric data available for ML training'}), 400
        except Exception as e:
            logger.error(f"Error preparing training data: {str(e)}")
            return jsonify({'error': f'Error preparing training data: {str(e)}'}), 500
        
        # Convert to JSON-serializable format
        if format_type == 'numpy':
            import numpy as np
            try:
                if not prepared_data or len(prepared_data) == 0:
                    return jsonify({'error': 'No data prepared for conversion'}), 500
                
                data_array = prepared_data[0]
                if data_array is None or (hasattr(data_array, '__len__') and len(data_array) == 0):
                    return jsonify({'error': 'Prepared data is empty'}), 500
                
                # Convert numpy types to native Python types for JSON serialization
                import numpy as np
                shape = list(data_array.shape) if hasattr(data_array, 'shape') else None
                if shape:
                    shape = [int(s) for s in shape]  # Convert numpy int64 to Python int
                
                dtype = str(data_array.dtype) if hasattr(data_array, 'dtype') else None
                sample_size = int(len(data_array)) if hasattr(data_array, '__len__') else 0
                
                # Convert preview data to native Python types
                data_preview = []
                if hasattr(data_array, '__len__') and len(data_array) > 0:
                    preview = data_array[:10]
                    if hasattr(preview, 'tolist'):
                        data_preview = preview.tolist()
                    else:
                        data_preview = [float(x) if isinstance(x, (np.integer, np.floating)) else x for x in preview]
                
                result = {
                    'format': 'numpy',
                    'shape': shape,
                    'dtype': dtype,
                    'sample_size': sample_size,
                    'data_preview': data_preview
                }
            except Exception as e:
                logger.error(f"Error converting numpy data: {str(e)}")
                return jsonify({'error': f'Error converting to numpy format: {str(e)}'}), 500
        elif format_type == 'tensorflow':
            try:
                import tensorflow as tf
                if tf is None:
                    return jsonify({'error': 'TensorFlow is not installed'}), 500
                
                # Always use numeric columns only for TensorFlow (avoids mixed types error)
                import numpy as np
                if np is None:
                    return jsonify({'error': 'NumPy is not available'}), 500
                
                # Select only numeric columns to avoid mixed types error
                numeric_df = df.select_dtypes(include=[np.number])
                if numeric_df.empty:
                    return jsonify({'error': 'No numeric columns found in data'}), 400
                
                # Convert to numpy array with consistent dtype
                numpy_data = numeric_df.to_numpy(dtype=np.float32)  # Use float32 for TensorFlow
                tf_dataset = tf.data.Dataset.from_tensor_slices(numpy_data)
                
                # Get dataset info
                dataset_size = 0
                try:
                    cardinality = tf_dataset.cardinality().numpy()
                    if cardinality == -1:  # Unknown cardinality
                        dataset_size = int(len(df))
                    else:
                        dataset_size = int(cardinality)
                except:
                    dataset_size = int(len(df))
                
                # Convert element_spec to string safely
                element_spec_str = None
                try:
                    if hasattr(tf_dataset, 'element_spec'):
                        element_spec_str = str(tf_dataset.element_spec)
                except:
                    pass
                
                result = {
                    'format': 'tensorflow',
                    'type': 'Dataset',
                    'sample_size': dataset_size,
                    'element_spec': element_spec_str,
                    'message': 'TensorFlow Dataset created successfully'
                }
            except ImportError:
                return jsonify({'error': 'TensorFlow is not installed. Install with: pip install tensorflow'}), 500
            except Exception as e:
                logger.error(f"Error creating TensorFlow dataset: {str(e)}")
                return jsonify({'error': f'Error creating TensorFlow dataset: {str(e)}'}), 500
        else:
            return jsonify({'error': f'Unsupported format: {format_type}'}), 400
        
        return jsonify({
            'filename': filename,
            'format': format_type,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Error preparing ML data: {str(e)}")
        return jsonify({'error': str(e)}), 500


@analysis_ml_bp.route('/prepare-rl-state', methods=['POST'])
def prepare_rl_state():
    """Prepare reinforcement learning state from data."""
    try:
        data = request.get_json()
        filename = data.get('filename')
        portfolio = data.get('portfolio', {})
        format_type = data.get('format', 'numpy')  # numpy, tensorflow
        file_path_hint = data.get('file_path')
        
        if not filename:
            return jsonify({'error': 'No filename provided'}), 400
        
        from redline.core.format_converter import FormatConverter
        from redline.core.schema import EXT_TO_FORMAT
        
        converter = FormatConverter()
        
        # Find and load file (same logic as above)
        data_dir = os.path.join(os.getcwd(), 'data')
        data_path = None
        
        if file_path_hint and os.path.exists(file_path_hint):
            data_path = file_path_hint
        else:
            search_paths = [
                os.path.join(data_dir, filename),
                os.path.join(data_dir, 'stooq', filename),
                os.path.join(data_dir, 'downloaded', filename),
                os.path.join(data_dir, 'uploads', filename)
            ]
            
            converted_dir = os.path.join(data_dir, 'converted')
            if os.path.exists(converted_dir):
                for root, dirs, files in os.walk(converted_dir):
                    if filename in files:
                        search_paths.append(os.path.join(root, filename))
            
            for path in search_paths:
                if os.path.exists(path):
                    data_path = path
                    break
        
        if not data_path or not os.path.exists(data_path):
            return jsonify({'error': f'File not found: {filename}'}), 404
        
        # Load data
        ext = os.path.splitext(data_path)[1].lower()
        format_type_file = EXT_TO_FORMAT.get(ext, 'csv')
        
        if format_type_file == 'csv':
            df = pd.read_csv(data_path)
        elif format_type_file == 'parquet':
            df = pd.read_parquet(data_path)
        elif format_type_file == 'feather':
            df = pd.read_feather(data_path)
        elif format_type_file == 'json':
            df = pd.read_json(data_path)
        elif format_type_file == 'duckdb':
            import duckdb
            conn = duckdb.connect(data_path)
            df = conn.execute("SELECT * FROM tickers_data").fetchdf()
            conn.close()
        elif format_type_file in ('tensorflow', 'npz'):
            import numpy as np
            # Use allow_pickle=True for .npz files that may contain object arrays
            loaded = np.load(data_path, allow_pickle=True)
            if 'data' in loaded:
                data_array = loaded['data']
                # Restore column names if they were saved
                if 'columns' in loaded:
                    columns = loaded['columns'].tolist()
                    df = pd.DataFrame(data_array, columns=columns)
                else:
                    # Fallback: create generic column names
                    df = pd.DataFrame(data_array, columns=[f'col_{i}' for i in range(data_array.shape[1])])
            else:
                first_key = list(loaded.keys())[0]
                df = pd.DataFrame(loaded[first_key])
        elif format_type_file == 'txt':
            # Handle TXT files (Stooq format or tab-separated)
            try:
                # Try reading as CSV first (Stooq format uses commas)
                df = pd.read_csv(data_path)
            except:
                # Try different separators for TXT files
                for sep in ['\t', ';', ' ', '|']:
                    try:
                        df = pd.read_csv(data_path, sep=sep)
                        break
                    except:
                        continue
                else:
                    # If all separators fail, try reading as fixed-width
                    df = pd.read_fwf(data_path)
        elif format_type_file in ('keras', 'h5'):
            return jsonify({'error': 'Keras model files (.h5) cannot be used for ML data preparation. Use the Analysis tab for model operations.'}), 400
        elif format_type_file in ('pyarrow', 'arrow'):
            try:
                import pyarrow as pa
                with pa.ipc.open_file(data_path) as reader:
                    df = reader.read_all().to_pandas()
            except ImportError:
                return jsonify({'error': 'PyArrow is required to load .arrow files'}), 400
            except Exception as e:
                return jsonify({'error': f'Error loading Arrow file: {str(e)}'}), 400
        else:
            df = converter.load_file_by_type(data_path, format_type_file)
        
        if not isinstance(df, pd.DataFrame):
            return jsonify({'error': 'Invalid data format'}), 400
        
        df = clean_dataframe_columns(df)
        
        # Prepare RL state
        import numpy as np
        if np is None:
            return jsonify({'error': 'NumPy is not available'}), 500
        
        try:
            # Extract close prices for RL state
            if 'close' not in df.columns:
                return jsonify({'error': 'Close column not found in data'}), 400
            
            state = df[['close']].to_numpy()
            
            # Convert to tensorflow tensor if requested
            if format_type == 'tensorflow':
                try:
                    import tensorflow as tf
                    if tf is None:
                        return jsonify({'error': 'TensorFlow is not installed'}), 500
                    rl_state = tf.convert_to_tensor(state, dtype=tf.float32)
                except ImportError:
                    return jsonify({'error': 'TensorFlow is not installed. Install with: pip install tensorflow'}), 500
            else:
                rl_state = state
        except Exception as e:
            logger.error(f"Error preparing RL state: {str(e)}")
            return jsonify({'error': f'Error preparing RL state: {str(e)}'}), 500
        
        # Convert to JSON-serializable format
        if format_type == 'numpy':
            import numpy as np
            result = {
                'format': 'numpy',
                'shape': rl_state.shape if hasattr(rl_state, 'shape') else None,
                'dtype': str(rl_state.dtype) if hasattr(rl_state, 'dtype') else None,
                'data_preview': rl_state[:10].tolist() if len(rl_state) > 0 else []
            }
        elif format_type == 'tensorflow':
            result = {
                'format': 'tensorflow',
                'type': 'Tensor',
                'message': 'TensorFlow Tensor created successfully'
            }
        else:
            return jsonify({'error': f'Unsupported format: {format_type}'}), 400
        
        return jsonify({
            'filename': filename,
            'format': format_type,
            'portfolio': portfolio,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Error preparing RL state: {str(e)}")
        return jsonify({'error': str(e)}), 500



