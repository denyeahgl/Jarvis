import json

from core.config import Config
from core.logger import Logger
from core.llm import chat
from core.prompt import get_system_prompt

from memory.history import MessageHistory

from tools.registry import ToolRegistry


class Jarvis:
    """Jarvis 核心 Agent"""

    def __init__(self):
        self.config = Config()
        self.logger = Logger()

        self.history = MessageHistory()

        self.registry = ToolRegistry()

    def initialize(self):
        self.logger.info(f"{self.config.name} 初始化完成。")
        self.logger.info(f"使用模型: {self.config.model_name}")

    def greet(self):
        self.logger.info(f"你好，我是 {self.config.name}!")

    def start(self):
        self.logger.info(f"{self.config.name} 启动成功。")

    def _chat(self, stream=False, use_tools=False, return_message=False):
        """统一调用 LLM"""

        return chat(
            messages=self.history.get_messages(),
            stream=stream,
            tools=self.registry.get_tool_schemas() if use_tools else None,
            return_message=return_message,
        )

    def _execute_tool_calls(self, assistant_message):
        """执行 Tool Calls"""

        # 保存 assistant(tool_call) message
        self.history.add_message(
            assistant_message.model_dump(exclude_none=True)
        )

        for tool_call in assistant_message.tool_calls:

            tool_name = tool_call.function.name

            arguments = json.loads(
                tool_call.function.arguments
            )

            result = self.registry.execute(
                tool_name,
                **arguments,
            )

            self.history.add_message(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(
                        result,
                        ensure_ascii=False,
                    ),
                }
            )

    def respond(self, user_input: str):
        """处理用户输入"""

        self.history.add_user(user_input)

        # 第一次请求（带 Tool），必须拿完整 message 对象
        # 才能读取 tool_calls 字段
        assistant_message = self._chat(
            stream=False,
            use_tools=True,
            return_message=True,
        )

        # ---------- Tool Calling ----------
        if assistant_message.tool_calls:

            self._execute_tool_calls(
                assistant_message
            )

            # 第二次请求（不给 Tool，流式输出最终回复）
            reply = chat(
                self.history.get_messages(),
                stream=True,
            )

            self.history.add_assistant(reply)

            return

        # ---------- 普通回复 ----------
        reply = assistant_message.content

        print(f"Jarvis: {reply}")

        self.history.add_assistant(reply)

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
