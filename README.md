# 股票预测分析系统

## 项目介绍

股票预测分析系统是一个基于Python的综合股票分析和预测平台，集成了数据收集、处理、分析、预测、回测和可视化等功能，旨在为投资者提供全面的股票市场洞察和决策支持。

## 系统架构

系统采用模块化设计，主要包含以下模块：

1. **数据收集模块**：负责从TuShare获取股票数据并存储到SQLite数据库
2. **数据处理模块**：负责数据清洗、特征工程和数据标准化
3. **分析模块**：负责技术分析、基本面分析和情绪分析
4. **预测模块**：负责使用传统机器学习和深度学习模型进行股价预测
5. **回测模块**：负责测试交易策略的历史表现
6. **可视化模块**：负责生成图表、仪表盘和报告
7. **应用层**：提供Web界面、API服务和预警系统

## 技术栈

- **编程语言**：Python
- **数据处理**：pandas, numpy
- **机器学习**：scikit-learn, PyTorch, xgboost, lightgbm
- **可视化**：matplotlib
- **Web框架**：FastAPI
- **数据库**：SQLite

## 项目结构

```
stock_analysis/
├── analysis/              # 分析模块
│   ├── analysis_manager.py
│   ├── fundamental_analyzer.py
│   ├── sentiment_analyzer.py
│   └── technical_analyzer.py
├── application/           # 应用层
│   ├── alert/             # 预警系统
│   │   └── alert_system.py
│   ├── api/               # API服务
│   │   └── routes.py
│   └── app.py             # FastAPI应用主文件
├── backtest/              # 回测模块
│   ├── backtest_manager.py
│   ├── base_strategy.py
│   └── strategies.py
├── data_collection/       # 数据收集模块
│   ├── base_data_source.py
│   ├── data_collector.py
│   ├── data_storage.py
│   └── tushare_data_source.py
├── data_processing/       # 数据处理模块
│   ├── data_cleaner.py
│   ├── data_processor.py
│   ├── data_standardizer.py
│   └── feature_engineer.py
├── prediction/            # 预测模块
│   ├── base_model.py
│   ├── deep_learning_models.py
│   ├── model_ensemble.py
│   ├── prediction_manager.py
│   └── traditional_models.py
├── visualization/         # 可视化模块
│   ├── charts.py
│   ├── dashboard.py
│   └── report_generator.py
├── tests/                 # 测试目录
│   └── test_application.py
├── run_app.py             # 启动脚本
└── README.md              # 项目说明
```

## 安装与运行

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置

1. **TuShare API Key**：在 `data_collection/tushare_data_source.py` 中配置你的TuShare API Key

### 运行

```bash
# 启动Web服务
python run_app.py

# 运行测试
python -m unittest discover tests
```

## API接口

启动服务后，可以通过以下地址访问API文档：

- **Swagger UI**：http://localhost:8000/docs
- **ReDoc**：http://localhost:8000/redoc

主要API接口：

- `GET /api/stock/list`：获取股票列表
- `GET /api/stock/history`：获取股票历史数据
- `GET /api/stock/analysis`：获取股票分析结果
- `GET /api/stock/prediction`：获取股票预测结果
- `POST /api/backtest/strategy`：回测交易策略
- `GET /api/report/generate`：生成股票分析报告

## 使用示例

### 1. 获取股票历史数据

```python
from data_collection.data_collector import DataCollector

collector = DataCollector()
data = collector.get_stock_data('600519', '2023-01-01', '2023-12-31')
print(data.head())
```

### 2. 进行技术分析

```python
from analysis.analysis_manager import AnalysisManager

analyzer = AnalysisManager()
result = analyzer.technical_analysis('600519')
print(result)
```

### 3. 预测股价

```python
from prediction.prediction_manager import PredictionManager

predictor = PredictionManager()
prediction = predictor.predict('600519', 'ensemble', 5)
print(prediction)
```

### 4. 回测交易策略

```python
from backtest.backtest_manager import BacktestManager

backtester = BacktestManager()
result = backtester.run_backtest('ma_crossover', '600519', '2023-01-01', '2023-12-31')
print(result)
```

### 5. 生成分析报告

```python
from visualization.report_generator import ReportGenerator

generator = ReportGenerator()
report = generator.generate_report('600519', 'comprehensive')
print(report)
```

### 6. 设置预警规则

```python
from application.alert.alert_system import AlertSystem

alert_system = AlertSystem()
alert_system.add_alert_rule('600519', 'rsi', 70, 'above')
alert_system.start_monitoring()
```

## 注意事项

1. **数据来源**：本系统使用TuShare作为数据来源，需要注册并获取API Key
2. **预测准确性**：股价预测受多种因素影响，预测结果仅供参考，不构成投资建议
3. **回测结果**：回测结果基于历史数据，不代表未来表现
4. **系统性能**：对于大量股票数据的处理可能需要较长时间，建议在性能较好的设备上运行

## 许可证

MIT License
