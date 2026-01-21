import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import os
from .dashboard import Dashboard

class ReportGenerator:
    """报告生成器类"""
    
    def __init__(self):
        """初始化报告生成器"""
        self.dashboard = Dashboard()
    
    def generate_stock_analysis_report(self, stock_code: str, stock_name: str, 
                                     kline_data: List[Dict[str, Any]], 
                                     technical_analysis: Dict[str, Any] = None, 
                                     fundamental_analysis: Dict[str, Any] = None, 
                                     sentiment_analysis: Dict[str, Any] = None, 
                                     output_dir: str = './reports') -> str:
        """生成股票分析报告"""
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 创建仪表盘
        dashboard_data = self.dashboard.create_stock_dashboard(
            kline_data, technical_analysis, fundamental_analysis, sentiment_analysis,
            title=f'{stock_name}({stock_code}) 分析报告'
        )
        
        # 保存仪表盘图表
        report_dir = os.path.join(output_dir, f'{stock_code}')
        self.dashboard.save_dashboard(dashboard_data, report_dir)
        
        # 生成报告文本
        report_content = self._generate_report_content(stock_code, stock_name, dashboard_data)
        
        # 保存报告文本
        report_file = os.path.join(report_dir, 'analysis_report.md')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"股票分析报告已生成到 {report_file}")
        
        return report_file
    
    def _generate_report_content(self, stock_code: str, stock_name: str, 
                               dashboard_data: Dict[str, Any]) -> str:
        """生成报告内容"""
        report = f"# {stock_name}({stock_code}) 分析报告\n\n"
        
        # 添加报告头部
        report += "## 报告信息\n"
        report += f"- 股票代码: {stock_code}\n"
        report += f"- 股票名称: {stock_name}\n"
        report += f"- 报告生成日期: {pd.Timestamp.now().strftime('%Y-%m-%d')}\n\n"
        
        # 添加市场概览
        report += "## 市场概览\n"
        if 'charts' in dashboard_data and 'kline' in dashboard_data['charts']:
            report += "### 价格走势\n"
            report += "![K线图](kline.png)\n\n"
            
            report += "### 成交量\n"
            report += "![成交量](volume.png)\n\n"
        
        # 添加技术分析
        report += "## 技术分析\n"
        if 'summary' in dashboard_data and 'technical' in dashboard_data['summary']:
            technical = dashboard_data['summary']['technical']
            
            report += "### 趋势分析\n"
            report += f"- 短期趋势: {technical.get('trend_analysis', {}).get('short_term_trend', '中性')}\n"
            report += f"- 中期趋势: {technical.get('trend_analysis', {}).get('medium_term_trend', '中性')}\n"
            report += f"- 长期趋势: {technical.get('trend_analysis', {}).get('long_term_trend', '中性')}\n"
            report += f"- 均线关系: {technical.get('trend_analysis', {}).get('ma_relationship', '中性')}\n\n"
            
            report += "### 指标分析\n"
            report += "![MACD](macd.png)\n"
            report += "![RSI](rsi.png)\n"
            report += "![布林带](bollinger_bands.png)\n\n"
            
            report += f"### 整体信号\n"
            report += f"- 综合技术信号: {technical.get('overall_signal', '中性')}\n\n"
        
        # 添加基本面分析
        report += "## 基本面分析\n"
        if 'summary' in dashboard_data and 'fundamental' in dashboard_data['summary']:
            fundamental = dashboard_data['summary']['fundamental']
            
            report += "### 盈利能力\n"
            report += f"- 净资产收益率(ROE): {fundamental.get('profitability', {}).get('roe', 0)}%\n"
            report += f"- 总资产收益率(ROA): {fundamental.get('profitability', {}).get('roa', 0)}%\n"
            report += f"- 毛利率: {fundamental.get('profitability', {}).get('profit_margin', 0)}%\n\n"
            
            report += "### 成长能力\n"
            report += f"- 营收同比增长: {fundamental.get('growth', {}).get('revenue_growth', 0)}%\n"
            report += f"- 净利润同比增长: {fundamental.get('growth', {}).get('profit_growth', 0)}%\n\n"
            
            report += "### 偿债能力\n"
            report += f"- 流动比率: {fundamental.get('solvency', {}).get('current_ratio', 0)}\n"
            report += f"- 速动比率: {fundamental.get('solvency', {}).get('quick_ratio', 0)}\n"
            report += f"- 资产负债率: {fundamental.get('solvency', {}).get('debt_to_asset', 0)}%\n\n"
            
            report += "### 估值水平\n"
            report += f"- 市盈率(PE): {fundamental.get('valuation', {}).get('pe', 0)}\n"
            report += f"- 市净率(PB): {fundamental.get('valuation', {}).get('pb', 0)}\n"
            report += f"- 市销率(PS): {fundamental.get('valuation', {}).get('ps', 0)}\n\n"
            
            report += "### 综合评估\n"
            report += f"- 综合得分: {fundamental.get('overall_score', 0)}\n"
            report += f"- 投资建议: {fundamental.get('investment_advisory', '中性')}\n\n"
        
        # 添加情绪分析
        report += "## 情绪分析\n"
        if 'summary' in dashboard_data and 'sentiment' in dashboard_data['summary']:
            sentiment = dashboard_data['summary']['sentiment']
            
            report += f"- 整体情绪: {sentiment.get('overall_sentiment', '中性')}\n"
            report += f"- 情绪得分: {sentiment.get('overall_average_score', 0)}\n"
            report += f"- 市场影响: {sentiment.get('market_implication', '中性')}\n\n"
        
        # 添加投资建议
        report += "## 投资建议\n"
        report += self._generate_investment_advice(dashboard_data)
        
        # 添加风险提示
        report += "## 风险提示\n"
        report += "- 本报告仅供参考，不构成任何投资建议\n"
        report += "- 股市有风险，投资需谨慎\n"
        report += "- 过往业绩不代表未来表现\n"
        report += "- 请根据自身风险承受能力做出投资决策\n\n"
        
        return report
    
    def _generate_investment_advice(self, dashboard_data: Dict[str, Any]) -> str:
        """生成投资建议"""
        advice = ""
        
        # 综合各方面分析结果
        technical_signal = '中性'
        fundamental_score = 0
        sentiment = '中性'
        
        if 'summary' in dashboard_data:
            if 'technical' in dashboard_data['summary']:
                technical_signal = dashboard_data['summary']['technical'].get('overall_signal', '中性')
            
            if 'fundamental' in dashboard_data['summary']:
                fundamental_score = dashboard_data['summary']['fundamental'].get('overall_score', 0)
            
            if 'sentiment' in dashboard_data['summary']:
                sentiment = dashboard_data['summary']['sentiment'].get('overall_sentiment', '中性')
        
        # 生成投资建议
        if technical_signal == '看多' and fundamental_score >= 6 and sentiment in ['积极', '强烈积极']:
            advice += "### 强烈推荐\n"
            advice += "- 技术面、基本面和情绪面均表现良好\n"
            advice += "- 建议积极配置，可考虑分批买入\n"
            advice += "- 中长期持有策略\n\n"
        elif (technical_signal == '看多' or technical_signal == '中性') and fundamental_score >= 5:
            advice += "### 推荐\n"
            advice += "- 综合表现良好，具有一定投资价值\n"
            advice += "- 建议适度配置，可在回调时买入\n"
            advice += "- 中短期持有策略\n\n"
        elif technical_signal == '看空' or fundamental_score <= 4 or sentiment in ['消极', '强烈消极']:
            advice += "### 谨慎\n"
            advice += "- 存在一定风险因素\n"
            advice += "- 建议减少配置，避免重仓\n"
            advice += "- 短期观望为宜\n\n"
        else:
            advice += "### 中性\n"
            advice += "- 各方面表现均衡\n"
            advice += "- 建议保持现有仓位\n"
            advice += "- 关注市场变化，择机操作\n\n"
        
        return advice
    
    def generate_strategy_report(self, strategy_results: Dict[str, Dict[str, Any]], 
                               output_dir: str = './reports') -> str:
        """生成策略回测报告"""
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 创建仪表盘
        dashboard_data = self.dashboard.create_strategy_dashboard(
            strategy_results, title='策略回测报告'
        )
        
        # 保存仪表盘图表
        report_dir = os.path.join(output_dir, 'strategy_backtest')
        self.dashboard.save_dashboard(dashboard_data, report_dir)
        
        # 生成报告文本
        report_content = self._generate_strategy_report_content(strategy_results, dashboard_data)
        
        # 保存报告文本
        report_file = os.path.join(report_dir, 'strategy_report.md')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"策略回测报告已生成到 {report_file}")
        
        return report_file
    
    def _generate_strategy_report_content(self, strategy_results: Dict[str, Dict[str, Any]], 
                                        dashboard_data: Dict[str, Any]) -> str:
        """生成策略回测报告内容"""
        report = "# 策略回测报告\n\n"
        
        # 添加报告头部
        report += "## 报告信息\n"
        report += f"- 报告生成日期: {pd.Timestamp.now().strftime('%Y-%m-%d')}\n"
        report += f"- 策略数量: {len(strategy_results)}\n\n"
        
        # 添加绩效概览
        report += "## 绩效概览\n"
        if 'charts' in dashboard_data and 'performance' in dashboard_data['charts']:
            report += "![绩效对比](performance.png)\n\n"
        
        # 添加最佳策略
        if 'best_strategy' in dashboard_data:
            report += f"### 最佳策略\n"
            report += f"- 策略名称: {dashboard_data['best_strategy']}\n"
            report += f"- 最高收益率: {dashboard_data['best_return']}%\n\n"
        
        # 添加详细绩效
        report += "## 详细绩效\n"
        for strategy_name, performance in strategy_results.items():
            report += f"### {strategy_name}\n"
            report += f"- 总收益率: {performance.get('total_return', 0)}%\n"
            report += f"- 年化收益率: {performance.get('annual_return', 0)}%\n"
            report += f"- 夏普比率: {performance.get('sharpe_ratio', 0)}\n"
            report += f"- 最大回撤: {performance.get('max_drawdown', 0)}%\n"
            report += f"- 胜率: {performance.get('win_rate', 0)}%\n"
            report += f"- 交易次数: {performance.get('number_of_trades', 0)}\n"
            report += f"- 回测周期: {performance.get('trading_days', 0)} 天\n\n"
        
        # 添加策略评估
        report += "## 策略评估\n"
        report += self._evaluate_strategies(strategy_results)
        
        # 添加风险提示
        report += "## 风险提示\n"
        report += "- 本报告基于历史数据回测，不代表未来表现\n"
        report += "- 市场环境变化可能导致策略绩效下降\n"
        report += "- 请结合实际市场情况调整策略参数\n\n"
        
        return report
    
    def _evaluate_strategies(self, strategy_results: Dict[str, Dict[str, Any]]) -> str:
        """评估策略"""
        evaluation = ""
        
        # 分析各策略表现
        for strategy_name, performance in strategy_results.items():
            total_return = performance.get('total_return', 0)
            sharpe_ratio = performance.get('sharpe_ratio', 0)
            max_drawdown = performance.get('max_drawdown', 0)
            
            evaluation += f"### {strategy_name} 评估\n"
            
            if total_return > 50:
                evaluation += "- 收益率表现优秀\n"
            elif total_return > 20:
                evaluation += "- 收益率表现良好\n"
            elif total_return > 0:
                evaluation += "- 收益率表现一般\n"
            else:
                evaluation += "- 收益率表现不佳\n"
            
            if sharpe_ratio > 1.5:
                evaluation += "- 风险调整后收益优秀\n"
            elif sharpe_ratio > 0.5:
                evaluation += "- 风险调整后收益良好\n"
            else:
                evaluation += "- 风险调整后收益一般\n"
            
            if max_drawdown < 20:
                evaluation += "- 风险控制良好\n"
            else:
                evaluation += "- 风险控制需要加强\n"
            
            evaluation += "\n"
        
        return evaluation
    
    def generate_report(self, symbol: str, report_type: str = 'comprehensive') -> str:
        """生成股票分析报告（API调用接口）"""
        # 这里应该从数据收集器获取股票数据，然后生成报告
        # 为了简化，我们返回一个示例结果
        
        # 生成报告内容
        report = f"# {symbol} 分析报告\n\n"
        
        # 添加报告头部
        report += "## 报告信息\n"
        report += f"- 股票代码: {symbol}\n"
        report += f"- 报告类型: {report_type}\n"
        report += f"- 报告生成日期: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # 根据报告类型添加不同内容
        if report_type == 'technical':
            report += "## 技术分析\n"
            report += "### 趋势分析\n"
            report += "- 短期趋势: 看多\n"
            report += "- 中期趋势: 中性\n"
            report += "- 长期趋势: 看多\n\n"
            
            report += "### 技术指标\n"
            report += "- MACD: 金叉，看多\n"
            report += "- RSI: 65，中性\n"
            report += "- KDJ: 70，看多\n"
            report += "- 布林带: 价格接近上轨\n\n"
            
            report += "### 综合信号\n"
            report += "- 整体信号: 看多\n"
        elif report_type == 'fundamental':
            report += "## 基本面分析\n"
            report += "### 财务指标\n"
            report += "- PE: 15.5\n"
            report += "- PB: 2.3\n"
            report += "- ROE: 12.5%\n"
            report += "- EPS: 2.1\n\n"
            
            report += "### 成长能力\n"
            report += "- 营收增长: 15.2%\n"
            report += "- 利润增长: 18.5%\n\n"
            
            report += "### 综合评估\n"
            report += "- 综合得分: 8.5\n"
            report += "- 投资建议: 推荐\n"
        else:  # comprehensive
            report += "## 综合分析\n"
            report += "### 技术分析\n"
            report += "- 整体信号: 看多\n\n"
            
            report += "### 基本面分析\n"
            report += "- 综合得分: 8.5\n"
            report += "- 投资建议: 推荐\n\n"
            
            report += "### 情绪分析\n"
            report += "- 整体情绪: 积极\n"
            report += "- 情绪得分: 0.6\n\n"
            
            report += "### 综合评估\n"
            report += "- 投资建议: 推荐\n"
            report += "- 风险等级: 中等\n"
        
        # 添加风险提示
        report += "## 风险提示\n"
        report += "- 本报告仅供参考，不构成任何投资建议\n"
        report += "- 股市有风险，投资需谨慎\n"
        report += "- 过往业绩不代表未来表现\n"
        report += "- 请根据自身风险承受能力做出投资决策\n"
        
        return report
