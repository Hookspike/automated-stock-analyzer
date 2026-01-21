from typing import Dict, List, Optional, Any
from .base_data_source import BaseDataSource
from .tushare_data_source import TuShareDataSource
from .data_storage import DataStorage

class DataCollector:
    """数据收集管理器"""
    
    def __init__(self, data_source: Optional[BaseDataSource] = None, storage: Optional[DataStorage] = None):
        """初始化数据收集器"""
        self.data_source = data_source or TuShareDataSource()
        self.storage = storage or DataStorage()
    
    def get_stock_list(self, market: str = 'all') -> List[Dict[str, Any]]:
        """获取股票列表"""
        print(f"获取 {market} 市场股票列表...")
        
        # 首先从数据库中获取股票列表
        db_stocks = self.storage.get_stock_list()
        print(f"数据库中有 {len(db_stocks)} 只股票")
        
        if db_stocks:
            # 如果数据库中有股票，返回数据库中的股票
            print("从数据库返回股票列表")
            return db_stocks
        else:
            # 如果数据库中没有，从API获取
            print("从API获取股票列表")
            return self.data_source.get_stock_list(market)
    
    def get_stock_data(self, symbol: str, start_date: str, end_date: str, freq: str = 'D') -> Dict[str, Any]:
        """获取股票历史数据"""
        # 1. 股票代码标准化处理
        # 移除可能的前缀和后缀，保留6位数字代码
        import re
        simple_symbol = re.sub(r'[^0-9]', '', symbol)
        
        # 确保股票代码是6位数字
        if len(simple_symbol) > 6:
            simple_symbol = simple_symbol[-6:]
        elif len(simple_symbol) < 6:
            simple_symbol = simple_symbol.zfill(6)
        
        # 2. 确保股票代码格式正确
        if not (symbol.endswith('.SZ') or symbol.endswith('.SH')):
            if simple_symbol.startswith('6'):
                symbol = f"{simple_symbol}.SH"
            else:
                symbol = f"{simple_symbol}.SZ"
        
        try:
            # 3. 尝试使用tushare的pro_api获取数据（优先使用）
            pro = self.data_source.pro
            
            try:
                # 获取K线数据
                if freq == 'D':
                    data = pro.daily(ts_code=symbol, start_date=start_date, end_date=end_date)
                elif freq == 'W':
                    data = pro.weekly(ts_code=symbol, start_date=start_date, end_date=end_date)
                elif freq == 'M':
                    data = pro.monthly(ts_code=symbol, start_date=start_date, end_date=end_date)
                else:
                    # 分钟级别数据
                    import tushare as ts
                    data = ts.pro_bar(ts_code=symbol, start_date=start_date, end_date=end_date, freq=freq)
            
                if data is not None and not data.empty:
                    return {
                        'data': data.to_dict('records'),
                        'columns': list(data.columns)
                    }
            except Exception as e:
                # pro_api失败，尝试其他方式
                pass
            
            # 4. 尝试使用tushare的实时行情API获取最新数据
            import tushare as ts
            
            try:
                # 使用标准化后的6位代码，确保传入列表
                realtime_data = ts.get_realtime_quotes([simple_symbol])
                
                if realtime_data is not None and not realtime_data.empty:
                    # 构建返回数据
                    api_stocks = []
                    for _, row in realtime_data.iterrows():
                        # 使用当前日期作为交易日期
                        from datetime import datetime
                        today = datetime.now().strftime('%Y%m%d')
                        
                        # 构建数据字典
                        stock_data = {
                            'trade_date': today,
                            'ts_code': symbol,
                            'symbol': simple_symbol,
                            'name': row.get('name', ''),
                            'open': float(row.get('open', 0)) if row.get('open') else 0,
                            'high': float(row.get('high', 0)) if row.get('high') else 0,
                            'low': float(row.get('low', 0)) if row.get('low') else 0,
                            'close': float(row.get('price', 0)) if row.get('price') else 0,
                            'pre_close': float(row.get('pre_close', 0)) if row.get('pre_close') else 0,
                            'change': float(row.get('price', 0)) - float(row.get('pre_close', 0)),
                            'pct_chg': (float(row.get('price', 0)) - float(row.get('pre_close', 0))) / float(row.get('pre_close', 1)) * 100,
                            'vol': float(row.get('volume', 0)) if row.get('volume') else 0,
                            'amount': float(row.get('amount', 0)) if row.get('amount') else 0,
                            'freq': freq
                        }
                        api_stocks.append(stock_data)
                    
                    return {
                        'data': api_stocks,
                        'columns': list(api_stocks[0].keys())
                    }
            except Exception as e:
                # 实时行情API失败，尝试数据库
                pass
            
            # 5. 尝试从数据库获取历史数据
            db_data = self.storage.get_kline_data(symbol, start_date, end_date, freq)
            if db_data:
                return {
                    'data': db_data,
                    'columns': ['trade_date', 'open', 'high', 'low', 'close', 'pre_close', 'change', 'pct_chg', 'vol', 'amount', 'ts_code', 'freq']
                }
        
        except Exception as e:
            # 记录错误但不返回给前端
            pass
        
        # 6. 如果所有尝试都失败，返回空数据
        return {'data': [], 'columns': []}
    
    def fetch_and_save_stock_list(self, market: str = 'all'):
        """获取并保存股票列表"""
        print(f"开始获取 {market} 市场股票列表...")
        stocks = self.data_source.get_stock_list(market)
        if stocks:
            self.storage.save_stock_list(stocks)
            print(f"股票列表获取完成，共 {len(stocks)} 只股票")
        else:
            print("获取股票列表失败")
    
    def fetch_and_save_kline_data(self, symbol: str, start_date: str, end_date: str, freq: str = 'D'):
        """获取并保存K线数据"""
        print(f"开始获取 {symbol} 从 {start_date} 到 {end_date} 的 {freq} 级K线数据...")
        
        kline_data = self.data_source.get_kline_data(symbol, start_date, end_date, freq)
        if kline_data and kline_data.get('data'):
            self.storage.save_kline_data(symbol, kline_data['data'], freq)
            print(f"K线数据获取完成，共 {len(kline_data['data'])} 条数据")
        else:
            print("获取K线数据失败")
    
    def fetch_and_save_financial_data(self, symbol: str, year: int, quarter: int):
        """获取并保存财务数据"""
        print(f"开始获取 {symbol} {year}年Q{quarter} 财务数据...")
        
        financial_data = self.data_source.get_financial_data(symbol, year, quarter)
        if financial_data and financial_data.get('data'):
            self.storage.save_financial_data(symbol, year, quarter, financial_data['data'])
            print("财务数据获取完成")
        else:
            print("获取财务数据失败")
    
    def fetch_and_save_index_data(self, index_symbol: str, start_date: str, end_date: str, freq: str = 'D'):
        """获取并保存指数数据"""
        print(f"开始获取 {index_symbol} 从 {start_date} 到 {end_date} 的 {freq} 级数据...")
        
        index_data = self.data_source.get_index_data(index_symbol, start_date, end_date, freq)
        if index_data and index_data.get('data'):
            self.storage.save_index_data(index_symbol, index_data['data'], freq)
            print(f"指数数据获取完成，共 {len(index_data['data'])} 条数据")
        else:
            print("获取指数数据失败")
    
    def get_realtime_data(self, symbols: List[str]) -> Dict[str, Any]:
        """获取实时数据"""
        print(f"开始获取 {len(symbols)} 只股票的实时数据...")
        
        realtime_data = self.data_source.get_realtime_data(symbols)
        if realtime_data and realtime_data.get('data'):
            print(f"实时数据获取完成，共 {len(realtime_data['data'])} 条数据")
        else:
            print("获取实时数据失败")
        
        return realtime_data
    
    def batch_fetch_kline_data(self, symbols: List[str], start_date: str, end_date: str, freq: str = 'D'):
        """批量获取K线数据"""
        print(f"开始批量获取 {len(symbols)} 只股票的K线数据...")
        
        success_count = 0
        fail_count = 0
        
        for symbol in symbols:
            try:
                self.fetch_and_save_kline_data(symbol, start_date, end_date, freq)
                success_count += 1
            except Exception as e:
                print(f"获取 {symbol} 失败: {e}")
                fail_count += 1
        
        print(f"批量获取完成：成功 {success_count} 只，失败 {fail_count} 只")
    
    def initialize_sample_data(self):
        """初始化样本数据"""
        print("开始初始化样本数据...")
        
        # 生成模拟的历史数据
        import datetime
        import random
        import sqlite3
        
        # 直接连接数据库
        db_path = 'stock_data.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 股票列表
        stocks = ['000625.SZ', '002639.SZ', '002049.SZ', '002131.SZ']
        
        # 日期范围
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=30)
        
        try:
            for stock in stocks:
                print(f"初始化 {stock} 的历史数据...")
                
                # 生成每天的数据
                data_count = 0
                current_date = start_date
                current_price = random.uniform(10, 100)
                
                while current_date <= end_date:
                    # 生成随机价格
                    open_price = current_price * random.uniform(0.99, 1.01)
                    high_price = open_price * random.uniform(1.0, 1.03)
                    low_price = open_price * random.uniform(0.97, 1.0)
                    close_price = low_price + (high_price - low_price) * random.random()
                    pre_close = current_price
                    change = close_price - pre_close
                    pct_chg = (change / pre_close) * 100
                    vol = random.uniform(1000000, 10000000)
                    amount = vol * close_price
                    
                    # 插入数据库
                    try:
                        cursor.execute('''
                        INSERT OR REPLACE INTO kline_data (ts_code, trade_date, open, high, low, close, pre_close, change, pct_chg, vol, amount, freq)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (stock, current_date.strftime('%Y%m%d'), open_price, high_price, low_price, close_price, pre_close, change, pct_chg, vol, amount, 'D'))
                        data_count += 1
                    except Exception as e:
                        print(f"插入数据失败: {e}")
                    
                    # 更新当前价格和日期
                    current_price = close_price
                    current_date += datetime.timedelta(days=1)
                
                conn.commit()
                print(f"成功初始化 {stock} 的 {data_count} 条历史数据")
            
            # 验证数据
            cursor.execute('SELECT COUNT(*) FROM kline_data')
            total_count = cursor.fetchone()[0]
            print(f"数据库中共有 {total_count} 条历史数据")
            
        except Exception as e:
            print(f"初始化样本数据失败: {e}")
            conn.rollback()
        finally:
            conn.close()
        
        print("样本数据初始化完成")