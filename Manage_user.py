import os
import random
import string

def get_htpasswd_file_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    htpasswd_dir = os.path.join(script_dir, 'conf')
    if not os.path.exists(htpasswd_dir):
        os.makedirs(htpasswd_dir)
    htpasswd_file = os.path.join(htpasswd_dir, '.htpasswd')
    return htpasswd_file

def create_htpasswd_file(htpasswd_file):
    if os.path.exists(htpasswd_file):
        print(f"错误: {htpasswd_file} 已经存在。")
    else:
        open(htpasswd_file, 'w').close()
        print(f"{htpasswd_file} 创建成功。")

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def add_user(username, password, htpasswd_file):
    # 使用纯文本形式存储密码
    with open(htpasswd_file, 'a') as file:
        file.write(f"{username}:{password}\n")
    print(f"用户 {username} 添加成功。")
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
            print(f"用户 '{username}' 未找到。")
        else:
            print(f"用户 '{username}' 的密码已更新。")
            print(f"用户名: {username}")
            print(f"新密码: {new_password}")

    except Exception as e:
        print(f"发生错误: {e}")

def manual_change_user_password(username, htpasswd_file):
    while True:
        new_password = input("请输入新密码: ")
        confirm_password = input("请再次输入新密码: ")
        
        if new_password != confirm_password:
            print("两次输入的密码不匹配。请再试一次。")
        elif len(new_password) <= 5:
            print("密码长度必须大于5个字符。请再试一次。")
        else:
            change_user_password(username, new_password, htpasswd_file)
            break

def delete_user(username, htpasswd_file):
    try:
        with open(htpasswd_file, 'r') as file:
            lines = file.readlines()

        deleted = False
        with open(htpasswd_file, 'w') as file:
            for line in lines:
                stored_user, _ = line.strip().split(':', 1)
                if stored_user != username:
                    file.write(line)
                else:
                    deleted = True
        
        if not deleted:
            print(f"用户 '{username}' 未找到。")
        else:
            print(f"用户 '{username}' 已被删除。")

    except Exception as e:
        print(f"发生错误: {e}")

def main():
    htpasswd_file = get_htpasswd_file_path()

    while True:
        print("\n菜单:")
        print("1. 创建 htpasswd 文件")
        print("2. 添加用户")
        print("3. 自动更改用户密码")
        print("4. 手动更改用户密码")
        print("5. 删除用户")
        print("@. 退出")
        choice = input("请选择一个选项: ")

        if choice == '1':
            create_htpasswd_file(htpasswd_file)

        elif choice == '2':
            username = input("请输入用户名: ")
            password = generate_random_password()
            add_user(username, password, htpasswd_file)

        elif choice == '3':
            username = input("请输入用户名: ")
            if username_exists(username, htpasswd_file):
                new_password = generate_random_password()
                change_user_password(username, new_password, htpasswd_file)
            else:
                print(f"用户 '{username}' 未找到。请再试一次。")

        elif choice == '4':
            username = input("请输入用户名: ")
            if username_exists(username, htpasswd_file):
                manual_change_user_password(username, htpasswd_file)
            else:
                print(f"用户 '{username}' 未找到。请再试一次。")

        elif choice == '5':
            username = input("请输入用户名: ")
            confirm_username = input("请确认用户名: ")
            if username == confirm_username:
                delete_user(username, htpasswd_file)
            else:
                print("两次输入的用户名不匹配。")

        elif choice == '@':
            print("退出程序。")
            break

        else:
            print("无效选项。请再试一次。")

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
