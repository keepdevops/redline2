#!/usr/bin/env python3
"""
Download Events Helper for DownloadTab
Handles event bindings and UI interactions.
"""

import logging

logger = logging.getLogger(__name__)


class DownloadEventsHelper:
    """Helper class for event handling in DownloadTab."""
    
    def __init__(self, download_tab):
        """Initialize with reference to DownloadTab."""
        self.download_tab = download_tab
        self.logger = logging.getLogger(__name__)
    
    def setup_event_handlers(self):
        """Setup event handlers."""
        pass  # Event handlers are set up in UI creation
    
    def show_context_menu(self, event):
        """Show context menu for results tree."""
        try:
            self.download_tab.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.download_tab.context_menu.grab_release()
    
    def _on_left_frame_configure(self, event):
        """Handle scrollable frame configuration."""
        # Update scroll region when frame size changes
        if hasattr(self.download_tab, 'left_canvas') and self.download_tab.left_canvas:
            self.download_tab.left_canvas.configure(scrollregion=self.download_tab.left_canvas.bbox("all"))
            
            # Ensure canvas window uses full canvas width for horizontal expansion
            canvas_width = self.download_tab.left_canvas.winfo_width()
            if canvas_width > 1:  # Only update if canvas has been rendered
                try:
                    canvas_items = self.download_tab.left_canvas.find_all()
                    if canvas_items:
                        self.download_tab.left_canvas.itemconfig(canvas_items[0], width=canvas_width)
                except:
                    pass  # Ignore errors if canvas items not found
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        if not hasattr(self.download_tab, 'left_canvas') or not self.download_tab.left_canvas:
            return
        
        # Scroll the canvas
        if hasattr(event, 'delta') and event.delta:
            self.download_tab.left_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            # Linux
            if hasattr(event, 'num'):
                if event.num == 4:
                    self.download_tab.left_canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    self.download_tab.left_canvas.yview_scroll(1, "units")
    
    def scroll_to_top(self):
        """Scroll the left panel to the top."""
        if hasattr(self.download_tab, 'left_canvas'):
            self.download_tab.left_canvas.yview_moveto(0)
    
    def scroll_to_bottom(self):
        """Scroll the left panel to the bottom."""
        if hasattr(self.download_tab, 'left_canvas'):
            self.download_tab.left_canvas.yview_moveto(1)
    
    def on_tab_activated(self):
        """Handle tab activation."""
        # Scroll to top when tab becomes active
        self.scroll_to_top()
    
    def on_window_resize(self):
        """Handle window resize events."""
        try:
            # Update results tree layout if needed
            if hasattr(self.download_tab, 'results_tree') and self.download_tab.results_tree:
                # Could update tree column widths or refresh display
                pass
                
        except Exception as e:
            self.download_tab.logger.error(f"Error handling window resize in DownloadTab: {str(e)}")

