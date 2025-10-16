#!/usr/bin/env python3
"""
Simple script to open Stooq website for manual historical data download
"""

import webbrowser
import tkinter as tk
from tkinter import messagebox, simpledialog
import os

def open_stooq_historical():
    """Open Stooq historical page for manual download"""
    
    # Create a simple GUI for ticker input
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    # Ask for ticker symbol
    ticker = simpledialog.askstring("Stock Ticker", 
                                   "Enter stock ticker symbol (e.g., AAPL, MSFT, GOOGL):",
                                   initialvalue="AAPL")
    
    if ticker:
        # Open Stooq historical page
        stooq_url = f"https://stooq.com/q/h/?s={ticker}"
        webbrowser.open(stooq_url)
        
        # Show instructions
        instructions = f"""
🌐 Stooq website opened for {ticker.upper()}

📋 MANUAL DOWNLOAD STEPS:

1. 🔐 LOGIN to your Stooq account
   - If you don't have an account, create one at stooq.com

2. 🔑 COMPLETE 2FA (Two-Factor Authentication)
   - Check your email/SMS for verification code
   - Enter the code when prompted

3. 📊 NAVIGATE to Historical Data
   - Look for "Dane historyczne" or "Historical Data" button
   - Click on it to access historical data

4. 📅 SELECT DATE RANGE
   - Choose your desired start and end dates
   - Historical data is available from 1990s to present

5. 💾 DOWNLOAD CSV FILE
   - Click the download button (usually CSV format)
   - Save the file to your computer

6. 📁 SAVE TO REDLINE DATA FOLDER
   - Copy the downloaded CSV to: {os.getcwd()}/data/
   - Rename it to: {ticker.lower()}_historical_stooq.csv

✅ The file will be automatically detected by REDLINE!

💡 TIP: You can download multiple tickers by repeating these steps
        """
        
        messagebox.showinfo("Manual Download Instructions", instructions)
        
        # Ask if they want to open another ticker
        another = messagebox.askyesno("Another Ticker?", 
                                     f"Would you like to open another ticker?")
        if another:
            open_stooq_historical()
    else:
        messagebox.showwarning("No Ticker", "Please enter a ticker symbol")

def main():
    """Main function"""
    print("🚀 Opening Stooq for manual historical data download...")
    open_stooq_historical()

if __name__ == "__main__":
    main()
