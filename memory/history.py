"""
history.py

负责管理对话历史（Conversation Memory）。

MessageHistory 是整个 Jarvis 的消息管理器，
统一维护符合 OpenAI Chat API 格式的 messages 列表。
"""


class MessageHistory:
    """管理对话历史消息"""

    def __init__(self):
        """初始化消息列表"""
        self.messages = []

    def _add_message(self, role: str, content: str):
        """
        添加一条消息（内部方法）

        Args:
            role: 消息角色（system / user / assistant）
            content: 消息内容
        """
        self.messages.append(
            {
                "role": role,
                "content": content,
            }
        )

    def add_system(self, content: str):
        """添加 System Message"""
        self._add_message("system", content)

    def add_user(self, content: str):
        """添加 User Message"""
        self._add_message("user", content)

    def add_assistant(self, content: str):
        """添加 Assistant Message"""
        self._add_message("assistant", content)

    def get_messages(self):
        """
        获取当前全部消息

        返回消息列表的浅拷贝，避免外部直接修改内部数据。
        """
        return self.messages.copy()

    def clear(self):
        """清空所有历史消息"""
        self.messages.clear()