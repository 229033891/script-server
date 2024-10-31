import sys

def main():
    # 检查参数数量
    if len(sys.argv) != 3:
        print("用法: python print_six_args.py <a> <b>")
        return

    # 提取命令行参数
    a = sys.argv[1]
    b = sys.argv[2]


    # 分别打印参数
    print(f"参数 a: {a}")
    print(f"参数 b: {b}")


if __name__ == "__main__":
    main()
