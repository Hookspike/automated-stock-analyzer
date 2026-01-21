# 修复股票数据，确保所有股票都有正确的symbol字段
import sqlite3

# 连接数据库
db_path = 'stock_data.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("开始检查股票数据...")

# 获取所有股票
cursor.execute('SELECT ts_code, symbol, name FROM stock_list')
stocks = cursor.fetchall()

print(f"找到 {len(stocks)} 只股票")

# 修复每只股票的symbol字段
fixed_count = 0
for stock in stocks:
    ts_code, symbol, name = stock
    print(f"\n股票: {name}, ts_code: {ts_code}, 当前symbol: {symbol}")
    
    # 检查symbol是否为空或无效
    if not symbol or symbol.strip() == '':
        # 从ts_code中提取symbol（6位数字）
        new_symbol = ts_code.split('.')[0]
        print(f"修复symbol: {symbol} -> {new_symbol}")
        
        # 更新数据库
        cursor.execute('UPDATE stock_list SET symbol = ? WHERE ts_code = ?', (new_symbol, ts_code))
        fixed_count += 1
    else:
        print("symbol有效，无需修复")

# 提交更改
conn.commit()
print(f"\n修复完成，共修复了 {fixed_count} 只股票")

# 关闭连接
conn.close()
