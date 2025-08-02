 # start_at_market_open.py
"""
Auto-start AIMn Trading System at market open
Checks market status and starts trading when market opens
"""

import time
from datetime import datetime, timedelta
import subprocess
import sys
from alpaca_connector import AlpacaTradingConnector

print("\n" + "="*60)
print("🕐 AIMn AUTO-START SYSTEM")
print("="*60)

# Initialize connector to check market status
print("\n📡 Connecting to Alpaca to check market status...")
connector = AlpacaTradingConnector(paper_trading=True)

def check_market_status():
    """Check if market is open and when it opens"""
    clock = connector.api.get_clock()
    
    is_open = clock.is_open
    next_open = clock.next_open
    next_close = clock.next_close
    current_time = clock.timestamp
    
    return {
        'is_open': is_open,
        'next_open': next_open,
        'next_close': next_close,
        'current_time': current_time
    }

def time_until_market_open():
    """Calculate time until market opens"""
    status = check_market_status()
    
    if status['is_open']:
        return 0  # Market is already open
    
    time_diff = status['next_open'] - status['current_time']
    return time_diff.total_seconds()

def format_time_remaining(seconds):
    """Format seconds into readable time"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours} hours, {minutes} minutes"

# Main monitoring loop
print("\n🔍 Checking market status...")

while True:
    status = check_market_status()
    
    if status['is_open']:
        print(f"\n✅ Market is OPEN! (closes at {status['next_close']})")
        print("🚀 Starting AIMn Trading System...\n")
        
        # Start the main trading system
        subprocess.run([sys.executable, "main_v2.py"])
        break
    else:
        seconds_until_open = time_until_market_open()
        time_remaining = format_time_remaining(seconds_until_open)
        
        print(f"\r⏰ Market opens in {time_remaining} (at {status['next_open']})   ", end='', flush=True)
        
        # If market opens in less than 5 minutes, check every 30 seconds
        if seconds_until_open < 300:
            time.sleep(30)
        # Otherwise check every 5 minutes
        else:
            time.sleep(300)

print("\n\n✅ Auto-start complete!")