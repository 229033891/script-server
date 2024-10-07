import os
import subprocess
import datetime
import pyttsx3

engine = pyttsx3.init('sapi5')

# 调整语速
rate = engine.getProperty('rate')
engine.setProperty('rate', rate - 50)

def speak_message(message):
    engine.say(message)
    engine.runAndWait()

def check_printer_exists(printer_name):
    try:
        result = subprocess.run(['wmic', 'printer', 'get', 'name'], capture_output=True, text=True, check=True)
        printer_list = result.stdout.splitlines()
        return any(printer_name in printer for printer in printer_list)
    except subprocess.CalledProcessError as e:
        error_message = f"错误! 检查打印机失败: {str(e)}"
        print(error_message)
        speak_message("有错误")
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
        print(f"打印成功：{file_path}")
        
    except subprocess.CalledProcessError as e:
        error_message = f"错误! 打印失败: {str(e)}"
        print(error_message)
        speak_message("有错误")

printer_name = 'CL421D'
folder_path = r"D:\AutoPrint\output"
sumatra_exe_path = r"C:\Program Files\SumatraPDF\SumatraPDF.exe"

# 检查打印机是否存在
if not check_printer_exists(printer_name):
    print(f"错误! 打印机 '{printer_name}' 不存在，请检查打印机名称是否正确。")
    speak_message(f"打印机 {printer_name} 不存在，请检查打印机名称")
else:
    while True:
        order_number = input("请输入型号（@退出）：")
        
        if order_number == '@':
            print("退出程序")
            break
        
        if len(order_number) < 10:
            print("错误! 长度必须大于10。")
            speak_message("有错误")
            continue

        pdf_file = next((f for f in os.listdir(folder_path)
                         if order_number in f and f.endswith('.pdf') and not f.startswith('Printed_')), None)

        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if pdf_file:
            file_path = os.path.join(folder_path, pdf_file)
            new_file_path = os.path.join(folder_path, f"Printed_{pdf_file}")
            
            try:
                os.rename(file_path, new_file_path)
                print_pdf(new_file_path, printer_name, sumatra_exe_path)
                print(f"{pdf_file} 已重命名为 {os.path.basename(new_file_path)} 并打印成功。", current_time)
            except Exception as e:
                error_message = f"错误! 文件重命名或打印失败: {str(e)}"
                print(error_message)
                speak_message("有错误")
        else:
            print(f"错误! 文件 {order_number} 不存在，请重新输入.", current_time)
            speak_message("有错误")
