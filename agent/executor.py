"""
Agent Executor

负责：
1. 调用 LLM
2. 判断 Tool Calling
3. 调用 ToolExecutor
4. 多轮推理
"""

from core.llm import chat
from agent.tool_executor import ToolExecutor


class AgentExecutor:
    """
    Agent 执行器
    """

    def __init__(
        self,
        registry,
        memory_manager=None,
        max_tool_rounds=8
    ):
        self.registry = registry
        self.tool_executor = ToolExecutor(self.registry)
        self.memory = memory_manager          # MemoryManager 实例，用于持久化
        self.max_tool_rounds = max_tool_rounds

    def run(self, messages: list[dict]) -> str:
        """
        执行 Agent 推理循环。

        Args:
            messages: 完整的临时消息列表，包含系统提示、对话历史（不含记忆注入）、
                      长期记忆（若注入）、当前用户输入。此列表会被修改（追加助手消息、工具消息等），
                      但不会影响持久化的对话历史（self.memory.history）。

        Returns:
            str: 最终回复文本。
        """
        working_messages = messages  # 直接使用传入列表，后续追加

        for round_index in range(self.max_tool_rounds):
            # 调用 LLM
            message = chat(
                working_messages,
                tools=self.registry.get_tool_schemas(),
                stream=False,
                return_message=True,
            )

            # 无工具调用：普通回答
            if not getattr(message, "tool_calls", None):
                reply = message.content or ""
                # 持久化助手回复
                if self.memory:
                    self.memory.add_assistant(reply)
                    # 保存长期记忆（可选）
                    # self.memory.remember(reply)
                return reply

            # 有工具调用：构建 assistant 消息（含 tool_calls）
            assistant_message = {
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    tc.model_dump() if hasattr(tc, "model_dump") else tc.dict()
                    for tc in message.tool_calls
                ],
            }

            # 追加到工作消息（供后续 LLM 上下文）
            working_messages.append(assistant_message)

            # 持久化到对话历史
            if self.memory:
                self.memory.history.add_message(assistant_message)

            # 执行每个工具调用
            for tool_call in message.tool_calls:
                tool_message = self.tool_executor.execute(tool_call)
                # 追加到工作消息
                working_messages.append(tool_message)
                # 持久化
                if self.memory:
                    self.memory.history.add_message(tool_message)

        # 超出最大轮数
        fallback_reply = "抱歉，工具调用轮数超过上限。"
        if self.memory:
            self.memory.add_assistant(fallback_reply)
        return fallback_reply