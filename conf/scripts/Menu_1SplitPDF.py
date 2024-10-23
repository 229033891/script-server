import fitz
import os
import re
import time
from datetime import datetime
import ctypes

def ensure_folder_exists(folder_path):
    """确保文件夹存在，如果不存在则创建它。"""
    try:
        os.makedirs(folder_path, exist_ok=True)
        print_message(f"创建文件夹 '{folder_path}' 成功。", success=True)
    except Exception as e:
        print_message(f"错误! 创建文件夹 '{folder_path}' 失败: {str(e)}", success=False)

def create_unique_filename(base_name, suffix, directory):
    """创建一个唯一的文件名，如果文件名冲突则附加一个计数器。"""
    count = 1
    new_name = f"{base_name}_{suffix}.pdf"
    while os.path.exists(os.path.join(directory, new_name)):
        new_name = f"{base_name}_{suffix}_{count}.pdf"
        count += 1
    return new_name

def adjust_console_window():
    """调整控制台窗口位置和大小"""
    user32 = ctypes.windll.user32
    screen_width, screen_height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    window_width, window_height = int(screen_width * 0.5), int(screen_height * 0.9)
    window_x, window_y = screen_width - window_width - 20, 20
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    SWP_NOZORDER = 0x0004
    user32.SetWindowPos(hwnd, None, window_x, window_y, window_width, window_height, SWP_NOZORDER)

def print_message(message, success=True):
    """打印消息，成功的用绿色，错误的用红色"""
    color_code = "\033[92m" if success else "\033[91m"  # 绿色: 92, 红色: 91
    reset_code = "\033[0m"
    print(f"{color_code}{message}{reset_code}")

def process_pdfs(input_folder, output_folder, txt_filename):
    """处理输入文件夹中的所有 PDF 文件，将它们拆分并重命名保存到输出文件夹。"""
    pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]

    if not pdf_files:
        print_message("错误! 输入文件夹中没有找到 PDF 文件。", success=False)
        return

    total_generated_files = 0

    with open(txt_filename, 'w', encoding='utf-8') as txt_file:
        for pdf_file in pdf_files:
            full_path = os.path.join(input_folder, pdf_file)
            try:
                doc = fitz.open(full_path)
            except Exception as e:
                print_message(f"错误! 无法打开文件 {pdf_file}: {str(e)}", success=False)
                continue
            
            for page_num, page in enumerate(doc.pages()):
                try:
                    output_filename = os.path.join(output_folder, f'{os.path.splitext(pdf_file)[0]}_page{page_num + 1}.pdf')
                    new_doc = fitz.open()
                    new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
                    new_doc.save(output_filename)
                    new_doc.close()

                    text = page.get_text("text")
                    cleaned_text = re.sub(r'[^a-zA-Z0-9._-]', '', text)[:100]
                    cleaned_text = cleaned_text.strip() or "empty"
                    new_filename = create_unique_filename(cleaned_text, f'page{page_num + 1}', output_folder)
                    final_path = os.path.join(output_folder, new_filename)
                    os.rename(output_filename, final_path)
                    print_message(f"页面 {page_num + 1} 已保存为 {new_filename}", success=True)

                    txt_file.write(text)
                    txt_file.write("\n" + "-" * 50 + "\n")

                    total_generated_files += 1
                
                except Exception as e:
                    print_message(f"错误! 处理文件 {pdf_file} 的页面 {page_num + 1} 时出错: {str(e)}", success=False)
            
            doc.close()
    
    print_message(f"总共生成了 {total_generated_files} 个新的 PDF 文件。", success=True)
    print_message(f"生成的 PDF 文件保存在目录: {output_folder}", success=True)

def main():
    """adjust_console_window()"""
    base_directory = r"D:\py\AutoPrint"
    input_folder = os.path.join(base_directory, 'input')
    output_folder = os.path.join(base_directory, 'output')

    ensure_folder_exists(output_folder)

    timestamp = datetime.now().strftime('%y%m%d%H%M%S')
    txt_filename = os.path.join(output_folder, f"{timestamp}.txt")

    process_pdfs(input_folder, output_folder, txt_filename)
    print_message("拆分并重命名完成", success=True)

if __name__ == '__main__':
    main()
    print_message("程序将在3秒后返回主菜单...", success=True)
    for remaining in range(3, 0, -1):
        print(f"\033[92m{remaining}秒后返回主菜单...\033[0m", end="\r")
        time.sleep(1)
    print_message("返回主菜单" + " " * 20, success=True)  # 清除倒计时行的内容
