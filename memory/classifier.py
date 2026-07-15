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



        best_score = max(scores.values())

        if best_score == 0:
            return "conversation"

        top_types = [
            category
            for category, score in scores.items()
            if score == best_score
        ]

        # 多个类别同分时，max(scores, key=scores.get) 会隐式偏向
        # self.rules 字典中排在最前面的类别（即 project），造成系统性分类偏差。
        # 这里改为：并列的情况不做武断猜测，视为无法明确判断，归为 conversation。
        if len(top_types) > 1:
            return "conversation"

        return top_types[0]