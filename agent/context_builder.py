"""
context_builder.py

LLM Context Builder

负责构建发送给 LLM 的完整上下文。

组成：

System Prompt
↓

Memory Context
↓

Conversation History
↓

Current User
↓

messages[]
"""

from copy import deepcopy


class ContextBuilder:
    """
    LLM Context Builder

    负责：

    - Conversation History
    - Memory Context
    - Current User Message

    输出：

        messages[]
    """

    def __init__(self, memory):

        self.memory = memory

    # ==================================================
    # Public
    # ==================================================

    def build(
        self,
        user_input: str | None = None,
        limit: int = 5,
        include_current_user: bool = True,
    ) -> list[dict]:
        """
        构建发送给 LLM 的完整上下文。

        Parameters
        ----------
        user_input : str | None
            当前用户输入。

        limit : int
            Memory 最大召回数量。

        include_current_user : bool
            是否把当前用户输入加入 messages。

        Returns
        -------
        list[dict]
            LLM messages
        """

        # 深拷贝，避免污染 History
        messages = deepcopy(
            self.memory.get_messages()
        )

        if not user_input:
            return messages

        # 构建 Memory Context
        memory_context = self.memory.build_memory_context(
            user_input=user_input,
            limit=limit,
        )

        # 插入 Memory Context
        if memory_context:

            messages.insert(
                self._system_insert_index(messages),
                {
                    "role": "system",
                    "content": memory_context,
                },
            )

        # 当前用户消息
        if include_current_user:

            messages.append(
                {
                    "role": "user",
                    "content": user_input,
                }
            )

        return messages

    # ==================================================
    # Private
    # ==================================================

    @staticmethod
    def _system_insert_index(
        messages: list[dict],
    ) -> int:
        """
        Memory Context 放到 System Prompt 后。

        Returns
        -------
        int
            插入位置
        """

        if (
            messages
            and messages[0].get("role") == "system"
        ):
            return 1

        return 0