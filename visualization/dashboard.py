import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from .charts import Charts

class Dashboard:
    """仪表盘类"""
    
    def __init__(self):
        """初始化仪表盘"""
        self.charts = Charts()
    
    def create_stock_dashboard(self, kline_data: List[Dict[str, Any]], 
                             technical_analysis: Dict[str, Any] = None, 
                             fundamental_analysis: Dict[str, Any] = None, 
                             sentiment_analysis: Dict[str, Any] = None, 
                             title: str = '股票分析仪表盘') -> Dict[str, Any]:
        """创建股票分析仪表盘"""
        if not kline_data:
            return {}
        
        df = pd.DataFrame(kline_data)
        
        # 创建图表
        dashboard_data = {
            'title': title,
            'charts': {},
            'summary': {}
        }
        
        # 1. K线图
        kline_fig = self.charts.plot_kline(df)
        dashboard_data['charts']['kline'] = kline_fig
        
        # 2. 移动平均线
        ma_fig = self.charts.plot_ma(df)
        dashboard_data['charts']['ma'] = ma_fig
        
        # 3. MACD指标
        macd_fig = self.charts.plot_macd(df)
        dashboard_data['charts']['macd'] = macd_fig
        
        # 4. RSI指标
        rsi_fig = self.charts.plot_rsi(df)
        dashboard_data['charts']['rsi'] = rsi_fig
        
        # 5. 布林带
        bb_fig = self.charts.plot_bollinger_bands(df)
        dashboard_data['charts']['bollinger_bands'] = bb_fig
        
        # 6. 成交量
        volume_fig = self.charts.plot_volume(df)
        dashboard_data['charts']['volume'] = volume_fig
        
        # 添加分析摘要
        if technical_analysis:
            dashboard_data['summary']['technical'] = technical_analysis
        
        if fundamental_analysis:
            dashboard_data['summary']['fundamental'] = fundamental_analysis
        
        if sentiment_analysis:
            dashboard_data['summary']['sentiment'] = sentiment_analysis
        
        return dashboard_data
    
    def create_strategy_dashboard(self, performance_data: Dict[str, Dict[str, Any]], 
                                title: str = '策略绩效仪表盘') -> Dict[str, Any]:
        """创建策略绩效仪表盘"""
        if not performance_data:
            return {}
        
        dashboard_data = {
            'title': title,
            'charts': {},
            'performance_data': performance_data
        }
        
        # 1. 策略绩效对比图
        performance_fig = self.charts.plot_performance(performance_data)
        dashboard_data['charts']['performance'] = performance_fig
        
        # 添加绩效摘要
        best_strategy = None
        best_return = -float('inf')
        
        for strategy, data in performance_data.items():
            if data['total_return'] > best_return:
                best_return = data['total_return']
                best_strategy = strategy
        
        dashboard_data['best_strategy'] = best_strategy
        dashboard_data['best_return'] = best_return
        
        return dashboard_data
    
    def create_prediction_dashboard(self, historical_data: List[Dict[str, Any]], 
                                  prediction_data: List[float], 
                                  title: str = '价格预测仪表盘') -> Dict[str, Any]:
        """创建价格预测仪表盘"""
        if not historical_data or not prediction_data:
            return {}
        
        df = pd.DataFrame(historical_data)
        
        dashboard_data = {
            'title': title,
            'charts': {},
            'prediction_data': prediction_data
        }
        
        # 1. 历史价格和预测价格对比图
        fig = self.charts.plot_kline(df, title='历史价格与预测价格')
        
        if fig:
            # 获取图表的轴对象
            ax = fig.gca()
            
            # 添加预测价格
            # 假设预测数据是未来几天的价格
            last_date = df['trade_date'].iloc[-1]
            prediction_dates = pd.date_range(last_date, periods=len(prediction_data) + 1)[1:]
            
            # 转换为与历史数据相同的日期格式
            prediction_dates_str = [date.strftime('%Y%m%d') for date in prediction_dates]
            
            # 添加预测价格到图表
            ax.plot(prediction_dates_str, prediction_data, label='预测价格', color='red', linestyle='--')
            ax.legend()
            
            dashboard_data['charts']['prediction'] = fig
        
        return dashboard_data
    
    def save_dashboard(self, dashboard_data: Dict[str, Any], output_dir: str) -> None:
        """保存仪表盘图表"""
        import os
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存图表
        if 'charts' in dashboard_data:
            for chart_name, fig in dashboard_data['charts'].items():
                if fig:
                    filename = os.path.join(output_dir, f'{chart_name}.png')
                    self.charts.save_figure(fig, filename)
        
        print(f"仪表盘图表已保存到 {output_dir}")
    
    def generate_summary_report(self, dashboard_data: Dict[str, Any]) -> str:
        """生成仪表盘摘要报告"""
        report = f"# {dashboard_data.get('title', '股票分析报告')}\n\n"
        
        # 添加技术分析摘要
        if 'summary' in dashboard_data and 'technical' in dashboard_data['summary']:
            technical = dashboard_data['summary']['technical']
            report += "## 技术分析\n"
            report += f"- 整体信号: {technical.get('overall_signal', '中性')}\n"
            report += f"- 短期趋势: {technical.get('trend_analysis', {}).get('short_term_trend', '中性')}\n"
            report += f"- 中期趋势: {technical.get('trend_analysis', {}).get('medium_term_trend', '中性')}\n"
            report += f"- 长期趋势: {technical.get('trend_analysis', {}).get('long_term_trend', '中性')}\n\n"
        
        # 添加基本面分析摘要
        if 'summary' in dashboard_data and 'fundamental' in dashboard_data['summary']:
            fundamental = dashboard_data['summary']['fundamental']
            report += "## 基本面分析\n"
            report += f"- 综合得分: {fundamental.get('overall_score', 0)}\n"
            report += f"- 投资建议: {fundamental.get('investment_advisory', '中性')}\n"
            report += f"- 盈利能力: {fundamental.get('profitability', {}).get('roe_grade', '中性')}\n"
            report += f"- 成长能力: {fundamental.get('growth', {}).get('revenue_growth_grade', '中性')}\n"
            report += f"- 偿债能力: {fundamental.get('solvency', {}).get('current_ratio_grade', '中性')}\n\n"
        
        # 添加情绪分析摘要
        if 'summary' in dashboard_data and 'sentiment' in dashboard_data['summary']:
            sentiment = dashboard_data['summary']['sentiment']
            report += "## 情绪分析\n"
            report += f"- 整体情绪: {sentiment.get('overall_sentiment', '中性')}\n"
            report += f"- 情绪得分: {sentiment.get('overall_average_score', 0)}\n"
            report += f"- 市场影响: {sentiment.get('market_implication', '中性')}\n\n"
        
        # 添加策略绩效摘要
        if 'performance_data' in dashboard_data:
            report += "## 策略绩效\n"
            for strategy, data in dashboard_data['performance_data'].items():
                report += f"### {strategy}\n"
                report += f"- 总收益率: {data.get('total_return', 0)}%\n"
                report += f"- 年化收益率: {data.get('annual_return', 0)}%\n"
                report += f"- 夏普比率: {data.get('sharpe_ratio', 0)}\n"
                report += f"- 最大回撤: {data.get('max_drawdown', 0)}%\n"
                report += f"- 胜率: {data.get('win_rate', 0)}%\n\n"
        
        return report