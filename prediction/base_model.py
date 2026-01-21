from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import numpy as np

class BaseModel(ABC):
    """预测模型抽象基类"""
    
    @abstractmethod
    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """训练模型"""
        pass
    
    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """预测"""
        pass
    
    @abstractmethod
    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """评估模型"""
        pass
    
    @abstractmethod
    def save(self, path: str) -> None:
        """保存模型"""
        pass
    
    @abstractmethod
    def load(self, path: str) -> None:
        """加载模型"""
        pass
    
    def calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """计算评估指标"""
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
        
        metrics = {
            'mse': mean_squared_error(y_true, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
            'mae': mean_absolute_error(y_true, y_pred),
            'r2': r2_score(y_true, y_pred)
        }
        
        return metrics