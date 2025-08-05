# indicators.py
"""
Technical indicators for AIMn Trading System
Includes RSI Real, MACD, Volume, and ATR calculations
"""

import pandas as pd
import numpy as np
from typing import Dict

try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    print("Warning: TA-Lib not installed. Using fallback calculations.")

class AIMnIndicators:
    """Calculate technical indicators for trading decisions"""
    
    @staticmethod
    def calculate_rsi_real(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate RSI Real (price-based RSI)
        RSI Real = (Close - Lowest Low) / (Highest High - Lowest Low) * 100
        """
        highest_high = df['high'].rolling(window=period).max()
        lowest_low = df['low'].rolling(window=period).min()
        
        # Avoid division by zero
        price_range = highest_high - lowest_low
        price_range[price_range == 0] = 1
        
        rsi_real = ((df['close'] - lowest_low) / price_range) * 100
        
        # Fill NaN values with 50 (neutral)
        rsi_real = rsi_real.fillna(50)
        
        return rsi_real
    
    @staticmethod
    def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """Calculate MACD indicator"""
        if TALIB_AVAILABLE:
            macd, signal_line, hist = talib.MACD(df['close'], fastperiod=fast, slowperiod=slow, signalperiod=signal)
        else:
            # Fallback calculation
            exp1 = df['close'].ewm(span=fast, adjust=False).mean()
            exp2 = df['close'].ewm(span=slow, adjust=False).mean()
            macd = exp1 - exp2
            signal_line = macd.ewm(span=signal, adjust=False).mean()
            hist = macd - signal_line
        
        # Detect crossovers
        macd_cross_up = (macd > signal_line) & (macd.shift(1) <= signal_line.shift(1))
        macd_cross_down = (macd < signal_line) & (macd.shift(1) >= signal_line.shift(1))
        
        return {
            'macd': macd,
            'signal': signal_line,
            'histogram': hist,
            'macd_cross_up': macd_cross_up,
            'macd_cross_down': macd_cross_down
        }
    
    @staticmethod
    def calculate_volume_indicators(df: pd.DataFrame, ma_period: int = 20) -> Dict[str, pd.Series]:
        """Calculate volume-based indicators"""
        # Volume moving average
        volume_ma = df['volume'].rolling(window=ma_period).mean()
        
        # Volume ratio
        volume_ratio = df['volume'] / volume_ma
        volume_ratio = volume_ratio.fillna(1.0)
        
        # On-Balance Volume (OBV)
        obv = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
        
        # OBV moving average
        obv_ma = obv.rolling(window=ma_period).mean()
        
        # OBV trend (1 for up, -1 for down)
        obv_trend = np.where(obv > obv_ma, 1, -1)
        
        # Price change percentage
        price_change = df['close'].pct_change() * 100
        
        # Volume direction
        volume_direction = np.where(
            (df['volume'] > volume_ma * 1.1) & (price_change > 0.1), 1,
            np.where(
                (df['volume'] > volume_ma * 1.1) & (price_change < -0.1), -1,
                0
            )
        )
        
        return {
            'volume_ma': volume_ma,
            'volume_ratio': volume_ratio,
            'obv': obv,
            'obv_ma': obv_ma,
            'obv_trend': obv_trend,
            'volume_direction': volume_direction,
            'price_change': price_change
        }
    
    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        if TALIB_AVAILABLE:
            atr = talib.ATR(df['high'], df['low'], df['close'], timeperiod=period)
        else:
            # Fallback calculation
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())
            
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(window=period).mean()
        
        return atr
    
    @staticmethod
    def calculate_atr_indicators(df: pd.DataFrame, atr_period: int = 14, ma_period: int = 20) -> Dict[str, pd.Series]:
        """Calculate ATR-based indicators"""
        atr = AIMnIndicators.calculate_atr(df, atr_period)
        atr_ma = atr.rolling(window=ma_period).mean()
        
        # ATR ratio
        atr_ratio = atr / atr_ma
        atr_ratio = atr_ratio.fillna(1.0)
        
        return {
            'atr': atr,
            'atr_ma': atr_ma,
            'atr_ratio': atr_ratio
        }
    
    @staticmethod
    def calculate_all_indicators(df: pd.DataFrame, params: Dict) -> pd.DataFrame:
        """Calculate all indicators and add to dataframe"""
        df = df.copy()
        
        # Get parameters with defaults
        rsi_period = params.get('rsi_period', 14)
        macd_fast = params.get('macd_fast', 12)
        macd_slow = params.get('macd_slow', 26)
        macd_signal = params.get('macd_signal', 9)
        volume_ma_period = params.get('volume_ma_period', 20)
        atr_period = params.get('atr_period', 14)
        atr_ma_period = params.get('atr_ma_period', 20)
        
        # Calculate RSI Real
        df['rsi_real'] = AIMnIndicators.calculate_rsi_real(df, rsi_period)
        
        # Calculate MACD
        macd_dict = AIMnIndicators.calculate_macd(df, macd_fast, macd_slow, macd_signal)
        for key, value in macd_dict.items():
            df[key] = value
        
        # Calculate Volume indicators
        volume_dict = AIMnIndicators.calculate_volume_indicators(df, volume_ma_period)
        for key, value in volume_dict.items():
            df[key] = value
        
        # Calculate ATR indicators
        atr_dict = AIMnIndicators.calculate_atr_indicators(df, atr_period, atr_ma_period)
        for key, value in atr_dict.items():
            df[key] = value
        
        # Fill any remaining NaN values
        df = df.fillna(method='ffill').fillna(method='bfill')
        
        return df
    
    @staticmethod
    def check_entry_conditions(df: pd.DataFrame, params: Dict) -> Dict[str, bool]:
        """Check if entry conditions are met"""
        if len(df) < 2:
            return {'buy': False, 'sell': False}
        
        latest = df.iloc[-1]
        
        # Get thresholds
        rsi_oversold = params.get('rsi_oversold', 30)
        rsi_overbought = params.get('rsi_overbought', 70)
        volume_threshold = params.get('volume_threshold', 1.2)
        atr_threshold = params.get('atr_threshold', 1.3)
        
        # RSI conditions
        rsi_buy = latest['rsi_real'] <= rsi_oversold
        rsi_sell = latest['rsi_real'] >= rsi_overbought
        
        # MACD conditions
        macd_buy = latest.get('macd_cross_up', False)
        macd_sell = latest.get('macd_cross_down', False)
        
        # Volume conditions
        high_volume = latest['volume_ratio'] >= volume_threshold
        volume_buy = high_volume and latest['obv_trend'] > 0
        volume_sell = high_volume and latest['obv_trend'] < 0
        
        # ATR condition
        high_volatility = latest['atr_ratio'] >= atr_threshold
        
        # Combined conditions
        buy_signal = rsi_buy and macd_buy and volume_buy and high_volatility
        sell_signal = rsi_sell and macd_sell and volume_sell and high_volatility
        
        return {
            'buy': buy_signal,
            'sell': sell_signal,
            'rsi_buy': rsi_buy,
            'rsi_sell': rsi_sell,
            'macd_buy': macd_buy,
            'macd_sell': macd_sell,
            'volume_buy': volume_buy,
            'volume_sell': volume_sell,
            'high_volatility': high_volatility
        }


# Test the indicators
if __name__ == "__main__":
    # Create sample data
    dates = pd.date_range('2023-01-01', periods=100, freq='1min')
    np.random.seed(42)
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': 100 + np.random.randn(100).cumsum(),
        'high': 102 + np.random.randn(100).cumsum(),
        'low': 98 + np.random.randn(100).cumsum(),
        'close': 100 + np.random.randn(100).cumsum(),
        'volume': 1000 + np.random.randint(-100, 100, 100)
    })
    
    # Test parameters
    params = {
        'rsi_period': 14,
        'rsi_oversold': 30,
        'rsi_overbought': 70,
        'macd_fast': 12,
        'macd_slow': 26,
        'macd_signal': 9,
        'volume_threshold': 1.2,
        'atr_threshold': 1.3
    }
    
    # Calculate indicators
    df_with_indicators = AIMnIndicators.calculate_all_indicators(df, params)
    
    # Check conditions
    conditions = AIMnIndicators.check_entry_conditions(df_with_indicators, params)
    
    print("Sample Indicator Calculations:")
    print(f"Latest RSI Real: {df_with_indicators['rsi_real'].iloc[-1]:.2f}")
    print(f"Latest MACD: {df_with_indicators['macd'].iloc[-1]:.4f}")
    print(f"Latest Volume Ratio: {df_with_indicators['volume_ratio'].iloc[-1]:.2f}")
    print(f"Latest ATR Ratio: {df_with_indicators['atr_ratio'].iloc[-1]:.2f}")
    print(f"\nEntry Conditions: {conditions}")