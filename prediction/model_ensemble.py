import numpy as np
from typing import Dict, List, Any
from .base_model import BaseModel

class ModelEnsemble(BaseModel):
    """模型融合类"""
    
    def __init__(self, models: List[BaseModel], weights: List[float] = None):
        """初始化模型融合器"""
        self.models = models
        self.weights = weights or [1.0 / len(models)] * len(models)
        
        # 确保权重和为1
        total_weight = sum(self.weights)
        self.weights = [w / total_weight for w in self.weights]
    
    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """训练所有模型"""
        for i, model in enumerate(self.models):
            print(f"训练模型 {i+1}/{len(self.models)}...")
            model.train(X, y)
            print(f"模型 {i+1} 训练完成")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """融合预测"""
        # 获取所有模型的预测结果
        predictions = []
        for model in self.models:
            pred = model.predict(X)
            predictions.append(pred)
        
        # 加权融合
        weighted_predictions = np.zeros_like(predictions[0])
        for pred, weight in zip(predictions, self.weights):
            weighted_predictions += pred * weight
        
        return weighted_predictions
    
    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """评估融合模型"""
        # 评估融合模型
        y_pred = self.predict(X)
        ensemble_metrics = self.calculate_metrics(y, y_pred)
        
        # 评估每个单独模型
        individual_metrics = []
        for i, model in enumerate(self.models):
            metrics = model.evaluate(X, y)
            individual_metrics.append({
                f'model_{i+1}': metrics
            })
        
        return {
            'ensemble': ensemble_metrics,
            'individual': individual_metrics
        }
    
    def save(self, path: str) -> None:
        """保存所有模型"""
        import os
        os.makedirs(path, exist_ok=True)
        
        for i, model in enumerate(self.models):
            model_path = os.path.join(path, f'model_{i+1}')
            model.save(model_path)
        
        # 保存权重
        np.save(os.path.join(path, 'weights.npy'), self.weights)
    
    def load(self, path: str) -> None:
        """加载所有模型"""
        import os
        
        # 加载权重
        weights_path = os.path.join(path, 'weights.npy')
        if os.path.exists(weights_path):
            self.weights = np.load(weights_path).tolist()
        
        # 加载每个模型
        for i, model in enumerate(self.models):
            model_path = os.path.join(path, f'model_{i+1}')
            if os.path.exists(model_path):
                model.load(model_path)