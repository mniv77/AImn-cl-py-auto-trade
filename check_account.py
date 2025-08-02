# SAVE THIS FILE AS: check_account.py
# LOCATION: C:\Users\mniv7\Documents\meir\cl-py\check_account.py

"""
Quick check to see your actual account and settings
"""

import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient

# Load environment
load_dotenv()

# Check which account we're using
api_key = os.getenv('ALPACA_API_KEY')
api_secret = os.getenv('ALPACA_SECRET_KEY')
paper = os.getenv('ALPACA_PAPER', 'true').lower() == 'true'

print("🔍 CHECKING YOUR SETUP")
print("=" * 60)

# Connect to Alpaca
trading_client = TradingClient(api_key, api_secret, paper=paper)
account = trading_client.get_account()

print(f"\n📊 ACCOUNT INFO:")
print(f"   Account Type: {'PAPER' if paper else 'LIVE'}")
print(f"   Buying Power: ${float(account.buying_power):,.2f}")
print(f"   Portfolio Value: ${float(account.portfolio_value):,.2f}")
print(f"   Cash: ${float(account.cash):,.2f}")

# Check config
print(f"\n⚙️ CURRENT SETTINGS:")
try:
    import aimn_crypto_config as config
    symbol_config = config.SYMBOL_CONFIGS.get('BTC/USD', {})
    print(f"   RSI Oversold: {symbol_config.get('rsi_oversold', 'Not found')}")
    print(f"   RSI Overbought: {symbol_config.get('rsi_overbought', 'Not found')}")
    print(f"   Volume Threshold: {symbol_config.get('volume_threshold', 'Not found')}")
    print(f"   ATR Threshold: {symbol_config.get('atr_threshold', 'Not found')}")
except Exception as e:
    print(f"   Error reading config: {e}")

print("\n💡 WHAT THIS MEANS:")
if float(account.buying_power) > 100000:
    print("   ✅ You're using the main paper account ($372k)")
else:
    print("   ⚠️ You might be using a different account ($2k)")

print("\n🎯 Your bot SHOULD show RSI 40/60 after our changes!")
print("=" * 60)