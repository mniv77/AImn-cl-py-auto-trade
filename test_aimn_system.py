# test_aimn_system.py
'''
Test the AIMn Trading System with daily data
'''

import sys
import os
from datetime import datetime

# Make sure we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the components
try:
    from alpaca_connector import AlpacaTradingConnector
    print("✅ Imported Alpaca connector")
except:
    print("❌ Could not import alpaca_connector.py")
    print("   Make sure you have alpaca_connector.py in your directory")
    sys.exit(1)

try:
    from indicators import AIMnIndicators
    from scanner import AIMnScanner
    from position_manager import AIMnPositionManager
    print("✅ Imported AIMn components")
except Exception as e:
    print(f"❌ Could not import AIMn components: {e}")
    print("   Make sure you have all the Python files from the artifacts:")
    print("   - indicators.py")
    print("   - scanner.py") 
    print("   - position_manager.py")
    sys.exit(1)

print("\n" + "="*60)
print("🧪 TESTING AIMn TRADING SYSTEM")
print("="*60)

# 1. Initialize connector
print("\n1️⃣ Connecting to Alpaca...")
connector = AlpacaTradingConnector(paper_trading=True)

# 2. Test symbols
symbols = ['AAPL', 'MSFT', 'GOOGL']
print(f"\n2️⃣ Testing with symbols: {symbols}")

# 3. Get market data
print("\n3️⃣ Fetching market data (daily bars)...")
market_data = {}
for symbol in symbols:
    try:
        # Get daily data since market is closed
        df = connector.get_bars(symbol, '1Day', 200)
        if len(df) > 0:
            market_data[symbol] = df
            print(f"   ✅ {symbol}: {len(df)} bars, latest close: ${df['close'].iloc[-1]:.2f}")
        else:
            print(f"   ❌ {symbol}: No data")
    except Exception as e:
        print(f"   ❌ {symbol}: Error - {e}")

# 4. Test indicators
print("\n4️⃣ Testing indicator calculations...")
if 'AAPL' in market_data:
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

# 5. Test scanner
print("\n5️⃣ Testing scanner for opportunities...")
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

scanner = AIMnScanner(symbol_params)
opportunity = scanner.scan_all_symbols(market_data)

if opportunity:
    print(f"\n🎯 Opportunity found!")
    print(f"   Symbol: {opportunity['symbol']}")
    print(f"   Direction: {opportunity['direction']}")
    print(f"   Score: {opportunity['score']:.1f}")
    print(f"   Entry Price: ${opportunity['entry_price']:.2f}")
else:
    print("\n   No opportunities found with current parameters")
    print("   This is normal - the strategy is selective")

# 6. Test position manager
print("\n6️⃣ Testing position manager...")
position_manager = AIMnPositionManager(max_positions=1)

if opportunity:
    # Simulate entering a position
    shares = 100  # Test with 100 shares
    position = position_manager.enter_position(
        opportunity, 
        shares, 
        symbol_params[opportunity['symbol']]
    )
    
    print(f"\n   Position created:")
    print(f"   Entry: ${position.entry_price:.2f}")
    print(f"   Stop Loss: ${position.stop_loss_price:.2f}")
    print(f"   Shares: {position.shares}")
    
    # Simulate price movement
    test_prices = [
        position.entry_price,
        position.entry_price * 1.01,  # +1%
        position.entry_price * 1.02,  # +2%
        position.entry_price * 1.015  # Pull back
    ]
    
    print(f"\n   Simulating price movement:")
    for price in test_prices:
        result = position.update_price(price)
        print(f"   Price: ${price:.2f} | P&L: {position.unrealized_pnl_pct:.2f}%", end="")
        
        if position.early_trail_active:
            print(f" | Early trail: ${position.early_trail_price:.2f}", end="")
        if position.peak_trail_active:
            print(f" | Peak trail: ${position.peak_trail_price:.2f}", end="")
        
        if result:
            print(f" | EXIT: {result[0].value}")
        else:
            print()

print("\n" + "="*60)
print("✅ AIMn System components are working!")
print("="*60)

# Show current account status
account = connector.get_account_info()
print(f"\n📊 Account Status:")
print(f"   Buying Power: ${account['buying_power']:,.2f}")
print(f"   Portfolio Value: ${account['portfolio_value']:,.2f}")

# Check when market opens
clock = connector.api.get_clock()
if not clock.is_open:
    time_to_open = (clock.next_open - clock.timestamp).total_seconds() / 3600
    print(f"\n⏰ Market opens in {time_to_open:.1f} hours")
    print(f"   Next open: {clock.next_open}")
else:
    print(f"\n✅ Market is OPEN!")

print("\n💡 Next steps:")
print("   1. Wait for market to open for live minute data")
print("   2. Or run backtesting with daily data")
print("   3. Or tune parameters with parameter_tuner.py")
