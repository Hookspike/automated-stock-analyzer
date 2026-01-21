import pandas as pd
from typing import Dict, List, Any, Optional
from .data_cleaner import DataCleaner
from .feature_engineer import FeatureEngineer
from .data_standardizer import DataStandardizer

class DataProcessor:
    """数据处理管理器"""
    
    def __init__(self):
        """初始化数据处理器"""
        self.cleaner = DataCleaner()
        self.feature_engineer = FeatureEngineer()
        self.standardizer = DataStandardizer()
    
    def process_kline_data(self, kline_data: List[Dict[str, Any]], include_technical_indicators: bool = True) -> pd.DataFrame:
        """处理K线数据"""
        # 1. 清洗数据
        cleaned_df = self.cleaner.clean_kline_data(kline_data)
        
        if cleaned_df.empty:
            return cleaned_df
        
        # 2. 生成时间相关特征
        cleaned_df = self.feature_engineer.generate_time_based_features(cleaned_df)
        
        # 3. 生成价格相关特征
        cleaned_df = self.feature_engineer.generate_price_features(cleaned_df)
        
        # 4. 生成波动率特征
        cleaned_df = self.feature_engineer.generate_volatility_features(cleaned_df)
        
        # 5. 计算技术指标
        if include_technical_indicators:
            cleaned_df = self.feature_engineer.calculate_technical_indicators(cleaned_df)
        
        return cleaned_df
    
    def process_financial_data(self, financial_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """处理财务数据"""
        # 1. 清洗数据
        cleaned_df = self.cleaner.clean_financial_data(financial_data)
        
        # 2. 计算基本面特征
        fundamental_features = self.feature_engineer.calculate_fundamental_features(cleaned_df)
        
        return fundamental_features
    
    def process_index_data(self, index_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """处理指数数据"""
        # 1. 清洗数据
        cleaned_df = self.cleaner.clean_index_data(index_data)
        
        if cleaned_df.empty:
            return cleaned_df
        
        # 2. 生成时间相关特征
        cleaned_df = self.feature_engineer.generate_time_based_features(cleaned_df)
        
        # 3. 生成价格相关特征
        cleaned_df = self.feature_engineer.generate_price_features(cleaned_df)
        
        return cleaned_df
    
    def standardize_features(self, df: pd.DataFrame, target: str = 'close', method: str = 'standard') -> pd.DataFrame:
        """标准化特征"""
        if df.empty:
            return df
        
        # 选择数值特征列
        numeric_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col]) and col != target]
        
        # 标准化特征
        standardized_df = self.standardizer.standardize(df, numeric_cols, method)
        
        return standardized_df
    
    def prepare_training_data(self, kline_data: List[Dict[str, Any]], lookback: int = 30, predict_days: int = 1) -> Dict[str, Any]:
        """准备训练数据"""
        # 处理K线数据
        processed_df = self.process_kline_data(kline_data)
        
        if processed_df.empty:
            return {'X': [], 'y': []}
        
        # 选择特征列
        feature_cols = [col for col in processed_df.columns if pd.api.types.is_numeric_dtype(processed_df[col]) and col != 'trade_date']
        
        # 准备输入和输出数据
        X = []
        y = []
        
        for i in range(lookback, len(processed_df) - predict_days + 1):
            # 输入特征
            X.append(processed_df[feature_cols].iloc[i-lookback:i].values.flatten())
            # 输出标签（未来几天的收盘价）
            y.append(processed_df['close'].iloc[i:i+predict_days].values)
        
        return {
            'X': X,
            'y': y,
            'feature_cols': feature_cols,
            'data': processed_df
        }
    
    def select_importance_features(self, df: pd.DataFrame, target: str = 'close', top_n: Optional[int] = 20) -> List[str]:
        """选择重要特征"""
        return self.standardizer.select_features(df, target, top_n=top_n)
