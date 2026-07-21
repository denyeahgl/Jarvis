# core/assistant.py

from core.config import Config
from core.logger import Logger
from core.prompt import get_system_prompt
from core.anchor_store import AnchorProfileStore
from core.anchor_wizard import AnchorWizard
from core.anchor import AnchorResolver

from tools.registry import ToolRegistry

from memory.manager import MemoryManager

from agent.executor import AgentExecutor
from agent.runtime import AgentRuntime
from agent.context_builder import ContextBuilder


class Jarvis:
    """
    Jarvis CLI
    """

    def __init__(self):

        self.config = Config()
        self.logger = Logger()

        self.registry = ToolRegistry()

        self.runtime = None
        self._wizard = None

    # ==================================================
    # Initialize
    # ==================================================

    def initialize(self):

        self.logger.info(
            f"{self.config.name} 初始化开始..."
        )

        # -------------------------
        # ① Anchor（不依赖工具/记忆，最先做，
        #    因为向导是同步阻塞的 input()，
        #    放前面能让用户第一时间看到设置提示）
        # -------------------------

        anchor_store = AnchorProfileStore()
        wizard = AnchorWizard(anchor_store)

        if anchor_store.is_empty():
            wizard.run_full()

        anchor = AnchorResolver(anchor_store)

        self._wizard = wizard

        # -------------------------
        # ② Tools
        # -------------------------

        loaded_tools = self.registry.load_tools()

        self.logger.info(
            f"加载工具: {loaded_tools}"
        )

        self.registry.initialize_tools()

        # -------------------------
        # ③ Memory
        # -------------------------

        memory = MemoryManager()

        if not memory.history.has_system_message():

            memory.add_system(
                get_system_prompt()
            )

        # -------------------------
        # ④ Executor
        # -------------------------

        executor = AgentExecutor(
            registry=self.registry
        )

        # -------------------------
        # ⑤ Runtime（唯一一次构造，
        #    context_builder 显式传入 anchor）
        # -------------------------

        self.runtime = AgentRuntime(
            memory=memory,
            executor=executor,
            context_builder=ContextBuilder(memory, anchor=anchor),
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

            if user_input == "/setup":
                self._wizard.run_full()
                continue

            if user_input == "/setup show":
                self._wizard.show()
                continue

            if user_input.startswith("/setup "):
                key = user_input.split(" ", 1)[1].strip()
                self._wizard.run_single(key)
                continue

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