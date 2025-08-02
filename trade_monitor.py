# SAVE THIS FILE AS: trade_monitor.py
# LOCATION: C:\Users\mniv7\Documents\meir\cl-py\trade_monitor.py

"""
Clean monitor that shows ONLY trades and opportunities
No boring scanning messages!
"""

import time
import os
from datetime import datetime
import re

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_important_events(log_file, last_position=0):
    """Extract only trade-related events"""
    events = []
    
    if not os.path.exists(log_file):
        return events, last_position
    
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(last_position)
        new_lines = f.readlines()
        new_position = f.tell()
    
    for line in new_lines:
        # Skip scanning messages
        if any(skip in line for skip in ['scanning for opportunities', 'No trading opportunities', 
                                         'Waiting', 'Trading cycle started', 'Account Status']):
            continue
        
        # Look for important events
        if 'Opportunity found' in line:
            timestamp = line[:19] if len(line) > 19 else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            events.append(('SIGNAL', timestamp, line.strip()))
            
        elif 'TRADE EXECUTED' in line:
            timestamp = line[:19] if len(line) > 19 else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            events.append(('TRADE', timestamp, line.strip()))
            
        elif 'Active position' in line and 'P&L:' in line:
            # Only show significant P&L updates
            match = re.search(r'P&L: \$([\d,.-]+) \(([\d.-]+)%\)', line)
            if match:
                pnl = float(match.group(1).replace(',', ''))
                pnl_pct = float(match.group(2))
                if abs(pnl_pct) > 0.5:  # Only show if > 0.5% move
                    timestamp = line[:19] if len(line) > 19 else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    events.append(('UPDATE', timestamp, line.strip()))
                    
        elif 'EXIT ORDER' in line or 'Position closed' in line:
            timestamp = line[:19] if len(line) > 19 else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            events.append(('EXIT', timestamp, line.strip()))
    
    return events, new_position

def main():
    log_file = 'aimn_crypto_trading.log'
    last_position = 0
    all_events = []
    
    print("🎯 AIMn TRADE MONITOR - Shows Only Important Events")
    print("=" * 60)
    print("Waiting for trades... (No boring scan messages!)")
    print("=" * 60)
    
    while True:
        # Get new events
        new_events, last_position = get_important_events(log_file, last_position)
        
        if new_events:
            all_events.extend(new_events)
            
            # Clear and redraw
            clear_screen()
            print("🎯 AIMn TRADE MONITOR - Shows Only Important Events")
            print("=" * 60)
            
            # Show stats
            signal_count = len([e for e in all_events if e[0] == 'SIGNAL'])
            trade_count = len([e for e in all_events if e[0] == 'TRADE'])
            exit_count = len([e for e in all_events if e[0] == 'EXIT'])
            
            print(f"📊 Stats: {signal_count} Signals | {trade_count} Trades | {exit_count} Exits")
            print("=" * 60)
            
            # Show last 20 events
            for event_type, timestamp, message in all_events[-20:]:
                if event_type == 'SIGNAL':
                    print(f"💡 {timestamp} - OPPORTUNITY FOUND!")
                    print(f"   {message}")
                elif event_type == 'TRADE':
                    print(f"🎯 {timestamp} - TRADE EXECUTED!")
                    print(f"   {message}")
                elif event_type == 'UPDATE':
                    print(f"📈 {timestamp} - Position Update")
                    print(f"   {message}")
                elif event_type == 'EXIT':
                    print(f"🚪 {timestamp} - TRADE CLOSED!")
                    print(f"   {message}")
                print()
            
            if not all_events:
                print("⏳ No trades yet... Keep waiting!")
        
        # Check every 2 seconds
        time.sleep(2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Trade monitor stopped!")