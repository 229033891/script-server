import subprocess
import sys
import os
import threading
import hashlib

# 模拟用户凭证的哈希值
USER_CREDENTIALS = {
    "user1": hashlib.sha256("password1".encode()).hexdigest(),
    "user2": hashlib.sha256("password2".encode()).hexdigest()
}

class TimeoutException(Exception):
    pass

def input_with_timeout(prompt, timeout):
    """带超时的输入"""
    result = [None]
    def target():
        result[0] = input(prompt)
    
    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        print("\033[91m超时! 程序将自动退出。\033[0m")
        os._exit(1)  # 超时立即退出程序
    return result[0]

def clear_console():
    """清除控制台"""
    if os.name == 'nt':  # 如果是 Windows 系统
        os.system('cls')
    else:  # 对于 Unix/Linux/Mac 系统
        os.system('clear')

def authenticate_user():
    """用户登录验证"""
    print("请输入用户名和密码登录系统!")
    while True:
        username = input_with_timeout("用户名: ", 30)
        if username is None:
            os._exit(1)
        if username == '@':
            return False
        if username not in USER_CREDENTIALS:
            print("\033[91m用户名不存在，请重新输入。\033[0m")
            continue

        while True:
            password = input_with_timeout("密码: ", 30)
            if password is None:
                os._exit(1)
            if password == '@':
                break
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            if USER_CREDENTIALS.get(username) == hashed_password:
                clear_console()
                print("\033[92m登录成功!\033[0m")
                return True
            print("\033[91m密码不正确，请重新输入。\033[0m")

def execute_script(script_name):
    """执行指定的脚本"""
    try:
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script_name)
        subprocess.run([sys.executable, script_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\033[91m错误! 无法调用 {script_name}: {str(e)}\033[0m")

def main_menu():
    """显示主菜单并处理用户选择"""
    actions = {
        '1': 'Menu_1SplitPDF.py',
        '2': 'Menu_2Autoprint.py',
        '3': 'Menu_3Autoprint.py'
    }

    while True:
        print("\n请选择操作:")
        print("1. 拆分PDF文件")
        print("2. 打印文件")
        print("3. 打印文件(PDFtoPrinter)")
        print("@. 退出")

        choice = input_with_timeout("请输入对应的编号: ", 30)
        if choice is None:
            print("\033[92m退出程序\033[0m")
            os._exit(1)
        if choice == '@':
            print("\033[92m退出程序\033[0m")
            break
        if choice in actions:
            execute_script(actions[choice])
        else:
            print("\033[91m无效的输入，请重新输入。\033[0m")

def main():
    if not authenticate_user():
        print("\033[92m正在退出程序...\033[0m")
        os._exit(1)

    main_menu()

if __name__ == "__main__":
    main()
