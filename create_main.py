# create_main.py
"""
Creates the main.py file for AIMn Trading System
"""

code = """# main.py
'''
AIMn Trading System - Main Engine
Coordinates all components for 24/7 automated trading
'''

import time
import logging
from datetime import datetime
from typing import Dict, List
import json
import pandas as pd

# Import components
from alpaca_connector import AlpacaTradingConnector
from scanner import AIMnScanner
from position_manager import AIMnPositionManager, ExitCode
from indicators import AIMnIndicators

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('aimn_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AIMnTradingEngine:
    '''
    Main trading engine that coordinates all components
    '''
    
    def __init__(self, connector: AlpacaTradingConnector, 
                 symbols: List[str], 
                 symbol_params: Dict[str, Dict],
                 capital_per_trade: float = 0.2):
        '''
        Initialize the AIMn Trading Engine
        
        Args:
            connector: Alpaca API connector
            symbols: List of symbols to trade
            symbol_params: Symbol-specific parameters
            capital_per_trade: Fraction of capital to use per trade (0.2 = 20%)
        '''
        self.connector = connector
        self.symbols = symbols
        self.symbol_params = symbol_params
        self.capital_per_trade = capital_per_trade
        
        # Initialize components
        self.scanner = AIMnScanner(symbol_params)
        self.position_manager = AIMnPositionManager(max_positions=1)  # One position at a time
        
        # Control flags
        self.running = False
        self.scan_interval = 60  # Scan every 60 seconds
        
        logger.info("AIMn Trading Engine initialized")
        logger.info(f"Trading symbols: {symbols}")
    
    def get_market_data(self) -> Dict[str, pd.DataFrame]:
        '''Fetch latest market data for all symbols'''
        market_data = {}
        
        for symbol in self.symbols:
            try:
                # Get 200 bars of 1-minute data
                df = self.connector.get_latest_bars(symbol, count=200)
                market_data[symbol] = df
                logger.debug(f"Fetched data for {symbol}: {len(df)} bars")
            except Exception as e:
                logger.error(f"Failed to fetch data for {symbol}: {e}")
        
        return market_data
    
    def calculate_position_size(self, price: float) -> int:
        '''Calculate number of shares to trade based on available capital'''
        try:
            account = self.connector.get_account_info()
            available_capital = account['buying_power']
            
            # Use specified fraction of capital
            position_value = available_capital * self.capital_per_trade
            shares = int(position_value / price)
            
            # Ensure we have at least 1 share
            return max(1, shares)
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0
    
    def process_active_positions(self, market_data: Dict[str, pd.DataFrame]):
        '''Update and check exits for all active positions'''
        for symbol, position in list(self.position_manager.positions.items()):
            try:
                # Get current data
                if symbol not in market_data:
                    continue
                
                df = market_data[symbol]
                current_price = df['close'].iloc[-1]
                
                # Calculate current RSI for RSI exit
                params = self.scanner.get_symbol_params(symbol)
                df_with_indicators = AIMnIndicators.calculate_all_indicators(df, params)
                current_rsi = df_with_indicators['rsi_real'].iloc[-1]
                
                # Update position and check for exit
                exit_info = self.position_manager.update_position(
                    symbol, current_price, current_rsi
                )
                
                if exit_info:
                    # Position was closed, log it
                    self.log_trade(exit_info)
                    
                    # Show current statistics
                    stats = self.position_manager.get_statistics()
                    logger.info(f"Stats: Trades={stats['total_trades']}, "
                               f"Win Rate={stats['win_rate']:.1f}%, "
                               f"Total P&L=${stats['total_pnl']:.2f}")
                    
            except Exception as e:
                logger.error(f"Error processing position {symbol}: {e}")
    
    def execute_trade(self, opportunity: Dict):
        '''Execute a trade based on scanner opportunity'''
        try:
            # Calculate position size
            shares = self.calculate_position_size(opportunity['entry_price'])
            
            if shares == 0:
                logger.warning("Insufficient capital for trade")
                return
            
            # Get symbol parameters
            params = self.scanner.get_symbol_params(opportunity['symbol'])
            
            # Place order with broker
            order = self.connector.place_order(
                symbol=opportunity['symbol'],
                side='buy' if opportunity['direction'] == 'BUY' else 'sell',
                qty=shares
            )
            
            # Record position
            position = self.position_manager.enter_position(
                opportunity, shares, params
            )
            
            # Log entry
            logger.info(f"TRADE EXECUTED: {opportunity['direction']} {shares} shares of "
                       f"{opportunity['symbol']} @ ${opportunity['entry_price']:.2f}")
            logger.info(f"Indicators: RSI={opportunity['indicators']['rsi_real']:.1f}, "
                       f"Volume Ratio={opportunity['indicators']['volume_ratio']:.2f}, "
                       f"ATR Ratio={opportunity['indicators']['atr_ratio']:.2f}")
            
        except Exception as e:
            logger.error(f"Failed to execute trade: {e}")
    
    def run_trading_cycle(self):
        '''Run one complete trading cycle'''
        try:
            logger.info("="*50)
            logger.info(f"Trading cycle started at {datetime.now()}")
            
            # 1. Get latest market data
            market_data = self.get_market_data()
            
            if not market_data:
                logger.warning("No market data available")
                return
            
            # 2. Process existing positions
            self.process_active_positions(market_data)
            
            # 3. If no position, scan for opportunities
            if not self.position_manager.has_position():
                logger.info("No active position, scanning for opportunities...")
                
                opportunity = self.scanner.scan_all_symbols(market_data)
                
                if opportunity:
                    logger.info(f"Opportunity found: {opportunity['symbol']} "
                               f"{opportunity['direction']} (score: {opportunity['score']:.1f})")
                    
                    # Execute trade
                    self.execute_trade(opportunity)
                else:
                    logger.info("No trading opportunities found")
            else:
                # Log current position status
                for symbol, position in self.position_manager.positions.items():
                    logger.info(f"Active position: {symbol} {position.direction} | "
                               f"P&L: ${position.unrealized_pnl:.2f} "
                               f"({position.unrealized_pnl_pct:.2f}%)")
                    
                    if position.early_trail_active:
                        logger.info(f"  Early trail active: ${position.early_trail_price:.2f}")
                    if position.peak_trail_active:
                        logger.info(f"  Peak trail active: ${position.peak_trail_price:.2f}")
            
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}")
    
    def log_trade(self, trade_info: Dict):
        '''Log completed trade to file'''
        with open('aimn_trades.json', 'a') as f:
            f.write(json.dumps(trade_info, default=str) + '\\n')
    
    def start(self):
        '''Start the trading engine'''
        logger.info("Starting AIMn Trading Engine...")
        self.running = True
        
        # Show initial account status
        try:
            account = self.connector.get_account_info()
            logger.info(f"Account Status: Buying Power=${account['buying_power']:,.2f}, "
                       f"Portfolio=${account['portfolio_value']:,.2f}")
        except Exception as e:
            logger.error(f"Failed to get account info: {e}")
        
        # Main trading loop
        while self.running:
            try:
                self.run_trading_cycle()
                
                # Wait before next cycle
                logger.info(f"Waiting {self.scan_interval} seconds until next scan...")
                time.sleep(self.scan_interval)
                
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                time.sleep(30)  # Wait 30 seconds on error
    
    def stop(self):
        '''Stop the trading engine'''
        logger.info("Stopping AIMn Trading Engine...")
        self.running = False
        
        # Show final statistics
        stats = self.position_manager.get_statistics()
        logger.info("="*50)
        logger.info("FINAL STATISTICS:")
        logger.info(f"Total Trades: {stats['total_trades']}")
        logger.info(f"Winning Trades: {stats['winning_trades']}")
        logger.info(f"Losing Trades: {stats['losing_trades']}")
        logger.info(f"Win Rate: {stats['win_rate']:.1f}%")
        logger.info(f"Total P&L: ${stats['total_pnl']:.2f}")
        logger.info(f"Average P&L: ${stats['avg_pnl']:.2f}")
        logger.info("="*50)


# Default symbol parameters
DEFAULT_SYMBOL_PARAMS = {
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
        'atr_multiplier': 1.2,
        'use_rsi_exit': True,
        'rsi_exit_min_profit': 0.5
    },
    'MSFT': {
        'rsi_window': 100,
        'rsi_overbought': 70,
        'rsi_oversold': 30,
        'stop_loss_percent': 2.0,
        'early_trail_start': 1.0,
        'early_trail_minus': 15.0,
        'peak_trail_start': 5.0,
        'peak_trail_minus': 0.5,
        'volume_threshold': 0.9,
        'atr_multiplier': 1.2,
        'use_rsi_exit': True,
        'rsi_exit_min_profit': 0.5
    },
    'TSLA': {
        'rsi_window': 120,
        'rsi_overbought': 75,
        'rsi_oversold': 25,
        'stop_loss_percent': 3.0,  # More volatile
        'early_trail_start': 1.5,
        'early_trail_minus': 20.0,
        'peak_trail_start': 7.0,
        'peak_trail_minus': 0.7,
        'volume_threshold': 1.0,
        'atr_multiplier': 1.3,
        'use_rsi_exit': True,
        'rsi_exit_min_profit': 1.0
    }
}


def main():
    '''Main entry point'''
    print("\\n" + "="*60)
    print("🚀 AIMn TRADING SYSTEM V1.0")
    print("="*60)
    print("Philosophy: Let the market pick your trades.")
    print("            Let logic pick your exits.")
    print("="*60 + "\\n")
    
    # Configuration
    SYMBOLS = ['AAPL', 'MSFT', 'TSLA']  # Add more symbols as needed
    PAPER_TRADING = True
    CAPITAL_PER_TRADE = 0.2  # Use 20% of capital per trade
    
    # Initialize Alpaca connector
    print("1️⃣ Connecting to Alpaca...")
    connector = AlpacaTradingConnector(paper_trading=PAPER_TRADING)
    
    # Initialize trading engine
    print("\\n2️⃣ Initializing AIMn Trading Engine...")
    engine = AIMnTradingEngine(
        connector=connector,
        symbols=SYMBOLS,
        symbol_params=DEFAULT_SYMBOL_PARAMS,
        capital_per_trade=CAPITAL_PER_TRADE
    )
    
    # Start trading
    print("\\n3️⃣ Starting automated trading...")
    print("   Press Ctrl+C to stop\\n")
    
    try:
        engine.start()
    except KeyboardInterrupt:
        print("\\n\\n⛔ Shutdown signal received")
        engine.stop()


if __name__ == "__main__":
    main()
"""

# Write the file
with open('main.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("✅ Created main.py successfully!")
print("\n✅ All AIMn Trading System files have been created!")
print("\nNow you can run the test with: py test_aimn_system.py")