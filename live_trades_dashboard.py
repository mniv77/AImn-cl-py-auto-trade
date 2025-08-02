# SAVE THIS FILE AS: live_trades_dashboard.py
# LOCATION: C:\Users\mniv7\Documents\meir\cl-py\live_trades_dashboard.py

"""
Live trading dashboard that shows active positions with real-time P&L
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import time
import re
from alpaca.trading.client import TradingClient
from alpaca.data import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoLatestQuoteRequest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="AIMn Live Trades Monitor",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize Alpaca clients
@st.cache_resource
def init_alpaca():
    api_key = os.getenv('ALPACA_API_KEY')
    api_secret = os.getenv('ALPACA_SECRET_KEY')
    paper = os.getenv('ALPACA_PAPER', 'true').lower() == 'true'
    
    trading_client = TradingClient(api_key, api_secret, paper=paper)
    crypto_client = CryptoHistoricalDataClient()
    
    return trading_client, crypto_client

trading_client, crypto_client = init_alpaca()

# Custom CSS
st.markdown("""
<style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
    }
    .profit {
        color: #00ff00;
    }
    .loss {
        color: #ff0000;
    }
    .position-card {
        background-color: #1f1f1f;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border: 2px solid #333;
    }
</style>
""", unsafe_allow_html=True)

def get_current_prices(symbols):
    """Get current prices for all symbols"""
    prices = {}
    for symbol in symbols:
        try:
            request = CryptoLatestQuoteRequest(symbol_or_symbols=symbol)
            quotes = crypto_client.get_crypto_latest_quote(request)
            if symbol in quotes:
                prices[symbol] = float(quotes[symbol].ask_price)
        except:
            prices[symbol] = 0
    return prices

def parse_active_positions_from_log():
    """Parse the log file to find active positions"""
    positions = {}
    log_file = 'aimn_crypto_trading.log'
    
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()[-500:]  # Last 500 lines
            
        for line in reversed(lines):  # Start from newest
            # Look for trade execution
            if 'TRADE EXECUTED: BUY' in line:
                match = re.search(r'BUY ([\d.]+) units of (\S+) @ \$([\d,]+\.?\d*)', line)
                if match:
                    qty = float(match.group(1))
                    symbol = match.group(2)
                    price = float(match.group(3).replace(',', ''))
                    
                    if symbol not in positions:
                        positions[symbol] = {
                            'qty': qty,
                            'entry_price': price,
                            'direction': 'BUY',
                            'entry_time': line[:19]
                        }
    
    return positions

def main():
    st.title("💰 AIMn Live Trading Monitor")
    st.markdown("**Real-time P&L for Active Positions**")
    
    # Get account info
    try:
        account = trading_client.get_account()
        portfolio_value = float(account.portfolio_value)
        buying_power = float(account.buying_power)
        cash = float(account.cash)
    except:
        portfolio_value = 0
        buying_power = 0
        cash = 0
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Portfolio Value", f"${portfolio_value:,.2f}")
    with col2:
        st.metric("Buying Power", f"${buying_power:,.2f}")
    with col3:
        st.metric("Cash", f"${cash:,.2f}")
    with col4:
        st.metric("Equity", f"${portfolio_value - cash:,.2f}")
    
    st.markdown("---")
    
    # Get active positions
    positions = parse_active_positions_from_log()
    
    if positions:
        st.header("📊 Active Positions")
        
        # Get current prices
        symbols = list(positions.keys())
        current_prices = get_current_prices(symbols)
        
        # Calculate P&L for each position
        total_pnl = 0
        
        for symbol, pos in positions.items():
            current_price = current_prices.get(symbol, pos['entry_price'])
            
            # Calculate P&L
            position_value = pos['qty'] * current_price
            cost_basis = pos['qty'] * pos['entry_price']
            pnl = position_value - cost_basis
            pnl_pct = (pnl / cost_basis) * 100 if cost_basis > 0 else 0
            total_pnl += pnl
            
            # Display position card
            pnl_color = "profit" if pnl >= 0 else "loss"
            
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                with col1:
                    st.markdown(f"### {symbol}")
                    st.text(f"Position: {pos['qty']:.4f} units")
                
                with col2:
                    st.markdown("**Entry**")
                    st.text(f"${pos['entry_price']:,.2f}")
                
                with col3:
                    st.markdown("**Current**")
                    st.text(f"${current_price:,.2f}")
                
                with col4:
                    st.markdown("**P&L**")
                    st.markdown(f"<p class='{pnl_color}'>${pnl:,.2f}<br/>({pnl_pct:+.2f}%)</p>", 
                              unsafe_allow_html=True)
            
            # Progress bar showing position status
            if pos['direction'] == 'BUY':
                # For BUY positions, show progress to profit targets
                progress = min(max(pnl_pct / 5 * 100, 0), 100)  # Progress to 5% target
                st.progress(progress / 100)
                
                if pnl_pct >= 5:
                    st.success("🟢 Peak trail active (5% target reached!)")
                elif pnl_pct >= 1:
                    st.info("🔵 Early trail active (1% target reached)")
                elif pnl_pct <= -2:
                    st.error("🔴 Near stop loss (-2%)")
            
            st.markdown("---")
        
        # Total P&L summary
        st.header("💵 Total P&L")
        total_color = "profit" if total_pnl >= 0 else "loss"
        st.markdown(f"<p class='big-font {total_color}'>${total_pnl:,.2f}</p>", 
                   unsafe_allow_html=True)
        
    else:
        st.info("No active positions found. Waiting for trades...")
    
    # Recent trades from log
    st.header("📜 Recent Activity")
    
    if os.path.exists('aimn_crypto_trading.log'):
        with open('aimn_crypto_trading.log', 'r', encoding='utf-8') as f:
            lines = f.readlines()[-20:]
        
        activities = []
        for line in reversed(lines):
            if any(key in line for key in ['TRADE EXECUTED', 'Opportunity found', 'EXIT ORDER']):
                activities.append(line.strip())
        
        for activity in activities[:5]:  # Show last 5 activities
            if 'TRADE EXECUTED' in activity:
                st.success(activity)
            elif 'Opportunity found' in activity:
                st.info(activity)
            elif 'EXIT ORDER' in activity:
                st.warning(activity)
    
    # Auto refresh
    st.markdown("---")
    auto_refresh = st.checkbox("Auto-refresh (5 seconds)", value=True)
    
    if auto_refresh:
        time.sleep(5)
        st.rerun()

if __name__ == "__main__":
    main()