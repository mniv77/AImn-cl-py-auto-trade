# main_v2.py
"""
AIMn Trading System - Enhanced Main Script
Uses configuration file for easy parameter adjustment
"""

import time
import logging
from datetime import datetime
from typing import Dict, List
import json
import pandas as pd

# Import configuration
from aimn_crypto_config import *

# Import components
from alpaca_connector import AlpacaTradingConnector
from scanner import AIMnScanner
from position_manager import AIMnPositionManager, ExitCode
from indicators import AIMnIndicators

# Set up logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AIMnTradingEngine:
    """
    Main trading engine that coordinates all components
    """
    
    def __init__(self, connector: AlpacaTradingConnector, 
                 symbols: List[str], 
                 symbol_params: Dict[str, Dict],
                 capital_per_trade: float = 0.2,
                 scan_interval: int = 60):
        """
        Initialize the AIMn Trading Engine
        """
        self.connector = connector
        self.symbols = symbols
        self.symbol_params = symbol_params
        self.capital_per_trade = capital_per_trade
        self.scan_interval = scan_interval
        
        # Initialize components
        self.scanner = AIMnScanner(symbol_params)
        self.position_manager = AIMnPositionManager(max_positions=1)  # One position at a time
        
        # Control flags
        self.running = False
        
        # Performance tracking
        self.start_time = datetime.now()
        self.initial_portfolio_value = None
        
        logger.info("AIMn Trading Engine initialized")
        logger.info(f"Trading symbols: {symbols}")
        logger.info(f"Scan interval: {scan_interval} seconds")
    
    def get_market_data(self) -> Dict[str, pd.DataFrame]:
        """Fetch latest market data for all symbols"""
        market_data = {}
        
        # Check if market is open
        clock = self.connector.api.get_clock()
        
        for symbol in self.symbols:
            try:
                # Use appropriate timeframe based on market status
                if clock.is_open:
                    # Market open - use 1-minute data
                    df = self.connector.get_bars(symbol, '1Min', 200)
                else:
                    # Market closed - use daily data
                    df = self.connector.get_bars(symbol, '1Day', 200)
                
                if len(df) > 0:
                    market_data[symbol] = df
                    logger.debug(f"Fetched data for {symbol}: {len(df)} bars")
                else:
                    logger.warning(f"No data returned for {symbol}")
                    
            except Exception as e:
                logger.error(f"Failed to fetch data for {symbol}: {e}")
        
        return market_data
    
    def calculate_position_size(self, price: float) -> int:
        """Calculate number of shares to trade based on available capital"""
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
        """Update and check exits for all active positions"""
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
                    logger.info(f"📊 Stats: Trades={stats['total_trades']}, "
                               f"Win Rate={stats['win_rate']:.1f}%, "
                               f"Total P&L=${stats['total_pnl']:.2f}")
                    
            except Exception as e:
                logger.error(f"Error processing position {symbol}: {e}")
    
    def execute_trade(self, opportunity: Dict):
        """Execute a trade based on scanner opportunity"""
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
            logger.info(f"🎯 TRADE EXECUTED: {opportunity['direction']} {shares} shares of "
                       f"{opportunity['symbol']} @ ${opportunity['entry_price']:.2f}")
            logger.info(f"📈 Indicators: RSI={opportunity['indicators']['rsi_real']:.1f}, "
                       f"Volume Ratio={opportunity['indicators']['volume_ratio']:.2f}, "
                       f"ATR Ratio={opportunity['indicators']['atr_ratio']:.2f}")
            
        except Exception as e:
            logger.error(f"Failed to execute trade: {e}")
    
    def run_trading_cycle(self):
        """Run one complete trading cycle"""
        try:
            logger.info("="*50)
            logger.info(f"Trading cycle started at {datetime.now()}")
            
            # Check market status
            clock = self.connector.api.get_clock()
            if not clock.is_open:
                logger.info(f"⏰ Market is CLOSED. Next open: {clock.next_open}")
                logger.info("   Using daily data for analysis...")
            
            # 1. Get latest market data
            market_data = self.get_market_data()
            
            if not market_data:
                logger.warning("No market data available")
                return
            
            # 2. Process existing positions
            self.process_active_positions(market_data)
            
            # 3. If no position, scan for opportunities
            if not self.position_manager.has_position():
                logger.info("🔍 No active position, scanning for opportunities...")
                
                opportunity = self.scanner.scan_all_symbols(market_data)
                
                if opportunity:
                    logger.info(f"💡 Opportunity found: {opportunity['symbol']} "
                               f"{opportunity['direction']} (score: {opportunity['score']:.1f})")
                    
                    # Execute trade only if market is open
                    if clock.is_open:
                        self.execute_trade(opportunity)
                    else:
                        logger.info("   Waiting for market to open to execute trade")
                else:
                    logger.info("   No trading opportunities found")
            else:
                # Log current position status
                for symbol, position in self.position_manager.positions.items():
                    logger.info(f"📊 Active position: {symbol} {position.direction} | "
                               f"P&L: ${position.unrealized_pnl:.2f} "
                               f"({position.unrealized_pnl_pct:.2f}%)")
                    
                    if position.early_trail_active:
                        logger.info(f"   🔵 Early trail active: ${position.early_trail_price:.2f}")
                    if position.peak_trail_active:
                        logger.info(f"   🟢 Peak trail active: ${position.peak_trail_price:.2f}")
            
            # Show account status
            self.show_account_status()
            
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}")
    
    def show_account_status(self):
        """Display current account status"""
        try:
            account = self.connector.get_account_info()
            
            # Track performance
            if self.initial_portfolio_value is None:
                self.initial_portfolio_value = account['portfolio_value']
            
            current_value = account['portfolio_value']
            total_return = ((current_value - self.initial_portfolio_value) / 
                           self.initial_portfolio_value * 100)
            
            logger.info(f"\n💰 Account Status:")
            logger.info(f"   Portfolio Value: ${current_value:,.2f}")
            logger.info(f"   Buying Power: ${account['buying_power']:,.2f}")
            logger.info(f"   Session Return: {total_return:+.2f}%")
            
        except Exception as e:
            logger.error(f"Error getting account status: {e}")
    
    def log_trade(self, trade_info: Dict):
        """Log completed trade to file"""
        with open('aimn_trades.json', 'a') as f:
            f.write(json.dumps(trade_info, default=str) + '\n')
        
        # Also log to performance file if enabled
        if TRACK_PERFORMANCE:
            self.log_performance(trade_info)
    
    def log_performance(self, trade_info: Dict):
        """Log trade performance for analysis"""
        try:
            performance_data = {
                'timestamp': datetime.now().isoformat(),
                'symbol': trade_info['symbol'],
                'direction': trade_info['direction'],
                'entry_price': trade_info['entry_price'],
                'exit_price': trade_info['exit_price'],
                'shares': trade_info['shares'],
                'pnl': trade_info['pnl'],
                'pnl_pct': trade_info['pnl_pct'],
                'exit_code': trade_info['exit_code'],
                'hold_time': (trade_info['exit_time'] - trade_info['entry_time']).total_seconds() / 60
            }
            
            # Append to CSV
            df = pd.DataFrame([performance_data])
            df.to_csv(PERFORMANCE_FILE, mode='a', header=not pd.io.common.file_exists(PERFORMANCE_FILE), index=False)
            
        except Exception as e:
            logger.error(f"Error logging performance: {e}")
    
    def start(self):
        """Start the trading engine"""
        logger.info("🚀 Starting AIMn Trading Engine...")
        self.running = True
        
        # Show initial account status
        try:
            account = self.connector.get_account_info()
            logger.info(f"📊 Initial Account Status:")
            logger.info(f"   Buying Power: ${account['buying_power']:,.2f}")
            logger.info(f"   Portfolio Value: ${account['portfolio_value']:,.2f}")
            
            # Check current positions
            positions = self.connector.get_positions()
            if not positions.empty:
                logger.info(f"\n📈 Current Positions:")
                for _, pos in positions.iterrows():
                    logger.info(f"   {pos['symbol']}: {pos['qty']} shares @ ${pos['market_value']:,.2f}")
                    
        except Exception as e:
            logger.error(f"Failed to get account info: {e}")
        
        # Main trading loop
        while self.running:
            try:
                self.run_trading_cycle()
                
                # Wait before next cycle
                logger.info(f"\n⏳ Waiting {self.scan_interval} seconds until next scan...")
                time.sleep(self.scan_interval)
                
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                time.sleep(30)  # Wait 30 seconds on error
    
    def stop(self):
        """Stop the trading engine"""
        logger.info("Stopping AIMn Trading Engine...")
        self.running = False
        
        # Show final statistics
        stats = self.position_manager.get_statistics()
        runtime = (datetime.now() - self.start_time).total_seconds() / 3600
        
        logger.info("="*50)
        logger.info("📊 FINAL STATISTICS:")
        logger.info(f"⏱️  Runtime: {runtime:.1f} hours")
        logger.info(f"📈 Total Trades: {stats['total_trades']}")
        logger.info(f"✅ Winning Trades: {stats['winning_trades']}")
        logger.info(f"❌ Losing Trades: {stats['losing_trades']}")
        logger.info(f"📊 Win Rate: {stats['win_rate']:.1f}%")
        logger.info(f"💰 Total P&L: ${stats['total_pnl']:.2f}")
        logger.info(f"💵 Average P&L: ${stats['avg_pnl']:.2f}")
        logger.info("="*50)


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("🚀 AIMn TRADING SYSTEM V2.0")
    print("="*60)
    print("Philosophy: Let the market pick your trades.")
    print("            Let logic pick your exits.")
    print("="*60 + "\n")
    
    # Initialize Alpaca connector
    print("1️⃣ Connecting to Alpaca...")
    connector = AlpacaTradingConnector(paper_trading=PAPER_TRADING)
    
    # Initialize trading engine
    print("\n2️⃣ Initializing AIMn Trading Engine...")
    engine = AIMnTradingEngine(
        connector=connector,
        symbols=SYMBOLS,
        symbol_params=SYMBOL_PARAMS,
        capital_per_trade=CAPITAL_PER_TRADE,
        scan_interval=SCAN_INTERVAL
    )
    
    # Start trading
    print("\n3️⃣ Starting automated trading...")
    print("   Press Ctrl+C to stop\n")
    
    try:
        engine.start()
    except KeyboardInterrupt:
        print("\n\n⛔ Shutdown signal received")
        engine.stop()


if __name__ == "__main__":
    main()