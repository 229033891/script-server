#!/usr/bin/env python
import pandas as pd
from sqlalchemy import create_engine
from prettytable import PrettyTable

def print_message(message, success=True):
    """以绿色打印成功消息，以红色打印错误消息。"""
    color = '\033[32m' if success else '\033[91m'
    reset = '\033[0m'
    print(f"{color}{message}{reset}")

def display_top_rows(table_name, engine, num_rows=5):
    """从数据库表中检索并打印前几行数据，使用 PrettyTable 格式化输出。"""
    try:
        query = f"SELECT TOP {num_rows} ID, Item, Available as QTY FROM {table_name}"
        df = pd.read_sql(query, engine)

        # 创建 PrettyTable 对象
        table = PrettyTable()

        # 添加列名
        table.field_names = df.columns

        # 添加数据行
        for index, row in df.iterrows():
            table.add_row(row)

        # 设置每列居中对齐
        for column in table.field_names:
            table.align[column] = 'c'

        print_message(f"\n数据库表 {table_name} 的前 {num_rows} 行数据：", success=True)
        print(table)
    except Exception as e:
        print_message(f"检索数据失败: {e}", success=False)

def main():
    # 常量
    TABLE_NAME = 'TTL_Inventory_Report2023'

    # 数据库连接配置
    server = '192.168.10.201'
    database = 'oms'
    username = 'bt'
    password = 'Integrated@2019'
    connection_string = (
        'DRIVER={ODBC Driver 17 for SQL Server};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'UID={username};'
        f'PWD={password};'
    )

    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={connection_string}", pool_size=10, max_overflow=20)

    # 打印数据库表前5行数据
    display_top_rows(TABLE_NAME, engine)

if __name__ == "__main__":
    main()
