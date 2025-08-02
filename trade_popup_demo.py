# SAVE THIS FILE AS: trade_popup_demo.py
# LOCATION: C:\Users\mniv7\Documents\meir\cl-py\trade_popup_demo.py

"""
Demo of what the trade pop-up window will look like
This is a preview of the feature for clients
"""

import tkinter as tk
from tkinter import ttk
import random
import threading
import time

class TradePopup:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎯 LIVE TRADE - ETH/USD")
        self.root.geometry("400x300")
        
        # Make it stay on top
        self.root.attributes('-topmost', True)
        
        # Trade info
        self.symbol = "ETH/USD"
        self.direction = "BUY"
        self.entry_price = 3799.50
        self.current_price = 3799.50
        self.quantity = 0.823
        self.pnl = 0.0
        
        self.setup_ui()
        self.update_price()
        
    def setup_ui(self):
        # Header
        header = tk.Label(self.root, text="🎯 NEW TRADE EXECUTED!", 
                         font=("Arial", 16, "bold"), fg="green")
        header.pack(pady=10)
        
        # Trade info frame
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=10)
        
        # Symbol and direction
        tk.Label(info_frame, text=f"{self.symbol} - {self.direction}", 
                font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2)
        
        # Entry price
        tk.Label(info_frame, text="Entry Price:", 
                font=("Arial", 10)).grid(row=1, column=0, sticky="e", padx=5)
        tk.Label(info_frame, text=f"${self.entry_price:,.2f}", 
                font=("Arial", 10, "bold")).grid(row=1, column=1, sticky="w")
        
        # Current price
        tk.Label(info_frame, text="Current Price:", 
                font=("Arial", 10)).grid(row=2, column=0, sticky="e", padx=5)
        self.current_price_label = tk.Label(info_frame, text=f"${self.current_price:,.2f}", 
                                          font=("Arial", 10, "bold"))
        self.current_price_label.grid(row=2, column=1, sticky="w")
        
        # P&L
        tk.Label(info_frame, text="P&L:", 
                font=("Arial", 10)).grid(row=3, column=0, sticky="e", padx=5)
        self.pnl_label = tk.Label(info_frame, text="$0.00 (0.00%)", 
                                 font=("Arial", 10, "bold"))
        self.pnl_label.grid(row=3, column=1, sticky="w")
        
        # Visual chart (simplified)
        self.canvas = tk.Canvas(self.root, width=350, height=100, bg="black")
        self.canvas.pack(pady=10)
        
        # Draw entry line
        self.canvas.create_line(25, 50, 325, 50, fill="yellow", width=2, dash=(5, 5))
        self.canvas.create_text(350, 50, text="Entry", fill="yellow", anchor="e")
        
        # Price line (will move)
        self.price_line = self.canvas.create_line(25, 50, 325, 50, fill="green", width=3)
        
        # Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        expand_btn = tk.Button(button_frame, text="📊 Expand Chart", 
                             command=self.expand_chart, bg="blue", fg="white")
        expand_btn.pack(side="left", padx=5)
        
        close_btn = tk.Button(button_frame, text="✕ Minimize", 
                            command=self.minimize, bg="gray", fg="white")
        close_btn.pack(side="left", padx=5)
        
    def update_price(self):
        """Simulate price movement"""
        # Random walk
        change = random.uniform(-5, 6)  # Slightly bullish
        self.current_price += change
        
        # Update P&L
        self.pnl = (self.current_price - self.entry_price) * self.quantity
        pnl_pct = (self.current_price / self.entry_price - 1) * 100
        
        # Update labels
        self.current_price_label.config(text=f"${self.current_price:,.2f}")
        
        if self.pnl >= 0:
            self.pnl_label.config(text=f"${self.pnl:,.2f} ({pnl_pct:+.2f}%)", fg="green")
            # Move price line up
            y_pos = 50 - (pnl_pct * 2)  # Scale for visualization
            self.canvas.coords(self.price_line, 25, y_pos, 325, y_pos)
        else:
            self.pnl_label.config(text=f"${self.pnl:,.2f} ({pnl_pct:+.2f}%)", fg="red")
            # Move price line down
            y_pos = 50 - (pnl_pct * 2)
            self.canvas.coords(self.price_line, 25, y_pos, 325, y_pos)
            self.canvas.itemconfig(self.price_line, fill="red")
        
        # Schedule next update
        self.root.after(1000, self.update_price)  # Update every second
        
    def expand_chart(self):
        """Expand to full chart view"""
        print("📊 Opening full chart view...")
        # In real version, this would open a full TradingView-style chart
        
    def minimize(self):
        """Minimize the popup"""
        self.root.iconify()
        
    def run(self):
        self.root.mainloop()

# Demo
if __name__ == "__main__":
    print("🎯 DEMO: Trade Pop-up Window")
    print("This shows what clients will see when a trade executes!")
    print("=" * 60)
    
    popup = TradePopup()
    popup.run()