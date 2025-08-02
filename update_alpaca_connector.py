# update_alpaca_connector.py
"""
Updates the get_bars method in alpaca_connector.py to fix data fetching
"""

# Read the current file
with open('alpaca_connector.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the get_bars method
new_get_bars = '''    def get_bars(self, symbol: str, timeframe: str = '1Min', limit: int = 200) -> pd.DataFrame:
        """
        Get historical bars - SAME as TradingView chart
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            timeframe: '1Min', '5Min', '15Min', '1Hour', '1Day'
            limit: Number of bars to retrieve
            
        Returns:
            DataFrame with columns: open, high, low, close, volume
        """
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
            
            alpaca_timeframe = timeframe_map.get(timeframe, tradeapi.TimeFrame.Minute)
            
            # Get bars based on timeframe
            if timeframe == '1Day':
                # For daily bars, use date range
                end = datetime.now()
                start = end - timedelta(days=limit * 2)  # Extra days for weekends
                bars = self.api.get_bars(
                    symbol,
                    alpaca_timeframe,
                    start=start.strftime('%Y-%m-%d'),
                    end=end.strftime('%Y-%m-%d'),
                    limit=limit,
                    adjustment='raw'
                ).df
            else:
                # For intraday bars, just use limit
                bars = self.api.get_bars(
                    symbol,
                    alpaca_timeframe,
                    limit=limit,
                    adjustment='raw'
                ).df
            
            # Check if we got any data
            if len(bars) == 0:
                print(f"⚠️  No data returned for {timeframe}.")
                # Try without adjustment parameter
                if timeframe == '1Day':
                    end = datetime.now()
                    start = end - timedelta(days=limit * 2)
                    bars = self.api.get_bars(
                        symbol,
                        alpaca_timeframe,
                        start=start.strftime('%Y-%m-%d'),
                        end=end.strftime('%Y-%m-%d')
                    ).df
                else:
                    bars = self.api.get_bars(
                        symbol,
                        alpaca_timeframe,
                        limit=limit
                    ).df
                
                if len(bars) == 0:
                    raise Exception("No data available for this symbol")
            
            # Ensure column names match our system
            bars = bars.rename(columns={
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'volume': 'volume'
            })
            
            print(f"✅ Retrieved {len(bars)} bars")
            if len(bars) > 0:
                print(f"   Latest close: ${bars['close'].iloc[-1]:.2f}")
                print(f"   Time: {bars.index[-1]}")
            
            return bars
            
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            raise'''

# Replace the old get_bars method
import re

# Pattern to find the get_bars method
pattern = r'def get_bars\(self.*?\n(?:.*?\n)*?.*?raise'

# Check if we can find the method
if re.search(pattern, content, re.DOTALL):
    # Replace it
    content = re.sub(pattern, new_get_bars.strip() + '\n            raise', content, count=1, flags=re.DOTALL)
    
    # Write back
    with open('alpaca_connector.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Updated alpaca_connector.py with the fix!")
    print("\nNow run: py test_aimn_system.py")
else:
    print("❌ Could not find get_bars method to replace")
    print("You may need to manually update the get_bars method in alpaca_connector.py")