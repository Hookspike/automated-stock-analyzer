import json
import os
from typing import Dict, List, Any
import psycopg2
from psycopg2.extras import DictCursor

class DataStorage:
    """数据存储类 - 支持 PostgreSQL"""
    
    def __init__(self, db_url: str = None):
        """初始化数据库连接
        
        Args:
            db_url: PostgreSQL 连接字符串，格式：postgresql://username:password@host:port/database
                   如果为 None，从环境变量 DATABASE_URL 获取
        """
        self.db_url = db_url or os.getenv('DATABASE_URL')
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表结构"""
        if not self.db_url:
            print("警告：未设置 DATABASE_URL，无法初始化数据库")
            return
        
        conn = psycopg2.connect(self.db_url)
        cursor = conn.cursor()
        
        # 创建股票列表表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_list (
            id SERIAL PRIMARY KEY,
            ts_code TEXT UNIQUE,
            symbol TEXT,
            name TEXT,
            area TEXT,
            industry TEXT,
            list_date TEXT
        )
        ''')
        
        # 创建K线数据表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS kline_data (
            id SERIAL PRIMARY KEY,
            ts_code TEXT,
            trade_date TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            pre_close REAL,
            change REAL,
            pct_chg REAL,
            vol REAL,
            amount REAL,
            freq TEXT,
            UNIQUE(ts_code, trade_date, freq)
        )
        ''')
        
        # 创建财务数据表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS financial_data (
            id SERIAL PRIMARY KEY,
            ts_code TEXT,
            year INTEGER,
            quarter INTEGER,
            data TEXT,
            UNIQUE(ts_code, year, quarter)
        )
        ''')
        
        # 创建指数数据表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS index_data (
            id SERIAL PRIMARY KEY,
            ts_code TEXT,
            trade_date TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            pre_close REAL,
            change REAL,
            pct_chg REAL,
            vol REAL,
            amount REAL,
            freq TEXT,
            UNIQUE(ts_code, trade_date, freq)
        )
        ''')
        
        conn.commit()
        conn.close()
        print("PostgreSQL 数据库表结构初始化完成")
    
    def save_stock_list(self, stocks: List[Dict[str, Any]]):
        """保存股票列表"""
        if not self.db_url:
            print("警告：未设置 DATABASE_URL，无法保存股票列表")
            return
        
        conn = psycopg2.connect(self.db_url)
        cursor = conn.cursor()
        
        try:
            for stock in stocks:
                cursor.execute('''
                INSERT INTO stock_list (ts_code, symbol, name, area, industry, list_date)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (ts_code) DO UPDATE SET
                    symbol = EXCLUDED.symbol,
                    name = EXCLUDED.name,
                    area = EXCLUDED.area,
                    industry = EXCLUDED.industry,
                    list_date = EXCLUDED.list_date
                ''', (stock.get('ts_code'), stock.get('symbol'), stock.get('name'), 
                      stock.get('area'), stock.get('industry'), stock.get('list_date')))
            
            conn.commit()
            print(f"成功保存 {len(stocks)} 条股票数据")
        except Exception as e:
            print(f"保存股票列表失败: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def save_kline_data(self, symbol: str, data: List[Dict[str, Any]], freq: str):
        """保存K线数据"""
        if not self.db_url:
            print("警告：未设置 DATABASE_URL，无法保存K线数据")
            return
        
        conn = psycopg2.connect(self.db_url)
        cursor = conn.cursor()
        
        try:
            count = 0
            for item in data:
                cursor.execute('''
                INSERT INTO kline_data (ts_code, trade_date, open, high, low, close, 
                pre_close, change, pct_chg, vol, amount, freq)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (ts_code, trade_date, freq) DO UPDATE SET
                    open = EXCLUDED.open,
                    high = EXCLUDED.high,
                    low = EXCLUDED.low,
                    close = EXCLUDED.close,
                    pre_close = EXCLUDED.pre_close,
                    change = EXCLUDED.change,
                    pct_chg = EXCLUDED.pct_chg,
                    vol = EXCLUDED.vol,
                    amount = EXCLUDED.amount
                ''', (symbol, item.get('trade_date'), item.get('open'), item.get('high'), 
                      item.get('low'), item.get('close'), item.get('pre_close'), 
                      item.get('change'), item.get('pct_chg'), item.get('vol'), 
                      item.get('amount'), freq))
                count += 1
            
            conn.commit()
            print(f"成功保存 {count} 条K线数据")
        except Exception as e:
            print(f"保存K线数据失败: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def save_financial_data(self, symbol: str, year: int, quarter: int, data: Dict[str, Any]):
        """保存财务数据"""
        if not self.db_url:
            print("警告：未设置 DATABASE_URL，无法保存财务数据")
            return
        
        conn = psycopg2.connect(self.db_url)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO financial_data (ts_code, year, quarter, data)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (ts_code, year, quarter) DO UPDATE SET
                data = EXCLUDED.data
            ''', (symbol, year, quarter, json.dumps(data)))
            
            conn.commit()
            print(f"成功保存 {symbol} {year}年Q{quarter} 财务数据")
        except Exception as e:
            print(f"保存财务数据失败: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def save_index_data(self, symbol: str, data: List[Dict[str, Any]], freq: str):
        """保存指数数据"""
        if not self.db_url:
            print("警告：未设置 DATABASE_URL，无法保存指数数据")
            return
        
        conn = psycopg2.connect(self.db_url)
        cursor = conn.cursor()
        
        try:
            count = 0
            for item in data:
                cursor.execute('''
                INSERT INTO index_data (ts_code, trade_date, open, high, low, close, 
                pre_close, change, pct_chg, vol, amount, freq)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (ts_code, trade_date, freq) DO UPDATE SET
                    open = EXCLUDED.open,
                    high = EXCLUDED.high,
                    low = EXCLUDED.low,
                    close = EXCLUDED.close,
                    pre_close = EXCLUDED.pre_close,
                    change = EXCLUDED.change,
                    pct_chg = EXCLUDED.pct_chg,
                    vol = EXCLUDED.vol,
                    amount = EXCLUDED.amount
                ''', (symbol, item.get('trade_date'), item.get('open'), item.get('high'), 
                      item.get('low'), item.get('close'), item.get('pre_close'), 
                      item.get('change'), item.get('pct_chg'), item.get('vol'), 
                      item.get('amount'), freq))
                count += 1
            
            conn.commit()
            print(f"成功保存 {count} 条指数数据")
        except Exception as e:
            print(f"保存指数数据失败: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_stock_list(self) -> List[Dict[str, Any]]:
        """获取股票列表"""
        if not self.db_url:
            print("警告：未设置 DATABASE_URL，无法获取股票列表")
            return []
        
        conn = psycopg2.connect(self.db_url)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT ts_code, symbol, name, area, industry, list_date FROM stock_list')
            rows = cursor.fetchall()
            
            stocks = []
            for row in rows:
                stocks.append({
                    'ts_code': row[0],
                    'symbol': row[1],
                    'name': row[2],
                    'area': row[3],
                    'industry': row[4],
                    'list_date': row[5]
                })
            
            return stocks
        except Exception as e:
            print(f"获取股票列表失败: {e}")
            return []
        finally:
            conn.close()
    
    def get_kline_data(self, symbol: str, start_date: str, end_date: str, freq: str) -> List[Dict[str, Any]]:
        """获取K线数据"""
        if not self.db_url:
            print("警告：未设置 DATABASE_URL，无法获取K线数据")
            return []
        
        conn = psycopg2.connect(self.db_url)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT trade_date, open, high, low, close, pre_close, change, pct_chg, vol, amount
            FROM kline_data
            WHERE ts_code = %s AND trade_date >= %s AND trade_date <= %s AND freq = %s
            ORDER BY trade_date
            ''', (symbol, start_date, end_date, freq))
            
            rows = cursor.fetchall()
            kline_data = []
            for row in rows:
                kline_data.append({
                    'trade_date': row[0],
                    'open': row[1],
                    'high': row[2],
                    'low': row[3],
                    'close': row[4],
                    'pre_close': row[5],
                    'change': row[6],
                    'pct_chg': row[7],
                    'vol': row[8],
                    'amount': row[9]
                })
            
            return kline_data
        except Exception as e:
            print(f"获取K线数据失败: {e}")
            return []
        finally:
            conn.close()
    
    def delete_stock(self, symbol: str) -> bool:
        """删除股票"""
        if not self.db_url:
            print("警告：未设置 DATABASE_URL，无法删除股票")
            return False
        
        conn = psycopg2.connect(self.db_url)
        cursor = conn.cursor()
        
        try:
            # 构建完整的ts_code
            if symbol.startswith('00') or symbol.startswith('30'):
                ts_code = f"{symbol}.SZ"
            elif symbol.startswith('60'):
                ts_code = f"{symbol}.SH"
            else:
                ts_code = symbol
            
            # 删除股票列表中的记录
            cursor.execute('DELETE FROM stock_list WHERE ts_code = %s OR symbol = %s', (ts_code, symbol))
            
            # 删除相关的K线数据
            cursor.execute('DELETE FROM kline_data WHERE ts_code = %s', (ts_code,))
            
            # 删除相关的财务数据
            cursor.execute('DELETE FROM financial_data WHERE ts_code = %s', (ts_code,))
            
            # 删除相关的指数数据
            cursor.execute('DELETE FROM index_data WHERE ts_code = %s', (ts_code,))
            
            conn.commit()
            print(f"成功删除股票 {symbol} 的所有数据")
            return True
        except Exception as e:
            print(f"删除股票数据失败: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()