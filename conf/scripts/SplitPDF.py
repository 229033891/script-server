import fitz
import os
import re
import time

def ensure_folder_exists(folder_path):
    """确保文件夹存在，如果不存在则创建它。"""
    try:
        os.makedirs(folder_path, exist_ok=True)
    except Exception as e:
        raise RuntimeError(f"!★★错误! 创建文件夹 '{folder_path}' 失败: {str(e)}")

def create_unique_filename(base_name, suffix, directory):
    """创建一个唯一的文件名，如果文件名冲突则附加一个计数器。"""
    count = 1
    new_name = f"{base_name}_{suffix}.pdf"
    while os.path.exists(os.path.join(directory, new_name)):
        new_name = f"{base_name}_{suffix}_{count}.pdf"
        count += 1
    return new_name

def process_pdfs(input_folder, output_folder):
    """处理输入文件夹中的所有 PDF 文件，将它们拆分并重命名保存到输出文件夹。"""
    # 获取输入文件夹中的所有 PDF 文件
    pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]

    if not pdf_files:
        print("!★★错误! 输入文件夹中没有找到 PDF 文件。")
        return

    total_generated_files = 0

    # 循环处理每个PDF文件
    for pdf_file in pdf_files:
        full_path = os.path.join(input_folder, pdf_file)
        try:
            doc = fitz.open(full_path)
        except Exception as e:
            print(f"!★★错误! 无法打开文件 {pdf_file}: {str(e)}")
            continue
        
        # 对每一页进行拆分
        for page_num, page in enumerate(doc.pages()):
            try:
                output_filename = os.path.join(output_folder, f'{os.path.splitext(pdf_file)[0]}_page{page_num + 1}.pdf')
                new_doc = fitz.open()
                new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
                new_doc.save(output_filename)
                new_doc.close()
                
                # 获取当前页面的文本内容
                text = page.get_text("text")
                # 清理文本，仅保留字母数字._-
                cleaned_text = re.sub(r'[^a-zA-Z0-9._-]', '', text)[:100]  # 限制长度，避免文件名过长
                cleaned_text = cleaned_text.strip() or "empty"  # 防止空白文件名
                new_filename = create_unique_filename(cleaned_text, f'page{page_num + 1}', output_folder)
                final_path = os.path.join(output_folder, new_filename)
                os.rename(output_filename, final_path)
                print(f"页面 {page_num + 1} 已保存为 {new_filename}")
                
                total_generated_files += 1
            
            except Exception as e:
                print(f"!★★错误! 处理文件 {pdf_file} 的页面 {page_num + 1} 时出错: {str(e)}")
        
        doc.close()
    
    # 打印生成的文件数量和输出文件夹路径
    print(f"总共生成了 {total_generated_files} 个新的 PDF 文件。")
    print(f"生成的 PDF 文件保存在目录: {output_folder}")

def main():
    # 设置固定的目录
    base_directory = r"D:\py\AutoPrint"
    
    # 设置输入文件夹为固定目录下的 'input'
    input_folder = os.path.join(base_directory, 'input')
    # 设置输出文件夹为固定目录下的 'output'
    output_folder = os.path.join(base_directory, 'output')

    # 确保输出文件夹存在
    ensure_folder_exists(output_folder)

    # 处理PDF文件
    process_pdfs(input_folder, output_folder)

    print("拆分并重命名完成,本窗口5s后关闭！")
    
    # 等待5秒
    time.sleep(5)

if __name__ == '__main__':
    main()
