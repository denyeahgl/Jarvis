"""
Memory Type Classifier

负责判断 Memory 类型
"""


class MemoryClassifier:
    """
    Memory 类型分类器
    """


    def __init__(self):

        self.rules = {

            "project": [
                "项目",
                "开发",
                "Jarvis",
                "Agent",
                "架构",
                "代码",
                "系统",
            ],


            "preference": [
                "喜欢",
                "偏好",
                "习惯",
                "希望",
            ],


            "skill": [
                "学习",
                "掌握",
                "完成",
                "实现",
                "熟悉",
            ],


            "fact": [
                "是",
                "叫",
                "使用",
                "来自",
            ],

        }



    def classify(
        self,
        content: str
    ) -> str:
        """
        返回 memory_type
        """


        if not content:
            return "conversation"


        text = content.strip()



        scores = {}


        for category, keywords in self.rules.items():

            score = 0

            for keyword in keywords:

                if keyword in text:
                    score += 1


            scores[category] = score



        best_type = max(
            scores,
            key=scores.get
        )


        if scores[best_type] == 0:
            return "conversation"


        return best_type