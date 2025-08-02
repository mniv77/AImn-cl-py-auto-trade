# crypto_data_fix.py
"""
Fix for the get_market_data method in your main_v2.py
Add this method to your AIMnTradingEngine class
"""

def get_crypto_data(self, symbol: str) -> pd.DataFrame:
    """
    Fetch crypto data using the correct method for Alpaca
    Alpaca crypto symbols MUST have slashes (e.g., BTC/USD)
    """
    try:
        # Calculate time range
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=4)  # 4 hours of data
        
        print(f"   Fetching {symbol} crypto data...")
        
        # Use get_crypto_bars (the working method from our test)
        bars = self.connector.api.get_crypto_bars(
            symbol,  # Symbol WITH slash (e.g., 'BTC/USD')
            timeframe=TIMEFRAME,
            start=start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            end=end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            limit=200
        ).df
        
        if not bars.empty:
            # Reset index and prepare dataframe
            bars = bars.reset_index()
            bars.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'trade_count', 'vwap']
            print(f"   ✅ Got {len(bars)} bars, latest price: ${bars['close'].iloc[-1]:.2f}")
            return bars
        else:
            print(f"   ⚠️ No data returned for {symbol}")
            return pd.DataFrame()
            
    except Exception as e:
        logger.error(f"Error fetching crypto data for {symbol}: {e}")
        print(f"   ❌ Error: {str(e)[:100]}")
        return pd.DataFrame()

def get_market_data(self) -> Dict[str, pd.DataFrame]:
    """
    Fetch latest market data for all symbols
    Updated to properly handle crypto with slashes
    """
    market_data = {}
    
    # Check if we're trading crypto (symbols have slashes)
    is_crypto = any('/' in s for s in self.symbols)
    
    if is_crypto:
        print("🌐 Fetching crypto market data (24/7 trading)...")
    else:
        # Check if market is open (only for stocks)
        clock = self.connector.api.get_clock()
        if not clock.is_open:
            logger.info("⏰ Stock market is closed")
    
    for symbol in self.symbols:
        try:
            print(f"\n📊 Processing {symbol}...")
            
            if '/' in symbol:  # It's crypto
                df = self.get_crypto_data(symbol)
            else:  # It's stock
                df = self.connector.get_bars(symbol, TIMEFRAME, 200)
            
            if df is not None and len(df) > 0:
                market_data[symbol] = df
                logger.debug(f"✅ Fetched data for {symbol}: {len(df)} bars")
            else:
                logger.warning(f"⚠️ No data returned for {symbol}")
                
        except Exception as e:
            logger.error(f"Failed to fetch data for {symbol}: {e}")
            print(f"❌ Error: {str(e)[:100]}")
    
    return market_data