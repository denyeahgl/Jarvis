from core.config import Config
from core.logger import Logger
from core.prompt import get_system_prompt

from memory.history import MessageHistory

from agent.executor import AgentExecutor


class Jarvis:
    """Jarvis 核心 Agent"""

    def __init__(self):

        self.config = Config()
        self.logger = Logger()

        self.history = MessageHistory()

        # Agent Executor
        self.executor = AgentExecutor()


    def initialize(self):

        self.logger.info(
            f"{self.config.name} 初始化完成。"
        )

        self.logger.info(
            f"使用模型: {self.config.model_name}"
        )


    def setup_prompt(self):

        if not self.history.has_system_message():

            self.history.add_system(
                get_system_prompt()
            )


    def greet(self):

        self.logger.info(
            f"你好，我是 {self.config.name}!"
        )


    def start(self):

        self.logger.info(
            f"{self.config.name} 启动成功。"
        )


    def chat(self, user_input):

        self.history.add_user(
            user_input
        )

        return self.executor.run(
            self.history
        )


    def run(self):

        self.initialize()

        self.setup_prompt()

        self.greet()


        while True:

            user_input = input("你: ").strip()


            if user_input.lower() in (
                "exit",
                "quit"
            ):

                print(
                    "Jarvis: Goodbye!"
                )

                break


            reply = self.chat(
                user_input
            )


            print(
                f"Jarvis: {reply}"
            )