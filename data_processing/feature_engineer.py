import pandas as pd
import numpy as np
from typing import Dict, List, Any

class FeatureEngineer:
    """特征工程类"""
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算技术指标"""
        if df.empty:
            return df
        
        # 计算移动平均线
        df['MA5'] = df['close'].rolling(window=5).mean()
        df['MA10'] = df['close'].rolling(window=10).mean()
        df['MA20'] = df['close'].rolling(window=20).mean()
        df['MA60'] = df['close'].rolling(window=60).mean()
        
        # 计算MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['Signal']
        
        # 计算KDJ
        low_min = df['low'].rolling(window=9).min()
        high_max = df['high'].rolling(window=9).max()
        df['RSV'] = (df['close'] - low_min) / (high_max - low_min) * 100
        df['K'] = df['RSV'].ewm(alpha=1/3, adjust=False).mean()
        df['D'] = df['K'].ewm(alpha=1/3, adjust=False).mean()
        df['J'] = 3 * df['K'] - 2 * df['D']
        
        # 计算RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # 计算布林带
        df['BB_Mid'] = df['close'].rolling(window=20).mean()
        df['BB_Std'] = df['close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Mid'] + 2 * df['BB_Std']
        df['BB_Lower'] = df['BB_Mid'] - 2 * df['BB_Std']
        
        # 计算成交量指标
        df['VOL_MA5'] = df['vol'].rolling(window=5).mean()
        df['VOL_MA10'] = df['vol'].rolling(window=10).mean()
        
        # 计算价格波动指标
        df['ATR'] = df[['high', 'low', 'close']].apply(lambda x: max(x[0]-x[1], abs(x[0]-x[2]), abs(x[1]-x[2])), axis=1).rolling(window=14).mean()
        
        # 计算动量指标
        df['MOM'] = df['close'] - df['close'].shift(10)
        
        # 处理缺失值
        df = df.fillna(0)
        
        return df
    
    def calculate_fundamental_features(self, financial_df: pd.DataFrame) -> Dict[str, Any]:
        """计算基本面特征"""
        if financial_df.empty:
            return {}
        
        features = {}
        
        # 获取最新一期财务数据
        latest_data = financial_df.iloc[-1] if not financial_df.empty else None
        
        if latest_data is not None:
            # 盈利能力指标
            features['roe'] = latest_data.get('roe', 0)  # 净资产收益率
            features['roa'] = latest_data.get('roa', 0)  # 总资产收益率
            features['profit_margin'] = latest_data.get('grossprofit_margin', 0)  # 毛利率
            
            # 成长能力指标
            features['revenue_growth'] = latest_data.get('revenue_yoy', 0)  # 营收同比增长
            features['profit_growth'] = latest_data.get('net_profit_yoy', 0)  # 净利润同比增长
            
            # 偿债能力指标
            features['current_ratio'] = latest_data.get('current_ratio', 0)  # 流动比率
            features['quick_ratio'] = latest_data.get('quick_ratio', 0)  # 速动比率
            features['debt_to_asset'] = latest_data.get('asset_liab_ratio', 0)  # 资产负债率
            
            # 运营能力指标
            features['inventory_turnover'] = latest_data.get('inventory_turnover', 0)  # 存货周转率
            features['asset_turnover'] = latest_data.get('total_asset_turnover', 0)  # 总资产周转率
            
            # 估值指标
            features['pe'] = latest_data.get('pe', 0)  # 市盈率
            features['pb'] = latest_data.get('pb', 0)  # 市净率
            features['ps'] = latest_data.get('ps', 0)  # 市销率
        
        return features
    
    def generate_time_based_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """生成时间相关特征"""
        if df.empty or 'trade_date' not in df.columns:
            return df
        
        # 提取年、月、日
        df['year'] = df['trade_date'].dt.year
        df['month'] = df['trade_date'].dt.month
        df['day'] = df['trade_date'].dt.day
        
        # 提取星期几
        df['weekday'] = df['trade_date'].dt.weekday
        
        # 提取是否是月末、季末、年末
        df['is_month_end'] = df['trade_date'].dt.is_month_end.astype(int)
        df['is_quarter_end'] = df['trade_date'].dt.is_quarter_end.astype(int)
        df['is_year_end'] = df['trade_date'].dt.is_year_end.astype(int)
        
        return df
    
    def generate_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """生成价格相关特征"""
        if df.empty:
            return df
        
        # 价格变化率
        df['price_change_pct'] = df['close'].pct_change() * 100
        
        # 价格波动幅度
        df['price_range_pct'] = (df['high'] - df['low']) / df['open'] * 100
        
        # 收盘价相对开盘价的变化
        df['close_to_open_pct'] = (df['close'] - df['open']) / df['open'] * 100
        
        # 最高价相对开盘价的变化
        df['high_to_open_pct'] = (df['high'] - df['open']) / df['open'] * 100
        
        # 最低价相对开盘价的变化
        df['low_to_open_pct'] = (df['low'] - df['open']) / df['open'] * 100
        
        # 处理缺失值
        df = df.fillna(0)
        
        return df
    
    def generate_volatility_features(self, df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        """生成波动率特征"""
        if df.empty:
            return df
        
        # 计算收益率
        df['returns'] = df['close'].pct_change()
        
        # 计算历史波动率
        df['volatility'] = df['returns'].rolling(window=window).std() * np.sqrt(252)  # 年化波动率
        
        # 计算收益率的偏度和峰度
        df['skewness'] = df['returns'].rolling(window=window).skew()
        df['kurtosis'] = df['returns'].rolling(window=window).kurt()
        
        # 处理缺失值
        df = df.fillna(0)
        
        return df