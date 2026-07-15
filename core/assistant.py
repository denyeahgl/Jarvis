from core.config import Config
from core.logger import Logger
from core.prompt import get_system_prompt

from tools.registry import ToolRegistry

from memory.manager import MemoryManager

from agent.executor import AgentExecutor
from agent.runtime import AgentRuntime


class Jarvis:
    """
    Jarvis CLI

    Assistant 只负责：

    1. 初始化
    2. CLI
    3. 生命周期

    所有业务逻辑全部交给 AgentRuntime。
    """

    def __init__(self):

        self.config = Config()
        self.logger = Logger()

        self.registry = ToolRegistry()

        self.runtime = None

    # ==================================================
    # Initialize
    # ==================================================

    def initialize(self):

        self.logger.info(
            f"{self.config.name} 初始化开始..."
        )

        loaded_tools = self.registry.load_tools()

        self.logger.info(
            f"加载工具: {loaded_tools}"
        )

        self.registry.initialize_tools()

        memory = MemoryManager()

        if not memory.history.has_system_message():

            memory.add_system(
                get_system_prompt()
            )

        executor = AgentExecutor(
            registry=self.registry
        )

        self.runtime = AgentRuntime(
            memory=memory,
            executor=executor,
        )

        self.logger.info(
            f"使用模型: {self.config.model_name}"
        )

        self.logger.info(
            f"{self.config.name} 初始化完成。"
        )

    # ==================================================
    # UI
    # ==================================================

    def greet(self):

        self.logger.info(
            f"你好，我是 {self.config.name}!"
        )

    def chat(
        self,
        user_input: str,
    ) -> str:

        return self.runtime.chat(
            user_input
        )

    # ==================================================
    # Main Loop
    # ==================================================

    def run(self):

        self.greet()

        while True:

            user_input = input("你: ").strip()

            if user_input.lower() in (
                "exit",
                "quit",
            ):

                print("Jarvis: Goodbye!")
                break

            reply = self.chat(
                user_input
            )

            print(
                f"Jarvis: {reply}"
            )

    # ==================================================
    # Shutdown
    # ==================================================

    def shutdown(self):

        self.logger.info(
            "Jarvis 正在关闭..."
        )

        self.registry.shutdown_tools()

        self.logger.info(
            "Jarvis 已关闭。"
        )