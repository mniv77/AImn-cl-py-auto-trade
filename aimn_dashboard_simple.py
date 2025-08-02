"""
Save this as aimn_dashboard_simple.py and run it
This version will work with your config structure
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import re

st.set_page_config(page_title="AIMn Trading Dashboard", page_icon="📈", layout="wide")

st.title("🚀 AIMn Trading System Dashboard")
st.markdown("**Let the market pick your trades. Let logic pick your exits.**")

# Load config safely
try:
    import aimn_crypto_config as config
    SYMBOLS = config.SYMBOLS
    SCAN_INTERVAL = config.SCAN_INTERVAL
    CAPITAL_PER_TRADE = config.CAPITAL_PER_TRADE
except:
    SYMBOLS = ['BTC/USD', 'ETH/USD']
    SCAN_INTERVAL = 30
    CAPITAL_PER_TRADE = 0.3

# Parse log file
def parse_log(log_path='aimn_crypto_trading.log', last_n=100):
    events = []
    positions = {}
    
    if os.path.exists(log_path):
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()[-last_n:]
        
        for line in lines:
            if '💡 Opportunity found' in line:
                events.append(('opportunity', line.strip()))
            elif '🎯 TRADE EXECUTED' in line:
                events.append(('trade', line.strip()))
            elif '🚪 EXIT ORDER PLACED' in line:
                events.append(('exit', line.strip()))
            elif '📊 Active position' in line:
                # Extract position info
                match = re.search(r'(\S+) (\w+) \| .*P&L: \$([\d,.-]+) \(([\d.-]+)%\)', line)
                if match:
                    positions[match.group(1)] = {
                        'direction': match.group(2),
                        'pnl': float(match.group(3).replace(',', '')),
                        'pnl_pct': float(match.group(4))
                    }
    
    return events, positions

# Load trades
def load_trades():
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
events, positions = parse_log()
trades = load_trades()

# Sidebar
st.sidebar.header("⚙️ System Status")
if os.path.exists('aimn_crypto_trading.log'):
    mod_time = datetime.fromtimestamp(os.path.getmtime('aimn_crypto_trading.log'))
    if (datetime.now() - mod_time).seconds < 60:
        st.sidebar.success("🟢 System Running")
    else:
        st.sidebar.warning("🟡 System Idle")
else:
    st.sidebar.error("🔴 Log not found")

# Metrics
col1, col2, col3, col4 = st.columns(4)

total_trades = len(trades)
winning_trades = len([t for t in trades if t.get('pnl', 0) > 0])
win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
total_pnl = sum(t.get('pnl', 0) for t in trades)

with col1:
    st.metric("Total Trades", total_trades)
with col2:
    st.metric("Win Rate", f"{win_rate:.1f}%")
with col3:
    st.metric("Total P&L", f"${total_pnl:,.2f}")
with col4:
    st.metric("Active Positions", len(positions))

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Positions", "📈 Performance", "📰 Events"])

with tab1:
    st.subheader("Active Positions")
    if positions:
        for symbol, pos in positions.items():
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**{symbol}** - {pos['direction']}")
            with col2:
                color = "green" if pos['pnl'] > 0 else "red"
                st.markdown(f"<span style='color:{color}'>P&L: ${pos['pnl']:,.2f}</span>", 
                          unsafe_allow_html=True)
            with col3:
                st.write(f"{pos['pnl_pct']:.1f}%")
    else:
        st.info("No active positions")

with tab2:
    st.subheader("Trade Performance")
    if trades:
        df = pd.DataFrame(trades)
        st.line_chart(df['pnl'].cumsum())
        
        # Recent trades
        st.subheader("Recent Trades")
        recent = df.tail(10)
        st.dataframe(recent[['timestamp', 'symbol', 'direction', 'pnl']])
    else:
        st.info("No trades yet")

with tab3:
    st.subheader("Recent Events")
    for event_type, message in events[-20:][::-1]:
        if event_type == 'trade':
            st.success(message)
        elif event_type == 'opportunity':
            st.info(message)
        elif event_type == 'exit':
            st.warning(message)

# Auto refresh
if st.sidebar.checkbox("Auto-refresh", value=True):
    import time
    time.sleep(5)
    st.rerun()