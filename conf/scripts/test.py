# -*- coding: utf-8 -*-

def main():
    while True:  
        # 提示用户输入内容
        user_input = input("请输入一些内容（输入 '666' 以退出）: ")
        
        # 检查用户是否想要退出
        if user_input == '666':
            print("程序已退出。")
            break
        
        # 打印用户输入的内容
        print("你输入的是: " + user_input)

# 运行主函数
if __name__ == "__main__":
    main()
