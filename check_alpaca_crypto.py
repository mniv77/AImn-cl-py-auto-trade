# check_alpaca_crypto.py
"""
Check which crypto symbols Alpaca actually supports
"""

import alpaca_trade_api as tradeapi
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials
api_key = os.getenv('ALPACA_API_KEY')
secret_key = os.getenv('ALPACA_SECRET_KEY')
base_url = 'https://paper-api.alpaca.markets'

print("🔍 Checking Alpaca crypto support...")
print("="*50)

try:
    # Create API connection
    api = tradeapi.REST(api_key, secret_key, base_url, api_version='v2')
    
    # Get all assets
    assets = api.list_assets()
    
    # Filter for crypto
    crypto_assets = [asset for asset in assets if asset.asset_class == 'crypto' and asset.tradable]
    
    if crypto_assets:
        print(f"✅ Found {len(crypto_assets)} tradable cryptocurrencies:\n")
        for crypto in crypto_assets[:10]:  # Show first 10
            print(f"   Symbol: {crypto.symbol}")
            print(f"   Name: {crypto.name}")
            print(f"   Exchange: {crypto.exchange}")
            print(f"   Status: {crypto.status}")
            print(f"   Tradable: {crypto.tradable}")
            print("-" * 30)
    else:
        print("❌ No crypto assets found")
        print("\n🤔 Checking if crypto trading is enabled on your account...")
        
        # Check account
        account = api.get_account()
        print(f"\nAccount Status: {account.status}")
        print(f"Crypto Trading Enabled: {account.crypto_status if hasattr(account, 'crypto_status') else 'Unknown'}")
        
        print("\n💡 Possible reasons:")
        print("1. Crypto trading might not be enabled on your account")
        print("2. Crypto might require a separate Alpaca Crypto account")
        print("3. Try checking: https://alpaca.markets/crypto")
    
    # Try alternative - check if we can get crypto bars directly
    print("\n🔍 Testing direct crypto data access...")
    test_symbols = ['BTCUSD', 'BTC/USD', 'BTCUSDT', 'BTC']
    
    for symbol in test_symbols:
        try:
            print(f"\nTrying {symbol}...")
            bars = api.get_bars(
                symbol,
                tradeapi.TimeFrame.Minute,
                limit=1
            ).df
            
            if len(bars) > 0:
                print(f"✅ SUCCESS! {symbol} works!")
                print(f"   Latest: ${bars['close'].iloc[-1]:.2f}")
                break
        except Exception as e:
            print(f"❌ {symbol}: {str(e)[:50]}...")

except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "="*50)