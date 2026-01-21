import pandas as pd
import numpy as np
from typing import Dict, List, Any

class DataCleaner:
    """数据清洗类"""
    
    def clean_kline_data(self, kline_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """清洗K线数据"""
        if not kline_data:
            return pd.DataFrame()
        
        # 转换为DataFrame
        df = pd.DataFrame(kline_data)
        
        # 处理日期列
        if 'trade_date' in df.columns:
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            df = df.sort_values('trade_date')
        
        # 处理数值列
        numeric_cols = ['open', 'high', 'low', 'close', 'pre_close', 'change', 'pct_chg', 'vol', 'amount']
        for col in numeric_cols:
            if col in df.columns:
                # 转换为数值类型
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # 处理缺失值
                df[col] = df[col].fillna(method='ffill')  # 前向填充
                df[col] = df[col].fillna(method='bfill')  # 后向填充
        
        # 检查并移除异常值（使用3σ法则）
        for col in ['open', 'high', 'low', 'close']:
            if col in df.columns:
                mean = df[col].mean()
                std = df[col].std()
                df = df[(df[col] >= mean - 3 * std) & (df[col] <= mean + 3 * std)]
        
        return df
    
    def clean_financial_data(self, financial_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """清洗财务数据"""
        if not financial_data:
            return pd.DataFrame()
        
        # 转换为DataFrame
        df = pd.DataFrame(financial_data)
        
        # 处理数值列
        for col in df.columns:
            if col not in ['ts_code', 'ann_date', 'f_ann_date', 'end_date']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 处理缺失值
        df = df.fillna(0)
        
        return df
    
    def clean_index_data(self, index_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """清洗指数数据"""
        if not index_data:
            return pd.DataFrame()
        
        # 转换为DataFrame
        df = pd.DataFrame(index_data)
        
        # 处理日期列
        if 'trade_date' in df.columns:
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            df = df.sort_values('trade_date')
        
        # 处理数值列
        numeric_cols = ['open', 'high', 'low', 'close', 'pre_close', 'change', 'pct_chg', 'vol', 'amount']
        for col in numeric_cols:
            if col in df.columns:
                # 转换为数值类型
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # 处理缺失值
                df[col] = df[col].fillna(method='ffill')  # 前向填充
                df[col] = df[col].fillna(method='bfill')  # 后向填充
        
        return df
    
    def remove_duplicates(self, df: pd.DataFrame, subset: List[str] = None) -> pd.DataFrame:
        """移除重复数据"""
        if subset:
            return df.drop_duplicates(subset=subset)
        else:
            return df.drop_duplicates()
    
    def handle_missing_values(self, df: pd.DataFrame, strategy: str = 'fill') -> pd.DataFrame:
        """处理缺失值"""
        if strategy == 'fill':
            # 数值列填充0或均值
            numeric_cols = df.select_dtypes(include=['number']).columns
            df[numeric_cols] = df[numeric_cols].fillna(0)
            
            # 非数值列填充空字符串
            non_numeric_cols = df.select_dtypes(exclude=['number']).columns
            df[non_numeric_cols] = df[non_numeric_cols].fillna('')
        elif strategy == 'drop':
            # 移除包含缺失值的行
            df = df.dropna()
        
        return df