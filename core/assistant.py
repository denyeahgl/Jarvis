from core.config import Config
from core.logger import Logger
from core.llm import chat
from memory.history import MessageHistory
from core.prompt import get_system_prompt


class Jarvis:
    """Jarvis 核心类"""

    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.history = MessageHistory()
    
    def initialize(self):
        self.logger.info(f"{self.config.name} 初始化完成。")
        self.logger.info(f"使用模型: {self.config.model_name}")

    def greet(self):
        self.logger.info(f"你好，我是 {self.config.name}!")   

    def start(self):
        self.logger.info(f"{self.config.name} 启动成功。")
    
    def respond(self, user_input: str):
        """处理用户输入并生成回复"""

        # 保存用户消息
        self.history.add_user(user_input)

        # 调用 LLM
        response = chat(
            self.history.get_messages(),
            stream=True
        )

        # 保存 Assistant 回复
        self.history.add_assistant(response)


    def run(self):
        self.initialize()
        self.greet()

        if not self.history.has_system_message():
            self.history.add_system(
                get_system_prompt()
            )

        while True:
            
            user_input = input("你: ").strip()

            if user_input.lower() in ("exit", "quit"):
                print("Jarvis: Goodbye!")
                break       

            self.respond(user_input)
            print()