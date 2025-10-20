#!/usr/bin/env python3
"""
REDLINE Progress Tracker Widget
GUI component for tracking and displaying progress of operations.
"""

import logging
import tkinter as tk
from tkinter import ttk
import threading
from typing import Optional, Callable

logger = logging.getLogger(__name__)

class ProgressTracker:
    """GUI progress tracker with thread-safe updates."""
    
    def __init__(self, parent, title: str = "Progress"):
        """Initialize progress tracker."""
        self.parent = parent
        self.title = title
        self.logger = logging.getLogger(__name__)
        
        # Progress tracking variables
        self.current_step = 0
        self.total_steps = 0
        self.current_progress = 0
        self.total_progress = 0
        self.current_operation = ""
        self.is_running = False
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Create GUI components
        self.create_widgets()
        
        # Callbacks
        self.on_complete: Optional[Callable] = None
        self.on_cancel: Optional[Callable] = None
    
    def create_widgets(self):
        """Create the GUI widgets."""
        # Main frame
        self.frame = ttk.Frame(self.parent)
        
        # Title label
        self.title_label = ttk.Label(self.frame, text=self.title, font=('Arial', 10, 'bold'))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky='w')
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            self.frame, 
            mode='determinate',
            length=300
        )
        self.progress_bar.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0, 5))
        
        # Status label
        self.status_label = ttk.Label(self.frame, text="Ready", font=('Arial', 9))
        self.status_label.grid(row=2, column=0, columnspan=2, sticky='w', pady=(0, 5))
        
        # Step counter
        self.step_label = ttk.Label(self.frame, text="0 / 0", font=('Arial', 8))
        self.step_label.grid(row=3, column=0, sticky='w')
        
        # Cancel button
        self.cancel_button = ttk.Button(
            self.frame, 
            text="Cancel",
            command=self.cancel_operation
        )
        self.cancel_button.grid(row=3, column=1, sticky='e')
        
        # Configure grid weights
        self.frame.grid_columnconfigure(0, weight=1)
    
    def start_operation(self, total_steps: int, operation_name: str = ""):
        """
        Start a new operation.
        
        Args:
            total_steps: Total number of steps
            operation_name: Name of the operation
        """
        with self.lock:
            self.total_steps = total_steps
            self.current_step = 0
            self.current_operation = operation_name
            self.is_running = True
            
            # Update GUI
            self.progress_bar['maximum'] = total_steps
            self.progress_bar['value'] = 0
            self.status_label.config(text=operation_name or "Starting...")
            self.step_label.config(text=f"0 / {total_steps}")
            self.cancel_button.config(state='normal')
    
    def update_progress(self, step: int = None, operation: str = None, increment: bool = False):
        """
        Update progress.
        
        Args:
            step: Current step number
            operation: Current operation description
            increment: If True, increment current step by 1
        """
        with self.lock:
            if not self.is_running:
                return
            
            if increment:
                self.current_step += 1
            elif step is not None:
                self.current_step = step
            
            # Update progress values
            self.current_progress = self.current_step
            self.total_progress = self.total_steps
            
            # Store operation for GUI update
            self.current_operation = operation or self.current_operation
            
            # Update GUI safely with error handling
            try:
                print(f"DEBUG: Progress update - {self.current_operation} ({self.current_progress}/{self.total_progress})")
                # Use after(0) instead of after_idle to avoid GIL issues
                self.parent.after(0, self._update_gui)
            except Exception as e:
                print(f"DEBUG: Error scheduling GUI update: {str(e)}")
                self.logger.error(f"Error scheduling GUI update: {str(e)}")
    
    def _update_gui(self):
        """Update GUI components (called from main thread)."""
        try:
            print(f"DEBUG: _update_gui called - {self.current_operation} ({self.current_progress}/{self.total_progress})")
            # Update progress bar
            progress_value = (self.current_step / self.total_steps) * 100 if self.total_steps > 0 else 0
            self.progress_bar['value'] = progress_value
            
            # Update status
            if self.current_operation:
                self.status_label.config(text=self.current_operation)
            
            # Update step counter
            self.step_label.config(text=f"{self.current_step} / {self.total_steps}")
            
            # Check if complete
            if self.current_step >= self.total_steps:
                self.complete_operation()
                
        except Exception as e:
            self.logger.error(f"Error updating GUI: {str(e)}")
    
    def complete_operation(self):
        """Mark operation as complete."""
        print(f"DEBUG: complete_operation called")
        with self.lock:
            self.is_running = False
            
            # Update GUI safely
            try:
                print(f"DEBUG: Updating completion GUI")
                self.status_label.config(text="Complete")
                self.cancel_button.config(state='disabled')
            except Exception as e:
                print(f"DEBUG: Error updating completion GUI: {str(e)}")
                self.logger.error(f"Error updating completion GUI: {str(e)}")
            
            # Call completion callback safely
            if self.on_complete:
                try:
                    print(f"DEBUG: Scheduling completion callback")
                    # Use after(0) instead of after_idle to avoid GIL issues
                    self.parent.after(0, self._safe_completion_callback)
                except Exception as e:
                    print(f"DEBUG: Error scheduling completion callback: {str(e)}")
                    self.logger.error(f"Error scheduling completion callback: {str(e)}")
    
    def _safe_completion_callback(self):
        """Safely call completion callback from main thread."""
        try:
            if self.on_complete:
                self.on_complete()
        except Exception as e:
            self.logger.error(f"Error in completion callback: {str(e)}")
    
    def cancel_operation(self):
        """Cancel the current operation."""
        with self.lock:
            if not self.is_running:
                return
            
            self.is_running = False
            self.status_label.config(text="Cancelled")
            self.cancel_button.config(state='disabled')
            
            # Call cancel callback
            if self.on_cancel:
                try:
                    self.on_cancel()
                except Exception as e:
                    self.logger.error(f"Error in cancel callback: {str(e)}")
    
    def reset(self):
        """Reset the progress tracker."""
        with self.lock:
            self.current_step = 0
            self.total_steps = 0
            self.current_operation = ""
            self.is_running = False
            
            # Reset GUI
            self.progress_bar['value'] = 0
            self.status_label.config(text="Ready")
            self.step_label.config(text="0 / 0")
            self.cancel_button.config(state='normal')
    
    def set_completion_callback(self, callback: Callable):
        """Set callback for operation completion."""
        self.on_complete = callback
    
    def set_cancel_callback(self, callback: Callable):
        """Set callback for operation cancellation."""
        self.on_cancel = callback
    
    def is_operation_running(self) -> bool:
        """Check if operation is currently running."""
        with self.lock:
            return self.is_running
    
    def get_progress_percentage(self) -> float:
        """Get current progress as percentage."""
        with self.lock:
            if self.total_steps == 0:
                return 0.0
            return (self.current_step / self.total_steps) * 100
    
    def get_current_step(self) -> int:
        """Get current step number."""
        with self.lock:
            return self.current_step
    
    def get_total_steps(self) -> int:
        """Get total number of steps."""
        with self.lock:
            return self.total_steps
    
    def pack(self, **kwargs):
        """Pack the progress tracker widget."""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the progress tracker widget."""
        self.frame.grid(**kwargs)
    
    def place(self, **kwargs):
        """Place the progress tracker widget."""
        self.frame.place(**kwargs)
    
    def destroy(self):
        """Destroy the progress tracker widget."""
        self.frame.destroy()
