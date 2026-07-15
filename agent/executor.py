"""
Agent Executor

负责：

1. 调用 LLM
2. Tool Calling
3. Tool Loop
4. 返回最终回复

不负责：

- Memory
- History
- Context
- Runtime
"""

from core.llm import chat
from agent.tool_executor import ToolExecutor


class AgentExecutor:
    """
    Agent 执行器

    只负责 Agent 推理循环。
    """

    def __init__(
        self,
        registry,
        max_tool_rounds=8,
    ):
        self.registry = registry

        self.tool_executor = ToolExecutor(
            registry
        )

        self.max_tool_rounds = max_tool_rounds

    def run(
        self,
        messages: list[dict],
    ) -> str:
        """
        Agent Loop

        Parameters
        ----------
        messages
            Runtime 构建好的完整上下文。

        Returns
        -------
        str
            最终回复。
        """

        working_messages = list(messages)

        for _ in range(self.max_tool_rounds):

            message = chat(
                working_messages,
                tools=self.registry.get_tool_schemas(),
                stream=False,
                return_message=True,
            )

            # ===========================
            # 无 Tool Calling
            # ===========================

            if not getattr(
                message,
                "tool_calls",
                None,
            ):
                return message.content or ""

            # ===========================
            # Assistant Tool Call
            # ===========================

            assistant_message = {
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    tc.model_dump()
                    if hasattr(tc, "model_dump")
                    else tc.dict()
                    for tc in message.tool_calls
                ],
            }

            working_messages.append(
                assistant_message
            )

            # ===========================
            # Execute Tool
            # ===========================

            for tool_call in message.tool_calls:

                tool_message = (
                    self.tool_executor.execute(
                        tool_call
                    )
                )

                working_messages.append(
                    tool_message
                )

        return "抱歉，工具调用轮数超过上限。"