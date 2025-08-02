"""
Save this as aimn_realtime_dashboard.py
This version will show your actual trading bot activity
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import re
import time

st.set_page_config(page_title="AIMn Real-Time Monitor", page_icon="🚀", layout="wide")

# Title
st.title("🚀 AIMn Trading System - Real-Time Monitor")

# Initialize session state
if 'last_position' not in st.session_state:
    st.session_state.last_position = 0

def get_latest_logs(filename='aimn_crypto_trading.log', num_lines=100):
    """Get the latest lines from log file"""
    if not os.path.exists(filename):
        return []
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    return lines[-num_lines:] if len(lines) > num_lines else lines

def parse_logs(lines):
    """Parse log lines into structured data"""
    scans = []
    prices = {}
    events = []
    
    for line in lines:
        # Extract timestamp
        timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
        timestamp = timestamp_match.group(1) if timestamp_match else ''
        
        # Parse different log types
        if 'Fetching' in line and 'latest price:' in line:
            # Extract price data
            match = re.search(r'Fetching (\S+) data.*latest price: \$?([\d,]+\.?\d*)', line)
            if match:
                symbol = match.group(1)
                price = float(match.group(2).replace(',', ''))
                prices[symbol] = price
                
        elif 'scanning for opportunities' in line:
            scans.append({
                'time': timestamp,
                'message': 'Scanning all symbols for opportunities'
            })
            
        elif 'No trading opportunities found' in line:
            events.append({
                'time': timestamp,
                'type': 'no_signal',
                'message': '🔍 No valid signals found'
            })
            
        elif 'Account Status:' in line or 'Portfolio Value:' in line:
            events.append({
                'time': timestamp,
                'type': 'status',
                'message': line.strip()
            })
            
        elif 'Opportunity found:' in line:
            events.append({
                'time': timestamp,
                'type': 'opportunity',
                'message': '💡 ' + line.strip()
            })
            
        elif 'TRADE EXECUTED:' in line:
            events.append({
                'time': timestamp,
                'type': 'trade',
                'message': '🎯 ' + line.strip()
            })
    
    return scans, prices, events

def load_trades():
    """Load completed trades"""
    trades = []
    if os.path.exists('aimn_trades.json'):
        with open('aimn_trades.json', 'r') as f:
            for line in f:
                try:
                    trades.append(json.loads(line))
                except:
                    pass
    return trades

# Get data
lines = get_latest_logs()
scans, prices, events = parse_logs(lines)
trades = load_trades()

# Sidebar
with st.sidebar:
    st.header("⚙️ System Control")
    
    # Check if system is running
    if os.path.exists('aimn_crypto_trading.log'):
        mod_time = os.path.getmtime('aimn_crypto_trading.log')
        seconds_ago = (datetime.now().timestamp() - mod_time)
        
        if seconds_ago < 60:
            st.success(f"🟢 System Active ({int(seconds_ago)}s ago)")
        elif seconds_ago < 300:
            st.warning(f"🟡 System Idle ({int(seconds_ago/60)}m ago)")
        else:
            st.error(f"🔴 System Stopped ({int(seconds_ago/60)}m ago)")
    
    # Auto refresh
    auto_refresh = st.checkbox("Auto-refresh (3s)", value=True)
    
    # Show config
    with st.expander("📊 Configuration"):
        st.text("Symbols: 7 cryptos")
        st.text("Scan Interval: 30s")
        st.text("Strategy: Triple confirmation")
        st.text("- RSI (30/70)")
        st.text("- MACD crossover")
        st.text("- Volume confirmation")

# Main content
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_trades = len(trades)
    st.metric("Total Trades", total_trades)

with col2:
    if total_trades > 0:
        winning = len([t for t in trades if t.get('pnl', 0) > 0])
        win_rate = (winning / total_trades) * 100
        st.metric("Win Rate", f"{win_rate:.1f}%")
    else:
        st.metric("Win Rate", "N/A")

with col3:
    total_pnl = sum(t.get('pnl', 0) for t in trades)
    st.metric("Total P&L", f"${total_pnl:,.2f}")

with col4:
    st.metric("Scans Today", len(scans))

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Live Prices", "📈 Activity Monitor", "💰 Trades", "📋 Raw Logs"])

with tab1:
    st.subheader("Current Crypto Prices")
    
    if prices:
        # Create price grid
        cols = st.columns(3)
        for i, (symbol, price) in enumerate(prices.items()):
            with cols[i % 3]:
                # Price card
                st.info(f"""
                **{symbol}**  
                ${price:,.2f}
                """)
    else:
        st.warning("Waiting for price data...")

with tab2:
    st.subheader("System Activity")
    
    # Recent scans
    if scans:
        latest_scan = scans[-1]
        st.success(f"Last scan: {latest_scan['time']} - {latest_scan['message']}")
    
    # Activity feed
    st.subheader("Recent Events")
    
    if events:
        # Show last 20 events
        for event in reversed(events[-20:]):
            if event['type'] == 'opportunity':
                st.info(event['message'])
            elif event['type'] == 'trade':
                st.success(event['message'])
            elif event['type'] == 'no_signal':
                st.text(event['message'])
            else:
                st.text(f"{event['time']}: {event['message']}")
    else:
        st.info("Waiting for trading signals...")
        st.text("The system scans every 30 seconds for opportunities.")
        st.text("When RSI, MACD, and Volume align, you'll see trades here!")

with tab3:
    st.subheader("Trade History")
    
    if trades:
        df = pd.DataFrame(trades)
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_trade = df['pnl'].mean()
            st.metric("Avg Trade", f"${avg_trade:.2f}")
        with col2:
            best_trade = df['pnl'].max()
            st.metric("Best Trade", f"${best_trade:.2f}")
        with col3:
            worst_trade = df['pnl'].min()
            st.metric("Worst Trade", f"${worst_trade:.2f}")
        
        # Trade table
        st.dataframe(df[['timestamp', 'symbol', 'direction', 'pnl']], use_container_width=True)
    else:
        st.info("No completed trades yet. The system is being patient and selective!")

with tab4:
    st.subheader("Raw Log Output")
    
    # Show raw logs
    if st.button("Refresh Logs"):
        lines = get_latest_logs(num_lines=50)
    
    if lines:
        # Show in reverse order (newest first)
        log_text = ''.join(reversed(lines[-30:]))
        st.text_area("Recent Logs", log_text, height=400)
    
    # Log stats
    st.info(f"Log file size: {os.path.getsize('aimn_crypto_trading.log') / 1024:.1f} KB")

# Auto refresh
if auto_refresh:
    time.sleep(3)
    st.rerun()

# Footer
st.markdown("---")
st.info("💡 **Why no trades yet?** Your system uses triple confirmation (RSI + MACD + Volume). "
        "This selective approach waits for high-probability setups. Keep it running - opportunities will come!")