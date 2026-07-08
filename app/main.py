def chat():
    print("Jarvis: 你好，我是你的智能助手Jarvis。请问有什么我可以帮你的吗？")

def main():
     print("===Jarvis 启动===")
     user_input = input("你：")
     print("收到你的消息:",user_input)
     chat()

if __name__ == "__main__":
    main()
