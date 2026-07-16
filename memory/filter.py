"""
Memory Filter

负责：

过滤明显无意义的信息。

注意：
Filter 不负责判断重要性，
重要程度交给 MemoryScorer。
"""


class MemoryFilter:
    """
    Memory 过滤器
    """

    def __init__(self):

        # 完全无意义的信息
        self.ignore_words = {

            "你好",
            "您好",

            "hi",
            "hello",

            "谢谢",
            "thanks",

            "拜拜",
            "再见",

            "退出",
            "quit",
            "exit",

            "好的",
            "好的。",
            "嗯",
            "嗯嗯",
            "哦",
            "哈哈",

            "ok",
            "okay",
        }

        # 问句通常不进入长期记忆
        self.question_words = [

            "吗",
            "么",
            "呢",

            "为什么",
            "多少",
            "几点",

            "谁",
            "哪里",
            "哪",
            "哪个",

            "什么",
            "怎样",
            "如何",

            "?",
            "？",
        ]

    def should_remember(
        self,
        content: str,
    ) -> bool:
        """
        是否值得进入长期记忆
        """

        if not content:
            return False

        text = content.strip()

        if not text:
            return False

        # 太短
        if len(text) < 3:
            return False

        # 固定忽略词
        if text.lower() in self.ignore_words:
            return False

        # 单纯问句一般不保存
        #
        # 例如：
        # 用户喜欢什么运动？
        #
        # 避免污染长期记忆
        #
        # 但：
        # "我喜欢什么运动你知道吗"
        # 属于事实表达，不过滤。
        #
        if not text.startswith("用户"):

            for word in self.question_words:

                if word in text:
                    return False

        return True