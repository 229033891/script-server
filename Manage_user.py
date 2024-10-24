import os
import random
import string
import threading

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

def find_script_server_dir(starting_dir):
    """从起始目录向上查找 script-server 目录"""
    current_dir = starting_dir
    while True:
        if os.path.basename(current_dir) == 'script-server':
            return current_dir
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:  # 已到达文件系统的根目录
            break
        current_dir = parent_dir
    return None

def get_htpasswd_file_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_server_dir = find_script_server_dir(script_dir)
    if script_server_dir is None:
        raise Exception("未找到 script-server 目录")
    
    htpasswd_dir = os.path.join(script_server_dir, 'conf')
    if not os.path.exists(htpasswd_dir):
        os.makedirs(htpasswd_dir)
    htpasswd_file = os.path.join(htpasswd_dir, '.htpasswd')
    return htpasswd_file

def create_htpasswd_file(htpasswd_file):
    if os.path.exists(htpasswd_file):
        print(f"\033[91m错误: {htpasswd_file} 已经存在。\033[0m")
    else:
        open(htpasswd_file, 'w').close()
        print(f"\033[92m{htpasswd_file} 创建成功。\033[0m")

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def add_user(username, password, htpasswd_file):
    with open(htpasswd_file, 'a') as file:
        file.write(f"{username}:{password}\n")
    print(f"\033[92m用户 {username} 添加成功。\033[0m")
    print(f"用户名: {username}")
    print(f"密码: {password}")

def change_user_password(username, new_password, htpasswd_file):
    try:
        with open(htpasswd_file, 'r') as file:
            lines = file.readlines()

        updated = False
        with open(htpasswd_file, 'w') as file:
            for line in lines:
                stored_user, stored_hash = line.strip().split(':', 1)
                if stored_user == username:
                    file.write(f"{username}:{new_password}\n")
                    updated = True
                else:
                    file.write(line)
        
        if not updated:
            print(f"\033[91m用户 '{username}' 未找到。\033[0m")
        else:
            print(f"\033[92m用户 '{username}' 的密码已更新。\033[0m")
            print(f"用户名: {username}")
            print(f"新密码: {new_password}")

    except Exception as e:
        print(f"\033[91m发生错误: {e}\033[0m")

def manual_change_user_password(username, htpasswd_file):
    while True:
        old_password = input_with_timeout("请输入旧密码: ", 60)
        if old_password == "@":
            return
        if not verify_user_password(username, old_password, htpasswd_file):
            print("\033[91m旧密码错误。请再试一次。\033[0m")
            continue
        while True:
            new_password = input_with_timeout("请输入新密码: ", 60)
            if new_password == "@":
                return
            confirm_password = input_with_timeout("请再次输入新密码: ", 60)
            if confirm_password == "@":
                return
                
            if new_password != confirm_password:
                print("\033[91m两次输入的密码不匹配。请再试一次。\033[0m")
            elif len(new_password) <= 5:
                print("\033[91m密码长度必须大于5个字符。请再试一次。\033[0m")
            else:
                change_user_password(username, new_password, htpasswd_file)
                return

def verify_user_password(username, password, htpasswd_file):
    try:
        with open(htpasswd_file, 'r') as file:
            lines = file.readlines()

        for line in lines:
            stored_user, stored_password = line.strip().split(':', 1)
            if stored_user == username and stored_password == password:
                return True
        return False
    except Exception as e:
        print(f"\033[91m发生错误: {e}\033[0m")
        return False

def main():
    htpasswd_file = get_htpasswd_file_path()

    while True:
        print("\n菜单:")
        print("1. 生成文件(勿动)")
        print("2. 添加用户")
        print("3. 自动更改用户密码")
        print("4. 手动更改用户密码")
        print("@. 退出")
        choice = input_with_timeout("请选择一个选项: ", 60)

        if choice is None:
            print("\033[92m退出程序\033[0m")
            os._exit(1)
        if choice == '1':
            create_htpasswd_file(htpasswd_file)

        elif choice == '2':
            username = input_with_timeout("请输入用户名: ", 60)
            if username is None:
                os._exit(1)
            password = generate_random_password()
            add_user(username, password, htpasswd_file)

        elif choice == '3':
            username = input_with_timeout("请输入用户名: ", 60)
            if username is None:
                os._exit(1)
            if username_exists(username, htpasswd_file):
                auto_change_user_password(username, htpasswd_file)
            else:
                print(f"\033[91m用户 '{username}' 未找到。请再试一次。\033[0m")

        elif choice == '4':
            username = input_with_timeout("请输入用户名: ", 60)
            if username is None:
                os._exit(1)
            if username_exists(username, htpasswd_file):
                manual_change_user_password(username, htpasswd_file)
            else:
                print(f"\033[91m用户 '{username}' 未找到。请再试一次。\033[0m")

        elif choice == '@':
            print("退出程序。")
            break

        else:
            print("\033[91m无效选项。请再试一次。\033[0m")

def username_exists(username, htpasswd_file):
    if not os.path.exists(htpasswd_file):
        return False
    
    with open(htpasswd_file, 'r') as file:
        lines = file.readlines()
        
    for line in lines:
        stored_user, _ = line.strip().split(':', 1)
        if stored_user == username:
            return True
    return False

if __name__ == "__main__":
    main()
