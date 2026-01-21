from fastapi import APIRouter, HTTPException, Query
from data_collection.data_collector import DataCollector
from data_processing.data_processor import DataProcessor
from analysis.analysis_manager import AnalysisManager
from prediction.prediction_manager import PredictionManager
from backtest.backtest_manager import BacktestManager
from visualization.report_generator import ReportGenerator

router = APIRouter()

# Initialize components
data_collector = DataCollector()
data_processor = DataProcessor()
analysis_manager = AnalysisManager()
prediction_manager = PredictionManager()
backtest_manager = BacktestManager()
report_generator = ReportGenerator()
data_storage = data_collector.storage

@router.get("/stock/list")
async def get_stock_list():
    """获取股票列表"""
    try:
        # 先从数据库获取
        stocks = data_collector.get_stock_list()
        
        # 如果数据库为空，从API获取
        if not stocks:
            print("数据库股票列表为空，从API获取...")
            stocks = data_collector.data_source.get_stock_list()
            if stocks:
                # 保存到数据库
                data_storage.save_stock_list(stocks)
                print(f"从API获取并保存了 {len(stocks)} 只股票")
            else:
                print("从API获取股票列表失败")
        
        return {"status": "success", "data": stocks}
    except Exception as e:
        print(f"获取股票列表错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stock/add")
async def add_stock(
    symbol: str = Query(..., description="股票代码"),
    name: str = Query(..., description="股票名称"),
    area: str = Query(None, description="地区"),
    industry: str = Query(None, description="行业")
):
    """手动添加股票"""
    try:
        # 构建股票代码格式
        if symbol.startswith('00') or symbol.startswith('30'):
            ts_code = f"{symbol}.SZ"
        elif symbol.startswith('60'):
            ts_code = f"{symbol}.SH"
        else:
            ts_code = symbol
        
        # 创建股票数据
        stock_data = [{
            "ts_code": ts_code,
            "symbol": symbol,
            "name": name,
            "area": area or "未知",
            "industry": industry or "未知",
            "list_date": "2020-01-01"  # 默认上市日期
        }]
        
        # 保存到数据库
        data_storage.save_stock_list(stock_data)
        
        return {"status": "success", "message": f"股票 {name} ({symbol}) 添加成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/stock/delete")
async def delete_stock(
    symbol: str = Query(..., description="股票代码")
):
    """删除股票"""
    try:
        # 从数据库中删除股票
        success = data_storage.delete_stock(symbol)
        if success:
            return {"status": "success", "message": f"股票 {symbol} 已成功删除"}
        else:
            raise HTTPException(status_code=404, detail=f"股票 {symbol} 不存在或删除失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stock/search")
async def search_stock(
    keyword: str = Query(..., description="搜索关键词")
):
    """搜索股票"""
    try:
        # 从数据库中搜索股票
        stocks = data_collector.get_stock_list()
        print(f"数据库中有 {len(stocks)} 只股票")
        print(f"搜索关键词: {keyword}")
        
        # 过滤匹配的股票
        filtered_stocks = []
        for stock in stocks:
            stock_name = stock.get('name', '')
            if (
                keyword in stock['ts_code'] or 
                keyword in stock['symbol'] or 
                keyword in stock_name
            ):
                filtered_stocks.append(stock)
        
        print(f"搜索结果: {len(filtered_stocks)} 只股票")
        
        # 如果数据库中没有，尝试从TuShare API搜索
        if not filtered_stocks:
            try:
                # 尝试使用tushare的实时行情API搜索
                import tushare as ts
                realtime_data = ts.get_realtime_quotes([keyword])
                if not realtime_data.empty:
                    api_stocks = []
                    for _, row in realtime_data.iterrows():
                        api_stocks.append({
                            "ts_code": f"{row['code']}.SZ" if row['code'].startswith('00') or row['code'].startswith('30') else f"{row['code']}.SH",
                            "symbol": row['code'],
                            "name": row['name'],
                            "industry": "未知",
                            "list_date": "2020-01-01"
                        })
                    filtered_stocks = api_stocks
                    print(f"API搜索成功，找到 {len(api_stocks)} 只股票")
                else:
                    print("API搜索未找到匹配股票")
            except Exception as e:
                print(f"API搜索失败: {e}")
        
        return {"status": "success", "data": filtered_stocks}
    except Exception as e:
        print(f"搜索错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stock/realtime")
async def get_stock_realtime(
    symbols: str = Query(..., description="股票代码列表，用逗号分隔")
):
    """获取股票实时价格"""
    try:
        symbol_list = symbols.split(',')
        print(f"获取实时价格：{symbol_list}")
        
        # 直接从tushare获取实时价格
        import tushare as ts
        
        try:
            # 使用tushare的实时行情API
            realtime_data = ts.get_realtime_quotes(symbol_list)
            
            if not realtime_data.empty:
                result = []
                for _, row in realtime_data.iterrows():
                    symbol = row['code']
                    # 构建完整的ts_code
                    ts_code = f"{symbol}.SZ" if symbol.startswith('00') or symbol.startswith('30') else f"{symbol}.SH"
                    
                    # 计算价格和涨跌幅
                    price = float(row.get('price', 0)) if row.get('price') else 0
                    pre_close = float(row.get('pre_close', 0)) if row.get('pre_close') else 0
                    change = price - pre_close
                    pct_chg = (change / pre_close) * 100 if pre_close != 0 else 0
                    volume = float(row.get('volume', 0)) if row.get('volume') else 0
                    
                    # 检查是否停牌（价格为0或交易量为0或涨跌幅为-100%可能表示停牌）
                    is_suspended = False
                    if price == 0 or volume == 0 or abs(pct_chg) == 100:
                        is_suspended = True
                    
                    result.append({
                        'ts_code': ts_code,
                        'symbol': symbol,
                        'name': row.get('name', ''),
                        'price': price,
                        'is_suspended': is_suspended,
                        'pre_close': pre_close,
                        'change': change,
                        'pct_chg': pct_chg,
                        'open': float(row.get('open', 0)) if row.get('open') else 0,
                        'high': float(row.get('high', 0)) if row.get('high') else 0,
                        'low': float(row.get('low', 0)) if row.get('low') else 0,
                        'volume': volume
                    })
                
                return {"status": "success", "data": result}
        except Exception as e:
            print(f"从tushare获取实时价格失败: {e}")
            
        # 如果tushare API失败，尝试从历史数据获取最新价格
        result = []
        for symbol in symbol_list:
            try:
                # 获取最近的K线数据
                from datetime import datetime, timedelta
                end_date = datetime.now().strftime('%Y%m%d')
                start_date = (datetime.now() - timedelta(days=7)).strftime('%Y%m%d')
                
                stock_data = data_collector.get_stock_data(symbol, start_date, end_date, freq='D')
                data = stock_data.get('data', [])
                
                if data:
                    # 按日期排序，获取最新的数据
                    sorted_data = sorted(data, key=lambda x: x['trade_date'], reverse=True)
                    latest = sorted_data[0]
                    
                    # 检查是否停牌（价格为0或交易量为0可能表示停牌）
                    is_suspended = False
                    price = latest.get('close', 0)
                    volume = latest.get('vol', 0)
                    
                    # 如果价格为0或交易量为0，可能是停牌
                    if price == 0 or volume == 0:
                        is_suspended = True
                        
                    result.append({
                        'ts_code': latest.get('ts_code', f"{symbol}.SH" if symbol.startswith('6') else f"{symbol}.SZ"),
                        'symbol': symbol,
                        'name': '',
                        'price': price,
                        'is_suspended': is_suspended,
                        'pre_close': latest.get('pre_close', 0),
                        'change': latest.get('change', 0),
                        'pct_chg': latest.get('pct_chg', 0),
                        'open': latest.get('open', 0),
                        'high': latest.get('high', 0),
                        'low': latest.get('low', 0),
                        'volume': volume
                    })
                else:
                    # 如果没有数据，返回默认值，标记为停牌
                    result.append({
                        'ts_code': f"{symbol}.SH" if symbol.startswith('6') else f"{symbol}.SZ",
                        'symbol': symbol,
                        'name': '',
                        'price': 0,
                        'is_suspended': True,
                        'pre_close': 0,
                        'change': 0,
                        'pct_chg': 0,
                        'open': 0,
                        'high': 0,
                        'low': 0,
                        'volume': 0
                    })
            except Exception as e:
                print(f"获取 {symbol} 最新价格失败: {e}")
                # 出错时，标记为停牌
                result.append({
                    'ts_code': f"{symbol}.SH" if symbol.startswith('6') else f"{symbol}.SZ",
                    'symbol': symbol,
                    'name': '',
                    'price': 0,
                    'is_suspended': True,
                    'pre_close': 0,
                    'change': 0,
                    'pct_chg': 0,
                    'open': 0,
                    'high': 0,
                    'low': 0,
                    'volume': 0
                })
                continue
        
        return {"status": "success", "data": result}
    except Exception as e:
        print(f"获取实时价格错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stock/history")
async def get_stock_history(
    symbol: str = Query(..., description="股票代码"),
    start_date: str = Query(..., description="开始日期，格式：YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期，格式：YYYY-MM-DD")
):
    """获取股票历史数据"""
    try:
        data = data_collector.get_stock_data(symbol, start_date, end_date)
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stock/analysis")
async def get_stock_analysis(
    symbol: str = Query(..., description="股票代码"),
    analysis_type: str = Query("technical", description="分析类型：technical, fundamental, sentiment")
):
    """获取股票分析结果"""
    try:
        if analysis_type == "technical":
            result = analysis_manager.technical_analysis(symbol)
        elif analysis_type == "fundamental":
            result = analysis_manager.fundamental_analysis(symbol)
        elif analysis_type == "sentiment":
            result = analysis_manager.sentiment_analysis(symbol)
        else:
            raise HTTPException(status_code=400, detail="Invalid analysis type")
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stock/prediction")
async def get_stock_prediction(
    symbol: str = Query(..., description="股票代码"),
    model_type: str = Query("ensemble", description="模型类型：traditional, deep_learning, ensemble"),
    days: int = Query(5, description="预测天数")
):
    """获取股票预测结果"""
    try:
        prediction = prediction_manager.predict(symbol, model_type, days)
        return {"status": "success", "data": prediction}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/backtest/strategy")
async def backtest_strategy(
    strategy_name: str = Query(..., description="策略名称"),
    symbol: str = Query(..., description="股票代码"),
    start_date: str = Query(..., description="开始日期，格式：YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期，格式：YYYY-MM-DD")
):
    """回测交易策略"""
    try:
        result = backtest_manager.run_backtest(strategy_name, symbol, start_date, end_date)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/report/generate")
async def generate_report(
    symbol: str = Query(..., description="股票代码"),
    report_type: str = Query("comprehensive", description="报告类型：technical, fundamental, comprehensive")
):
    """生成股票分析报告"""
    try:
        report = report_generator.generate_report(symbol, report_type)
        return {"status": "success", "data": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
