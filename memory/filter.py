"""
Memory Filter

负责判断：
一条信息是否值得进入长期记忆。
"""


class MemoryFilter:
    """
    Memory 筛选器
    """

    def __init__(self):

        # 明确不保存的短消息
        self.ignore_words = {
            "你好",
            "hello",
            "hi",
            "谢谢",
            "thanks",
            "退出",
            "quit",
            "exit",
        }


    def should_remember(
        self,
        content: str
    ) -> bool:
        """
        判断是否保存

        True:
            保存

        False:
            丢弃
        """

        if not content:
            return False


        text = content.strip()


        # 太短的信息忽略
        if len(text) < 5:
            return False


        # 常见无意义输入
        if text.lower() in self.ignore_words:
            return False


        return True