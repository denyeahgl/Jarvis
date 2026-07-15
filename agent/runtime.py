"""
runtime.py

Jarvis Agent Runtime

负责：

1. 协调 Memory
2. 协调 Context Builder
3. 调用 AgentExecutor
4. 更新 Conversation

Runtime 不负责创建任何对象，
所有依赖均由外部注入。
"""

from agent.context_builder import ContextBuilder


class AgentRuntime:
    """
    Jarvis Agent Runtime
    """

    def __init__(
        self,
        memory,
        executor,
        context_builder=None,
    ):
        """
        Parameters
        ----------
        memory : MemoryManager

        executor : AgentExecutor

        context_builder : ContextBuilder | None
        """

        self.memory = memory
        self.executor = executor

        self.context_builder = (
            context_builder
            if context_builder is not None
            else ContextBuilder(memory)
        )

    # ==================================================
    # Chat
    # ==================================================

    def chat(
        self,
        user_input: str,
    ) -> str:
        """
        Runtime 对外统一接口
        """

        # ③ Build Context
        messages = self.context_builder.build(
            user_input=user_input
        )

        # ① Conversation Memory
        self.memory.add_user(user_input)

        # ② Long-term Memory
        self.memory.remember_if_needed(user_input)


        # ④ Agent Loop
        reply = self.executor.run(messages)

        # ⑤ 保存回复
        self.memory.add_assistant(reply)

        return reply

    # ==================================================
    # Conversation
    # ==================================================

    def clear(self):
        """
        清空当前会话
        """
        self.memory.clear_history()

    def get_messages(self):
        """
        获取当前 Conversation
        """
        return self.memory.get_messages()

    # ==================================================
    # Memory
    # ==================================================

    def search_memory(
        self,
        query: str,
        limit: int = 5,
    ):
        return self.memory.search_memory(
            query=query,
            limit=limit,
        )

    def recall(self):
        """
        返回全部长期记忆
        """
        return self.memory.recall()