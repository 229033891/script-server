#!/usr/bin/env python3

import os
import sys

def main():
    # 确保 src 目录存在
    src_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "src")
    if not os.path.isdir(src_dir):
        print(f"Error: Directory '{src_dir}' does not exist.", file=sys.stderr)
        sys.exit(1)

    # 添加 src 目录到 sys.path
    sys.path.append(src_dir)
    
    # 切换工作目录到脚本所在目录
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    
    try:
        # 尝试导入和运行 main 模块
        import main
        main.main()
    except ImportError as e:
        print(f"Error: Failed to import module 'main'. {e}", file=sys.stderr)
        sys.exit(1)
    except AttributeError as e:
        print(f"Error: Module 'main' does not have a 'main' function. {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
