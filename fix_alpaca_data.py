# fix_alpaca_data.py
"""
Fix the Alpaca data fetching issue
"""

import alpaca_trade_api as tradeapi
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pandas as pd

# Load environment variables
load_dotenv()

# Get credentials
api_key = os.getenv('ALPACA_API_KEY')
secret_key = os.getenv('ALPACA_SECRET_KEY')
base_url = 'https://paper-api.alpaca.markets'

print("🔍 Testing different data fetching methods...")
print("="*50)

try:
    # Create API connection
    api = tradeapi.REST(api_key, secret_key, base_url, api_version='v2')
    
    # Method 1: Get bars without any date parameters
    print("\n1️⃣ Method 1: Simple request (no dates)")
    try:
        bars = api.get_bars(
            'AAPL',
            tradeapi.TimeFrame.Day,
            limit=10
        ).df
        
        if len(bars) > 0:
            print(f"✅ Success! Got {len(bars)} bars")
            print(f"Latest bar: {bars.index[-1]} - Close: ${bars['close'].iloc[-1]:.2f}")
            print("\nLast 5 days:")
            print(bars[['open', 'high', 'low', 'close', 'volume']].tail())
        else:
            print("❌ No data returned")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Method 2: Use get_trades instead
    print("\n2️⃣ Method 2: Get latest trade")
    try:
        trade = api.get_latest_trade('AAPL')
        print(f"✅ Latest trade: ${trade.price:.2f} at {trade.timestamp}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Method 3: Use different date format
    print("\n3️⃣ Method 3: With specific date format")
    try:
        end = datetime.now()
        start = end - timedelta(days=10)
        
        bars = api.get_bars(
            'AAPL',
            tradeapi.TimeFrame.Day,
            start=start.strftime('%Y-%m-%d'),
            end=end.strftime('%Y-%m-%d')
        ).df
        
        if len(bars) > 0:
            print(f"✅ Success! Got {len(bars)} bars")
        else:
            print("❌ No data returned")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Method 4: Use page_limit
    print("\n4️⃣ Method 4: Using page_limit")
    try:
        bars = api.get_bars(
            'AAPL',
            tradeapi.TimeFrame.Day,
            page_limit=10
        ).df
        
        if len(bars) > 0:
            print(f"✅ Success! Got {len(bars)} bars")
        else:
            print("❌ No data returned")
    except Exception as e:
        print(f"❌ Error: {e}")

except Exception as e:
    print(f"\n❌ Connection failed: {e}")

print("\n" + "="*50)

# Create updated get_bars method
code = '''
def get_bars_fixed(self, symbol: str, timeframe: str = '1Day', limit: int = 200) -> pd.DataFrame:
    """Fixed version of get_bars that actually works"""
    print(f"\\n📊 Fetching {symbol} data from Alpaca...")
    print(f"   Timeframe: {timeframe}")
    print(f"   Bars requested: {limit}")
    
    try:
        # Convert timeframe to Alpaca format
        timeframe_map = {
            '1Min': tradeapi.TimeFrame.Minute,
            '5Min': tradeapi.TimeFrame(5, tradeapi.TimeFrameUnit.Minute),
            '15Min': tradeapi.TimeFrame(15, tradeapi.TimeFrameUnit.Minute),
            '1Hour': tradeapi.TimeFrame.Hour,
            '1Day': tradeapi.TimeFrame.Day
        }
        
        alpaca_timeframe = timeframe_map.get(timeframe, tradeapi.TimeFrame.Day)
        
        # For daily bars, use simple request without dates
        if timeframe == '1Day':
            bars = self.api.get_bars(
                symbol,
                alpaca_timeframe,
                limit=limit
            ).df
        else:
            # For intraday, we might need dates
            bars = self.api.get_bars(
                symbol,
                alpaca_timeframe,
                limit=limit
            ).df
        
        # Check if we got data
        if len(bars) == 0:
            # Try alternative method
            print("   Trying alternative method...")
            bars = self.api.get_bars(
                symbol,
                alpaca_timeframe,
                page_limit=limit
            ).df
        
        if len(bars) > 0:
            print(f"✅ Retrieved {len(bars)} bars")
            print(f"   Latest close: ${bars['close'].iloc[-1]:.2f}")
            print(f"   Time: {bars.index[-1]}")
        else:
            print("❌ No data available")
            
        return bars
        
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        raise
'''

print("\n💡 Fix found! Add this method to your alpaca_connector.py")
print("Or wait for the market to open for real-time data.")