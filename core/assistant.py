from core.config import Config
from core.logger import Logger
from core.prompt import get_system_prompt

from memory.history import MessageHistory

from agent.executor import AgentExecutor

from tools.registry import ToolRegistry



class Jarvis:
    """
    Jarvis 核心 Runtime

    负责：

    1. 初始化系统
    2. 管理生命周期
    3. 调度 Agent
    4. 关闭资源
    """



    def __init__(self):

        self.config = Config()

        self.logger = Logger()


        self.history = MessageHistory()


        # Tool Runtime

        self.registry = ToolRegistry()


        # Agent Executor

        self.executor = None



    def initialize(self):
        """
        Jarvis 启动流程
        """


        self.logger.info(
            f"{self.config.name} 初始化开始..."
        )


        # -----------------
        # 初始化 Tools
        # -----------------

        loaded_tools = (
            self.registry.load_tools()
        )


        self.logger.info(
            f"加载工具: {loaded_tools}"
        )


        self.registry.initialize_tools()



        # -----------------
        # 初始化 Agent
        # -----------------

        self.executor = AgentExecutor(
            self.registry
        )


        self.logger.info(
            f"使用模型: {self.config.model_name}"
        )


        self.logger.info(
            f"{self.config.name} 初始化完成。"
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



    def chat(self, user_input):


        self.history.add_user(
            user_input
        )


        return self.executor.run(
            self.history
        )



    def run(self):
        """
        Jarvis 主循环
        """


        self.setup_prompt()

        self.greet()


        while True:


            user_input = input(
                "你: "
            ).strip()



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



    def shutdown(self):
        """
        Jarvis 关闭流程
        """


        self.logger.info(
            "Jarvis 正在关闭..."
        )


        if self.registry:


            self.registry.shutdown_tools()



        self.logger.info(
            "Jarvis 已关闭。"
        )