import numpy as np
import joblib
from typing import Dict, List, Any
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from .base_model import BaseModel

class LinearRegressionModel(BaseModel):
    """线性回归模型"""
    
    def __init__(self, params: Dict[str, Any] = None):
        """初始化模型"""
        self.params = params or {}
        self.model = LinearRegression(**self.params)
    
    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """训练模型"""
        self.model.fit(X, y)
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """预测"""
        return self.model.predict(X)
    
    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """评估模型"""
        y_pred = self.predict(X)
        return self.calculate_metrics(y, y_pred)
    
    def save(self, path: str) -> None:
        """保存模型"""
        joblib.dump(self.model, path)
    
    def load(self, path: str) -> None:
        """加载模型"""
        self.model = joblib.load(path)

class RandomForestModel(BaseModel):
    """随机森林回归模型"""
    
    def __init__(self, params: Dict[str, Any] = None):
        """初始化模型"""
        self.params = params or {
            'n_estimators': 100,
            'max_depth': 10,
            'random_state': 42
        }
        self.model = RandomForestRegressor(**self.params)
    
    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """训练模型"""
        self.model.fit(X, y)
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """预测"""
        return self.model.predict(X)
    
    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """评估模型"""
        y_pred = self.predict(X)
        return self.calculate_metrics(y, y_pred)
    
    def save(self, path: str) -> None:
        """保存模型"""
        joblib.dump(self.model, path)
    
    def load(self, path: str) -> None:
        """加载模型"""
        self.model = joblib.load(path)

class XGBoostModel(BaseModel):
    """XGBoost回归模型"""
    
    def __init__(self, params: Dict[str, Any] = None):
        """初始化模型"""
        self.params = params or {
            'n_estimators': 100,
            'max_depth': 6,
            'learning_rate': 0.1,
            'random_state': 42
        }
        self.model = XGBRegressor(**self.params)
    
    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """训练模型"""
        self.model.fit(X, y)
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """预测"""
        return self.model.predict(X)
    
    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """评估模型"""
        y_pred = self.predict(X)
        return self.calculate_metrics(y, y_pred)
    
    def save(self, path: str) -> None:
        """保存模型"""
        self.model.save_model(path)
    
    def load(self, path: str) -> None:
        """加载模型"""
        self.model.load_model(path)

class LightGBMModel(BaseModel):
    """LightGBM回归模型"""
    
    def __init__(self, params: Dict[str, Any] = None):
        """初始化模型"""
        self.params = params or {
            'n_estimators': 100,
            'max_depth': 6,
            'learning_rate': 0.1,
            'random_state': 42
        }
        self.model = LGBMRegressor(**self.params)
    
    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """训练模型"""
        self.model.fit(X, y)
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """预测"""
        return self.model.predict(X)
    
    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """评估模型"""
        y_pred = self.predict(X)
        return self.calculate_metrics(y, y_pred)
    
    def save(self, path: str) -> None:
        """保存模型"""
        joblib.dump(self.model, path)
    
    def load(self, path: str) -> None:
        """加载模型"""
        self.model = joblib.load(path)