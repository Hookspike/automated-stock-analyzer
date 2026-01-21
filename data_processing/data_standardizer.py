import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from typing import Dict, List, Optional

class DataStandardizer:
    """数据标准化类"""
    
    def __init__(self):
        """初始化标准化器"""
        self.scalers = {
            'standard': StandardScaler(),
            'minmax': MinMaxScaler(),
            'robust': RobustScaler()
        }
        self.fitted_scalers = {}
    
    def standardize(self, df: pd.DataFrame, columns: List[str], method: str = 'standard') -> pd.DataFrame:
        """标准化数据"""
        if df.empty or not columns:
            return df
        
        # 选择标准化方法
        scaler = self.scalers.get(method, self.scalers['standard'])
        
        # 复制数据
        standardized_df = df.copy()
        
        # 只对存在的列进行标准化
        valid_columns = [col for col in columns if col in standardized_df.columns]
        
        if valid_columns:
            # 拟合并转换数据
            standardized_df[valid_columns] = scaler.fit_transform(standardized_df[valid_columns])
            
            # 保存拟合后的标准化器
            self.fitted_scalers[method] = scaler
        
        return standardized_df
    
    def normalize(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """归一化数据到[0, 1]范围"""
        return self.standardize(df, columns, method='minmax')
    
    def robust_scale(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """使用RobustScaler进行标准化（对异常值不敏感）"""
        return self.standardize(df, columns, method='robust')
    
    def transform_new_data(self, df: pd.DataFrame, columns: List[str], method: str = 'standard') -> pd.DataFrame:
        """使用已拟合的标准化器转换新数据"""
        if df.empty or not columns:
            return df
        
        # 检查是否有拟合后的标准化器
        if method not in self.fitted_scalers:
            raise ValueError(f"未找到已拟合的 {method} 标准化器")
        
        # 复制数据
        transformed_df = df.copy()
        
        # 只对存在的列进行转换
        valid_columns = [col for col in columns if col in transformed_df.columns]
        
        if valid_columns:
            transformed_df[valid_columns] = self.fitted_scalers[method].transform(transformed_df[valid_columns])
        
        return transformed_df
    
    def get_feature_importance(self, df: pd.DataFrame, target: str) -> Dict[str, float]:
        """计算特征重要性（基于相关性）"""
        if df.empty or target not in df.columns:
            return {}
        
        # 计算各特征与目标变量的相关性
        correlations = {}
        for col in df.columns:
            if col != target and pd.api.types.is_numeric_dtype(df[col]):
                corr = df[col].corr(df[target])
                correlations[col] = abs(corr)
        
        # 按重要性排序
        sorted_correlations = dict(sorted(correlations.items(), key=lambda item: item[1], reverse=True))
        
        return sorted_correlations
    
    def select_features(self, df: pd.DataFrame, target: str, top_n: Optional[int] = None, threshold: Optional[float] = None) -> List[str]:
        """选择重要特征"""
        if df.empty or target not in df.columns:
            return []
        
        # 计算特征重要性
        importance = self.get_feature_importance(df, target)
        
        selected_features = []
        
        if top_n:
            # 选择前N个重要特征
            selected_features = list(importance.keys())[:top_n]
        elif threshold:
            # 选择重要性超过阈值的特征
            selected_features = [col for col, imp in importance.items() if imp >= threshold]
        else:
            # 选择所有特征
            selected_features = list(importance.keys())
        
        return selected_features