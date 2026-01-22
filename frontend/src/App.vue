<template>
  <div class="app-container">
    <!-- 头部导航 -->
    <header class="app-header">
      <h1>股票预测分析系统</h1>
      <nav class="app-nav">
        <ul>
          <li><a href="#stock-list" @click="activeTab = 'stock-list'">股票列表</a></li>
          <li><a href="#stock-history" @click="activeTab = 'stock-history'">历史数据</a></li>
          <li><a href="#stock-analysis" @click="activeTab = 'stock-analysis'">分析结果</a></li>
          <li><a href="#stock-prediction" @click="activeTab = 'stock-prediction'">预测结果</a></li>
          <li><a href="#backtest" @click="activeTab = 'backtest'">策略回测</a></li>
          <li><a href="#report" @click="activeTab = 'report'">分析报告</a></li>
        </ul>
      </nav>
    </header>

    <!-- 主内容区域 -->
    <main class="app-main">
      <!-- 股票列表 -->
      <div v-if="activeTab === 'stock-list'" class="tab-content">
        <h2>股票列表</h2>
        
        <!-- 搜索栏 -->
        <div class="search-bar">
          <input 
            type="text" 
            v-model="searchKeyword" 
            placeholder="搜索股票代码或名称" 
            @input="searchStock"
          />
          <button @click="searchStock">搜索</button>
        </div>
        
        <!-- 股票列表 -->
        <div class="stock-list-container">
          <!-- 列表标题行 -->
          <div class="stock-header-row">
            <div class="header-cell name-header">股票名称</div>
            <div class="header-cell price-header">最新</div>
            <div class="header-cell change-header">涨跌</div>
            <div class="header-cell percent-header">涨幅</div>
            <div class="header-cell prev-header">昨收</div>
            <div class="header-cell actions-header">操作</div>
          </div>
          
          <!-- 股票列表内容 -->
          <div class="stock-items-container">
            <div class="stock-item-card" v-for="stock in filteredStocks" :key="stock.ts_code">
              <div class="stock-item-content">
                <!-- 股票名称和代码 -->
                <div class="stock-info-section">
                  <div class="stock-name-section">
                    <div class="stock-name-text">{{ stock.name }}</div>
                    <div class="stock-code-text">{{ stock.symbol }}</div>
                  </div>
                </div>
                
                <!-- 价格信息 -->
                <div class="price-info-section">
                  <div :class="['price-value', stock.is_suspended ? 'suspended' : stock.change > 0 ? 'positive' : stock.change < 0 ? 'negative' : 'neutral']">
                    {{ stock.is_suspended ? '停牌' : (stockPrices[stock.symbol] ? stockPrices[stock.symbol].toFixed(2) : '加载中...') }}
                  </div>
                </div>
                
                <!-- 涨跌信息 -->
                <div class="change-info-section">
                  <div :class="['change-value', stock.change > 0 ? 'positive' : stock.change < 0 ? 'negative' : 'neutral']">
                    {{ stock.change > 0 ? '+' : '' }}{{ stock.change ? stock.change.toFixed(2) : '0.00' }}
                  </div>
                </div>
                
                <!-- 涨幅信息 -->
                <div class="percent-info-section">
                  <div :class="['percent-value', stock.change_percent > 0 ? 'positive' : stock.change_percent < 0 ? 'negative' : 'neutral']">
                    {{ stock.change_percent > 0 ? '+' : '' }}{{ stock.change_percent ? stock.change_percent.toFixed(2) : '0.00' }}%
                  </div>
                </div>
                
                <!-- 昨收信息 -->
                <div class="prev-info-section">
                  <div class="prev-value">
                    {{ stock.pre_close ? stock.pre_close.toFixed(2) : '0.00' }}
                  </div>
                </div>
                
                <!-- 操作按钮 -->
                <div class="actions-section">
                  <button class="action-btn select-btn" @click="selectStock(stock.ts_code)">
                    选择
                  </button>
                  <button class="action-btn delete-btn" @click="removeStock(stock.ts_code)">
                    删除
                  </button>
                  <button class="action-btn add-btn" @click="addStockFromList(stock)">
                    添加
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="pagination">
          <button @click="prevPage" :disabled="currentPage === 1">上一页</button>
          <span>{{ currentPage }} / {{ totalPages }}</span>
          <button @click="nextPage" :disabled="currentPage === totalPages">下一页</button>
        </div>
      </div>

      <!-- 历史数据 -->
      <div v-if="activeTab === 'stock-history'" class="tab-content">
        <h2>股票历史数据</h2>
        <div class="form-group">
          <label>股票代码:</label>
          <input type="text" v-model="stockSymbol" placeholder="请输入股票代码" />
          <label>开始日期:</label>
          <input type="date" v-model="startDate" />
          <label>结束日期:</label>
          <input type="date" v-model="endDate" />
          <button @click="getStockHistory">获取数据</button>
        </div>
        <div v-if="stockHistoryData" class="stock-history">
          <div v-if="stockHistoryData.data && stockHistoryData.data.length > 0">
            <div class="stock-history-list">
              <div class="stock-history-header">
                <div class="history-item">
                  <div class="history-field">日期</div>
                  <div class="history-field">开盘价</div>
                  <div class="history-field">最高价</div>
                  <div class="history-field">最低价</div>
                  <div class="history-field">收盘价</div>
                  <div class="history-field">成交量</div>
                  <div class="history-field">成交额</div>
                </div>
              </div>
              <div class="history-items">
                <div v-for="item in stockHistoryData.data" :key="item.trade_date" class="history-item">
                  <div class="history-field">{{ item.trade_date }}</div>
                  <div class="history-field">{{ item.open ? item.open.toFixed(2) : '0.00' }}</div>
                  <div class="history-field">{{ item.high ? item.high.toFixed(2) : '0.00' }}</div>
                  <div class="history-field">{{ item.low ? item.low.toFixed(2) : '0.00' }}</div>
                  <div class="history-field">{{ item.close ? item.close.toFixed(2) : '0.00' }}</div>
                  <div class="history-field">{{ item.vol ? (item.vol / 10000).toFixed(2) + '万' : '0.00万' }}</div>
                  <div class="history-field">{{ item.amount ? (item.amount / 10000).toFixed(2) + '万' : '0.00万' }}</div>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="no-data">
            <p>未获取到历史数据，请检查股票代码是否正确，或尝试调整日期范围。</p>
          </div>
        </div>
      </div>

      <!-- 分析结果 -->
      <div v-if="activeTab === 'stock-analysis'" class="tab-content">
        <h2>股票分析结果</h2>
        <div class="form-group analysis-form">
          <label>股票代码:</label>
          <input type="text" v-model="analysisSymbol" placeholder="请输入股票代码" />
          <label>分析类型:</label>
          <select v-model="analysisType" @change="clearAnalysisResult">
            <option value="technical">技术分析</option>
            <option value="fundamental">基本面分析</option>
            <option value="sentiment">情绪分析</option>
          </select>
          <button @click="getStockAnalysis" class="analysis-btn">分析</button>
        </div>
        <div v-if="analysisResult" class="analysis-result-container">
          <!-- 技术分析 -->
          <div v-if="analysisType === 'technical'" class="analysis-content">
            <h3 class="analysis-title">技术分析</h3>
            
            <!-- 信号概览卡片 -->
            <div class="signal-overview">
              <div class="signal-card bullish" v-if="analysisResult.overall_signal === '买入'">
                <div class="signal-icon">📈</div>
                <div class="signal-info">
                  <div class="signal-type">综合信号</div>
                  <div class="signal-value">买入信号</div>
                </div>
              </div>
              <div class="signal-card bearish" v-else-if="analysisResult.overall_signal === '卖出'">
                <div class="signal-icon">📉</div>
                <div class="signal-info">
                  <div class="signal-type">综合信号</div>
                  <div class="signal-value">卖出信号</div>
                </div>
              </div>
              <div class="signal-card neutral" v-else>
                <div class="signal-icon">📊</div>
                <div class="signal-info">
                  <div class="signal-type">综合信号</div>
                  <div class="signal-value">观望信号</div>
                </div>
              </div>
            </div>
            
            <!-- 技术指标卡片 -->
            <div class="analysis-cards">
              <!-- MACD卡片 -->
              <div class="analysis-card">
                <div class="card-header">
                  <h4>MACD</h4>
                  <div class="signal-badge" :class="analysisResult.macd.signal.toLowerCase()">
                    {{ analysisResult.macd.signal }}
                  </div>
                </div>
                <div class="card-content">
                  <div class="metric-item">
                    <span class="metric-label">MACD值:</span>
                    <span class="metric-value">{{ analysisResult.macd.macd }}</span>
                  </div>
                  <div class="metric-item">
                    <span class="metric-label">信号线:</span>
                    <span class="metric-value">{{ analysisResult.macd.signal }}</span>
                  </div>
                  <div class="metric-item">
                    <span class="metric-label">柱状图:</span>
                    <span class="metric-value">{{ analysisResult.macd.histogram }}</span>
                  </div>
                </div>
              </div>
              
              <!-- RSI卡片 -->
              <div class="analysis-card">
                <div class="card-header">
                  <h4>RSI</h4>
                  <div class="signal-badge" :class="analysisResult.rsi.signal.toLowerCase()">
                    {{ analysisResult.rsi.signal }}
                  </div>
                </div>
                <div class="card-content">
                  <div class="metric-item">
                    <span class="metric-label">RSI值:</span>
                    <span class="metric-value">{{ analysisResult.rsi.rsi }}</span>
                  </div>
                  <div class="rsi-indicator">
                    <div class="rsi-bar">
                      <div class="rsi-level" :style="{width: `${analysisResult.rsi.rsi}%`}"></div>
                    </div>
                    <div class="rsi-labels">
                      <span>0</span>
                      <span>30</span>
                      <span>50</span>
                      <span>70</span>
                      <span>100</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- KDJ卡片 -->
              <div class="analysis-card">
                <div class="card-header">
                  <h4>KDJ</h4>
                  <div class="signal-badge" :class="analysisResult.kdj.signal.toLowerCase()">
                    {{ analysisResult.kdj.signal }}
                  </div>
                </div>
                <div class="card-content">
                  <div class="metric-item">
                    <span class="metric-label">K值:</span>
                    <span class="metric-value">{{ analysisResult.kdj.k }}</span>
                  </div>
                  <div class="metric-item">
                    <span class="metric-label">D值:</span>
                    <span class="metric-value">{{ analysisResult.kdj.d }}</span>
                  </div>
                  <div class="metric-item">
                    <span class="metric-label">J值:</span>
                    <span class="metric-value">{{ analysisResult.kdj.j }}</span>
                  </div>
                </div>
              </div>
              
              <!-- MA卡片 -->
              <div class="analysis-card">
                <div class="card-header">
                  <h4>移动平均线</h4>
                  <div class="signal-badge" :class="analysisResult.ma.signal.toLowerCase()">
                    {{ analysisResult.ma.signal }}
                  </div>
                </div>
                <div class="card-content">
                  <div class="ma-values">
                    <div class="ma-item">
                      <span class="ma-label">MA5:</span>
                      <span class="ma-value">{{ analysisResult.ma.ma5 }}</span>
                    </div>
                    <div class="ma-item">
                      <span class="ma-label">MA10:</span>
                      <span class="ma-value">{{ analysisResult.ma.ma10 }}</span>
                    </div>
                    <div class="ma-item">
                      <span class="ma-label">MA20:</span>
                      <span class="ma-value">{{ analysisResult.ma.ma20 }}</span>
                    </div>
                    <div class="ma-item">
                      <span class="ma-label">MA60:</span>
                      <span class="ma-value">{{ analysisResult.ma.ma60 }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 基本面分析 -->
          <div v-else-if="analysisType === 'fundamental'" class="analysis-content">
            <h3 class="analysis-title">基本面分析</h3>
            
            <!-- 评分卡片 -->
            <div class="score-card">
              <div class="score-header">
                <div class="score-title">综合得分</div>
                <div class="score-value">{{ analysisResult.overall_score }}</div>
              </div>
              <div class="score-bar">
                <div class="score-progress" :style="{width: `${analysisResult.overall_score}%`}"></div>
              </div>
              <div class="score-advice">{{ analysisResult.signal }}</div>
            </div>
            
            <!-- 分析卡片 -->
            <div class="analysis-cards">
              <!-- 财务指标卡片 -->
              <div class="analysis-card">
                <div class="card-header">
                  <h4>财务指标</h4>
                </div>
                <div class="card-content">
                  <div class="metric-grid">
                    <div class="metric-item">
                      <span class="metric-label">市盈率 (PE):</span>
                      <span class="metric-value">{{ analysisResult.financial_metrics.pe }}</span>
                    </div>
                    <div class="metric-item">
                      <span class="metric-label">市净率 (PB):</span>
                      <span class="metric-value">{{ analysisResult.financial_metrics.pb }}</span>
                    </div>
                    <div class="metric-item">
                      <span class="metric-label">净资产收益率 (ROE):</span>
                      <span class="metric-value">{{ analysisResult.financial_metrics.roe }}%</span>
                    </div>
                    <div class="metric-item">
                      <span class="metric-label">每股收益 (EPS):</span>
                      <span class="metric-value">{{ analysisResult.financial_metrics.eps }}</span>
                    </div>
                    <div class="metric-item">
                      <span class="metric-label">营收增长率:</span>
                      <span class="metric-value">{{ analysisResult.financial_metrics.revenue_growth }}%</span>
                    </div>
                    <div class="metric-item">
                      <span class="metric-label">利润增长率:</span>
                      <span class="metric-value">{{ analysisResult.financial_metrics.profit_growth }}%</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 行业对比卡片 -->
              <div class="analysis-card">
                <div class="card-header">
                  <h4>行业对比</h4>
                </div>
                <div class="card-content">
                  <div class="industry-comparison">
                    <div class="comparison-item">
                      <span class="comparison-label">PE排名:</span>
                      <div class="ranking-badge">{{ analysisResult.industry_comparison.pe_rank }}</div>
                    </div>
                    <div class="comparison-item">
                      <span class="comparison-label">PB排名:</span>
                      <div class="ranking-badge">{{ analysisResult.industry_comparison.pb_rank }}</div>
                    </div>
                    <div class="comparison-item">
                      <span class="comparison-label">ROE排名:</span>
                      <div class="ranking-badge">{{ analysisResult.industry_comparison.roe_rank }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 情绪分析 -->
          <div v-else-if="analysisType === 'sentiment'" class="analysis-content">
            <h3 class="analysis-title">情绪分析</h3>
            
            <!-- 情绪得分卡片 -->
            <div class="sentiment-score-card">
              <div class="sentiment-score">
                <div class="sentiment-score-value">{{ analysisResult.sentiment_score }}</div>
                <div class="sentiment-score-label">情绪得分</div>
              </div>
              <div class="sentiment-overview">
                <div class="sentiment-type">综合情绪</div>
                <div class="sentiment-value" :class="analysisResult.overall_sentiment.toLowerCase()">
                  {{ analysisResult.overall_sentiment }}
                </div>
              </div>
              <div class="sentiment-advice">{{ analysisResult.signal }}</div>
            </div>
            
            <!-- 情绪卡片 -->
            <div class="analysis-cards">
              <!-- 新闻情绪卡片 -->
              <div class="analysis-card sentiment">
                <div class="card-header">
                  <h4>新闻情绪</h4>
                  <div class="sentiment-badge" :class="analysisResult.news_sentiment.toLowerCase()">
                    {{ analysisResult.news_sentiment }}
                  </div>
                </div>
                <div class="card-content">
                  <div class="sentiment-detail">
                    基于新闻媒体报道分析，当前市场对该股票的情绪偏向于{{ analysisResult.news_sentiment }}。
                  </div>
                </div>
              </div>
              
              <!-- 社交媒体情绪卡片 -->
              <div class="analysis-card sentiment">
                <div class="card-header">
                  <h4>社交媒体情绪</h4>
                  <div class="sentiment-badge" :class="analysisResult.social_media_sentiment.toLowerCase()">
                    {{ analysisResult.social_media_sentiment }}
                  </div>
                </div>
                <div class="card-content">
                  <div class="sentiment-detail">
                    基于社交媒体讨论分析，投资者对该股票的情绪偏向于{{ analysisResult.social_media_sentiment }}。
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 预测结果 -->
      <div v-if="activeTab === 'stock-prediction'" class="tab-content">
        <h2>股票预测结果</h2>
        <div class="form-group">
          <label>股票代码:</label>
          <input type="text" v-model="predictionSymbol" placeholder="请输入股票代码" />
          <label>模型类型:</label>
          <select v-model="modelType">
            <option value="traditional">传统机器学习</option>
            <option value="deep_learning">深度学习</option>
            <option value="ensemble">模型融合</option>
          </select>
          <label>预测天数:</label>
          <input type="number" v-model="predictionDays" min="1" max="30" />
          <button @click="getStockPrediction">预测</button>
        </div>
        <div v-if="predictionResult" class="prediction-result">
          <!-- 股票基本信息栏 -->
          <div class="stock-info-bar">
            <div class="stock-basic">
              <h3>{{ stockInfo.name || predictionResult.symbol }}</h3>
              <span class="stock-code">{{ predictionResult.symbol }}</span>
            </div>
            <div class="stock-price-info">
              <div class="current-price">
                <span class="price-value">{{ stockInfo.currentPrice || '0.00' }}</span>
                <span :class="stockInfo.change >= 0 ? 'rise' : 'fall'">
                  {{ stockInfo.change >= 0 ? '+' : '' }}{{ stockInfo.change || '0.00' }} ({{ stockInfo.changePercent || '0.00' }}%)
                </span>
              </div>
            </div>
          </div>
          
          <div class="prediction-info">
            <div class="info-item">
              <span class="label">模型类型:</span>
              <span class="value">{{ predictionResult.model_type }}</span>
            </div>
            <div class="info-item">
              <span class="label">预测天数:</span>
              <span class="value">{{ predictionResult.prediction_days }}天</span>
            </div>
            <div class="info-item">
              <span class="label">预测时间:</span>
              <span class="value">{{ predictionResult.prediction_time }}</span>
            </div>
            <div class="info-item">
              <span class="label">置信度:</span>
              <span class="value">{{ (predictionResult.confidence * 100).toFixed(2) }}%</span>
            </div>
          </div>
          <div id="prediction-chart" class="chart-container"></div>
          <div class="prediction-table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>日期</th>
                  <th>预测价格</th>
                  <th>涨跌额</th>
                  <th>涨跌幅</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in predictionResult.predictions" :key="item.date">
                  <td>{{ item.date }}</td>
                  <td>{{ item.predicted_price }}</td>
                  <td :class="item.change >= 0 ? 'rise' : 'fall'">
                    {{ item.change >= 0 ? '+' : '' }}{{ item.change }}
                  </td>
                  <td :class="item.change_percent >= 0 ? 'rise' : 'fall'">
                    {{ item.change_percent >= 0 ? '+' : '' }}{{ item.change_percent }}%
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- 策略回测 -->
      <div v-if="activeTab === 'backtest'" class="tab-content">
        <h2>策略回测</h2>
        <div class="form-group">
          <label>策略名称:</label>
          <select v-model="strategyName">
            <option value="ma_crossover">MA交叉</option>
            <option value="rsi">RSI</option>
            <option value="macd">MACD</option>
            <option value="kdj">KDJ</option>
            <option value="bollinger_bands">布林带</option>
          </select>
          <label>股票代码:</label>
          <input type="text" v-model="backtestSymbol" placeholder="请输入股票代码" />
          <label>开始日期:</label>
          <input type="date" v-model="backtestStartDate" />
          <label>结束日期:</label>
          <input type="date" v-model="backtestEndDate" />
          <button @click="runBacktest">回测</button>
        </div>
        <div v-if="backtestResult" class="backtest-result">
          <div class="backtest-info">
            <p>策略名称: {{ backtestResult.strategy }}</p>
            <p>股票代码: {{ backtestResult.symbol }}</p>
            <p>回测周期: {{ backtestResult.period }}</p>
          </div>
          <div class="performance-metrics">
            <h3>绩效指标</h3>
            <table>
              <tr>
                <th>总收益率</th>
                <th>年化收益率</th>
                <th>最大回撤</th>
                <th>夏普比率</th>
                <th>胜率</th>
                <th>交易次数</th>
                <th>盈亏比</th>
              </tr>
              <tr>
                <td>{{ backtestResult.performance.total_return.toFixed(2) }}%</td>
                <td>{{ backtestResult.performance.annual_return.toFixed(2) }}%</td>
                <td>{{ backtestResult.performance.max_drawdown.toFixed(2) }}%</td>
                <td>{{ backtestResult.performance.sharpe_ratio.toFixed(2) }}</td>
                <td>{{ backtestResult.performance.win_rate.toFixed(2) }}%</td>
                <td>{{ backtestResult.performance.total_trades }}</td>
                <td>{{ backtestResult.performance.profit_factor.toFixed(2) }}</td>
              </tr>
            </table>
          </div>
          <div class="backtest-summary">
            <h3>回测摘要</h3>
            <p>{{ backtestResult.summary }}</p>
          </div>
        </div>
      </div>

      <!-- 分析报告 -->
      <div v-if="activeTab === 'report'" class="tab-content">
        <h2>股票分析报告</h2>
        <div class="form-group">
          <label>股票代码:</label>
          <input type="text" v-model="reportSymbol" placeholder="请输入股票代码" />
          <label>报告类型:</label>
          <select v-model="reportType">
            <option value="technical">技术分析报告</option>
            <option value="fundamental">基本面分析报告</option>
            <option value="comprehensive">综合分析报告</option>
          </select>
          <button @click="generateReport">生成报告</button>
        </div>
        <div v-if="reportContent" class="report-content">
          <pre>{{ reportContent }}</pre>
        </div>
      </div>
    </main>

    <!-- 底部信息 -->
    <footer class="app-footer">
      <p>&copy; 2026 股票预测分析系统 | 技术栈：Python, FastAPI, Vue.js, ECharts</p>
    </footer>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      // 导航相关
      activeTab: 'stock-list',
      
      // 股票列表相关
      stocks: [],
      searchKeyword: '',
      currentPage: 1,
      pageSize: 20,
      stockPrices: {}, // 存储实时股票价格
      
      // 添加股票相关
      newStock: {
        symbol: '',
        name: '',
        industry: ''
      },
      
      // 历史数据相关
      stockSymbol: '',
      startDate: '',
      endDate: '',
      stockHistoryData: null,
      
      // 分析结果相关
      analysisSymbol: '',
      analysisType: 'technical',
      analysisResult: null,
      
      // 预测结果相关
      predictionSymbol: '',
      modelType: 'ensemble',
      predictionDays: 5,
      predictionResult: null,
      stockInfo: {
        name: '',
        currentPrice: '0.00',
        change: '0.00',
        changePercent: '0.00'
      },
      
      // 回测相关
      strategyName: 'ma_crossover',
      backtestSymbol: '',
      backtestStartDate: '',
      backtestEndDate: '',
      backtestResult: null,
      
      // 报告相关
      reportSymbol: '',
      reportType: 'comprehensive',
      reportContent: null,
      
      // ECharts实例
      charts: {}
    }
  },
  computed: {
    // 过滤后的股票列表
    filteredStocks() {
      if (!this.searchKeyword) {
        return this.stocks.slice((this.currentPage - 1) * this.pageSize, this.currentPage * this.pageSize)
      }
      return this.stocks
        .filter(stock => 
          stock.ts_code.includes(this.searchKeyword) || 
          stock.name.includes(this.searchKeyword)
        )
        .slice((this.currentPage - 1) * this.pageSize, this.currentPage * this.pageSize)
    },
    // 总页数
    totalPages() {
      return Math.ceil(this.stocks.length / this.pageSize)
    }
  },
  mounted() {
    // 初始化页面
    this.initPage()
  },
  methods: {
    // 初始化页面
    async initPage() {
      // 获取股票列表
      await this.getStockList()
      
      // 设置默认日期
      const today = new Date()
      const oneMonthAgo = new Date(today.setMonth(today.getMonth() - 1))
      
      this.startDate = oneMonthAgo.toISOString().split('T')[0]
      this.endDate = new Date().toISOString().split('T')[0]
      this.backtestStartDate = oneMonthAgo.toISOString().split('T')[0]
      this.backtestEndDate = new Date().toISOString().split('T')[0]
    },
    
    // 获取股票列表
    async getStockList() {
      try {
        const response = await this.$api.get('/stock/list')
        if (response.data.status === 'success') {
          this.stocks = response.data.data
          // 获取实时价格
          await this.getStockPrices()
        }
      } catch (error) {
        console.error('获取股票列表失败:', error)
        // 清空股票列表，不使用模拟数据
        this.stocks = []
      }
    },
    
    // 处理搜索输入
    handleSearchInput(event) {
      console.log(`搜索输入: ${event.target.value}`)
      // 防抖处理，避免频繁请求
      clearTimeout(this.searchTimer)
      this.searchTimer = setTimeout(() => {
        console.log(`执行搜索: ${this.searchKeyword}`)
        this.searchStock()
      }, 300)
    },
    
    // 搜索股票
    async searchStock() {
      // 重置页码
      this.currentPage = 1
      
      // 如果搜索关键词不为空，从API搜索
      if (this.searchKeyword) {
        try {
          console.log(`开始搜索: ${this.searchKeyword}`)
          
          // 直接使用axios发起请求，确保编码正确
          const response = await axios.get(`http://localhost:8000/api/stock/search`, {
            params: {
              keyword: this.searchKeyword
            }
          })
          
          console.log('API响应:', response.data)
          
          if (response.data.status === 'success') {
            console.log(`搜索结果: ${response.data.data.length} 只股票`)
            console.log('搜索结果详情:', response.data.data)
            // 使用搜索结果替换当前列表
            this.stocks = response.data.data
            // 获取搜索结果的实时价格
            await this.getStockPrices()
            console.log(`搜索成功，找到 ${response.data.data.length} 只股票`)
          } else {
            console.log('搜索失败，状态码:', response.data.status)
          }
        } catch (error) {
          console.error('搜索股票失败:', error)
          // 如果API搜索失败，使用本地过滤
          console.log('使用本地过滤')
        }
      } else {
        // 如果搜索关键词为空，重新获取完整列表
        await this.getStockList()
      }
    },
    
    // 上一页
    prevPage() {
      if (this.currentPage > 1) {
        this.currentPage--
      }
    },
    
    // 下一页
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++
      }
    },
    
    // 选择股票
    selectStock(symbol) {
      this.stockSymbol = symbol
      this.analysisSymbol = symbol
      this.predictionSymbol = symbol
      this.backtestSymbol = symbol
      this.reportSymbol = symbol
      this.activeTab = 'stock-history'
    },
    
    // 添加股票
    async addStock() {
      if (!this.newStock.symbol || !this.newStock.name) {
        alert('请输入股票代码和名称')
        return
      }
      
      try {
        const response = await this.$api.post(`/stock/add?symbol=${this.newStock.symbol}&name=${this.newStock.name}&industry=${this.newStock.industry}`)
        if (response.data.status === 'success') {
          alert(`股票 ${this.newStock.name} (${this.newStock.symbol}) 添加成功`)
          // 重新获取股票列表
          await this.getStockList()
          // 清空表单
          this.newStock = {
            symbol: '',
            name: '',
            industry: ''
          }
        }
      } catch (error) {
        console.error('添加股票失败:', error)
        alert('添加股票失败，请重试')
      }
    },
    
    // 删除股票
    async removeStock(symbol) {
      if (confirm(`确定要删除股票 ${symbol} 吗？`)) {
        try {
          // 调用后端API删除股票
          const response = await this.$api.delete(`/stock/delete?symbol=${symbol}`)
          
          if (response.data.status === 'success') {
            // 从前端列表中移除
            this.stocks = this.stocks.filter(stock => !stock.ts_code.includes(symbol))
            alert(response.data.message)
          } else {
            alert(`删除失败: ${response.data.message}`)
          }
        } catch (error) {
          console.error('删除股票失败:', error)
          alert('删除股票失败，请重试')
        }
      }
    },
    
    // 从列表中添加股票
    async addStockFromList(stock) {
      try {
        const symbol = stock.symbol || stock.ts_code.split('.')[0]
        const name = stock.name
        const industry = stock.industry || '未知'
        
        const response = await this.$api.post(`/stock/add?symbol=${symbol}&name=${name}&industry=${industry}`)
        if (response.data.status === 'success') {
          alert(`股票 ${name} (${symbol}) 添加成功`)
          // 重新获取完整的股票列表（不带搜索关键词）
          this.searchKeyword = '' // 清空搜索关键词
          await this.getStockList() // 重新获取完整列表
        }
      } catch (error) {
        console.error('添加股票失败:', error)
        alert('添加股票失败，请重试')
      }
    },
    
    // 获取实时股票价格和相关数据
    async getStockPrices() {
      try {
        // 收集所有股票代码
        const symbol_list = this.stocks.map(stock => stock.symbol).join(',')
        
        // 调用新的实时价格API
        const response = await this.$api.get(`/stock/realtime?symbols=${symbol_list}`)
        
        if (response.data.status === 'success') {
          const realtime_data = response.data.data
          
          // 更新每个股票的价格
          for (const stock of this.stocks) {
            const symbol = stock.symbol
            const data = realtime_data.find(item => item.symbol === symbol)
            
            if (data) {
              // 使用真实的实时价格
              this.stockPrices[symbol] = data.price
              stock.pre_close = data.pre_close
              stock.change = data.change
              stock.change_percent = data.pct_chg
              // 保存停牌状态
              stock.is_suspended = data.is_suspended || false
            } else {
              // 如果没有找到该股票的数据，使用默认值
              this.stockPrices[symbol] = 0
              stock.pre_close = 0
              stock.change = 0
              stock.change_percent = 0
              // 未找到数据时默认为停牌
              stock.is_suspended = true
            }
          }
        }
      } catch (error) {
        console.error('获取实时价格失败:', error)
        // 如果API调用失败，使用默认价格
        for (const stock of this.stocks) {
          const symbol = stock.symbol
          this.stockPrices[symbol] = 0
          stock.pre_close = 0
          stock.change = 0
          stock.change_percent = 0
        }
      }
    },
    
    // 获取股票历史数据
    async getStockHistory() {
      try {
        console.log(`开始获取历史数据: 股票代码=${this.stockSymbol}, 开始日期=${this.startDate}, 结束日期=${this.endDate}`)
        const response = await this.$api.get(`/stock/history?symbol=${this.stockSymbol}&start_date=${this.startDate}&end_date=${this.endDate}`)
        console.log('历史数据API响应:', response.data)
        if (response.data.status === 'success') {
          this.stockHistoryData = response.data.data
          console.log('历史数据:', this.stockHistoryData)
          this.renderKlineChart()
          this.renderVolumeChart()
        }
      } catch (error) {
        console.error('获取股票历史数据失败:', error)
        // 清空历史数据，不使用模拟数据
        this.stockHistoryData = null
      }
    },
    
    // 清空分析结果
    clearAnalysisResult() {
      this.analysisResult = null
    },
    
    // 获取股票分析结果
    async getStockAnalysis() {
      try {
        const response = await this.$api.get(`/stock/analysis?symbol=${this.analysisSymbol}&analysis_type=${this.analysisType}`)
        if (response.data.status === 'success') {
          this.analysisResult = response.data.data
        }
      } catch (error) {
        console.error('获取股票分析结果失败:', error)
        // 清空分析结果，不使用模拟数据
        this.analysisResult = null
      }
    },
    
    // 获取股票预测结果
    async getStockPrediction() {
      try {
        const response = await this.$api.get(`/stock/prediction?symbol=${this.predictionSymbol}&model_type=${this.modelType}&days=${this.predictionDays}`)
        if (response.data.status === 'success') {
          this.predictionResult = response.data.data
          this.renderPredictionChart()
          
          // 填充股票基本信息
          this.fillStockInfo(this.predictionSymbol)
        }
      } catch (error) {
        console.error('获取股票预测结果失败:', error)
        // 清空预测结果，不使用模拟数据
        this.predictionResult = null
      }
    },
    
    // 填充股票基本信息
    fillStockInfo(symbol) {
      // 查找股票列表中是否有该股票的信息
      const stock = this.stocks.find(s => s.symbol === symbol || s.ts_code === symbol)
      
      // 从预测结果中获取最新价格（作为基准）
      let currentPrice = '20.00'
      if (this.predictionResult && this.predictionResult.predictions.length > 0) {
        // 使用预测结果中的基准价格作为当前价格
        const firstPrediction = this.predictionResult.predictions[0]
        // 计算当前价格（假设预测的第一天变化是基于当前价格）
        currentPrice = (firstPrediction.predicted_price - firstPrediction.change).toFixed(2)
      }
      
      // 更新股票基本信息
      this.stockInfo = {
        name: stock ? stock.name : symbol,
        currentPrice: currentPrice,
        change: this.predictionResult ? this.predictionResult.predictions[0].change.toFixed(2) : '0.00',
        changePercent: this.predictionResult ? this.predictionResult.predictions[0].change_percent.toFixed(2) : '0.00'
      }
    },
    
    // 回测交易策略
    async runBacktest() {
      try {
        const response = await this.$api.post(`/backtest/strategy?strategy_name=${this.strategyName}&symbol=${this.backtestSymbol}&start_date=${this.backtestStartDate}&end_date=${this.backtestEndDate}`)
        if (response.data.status === 'success') {
          this.backtestResult = response.data.data
        }
      } catch (error) {
        console.error('回测交易策略失败:', error)
        // 清空回测结果，不使用模拟数据
        this.backtestResult = null
      }
    },
    
    // 生成分析报告
    async generateReport() {
      try {
        const response = await this.$api.get(`/report/generate?symbol=${this.reportSymbol}&report_type=${this.reportType}`)
        if (response.data.status === 'success') {
          this.reportContent = response.data.data
        }
      } catch (error) {
        console.error('生成分析报告失败:', error)
        // 清空报告内容，不使用模拟数据
        this.reportContent = null
      }
    },
    
    // 渲染K线图
    renderKlineChart() {
      if (!this.$echarts) return
      
      const chartDom = document.getElementById('kline-chart')
      if (!chartDom) return
      
      const myChart = this.$echarts.init(chartDom)
      this.charts.kline = myChart
      
      const option = {
        title: {
          text: 'K线图',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          }
        },
        xAxis: {
          type: 'category',
          data: this.stockHistoryData.data.map(item => item.trade_date)
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            data: this.stockHistoryData.data.map(item => [item.open, item.close, item.low, item.high]),
            type: 'candlestick',
            itemStyle: {
              color: '#57a3f3',
              color0: '#fac858',
              borderColor: '#57a3f3',
              borderColor0: '#fac858'
            }
          }
        ]
      }
      
      myChart.setOption(option)
    },
    
    // 渲染成交量图
    renderVolumeChart() {
      if (!this.$echarts) return
      
      const chartDom = document.getElementById('volume-chart')
      if (!chartDom) return
      
      const myChart = this.$echarts.init(chartDom)
      this.charts.volume = myChart
      
      const option = {
        title: {
          text: '成交量',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: this.stockHistoryData.data.map(item => item.trade_date)
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            data: this.stockHistoryData.data.map(item => item.vol),
            type: 'bar',
            itemStyle: {
              color: function(params) {
                const data = this.stockHistoryData.data[params.dataIndex]
                return data.close >= data.open ? '#57a3f3' : '#fac858'
              }.bind(this)
            }
          }
        ]
      }
      
      myChart.setOption(option)
    },
    
    // 渲染预测图
    renderPredictionChart() {
      if (!this.$echarts) return
      
      const chartDom = document.getElementById('prediction-chart')
      if (!chartDom) return
      
      const myChart = this.$echarts.init(chartDom)
      this.charts.prediction = myChart
      
      const option = {
        title: {
          text: '价格预测',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: this.predictionResult.predictions.map(item => item.date)
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            data: this.predictionResult.predictions.map(item => item.predicted_price),
            type: 'line',
            smooth: true,
            lineStyle: {
              color: '#57a3f3',
              width: 2
            },
            itemStyle: {
              color: '#57a3f3'
            }
          }
        ]
      }
      
      myChart.setOption(option)
    }
  }
}
</script>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: Arial, sans-serif;
  background-color: #f5f5f5;
  color: #333;
  line-height: 1.6;
}

/* 应用容器 */
.app-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* 头部导航 */
.app-header {
  background-color: #2c3e50;
  color: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.app-header h1 {
  text-align: center;
  margin-bottom: 20px;
}

.app-nav ul {
  display: flex;
  justify-content: center;
  list-style: none;
  flex-wrap: wrap;
}

.app-nav li {
  margin: 0 10px;
}

.app-nav a {
  color: white;
  text-decoration: none;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.app-nav a:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

/* 主内容区域 */
.app-main {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 标签内容 */
.tab-content {
  padding: 20px 0;
}

.tab-content h2 {
  margin-bottom: 20px;
  color: #3498db;
}

/* 表单组 */
.form-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
  align-items: center;
}

.form-group label {
  font-weight: bold;
}

.form-group input,
.form-group select,
.form-group button {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.form-group button {
  background-color: #3498db;
  color: white;
  border: none;
  cursor: pointer;
  transition: background-color 0.3s;
}

.form-group button:hover {
  background-color: #2980b9;
}

/* 搜索栏 */
.search-bar {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.search-bar input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.search-bar button {
  padding: 8px 12px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.search-bar button:hover {
  background-color: #2980b9;
}

/* 股票列表 */
.stock-list {
  margin-bottom: 20px;
  background-color: #ffffff;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  overflow: hidden;
}

.stock-row {
  display: flex;
  align-items: center;
  border-bottom: 1px solid #f0f0f0;
  background-color: #ffffff;
  transition: background-color 0.2s ease;
}

.stock-row:last-child {
  border-bottom: none;
}

.stock-row:hover {
  background-color: #fafafa;
}

.stock-cell {
  padding: 15px 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.name-cell {
  flex: 1;
  justify-content: flex-start;
}

.stock-full-name {
  font-size: 16px;
  font-weight: 600;
  color: #333333;
  display: flex;
  align-items: center;
}

.stock-symbol-code {
  font-size: 14px;
  font-weight: 500;
  color: #000000;
  margin-left: 8px;
  background-color: #f0f0f0;
  padding: 2px 8px;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.data-cell {
  flex: 1;
  flex-direction: column;
  gap: 3px;
}

.actions-cell {
  flex: 0 0 auto;
  gap: 8px;
}

.stock-data-label {
  font-size: 12px;
  color: #666666;
}

.stock-data-value {
  font-size: 16px;
  font-weight: 600;
  color: #333333;
}

.stock-data {
  flex: 1;
  display: flex;
  justify-content: space-around;
  align-items: center;
}

.stock-data-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stock-data-label {
  font-size: 12px;
  color: #999;
  margin-bottom: 2px;
}

.stock-price {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.stock-change {
  font-size: 14px;
  font-weight: bold;
}

.stock-change-percent {
  font-size: 14px;
  font-weight: bold;
}

.stock-prev-close {
  font-size: 14px;
  color: #333;
}

.stock-actions {
  display: flex;
  gap: 5px;
}

.stock-actions button {
  padding: 5px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: background-color 0.3s;
}

.stock-actions button:hover {
  opacity: 0.9;
}

.stock-actions .remove-btn {
  background-color: #e74c3c;
  color: white;
}

.stock-actions .add-btn {
  background-color: #27ae60;
  color: white;
}

.rise {
  color: #e74c3c;
}

.fall {
  color: #27ae60;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stock-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .stock-data {
    width: 100%;
    justify-content: space-between;
  }
  
  .stock-actions {
    width: 100%;
    justify-content: flex-end;
  }
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  gap: 10px;
  align-items: center;
}

.pagination button {
  padding: 5px 10px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.pagination button:hover:not(:disabled) {
  background-color: #2980b9;
}

.pagination button:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
}

/* 股票历史数据 */
.stock-history {
  margin-top: 20px;
}

/* 历史数据列表 */
.stock-history-list {
  background-color: #f5f5f5;
  border-radius: 4px;
  padding: 10px;
  margin-top: 20px;
  clear: both;
  overflow: hidden;
}

.stock-history-header {
  background-color: #3498db;
  color: white;
  border-radius: 4px;
  padding: 10px;
  margin-bottom: 10px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: white;
  border-radius: 4px;
  padding: 12px;
  margin-bottom: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  color: #333;
}

.history-item:hover {
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
}

.history-field {
  flex: 1;
  text-align: center;
  font-size: 14px;
  color: #333;
}

/* 表单输入框样式 */
.form-group input,
.form-group select {
  color: #333;
  background-color: white;
  border: 1px solid #ddd;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .history-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  
  .history-field {
    text-align: left;
    width: 100%;
    display: flex;
    justify-content: space-between;
    color: #333;
  }
  
  .history-field::before {
    content: attr(data-label);
    font-weight: bold;
    margin-right: 10px;
    color: #333;
  }
}

/* 无数据提示 */
.no-data {
  text-align: center;
  padding: 40px 20px;
  background-color: #f9f9f9;
  border-radius: 4px;
  margin-top: 20px;
  color: #777;
  font-size: 16px;
}

/* 分析表单 */
.analysis-form {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  align-items: center;
}

.analysis-form label {
  color: white;
  font-weight: 600;
  margin-right: 5px;
}

.analysis-form input,
.analysis-form select {
  padding: 10px 15px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.9);
  color: #333;
  min-width: 120px;
}

.analysis-btn {
  background: #27ae60;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.analysis-btn:hover {
  background: #229954;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

/* 分析结果容器 */
.analysis-result-container {
  margin-top: 20px;
}

.analysis-content {
  animation: fadeIn 0.5s ease-in-out;
}

.analysis-title {
  font-size: 24px;
  color: #2c3e50;
  margin-bottom: 20px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 信号概览卡片 */
.signal-overview {
  margin-bottom: 24px;
}

.signal-card {
  display: flex;
  align-items: center;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  max-width: 300px;
  transition: all 0.3s ease;
}

.signal-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.signal-card.bullish {
  background: linear-gradient(135deg, #66bb6a 0%, #43a047 100%);
  color: white;
}

.signal-card.bearish {
  background: linear-gradient(135deg, #ef5350 0%, #e53935 100%);
  color: white;
}

.signal-card.neutral {
  background: linear-gradient(135deg, #64b5f6 0%, #42a5f5 100%);
  color: white;
}

.signal-icon {
  font-size: 40px;
  margin-right: 15px;
}

.signal-info {
  flex: 1;
}

.signal-type {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 4px;
}

.signal-value {
  font-size: 24px;
  font-weight: 700;
}

/* 分析卡片容器 */
.analysis-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

/* 通用分析卡片 */
.analysis-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
  border: 1px solid #e0e0e0;
}

.analysis-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  border-color: #3498db;
}

.card-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.card-content {
  padding: 20px;
}

/* 信号徽章 */
.signal-badge {
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.signal-badge.buy {
  background: #27ae60;
  color: white;
}

.signal-badge.sell {
  background: #e74c3c;
  color: white;
}

.signal-badge.hold {
  background: #f39c12;
  color: white;
}

/* 指标项 */
.metric-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.metric-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.metric-label {
  color: #666;
  font-size: 14px;
}

.metric-value {
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

/* 指标网格 */
.metric-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

/* RSI指标 */
.rsi-indicator {
  margin-top: 16px;
}

.rsi-bar {
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.rsi-level {
  height: 100%;
  background: linear-gradient(90deg, #e74c3c 0%, #f39c12 50%, #27ae60 100%);
  border-radius: 4px;
  transition: width 0.5s ease;
}

.rsi-labels {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;
}

/* MA值显示 */
.ma-values {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.ma-item {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 8px;
  text-align: center;
  border: 1px solid #e9ecef;
}

.ma-label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.ma-value {
  display: block;
  font-weight: 600;
  color: #333;
  font-size: 16px;
}

/* 评分卡片 */
.score-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  padding: 24px;
  margin-bottom: 24px;
  text-align: center;
}

.score-header {
  margin-bottom: 20px;
}

.score-title {
  font-size: 16px;
  color: #666;
  margin-bottom: 8px;
}

.score-value {
  font-size: 48px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.score-bar {
  height: 12px;
  background: #e0e0e0;
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 16px;
}

.score-progress {
  height: 100%;
  background: linear-gradient(90deg, #e74c3c 0%, #f39c12 50%, #27ae60 100%);
  border-radius: 6px;
  transition: width 0.8s ease;
}

.score-advice {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

/* 行业对比 */
.industry-comparison {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.comparison-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.comparison-label {
  font-size: 14px;
  color: #666;
}

.ranking-badge {
  background: #3498db;
  color: white;
  padding: 6px 16px;
  border-radius: 16px;
  font-weight: 600;
  font-size: 14px;
}

/* 情绪分析 */
.sentiment-score-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  padding: 24px;
  margin-bottom: 24px;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sentiment-score {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.sentiment-score-value {
  font-size: 48px;
  font-weight: 700;
  color: #3498db;
}

.sentiment-score-label {
  font-size: 16px;
  color: #666;
  margin-top: -8px;
}

.sentiment-overview {
  margin: 8px 0;
}

.sentiment-type {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.sentiment-value {
  font-size: 24px;
  font-weight: 700;
  padding: 8px 24px;
  border-radius: 20px;
  display: inline-block;
}

.sentiment-value.bullish {
  background: #27ae60;
  color: white;
}

.sentiment-value.bearish {
  background: #e74c3c;
  color: white;
}

.sentiment-value.neutral {
  background: #f39c12;
  color: white;
}

.sentiment-advice {
  font-size: 16px;
  color: #333;
  font-weight: 600;
}

/* 情绪卡片 */
.analysis-card.sentiment .card-header {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.sentiment-badge {
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.sentiment-detail {
  color: #666;
  line-height: 1.6;
  font-size: 14px;
}

/* 情绪得分 */
.sentiment-score-card .sentiment-score-value {
  font-size: 56px;
}

/* 动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .analysis-cards {
    grid-template-columns: 1fr;
  }
  
  .metric-grid {
    grid-template-columns: 1fr;
  }
  
  .ma-values {
    grid-template-columns: 1fr;
  }
  
  .analysis-form {
    flex-direction: column;
    align-items: stretch;
  }
  
  .analysis-form input,
  .analysis-form select {
    width: 100%;
  }
}

/* 股票列表 - 专业设计 */
.stock-list-container {
  margin: 20px 0;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  border: 1px solid #e8eaed;
}

/* 列表标题行 */
.stock-header-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 1fr 1.2fr;
  padding: 16px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 600;
  font-size: 14px;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  align-items: center;
  height: 60px;
}

.header-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  width: 100%;
}

.name-header {
  justify-content: flex-start;
}

/* 操作标题居中，与下方操作按钮对齐 */
.actions-header {
  justify-content: center;
}

/* 股票列表内容容器 */
.stock-items-container {
  display: flex;
  flex-direction: column;
}

/* 股票项卡片 */
.stock-item-card {
  border-bottom: 1px solid #f0f2f5;
  transition: all 0.3s ease;
}

.stock-item-card:last-child {
  border-bottom: none;
}

.stock-item-card:hover {
  background-color: #f8fafc;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-1px);
}

.stock-item-content {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 1fr 1.2fr;
  padding: 16px 24px;
  align-items: center;
  height: 60px;
}

/* 统一数据单元格样式 */
.stock-info-section,
.price-info-section,
.change-info-section,
.percent-info-section,
.prev-info-section,
.actions-section {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  width: 100%;
  padding: 0;
}

/* 股票名称特殊处理 */
.stock-info-section {
  justify-content: flex-start;
}

/* 操作按钮间距 */
.actions-section {
  gap: 8px;
}

/* 股票信息部分 */
.stock-info-section {
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.stock-name-section {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stock-name-text {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.4;
}

.stock-code-text {
  font-size: 14px;
  font-weight: 500;
  color: #64748b;
  background: #f1f5f9;
  padding: 3px 10px;
  border-radius: 12px;
  display: inline-block;
  align-self: flex-start;
}

.price-value {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.2;
}

/* 涨跌信息部分 */
.change-info-section {
  display: flex;
  align-items: center;
  justify-content: center;
}

.change-value {
  font-size: 16px;
  font-weight: 600;
  line-height: 1.2;
}

/* 涨幅信息部分 */
.percent-info-section {
  display: flex;
  align-items: center;
  justify-content: center;
}

.percent-value {
  font-size: 16px;
  font-weight: 600;
  line-height: 1.2;
}

/* 昨收信息部分 */
.prev-info-section {
  display: flex;
  align-items: center;
  justify-content: center;
}

.prev-value {
  font-size: 16px;
  font-weight: 500;
  color: #64748b;
  line-height: 1.2;
}

/* 操作按钮部分 */
.actions-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

/* 操作按钮 */
.action-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  min-width: 80px;
}

.action-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.action-btn:active {
  transform: translateY(0);
}

/* 按钮样式 */
.select-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.delete-btn {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
}

.add-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

/* 涨跌颜色 */
.positive {
  color: #ef4444;
}

.negative {
  color: #10b981;
}

.neutral {
  color: #64748b;
}

/* 停牌样式 */
.suspended {
  color: #f59e0b;
  font-style: italic;
  font-weight: 600;
}

/* 分页 - 专业设计 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 30px 0;
  gap: 12px;
}

.pagination button {
  padding: 10px 20px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  color: #475569;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 80px;
}

.pagination button:hover:not(:disabled) {
  border-color: #667eea;
  color: #667eea;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.pagination span {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
  padding: 10px 0;
}

/* 页面标题样式 */
h2 {
  color: #1e293b;
  font-size: 28px;
  font-weight: 700;
  margin: 24px 0;
  text-align: center;
  letter-spacing: -0.5px;
}

/* 标签页内容样式 */
.tab-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  padding: 24px;
  margin-top: 16px;
  border: 1px solid #e8eaed;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .stock-header-row,
  .stock-item-content {
    grid-template-columns: 1.5fr 1fr 1fr 1fr 1fr 1fr;
    padding: 16px 12px;
  }
  
  .stock-name-text {
    font-size: 16px;
  }
  
  .stock-code-text {
    font-size: 13px;
  }
  
  .price-value,
  .change-value,
  .percent-value,
  .prev-value {
    font-size: 16px;
  }
  
  .action-btn {
    padding: 6px 12px;
    font-size: 12px;
    min-width: 70px;
  }
}

@media (max-width: 768px) {
  .stock-header-row {
    display: none;
  }
  
  .stock-item-content {
    grid-template-columns: 1fr;
    gap: 16px;
    text-align: center;
    padding: 20px;
  }
  
  .actions-section {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .action-btn {
    flex: 1;
    min-width: 120px;
  }
}

/* 预测结果 */
.prediction-result {
  margin-top: 20px;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

/* 股票基本信息栏 */
.stock-info-bar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stock-basic {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stock-basic h3 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.stock-code {
  background-color: rgba(255, 255, 255, 0.35);
  color: white;
  padding: 5px 12px;
  border-radius: 15px;
  font-size: 14px;
  font-weight: 600;
  opacity: 1;
}

.stock-price-info {
  text-align: right;
}

.current-price {
  font-size: 18px;
}

.price-value {
  font-size: 28px;
  font-weight: 700;
  margin-right: 10px;
}

/* 预测信息 */
.prediction-info {
  background-color: #f8f9fa;
  padding: 20px;
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  border-bottom: 1px solid #e9ecef;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-item .label {
  color: #6c757d;
  font-size: 14px;
  font-weight: 500;
}

.info-item .value {
  color: #495057;
  font-size: 14px;
  font-weight: 600;
}

/* 图表容器 */
.chart-container {
  padding: 20px;
  height: 400px;
}

/* 预测表格 */
.prediction-table-wrapper {
  padding: 20px;
  overflow-x: auto;
}

.prediction-result table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.prediction-result th,
.prediction-result td {
  padding: 12px 15px;
  text-align: right;
  border-bottom: 1px solid #e9ecef;
}

.prediction-result th:first-child,
.prediction-result td:first-child {
  text-align: left;
}

.prediction-result th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #495057;
  text-transform: uppercase;
  font-size: 12px;
  letter-spacing: 0.5px;
  position: sticky;
  top: 0;
  z-index: 10;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.prediction-result tbody tr:hover {
  background-color: #f8f9fa;
  transition: background-color 0.2s ease;
}

/* 涨跌颜色 */
.rise {
  color: #dc3545;
  font-weight: 600;
}

.fall {
  color: #28a745;
  font-weight: 600;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stock-info-bar {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .stock-basic {
    justify-content: center;
  }
  
  .prediction-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .chart-container {
    height: 300px;
    padding: 10px;
  }
}

/* 回测结果 */
.backtest-result {
  margin-top: 20px;
}

.backtest-info {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 15px;
}

.performance-metrics {
  margin-bottom: 15px;
}

.performance-metrics table {
  width: 100%;
  border-collapse: collapse;
}

.performance-metrics th,
.performance-metrics td {
  padding: 10px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.performance-metrics th {
  background-color: #f2f2f2;
  font-weight: bold;
}

.backtest-summary {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 4px;
}

/* 分析报告 */
.report-content {
  margin-top: 20px;
  white-space: pre-wrap;
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 4px;
  font-family: monospace;
}

/* 图表容器 */
.chart-container {
  width: 100%;
  height: 400px;
  margin-bottom: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-nav ul {
    flex-direction: column;
    align-items: center;
  }
  
  .form-group {
    flex-direction: column;
    align-items: stretch;
  }
  
  .chart-container {
    height: 300px;
  }
}
</style>
