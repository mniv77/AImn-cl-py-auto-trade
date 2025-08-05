# alpaca_connector.py
"""
Alpaca Trading Connector for AIMn System
Handles all broker interactions
"""

import os
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
import pandas as pd
from datetime import datetime, timedelta
import logging

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class AlpacaTradingConnector:
    """Connector for Alpaca Trading API"""
    
    def __init__(self, paper_trading=True):
        """Initialize Alpaca connection"""
        
        # Get API keys from environment or .env file
        api_key = os.getenv('ALPACA_API_KEY', 'PKIU63SSI0ZS85BQUY2E')
        secret_key = os.getenv('ALPACA_SECRET_KEY', 'lwG2g6Hrgtd6V1oWwGjzcvdOQgMxfgAmVdgo88Pq')
        
        # Set base URL based on paper/live trading
        if paper_trading:
            base_url = 'https://paper-api.alpaca.markets'
        else:
            base_url = 'https://api.alpaca.markets'
            
        # Initialize the API
        try:
            self.api = tradeapi.REST(
                api_key,
                secret_key,
                base_url,
                api_version='v2'
            )
            
            # Test connection
            account = self.api.get_account()
            logger.info(f"✅ Connected to Alpaca ({'Paper' if paper_trading else 'Live'} Trading)")
            logger.info(f"   Account: ${float(account.equity):,.2f}")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Alpaca: {e}")
            raise
    
    def get_account_info(self):
        """Get account information"""
        try:
            account = self.api.get_account()
            return {
                'buying_power': float(account.buying_power),
                'cash': float(account.cash),
                'portfolio_value': float(account.equity),
                'day_trading_buying_power': float(account.daytrading_buying_power),
                'pattern_day_trader': account.pattern_day_trader
            }
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            raise
    
    def get_positions(self):
        """Get all current positions"""
        try:
            positions = self.api.list_positions()
            
            if not positions:
                return pd.DataFrame()
            
            data = []
            for pos in positions:
                data.append({
                    'symbol': pos.symbol,
                    'qty': float(pos.qty),
                    'side': pos.side,
                    'market_value': float(pos.market_value),
                    'cost_basis': float(pos.cost_basis),
                    'unrealized_pl': float(pos.unrealized_pl),
                    'unrealized_plpc': float(pos.unrealized_plpc),
                    'current_price': float(pos.current_price),
                    'avg_entry_price': float(pos.avg_entry_price)
                })
            
            return pd.DataFrame(data)
            
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return pd.DataFrame()
    
    def place_order(self, symbol, qty, side, order_type='market', limit_price=None):
        """Place an order"""
        try:
            # Clean symbol format for Alpaca
            alpaca_symbol = symbol.replace('/', '')  # BTC/USD -> BTCUSD
            
            order = self.api.submit_order(
                symbol=alpaca_symbol,
                qty=qty,
                side=side,
                type=order_type,
                time_in_force='gtc',
                limit_price=limit_price
            )
            
            logger.info(f"✅ Order placed: {side} {qty} {symbol}")
            return order
            
        except Exception as e:
            logger.error(f"❌ Error placing order: {e}")
            raise
    
    def get_bars(self, symbol, timeframe, limit=200):
        """Get historical bars for a symbol"""
        try:
            # Clean symbol format
            alpaca_symbol = symbol.replace('/', '')
            
            # For crypto, use get_crypto_bars
            if '/' in symbol:
                end_time = datetime.now()
                start_time = end_time - timedelta(days=2)
                
                bars = self.api.get_crypto_bars(
                    alpaca_symbol,
                    timeframe,
                    start=start_time.isoformat(),
                    end=end_time.isoformat(),
                    limit=limit
                ).df
            else:
                # For stocks
                bars = self.api.get_bars(
                    alpaca_symbol,
                    timeframe,
                    limit=limit
                ).df
            
            if bars is not None and not bars.empty:
                bars = bars.reset_index()
                # Standardize column names
                bars.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'trade_count', 'vwap']
                # Keep only needed columns
                bars = bars[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
                return bars
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error getting bars for {symbol}: {e}")
            return pd.DataFrame()
    
    def cancel_all_orders(self):
        """Cancel all open orders"""
        try:
            self.api.cancel_all_orders()
            logger.info("✅ All open orders cancelled")
        except Exception as e:
            logger.error(f"Error cancelling orders: {e}")
    
    def close_all_positions(self):
        """Close all positions"""
        try:
            self.api.close_all_positions()
            logger.info("✅ All positions closed")
        except Exception as e:
            logger.error(f"Error closing positions: {e}")
    
    def get_clock(self):
        """Get market clock"""
        try:
            return self.api.get_clock()
        except Exception as e:
            logger.error(f"Error getting clock: {e}")
            raise


# Test the connection
if __name__ == "__main__":
    print("Testing Alpaca Connection...")
    
    # Test paper trading connection
    connector = AlpacaTradingConnector(paper_trading=True)
    
    # Get account info
    account = connector.get_account_info()
    print(f"\n💰 Account Status:")
    print(f"   Buying Power: ${account['buying_power']:,.2f}")
    print(f"   Portfolio Value: ${account['portfolio_value']:,.2f}")
    
    # Get positions
    positions = connector.get_positions()
    if not positions.empty:
        print(f"\n📈 Current Positions:")
        print(positions)
    else:
        print("\n📈 No open positions")
    
    # Test getting bars
    print("\n📊 Testing market data...")
    bars = connector.get_bars('BTC/USD', '1Min', limit=5)
    if not bars.empty:
        print(f"✅ Got {len(bars)} bars for BTC/USD")
        print(f"   Latest price: ${bars['close'].iloc[-1]:,.2f}")
    else:
        print("❌ No data returned")