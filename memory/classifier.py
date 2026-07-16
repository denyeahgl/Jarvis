"""
Memory Type Classifier

负责判断 Memory 类型

Version:
    3.0
"""


class MemoryClassifier:
    """
    Memory 类型分类器
    """

    def __init__(self):

        self.rules = {

            # ==========================
            # 项目
            # ==========================
            "project": [

                "Jarvis",
                "Agent",

                "项目",
                "开发",
                "构建",
                "设计",
                "实现",
                "重构",
                "优化",
                "架构",
                "系统",
                "代码",
                "模块",
                "功能",
                "版本",

            ],

            # ==========================
            # 用户偏好
            # ==========================
            "preference": [

                "喜欢",
                "最喜欢",
                "偏好",
                "习惯",
                "希望",

                "爱好",
                "热爱",
                "支持",

                "想要",
                "更喜欢",

            ],

            # ==========================
            # 技能
            # ==========================
            "skill": [

                "学习",
                "掌握",
                "熟悉",
                "了解",

                "实现",
                "完成",

                "会",
                "能够",
                "擅长",

            ],

            # ==========================
            # 长期事实
            # ==========================
            "fact": [

                "我是",
                "我叫",
                "名字",

                "住在",
                "居住",
                "来自",

                "年龄",
                "今年",

                "生日",
                "出生",

                "学校",
                "大学",
                "学院",

                "专业",

                "工作",
                "职业",
                "公司",

                "城市",
                "国家",

                "使用",

            ],

        }

    def classify(
        self,
        content: str,
    ) -> str:
        """
        返回 memory_type
        """

        if not content:
            return "conversation"

        text = content.strip()

        if not text:
            return "conversation"

        scores = {}

        for category, keywords in self.rules.items():

            score = 0

            for keyword in keywords:

                if keyword in text:
                    score += 1

            scores[category] = score

        best_score = max(scores.values())

        if best_score == 0:
            return "conversation"

        top_types = [
            category
            for category, score in scores.items()
            if score == best_score
        ]

        # 多类别并列，不武断判断
        if len(top_types) > 1:
            return "conversation"

        return top_types[0]