import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import time
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path
import os
import re

# Page config
st.set_page_config(
    page_title="AIMn Trading Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stMetric {
        background-color: #1f1f1f;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #333;
    }
    .positive {
        color: #00ff00;
    }
    .negative {
        color: #ff0000;
    }
    div[data-testid="metric-container"] {
        background-color: rgba(28, 28, 28, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.4);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()
if 'active_positions' not in st.session_state:
    st.session_state.active_positions = {}

def load_config():
    """Load configuration from aimn_crypto_config.py"""
    try:
        import aimn_crypto_config as config
        return config
    except:
        # Default config if file not found
        return type('obj', (object,), {
            'SYMBOLS': ['BTC/USD', 'ETH/USD', 'LTC/USD'],
            'SCAN_INTERVAL': 30,
            'CAPITAL_PER_TRADE': 0.3,
            'RSI_PERIOD': 14,
            'RSI_OVERSOLD': 30,
            'RSI_OVERBOUGHT': 70,
            'STOP_LOSS': 2.0,
            'EARLY_TRAIL_START': 1.0,
            'EARLY_TRAIL_MINUS': 15.0,
            'PEAK_TRAIL_START': 5.0,
            'PEAK_TRAIL_MINUS': 0.5
        })

def parse_log_file(log_path, last_n_lines=200):
    """Parse the trading log file for recent events"""
    events = []
    positions = {}
    
    if os.path.exists(log_path):
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()[-last_n_lines:]
            
        for line in lines:
            try:
                # Extract timestamp
                timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                if timestamp_match:
                    timestamp = timestamp_match.group(1)
                else:
                    continue
                
                # Parse different event types
                if '💡 Opportunity found' in line:
                    match = re.search(r'Opportunity found: (\S+) (\w+) \(score: ([\d.]+)\)', line)
                    if match:
                        events.append({
                            'time': timestamp,
                            'type': 'opportunity',
                            'symbol': match.group(1),
                            'direction': match.group(2),
                            'score': float(match.group(3)),
                            'message': line.strip()
                        })
                
                elif '🎯 TRADE EXECUTED' in line:
                    match = re.search(r'TRADE EXECUTED: (\w+) ([\d.]+) units of (\S+) @ \$([\d,]+\.?\d*)', line)
                    if match:
                        events.append({
                            'time': timestamp,
                            'type': 'trade',
                            'direction': match.group(1),
                            'quantity': float(match.group(2)),
                            'symbol': match.group(3),
                            'price': float(match.group(4).replace(',', '')),
                            'message': line.strip()
                        })
                
                elif '🚪 EXIT ORDER PLACED' in line:
                    match = re.search(r'EXIT ORDER PLACED: (\w+) ([\d.]+) units of (\S+)', line)
                    if match:
                        events.append({
                            'time': timestamp,
                            'type': 'exit',
                            'action': match.group(1),
                            'quantity': float(match.group(2)),
                            'symbol': match.group(3),
                            'message': line.strip()
                        })
                
                elif '📊 Active position' in line:
                    # Parse active position update
                    match = re.search(r'Active position: (\S+) (\w+) \| Entry: \$([\d,]+\.?\d*) \| Current: \$([\d,]+\.?\d*) \| P&L: \$([\d,.-]+) \(([\d.-]+)%\)', line)
                    if match:
                        symbol = match.group(1)
                        positions[symbol] = {
                            'time': timestamp,
                            'symbol': symbol,
                            'direction': match.group(2),
                            'entry_price': float(match.group(3).replace(',', '')),
                            'current_price': float(match.group(4).replace(',', '')),
                            'pnl': float(match.group(5).replace(',', '')),
                            'pnl_pct': float(match.group(6))
                        }
                        
                        # Check for trailing stops
                        if '🔵 Early trail active' in line:
                            match2 = re.search(r'Early trail active: \$([\d,]+\.?\d*)', line)
                            if match2:
                                positions[symbol]['early_trail'] = float(match2.group(1).replace(',', ''))
                        
                        if '🟢 Peak trail active' in line:
                            match2 = re.search(r'Peak trail active: \$([\d,]+\.?\d*)', line)
                            if match2:
                                positions[symbol]['peak_trail'] = float(match2.group(1).replace(',', ''))
                
                elif 'No valid signals found' in line:
                    events.append({
                        'time': timestamp,
                        'type': 'no_signal',
                        'message': 'No valid signals found'
                    })
                    
            except Exception as e:
                pass
    
    # Update session state with active positions
    st.session_state.active_positions = positions
    
    return events, positions

def load_trades():
    """Load trade history from JSON file"""
    trades = []
    if os.path.exists('aimn_trades.json'):
        with open('aimn_trades.json', 'r') as f:
            for line in f:
                try:
                    trades.append(json.loads(line))
                except:
                    pass
    return trades

def create_signal_indicator(value, min_val, max_val, title):
    """Create a gauge indicator for signal strength"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title},
        gauge = {
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [min_val, 30], 'color': "lightgreen"},
                {'range': [30, 70], 'color': "gray"},
                {'range': [70, max_val], 'color': "lightcoral"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 70 if title == "RSI" else 50
            }
        }
    ))
    
    fig.update_layout(
        height=200,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "white"}
    )
    
    return fig

def create_position_chart(positions):
    """Create a chart showing current positions with P&L"""
    if not positions:
        fig = go.Figure()
        fig.add_annotation(
            text="No Active Positions",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20, color="gray")
        )
    else:
        symbols = list(positions.keys())
        pnl_values = [positions[s]['pnl'] for s in symbols]
        pnl_pcts = [positions[s]['pnl_pct'] for s in symbols]
        colors = ['green' if p > 0 else 'red' for p in pnl_values]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=symbols,
            y=pnl_values,
            text=[f"${p:,.2f}<br>({pct:.1f}%)" for p, pct in zip(pnl_values, pnl_pcts)],
            textposition='outside',
            marker_color=colors
        ))
        
        fig.update_layout(
            title="Active Positions P&L",
            yaxis_title="P&L ($)",
            showlegend=False
        )
    
    fig.update_layout(
        height=300,
        template='plotly_dark',
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    return fig

def create_signal_heatmap(events, config):
    """Create a heatmap showing recent signals for all symbols"""
    # Get last signal for each symbol
    symbol_signals = {}
    for event in events:
        if event['type'] == 'opportunity':
            symbol = event['symbol']
            if symbol not in symbol_signals or event['time'] > symbol_signals[symbol]['time']:
                symbol_signals[symbol] = event
    
    # Create data for all symbols
    data = []
    for symbol in config.SYMBOLS:
        if symbol in symbol_signals:
            sig = symbol_signals[symbol]
            data.append({
                'Symbol': symbol,
                'Last Signal': sig['direction'],
                'Score': sig['score'],
                'Time': sig['time'],
                'Status': 'Active' if symbol in st.session_state.active_positions else 'Ready'
            })
        else:
            data.append({
                'Symbol': symbol,
                'Last Signal': '-',
                'Score': 0,
                'Time': '-',
                'Status': 'Active' if symbol in st.session_state.active_positions else 'Waiting'
            })
    
    df = pd.DataFrame(data)
    
    # Color mapping for status
    status_colors = {
        'Active': '#00ff00',
        'Ready': '#ffff00',
        'Waiting': '#808080'
    }
    
    fig = go.Figure(data=[
        go.Table(
            header=dict(
                values=list(df.columns),
                fill_color='#1f1f1f',
                align='center',
                font=dict(color='white', size=12)
            ),
            cells=dict(
                values=[df[col] for col in df.columns],
                fill_color=[
                    ['#2f2f2f'] * len(df),  # Symbol
                    ['#004000' if v == 'BUY' else '#400000' if v == 'SELL' else '#2f2f2f' for v in df['Last Signal']],  # Signal
                    ['#004000' if v > 70 else '#404000' if v > 30 else '#2f2f2f' for v in df['Score']],  # Score
                    ['#2f2f2f'] * len(df),  # Time
                    [status_colors.get(v, '#2f2f2f') for v in df['Status']]  # Status
                ],
                align='center',
                font=dict(color='white', size=11)
            )
        )
    ])
    
    fig.update_layout(
        height=300,
        template='plotly_dark',
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    return fig

def create_performance_chart(trades):
    """Create cumulative P&L chart"""
    if not trades:
        fig = go.Figure()
        fig.add_annotation(
            text="No Trades Yet",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20, color="gray")
        )
    else:
        df = pd.DataFrame(trades)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        df['cumulative_pnl'] = df['pnl'].cumsum()
        
        fig = go.Figure()
        
        # Add cumulative P&L line
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['cumulative_pnl'],
            mode='lines+markers',
            name='Cumulative P&L',
            line=dict(color='green' if df['cumulative_pnl'].iloc[-1] > 0 else 'red', width=2),
            fill='tozeroy'
        ))
        
        # Add individual trades as markers
        win_trades = df[df['pnl'] > 0]
        loss_trades = df[df['pnl'] <= 0]
        
        if not win_trades.empty:
            fig.add_trace(go.Scatter(
                x=win_trades['timestamp'],
                y=win_trades['cumulative_pnl'],
                mode='markers',
                name='Winning Trades',
                marker=dict(color='green', size=10, symbol='triangle-up')
            ))
        
        if not loss_trades.empty:
            fig.add_trace(go.Scatter(
                x=loss_trades['timestamp'],
                y=loss_trades['cumulative_pnl'],
                mode='markers',
                name='Losing Trades',
                marker=dict(color='red', size=10, symbol='triangle-down')
            ))
    
    fig.update_layout(
        height=400,
        template='plotly_dark',
        title='Cumulative P&L Over Time',
        xaxis_title='Time',
        yaxis_title='P&L ($)',
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    return fig

# Main Dashboard
st.title("🚀 AIMn Trading System Dashboard")
st.markdown("**Let the market pick your trades. Let logic pick your exits.**")

# Load data
config = load_config()
events, positions = parse_log_file('aimn_crypto_trading.log')
trades = load_trades()

# Sidebar
st.sidebar.header("⚙️ System Control")

# Auto-refresh
auto_refresh = st.sidebar.checkbox("Auto-refresh (5s)", value=True)
refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 1, 30, 5)

# System Status
if os.path.exists('aimn_crypto_trading.log'):
    # Check if system is running (recent log entries)
    log_mod_time = datetime.fromtimestamp(os.path.getmtime('aimn_crypto_trading.log'))
    time_since_update = (datetime.now() - log_mod_time).total_seconds()
    
    if time_since_update < 60:  # Updated within last minute
        st.sidebar.success("🟢 System Running")
    else:
        st.sidebar.warning(f"🟡 System Idle ({int(time_since_update/60)}m)")
else:
    st.sidebar.error("🔴 System Not Started")

st.sidebar.info(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")

# Configuration Display
with st.sidebar.expander("📊 Configuration"):
    st.text(f"Symbols: {len(config.SYMBOLS)}")
    st.text(f"Scan Interval: {config.SCAN_INTERVAL}s")
    st.text(f"Capital/Trade: {config.CAPITAL_PER_TRADE*100}%")
    st.text(f"Stop Loss: {config.STOP_LOSS}%")
    st.text(f"RSI: {config.RSI_OVERSOLD}/{config.RSI_OVERBOUGHT}")

# Main metrics row
col1, col2, col3, col4, col5 = st.columns(5)

# Calculate metrics
total_trades = len(trades)
winning_trades = len([t for t in trades if t.get('pnl', 0) > 0])
win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
total_pnl = sum(t.get('pnl', 0) for t in trades)
avg_trade = total_pnl / total_trades if total_trades > 0 else 0
active_positions_count = len(positions)

with col1:
    st.metric("Total Trades", total_trades)
with col2:
    st.metric("Win Rate", f"{win_rate:.1f}%", 
              delta=f"{winning_trades}W/{total_trades-winning_trades}L" if total_trades > 0 else "No trades")
with col3:
    st.metric("Total P&L", f"${total_pnl:,.2f}", 
              delta=f"${avg_trade:.2f} avg" if total_trades > 0 else None)
with col4:
    st.metric("Active Positions", active_positions_count,
              delta=f"{sum(p['pnl'] for p in positions.values()):.2f}" if positions else None)
with col5:
    # Recent opportunities
    recent_opps = len([e for e in events[-20:] if e['type'] == 'opportunity'])
    st.metric("Recent Signals", recent_opps, delta="last 20 events")

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Live Positions", "🎯 Signal Scanner", "📈 Performance", "📋 Trade History", "📰 Event Log"])

with tab1:
    st.subheader("Current Positions & Market Status")
    
    # Active positions chart
    position_chart = create_position_chart(positions)
    st.plotly_chart(position_chart, use_container_width=True)
    
    # Position details
    if positions:
        st.subheader("Position Details")
        for symbol, pos in positions.items():
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"**{symbol}**")
                st.text(f"Direction: {pos['direction']}")
            
            with col2:
                st.text(f"Entry: ${pos['entry_price']:,.2f}")
                st.text(f"Current: ${pos['current_price']:,.2f}")
            
            with col3:
                color = "green" if pos['pnl'] > 0 else "red"
                st.markdown(f"<span style='color:{color}'>P&L: ${pos['pnl']:,.2f} ({pos['pnl_pct']:.1f}%)</span>", 
                          unsafe_allow_html=True)
            
            with col4:
                if 'early_trail' in pos:
                    st.text(f"🔵 Early Trail: ${pos['early_trail']:,.2f}")
                if 'peak_trail' in pos:
                    st.text(f"🟢 Peak Trail: ${pos['peak_trail']:,.2f}")
            
            st.markdown("---")

with tab2:
    st.subheader("Multi-Symbol Signal Scanner")
    
    # Signal heatmap
    signal_heatmap = create_signal_heatmap(events, config)
    st.plotly_chart(signal_heatmap, use_container_width=True)
    
    # Recent opportunities
    st.subheader("Recent Trading Opportunities")
    recent_opportunities = [e for e in events if e['type'] == 'opportunity'][-10:]
    
    if recent_opportunities:
        for opp in reversed(recent_opportunities):
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.text(f"{opp['time']} - {opp['symbol']}")
            with col2:
                color = "green" if opp['direction'] == 'BUY' else "red"
                st.markdown(f"<span style='color:{color}'>{opp['direction']}</span>", unsafe_allow_html=True)
            with col3:
                st.text(f"Score: {opp['score']:.1f}")
    else:
        st.info("No recent opportunities. The system is scanning...")

with tab3:
    st.subheader("Trading Performance Analytics")
    
    # Performance chart
    perf_chart = create_performance_chart(trades)
    st.plotly_chart(perf_chart, use_container_width=True)
    
    if trades:
        col1, col2 = st.columns(2)
        
        with col1:
            # P&L Distribution
            df = pd.DataFrame(trades)
            fig = px.histogram(df, x='pnl', nbins=20, 
                             title='P&L Distribution',
                             color_discrete_sequence=['#00ff00'])
            fig.update_layout(template='plotly_dark', height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Trade Statistics
            st.markdown("### Trade Statistics")
            
            # Calculate additional metrics
            if len(trades) > 0:
                avg_win = df[df['pnl'] > 0]['pnl'].mean() if len(df[df['pnl'] > 0]) > 0 else 0
                avg_loss = df[df['pnl'] <= 0]['pnl'].mean() if len(df[df['pnl'] <= 0]) > 0 else 0
                profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Avg Win", f"${avg_win:.2f}")
                    st.metric("Profit Factor", f"{profit_factor:.2f}")
                with col2:
                    st.metric("Avg Loss", f"${avg_loss:.2f}")
                    st.metric("Max Drawdown", f"${df['pnl'].min():.2f}")

with tab4:
    st.subheader("Trade History")
    
    if trades:
        # Convert to DataFrame for display
        df = pd.DataFrame(trades)
        
        # Format columns
        display_df = df.copy()
        display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
        display_df['entry_price'] = display_df['entry_price'].apply(lambda x: f"${x:,.2f}")
        display_df['exit_price'] = display_df['exit_price'].apply(lambda x: f"${x:,.2f}")
        display_df['pnl'] = display_df['pnl'].apply(lambda x: f"${x:,.2f}")
        
        # Select columns to display
        columns_to_show = ['timestamp', 'symbol', 'direction', 'quantity', 'entry_price', 'exit_price', 'pnl', 'exit_reason']
        if all(col in display_df.columns for col in columns_to_show):
            st.dataframe(display_df[columns_to_show], use_container_width=True)
        else:
            st.dataframe(display_df, use_container_width=True)
    else:
        st.info("No trades yet. The system is waiting for optimal entry conditions...")

with tab5:
    st.subheader("System Event Log")
    
    # Filter events
    event_types = st.multiselect(
        "Filter Events",
        options=['opportunity', 'trade', 'exit', 'position_update', 'no_signal'],
        default=['opportunity', 'trade', 'exit']
    )
    
    # Show filtered events
    filtered_events = [e for e in events if e['type'] in event_types][-50:]
    
    for event in reversed(filtered_events):
        if event['type'] == 'trade':
            st.success(f"🎯 {event['time']}: TRADE - {event['direction']} {event['quantity']:.4f} {event['symbol']} @ ${event['price']:,.2f}")
        elif event['type'] == 'opportunity':
            st.info(f"💡 {event['time']}: SIGNAL - {event['symbol']} {event['direction']} (score: {event['score']:.1f})")
        elif event['type'] == 'exit':
            st.warning(f"🚪 {event['time']}: EXIT - {event['action']} {event['quantity']:.4f} {event['symbol']}")
        elif event['type'] == 'no_signal':
            st.text(f"⏸️ {event['time']}: {event['message']}")

# Auto-refresh
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()

# Footer
st.markdown("---")
st.markdown("**AIMn Trading System** | Real-time monitoring dashboard | Created with ❤️ using Streamlit")
