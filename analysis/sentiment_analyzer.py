import pandas as pd
import numpy as np
from typing import Dict, List, Any
import re
import os

# 设置 Hugging Face 镜像站，加速模型下载
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

class SentimentAnalyzer:
    """情绪分析类"""
    
    def __init__(self, use_advanced_model: bool = True, model_name: str = None):
        """初始化情绪分析器"""
        # 简单的情感词典（作为备选）
        self.positive_words = {
            '上涨', '涨停', '牛市', '利好', '增长', '盈利', '创新高', '突破', '强劲',
            '看好', '买入', '持有', '增持', '推荐', '支撑', '反弹', '反转', '高增长',
            '超预期', '优质', '龙头', '领先', '稳健', '景气', '复苏', '扩张', '改善'
        }
        
        self.negative_words = {
            '下跌', '跌停', '熊市', '利空', '下降', '亏损', '创新低', '跌破', '疲软',
            '看空', '卖出', '减持', '风险', '压力', '回调', '调整', '低增长', '不及预期',
            '劣质', '落后', '波动', '衰退', '收缩', '恶化', '高估', '泡沫', '崩盘'
        }
        
        # 初始化先进的NLP模型
        self.use_advanced_model = use_advanced_model
        self.sentiment_pipeline = None
        self.model_available = False
        
        if self.use_advanced_model:
            try:
                # 支持的中文情感分析模型列表
                supported_models = [
                    "uer/roberta-base-finetuned-jd-full-chinese",  # 京东评论情感分析模型
                    "hfl/chinese-roberta-wwm-ext",                 # 中文预训练模型，可用于情感分析
                    "bert-base-chinese"                              # 基础中文BERT模型
                ]
                
                # 选择模型 - 使用京东评论情感分析模型作为默认
                target_model = model_name if model_name in supported_models else supported_models[0]
                
                print(f"尝试加载模型: {target_model}")
                
                # 使用中文情感分析预训练模型，添加更完善的配置
                self.sentiment_pipeline = pipeline(
                    "sentiment-analysis",
                    model=target_model,
                    tokenizer=target_model,
                    device=-1,  # 使用CPU
                    model_kwargs={
                        "low_cpu_mem_usage": True  # 低CPU内存使用
                        # 移除use_safetensors参数，因为模型不支持safetensors格式
                    }
                )
                self.model_available = True
                print(f"模型 {target_model} 加载成功")
            except Exception as e:
                print(f"初始化NLP模型失败，将使用情感词典方法: {e}")
                self.use_advanced_model = False
                self.model_available = False
    
    def analyze_text_sentiment(self, text: str) -> Dict[str, Any]:
        """分析单条文本的情绪"""
        if not text:
            return {'sentiment': '中性', 'score': 0, 'positive_count': 0, 'negative_count': 0}
        
        # 文本预处理
        processed_text = self._preprocess_text(text)
        
        # 如果使用先进模型且模型可用，优先使用transformer模型
        if self.use_advanced_model and self.model_available and self.sentiment_pipeline:
            try:
                # 使用transformer模型分析情绪
                result = self.sentiment_pipeline(processed_text, truncation=True, max_length=512)[0]
                
                # 映射模型输出到我们的情绪分类
                model_label = result['label']
                model_score = result['score']
                
                # 转换为系统的情绪分类
                # 处理星级评分（如"star 5"、"star 4"等）
                if 'star' in model_label:
                    # 提取星级数字
                    star_rating = int(model_label.split(' ')[1])
                    
                    # 根据星级评分计算情感得分
                    if star_rating == 5:
                        sentiment = '强烈积极'
                        score = 5  # 最高积极得分
                    elif star_rating == 4:
                        sentiment = '积极'
                        score = 3  # 中等积极得分
                    elif star_rating == 3:
                        sentiment = '中性'
                        score = 0  # 中性得分
                    elif star_rating == 2:
                        sentiment = '消极'
                        score = -3  # 中等消极得分
                    elif star_rating == 1:
                        sentiment = '强烈消极'
                        score = -5  # 最高消极得分
                    else:
                        sentiment = '中性'
                        score = 0
                # 处理传统的positive/negative标签
                elif model_label == 'positive':
                    sentiment = '积极'
                    score = model_score * 5
                elif model_label == 'negative':
                    sentiment = '消极'
                    score = -model_score * 5
                else:
                    sentiment = '中性'
                    score = 0
                
                # 返回结果，保持与原有方法相同的格式
                return {
                    'sentiment': sentiment,
                    'score': score,
                    'positive_count': int(score > 0),
                    'negative_count': int(score < 0),
                    'model_label': model_label,
                    'model_score': model_score,
                    'model_used': True
                }
            except Exception as e:
                print(f"使用NLP模型分析情绪失败，回退到情感词典方法: {e}")
        
        # 回退到原有方法：统计情感词
        positive_count = 0
        negative_count = 0
        
        for word in self.positive_words:
            positive_count += processed_text.count(word)
        
        for word in self.negative_words:
            negative_count += processed_text.count(word)
        
        # 计算情绪得分
        score = positive_count - negative_count
        
        # 确定情绪倾向
        if score > 0:
            sentiment = '积极'
        elif score < 0:
            sentiment = '消极'
        else:
            sentiment = '中性'
        
        return {
            'sentiment': sentiment,
            'score': score,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'model_used': False
        }
    
    def analyze_multiple_texts(self, texts: List[str]) -> Dict[str, Any]:
        """分析多条文本的情绪"""
        if not texts:
            return {'average_score': 0, 'sentiment_distribution': {'积极': 0, '中性': 0, '消极': 0}}
        
        sentiments = []
        scores = []
        
        for text in texts:
            result = self.analyze_text_sentiment(text)
            sentiments.append(result['sentiment'])
            scores.append(result['score'])
        
        # 计算统计信息
        average_score = np.mean(scores) if scores else 0
        sentiment_distribution = {
            '积极': sentiments.count('积极'),
            '中性': sentiments.count('中性'),
            '消极': sentiments.count('消极')
        }
        
        # 计算情绪比例
        total = len(sentiments)
        sentiment_ratio = {
            '积极': round(sentiment_distribution['积极'] / total * 100, 2),
            '中性': round(sentiment_distribution['中性'] / total * 100, 2),
            '消极': round(sentiment_distribution['消极'] / total * 100, 2)
        }
        
        return {
            'average_score': round(average_score, 2),
            'sentiment_distribution': sentiment_distribution,
            'sentiment_ratio': sentiment_ratio,
            'overall_sentiment': self._determine_overall_sentiment(average_score)
        }
    
    def _preprocess_text(self, text: str) -> str:
        """文本预处理"""
        # 转换为小写
        text = text.lower()
        
        # 去除特殊字符
        text = re.sub(r'[^一-龥a-zA-Z0-9\s]', ' ', text)
        
        # 去除多余空格
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def _determine_overall_sentiment(self, average_score: float) -> str:
        """根据平均得分确定整体情绪"""
        if average_score > 0.5:
            return '强烈积极'
        elif average_score > 0:
            return '积极'
        elif average_score > -0.5:
            return '中性'
        elif average_score > -1:
            return '消极'
        else:
            return '强烈消极'
    
    def analyze_news_sentiment(self, news_list: List[Dict[str, str]]) -> Dict[str, Any]:
        """分析新闻情绪"""
        if not news_list:
            return {}
        
        # 提取新闻标题和内容
        texts = []
        for news in news_list:
            title = news.get('title', '')
            content = news.get('content', '')
            texts.append(title + ' ' + content)
        
        # 分析情绪
        result = self.analyze_multiple_texts(texts)
        
        # 添加新闻相关信息
        result['news_count'] = len(news_list)
        
        return result
    
    def analyze_social_media_sentiment(self, posts: List[Dict[str, str]]) -> Dict[str, Any]:
        """分析社交媒体情绪"""
        if not posts:
            return {}
        
        # 提取帖子内容
        texts = []
        for post in posts:
            content = post.get('content', '')
            texts.append(content)
        
        # 分析情绪
        result = self.analyze_multiple_texts(texts)
        
        # 添加社交媒体相关信息
        result['post_count'] = len(posts)
        
        return result
    
    def comprehensive_sentiment_analysis(self, data_sources: Dict[str, List[Any]]) -> Dict[str, Any]:
        """综合情绪分析"""
        if not data_sources:
            return {}
        
        analysis_results = {}
        overall_scores = []
        
        # 分析各个数据源的情绪
        for source_name, data in data_sources.items():
            if source_name == 'news':
                result = self.analyze_news_sentiment(data)
            elif source_name == 'social_media':
                result = self.analyze_social_media_sentiment(data)
            else:
                # 通用文本分析
                texts = [item.get('content', '') for item in data]
                result = self.analyze_multiple_texts(texts)
            
            analysis_results[source_name] = result
            if 'average_score' in result:
                overall_scores.append(result['average_score'])
        
        # 计算综合情绪
        if overall_scores:
            average_overall_score = np.mean(overall_scores)
            overall_sentiment = self._determine_overall_sentiment(average_overall_score)
        else:
            average_overall_score = 0
            overall_sentiment = '中性'
        
        return {
            'source_analysis': analysis_results,
            'overall_average_score': round(average_overall_score, 2),
            'overall_sentiment': overall_sentiment,
            'market_implication': self._generate_market_implication(overall_sentiment)
        }
    
    def _generate_market_implication(self, sentiment: str) -> str:
        """根据情绪生成市场影响分析"""
        implications = {
            '强烈积极': '市场情绪非常乐观，可能推动股价上涨，建议关注多头机会',
            '积极': '市场情绪乐观，股价可能上涨，可考虑适当建仓',
            '中性': '市场情绪平稳，股价可能震荡整理，建议观望',
            '消极': '市场情绪悲观，股价可能下跌，建议谨慎操作',
            '强烈消极': '市场情绪非常悲观，可能导致股价大幅下跌，建议减仓或空仓'
        }
        
        return implications.get(sentiment, '市场情绪不明确，建议谨慎观望')