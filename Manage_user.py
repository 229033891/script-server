import os
import random
import string
import threading

def input_with_timeout(prompt, timeout):
    result = [None]
    def target():
        result[0] = input(prompt)
    
    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        print("\033[91m超时! 程序将自动退出。\033[0m")
        os._exit(1)
    return result[0]

def find_script_server_dir(starting_dir):
    while True:
        if os.path.basename(starting_dir) == 'script-server':
            return starting_dir
        parent_dir = os.path.dirname(starting_dir)
        if parent_dir == starting_dir:
            break
        starting_dir = parent_dir
    return None

def get_htpasswd_file_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_server_dir = find_script_server_dir(script_dir)
    if not script_server_dir:
        raise Exception("未找到 script-server 目录")
    
    htpasswd_dir = os.path.join(script_server_dir, 'conf')
    os.makedirs(htpasswd_dir, exist_ok=True)
    return os.path.join(htpasswd_dir, '.htpasswd')

def generate_random_password(length=12):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def modify_user_file(username, htpasswd_file, new_password=None):
    updated = False
    try:
        with open(htpasswd_file, 'r') as file:
            lines = file.readlines()

        with open(htpasswd_file, 'w') as file:
            for line in lines:
                stored_user, stored_password = line.strip().split(':', 1)
                if stored_user == username:
                    if new_password:
                        file.write(f"{username}:{new_password}\n")
                        updated = True
                else:
                    file.write(line)

        if new_password and updated:
            print(f"\033[92m用户 '{username}' 的密码已更新。\033[0m")
            print(f"新密码: {new_password}")
        elif not updated:
            print(f"\033[91m用户 '{username}' 未找到。\033[0m")

    except Exception as e:
        print(f"\033[91m发生错误: {e}\033[0m")

def add_user(username, password, htpasswd_file):
    with open(htpasswd_file, 'a') as file:
        file.write(f"{username}:{password}\n")
    print(f"\033[92m用户 {username} 添加成功。\033[0m")
    print(f"用户名: {username}\n密码: {password}")

def user_exists(username, htpasswd_file):
    try:
        with open(htpasswd_file, 'r') as file:
            for line in file:
                stored_user, _ = line.strip().split(':', 1)
                if stored_user == username:
                    return True
        return False
    except Exception as e:
        print(f"\033[91m发生错误: {e}\033[0m")
        return False

def verify_user_password(username, password, htpasswd_file):
    try:
        with open(htpasswd_file, 'r') as file:
            for line in file:
                stored_user, stored_password = line.strip().split(':', 1)
                if stored_user == username and stored_password == password:
                    return True
        return False
    except Exception as e:
        print(f"\033[91m发生错误: {e}\033[0m")
        return False

def change_user_password(username, htpasswd_file, manual=True):
    if manual:
        while True:
            new_password = input_with_timeout("请输入新密码: ", 60)
            if new_password == "@":
                return
            if new_password == "@" or input_with_timeout("请再次输入新密码: ", 60) != new_password:
                print("\033[91m密码错误或不匹配。\033[0m")
                continue
            if len(new_password) <= 5:
                print("\033[91m密码长度必须大于5个字符。\033[0m")
                continue
            break
    else:
        new_password = generate_random_password()

    modify_user_file(username, htpasswd_file, new_password)

def main():
    htpasswd_file = get_htpasswd_file_path()

    while True:
        print("\n菜单:")
        print("1. 初始密码文件(勿动)")
        print("2. 添加用户")
        print("3. 自动更改密码")
        print("4. 手动更改密码")
        print("@. 退出")
        choice = input_with_timeout("请选择一个选项: ", 60)

        if choice == '1':
            if not os.path.exists(htpasswd_file):
                open(htpasswd_file, 'w').close()
                print(f"\033[92m{htpasswd_file} 创建成功。\033[0m")
            else:
                print(f"\033[91m错误: {htpasswd_file} 已经存在。\033[0m")

        elif choice == '2':
            username = input_with_timeout("请输入用户名: ", 60)
            if username:
                add_user(username, generate_random_password(), htpasswd_file)

        elif choice in ['3', '4']:
            while True:
                username = input_with_timeout("请输入用户名: ", 60)
                if username == "@":
                    break
                if user_exists(username, htpasswd_file):
                    password = input_with_timeout("请输入密码: ", 60)
                    if password == "@":
                        break
                    if verify_user_password(username, password, htpasswd_file):
                        change_user_password(username, htpasswd_file, manual=(choice == '4'))
                        break
                    else:
                        print("\033[91m密码错误。请重试。\033[0m")
                else:
                    print("\033[91m用户不存在。请重试。\033[0m")

        elif choice == '@':
            print("退出程序。")
            break

        else:
            print("\033[91m无效选项。请再试一次。\033[0m")

if __name__ == "__main__":
    main()
