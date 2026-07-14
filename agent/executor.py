"""
Agent Executor

负责：
1. 调用 LLM
2. 判断 Tool Calling
3. 调用 ToolExecutor
4. 循环推理，直到模型给出最终回复（支持多轮 tool call）
"""

from core.llm import chat

from tools.registry import ToolRegistry

from agent.tool_executor import ToolExecutor


class AgentExecutor:
    """Agent 执行器"""


    def __init__(
        self,
        registry,
        max_tool_rounds=8
    ):

        self.registry = registry

        self.tool_executor = ToolExecutor(
            self.registry
        )

        self.max_tool_rounds = max_tool_rounds


    def run(self, history):
        """
        执行一次 Agent 推理，支持连续多轮 tool calling。

        Args:
            history: MessageHistory

        Returns:
            str
        """

        for round_index in range(self.max_tool_rounds):

            # -------- 调用 LLM --------

            message = chat(
                history.get_messages(),
                tools=self.registry.get_tool_schemas(),
                stream=False,
                return_message=True,
            )


            # -------- 普通回复：结束循环 --------

            if not getattr(
                message,
                "tool_calls",
                None
            ):

                reply = message.content or ""

                history.add_assistant(
                    reply
                )

                return reply


            # -------- 保存 assistant tool call --------

            history.messages.append(
                {
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        tc.model_dump()
                        if hasattr(tc, "model_dump")
                        else tc.dict()
                        for tc in message.tool_calls
                    ],
                }
            )


            # -------- 执行 Tool --------

            for tool_call in message.tool_calls:

                tool_message = (
                    self.tool_executor.execute(
                        tool_call
                    )
                )

                history.messages.append(
                    tool_message
                )

            # 本轮结束，回到循环开头，把 tool 结果带给模型继续推理


        # -------- 超过最大轮数仍未收敛 --------

        fallback_reply = (
            "抱歉，工具调用轮数超过上限，暂时无法给出最终答案。"
        )

        history.add_assistant(
            fallback_reply
        )

        return fallback_reply