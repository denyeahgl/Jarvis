"""
Memory Extractor

Version 4.0

新增：

1. 主语继承
2. 谓语继承
3. 更好的事实规范化
"""


class MemoryExtractor:

    def __init__(self):

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
            "另外",
        ]

        self.replace_rules = [

            ("我最喜欢", "用户最喜欢"),
            ("我喜欢", "用户喜欢"),
            ("我偏好", "用户偏好"),
            ("我希望", "用户希望"),
            ("我习惯", "用户习惯"),

            ("我住在", "用户住在"),
            ("我现在住在", "用户住在"),
            ("我居住在", "用户住在"),

            ("我来自", "用户来自"),

            ("我是", "用户是"),
            ("我叫", "用户叫"),

            ("我的生日是", "用户生日是"),
            ("我的专业是", "用户专业是"),
            ("我的年龄是", "用户年龄是"),
            ("我今年", "用户今年"),

            ("我正在开发", "用户正在开发"),
            ("我开发", "用户开发"),
            ("我设计", "用户设计"),
            ("我实现", "用户实现"),
            ("我构建", "用户构建"),

            ("我学习", "用户学习"),
            ("我掌握", "用户掌握"),
        ]

        # 能够继承的前缀
        self.context_prefix = [

            "用户最喜欢",
            "用户喜欢",
            "用户偏好",
            "用户希望",
            "用户习惯",

            "用户开发",
            "用户正在开发",
            "用户设计",
            "用户实现",
            "用户构建",

            "用户学习",
            "用户掌握",

            "用户住在",
            "用户来自",
        ]

    def extract(self, text: str) -> list[str]:

        if not text:
            return []

        text = text.strip()

        if not text:
            return []

        parts = [text]

        for splitter in self.split_words:

            new_parts = []

            for part in parts:

                for item in part.split(splitter):

                    item = item.strip()

                    if item:
                        new_parts.append(item)

            parts = new_parts

        memories = []

        last_prefix = ""

        for part in parts:

            memory = self.normalize(part)

            if not memory:
                continue

            # -----------------------
            # 主语继承
            # -----------------------

            if not memory.startswith("用户"):

                if last_prefix:

                    inherit = self.try_inherit(
                        memory,
                        last_prefix,
                    )

                    if inherit:
                        memory = inherit

            # 更新上下文

            prefix = self.extract_prefix(memory)

            if prefix:
                last_prefix = prefix

            if len(memory) < 4:
                continue

            memories.append(memory)

        return memories

    def normalize(self, text: str) -> str:

        text = text.strip()

        while text.endswith(("。", "！", "?", "？", "!")):
            text = text[:-1].strip()

        if text.startswith("用户"):
            return text

        for old, new in sorted(
            self.replace_rules,
            key=lambda x: len(x[0]),
            reverse=True,
        ):

            if text.startswith(old):
                return new + text[len(old):]

        if text.startswith("我"):
            return "用户" + text[1:]

        return text

    def extract_prefix(self, text: str):

        for prefix in self.context_prefix:

            if text.startswith(prefix):
                return prefix

        return ""

    def try_inherit(
        self,
        text: str,
        prefix: str,
    ):

        inherit_words = [

            "喜欢",
            "最喜欢",
            "偏好",
            "希望",
            "习惯",

            "开发",
            "设计",
            "实现",
            "构建",

            "学习",
            "掌握",
        ]

        for word in inherit_words:

            if text.startswith(word):

                return prefix + text[len(word):]

        return ""