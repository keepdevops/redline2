#!/usr/bin/env python3
"""
Safe File Dialog Wrapper for macOS
Provides macOS-safe file dialog functions that prevent crashes.
"""

import logging
import os
import sys
from tkinter import filedialog
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)

# Detect macOS
IS_MACOS = sys.platform == 'darwin'


def _validate_filetypes(filetypes: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """
    Ultra-strict validation of filetypes for macOS compatibility.
    
    Args:
        filetypes: List of (description, pattern) tuples
        
    Returns:
        Validated list of filetypes safe for macOS
    """
    logger.debug(f"🔍 _validate_filetypes called with {len(filetypes) if filetypes else 0} filetype(s)")
    if not filetypes:
        logger.debug(f"   No filetypes provided, using fallback")
        return [("All files", "*.*")]
    
    validated = []
    for idx, item in enumerate(filetypes):
        logger.debug(f"   Validating item {idx}: {item} (type: {type(item)})")
        # Must be a tuple or list of length 2
        if not isinstance(item, (tuple, list)) or len(item) != 2:
            logger.debug(f"      ❌ Item {idx} failed: not a tuple/list of length 2")
            continue
        
        desc, pattern = item
        logger.debug(f"      Checking desc='{desc}' (type: {type(desc)}), pattern='{pattern}' (type: {type(pattern)})")
        
        # Both must be strings
        if not isinstance(desc, str) or not isinstance(pattern, str):
            logger.debug(f"      ❌ Item {idx} failed: not both strings")
            continue
        
        # Strip whitespace
        desc = desc.strip()
        pattern = pattern.strip()
        
        # Must not be empty
        if not desc or not pattern:
            logger.debug(f"      ❌ Item {idx} failed: empty after strip")
            continue
        
        # Must not be the string "None"
        if desc.lower() == "none" or pattern.lower() == "none":
            logger.debug(f"      ❌ Item {idx} failed: is 'None' string")
            continue
        
        # Pattern must start with * or be a valid extension pattern
        if not (pattern.startswith("*") or pattern.startswith(".")):
            logger.debug(f"      ❌ Item {idx} failed: pattern doesn't start with * or .")
            continue
        
        # macOS doesn't handle semicolon-separated patterns well - split them
        # For "All supported files" type entries, we'll keep only the first pattern
        # or convert to a simpler format
        if ";" in pattern:
            logger.debug(f"      ⚠️ Item {idx} has semicolon-separated pattern, splitting...")
            # For macOS, use only the first pattern or convert to "*.*" for "all files" type
            if "All" in desc or "all" in desc.lower():
                # For "All supported files", use a simpler pattern
                pattern = "*.*"
                logger.debug(f"      Converted to: ('{desc}', '{pattern}')")
            else:
                # Take first pattern only
                pattern = pattern.split(";")[0].strip()
                logger.debug(f"      Using first pattern only: '{pattern}'")
        
        # Final check: ensure pattern is still valid after processing
        if not pattern or pattern == "None":
            logger.debug(f"      ❌ Item {idx} failed: pattern invalid after processing")
            continue
        
        # All checks passed - add to validated list
        logger.debug(f"      ✅ Item {idx} validated: ('{desc}', '{pattern}')")
        validated.append((desc, pattern))
    
    # If validation removed everything, use minimal fallback
    if not validated:
        logger.warning(f"⚠️ All filetypes failed validation, using fallback")
        validated = [("All files", "*.*")]
    else:
        logger.debug(f"✅ Validated {len(validated)} filetype(s)")
    
    return validated


def safe_askopenfilenames(title: str = "Select Files", 
                          filetypes: Optional[List[Tuple[str, str]]] = None,
                          initialdir: Optional[str] = None,
                          **kwargs) -> tuple:
    """
    macOS-safe wrapper for filedialog.askopenfilenames.
    
    Args:
        title: Dialog title
        filetypes: List of (description, pattern) tuples
        initialdir: Initial directory
        **kwargs: Additional arguments to pass to askopenfilenames
        
    Returns:
        Tuple of selected file paths (empty if cancelled)
    """
    import traceback
    logger.info(f"🔍 safe_askopenfilenames called: title='{title}'")
    logger.debug(f"   filetypes={filetypes}")
    logger.debug(f"   initialdir={initialdir}")
    logger.debug(f"   Call stack:\n{''.join(traceback.format_stack()[-5:-1])}")
    
    try:
        # On macOS, use ultra-strict validation
        if IS_MACOS:
            if filetypes:
                filetypes = _validate_filetypes(filetypes)
            else:
                # If no filetypes provided, use minimal safe default
                filetypes = [("All files", "*.*")]
            
            # Triple-check: ensure no None values can possibly exist
            # Also ensure no empty strings or problematic patterns
            safe_filetypes = []
            for desc, pattern in filetypes:
                # Convert to strings explicitly
                try:
                    desc_str = str(desc).strip() if desc else ""
                    pattern_str = str(pattern).strip() if pattern else ""
                except Exception as e:
                    logger.warning(f"   Error converting to string: {e}, skipping")
                    continue
                
                # Validate strings
                if not desc_str or not pattern_str:
                    logger.debug(f"   Skipping empty: desc='{desc_str}', pattern='{pattern_str}'")
                    continue
                
                if desc_str.lower() == "none" or pattern_str.lower() == "none":
                    logger.debug(f"   Skipping 'None' string: desc='{desc_str}', pattern='{pattern_str}'")
                    continue
                
                # Ensure pattern is valid for macOS
                if not (pattern_str.startswith("*") or pattern_str.startswith(".")):
                    logger.debug(f"   Skipping invalid pattern: '{pattern_str}'")
                    continue
                
                # Final validation - ensure both are non-empty strings
                if isinstance(desc_str, str) and isinstance(pattern_str, str):
                    if len(desc_str) > 0 and len(pattern_str) > 0:
                        safe_filetypes.append((desc_str, pattern_str))
                        logger.debug(f"   ✅ Added safe filetype: ('{desc_str}', '{pattern_str}')")
            
            if not safe_filetypes:
                logger.warning(f"   ⚠️ No safe filetypes after triple-check, using fallback")
                safe_filetypes = [("All files", "*.*")]
            
            logger.info(f"   Final safe filetypes count: {len(safe_filetypes)}")
            filetypes = safe_filetypes
        
        # Build arguments
        dialog_kwargs = {
            'title': title,
            **kwargs
        }
        
        if filetypes:
            dialog_kwargs['filetypes'] = filetypes
        
        if initialdir:
            dialog_kwargs['initialdir'] = os.path.expanduser(initialdir) if initialdir else None
        
        # Call the actual dialog
        logger.info(f"📂 Opening file dialog with {len(filetypes)} filetype(s)")
        result = filedialog.askopenfilenames(**dialog_kwargs)
        logger.info(f"✅ File dialog returned {len(result) if result else 0} file(s)")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error in safe_askopenfilenames: {str(e)}")
        import traceback
        logger.error(f"   Traceback:\n{traceback.format_exc()}")
        # Last resort: try with absolute minimal filetypes
        try:
            return filedialog.askopenfilenames(
                title=title,
                filetypes=[("All files", "*.*")],
                initialdir=initialdir if initialdir else None
            )
        except Exception as fallback_error:
            logger.error(f"Fallback file dialog also failed: {str(fallback_error)}")
            return ()


def safe_asksaveasfilename(title: str = "Save File",
                          defaultextension: str = "",
                          filetypes: Optional[List[Tuple[str, str]]] = None,
                          initialdir: Optional[str] = None,
                          **kwargs) -> str:
    """
    macOS-safe wrapper for filedialog.asksaveasfilename.
    
    Args:
        title: Dialog title
        defaultextension: Default file extension
        filetypes: List of (description, pattern) tuples
        initialdir: Initial directory
        **kwargs: Additional arguments to pass to asksaveasfilename
        
    Returns:
        Selected file path (empty string if cancelled)
    """
    import traceback
    logger.info(f"🔍 safe_asksaveasfilename called: title='{title}'")
    logger.debug(f"   filetypes={filetypes}")
    logger.debug(f"   initialdir={initialdir}")
    logger.debug(f"   Call stack:\n{''.join(traceback.format_stack()[-5:-1])}")
    
    try:
        # On macOS, use ultra-strict validation
        if IS_MACOS:
            if filetypes:
                filetypes = _validate_filetypes(filetypes)
            else:
                filetypes = [("All files", "*.*")]
            
            # Double-check: ensure no None values can possibly exist
            safe_filetypes = []
            for desc, pattern in filetypes:
                if desc and pattern and isinstance(desc, str) and isinstance(pattern, str):
                    if desc != "None" and pattern != "None":
                        safe_filetypes.append((str(desc), str(pattern)))
            
            if not safe_filetypes:
                safe_filetypes = [("All files", "*.*")]
            
            filetypes = safe_filetypes
        
        # Build arguments
        dialog_kwargs = {
            'title': title,
            **kwargs
        }
        
        if defaultextension:
            dialog_kwargs['defaultextension'] = defaultextension
        
        if filetypes:
            dialog_kwargs['filetypes'] = filetypes
        
        if initialdir:
            dialog_kwargs['initialdir'] = os.path.expanduser(initialdir) if initialdir else None
        
        # Call the actual dialog
        logger.info(f"💾 Opening save dialog with {len(filetypes)} filetype(s)")
        result = filedialog.asksaveasfilename(**dialog_kwargs)
        logger.info(f"✅ Save dialog returned: '{result}'")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error in safe_asksaveasfilename: {str(e)}")
        import traceback
        logger.error(f"   Traceback:\n{traceback.format_exc()}")
        # Last resort: try with absolute minimal filetypes
        try:
            return filedialog.asksaveasfilename(
                title=title,
                defaultextension=defaultextension,
                filetypes=[("All files", "*.*")],
                initialdir=initialdir if initialdir else None
            )
        except Exception as fallback_error:
            logger.error(f"Fallback file dialog also failed: {str(fallback_error)}")
            return ""

