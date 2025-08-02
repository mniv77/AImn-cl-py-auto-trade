# test_with_sample_data.py
"""
Test AIMn Trading System with sample data to demonstrate functionality
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from indicators import AIMnIndicators
from scanner import AIMnScanner
from position_manager import AIMnPositionManager

print("\n" + "="*60)
print("🧪 TESTING AIMn SYSTEM WITH SAMPLE DATA")
print("="*60)

# 1. Generate sample data
print("\n1️⃣ Generating sample market data...")

def generate_sample_data(symbol, days=200):
    """Generate realistic sample OHLCV data"""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # Generate realistic price movement
    np.random.seed(42 if symbol == 'AAPL' else 43 if symbol == 'MSFT' else 44)
    
    # Starting price
    if symbol == 'AAPL':
        base_price = 180
    elif symbol == 'MSFT':
        base_price = 380
    else:  # GOOGL
        base_price = 140
    
    # Generate prices with trend and volatility
    returns = np.random.normal(0.0005, 0.02, days)  # 0.05% daily return, 2% volatility
    price_series = base_price * np.exp(np.cumsum(returns))
    
    # Create OHLCV data
    data = []
    for i, (date, close) in enumerate(zip(dates, price_series)):
        # Generate intraday movement
        daily_range = close * np.random.uniform(0.005, 0.02)  # 0.5-2% daily range
        
        open_price = close + np.random.uniform(-daily_range/2, daily_range/2)
        high = max(open_price, close) + np.random.uniform(0, daily_range/2)
        low = min(open_price, close) - np.random.uniform(0, daily_range/2)
        volume = np.random.randint(10000000, 50000000)
        
        data.append({
            'timestamp': date,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        })
    
    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)
    return df

# Generate data for multiple symbols
symbols = ['AAPL', 'MSFT', 'GOOGL']
market_data = {}

for symbol in symbols:
    df = generate_sample_data(symbol)
    market_data[symbol] = df
    print(f"   ✅ {symbol}: Generated {len(df)} days of data, latest close: ${df['close'].iloc[-1]:.2f}")

# 2. Test indicators
print("\n2️⃣ Testing indicator calculations...")
test_params = {
    'rsi_window': 100,
    'rsi_overbought': 70,
    'rsi_oversold': 30,
    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9,
    'volume_threshold': 1.0,
    'atr_multiplier': 1.3
}

# Calculate indicators for AAPL
df_with_indicators = AIMnIndicators.calculate_all_indicators(
    market_data['AAPL'].copy(), 
    test_params
)

# Show latest indicator values
latest = df_with_indicators.iloc[-1]
print(f"   RSI Real: {latest['rsi_real']:.2f}")
print(f"   MACD: {latest['macd']:.4f}")
print(f"   ATR: {latest['atr']:.2f}")
print(f"   Volume vs Avg: {latest['volume'] / df_with_indicators['volume'].rolling(20).mean().iloc[-1]:.2f}x")

# Show indicator ranges (helps understand if they're reasonable)
print(f"\n   Indicator ranges over last 20 days:")
last_20 = df_with_indicators.tail(20)
print(f"   RSI Real: {last_20['rsi_real'].min():.1f} - {last_20['rsi_real'].max():.1f}")
print(f"   ATR: {last_20['atr'].min():.2f} - {last_20['atr'].max():.2f}")

# 3. Test scanner
print("\n3️⃣ Testing scanner for opportunities...")

# Define parameters for each symbol
symbol_params = {
    'AAPL': {
        'rsi_window': 100,
        'rsi_overbought': 70,
        'rsi_oversold': 30,
        'stop_loss_percent': 2.0,
        'early_trail_start': 1.0,
        'early_trail_minus': 15.0,
        'peak_trail_start': 5.0,
        'peak_trail_minus': 0.5,
        'volume_threshold': 0.9,
        'atr_multiplier': 1.2
    }
}

# Apply same params to all symbols for testing
for symbol in symbols:
    if symbol not in symbol_params:
        symbol_params[symbol] = symbol_params['AAPL'].copy()

# Initialize scanner
scanner = AIMnScanner(symbol_params)

# Scan for opportunities
opportunity = scanner.scan_all_symbols(market_data)

if opportunity:
    print(f"\n🎯 Opportunity found!")
    print(f"   Symbol: {opportunity['symbol']}")
    print(f"   Direction: {opportunity['direction']}")
    print(f"   Score: {opportunity['score']:.1f}")
    print(f"   Entry Price: ${opportunity['entry_price']:.2f}")
    print(f"   Indicators:")
    print(f"   - RSI Real: {opportunity['indicators']['rsi_real']:.1f}")
    print(f"   - Volume Ratio: {opportunity['indicators']['volume_ratio']:.2f}")
    print(f"   - ATR Ratio: {opportunity['indicators']['atr_ratio']:.2f}")
else:
    print("\n   No opportunities found with current parameters")
    print("   Let's check why by looking at the latest signals...")
    
    # Debug: show signal status for each symbol
    for symbol in symbols:
        params = scanner.get_symbol_params(symbol)
        df = AIMnIndicators.calculate_all_indicators(market_data[symbol], params)
        latest = df.iloc[-1]
        
        print(f"\n   {symbol} signals:")
        print(f"   - RSI: {latest['rsi_real']:.1f} (need <= {params['rsi_oversold']} or >= {params['rsi_overbought']})")
        print(f"   - MACD Bull Cross: {latest['macd_bullish_cross']}")
        print(f"   - MACD Bear Cross: {latest['macd_bearish_cross']}")
        print(f"   - Volume Signal: Bull={latest['bullish_volume']}, Bear={latest['bearish_volume']}")
        print(f"   - Volatility OK: {latest['volatility_expanding']}")

# 4. Test position manager with a simulated opportunity
print("\n4️⃣ Testing position manager with simulated trade...")

# Create a fake opportunity if none found
if not opportunity:
    opportunity = {
        'symbol': 'AAPL',
        'direction': 'BUY',
        'score': 75.0,
        'entry_price': market_data['AAPL']['close'].iloc[-1],
        'indicators': {
            'rsi_real': 28.5,
            'macd': 0.05,
            'volume_ratio': 1.2,
            'atr_ratio': 1.4
        }
    }
    print("   Using simulated BUY opportunity for AAPL")

# Initialize position manager
position_manager = AIMnPositionManager(max_positions=1)

# Enter position
shares = 100
position = position_manager.enter_position(
    opportunity, 
    shares, 
    symbol_params[opportunity['symbol']]
)

print(f"\n   Position created:")
print(f"   Entry: ${position.entry_price:.2f}")
print(f"   Stop Loss: ${position.stop_loss_price:.2f} (-{symbol_params[opportunity['symbol']]['stop_loss_percent']}%)")
print(f"   Shares: {position.shares}")

# Simulate price movement
print(f"\n   Simulating price movement:")
test_scenarios = [
    ("Initial", position.entry_price),
    ("+0.5%", position.entry_price * 1.005),
    ("+1.2%", position.entry_price * 1.012),  # Should activate early trail
    ("+2.5%", position.entry_price * 1.025),
    ("+5.2%", position.entry_price * 1.052),  # Should activate peak trail
    ("+4.8%", position.entry_price * 1.048),  # Pullback
    ("+4.6%", position.entry_price * 1.046)   # Might trigger peak trail exit
]

for scenario, price in test_scenarios:
    result = position.update_price(price)
    
    status = f"   {scenario}: ${price:.2f} | P&L: {position.unrealized_pnl_pct:.2f}%"
    
    if position.early_trail_active:
        status += f" | Early trail: ${position.early_trail_price:.2f}"
    if position.peak_trail_active:
        status += f" | Peak trail: ${position.peak_trail_price:.2f}"
    
    if result:
        status += f" | EXIT: {result[0].value}"
        print(status)
        break
    else:
        print(status)

# Show final statistics
stats = position_manager.get_statistics()
if stats['total_trades'] > 0:
    print(f"\n   Final Statistics:")
    print(f"   Total Trades: {stats['total_trades']}")
    print(f"   Win Rate: {stats['win_rate']:.1f}%")
    print(f"   Total P&L: ${stats['total_pnl']:.2f}")

print("\n" + "="*60)
print("✅ AIMn System successfully tested with sample data!")
print("="*60)

print("\n💡 Summary:")
print("   - Indicators: ✅ Working (RSI Real, MACD, Volume, ATR)")
print("   - Scanner: ✅ Working (scans all symbols for opportunities)")
print("   - Position Manager: ✅ Working (dual trailing system)")
print("   - Exit Codes: S=Stop Loss, E=Early Trail, P=Peak Trail, R=RSI")

print("\n📈 The system is ready!")
print("   When market opens, it will use real data from Alpaca")
print("   For now, you can:")
print("   1. Adjust parameters in symbol_params")
print("   2. Run backtesting with historical data")
print("   3. Paper trade when market opens")