import pandas as pd
import numpy as np
from typing import Dict, List, Any
from .strategies import MAStrategy, MACDStrategy, RSIStrategy, KDJStrategy, BollingerBandsStrategy

class BacktestManager:
    """回测管理器"""
    
    def __init__(self):
        """初始化回测管理器"""
        self.strategies = {
            'ma': MAStrategy,
            'macd': MACDStrategy,
            'rsi': RSIStrategy,
            'kdj': KDJStrategy,
            'bollinger_bands': BollingerBandsStrategy,
            'ma_crossover': MAStrategy  # 添加ma_crossover策略映射
        }
        self.backtest_results = {}
    
    def run_backtest(self, strategy_name: str, df: pd.DataFrame, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """运行单个策略回测"""
        if strategy_name not in self.strategies:
            raise ValueError(f"不支持的策略类型: {strategy_name}")
        
        # 创建策略实例
        strategy = self.strategies[strategy_name](params)
        
        # 执行回测
        result = strategy.execute_backtest(df)
        
        # 保存回测结果
        self.backtest_results[strategy_name] = result
        
        print(f"策略 {strategy_name} 回测完成，总收益率: {result['performance']['total_return']}%")
        
        return result
    
    def run_multiple_backtests(self, strategy_names: List[str], df: pd.DataFrame, 
                             params_dict: Dict[str, Dict[str, Any]] = None) -> Dict[str, Dict[str, Any]]:
        """运行多个策略回测"""
        if not strategy_names:
            return {}
        
        results = {}
        
        for strategy_name in strategy_names:
            params = params_dict.get(strategy_name, {}) if params_dict else {}
            result = self.run_backtest(strategy_name, df, params)
            results[strategy_name] = result
        
        return results
    
    def compare_strategies(self, df: pd.DataFrame, params_dict: Dict[str, Dict[str, Any]] = None) -> Dict[str, Any]:
        """比较所有策略的表现"""
        # 运行所有策略回测
        strategy_names = list(self.strategies.keys())
        results = self.run_multiple_backtests(strategy_names, df, params_dict)
        
        # 提取绩效指标
        performance_metrics = {}
        for strategy_name, result in results.items():
            performance_metrics[strategy_name] = result['performance']
        
        # 计算排名
        rankings = self._rank_strategies(performance_metrics)
        
        return {
            'performance_metrics': performance_metrics,
            'rankings': rankings,
            'best_strategy': rankings['total_return'][0][0] if rankings['total_return'] else None
        }
    
    def _rank_strategies(self, performance_metrics: Dict[str, Dict[str, Any]]) -> Dict[str, List[Tuple[str, float]]]:
        """对策略进行排名"""
        rankings = {
            'total_return': [],
            'annual_return': [],
            'sharpe_ratio': [],
            'max_drawdown': [],
            'win_rate': []
        }
        
        # 按各指标排序
        for metric in rankings.keys():
            if metric == 'max_drawdown':
                # 最大回撤越小越好
                sorted_strategies = sorted(performance_metrics.items(), 
                                         key=lambda x: x[1][metric])
            else:
                # 其他指标越大越好
                sorted_strategies = sorted(performance_metrics.items(), 
                                         key=lambda x: x[1][metric], reverse=True)
            
            rankings[metric] = [(name, data[metric]) for name, data in sorted_strategies]
        
        return rankings
    
    def optimize_strategy(self, strategy_name: str, df: pd.DataFrame, 
                         param_grid: Dict[str, List[Any]]) -> Dict[str, Any]:
        """优化策略参数"""
        if strategy_name not in self.strategies:
            raise ValueError(f"不支持的策略类型: {strategy_name}")
        
        best_params = None
        best_performance = None
        best_total_return = -float('inf')
        
        # 生成参数组合
        param_combinations = self._generate_param_combinations(param_grid)
        
        print(f"开始优化 {strategy_name} 策略，共 {len(param_combinations)} 组参数组合")
        
        for params in param_combinations:
            # 创建策略实例
            strategy = self.strategies[strategy_name](params)
            
            # 执行回测
            result = strategy.execute_backtest(df)
            total_return = result['performance']['total_return']
            
            # 记录最佳参数
            if total_return > best_total_return:
                best_total_return = total_return
                best_params = params
                best_performance = result['performance']
            
            print(f"参数 {params}，收益率: {total_return}%")
        
        print(f"优化完成，最佳参数: {best_params}，最佳收益率: {best_total_return}%")
        
        return {
            'best_params': best_params,
            'best_performance': best_performance,
            'best_total_return': best_total_return
        }
    
    def _generate_param_combinations(self, param_grid: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
        """生成参数组合"""
        import itertools
        
        # 提取参数名和参数值列表
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        
        # 生成所有可能的参数组合
        combinations = list(itertools.product(*param_values))
        
        # 转换为字典列表
        param_combinations = []
        for combo in combinations:
            param_dict = {}
            for name, value in zip(param_names, combo):
                param_dict[name] = value
            param_combinations.append(param_dict)
        
        return param_combinations
    
    def generate_backtest_report(self, strategy_name: str, df: pd.DataFrame, 
                                params: Dict[str, Any] = None) -> Dict[str, Any]:
        """生成回测报告"""
        # 运行回测
        result = self.run_backtest(strategy_name, df, params)
        
        # 生成报告
        report = {
            'strategy': strategy_name,
            'params': params,
            'performance': result['performance'],
            'trades': result['historical_orders'],
            'summary': self._generate_summary(result['performance'])
        }
        
        return report
    
    def _generate_summary(self, performance: Dict[str, Any]) -> str:
        """生成回测摘要"""
        total_return = performance['total_return']
        annual_return = performance['annual_return']
        max_drawdown = performance['max_drawdown']
        sharpe_ratio = performance['sharpe_ratio']
        win_rate = performance['win_rate']
        
        summary = f"回测摘要：\n"
        summary += f"总收益率: {total_return}%\n"
        summary += f"年化收益率: {annual_return}%\n"
        summary += f"最大回撤: {max_drawdown}%\n"
        summary += f"夏普比率: {sharpe_ratio}\n"
        summary += f"胜率: {win_rate}%\n"
        
        # 评估策略表现
        if total_return > 50:
            summary += "策略表现优秀，收益率显著高于市场平均水平\n"
        elif total_return > 20:
            summary += "策略表现良好，收益率高于市场平均水平\n"
        elif total_return > 0:
            summary += "策略表现一般，收益率为正但低于市场平均水平\n"
        else:
            summary += "策略表现不佳，收益率为负\n"
        
        return summary
    
    def run_backtest(self, strategy_name: str, symbol: str = None, start_date: str = None, end_date: str = None, df: pd.DataFrame = None, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """运行单个策略回测（支持两种调用方式）"""
        if strategy_name not in self.strategies:
            raise ValueError(f"不支持的策略类型: {strategy_name}")
        
        # 如果提供了df，直接使用
        if df is not None:
            # 创建策略实例
            strategy = self.strategies[strategy_name](params)
            
            # 执行回测
            result = strategy.execute_backtest(df)
            
            # 保存回测结果
            self.backtest_results[strategy_name] = result
            
            print(f"策略 {strategy_name} 回测完成，总收益率: {result['performance']['total_return']}%")
            
            return result
        else:
            # 从数据收集器获取真实股票数据
            from data_collection.data_collector import DataCollector
            
            # 创建数据收集器实例
            data_collector = DataCollector()
            
            # 获取股票历史数据
            data_dict = data_collector.get_stock_data(symbol, start_date, end_date)
            
            # 检查是否获取到数据
            if not data_dict['data']:
                raise ValueError(f"无法获取 {symbol} 的历史数据")
            
            # 将数据转换为DataFrame
            df = pd.DataFrame(data_dict['data'], columns=data_dict['columns'])
            
            # 确保数据按日期排序
            if 'trade_date' in df.columns:
                df = df.sort_values('trade_date')
            
            # 重置索引
            df = df.reset_index(drop=True)
            
            # 创建策略实例
            strategy = self.strategies[strategy_name](params)
            
            # 执行回测
            result = strategy.execute_backtest(df)
            
            # 保存回测结果
            self.backtest_results[strategy_name] = result
            
            print(f"策略 {strategy_name} 回测完成，总收益率: {result['performance']['total_return']}%")
            
            return result