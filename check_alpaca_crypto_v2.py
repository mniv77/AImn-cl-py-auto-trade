# check_alpaca_crypto_v2.py
"""
Check Alpaca crypto support - fixed version
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
    
    # Method 1: Try to get crypto quotes directly
    print("\n1️⃣ Testing crypto symbols directly...")
    crypto_symbols = ['BTCUSD', 'ETHUSD', 'BTC/USD', 'ETH/USD']
    
    for symbol in crypto_symbols:
        try:
            print(f"\nTesting {symbol}...")
            # Try to get latest trade
            trade = api.get_latest_trade(symbol)
            print(f"✅ {symbol} WORKS! Latest price: ${trade.price:.2f}")
            
            # Try to get bars too
            bars = api.get_bars(
                symbol,
                tradeapi.TimeFrame.Hour,
                limit=5
            ).df
            
            if len(bars) > 0:
                print(f"   Got {len(bars)} bars of data")
                print(f"   Latest close: ${bars['close'].iloc[-1]:.2f}")
                
        except Exception as e:
            error_msg = str(e)
            if "not found" in error_msg.lower():
                print(f"❌ {symbol}: Symbol not found")
            else:
                print(f"❌ {symbol}: {error_msg[:60]}...")
    
    # Method 2: Check account configuration
    print("\n2️⃣ Checking account configuration...")
    account = api.get_account()
    print(f"Account Status: {account.status}")
    print(f"Account Number: {account.account_number}")
    
    # Method 3: List all available assets and check for crypto
    print("\n3️⃣ Checking available asset types...")
    assets = api.list_assets(status='active')
    
    # Check different asset properties
    asset_types = set()
    crypto_count = 0
    
    for asset in assets[:100]:  # Check first 100
        # Check various attributes
        if hasattr(asset, 'class'):
            asset_types.add(asset.class_)
        if hasattr(asset, 'exchange'):
            if 'CRYPTO' in asset.exchange or 'crypto' in asset.exchange.lower():
                crypto_count += 1
                if crypto_count <= 5:  # Show first 5
                    print(f"   Found crypto: {asset.symbol} on {asset.exchange}")
    
    print(f"\nAsset types found: {asset_types}")
    print(f"Crypto assets found: {crypto_count}")
    
    # Method 4: Try stock symbols that we know work
    print("\n4️⃣ Testing known stock symbols for comparison...")
    test_stock = 'AAPL'
    try:
        trade = api.get_latest_trade(test_stock)
        print(f"✅ {test_stock} works: ${trade.price:.2f}")
    except Exception as e:
        print(f"❌ Even {test_stock} failed: {e}")
    
    print("\n💡 IMPORTANT NOTE:")
    print("Alpaca discontinued crypto trading for new accounts in 2023!")
    print("Your account likely doesn't have crypto access.")
    print("\nALTERNATIVES:")
    print("1. Trade stocks/ETFs (what we built works great for this!)")
    print("2. Trade crypto ETFs like BITO (Bitcoin ETF)")
    print("3. Use a dedicated crypto exchange API")

except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "="*50)