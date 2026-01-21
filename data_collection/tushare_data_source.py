import tushare as ts
from typing import Dict, List, Any
from .base_data_source import BaseDataSource

class TuShareDataSource(BaseDataSource):
    """TuShare数据源实现"""
    
    def __init__(self, token: str = 'ee045be133e95e7faf43a5e656aea979353f2aca66fba160b7f3e348'):
        """初始化TuShare"""
        if token:
            ts.set_token(token)
        self.pro = ts.pro_api()
    
    def search_stocks_by_name(self, keyword: str) -> List[Dict[str, Any]]:
        """根据名称搜索股票"""
        try:
            # 尝试从股票列表中搜索
            stocks = self.get_stock_list()
            # 过滤名称包含关键词的股票
            filtered_stocks = []
            for stock in stocks:
                stock_name = stock.get('name', '')
                if keyword in stock_name:
                    filtered_stocks.append(stock)
            return filtered_stocks
        except Exception as e:
            print(f"搜索股票失败: {e}")
            return []
    
    def get_stock_list(self, market: str = 'all') -> List[Dict[str, Any]]:
        """获取股票列表"""
        try:
            if market == 'all':
                data = self.pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
            elif market == 'sh':
                data = self.pro.stock_basic(exchange='SSE', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
            elif market == 'sz':
                data = self.pro.stock_basic(exchange='SZSE', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
            else:
                data = self.pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
            
            return data.to_dict('records')
        except Exception as e:
            print(f"获取股票列表失败: {e}")
            return []
    
    def get_kline_data(self, symbol: str, start_date: str, end_date: str, freq: str = 'D') -> Dict[str, Any]:
        """获取K线数据"""
        try:
            # 确保股票代码格式正确
            if not (symbol.endswith('.SZ') or symbol.endswith('.SH')):
                # 尝试添加后缀
                if symbol.startswith('6'):
                    symbol = f"{symbol}.SH"
                else:
                    symbol = f"{symbol}.SZ"
                print(f"修正股票代码格式为: {symbol}")
            
            # 转换频率参数
            freq_map = {
                'D': 'D',
                'W': 'W',
                'M': 'M',
                '60': '60min',
                '30': '30min',
                '15': '15min',
                '5': '5min',
                '1': '1min'
            }
            
            tushare_freq = freq_map.get(freq, 'D')
            
            # 获取K线数据
            if tushare_freq == 'D':
                data = self.pro.daily(ts_code=symbol, start_date=start_date, end_date=end_date)
            elif tushare_freq == 'W':
                data = self.pro.weekly(ts_code=symbol, start_date=start_date, end_date=end_date)
            elif tushare_freq == 'M':
                data = self.pro.monthly(ts_code=symbol, start_date=start_date, end_date=end_date)
            else:
                import tushare as ts
                data = ts.pro_bar(ts_code=symbol, start_date=start_date, end_date=end_date, freq=tushare_freq)
            
            return {
                'data': data.to_dict('records'),
                'columns': list(data.columns)
            }
        except Exception as e:
            print(f"获取K线数据失败: {e}")
            return {'data': [], 'columns': []}
    
    def get_realtime_data(self, symbols: List[str]) -> Dict[str, Any]:
        """获取实时数据"""
        try:
            # 使用tushare的实时行情接口
            data = ts.get_realtime_quotes([s.split('.')[0] for s in symbols])
            return {
                'data': data.to_dict('records'),
                'columns': list(data.columns)
            }
        except Exception as e:
            print(f"获取实时数据失败: {e}")
            return {'data': [], 'columns': []}
    
    def get_financial_data(self, symbol: str, year: int, quarter: int) -> Dict[str, Any]:
        """获取财务数据"""
        try:
            # 获取季度财务数据
            data = self.pro.fina_indicator(ts_code=symbol, year=year, quarter=quarter)
            return {
                'data': data.to_dict('records'),
                'columns': list(data.columns)
            }
        except Exception as e:
            print(f"获取财务数据失败: {e}")
            return {'data': [], 'columns': []}
    
    def get_index_data(self, index_symbol: str, start_date: str, end_date: str, freq: str = 'D') -> Dict[str, Any]:
        """获取指数数据"""
        try:
            # 转换频率参数
            freq_map = {
                'D': 'D',
                'W': 'W',
                'M': 'M'
            }
            
            tushare_freq = freq_map.get(freq, 'D')
            
            # 获取指数K线数据
            if tushare_freq == 'D':
                data = self.pro.index_daily(ts_code=index_symbol, start_date=start_date, end_date=end_date)
            elif tushare_freq == 'W':
                data = self.pro.index_weekly(ts_code=index_symbol, start_date=start_date, end_date=end_date)
            elif tushare_freq == 'M':
                data = self.pro.index_monthly(ts_code=index_symbol, start_date=start_date, end_date=end_date)
            else:
                data = self.pro.index_daily(ts_code=index_symbol, start_date=start_date, end_date=end_date)
            
            return {
                'data': data.to_dict('records'),
                'columns': list(data.columns)
            }
        except Exception as e:
            print(f"获取指数数据失败: {e}")
            return {'data': [], 'columns': []}