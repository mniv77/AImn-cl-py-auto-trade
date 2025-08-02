# crypto_data_patch.py
"""
Quick patch to fix the crypto data fetching issue
This will update your main_v2.py file
"""

import re

# Read the current main_v2.py
with open('main_v2.py', 'r') as f:
    content = f.read()

# The corrected get_market_data method
new_method = '''    def get_market_data(self) -> Dict[str, pd.DataFrame]:
        """Fetch latest market data for all symbols"""
        market_data = {}
        
        for symbol in self.symbols:
            try:
                print(f"📊 Fetching {symbol} data from Alpaca...")
                print(f"   Timeframe: {TIMEFRAME}")
                print(f"   Bars requested: 200")
                
                # For crypto symbols (containing /)
                if '/' in symbol:
                    # Calculate time range
                    end_time = datetime.now()
                    start_time = end_time - timedelta(hours=4)
                    
                    # Use get_crypto_bars for crypto
                    bars_response = self.connector.api.get_crypto_bars(
                        symbol,
                        timeframe=TIMEFRAME,
                        start=start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                        end=end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                        limit=200
                    )
                    
                    # Get the dataframe and handle multi-level columns
                    bars = bars_response.df
                    
                    if not bars.empty:
                        # Reset index to get timestamp
                        bars = bars.reset_index()
                        
                        # If we have multi-level columns, flatten them
                        if isinstance(bars.columns, pd.MultiIndex):
                            # Take only the data for our symbol
                            bars = bars[symbol]
                            bars = bars.reset_index()
                        
                        # Ensure column names are strings
                        bars.columns = [str(col).lower() for col in bars.columns]
                        
                        # Select only the columns we need
                        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                        available_columns = [col for col in required_columns if col in bars.columns]
                        
                        if len(available_columns) >= 5:  # Need at least OHLC + volume
                            df = bars[available_columns]
                            print(f"   ✅ Got {len(df)} bars, latest price: ${df['close'].iloc[-1]:.2f}")
                        else:
                            print(f"   ❌ Missing columns. Have: {list(bars.columns)}")
                            df = pd.DataFrame()
                    else:
                        print(f"   ⚠️ No data returned")
                        df = pd.DataFrame()
                else:
                    # Regular stock data
                    df = self.connector.get_bars(symbol, TIMEFRAME, 200)
                    if len(df) > 0:
                        print(f"   ✅ Got {len(df)} bars")
                
                if len(df) > 0:
                    market_data[symbol] = df
                    logger.debug(f"Fetched data for {symbol}: {len(df)} bars")
                else:
                    logger.warning(f"No data returned for {symbol}")
                    
            except Exception as e:
                print(f"❌ Error fetching data: {e}")
                logger.error(f"Failed to fetch data for {symbol}: {e}")
        
        return market_data'''

# Find and replace the get_market_data method
pattern = r'def get_market_data\(self\)[^}]+?return market_data'
match = re.search(pattern, content, re.DOTALL)

if match:
    content = content.replace(match.group(0), new_method.strip())
    
    # Save to a new file
    with open('main_v2_fixed.py', 'w') as f:
        f.write(content)
    
    print("✅ Created main_v2_fixed.py with the crypto data fix")
    print("\nTo use it:")
    print("1. Backup your current file: copy main_v2.py main_v2_backup2.py")
    print("2. Replace with fixed: copy main_v2_fixed.py main_v2.py")
    print("3. Run: py start_at_market_open.py")
else:
    print("❌ Could not find get_market_data method")
    print("Please manually replace the method in your main_v2.py")