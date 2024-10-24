import bcrypt
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
        print(f"Error: {htpasswd_file} already exists.")
    else:
        open(htpasswd_file, 'w').close()
        print(f"{htpasswd_file} created successfully.")

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def add_user(username, password, htpasswd_file):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    with open(htpasswd_file, 'a') as file:
        file.write(f"{username}:{hashed.decode('utf-8')}\n")
    print(f"User {username} added successfully.")
    print(f"Username: {username}")
    print(f"Password: {password}")

def change_user_password(username, new_password, htpasswd_file):
    try:
        with open(htpasswd_file, 'r') as file:
            lines = file.readlines()

        updated = False
        with open(htpasswd_file, 'w') as file:
            for line in lines:
                stored_user, stored_hash = line.strip().split(':', 1)
                if stored_user == username:
                    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                    file.write(f"{username}:{hashed.decode('utf-8')}\n")
                    updated = True
                else:
                    file.write(line)
        
        if not updated:
            print(f"User '{username}' not found.")
        else:
            print(f"Password for user '{username}' has been updated.")
            print(f"Username: {username}")
            print(f"New Password: {new_password}")

    except Exception as e:
        print(f"An error occurred: {e}")

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
            print(f"User '{username}' not found.")
        else:
            print(f"User '{username}' has been deleted.")

    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    htpasswd_file = get_htpasswd_file_path()

    while True:
        print("\nMenu:")
        print("1. Create htpasswd file")
        print("2. Add user")
        print("3. Change user password")
        print("4. Delete user")
        print("@. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            create_htpasswd_file(htpasswd_file)

        elif choice == '2':
            username = input("Enter username: ")
            password = generate_random_password()
            add_user(username, password, htpasswd_file)

        elif choice == '3':
            username = input("Enter username: ")
            if username_exists(username, htpasswd_file):
                new_password = generate_random_password()
                change_user_password(username, new_password, htpasswd_file)
            else:
                print(f"User '{username}' not found. Please try again.")

        elif choice == '4':
            username = input("Enter username: ")
            confirm_username = input("Confirm username: ")
            if username == confirm_username:
                delete_user(username, htpasswd_file)
            else:
                print("Usernames do not match.")

        elif choice == '@':
            print("Exiting program.")
            break

        else:
            print("Invalid option. Please try again.")

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
