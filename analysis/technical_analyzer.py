import pandas as pd
import numpy as np
from typing import Dict, List, Any

class TechnicalAnalyzer:
    """技术分析类"""
    
    def analyze_trend(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析趋势"""
        if df.empty:
            return {}
        
        # 计算移动平均线
        df['MA5'] = df['close'].rolling(window=5).mean()
        df['MA20'] = df['close'].rolling(window=20).mean()
        df['MA60'] = df['close'].rolling(window=60).mean()
        
        # 判断趋势 - 直接比较当前行与前一行的移动平均值
        if len(df) < 2:
            # 数据不足，返回中性
            trend_analysis = {
                'short_term_trend': '震荡',
                'medium_term_trend': '震荡',
                'long_term_trend': '震荡',
                'ma_relationship': '震荡整理'
            }
        else:
            latest_data = df.iloc[-1]
            prev_data = df.iloc[-2]
            
            trend_analysis = {
                'short_term_trend': '上升' if latest_data['MA5'] > prev_data['MA5'] else '下降',
                'medium_term_trend': '上升' if latest_data['MA20'] > prev_data['MA20'] else '下降',
                'long_term_trend': '上升' if latest_data['MA60'] > prev_data['MA60'] else '下降',
                'ma_relationship': self._analyze_ma_relationship(latest_data)
            }
        
        return trend_analysis
    
    def _analyze_ma_relationship(self, latest_data: pd.Series) -> str:
        """分析移动平均线关系"""
        if latest_data['MA5'] > latest_data['MA20'] > latest_data['MA60']:
            return '多头排列'
        elif latest_data['MA5'] < latest_data['MA20'] < latest_data['MA60']:
            return '空头排列'
        else:
            return '震荡整理'
    
    def analyze_macd(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析MACD指标"""
        if df.empty:
            return {}
        
        # 计算MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['Signal']
        
        latest_data = df.iloc[-1]
        
        macd_analysis = {
            'macd_value': latest_data['MACD'],
            'signal_value': latest_data['Signal'],
            'macd_hist': latest_data['MACD_Hist'],
            'signal': self._analyze_macd_signal(latest_data)
        }
        
        return macd_analysis
    
    def _analyze_macd_signal(self, latest_data: pd.Series) -> str:
        """分析MACD信号"""
        if latest_data['MACD'] > latest_data['Signal'] and latest_data['MACD_Hist'] > 0:
            return '金叉看多'
        elif latest_data['MACD'] < latest_data['Signal'] and latest_data['MACD_Hist'] < 0:
            return '死叉看空'
        else:
            return '信号不明确'
    
    def analyze_kdj(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析KDJ指标"""
        if df.empty:
            return {}
        
        # 计算KDJ
        low_min = df['low'].rolling(window=9).min()
        high_max = df['high'].rolling(window=9).max()
        df['RSV'] = (df['close'] - low_min) / (high_max - low_min) * 100
        df['K'] = df['RSV'].ewm(alpha=1/3, adjust=False).mean()
        df['D'] = df['K'].ewm(alpha=1/3, adjust=False).mean()
        df['J'] = 3 * df['K'] - 2 * df['D']
        
        latest_data = df.iloc[-1]
        
        kdj_analysis = {
            'k_value': latest_data['K'],
            'd_value': latest_data['D'],
            'j_value': latest_data['J'],
            'signal': self._analyze_kdj_signal(latest_data)
        }
        
        return kdj_analysis
    
    def _analyze_kdj_signal(self, latest_data: pd.Series) -> str:
        """分析KDJ信号"""
        if latest_data['K'] > latest_data['D'] and latest_data['J'] > latest_data['K']:
            return '金叉看多'
        elif latest_data['K'] < latest_data['D'] and latest_data['J'] < latest_data['K']:
            return '死叉看空'
        elif latest_data['K'] > 80:
            return '超买'
        elif latest_data['K'] < 20:
            return '超卖'
        else:
            return '信号不明确'
    
    def analyze_rsi(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析RSI指标"""
        if df.empty:
            return {}
        
        # 计算RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        latest_data = df.iloc[-1]
        
        rsi_analysis = {
            'rsi_value': latest_data['RSI'],
            'signal': self._analyze_rsi_signal(latest_data['RSI'])
        }
        
        return rsi_analysis
    
    def _analyze_rsi_signal(self, rsi_value: float) -> str:
        """分析RSI信号"""
        if rsi_value > 70:
            return '超买'
        elif rsi_value < 30:
            return '超卖'
        else:
            return '正常'
    
    def analyze_bollinger_bands(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析布林带"""
        if df.empty:
            return {}
        
        # 计算布林带
        df['BB_Mid'] = df['close'].rolling(window=20).mean()
        df['BB_Std'] = df['close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Mid'] + 2 * df['BB_Std']
        df['BB_Lower'] = df['BB_Mid'] - 2 * df['BB_Std']
        
        latest_data = df.iloc[-1]
        
        bb_analysis = {
            'bb_upper': latest_data['BB_Upper'],
            'bb_mid': latest_data['BB_Mid'],
            'bb_lower': latest_data['BB_Lower'],
            'close_position': self._analyze_bb_position(latest_data)
        }
        
        return bb_analysis
    
    def _analyze_bb_position(self, latest_data: pd.Series) -> str:
        """分析价格在布林带中的位置"""
        if latest_data['close'] > latest_data['BB_Upper']:
            return '突破上轨'
        elif latest_data['close'] < latest_data['BB_Lower']:
            return '突破下轨'
        elif latest_data['close'] > latest_data['BB_Mid']:
            return '中轨上方'
        else:
            return '中轨下方'
    
    def analyze_volume(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析成交量"""
        if df.empty:
            return {}
        
        # 计算成交量指标
        df['VOL_MA5'] = df['vol'].rolling(window=5).mean()
        df['VOL_MA10'] = df['vol'].rolling(window=10).mean()
        
        latest_data = df.iloc[-1]
        
        volume_analysis = {
            'current_volume': latest_data['vol'],
            'volume_ma5': latest_data['VOL_MA5'],
            'volume_ma10': latest_data['VOL_MA10'],
            'volume_trend': self._analyze_volume_trend(latest_data)
        }
        
        return volume_analysis
    
    def _analyze_volume_trend(self, latest_data: pd.Series) -> str:
        """分析成交量趋势"""
        if latest_data['vol'] > latest_data['VOL_MA5'] > latest_data['VOL_MA10']:
            return '放量上涨'
        elif latest_data['vol'] < latest_data['VOL_MA5'] < latest_data['VOL_MA10']:
            return '缩量下跌'
        else:
            return '成交量平稳'
    
    def comprehensive_technical_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """综合技术分析"""
        if df.empty:
            return {}
        
        analysis = {
            'trend_analysis': self.analyze_trend(df),
            'macd_analysis': self.analyze_macd(df),
            'kdj_analysis': self.analyze_kdj(df),
            'rsi_analysis': self.analyze_rsi(df),
            'bollinger_bands_analysis': self.analyze_bollinger_bands(df),
            'volume_analysis': self.analyze_volume(df),
            'overall_signal': self._generate_overall_signal(df)
        }
        
        return analysis
    
    def _generate_overall_signal(self, df: pd.DataFrame) -> str:
        """生成综合信号"""
        # 这里可以根据各个指标的信号综合判断
        # 简单实现：根据趋势和主要指标判断
        trend_analysis = self.analyze_trend(df)
        macd_analysis = self.analyze_macd(df)
        rsi_analysis = self.analyze_rsi(df)
        
        signals = []
        
        # 趋势信号
        if trend_analysis.get('medium_term_trend') == '上升':
            signals.append('看多')
        elif trend_analysis.get('medium_term_trend') == '下降':
            signals.append('看空')
        
        # MACD信号
        if macd_analysis.get('signal') == '金叉看多':
            signals.append('看多')
        elif macd_analysis.get('signal') == '死叉看空':
            signals.append('看空')
        
        # RSI信号
        if rsi_analysis.get('signal') == '超买':
            signals.append('看空')
        elif rsi_analysis.get('signal') == '超卖':
            signals.append('看多')
        
        # 统计信号
        if signals.count('看多') > signals.count('看空'):
            return '看多'
        elif signals.count('看空') > signals.count('看多'):
            return '看空'
        else:
            return '中性'