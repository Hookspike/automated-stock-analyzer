from abc import ABC, abstractmethod
from typing import Dict, List, Any, Tuple
import pandas as pd

class BaseStrategy(ABC):
    """策略抽象基类"""
    
    def __init__(self, params: Dict[str, Any] = None):
        """初始化策略"""
        self.params = params or {}
        self.position = 0  # 当前持仓
        self.capital = 1000000  # 初始资金
        self.historical_orders = []  # 历史订单
        self.historical_positions = []  # 历史持仓
        self.historical_capital = []  # 历史资金
    
    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> List[int]:
        """生成交易信号"""
        pass
    
    def execute_backtest(self, df: pd.DataFrame) -> Dict[str, Any]:
        """执行回测"""
        # 生成交易信号
        signals = self.generate_signals(df)
        
        # 模拟交易
        self._simulate_trading(df, signals)
        
        # 计算绩效
        performance = self._calculate_performance(df)
        
        return {
            'performance': performance,
            'historical_orders': self.historical_orders,
            'historical_positions': self.historical_positions,
            'historical_capital': self.historical_capital
        }
    
    def _simulate_trading(self, df: pd.DataFrame, signals: List[int]):
        """模拟交易"""
        current_position = 0
        current_capital = self.capital
        
        for i, signal in enumerate(signals):
            close_price = df.iloc[i]['close']
            
            # 记录当前状态
            self.historical_positions.append(current_position)
            self.historical_capital.append(current_capital)
            
            # 执行交易信号
            if signal == 1 and current_position == 0:
                # 买入
                shares = current_capital // close_price
                current_position = shares
                current_capital -= shares * close_price
                
                # 记录订单
                self.historical_orders.append({
                    'date': df.iloc[i]['trade_date'],
                    'signal': 'buy',
                    'price': close_price,
                    'shares': shares,
                    'capital': current_capital
                })
            elif signal == -1 and current_position > 0:
                # 卖出
                current_capital += current_position * close_price
                
                # 记录订单
                self.historical_orders.append({
                    'date': df.iloc[i]['trade_date'],
                    'signal': 'sell',
                    'price': close_price,
                    'shares': current_position,
                    'capital': current_capital
                })
                
                current_position = 0
    
    def _calculate_performance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """计算绩效"""
        # 计算最终资金
        final_capital = self.historical_capital[-1]
        if self.historical_positions[-1] > 0:
            final_capital += self.historical_positions[-1] * df.iloc[-1]['close']
        
        # 计算收益率
        total_return = (final_capital - self.capital) / self.capital * 100
        
        # 计算年化收益率（假设一年252个交易日）
        trading_days = len(df)
        annual_return = (pow((1 + total_return / 100), 252 / trading_days) - 1) * 100
        
        # 计算最大回撤
        portfolio_values = []
        for i, capital in enumerate(self.historical_capital):
            if i < len(df):
                position_value = self.historical_positions[i] * df.iloc[i]['close']
                portfolio_values.append(capital + position_value)
        
        max_drawdown = self._calculate_max_drawdown(portfolio_values)
        
        # 计算夏普比率（假设无风险利率为3%）
        sharpe_ratio = self._calculate_sharpe_ratio(portfolio_values)
        
        # 计算胜率
        win_rate = self._calculate_win_rate()
        
        return {
            'initial_capital': self.capital,
            'final_capital': final_capital,
            'total_return': round(total_return, 2),
            'annual_return': round(annual_return, 2),
            'max_drawdown': round(max_drawdown, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'win_rate': round(win_rate, 2),
            'trading_days': trading_days,
            'number_of_trades': len(self.historical_orders)
        }
    
    def _calculate_max_drawdown(self, portfolio_values: List[float]) -> float:
        """计算最大回撤"""
        if not portfolio_values:
            return 0
        
        max_value = portfolio_values[0]
        max_drawdown = 0
        
        for value in portfolio_values:
            if value > max_value:
                max_value = value
            drawdown = (max_value - value) / max_value * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return max_drawdown
    
    def _calculate_sharpe_ratio(self, portfolio_values: List[float]) -> float:
        """计算夏普比率"""
        if len(portfolio_values) < 2:
            return 0
        
        # 计算日收益率
        daily_returns = []
        for i in range(1, len(portfolio_values)):
            return_rate = (portfolio_values[i] - portfolio_values[i-1]) / portfolio_values[i-1]
            daily_returns.append(return_rate)
        
        # 计算平均日收益率和标准差
        avg_return = np.mean(daily_returns)
        std_return = np.std(daily_returns)
        
        if std_return == 0:
            return 0
        
        # 计算夏普比率（假设无风险利率为3%）
        risk_free_rate = 0.03 / 252  # 日无风险利率
        sharpe_ratio = (avg_return - risk_free_rate) / std_return * np.sqrt(252)  # 年化夏普比率
        
        return sharpe_ratio
    
    def _calculate_win_rate(self) -> float:
        """计算胜率"""
        if len(self.historical_orders) < 2:
            return 0
        
        win_trades = 0
        total_trades = len(self.historical_orders) // 2  # 每两次订单为一次完整交易
        
        for i in range(0, len(self.historical_orders), 2):
            if i + 1 < len(self.historical_orders):
                buy_order = self.historical_orders[i]
                sell_order = self.historical_orders[i+1]
                
                if sell_order['price'] > buy_order['price']:
                    win_trades += 1
        
        return win_trades / total_trades * 100 if total_trades > 0 else 0

# 导入numpy
import numpy as np