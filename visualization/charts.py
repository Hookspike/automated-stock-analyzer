import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import seaborn as sns

class Charts:
    """图表绘制类"""
    
    def __init__(self):
        """初始化图表设置"""
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        
        # 设置图表风格
        sns.set_style("whitegrid")
    
    def plot_kline(self, df: pd.DataFrame, title: str = 'K线图') -> plt.Figure:
        """绘制K线图"""
        if df.empty:
            return None
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 绘制收盘价
        ax.plot(df['trade_date'], df['close'], label='收盘价', color='blue')
        
        # 绘制最高价和最低价
        ax.plot(df['trade_date'], df['high'], label='最高价', color='green', alpha=0.5)
        ax.plot(df['trade_date'], df['low'], label='最低价', color='red', alpha=0.5)
        
        # 添加标题和标签
        ax.set_title(title)
        ax.set_xlabel('日期')
        ax.set_ylabel('价格')
        
        # 添加图例
        ax.legend()
        
        # 自动旋转日期标签
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return fig
    
    def plot_ma(self, df: pd.DataFrame, title: str = '移动平均线') -> plt.Figure:
        """绘制移动平均线"""
        if df.empty:
            return None
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 计算移动平均线
        df['MA5'] = df['close'].rolling(window=5).mean()
        df['MA10'] = df['close'].rolling(window=10).mean()
        df['MA20'] = df['close'].rolling(window=20).mean()
        df['MA60'] = df['close'].rolling(window=60).mean()
        
        # 绘制收盘价和移动平均线
        ax.plot(df['trade_date'], df['close'], label='收盘价', color='blue', alpha=0.5)
        ax.plot(df['trade_date'], df['MA5'], label='MA5', color='red')
        ax.plot(df['trade_date'], df['MA10'], label='MA10', color='green')
        ax.plot(df['trade_date'], df['MA20'], label='MA20', color='orange')
        ax.plot(df['trade_date'], df['MA60'], label='MA60', color='purple')
        
        # 添加标题和标签
        ax.set_title(title)
        ax.set_xlabel('日期')
        ax.set_ylabel('价格')
        
        # 添加图例
        ax.legend()
        
        # 自动旋转日期标签
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return fig
    
    def plot_macd(self, df: pd.DataFrame, title: str = 'MACD指标') -> plt.Figure:
        """绘制MACD指标"""
        if df.empty:
            return None
        
        # 计算MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['Signal']
        
        # 创建双轴图表
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
        
        # 绘制收盘价
        ax1.plot(df['trade_date'], df['close'], label='收盘价', color='blue')
        ax1.set_title(title)
        ax1.set_ylabel('价格')
        ax1.legend()
        
        # 绘制MACD
        ax2.plot(df['trade_date'], df['MACD'], label='MACD', color='blue')
        ax2.plot(df['trade_date'], df['Signal'], label='Signal', color='red')
        
        # 绘制MACD柱状图
        colors = ['green' if val > 0 else 'red' for val in df['MACD_Hist']]
        ax2.bar(df['trade_date'], df['MACD_Hist'], color=colors, alpha=0.5)
        
        ax2.set_xlabel('日期')
        ax2.set_ylabel('MACD')
        ax2.legend()
        
        # 自动旋转日期标签
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return fig
    
    def plot_rsi(self, df: pd.DataFrame, title: str = 'RSI指标') -> plt.Figure:
        """绘制RSI指标"""
        if df.empty:
            return None
        
        # 计算RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # 创建双轴图表
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
        
        # 绘制收盘价
        ax1.plot(df['trade_date'], df['close'], label='收盘价', color='blue')
        ax1.set_title(title)
        ax1.set_ylabel('价格')
        ax1.legend()
        
        # 绘制RSI
        ax2.plot(df['trade_date'], df['RSI'], label='RSI', color='purple')
        
        # 添加超买超卖线
        ax2.axhline(y=70, color='red', linestyle='--', label='超买线')
        ax2.axhline(y=30, color='green', linestyle='--', label='超卖线')
        
        ax2.set_xlabel('日期')
        ax2.set_ylabel('RSI')
        ax2.set_ylim(0, 100)
        ax2.legend()
        
        # 自动旋转日期标签
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return fig
    
    def plot_bollinger_bands(self, df: pd.DataFrame, title: str = '布林带') -> plt.Figure:
        """绘制布林带"""
        if df.empty:
            return None
        
        # 计算布林带
        df['BB_Mid'] = df['close'].rolling(window=20).mean()
        df['BB_Std'] = df['close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Mid'] + 2 * df['BB_Std']
        df['BB_Lower'] = df['BB_Mid'] - 2 * df['BB_Std']
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 绘制收盘价
        ax.plot(df['trade_date'], df['close'], label='收盘价', color='blue')
        
        # 绘制布林带
        ax.plot(df['trade_date'], df['BB_Mid'], label='中轨', color='orange')
        ax.plot(df['trade_date'], df['BB_Upper'], label='上轨', color='green', linestyle='--')
        ax.plot(df['trade_date'], df['BB_Lower'], label='下轨', color='red', linestyle='--')
        
        # 填充布林带区域
        ax.fill_between(df['trade_date'], df['BB_Upper'], df['BB_Lower'], color='gray', alpha=0.1)
        
        # 添加标题和标签
        ax.set_title(title)
        ax.set_xlabel('日期')
        ax.set_ylabel('价格')
        
        # 添加图例
        ax.legend()
        
        # 自动旋转日期标签
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return fig
    
    def plot_volume(self, df: pd.DataFrame, title: str = '成交量') -> plt.Figure:
        """绘制成交量"""
        if df.empty:
            return None
        
        fig, ax = plt.subplots(figsize=(12, 4))
        
        # 绘制成交量
        ax.bar(df['trade_date'], df['vol'], label='成交量', color='blue', alpha=0.7)
        
        # 添加标题和标签
        ax.set_title(title)
        ax.set_xlabel('日期')
        ax.set_ylabel('成交量')
        
        # 自动旋转日期标签
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return fig
    
    def plot_performance(self, performance_data: Dict[str, Dict[str, Any]], 
                        title: str = '策略绩效对比') -> plt.Figure:
        """绘制策略绩效对比图"""
        if not performance_data:
            return None
        
        # 提取数据
        strategies = list(performance_data.keys())
        total_returns = [data['total_return'] for data in performance_data.values()]
        annual_returns = [data['annual_return'] for data in performance_data.values()]
        sharpe_ratios = [data['sharpe_ratio'] for data in performance_data.values()]
        max_drawdowns = [data['max_drawdown'] for data in performance_data.values()]
        
        # 创建子图
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(title, fontsize=16)
        
        # 绘制总收益率
        axes[0, 0].bar(strategies, total_returns, color='blue')
        axes[0, 0].set_title('总收益率 (%)')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # 绘制年化收益率
        axes[0, 1].bar(strategies, annual_returns, color='green')
        axes[0, 1].set_title('年化收益率 (%)')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # 绘制夏普比率
        axes[1, 0].bar(strategies, sharpe_ratios, color='purple')
        axes[1, 0].set_title('夏普比率')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # 绘制最大回撤
        axes[1, 1].bar(strategies, max_drawdowns, color='red')
        axes[1, 1].set_title('最大回撤 (%)')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        
        return fig
    
    def plot_portfolio_value(self, dates: List[str], portfolio_values: List[float], 
                           title: str = ' portfolio 价值走势') -> plt.Figure:
        """绘制 portfolio 价值走势"""
        if not dates or not portfolio_values:
            return None
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 绘制 portfolio 价值
        ax.plot(dates, portfolio_values, label='portfolio 价值', color='blue')
        
        # 添加标题和标签
        ax.set_title(title)
        ax.set_xlabel('日期')
        ax.set_ylabel('价值')
        
        # 添加图例
        ax.legend()
        
        # 自动旋转日期标签
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return fig
    
    def save_figure(self, fig: plt.Figure, filename: str) -> None:
        """保存图表"""
        if fig:
            fig.savefig(filename)
            plt.close(fig)
            print(f"图表已保存到 {filename}")
    
    def show_figure(self, fig: plt.Figure) -> None:
        """显示图表"""
        if fig:
            plt.show()
            plt.close(fig)