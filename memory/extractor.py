"""
Memory Extractor

负责：

从用户输入中提取可保存的 Memory 单元。

Version:
    Rule Based Extractor 1.0
"""


class MemoryExtractor:
    """
    Memory 提取器
    """


    def __init__(self):

        # 分割关键词

        self.split_words = [
            "，",
            ",",
            "。",
            ".",
            "；",
            ";",
            "并且",
            "而且",
            "以及",
            "同时",
        ]



    def extract(
        self,
        text: str
    ) -> list[str]:
        """
        提取 Memory

        参数:
            text:
                用户输入

        返回:
            Memory列表
        """


        if not text:
            return []


        text = text.strip()


        if not text:
            return []



        # 第一步：
        # 按语义连接词拆分

        parts = [
            text
        ]


        for splitter in self.split_words:

            new_parts = []

            for part in parts:

                fragments = part.split(
                    splitter
                )

                for fragment in fragments:

                    fragment = fragment.strip()

                    if fragment:
                        new_parts.append(
                            fragment
                        )


            parts = new_parts



        # 第二步：
        # 清理无效片段


        memories = []


        for part in parts:


            # 太短忽略

            if len(part) < 5:
                continue


            memories.append(
                self.normalize(part)
            )
        return memories



    def normalize(self, text: str) -> str:
        """
        标准化 Memory 内容
        """
        text=text.strip()
        # 用户偏好

        preference_words=[
            "喜欢",
            "偏好",
            "习惯",
            "希望",
            "我喜欢",
            "我偏好",
            "我习惯",
            "我希望"
        ]


        if text.startswith("我") and any(word in text for word in preference_words):

            return (
                "用户"
                +
                text[1:]
            )


        # 项目信息

        project_words=[
            "正在开发",
            "开发",
            "设计",
            "构建"
        ]


        for word in project_words:
            if word in text and not text.startswith("用户"):
                if text.startswith("我"):
                    return "用户" + text[1:]
                return "用户" + text


        return text
    


