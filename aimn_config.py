# aimn_config.py
"""
AIMn Trading System Configuration
Adjust these parameters to control trading behavior
"""

# Symbols to trade
SYMBOLS = ['AAPL', 'MSFT', 'TSLA', 'GOOGL', 'NVDA']

# How much capital to use per trade (0.2 = 20%)
CAPITAL_PER_TRADE = 0.2

# Scanning interval in seconds (60 = check every minute)
SCAN_INTERVAL = 60

# Paper trading or live
PAPER_TRADING = True  # Keep True for safety!

# Symbol-specific parameters
# These are OPTIMIZED for more trading opportunities
SYMBOL_PARAMS = {
    # Default parameters (used for any symbol not specifically configured)
    'DEFAULT': {
        # RSI Real parameters
        'rsi_window': 100,          # Lookback period for RSI Real
        'rsi_overbought': 75,       # Loosened from 70 for more SELL signals
        'rsi_oversold': 25,         # Loosened from 30 for more BUY signals
        
        # MACD parameters
        'macd_fast': 12,
        'macd_slow': 26,
        'macd_signal': 9,
        
        # Volume filter (lower = more trades)
        'volume_threshold': 0.8,    # Reduced from 1.0 - just need 80% of average volume
        
        # ATR volatility filter (lower = more trades)
        'atr_multiplier': 1.1,      # Reduced from 1.3 - less volatility required
        'atr_period': 14,
        'atr_ma_period': 28,
        
        # Exit parameters (keep these tight for risk management)
        'stop_loss_percent': 2.0,   # 2% stop loss
        'early_trail_start': 1.0,   # Start loose trail at 1% profit
        'early_trail_minus': 15.0,  # Trail 15% from peak (loose)
        'peak_trail_start': 5.0,    # Start tight trail at 5% profit
        'peak_trail_minus': 0.5,    # Trail 0.5% from peak (tight)
        
        # Optional RSI exit
        'use_rsi_exit': True,
        'rsi_exit_min_profit': 0.5, # Exit on RSI reversal if >0.5% profit
        
        # Other parameters
        'obv_period': 20
    },
    
    # AAPL - Large cap, less volatile
    'AAPL': {
        'rsi_window': 100,
        'rsi_overbought': 75,
        'rsi_oversold': 25,
        'stop_loss_percent': 2.0,
        'early_trail_start': 1.0,
        'early_trail_minus': 15.0,
        'peak_trail_start': 5.0,
        'peak_trail_minus': 0.5,
        'volume_threshold': 0.8,
        'atr_multiplier': 1.1,
        'use_rsi_exit': True,
        'rsi_exit_min_profit': 0.5
    },
    
    # TSLA - More volatile
    'TSLA': {
        'rsi_window': 120,
        'rsi_overbought': 80,       # Higher threshold for volatile stock
        'rsi_oversold': 20,         # Lower threshold for volatile stock
        'stop_loss_percent': 3.0,   # Wider stop for volatility
        'early_trail_start': 1.5,   # Let it run more
        'early_trail_minus': 20.0,  # Looser trail
        'peak_trail_start': 7.0,    # Higher profit target
        'peak_trail_minus': 0.7,    # Still tight when winning big
        'volume_threshold': 0.7,    # Lower threshold - TSLA always has volume
        'atr_multiplier': 1.0,      # Lower - TSLA is always volatile
        'use_rsi_exit': True,
        'rsi_exit_min_profit': 1.0
    },
    
    # NVDA - Volatile tech stock
    'NVDA': {
        'rsi_window': 100,
        'rsi_overbought': 80,
        'rsi_oversold': 20,
        'stop_loss_percent': 3.0,
        'early_trail_start': 1.5,
        'early_trail_minus': 20.0,
        'peak_trail_start': 8.0,
        'peak_trail_minus': 0.8,
        'volume_threshold': 0.7,
        'atr_multiplier': 1.0,
        'use_rsi_exit': True,
        'rsi_exit_min_profit': 1.0
    }
}

# Apply default parameters to any symbol not specifically configured
for symbol in SYMBOLS:
    if symbol not in SYMBOL_PARAMS:
        SYMBOL_PARAMS[symbol] = SYMBOL_PARAMS['DEFAULT'].copy()

# Logging configuration
LOG_LEVEL = 'INFO'  # DEBUG for more details
LOG_FILE = 'aimn_trading.log'

# Alert settings (future enhancement)
ENABLE_ALERTS = False
ALERT_EMAIL = 'your-email@example.com'

# Performance tracking
TRACK_PERFORMANCE = True
PERFORMANCE_FILE = 'aimn_performance.csv'

# Backtesting configuration
BACKTEST_DAYS = 60  # How many days to backtest
BACKTEST_STARTING_CAPITAL = 100000  # $100k for backtesting

print("✅ Configuration loaded!")
print(f"   Symbols: {', '.join(SYMBOLS)}")
print(f"   Capital per trade: {CAPITAL_PER_TRADE*100}%")
print(f"   Scan interval: {SCAN_INTERVAL} seconds")
print(f"   Mode: {'PAPER' if PAPER_TRADING else 'LIVE'} TRADING")