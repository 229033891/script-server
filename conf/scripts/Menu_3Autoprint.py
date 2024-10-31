import os
import subprocess
import datetime
import pyttsx3
import wmi
import threading
from concurrent.futures import ThreadPoolExecutor

# 初始化 pyttsx3
engine = pyttsx3.init('sapi5')
engine.setProperty('rate', engine.getProperty('rate') - 50)

def speak_message(message, enable_speech_output):
    if enable_speech_output:
        engine.say(message)
        engine.runAndWait()

def print_message(message, success=True):
    color_code = "\033[92m" if success else "\033[91m"
    reset_code = "\033[0m"
    print(f"{color_code}{message}{reset_code}")

def is_printer_online(printer_name, enable_speech_output):
    try:
        c = wmi.WMI()
        printers = c.Win32_Printer(Name=printer_name)
        if not printers:
            print_message(f"错误! 打印机 '{printer_name}' 不存在", success=False)
            speak_message(f"打印机 {printer_name} 不存在", enable_speech_output)
            return False

        printer = printers[0]
        if printer.WorkOffline:
            print_message(f"打印机 '{printer_name}' 离线", success=False)
            speak_message(f"打印机 {printer_name} 离线", enable_speech_output)
            return False
        else:
            print_message(f"打印机 '{printer_name}' 在线", success=True)
            speak_message(f"打印机 {printer_name} 在线", enable_speech_output)
            return True
    except Exception as e:
        print_message(f"错误! 检查打印机状态失败: {str(e)}", success=False)
        speak_message("有错误", enable_speech_output)
        return False

def unique_filename(path, filename):
    base, extension = os.path.splitext(filename)
    counter = 1
    new_filename = f"Printed_{base}{extension}"
    while os.path.exists(os.path.join(path, new_filename)):
        new_filename = f"Printed_{base}_{counter}{extension}"
        counter += 1
    return new_filename

def auto_print(printer_name, folder_path, order_number, enable_speech_output):
    if len(order_number) < 5:
        error_message = "错误: 型号长度须大于5。"
        print_message(error_message, success=False)
        speak_message("型号长度须大于5", enable_speech_output)
        return error_message

    pdf_file = next((f for f in os.listdir(folder_path) if order_number in f and f.endswith('.pdf') and not f.startswith('Printed_')), None)
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if pdf_file:
        file_path = os.path.join(folder_path, pdf_file)
        new_file_name = unique_filename(folder_path, pdf_file)
        new_file_path = os.path.join(folder_path, new_file_name)
        
        try:
            os.rename(file_path, new_file_path)
            script_directory = os.path.dirname(os.path.abspath(__file__))
            pdf_to_printer_path = os.path.join(script_directory, 'PDFtoPrinter.exe')

            subprocess.run([pdf_to_printer_path, new_file_path, printer_name], check=True)
            success_message = f"成功: '{pdf_file}' 重命名并打印。({current_time})"
            print_message(success_message, success=True)
            return success_message
        except Exception as e:
            error_message = f"错误: 文件操作失败。({str(e)})"
            print_message(error_message, success=False)
            speak_message("文件操作失败", enable_speech_output)
            return error_message
    else:
        error_message = f"错误: 文件 '{order_number}' 不存在。({current_time})"
        print_message(error_message, success=False)
        speak_message("文件不存在", enable_speech_output)
        return error_message

def input_with_timeout(prompt, timeout):
    result = [None]

    def target():
        result[0] = input(prompt)

    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        return None
    return result[0]

def main():
    printer_name = 'T-4503E'
    folder_path = r"D:\py\AutoPrint\output"
    enable_speech_output = False

    if not is_printer_online(printer_name, enable_speech_output):
        print_message(f"错误: 打印机 '{printer_name}' 不在线或无法通信。", success=False)
        return

    with ThreadPoolExecutor(max_workers=5) as executor:
        while True:
            order_number = input_with_timeout("请输入型号（@退出）：", 600)
            if order_number is None:
                print_message("输入超时，程序退出。", success=False)
                os._exit(0)

            if order_number == '@':
                print("退出打印任务")
                os._exit(0)

            future = executor.submit(auto_print, printer_name, folder_path, order_number, enable_speech_output)
            future.result()  # Wait for the current task to complete

if __name__ == "__main__":
    main()
