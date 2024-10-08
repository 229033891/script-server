import pyodbc
import datetime
import time

def get_current_time():
    """获取当前时间的字符串表示"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def connect_to_db():
    """连接到数据库"""
    try:
        connection = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=192.168.10.201;'
            'DATABASE=scan;'
            'UID=bt;'
            'PWD=Integrated@2019;'
        )
        return connection
    except Exception as e:
        handle_error("!★★★数据库连接失败", e)
        return None

def load_shipments_from_db(connection):
    """从数据库加载出库单号"""
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT shipment_id FROM shipment_header")
        return set(row.shipment_id.lower() for row in cursor.fetchall())
    except Exception as e:
        handle_error("!★★★加载数据库记录失败", e)
        return set()

def load_no_exists_in_db(load_no, connection):
    """检查装载号是否存在于数据库中"""
    return execute_query_with_single_result("SELECT 1 FROM shipment_header WHERE load_no = ?", (load_no,), connection)

def load_no_all_scanned(load_no, connection):
    """检查装载号是否全部扫描完成"""
    return execute_query_with_multiple_results(
        "SELECT total_qty FROM shipment_header WHERE load_no = ?", 
        (load_no,), 
        connection, 
        lambda rows: all(row.total_qty == 0 for row in rows)
    )

def insert_shipment(shipment_id, load_no, connection):
    """插入扫描记录到数据库"""
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT total_qty FROM shipment_header WHERE LOWER(shipment_id) = ? AND load_no = ?", (shipment_id.lower(), load_no))
        result = cursor.fetchone()

        if result is None:
            handle_error("!★★★错误! 出库单号不存在")
        elif result[0] == 0:
            handle_error("!★★★错误! 请勿重复扫描")
        else:
            current_time = get_current_time()
            cursor.execute(
                "UPDATE shipment_header SET total_qty = total_qty - 1, date_time = ? WHERE LOWER(shipment_id) = ? AND load_no = ?",
                (current_time, shipment_id.lower(), load_no)
            )
            connection.commit()

            cursor.execute(
                "INSERT INTO shipping_container (shipment_id, load_no, date_time) VALUES (?, ?, ?)",
                (shipment_id.upper(), load_no, current_time)
            )
            connection.commit()

            cursor.execute("SELECT COUNT(*) FROM shipping_container WHERE load_no = ?", (load_no,))
            total_scanned = cursor.fetchone()[0]
            print_message(f"{'-' * 50}\n{total_scanned}箱")

    except Exception as e:
        connection.rollback()
        handle_error("!★★★扫描失败，请重新扫描", e)

def execute_query_with_single_result(query, params, connection):
    """执行查询并返回单个结果"""
    try:
        cursor = connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchone() is not None
    except Exception as e:
        handle_error("!★★★数据库查询失败", e)
        return False

def execute_query_with_multiple_results(query, params, connection, processor):
    """执行查询并处理多个结果"""
    try:
        cursor = connection.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return processor(rows)
    except Exception as e:
        handle_error("!★★★数据库查询失败", e)
        return False

def handle_error(message, exception=None):
    """处理错误并输出错误信息"""
    timestamp_message = f"{message}: {exception} [{get_current_time()}]" if exception else f"{message} [{get_current_time()}]"
    print(timestamp_message)

def print_message(message):
    """输出消息并带有时间戳"""
    timestamp_message = f"{message} [{get_current_time()}]"
    print(timestamp_message)

def prompt_for_input(prompt, validation_func=None, error_message=None):
    """通用的输入提示函数，带有可选的验证功能"""
    while True:
        user_input = input(prompt).strip()
        if user_input == '@':
            return user_input
        user_input = user_input.strip()  # 去除前后空格
        if validation_func and not validation_func(user_input):
            if error_message:
                handle_error(error_message)
            continue
        return user_input

def print_and_speak_exit_message():
    """打印和播放退出消息"""
    for i in range(3, 0, -1):
        message = f"{i}秒后退出程序..."
        print_message(message)
        time.sleep(1)
    exit()

def main():
    """主函数"""
    connection = connect_to_db()
    if not connection:
        return

    shipment_ids = load_shipments_from_db(connection)

    if not shipment_ids:
        handle_error("!★★★数据库中没有记录，5秒后退出程序...")
        time.sleep(5)
        return

    while True:
        load_no = prompt_for_input("请输入装载号（@退出）：", lambda x: len(x) >= 3, "!★★★错误! 装载号长度必须大于2")
        if load_no == '@':
            print_and_speak_exit_message()
            return

        if not load_no_exists_in_db(load_no, connection):
            handle_error("!★★★错误! 装载号不存在")
            continue

        if load_no_all_scanned(load_no, connection):
            handle_error("!★★★错误! 装载号已扫描完成")
            continue

        print_message("输入成功，请继续")

        while True:
            shipment_id = prompt_for_input("请输入单号（@返回）：", lambda x: len(x) >= 6, "!★★★错误! 单号长度必须大于5")
            if shipment_id == '@':
                break

            shipment_id = shipment_id.lower()

            if shipment_id in shipment_ids:
                insert_shipment(shipment_id, load_no, connection)
            else:
                handle_error("!★★★错误! 出库单号不存在")

if __name__ == "__main__":
    main()
