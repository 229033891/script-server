import os
import subprocess
import datetime
import time

def check_printer_exists(printer_name):
    try:
        result = subprocess.run(['wmic', 'printer', 'get', 'name'], capture_output=True, text=True, check=True)
        printer_list = result.stdout.splitlines()
        return any(printer_name in printer for printer in printer_list)
    except subprocess.CalledProcessError as e:
        print(f"!★★★错误! 检查打印机失败: {str(e)}")
        return False

def print_pdf(file_path, printer_name, sumatra_path):
    try:
        command = [
            sumatra_path,
            '-print-to',
            printer_name,
            '-print-settings',
            'auto',
            file_path
        ]
        subprocess.run(command, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"!★★★错误! 打印失败: {str(e)}")
        return False

def rename_file(file_path):
    base_name = os.path.basename(file_path)
    new_base_name = f"Printed_{base_name}"
    new_file_path = os.path.join(os.path.dirname(file_path), new_base_name)
    
    try:
        os.rename(file_path, new_file_path)
        return new_file_path
    except Exception as e:
        print(f"!★★★错误! 文件重命名失败: {str(e)}")
        return None

def create_folder_if_not_exists(folder_path):
    try:
        os.makedirs(folder_path, exist_ok=True)
    except Exception as e:
        raise RuntimeError(f"!★★★错误! 创建文件夹 '{folder_path}' 失败: {str(e)}")

def main():
    printer_name = 'CL421D'
    script_dir = r"D:\py\AutoPrint"
    folder_path = os.path.join(script_dir, 'output')
    sumatra_exe_path = r"C:\Program Files\SumatraPDF\SumatraPDF.exe"

    if not check_printer_exists(printer_name):
        print(f"!★★★错误! 打印机 '{printer_name}' 不存在，请检查打印机是否正确后重新运行程序。")
        time.sleep(10)
        return

    try:
        create_folder_if_not_exists(folder_path)
    except RuntimeError as e:
        print(str(e))
        return

    while True:
        order_number = input("请输入型号（@退出）：")
        
        if order_number == '@':
            print("退出程序")
            break
        
        if len(order_number) < 10:
            print("!★★★错误! 长度必须大于10。")
            continue

        pdf_file = next((f for f in os.listdir(folder_path)
                         if order_number.lower() in f.lower() and f.lower().endswith('.pdf') and not f.lower().startswith('printed')), None)

        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if pdf_file:
            file_path = os.path.join(folder_path, pdf_file)
            new_file_path = rename_file(file_path)
            if new_file_path and print_pdf(new_file_path, printer_name, sumatra_exe_path):
                print(f"{pdf_file} 已重命名并打印成功。", current_time)
            else:
                print(f"!★★★错误! {pdf_file} 打印失败或重命名失败。", current_time)
        else:
            print(f"!★★★错误! 文件 {order_number} 不存在或已打印过，请重新输入。", current_time)

if __name__ == '__main__':
    main()
