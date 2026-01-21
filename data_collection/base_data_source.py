from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

class BaseDataSource(ABC):
    """数据源抽象基类"""
    
    @abstractmethod
    def get_stock_list(self, market: str = 'all') -> List[Dict[str, Any]]:
        """获取股票列表"""
        pass
    
    @abstractmethod
    def get_kline_data(self, symbol: str, start_date: str, end_date: str, freq: str = 'D') -> Dict[str, Any]:
        """获取K线数据"""
        pass
    
    @abstractmethod
    def get_realtime_data(self, symbols: List[str]) -> Dict[str, Any]:
        """获取实时数据"""
        pass
    
    @abstractmethod
    def get_financial_data(self, symbol: str, year: int, quarter: int) -> Dict[str, Any]:
        """获取财务数据"""
        pass
    
    @abstractmethod
    def get_index_data(self, index_symbol: str, start_date: str, end_date: str, freq: str = 'D') -> Dict[str, Any]:
        """获取指数数据"""
        pass