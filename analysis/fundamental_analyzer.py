import pandas as pd
import numpy as np
from typing import Dict, List, Any

class FundamentalAnalyzer:
    """基本面分析类"""
    
    def analyze_profitability(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析盈利能力"""
        if not financial_data:
            return {}
        
        profitability_analysis = {
            'roe': financial_data.get('roe', 0),  # 净资产收益率
            'roa': financial_data.get('roa', 0),  # 总资产收益率
            'profit_margin': financial_data.get('profit_margin', 0),  # 毛利率
            'roe_grade': self._grade_metric(financial_data.get('roe', 0), 15, 10, 5),
            'roa_grade': self._grade_metric(financial_data.get('roa', 0), 8, 5, 3),
            'profit_margin_grade': self._grade_metric(financial_data.get('profit_margin', 0), 30, 20, 10)
        }
        
        return profitability_analysis
    
    def analyze_growth(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析成长能力"""
        if not financial_data:
            return {}
        
        growth_analysis = {
            'revenue_growth': financial_data.get('revenue_growth', 0),  # 营收同比增长
            'profit_growth': financial_data.get('profit_growth', 0),  # 净利润同比增长
            'revenue_growth_grade': self._grade_metric(financial_data.get('revenue_growth', 0), 30, 15, 5),
            'profit_growth_grade': self._grade_metric(financial_data.get('profit_growth', 0), 30, 15, 5)
        }
        
        return growth_analysis
    
    def analyze_solvency(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析偿债能力"""
        if not financial_data:
            return {}
        
        solvency_analysis = {
            'current_ratio': financial_data.get('current_ratio', 0),  # 流动比率
            'quick_ratio': financial_data.get('quick_ratio', 0),  # 速动比率
            'debt_to_asset': financial_data.get('debt_to_asset', 0),  # 资产负债率
            'current_ratio_grade': self._grade_metric(financial_data.get('current_ratio', 0), 2, 1.5, 1),
            'quick_ratio_grade': self._grade_metric(financial_data.get('quick_ratio', 0), 1.5, 1, 0.7),
            'debt_to_asset_grade': self._grade_metric(100 - financial_data.get('debt_to_asset', 0), 70, 60, 50)  # 反转指标，越高越好
        }
        
        return solvency_analysis
    
    def analyze_operation(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析运营能力"""
        if not financial_data:
            return {}
        
        operation_analysis = {
            'inventory_turnover': financial_data.get('inventory_turnover', 0),  # 存货周转率
            'asset_turnover': financial_data.get('asset_turnover', 0),  # 总资产周转率
            'inventory_turnover_grade': self._grade_metric(financial_data.get('inventory_turnover', 0), 8, 5, 3),
            'asset_turnover_grade': self._grade_metric(financial_data.get('asset_turnover', 0), 1, 0.7, 0.5)
        }
        
        return operation_analysis
    
    def analyze_valuation(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析估值水平"""
        if not financial_data:
            return {}
        
        valuation_analysis = {
            'pe': financial_data.get('pe', 0),  # 市盈率
            'pb': financial_data.get('pb', 0),  # 市净率
            'ps': financial_data.get('ps', 0),  # 市销率
            'pe_grade': self._grade_metric(30 / (financial_data.get('pe', 1)), 2, 1.5, 1) if financial_data.get('pe', 0) > 0 else '低',  # 反转指标
            'pb_grade': self._grade_metric(3 / (financial_data.get('pb', 1)), 2, 1.5, 1) if financial_data.get('pb', 0) > 0 else '低',  # 反转指标
            'ps_grade': self._grade_metric(5 / (financial_data.get('ps', 1)), 2, 1.5, 1) if financial_data.get('ps', 0) > 0 else '低'  # 反转指标
        }
        
        return valuation_analysis
    
    def _grade_metric(self, value: float, high_threshold: float, medium_threshold: float, low_threshold: float) -> str:
        """对指标进行评级"""
        if value >= high_threshold:
            return '高'
        elif value >= medium_threshold:
            return '中'
        elif value >= low_threshold:
            return '低'
        else:
            return '极低'
    
    def comprehensive_fundamental_analysis(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """综合基本面分析"""
        if not financial_data:
            return {}
        
        analysis = {
            'profitability': self.analyze_profitability(financial_data),
            'growth': self.analyze_growth(financial_data),
            'solvency': self.analyze_solvency(financial_data),
            'operation': self.analyze_operation(financial_data),
            'valuation': self.analyze_valuation(financial_data),
            'overall_score': self._calculate_overall_score(financial_data),
            'investment_advisory': self._generate_investment_advisory(financial_data)
        }
        
        return analysis
    
    def _calculate_overall_score(self, financial_data: Dict[str, Any]) -> float:
        """计算综合得分"""
        if not financial_data:
            return 0
        
        # 各项指标权重
        weights = {
            'roe': 0.2,  # 净资产收益率权重
            'revenue_growth': 0.15,  # 营收增长权重
            'profit_growth': 0.15,  # 利润增长权重
            'current_ratio': 0.1,  # 流动比率权重
            'debt_to_asset': 0.1,  # 资产负债率权重（反转）
            'inventory_turnover': 0.1,  # 存货周转率权重
            'asset_turnover': 0.1,  # 总资产周转率权重
            'pe': 0.1  # 市盈率权重（反转）
        }
        
        # 计算加权得分
        score = 0
        
        # 盈利能力
        roe = financial_data.get('roe', 0)
        score += roe * weights['roe']
        
        # 成长能力
        revenue_growth = financial_data.get('revenue_growth', 0)
        profit_growth = financial_data.get('profit_growth', 0)
        score += revenue_growth * weights['revenue_growth']
        score += profit_growth * weights['profit_growth']
        
        # 偿债能力
        current_ratio = financial_data.get('current_ratio', 0)
        debt_to_asset = financial_data.get('debt_to_asset', 0)
        score += current_ratio * weights['current_ratio']
        score += (100 - debt_to_asset) * weights['debt_to_asset'] / 100  # 反转并归一化
        
        # 运营能力
        inventory_turnover = financial_data.get('inventory_turnover', 0)
        asset_turnover = financial_data.get('asset_turnover', 0)
        score += inventory_turnover * weights['inventory_turnover'] / 10  # 归一化
        score += asset_turnover * weights['asset_turnover'] * 10  # 放大
        
        # 估值水平
        pe = financial_data.get('pe', 1)
        if pe > 0:
            score += (30 / pe) * weights['pe']  # 反转并归一化
        
        return round(score, 2)
    
    def _generate_investment_advisory(self, financial_data: Dict[str, Any]) -> str:
        """生成投资建议"""
        if not financial_data:
            return '无法生成投资建议，缺少财务数据'
        
        score = self._calculate_overall_score(financial_data)
        
        if score >= 8:
            return '强烈推荐：公司基本面优秀，盈利能力强，成长潜力大，估值合理'
        elif score >= 6:
            return '推荐：公司基本面良好，具有一定投资价值'
        elif score >= 4:
            return '谨慎推荐：公司基本面一般，存在一定风险'
        else:
            return '不推荐：公司基本面较差，投资风险较高'
    
    def compare_with_industry(self, company_data: Dict[str, Any], industry_averages: Dict[str, Any]) -> Dict[str, Any]:
        """与行业平均水平比较"""
        if not company_data or not industry_averages:
            return {}
        
        comparison = {}
        
        # 比较各项指标
        metrics = ['roe', 'revenue_growth', 'profit_growth', 'current_ratio', 'debt_to_asset', 'pe', 'pb']
        
        for metric in metrics:
            company_value = company_data.get(metric, 0)
            industry_value = industry_averages.get(metric, 0)
            
            if industry_value > 0:
                ratio = company_value / industry_value
                comparison[f'{metric}_comparison'] = {
                    'company_value': company_value,
                    'industry_average': industry_value,
                    'ratio': round(ratio, 2),
                    'evaluation': self._evaluate_comparison(ratio, metric)
                }
        
        return comparison
    
    def _evaluate_comparison(self, ratio: float, metric: str) -> str:
        """评估与行业平均水平的比较结果"""
        # 对于大多数指标，高于行业平均更好
        if metric in ['debt_to_asset', 'pe', 'pb']:
            # 这些指标越低越好
            if ratio < 0.8:
                return '优于行业'
            elif ratio < 1.2:
                return '接近行业'
            else:
                return '劣于行业'
        else:
            # 这些指标越高越好
            if ratio > 1.2:
                return '优于行业'
            elif ratio > 0.8:
                return '接近行业'
            else:
                return '劣于行业'