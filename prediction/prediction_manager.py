import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from .traditional_models import LinearRegressionModel, RandomForestModel, XGBoostModel, LightGBMModel
from .model_ensemble import ModelEnsemble

# Try to import deep learning models, but handle import error
try:
    from .deep_learning_models import LSTMModel, GRUModel, TransformerModel
    deep_learning_available = True
except ImportError:
    print("PyTorch not available, deep learning models will be skipped")
    deep_learning_available = False
    LSTMModel = None
    GRUModel = None
    TransformerModel = None

class PredictionManager:
    """预测管理器"""
    
    def __init__(self):
        """初始化预测管理器"""
        self.models = {
            'linear_regression': LinearRegressionModel,
            'random_forest': RandomForestModel,
            'xgboost': XGBoostModel,
            'lightgbm': LightGBMModel
        }
        
        # Add deep learning models only if available
        if deep_learning_available:
            self.models.update({
                'lstm': LSTMModel,
                'gru': GRUModel,
                'transformer': TransformerModel
            })
        
        self.trained_models = {}
    
    def create_model(self, model_name: str, params: Dict[str, Any] = None) -> Any:
        """创建模型"""
        if model_name not in self.models:
            raise ValueError(f"不支持的模型类型: {model_name}")
        
        if model_name in ['lstm', 'gru', 'transformer']:
            # 深度学习模型需要输入大小
            input_size = params.pop('input_size', 10)
            model = self.models[model_name](input_size=input_size, **params)
        else:
            # 传统机器学习模型
            model = self.models[model_name](params)
        
        return model
    
    def train_model(self, model_name: str, X: np.ndarray, y: np.ndarray, params: Dict[str, Any] = None) -> Dict[str, float]:
        """训练模型"""
        # 创建模型
        model = self.create_model(model_name, params)
        
        # 训练模型
        model.train(X, y)
        
        # 评估模型
        metrics = model.evaluate(X, y)
        
        # 保存训练好的模型
        self.trained_models[model_name] = model
        
        print(f"模型 {model_name} 训练完成，评估指标: {metrics}")
        return metrics
    
    def predict_with_model(self, model_name: str, X: np.ndarray) -> np.ndarray:
        """使用指定模型进行预测"""
        if model_name not in self.trained_models:
            raise ValueError(f"模型 {model_name} 尚未训练")
        
        model = self.trained_models[model_name]
        return model.predict(X)
    
    def create_ensemble(self, model_names: List[str], weights: List[float] = None) -> ModelEnsemble:
        """创建模型融合器"""
        # 收集训练好的模型
        models = []
        for model_name in model_names:
            if model_name not in self.trained_models:
                raise ValueError(f"模型 {model_name} 尚未训练")
            models.append(self.trained_models[model_name])
        
        # 创建模型融合器
        ensemble = ModelEnsemble(models, weights)
        return ensemble
    
    def train_ensemble(self, model_names: List[str], X: np.ndarray, y: np.ndarray, weights: List[float] = None) -> Dict[str, Any]:
        """训练并评估模型融合"""
        # 创建模型融合器
        ensemble = self.create_ensemble(model_names, weights)
        
        # 评估融合模型
        metrics = ensemble.evaluate(X, y)
        
        # 保存融合模型
        self.trained_models['ensemble'] = ensemble
        
        print(f"模型融合评估完成，指标: {metrics}")
        return metrics
    
    def save_model(self, model_name: str, path: str) -> None:
        """保存模型"""
        if model_name not in self.trained_models:
            raise ValueError(f"模型 {model_name} 尚未训练")
        
        model = self.trained_models[model_name]
        model.save(path)
        print(f"模型 {model_name} 已保存到 {path}")
    
    def load_model(self, model_name: str, path: str, params: Dict[str, Any] = None) -> None:
        """加载模型"""
        # 创建模型实例
        model = self.create_model(model_name, params)
        
        # 加载模型权重
        model.load(path)
        
        # 保存到训练好的模型字典
        self.trained_models[model_name] = model
        print(f"模型 {model_name} 已从 {path} 加载")
    
    def compare_models(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Dict[str, float]]:
        """比较所有训练好的模型"""
        comparisons = {}
        
        for model_name, model in self.trained_models.items():
            metrics = model.evaluate(X, y)
            comparisons[model_name] = metrics
        
        return comparisons
    
    def prepare_data(self, processed_df: pd.DataFrame, target: str = 'close', lookback: int = 30) -> Dict[str, np.ndarray]:
        """准备训练数据"""
        # 选择特征列
        feature_cols = [col for col in processed_df.columns if pd.api.types.is_numeric_dtype(processed_df[col]) and col != target]
        
        # 准备输入和输出数据
        X = []
        y = []
        
        for i in range(lookback, len(processed_df)):
            # 输入特征
            X.append(processed_df[feature_cols].iloc[i-lookback:i].values.flatten())
            # 输出标签
            y.append(processed_df[target].iloc[i])
        
        return {
            'X': np.array(X),
            'y': np.array(y),
            'feature_cols': feature_cols
        }
    
    def predict(self, symbol: str, model_type: str = 'ensemble', days: int = 5) -> Dict[str, Any]:
        """预测股票价格"""
        from datetime import datetime, timedelta
        import numpy as np
        import pandas as pd
        
        # 获取股票数据
        try:
            # 确保股票代码格式正确，添加后缀
            if not (symbol.endswith('.SZ') or symbol.endswith('.SH')):
                if symbol.startswith('6'):
                    full_symbol = f"{symbol}.SH"
                else:
                    full_symbol = f"{symbol}.SZ"
            else:
                full_symbol = symbol
            
            from data_collection.data_collector import DataCollector
            data_collector = DataCollector()
            
            # 获取足够的历史数据用于训练和预测
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')  # 使用过去一年的数据
            
            stock_data = data_collector.get_stock_data(symbol, start_date, end_date, freq='D')
            data = stock_data.get('data', [])
            
            if not data:
                # 如果获取不到数据，返回错误信息
                return {
                    'symbol': symbol,
                    'model_type': model_type,
                    'prediction_days': days,
                    'predictions': [],
                    'confidence': 0.0,
                    'prediction_time': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'error': '无法获取股票历史数据'
                }
            
            # 转换为DataFrame
            df = pd.DataFrame(data)
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            df.set_index('trade_date', inplace=True)
            df.sort_index(inplace=True)
            
            # 只使用收盘价作为特征，简化预测逻辑
            # 使用前5天的收盘价预测后1天的收盘价
            look_back = 5
            
            # 准备训练数据
            close_prices = df['close'].values
            
            if len(close_prices) < look_back + 1:
                return {
                    'symbol': symbol,
                    'model_type': model_type,
                    'prediction_days': days,
                    'predictions': [],
                    'confidence': 0.0,
                    'prediction_time': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'error': '数据量不足，无法进行预测'
                }
            
            # 构建训练集
            X = []
            y = []
            
            for i in range(len(close_prices) - look_back):
                # 使用前look_back天的收盘价预测后1天的收盘价
                X.append(close_prices[i:i+look_back])
                # 预测后一天的收盘价
                y.append(close_prices[i+look_back])
            
            X = np.array(X)
            y = np.array(y)
            
            # 数据归一化 - 对深度学习模型至关重要
            from sklearn.preprocessing import MinMaxScaler
            scaler = MinMaxScaler(feature_range=(0, 1))
            scaler_y = MinMaxScaler(feature_range=(0, 1))
            
            # 对X进行归一化（每个样本是look_back天的价格）
            # 将X重塑为2D数组，每个样本一行，look_back列
            X_2d = X.reshape(-1, look_back)
            X_scaled = scaler.fit_transform(X_2d)
            
            # 对y进行归一化
            y_2d = y.reshape(-1, 1)
            y_scaled = scaler_y.fit_transform(y_2d).flatten()
            
            # 根据model_type训练不同的模型
            if model_type == 'ensemble':
                # 模型融合：训练多个基础模型，然后融合
                print(f"训练模型融合...")
                
                # 基础模型列表
                base_models = ['xgboost', 'lightgbm', 'random_forest']
                model_keys = []
                
                # 训练每个基础模型
                for base_model in base_models:
                    model_key = f"{symbol}_{base_model}"
                    model_keys.append(model_key)
                    
                    if model_key not in self.trained_models:
                        print(f"训练基础模型: {base_model}")
                        # 训练基础模型，使用原始数据
                        model = self.create_model(base_model, None)
                        model.train(X, y)
                        self.trained_models[model_key] = model
                
                # 创建融合模型
                from .model_ensemble import ModelEnsemble
                ensemble = ModelEnsemble([self.trained_models[model_key] for model_key in model_keys])
                ensemble_model_key = f"{symbol}_ensemble"
                self.trained_models[ensemble_model_key] = ensemble
                
                # 使用融合模型进行预测
                final_model_key = ensemble_model_key
                # 保存用于预测的数据类型
                use_scaled = False
            elif model_type == 'traditional':
                # 传统机器学习模型：使用随机森林模型
                print(f"使用传统机器学习模型...")
                traditional_model = 'random_forest'  # 使用随机森林作为传统模型的默认选项，与xgboost区分
                model_key = f"{symbol}_{traditional_model}"
                
                if model_key not in self.trained_models:
                    print(f"训练传统模型: {traditional_model}")
                    # 训练模型，使用原始数据
                    model = self.create_model(traditional_model, None)
                    model.train(X, y)
                    self.trained_models[model_key] = model
                
                # 使用传统模型进行预测
                final_model_key = model_key
                # 保存用于预测的数据类型
                use_scaled = False
            elif model_type == 'deep_learning':
                # 深度学习模型：使用LSTM模型
                print(f"使用深度学习模型...")
                deep_model = 'lstm'  # 默认使用LSTM模型
                model_key = f"{symbol}_{deep_model}"
                
                if model_key not in self.trained_models:
                    print(f"训练深度学习模型: {deep_model}")
                    # 训练模型，使用归一化数据
                    # 对于深度学习模型，需要正确设置input_size
                    # input_size是每个时间步的特征数量，这里每个时间步只有一个特征：收盘价，所以input_size=1
                    # seq_len是时间序列的长度，即look_back
                    input_size = 1
                    
                    # 重塑归一化后的X为LSTM期望的形状：(batch_size, seq_len, input_size)
                    # X_scaled形状：(n_samples, look_back)
                    X_lstm_scaled = X_scaled.reshape(X_scaled.shape[0], X_scaled.shape[1], input_size)
                    
                    model = self.create_model(deep_model, {'input_size': input_size})
                    model.train(X_lstm_scaled, y_scaled)
                    self.trained_models[model_key] = model
                
                # 使用深度学习模型进行预测
                final_model_key = model_key
                # 保存用于预测的数据类型
                use_scaled = True
            else:
                # 单一模型：直接使用model_type作为模型名称
                model_key = f"{symbol}_{model_type}"
                
                if model_key not in self.trained_models:
                    print(f"训练 {model_type} 模型...")
                    # 训练模型，使用原始数据
                    model = self.create_model(model_type, None)
                    model.train(X, y)
                    self.trained_models[model_key] = model
                
                # 使用单一模型进行预测
                final_model_key = model_key
                # 保存用于预测的数据类型
                use_scaled = False
            
            # 获取最新的价格数据作为预测的起点
            latest_prices = close_prices[-look_back:].reshape(1, -1)
            
            # 进行多步预测
            predictions = []
            current_prices = latest_prices.copy()
            
            for i in range(days):
                if use_scaled:
                    # 深度学习模型：使用归一化数据进行预测
                    # 归一化输入数据
                    current_prices_scaled = scaler.transform(current_prices)
                    
                    # 重塑为LSTM期望的形状：(batch_size, seq_len, input_size)
                    input_data = current_prices_scaled.reshape(1, look_back, 1)
                    
                    # 使用模型进行预测（得到归一化后的价格）
                    next_price_scaled = self.predict_with_model(final_model_key, input_data)[0]
                    
                    # 反归一化预测结果
                    next_price = scaler_y.inverse_transform(np.array([[next_price_scaled]]))[0][0]
                else:
                    # 传统模型：直接使用原始数据进行预测
                    # 使用模型进行预测
                    next_price = self.predict_with_model(final_model_key, current_prices)[0]
                
                # 计算变化值和变化百分比
                previous_price = current_prices[0][-1]
                change = next_price - previous_price
                change_percent = (change / previous_price) * 100 if previous_price != 0 else 0
                
                # 计算预测日期
                pred_date = (datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d')
                
                # 添加到预测结果
                predictions.append({
                    'date': pred_date,
                    'predicted_price': round(float(next_price), 2),
                    'change': round(float(change), 2),
                    'change_percent': round(float(change_percent), 2)
                })
                
                # 更新当前价格序列，用于下一步预测
                current_prices = np.roll(current_prices, -1, axis=1)
                current_prices[0][-1] = next_price
            
            # 计算模型置信度（使用训练数据的R²）
            from sklearn.metrics import r2_score
            
            if use_scaled:
                # 深度学习模型：使用归一化数据计算R²
                # 重塑X为LSTM期望的形状
                X_lstm_scaled = X_scaled.reshape(X_scaled.shape[0], X_scaled.shape[1], 1)
                
                # 预测训练数据
                y_pred_train_scaled = self.predict_with_model(final_model_key, X_lstm_scaled)
                
                # 反归一化预测结果
                y_pred_train = scaler_y.inverse_transform(y_pred_train_scaled.reshape(-1, 1)).flatten()
            else:
                # 传统模型：直接预测训练数据
                y_pred_train = self.predict_with_model(final_model_key, X)
            
            r2 = r2_score(y, y_pred_train)
            confidence = max(0.5, min(r2, 0.99))  # 限制在0.5到0.99之间
            
            return {
                'symbol': symbol,
                'model_type': model_type,
                'prediction_days': days,
                'predictions': predictions,
                'confidence': round(float(confidence), 4),
                'prediction_time': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                'r2_score': round(float(r2), 4)
            }
            
        except Exception as e:
            print(f"预测失败: {e}")
            import traceback
            traceback.print_exc()
            # 返回错误信息
            return {
                'symbol': symbol,
                'model_type': model_type,
                'prediction_days': days,
                'predictions': [],
                'confidence': 0.0,
                'prediction_time': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                'error': f'预测失败: {str(e)}'
            }