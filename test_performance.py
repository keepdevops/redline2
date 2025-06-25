#!/usr/bin/env python3
"""
Performance test script to measure data loading speed
This will help verify if the scrollbar refactoring improved performance
"""

import time
import tkinter as tk
from tkinter import ttk, messagebox

def test_performance():
    """Test the performance of data loading operations"""
    print("Starting performance test...")
    
    # Create a simple test window
    root = tk.Tk()
    root.title("Performance Test")
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
    
    # Performance test results
    results = []
    
    def run_performance_test():
        """Run the performance test"""
        print("Running performance test...")
        
        # Test with different data sizes
        test_sizes = [100, 500, 1000, 2000]
        
        for size in test_sizes:
            print(f"Testing with {size} rows...")
            
            start_time = time.time()
            
            # Clear existing data
            tree.delete(*tree.get_children())
            
            # Add new data
            for i in range(size):
                tree.insert('', 'end', values=(
                    f'Row {i}', 
                    f'Data {i}', 
                    f'Value {i}', 
                    f'Info {i}', 
                    f'Extra {i}'
                ))
            
            end_time = time.time()
            duration = end_time - start_time
            results.append((size, duration))
            
            print(f"  {size} rows: {duration:.3f} seconds")
            
            # Small delay between tests
            time.sleep(0.5)
        
        # Show results
        result_text = "Performance Test Results:\n\n"
        for size, duration in results:
            result_text += f"{size} rows: {duration:.3f} seconds\n"
        
        avg_time = sum(duration for _, duration in results) / len(results)
        result_text += f"\nAverage time: {avg_time:.3f} seconds"
        
        print("Performance test completed!")
        messagebox.showinfo("Performance Test Complete", result_text)
    
    # Add a button to start the test
    test_button = ttk.Button(root, text="Start Performance Test", command=run_performance_test)
    test_button.pack(pady=10)
    
    # Add a button to close
    close_button = ttk.Button(root, text="Close", command=root.quit)
    close_button.pack(pady=5)
    
    print("Performance test window created. Click 'Start Performance Test' to begin.")
    
    root.mainloop()

if __name__ == "__main__":
    test_performance() 