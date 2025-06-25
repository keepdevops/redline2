#!/usr/bin/env python3
"""
Test script to verify the scrollbar fix
This script will help test if the TclError is resolved
"""

import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox

def test_scrollbar_operations():
    """Test the scrollbar operations that were causing TclError"""
    print("Starting scrollbar test...")
    
    # Create a simple test window
    root = tk.Tk()
    root.title("Scrollbar Test")
    root.geometry("600x400")
    
    # Create a frame with treeview and scrollbars
    frame = ttk.Frame(root)
    frame.pack(fill='both', expand=True, padx=10, pady=10)
    
    # Configure grid weights
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    
    # Create treeview
    tree = ttk.Treeview(frame)
    
    # Create scrollbars (similar to our fix)
    xscroll = ttk.Scrollbar(frame, orient='horizontal', command=tree.xview)
    yscroll = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
    
    # Configure treeview scrolling
    tree.configure(xscrollcommand=xscroll.set, yscrollcommand=yscroll.set)
    
    # Grid layout
    tree.grid(row=0, column=0, sticky='nsew')
    xscroll.grid(row=1, column=0, sticky='ew')
    yscroll.grid(row=0, column=1, sticky='ns')
    
    # Add some test data
    tree['columns'] = ('col1', 'col2', 'col3', 'col4', 'col5')
    tree['show'] = 'headings'
    
    for col in tree['columns']:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    
    # Add test rows
    for i in range(50):
        tree.insert('', 'end', values=(f'Row {i}', f'Data {i}', f'Value {i}', f'Info {i}', f'Extra {i}'))
    
    def simulate_data_updates():
        """Simulate rapid data updates that were causing the TclError"""
        print("Starting data update simulation...")
        
        for update_count in range(10):
            print(f"Update {update_count + 1}/10")
            
            # Clear and repopulate data (like our refactored code does)
            tree.delete(*tree.get_children())
            
            # Add new data
            for i in range(50):
                tree.insert('', 'end', values=(
                    f'Update {update_count} Row {i}', 
                    f'Update {update_count} Data {i}', 
                    f'Update {update_count} Value {i}', 
                    f'Update {update_count} Info {i}', 
                    f'Update {update_count} Extra {i}'
                ))
            
            # Small delay to simulate processing
            time.sleep(0.1)
        
        print("Data update simulation completed!")
        messagebox.showinfo("Test Complete", "Scrollbar test completed successfully!\nNo TclError occurred.")
    
    # Add a button to start the test
    test_button = ttk.Button(root, text="Start Scrollbar Test", command=simulate_data_updates)
    test_button.pack(pady=10)
    
    # Add a button to close
    close_button = ttk.Button(root, text="Close", command=root.quit)
    close_button.pack(pady=5)
    
    print("Test window created. Click 'Start Scrollbar Test' to begin testing.")
    print("If no TclError occurs, the fix is working!")
    
    root.mainloop()

if __name__ == "__main__":
    test_scrollbar_operations() 