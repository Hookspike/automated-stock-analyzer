import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from typing import Dict, List, Any
from .base_model import BaseModel

class LSTMModel(BaseModel):
    """LSTM时间序列预测模型"""
    
    def __init__(self, input_size: int, hidden_size: int = 64, num_layers: int = 2, output_size: int = 1, dropout: float = 0.2):
        """初始化模型"""
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.output_size = output_size
        self.dropout = dropout
        
        # 直接定义LSTM层和线性层，不使用nn.Sequential
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0  # 只有多层时才使用dropout
        )
        self.fc = nn.Linear(hidden_size, output_size)
        
        self.criterion = nn.MSELoss()
        self.optimizer = optim.Adam(
            list(self.lstm.parameters()) + list(self.fc.parameters()),
            lr=0.001
        )
    
    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """训练模型"""
        # 转换为PyTorch张量
        X_tensor = torch.tensor(X, dtype=torch.float32)
        y_tensor = torch.tensor(y, dtype=torch.float32)
        
        # 训练模型
        self.lstm.train()
        self.fc.train()
        
        for epoch in range(100):  # 简单训练100个 epoch
            self.optimizer.zero_grad()
            
            # 前向传播 - LSTM
            lstm_out, _ = self.lstm(X_tensor)  # lstm_out形状: (batch_size, seq_len, hidden_size)
            # 取最后一个时间步的输出
            last_out = lstm_out[:, -1, :]  # 形状: (batch_size, hidden_size)
            # 全连接层
            outputs = self.fc(last_out).squeeze()  # 形状: (batch_size)
            
            # 计算损失
            loss = self.criterion(outputs, y_tensor)
            
            # 反向传播
            loss.backward()
            self.optimizer.step()
            
            if (epoch + 1) % 10 == 0:
                print(f'Epoch [{epoch+1}/100], Loss: {loss.item():.4f}')
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """预测"""
        # 转换为PyTorch张量
        X_tensor = torch.tensor(X, dtype=torch.float32)
        
        # 预测
        self.lstm.eval()
        self.fc.eval()
        with torch.no_grad():
            # LSTM前向传播
            lstm_out, _ = self.lstm(X_tensor)
            # 取最后一个时间步的输出
            last_out = lstm_out[:, -1, :]
            # 全连接层
            outputs = self.fc(last_out).squeeze()
        
        # 确保输出形状正确
        if outputs.ndim == 0:
            outputs = outputs.unsqueeze(0)
        
        return outputs.numpy()
    
    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """评估模型"""
        y_pred = self.predict(X)
        return self.calculate_metrics(y, y_pred)
    
    def save(self, path: str) -> None:
        """保存模型"""
        torch.save({
            'lstm_state_dict': self.lstm.state_dict(),
            'fc_state_dict': self.fc.state_dict()
        }, path)
    
    def load(self, path: str) -> None:
        """加载模型"""
        checkpoint = torch.load(path)
        self.lstm.load_state_dict(checkpoint['lstm_state_dict'])
        self.fc.load_state_dict(checkpoint['fc_state_dict'])

class GRUModel(BaseModel):
    """GRU时间序列预测模型"""
    
    def __init__(self, input_size: int, hidden_size: int = 64, num_layers: int = 2, output_size: int = 1, dropout: float = 0.2):
        """初始化模型"""
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.output_size = output_size
        self.dropout = dropout
        
        # 创建GRU模型
        self.model = nn.Sequential(
            nn.GRU(input_size=input_size, hidden_size=hidden_size, num_layers=num_layers, 
                   batch_first=True, dropout=dropout),
            lambda x: x[0],  # 提取GRU的输出，忽略隐藏状态
            nn.Linear(hidden_size, output_size)
        )
        
        self.criterion = nn.MSELoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
    
    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """训练模型"""
        # 转换为PyTorch张量
        X_tensor = torch.tensor(X, dtype=torch.float32)
        y_tensor = torch.tensor(y, dtype=torch.float32)
        
        # 重塑输入数据为GRU格式
        seq_len = 1
        X_tensor = X_tensor.view(-1, seq_len, self.input_size)
        
        # 训练模型
        self.model.train()
        
        for epoch in range(100):
            self.optimizer.zero_grad()
            
            # 前向传播
            outputs = self.model(X_tensor)
            
            # 计算损失
            loss = self.criterion(outputs, y_tensor)
            
            # 反向传播
            loss.backward()
            self.optimizer.step()
            
            if (epoch + 1) % 10 == 0:
                print(f'Epoch [{epoch+1}/100], Loss: {loss.item():.4f}')
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """预测"""
        # 转换为PyTorch张量
        X_tensor = torch.tensor(X, dtype=torch.float32)
        
        # 重塑输入数据为GRU格式
        seq_len = 1
        X_tensor = X_tensor.view(-1, seq_len, self.input_size)
        
        # 预测
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(X_tensor)
        
        return outputs.numpy()
    
    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """评估模型"""
        y_pred = self.predict(X)
        return self.calculate_metrics(y, y_pred)
    
    def save(self, path: str) -> None:
        """保存模型"""
        torch.save(self.model.state_dict(), path)
    
    def load(self, path: str) -> None:
        """加载模型"""
        self.model.load_state_dict(torch.load(path))

class TransformerModel(BaseModel):
    """Transformer时间序列预测模型"""
    
    def __init__(self, input_size: int, d_model: int = 64, nhead: int = 2, num_encoder_layers: int = 2, 
                 num_decoder_layers: int = 2, dim_feedforward: int = 128, output_size: int = 1):
        """初始化模型"""
        self.input_size = input_size
        self.d_model = d_model
        self.output_size = output_size
        
        # 创建Transformer模型
        self.model = nn.Sequential(
            nn.Linear(input_size, d_model),  # 输入嵌入
            nn.Transformer(
                d_model=d_model,
                nhead=nhead,
                num_encoder_layers=num_encoder_layers,
                num_decoder_layers=num_decoder_layers,
                dim_feedforward=dim_feedforward
            ),
            nn.Linear(d_model, output_size)  # 输出层
        )
        
        self.criterion = nn.MSELoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
    
    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """训练模型"""
        # 转换为PyTorch张量
        X_tensor = torch.tensor(X, dtype=torch.float32)
        y_tensor = torch.tensor(y, dtype=torch.float32)
        
        # 训练模型
        self.model.train()
        
        for epoch in range(100):
            self.optimizer.zero_grad()
            
            # 前向传播
            outputs = self.model(X_tensor)
            
            # 计算损失
            loss = self.criterion(outputs, y_tensor)
            
            # 反向传播
            loss.backward()
            self.optimizer.step()
            
            if (epoch + 1) % 10 == 0:
                print(f'Epoch [{epoch+1}/100], Loss: {loss.item():.4f}')
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """预测"""
        # 转换为PyTorch张量
        X_tensor = torch.tensor(X, dtype=torch.float32)
        
        # 预测
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(X_tensor)
        
        return outputs.numpy()
    
    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """评估模型"""
        y_pred = self.predict(X)
        return self.calculate_metrics(y, y_pred)
    
    def save(self, path: str) -> None:
        """保存模型"""
        torch.save(self.model.state_dict(), path)
    
    def load(self, path: str) -> None:
        """加载模型"""
        self.model.load_state_dict(torch.load(path))