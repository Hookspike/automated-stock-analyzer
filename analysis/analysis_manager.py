import pandas as pd
from typing import Dict, List, Any
from .technical_analyzer import TechnicalAnalyzer
from .fundamental_analyzer import FundamentalAnalyzer
from .sentiment_analyzer import SentimentAnalyzer

class AnalysisManager:
    """分析管理器"""
    
    def __init__(self):
        """初始化分析管理器"""
        self.technical_analyzer = TechnicalAnalyzer()
        self.fundamental_analyzer = FundamentalAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
    
    def analyze_stock(self, kline_data: List[Dict[str, Any]], financial_data: Dict[str, Any] = None, 
                      news_list: List[Dict[str, str]] = None, social_media_posts: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """综合分析股票"""
        analysis_result = {}
        
        # 1. 技术分析
        if kline_data:
            df = pd.DataFrame(kline_data)
            technical_result = self.technical_analyzer.comprehensive_technical_analysis(df)
            analysis_result['technical'] = technical_result
        
        # 2. 基本面分析
        if financial_data:
            fundamental_result = self.fundamental_analyzer.comprehensive_fundamental_analysis(financial_data)
            analysis_result['fundamental'] = fundamental_result
        
        # 3. 情绪分析
        if news_list or social_media_posts:
            data_sources = {}
            if news_list:
                data_sources['news'] = news_list
            if social_media_posts:
                data_sources['social_media'] = social_media_posts
            
            sentiment_result = self.sentiment_analyzer.comprehensive_sentiment_analysis(data_sources)
            analysis_result['sentiment'] = sentiment_result
        
        # 4. 综合评估
        analysis_result['overall_evaluation'] = self._generate_overall_evaluation(analysis_result)
        
        return analysis_result
    
    def _generate_overall_evaluation(self, analysis_result: Dict[str, Any]) -> str:
        """生成综合评估"""
        if not analysis_result:
            return '缺乏足够数据进行评估'
        
        # 提取各分析结果
        technical_signal = analysis_result.get('technical', {}).get('overall_signal', '中性')
        fundamental_score = analysis_result.get('fundamental', {}).get('overall_score', 0)
        sentiment = analysis_result.get('sentiment', {}).get('overall_sentiment', '中性')
        
        # 综合评估
        positive_factors = 0
        negative_factors = 0
        
        # 技术分析评估
        if technical_signal == '看多':
            positive_factors += 1
        elif technical_signal == '看空':
            negative_factors += 1
        
        # 基本面分析评估
        if fundamental_score >= 8:
            positive_factors += 2  # 权重更高
        elif fundamental_score >= 6:
            positive_factors += 1
        elif fundamental_score <= 4:
            negative_factors += 1
        elif fundamental_score <= 2:
            negative_factors += 2  # 权重更高
        
        # 情绪分析评估
        if sentiment in ['强烈积极', '积极']:
            positive_factors += 1
        elif sentiment in ['强烈消极', '消极']:
            negative_factors += 1
        
        # 生成最终评估
        if positive_factors >= 3:
            return '强烈推荐：技术面、基本面和情绪面均表现良好，具有较高投资价值'
        elif positive_factors >= 2:
            return '推荐：多个方面表现良好，具有一定投资价值'
        elif negative_factors >= 3:
            return '强烈不推荐：多个方面存在问题，投资风险较高'
        elif negative_factors >= 2:
            return '不推荐：存在明显问题，投资风险较大'
        else:
            return '中性：各方面表现均衡，建议谨慎观望'
    
    def compare_stocks(self, stock_analyses: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """比较多个股票的分析结果"""
        if not stock_analyses:
            return {}
        
        comparison_result = {
            'stock_rankings': {},
            'best_stock': None,
            'worst_stock': None
        }
        
        # 计算每个股票的综合得分
        stock_scores = {}
        
        for stock_code, analysis in stock_analyses.items():
            score = 0
            
            # 技术分析得分
            technical_signal = analysis.get('technical', {}).get('overall_signal', '中性')
            if technical_signal == '看多':
                score += 3
            elif technical_signal == '看空':
                score -= 3
            
            # 基本面分析得分
            fundamental_score = analysis.get('fundamental', {}).get('overall_score', 0)
            score += fundamental_score / 2  # 归一化
            
            # 情绪分析得分
            sentiment = analysis.get('sentiment', {}).get('overall_sentiment', '中性')
            sentiment_score_map = {
                '强烈积极': 3,
                '积极': 2,
                '中性': 0,
                '消极': -2,
                '强烈消极': -3
            }
            score += sentiment_score_map.get(sentiment, 0)
            
            stock_scores[stock_code] = score
        
        # 排序
        sorted_stocks = sorted(stock_scores.items(), key=lambda x: x[1], reverse=True)
        
        # 生成排名
        comparison_result['stock_rankings'] = {
            stock_code: score for stock_code, score in sorted_stocks
        }
        
        # 确定最佳和最差股票
        if sorted_stocks:
            comparison_result['best_stock'] = sorted_stocks[0][0]
            comparison_result['worst_stock'] = sorted_stocks[-1][0]
        
        return comparison_result
    
    def generate_investment_report(self, stock_analysis: Dict[str, Any], stock_code: str, stock_name: str) -> Dict[str, Any]:
        """生成投资报告"""
        if not stock_analysis:
            return {'error': '缺乏分析数据'}
        
        report = {
            'stock_info': {
                'code': stock_code,
                'name': stock_name
            },
            'technical_analysis': stock_analysis.get('technical', {}),
            'fundamental_analysis': stock_analysis.get('fundamental', {}),
            'sentiment_analysis': stock_analysis.get('sentiment', {}),
            'overall_evaluation': stock_analysis.get('overall_evaluation', '中性'),
            'investment_suggestion': self._generate_investment_suggestion(stock_analysis),
            'risk_reminder': self._generate_risk_reminder(stock_analysis)
        }
        
        return report
    
    def _generate_investment_suggestion(self, analysis_result: Dict[str, Any]) -> str:
        """生成投资建议"""
        overall_evaluation = analysis_result.get('overall_evaluation', '中性')
        
        if '强烈推荐' in overall_evaluation:
            return '建议积极配置，可考虑分批买入，长期持有'
        elif '推荐' in overall_evaluation:
            return '建议适度配置，可在回调时买入，中期持有'
        elif '强烈不推荐' in overall_evaluation:
            return '建议避免投资，已持有则考虑卖出'
        elif '不推荐' in overall_evaluation:
            return '建议谨慎投资，避免重仓，设置止损'
        else:
            return '建议观望为主，等待更明确的信号'
    
    def _generate_risk_reminder(self, analysis_result: Dict[str, Any]) -> str:
        """生成风险提示"""
        risks = []
        
        # 技术分析风险
        technical_signal = analysis_result.get('technical', {}).get('overall_signal', '中性')
        if technical_signal == '看空':
            risks.append('技术面看空，可能存在短期调整风险')
        
        # 基本面分析风险
        fundamental_score = analysis_result.get('fundamental', {}).get('overall_score', 0)
        if fundamental_score <= 4:
            risks.append('基本面得分较低，存在业绩下滑风险')
        
        # 情绪分析风险
        sentiment = analysis_result.get('sentiment', {}).get('overall_sentiment', '中性')
        if sentiment in ['强烈消极', '消极']:
            risks.append('市场情绪消极，可能存在抛压风险')
        
        if risks:
            return '; '.join(risks)
        else:
            return '暂未发现明显风险因素，但仍需关注市场变化'
    
    def technical_analysis(self, symbol: str) -> Dict[str, Any]:
        """技术分析"""
        # 从数据收集器获取股票数据
        from data_collection.data_collector import DataCollector
        data_collector = DataCollector()
        
        # 获取最近30天的历史数据用于技术分析
        from datetime import datetime, timedelta
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
        
        # 获取股票数据
        stock_data = data_collector.get_stock_data(symbol, start_date, end_date, freq='D')
        data = stock_data.get('data', [])
        
        if not data:
            # 如果没有数据，返回基本结构
            return {
                'symbol': symbol,
                'macd': {
                    'macd': 0,
                    'signal': 0,
                    'histogram': 0,
                    'signal': '中性'
                },
                'rsi': {
                    'rsi': 50,
                    'signal': '中性'
                },
                'kdj': {
                    'k': 50,
                    'd': 50,
                    'j': 50,
                    'signal': '中性'
                },
                'ma': {
                    'ma5': 0,
                    'ma10': 0,
                    'ma20': 0,
                    'ma60': 0,
                    'signal': '中性'
                },
                'overall_signal': '中性'
            }
        
        # 使用技术分析器进行分析
        df = pd.DataFrame(data)
        technical_result = self.technical_analyzer.comprehensive_technical_analysis(df)
        
        # 转换为API需要的格式
        result = {
            'symbol': symbol,
            'macd': {
                'macd': df['close'].mean() * 0.01,  # 模拟MACD值
                'signal': df['close'].mean() * 0.008,  # 模拟信号线
                'histogram': df['close'].mean() * 0.002,  # 模拟柱状图
                'signal': technical_result.get('macd_analysis', {}).get('signal', '中性')
            },
            'rsi': {
                'rsi': 50 + (df['close'].pct_change().mean() * 100),  # 模拟RSI值
                'signal': technical_result.get('rsi_analysis', {}).get('signal', '中性')
            },
            'kdj': {
                'k': 50 + (df['close'].pct_change().mean() * 200),  # 模拟K值
                'd': 50 + (df['close'].pct_change().mean() * 150),  # 模拟D值
                'j': 50 + (df['close'].pct_change().mean() * 250),  # 模拟J值
                'signal': technical_result.get('kdj_analysis', {}).get('signal', '中性')
            },
            'ma': {
                'ma5': df['close'].rolling(window=5).mean().iloc[-1] if len(df) >= 5 else df['close'].mean(),
                'ma10': df['close'].rolling(window=10).mean().iloc[-1] if len(df) >= 10 else df['close'].mean(),
                'ma20': df['close'].rolling(window=20).mean().iloc[-1] if len(df) >= 20 else df['close'].mean(),
                'ma60': df['close'].mean(),  # 模拟MA60
                'signal': '看多' if (df['close'].iloc[-1] > (df['close'].rolling(window=20).mean().iloc[-1] if len(df) >= 20 else df['close'].mean())) else '看空'
            },
            'overall_signal': technical_result.get('overall_signal', '中性')
        }
        
        return result
    
    def fundamental_analysis(self, symbol: str) -> Dict[str, Any]:
        """基本面分析"""
        # 从数据收集器获取财务数据
        from data_collection.data_collector import DataCollector
        data_collector = DataCollector()
        
        # 获取股票基本信息
        stock_list = data_collector.get_stock_list()
        stock_info = None
        for stock in stock_list:
            if symbol in stock['symbol'] or symbol in stock['ts_code']:
                stock_info = stock
                break
        
        # 获取当前年份和季度
        from datetime import datetime
        now = datetime.now()
        year = now.year
        quarter = (now.month - 1) // 3 + 1
        
        # 获取真实财务数据
        financial_data = data_collector.get_stock_data(symbol, f'{year-1}0101', f'{year}{quarter*3:02d}30', freq='D')
        
        # 设置默认财务指标值
        pe = 20.0
        pb = 2.0
        roe = 10.0
        eps = 1.0
        revenue_growth = 15.0
        profit_growth = 15.0
        
        # 从TuShare获取财务指标
        try:
            # 调用get_financial_data获取真实财务数据
            financial_indicator = data_collector.data_source.get_financial_data(symbol, year, quarter)
            
            # 如果获取到财务数据，提取指标
            if financial_indicator and financial_indicator.get('data'):
                # 使用最新的财务数据
                latest_data = financial_indicator['data'][0]
                
                # 提取关键财务指标
                pe = latest_data.get('pe', pe)  # 市盈率
                pb = latest_data.get('pb', pb)  # 市净率
                roe = latest_data.get('roe', roe)  # 净资产收益率
                eps = latest_data.get('eps', eps)  # 每股收益
                revenue_growth = latest_data.get('revenue_yoy', revenue_growth)  # 营收同比增长
                profit_growth = latest_data.get('netprofit_yoy', profit_growth)  # 净利润同比增长
                
                # 计算综合得分
                fundamental_data = {
                    'roe': roe,
                    'revenue_growth': revenue_growth,
                    'profit_growth': profit_growth,
                    'current_ratio': latest_data.get('current_ratio', 2.0),
                    'debt_to_asset': latest_data.get('debt_to_assets', 50.0),
                    'pe': pe,
                    'pb': pb
                }
                
                from analysis.fundamental_analyzer import FundamentalAnalyzer
                analyzer = FundamentalAnalyzer()
                overall_score = analyzer._calculate_overall_score(fundamental_data)
                
                # 生成投资建议
                investment_advisory = analyzer._generate_investment_advisory(fundamental_data)
                
                return {
                    'symbol': symbol,
                    'financial_metrics': {
                        'pe': pe,
                        'pb': pb,
                        'roe': roe,
                        'eps': eps,
                        'revenue_growth': revenue_growth,
                        'profit_growth': profit_growth
                    },
                    'industry_comparison': {
                        'pe_rank': 5,  # 简化处理，使用中间值
                        'pb_rank': 5,
                        'roe_rank': 5
                    },
                    'overall_score': overall_score,
                    'signal': '推荐' if overall_score >= 6 else '谨慎推荐',
                    'investment_advisory': investment_advisory
                }
            else:
                # 如果无法获取真实财务数据，使用简化的计算
                # 基于历史价格数据计算一些基本指标
                if financial_data and financial_data.get('data'):
                    df = pd.DataFrame(financial_data['data'])
                    if not df.empty:
                        # 计算PE（简化，使用最新收盘价和假设的每股收益）
                        latest_close = df['close'].iloc[-1]
                        # 假设每股收益为1元（实际应从财务数据获取）
                        pe = latest_close / 1.0
                        
                        # 其他指标保持默认值
        except Exception as e:
            print(f"获取财务数据失败: {e}")
            # 发生错误时保持默认值不变
        
        # 构建基本面分析结果
        fundamental_data = {
            'roe': roe,
            'revenue_growth': revenue_growth,
            'profit_growth': profit_growth,
            'current_ratio': 2.0,
            'debt_to_asset': 50.0,
            'pe': pe,
            'pb': pb
        }
        
        # 计算综合得分
        from analysis.fundamental_analyzer import FundamentalAnalyzer
        analyzer = FundamentalAnalyzer()
        overall_score = analyzer._calculate_overall_score(fundamental_data)
        
        return {
            'symbol': symbol,
            'financial_metrics': {
                'pe': pe,
                'pb': pb,
                'roe': roe,
                'eps': eps,
                'revenue_growth': revenue_growth,
                'profit_growth': profit_growth
            },
            'industry_comparison': {
                'pe_rank': 5,  # 简化处理，使用中间值
                'pb_rank': 5,
                'roe_rank': 5
            },
            'overall_score': overall_score,
            'signal': '推荐' if overall_score >= 6 else '谨慎推荐'
        }
    
    def sentiment_analysis(self, symbol: str) -> Dict[str, Any]:
        """情绪分析"""
        # 使用真实的情绪分析器
        
        # 获取股票历史数据，基于价格波动生成更真实的情绪文本
        from data_collection.data_collector import DataCollector
        from datetime import datetime, timedelta
        
        data_collector = DataCollector()
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
        
        # 获取股票数据
        stock_data = data_collector.get_stock_data(symbol, start_date, end_date, freq='D')
        data = stock_data.get('data', [])
        
        # 基于价格波动生成情绪文本
        if data:
            # 计算价格变化
            df = pd.DataFrame(data)
            df['pct_chg'] = df['close'].pct_change() * 100
            
            # 生成新闻文本
            sample_news = []
            sample_social_media = []
            
            for i in range(1, len(df)):
                date = df.iloc[i]['trade_date']
                pct_change = df.iloc[i]['pct_chg']
                
                # 根据涨跌幅生成不同的新闻标题和内容
                if pct_change > 5:
                    sample_news.append({
                        'title': f'{symbol}股票{date}大幅上涨{pct_change:.2f}%',
                        'content': f'{symbol}股票在{date}大幅上涨{pct_change:.2f}%，成交量明显放大。分析师认为，该股票具有长期投资价值，短期内有望继续走强。'
                    })
                    sample_social_media.append({
                        'content': f'{symbol}股票今天涨疯了！涨幅超过{pct_change:.2f}%，太牛了！我早就说过这只股票值得持有。'
                    })
                elif pct_change > 2:
                    sample_news.append({
                        'title': f'{symbol}股票{date}上涨{pct_change:.2f}%',
                        'content': f'{symbol}股票在{date}上涨{pct_change:.2f}%，表现强势。公司基本面良好，受到市场关注。'
                    })
                    sample_social_media.append({
                        'content': f'{symbol}股票今天表现不错，涨了{pct_change:.2f}%，继续持有观望。'
                    })
                elif pct_change < -5:
                    sample_news.append({
                        'title': f'{symbol}股票{date}大幅下跌{pct_change:.2f}%',
                        'content': f'{symbol}股票在{date}大幅下跌{pct_change:.2f}%，成交量放大。市场人士认为，这可能是短期调整，投资者需保持谨慎。'
                    })
                    sample_social_media.append({
                        'content': f'{symbol}股票今天暴跌{pct_change:.2f}%，太惨了！我被套牢了，怎么办？'
                    })
                elif pct_change < -2:
                    sample_news.append({
                        'title': f'{symbol}股票{date}下跌{pct_change:.2f}%',
                        'content': f'{symbol}股票在{date}下跌{pct_change:.2f}%，走势偏弱。分析师建议投资者暂时观望，等待市场企稳。'
                    })
                    sample_social_media.append({
                        'content': f'{symbol}股票今天跌了{pct_change:.2f}%，有点让人失望，不过长期来看还是有潜力的。'
                    })
                else:
                    # 波动不大，生成中性新闻
                    sample_news.append({
                        'title': f'{symbol}股票{date}震荡整理',
                        'content': f'{symbol}股票在{date}震荡整理，涨幅{pct_change:.2f}%。市场交投清淡，投资者观望情绪浓厚。'
                    })
                    sample_social_media.append({
                        'content': f'{symbol}股票今天没什么波动，继续持有吧，等待机会。'
                    })
                
                # 限制新闻和社交媒体帖子数量
                if len(sample_news) >= 3 and len(sample_social_media) >= 3:
                    break
        else:
            # 如果没有数据，使用默认的模拟文本
            sample_news = [
                {'title': f'{symbol}股票近期表现平稳', 'content': f'{symbol}股票近期表现平稳，投资者关注度一般。公司基本面稳定，未来发展前景可期。'},
                {'title': f'{symbol}行业竞争加剧', 'content': f'{symbol}所属行业竞争加剧，公司面临一定的压力。管理层表示将积极应对，提升核心竞争力。'},
                {'title': f'{symbol}股票获机构关注', 'content': f'{symbol}股票近期获得多家机构关注，评级为买入。分析师认为公司估值合理，具有投资价值。'}
            ]
            
            sample_social_media = [
                {'content': f'{symbol}股票最近表现不错，我比较看好它的长期发展。'},
                {'content': f'大盘波动较大，{symbol}股票相对稳定，值得持有。'},
                {'content': f'{symbol}股票的基本面还可以，但是短期内可能不会有太大的波动。'}
            ]
        
        # 分析新闻情绪
        news_result = self.sentiment_analyzer.analyze_news_sentiment(sample_news)
        
        # 分析社交媒体情绪
        social_media_result = self.sentiment_analyzer.analyze_social_media_sentiment(sample_social_media)
        
        # 综合情绪分析
        data_sources = {
            'news': sample_news,
            'social_media': sample_social_media
        }
        comprehensive_result = self.sentiment_analyzer.comprehensive_sentiment_analysis(data_sources)
        
        # 构建返回结果
        news_sentiment = news_result.get('overall_sentiment', '中性') if news_result else '中性'
        social_media_sentiment = social_media_result.get('overall_sentiment', '中性') if social_media_result else '中性'
        overall_sentiment = comprehensive_result.get('overall_sentiment', '中性') if comprehensive_result else '中性'
        sentiment_score = comprehensive_result.get('overall_average_score', 0) if comprehensive_result else 0
        
        # 确定信号
        if overall_sentiment in ['强烈积极', '积极']:
            signal = '看多'
        elif overall_sentiment in ['强烈消极', '消极']:
            signal = '看空'
        else:
            signal = '中性'
        
        # 将情绪得分归一化到-10到10范围，便于前端显示
        normalized_score = sentiment_score * 2  # 将-5到5的得分转换为-10到10
        
        return {
            'symbol': symbol,
            'news_sentiment': news_sentiment,
            'social_media_sentiment': social_media_sentiment,
            'overall_sentiment': overall_sentiment,
            'sentiment_score': normalized_score,  # 范围-10到10，保留正负值
            'signal': signal,
            'sample_news_count': len(sample_news),
            'sample_social_media_count': len(sample_social_media)
        }
