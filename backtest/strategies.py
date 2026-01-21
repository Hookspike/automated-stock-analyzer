import pandas as pd
import numpy as np
from typing import Dict, List, Any
from .base_strategy import BaseStrategy

class MAStrategy(BaseStrategy):
    """移动平均线交叉策略"""
    
    def __init__(self, params: Dict[str, Any] = None):
        """初始化策略"""
        default_params = {
            'short_window': 5,
            'long_window': 20
        }
        default_params.update(params or {})
        super().__init__(default_params)
        
        self.short_window = self.params['short_window']
        self.long_window = self.params['long_window']
    
    def generate_signals(self, df: pd.DataFrame) -> List[int]:
        """生成交易信号"""
        signals = []
        
        # 计算移动平均线
        df['MA_short'] = df['close'].rolling(window=self.short_window).mean()
        df['MA_long'] = df['close'].rolling(window=self.long_window).mean()
        
        for i in range(len(df)):
            if i < self.long_window:
                signals.append(0)  # 无信号
                continue
            
            # 金叉：短期均线上穿长期均线
            if (df.iloc[i]['MA_short'] > df.iloc[i]['MA_long'] and 
                df.iloc[i-1]['MA_short'] <= df.iloc[i-1]['MA_long']):
                signals.append(1)  # 买入信号
            # 死叉：短期均线下穿长期均线
            elif (df.iloc[i]['MA_short'] < df.iloc[i]['MA_long'] and 
                  df.iloc[i-1]['MA_short'] >= df.iloc[i-1]['MA_long']):
                signals.append(-1)  # 卖出信号
            else:
                signals.append(0)  # 无信号
        
        return signals

class MACDStrategy(BaseStrategy):
    """MACD策略"""
    
    def __init__(self, params: Dict[str, Any] = None):
        """初始化策略"""
        default_params = {
            'fast_period': 12,
            'slow_period': 26,
            'signal_period': 9
        }
        default_params.update(params or {})
        super().__init__(default_params)
        
        self.fast_period = self.params['fast_period']
        self.slow_period = self.params['slow_period']
        self.signal_period = self.params['signal_period']
    
    def generate_signals(self, df: pd.DataFrame) -> List[int]:
        """生成交易信号"""
        signals = []
        
        # 计算MACD
        exp1 = df['close'].ewm(span=self.fast_period, adjust=False).mean()
        exp2 = df['close'].ewm(span=self.slow_period, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal'] = df['MACD'].ewm(span=self.signal_period, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['Signal']
        
        for i in range(len(df)):
            if i < self.slow_period:
                signals.append(0)  # 无信号
                continue
            
            # 金叉：MACD线上穿信号线
            if (df.iloc[i]['MACD'] > df.iloc[i]['Signal'] and 
                df.iloc[i-1]['MACD'] <= df.iloc[i-1]['Signal']):
                signals.append(1)  # 买入信号
            # 死叉：MACD线下穿信号线
            elif (df.iloc[i]['MACD'] < df.iloc[i]['Signal'] and 
                  df.iloc[i-1]['MACD'] >= df.iloc[i-1]['Signal']):
                signals.append(-1)  # 卖出信号
            else:
                signals.append(0)  # 无信号
        
        return signals

class RSIStrategy(BaseStrategy):
    """RSI策略"""
    
    def __init__(self, params: Dict[str, Any] = None):
        """初始化策略"""
        default_params = {
            'window': 14,
            'oversold_level': 30,
            'overbought_level': 70
        }
        default_params.update(params or {})
        super().__init__(default_params)
        
        self.window = self.params['window']
        self.oversold_level = self.params['oversold_level']
        self.overbought_level = self.params['overbought_level']
    
    def generate_signals(self, df: pd.DataFrame) -> List[int]:
        """生成交易信号"""
        signals = []
        
        # 计算RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.window).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        for i in range(len(df)):
            if i < self.window:
                signals.append(0)  # 无信号
                continue
            
            # 超卖：RSI低于超卖水平
            if df.iloc[i]['RSI'] < self.oversold_level:
                signals.append(1)  # 买入信号
            # 超买：RSI高于超买水平
            elif df.iloc[i]['RSI'] > self.overbought_level:
                signals.append(-1)  # 卖出信号
            else:
                signals.append(0)  # 无信号
        
        return signals

class KDJStrategy(BaseStrategy):
    """KDJ策略"""
    
    def __init__(self, params: Dict[str, Any] = None):
        """初始化策略"""
        default_params = {
            'window': 9,
            'oversold_level': 20,
            'overbought_level': 80
        }
        default_params.update(params or {})
        super().__init__(default_params)
        
        self.window = self.params['window']
        self.oversold_level = self.params['oversold_level']
        self.overbought_level = self.params['overbought_level']
    
    def generate_signals(self, df: pd.DataFrame) -> List[int]:
        """生成交易信号"""
        signals = []
        
        # 计算KDJ
        low_min = df['low'].rolling(window=self.window).min()
        high_max = df['high'].rolling(window=self.window).max()
        df['RSV'] = (df['close'] - low_min) / (high_max - low_min) * 100
        df['K'] = df['RSV'].ewm(alpha=1/3, adjust=False).mean()
        df['D'] = df['K'].ewm(alpha=1/3, adjust=False).mean()
        df['J'] = 3 * df['K'] - 2 * df['D']
        
        for i in range(len(df)):
            if i < self.window:
                signals.append(0)  # 无信号
                continue
            
            # 金叉：K线上穿D线
            if (df.iloc[i]['K'] > df.iloc[i]['D'] and 
                df.iloc[i-1]['K'] <= df.iloc[i-1]['D']):
                signals.append(1)  # 买入信号
            # 死叉：K线下穿D线
            elif (df.iloc[i]['K'] < df.iloc[i]['D'] and 
                  df.iloc[i-1]['K'] >= df.iloc[i-1]['D']):
                signals.append(-1)  # 卖出信号
            else:
                signals.append(0)  # 无信号
        
        return signals

class BollingerBandsStrategy(BaseStrategy):
    """布林带策略"""
    
    def __init__(self, params: Dict[str, Any] = None):
        """初始化策略"""
        default_params = {
            'window': 20,
            'std_dev': 2
        }
        default_params.update(params or {})
        super().__init__(default_params)
        
        self.window = self.params['window']
        self.std_dev = self.params['std_dev']
    
    def generate_signals(self, df: pd.DataFrame) -> List[int]:
        """生成交易信号"""
        signals = []
        
        # 计算布林带
        df['BB_Mid'] = df['close'].rolling(window=self.window).mean()
        df['BB_Std'] = df['close'].rolling(window=self.window).std()
        df['BB_Upper'] = df['BB_Mid'] + self.std_dev * df['BB_Std']
        df['BB_Lower'] = df['BB_Mid'] - self.std_dev * df['BB_Std']
        
        for i in range(len(df)):
            if i < self.window:
                signals.append(0)  # 无信号
                continue
            
            # 突破下轨：买入信号
            if df.iloc[i]['close'] < df.iloc[i]['BB_Lower']:
                signals.append(1)  # 买入信号
            # 突破上轨：卖出信号
            elif df.iloc[i]['close'] > df.iloc[i]['BB_Upper']:
                signals.append(-1)  # 卖出信号
            else:
                signals.append(0)  # 无信号
        
        return signals