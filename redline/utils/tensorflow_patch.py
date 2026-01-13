"""
TensorFlow import patch for ARM64 compatibility.
Fixes TypeError in TensorFlow 2.20.0 where docstrings can be None.
"""

import sys
import re
import types

def patch_tensorflow_util():
    """Patch TensorFlow's all_util.make_all function to handle None docstrings."""
    try:
        # Import the module that contains the problematic function
        import tensorflow.python.util.all_util as all_util
        
        # Store original function
        original_make_all = all_util.make_all
        
        def patched_make_all(module_name, doc_string_modules):
            """Patched version that handles None docstrings."""
            _reference_pattern = re.compile(r'^([A-Z][a-zA-Z0-9_]*):', re.MULTILINE)
            should_have = set()
            for doc_module in doc_string_modules:
                # Handle None docstrings gracefully
                doc_string = getattr(doc_module, '__doc__', None)
                if doc_string is None:
                    continue
                try:
                    for m in _reference_pattern.finditer(doc_string):
                        should_have.add(m.group(1))
                except (TypeError, AttributeError):
                    # Skip if doc_string is not a string
                    continue
            return should_have
        
        # Replace the function
        all_util.make_all = patched_make_all
        return True
    except (ImportError, AttributeError) as e:
        return False


def safe_import_tensorflow():
    """
    Safely import TensorFlow with patching for ARM64 compatibility.
    
    Returns:
        tuple: (tensorflow_module, success_flag)
    """
    # Try to import TensorFlow
    try:
        import tensorflow as tf
        # Try to patch after import
        patch_tensorflow_util()
        return tf, True
    except TypeError as e:
        # If we get the TypeError, try to patch and re-import
        if "expected string or bytes-like object" in str(e):
            try:
                # The error happens during import, so we need to patch before
                # But since it's during import, we can't patch it easily
                # Instead, we'll need to monkey-patch the source file
                import importlib
                import tensorflow.python.util.all_util as all_util
                
                # Patch the function
                _reference_pattern = re.compile(r'^([A-Z][a-zA-Z0-9_]*):', re.MULTILINE)
                
                def patched_make_all(module_name, doc_string_modules):
                    should_have = set()
                    for doc_module in doc_string_modules:
                        doc_string = getattr(doc_module, '__doc__', None)
                        if doc_string is None:
                            continue
                        try:
                            for m in _reference_pattern.finditer(doc_string):
                                should_have.add(m.group(1))
                        except (TypeError, AttributeError):
                            continue
                    return should_have
                
                all_util.make_all = patched_make_all
                
                # Now try to reload tensorflow
                if 'tensorflow' in sys.modules:
                    importlib.reload(sys.modules['tensorflow'])
                else:
                    import tensorflow as tf
                    return tf, True
            except Exception as patch_error:
                return None, False
        return None, False
    except Exception as e:
        return None, False
