from core.config import Config
from core.logger import Logger
from core.prompt import get_system_prompt

from memory.manager import MemoryManager

from agent.executor import AgentExecutor

from tools.registry import ToolRegistry


class Jarvis:
    """
    Jarvis Runtime
    """

    def __init__(self):
        self.config = Config()
        self.logger = Logger()

        # Memory System
        self.memory = MemoryManager()

        # Tool Runtime
        self.registry = ToolRegistry()

        self.executor = None

    def initialize(self):
        self.logger.info(f"{self.config.name} 初始化开始...")

        loaded_tools = self.registry.load_tools()
        self.logger.info(f"加载工具: {loaded_tools}")
        self.registry.initialize_tools()

        # Agent（传入 memory 供其内部使用，但调用时直接传递消息列表）
        self.executor = AgentExecutor(self.registry, self.memory)

        self.logger.info(f"使用模型: {self.config.model_name}")
        self.logger.info(f"{self.config.name} 初始化完成。")

    def setup_prompt(self):
        if not self.memory.history.has_system_message():
            self.memory.add_system(get_system_prompt())

    def greet(self):
        self.logger.info(f"你好，我是 {self.config.name}!")

    def chat(self, user_input):
        # 1. 构建临时消息（不含当前用户输入，但会利用 user_input 检索记忆）
        messages = self.memory.build_context(user_input)
        # 2. 持久化用户输入
        self.memory.add_user(user_input)
        # 2.5 将用户输入也存入长期记忆 ← 新增
        self.memory.remember(user_input, memory_type="conversation")
        # 3. 将当前用户消息追加到临时消息列表（供 LLM 使用）
        messages.append({"role": "user", "content": user_input})
        # 4. 执行 Agent，它会自动持久化 assistant 和 tool 消息
        reply = self.executor.run(messages)
        return reply

    def run(self):
        self.setup_prompt()
        self.greet()

        while True:
            user_input = input("你: ").strip()
            if user_input.lower() in ("exit", "quit"):
                print("Jarvis: Goodbye!")
                break

            reply = self.chat(user_input)
            print(f"Jarvis: {reply}")

    def shutdown(self):
        self.logger.info("Jarvis 正在关闭...")
        if self.registry:
            self.registry.shutdown_tools()
        self.logger.info("Jarvis 已关闭。")