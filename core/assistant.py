from core.config import Config
from core.logger import Logger
from core.llm import chat

class Jarvis:
    """Jarvis 核心类"""

    def __init__(self):
        self.config = Config()
        self.logger = Logger()
    
    def initialize(self):
        self.logger.info(f"{self.config.name} 初始化完成。")
        self.logger.info(f"使用模型: {self.config.model_name}")

    def greet(self):
        self.logger.info(f"你好，我是 {self.config.name}!")   

    def start(self):
        self.logger.info(f"{self.config.name} 启动成功。")
    
    def chat(self, user_input: str):

        messages = [
            {
                "role": "user",
                "content": user_input
            }
        ]

        chat(messages, stream=True)


    def run(self):
        self.initialize()
        self.greet()

        while True:
            user_input = input("你: ").strip()

            if user_input.lower() in ("exit", "quit"):
                print("Jarvis: Goodbye!")
                break       

            self.chat(user_input)