"""
history.py

负责管理对话历史（Conversation Memory）。

MessageHistory 统一维护符合 OpenAI Chat API 格式的 messages。
"""

from copy import deepcopy


class MessageHistory:
    """管理对话历史消息"""

    def __init__(self):
        self.messages = []

    def add_message(self, message: dict):
        """
        添加一条符合 OpenAI Chat API 格式的 Message。

        Args:
            message: Message 字典
        """
        self.messages.append(message)

    def _add_text_message(self, role: str, content: str):
        """添加普通文本消息"""

        self.add_message(
            {
                "role": role,
                "content": content,
            }
        )

    def add_system(self, content: str):
        self._add_text_message("system", content)

    def has_system_message(self) -> bool:
        return any(
            msg.get("role") == "system"
            for msg in self.messages
        )

    def add_user(self, content: str):
        self._add_text_message("user", content)

    def add_assistant(self, content: str):
        self._add_text_message("assistant", content)

    def get_messages(self) -> list[dict]:
        """
        返回 Message 副本，避免外部修改内部状态。
        """
        return deepcopy(self.messages)

    def clear(self):
        self.messages.clear()