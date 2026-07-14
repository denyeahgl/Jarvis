"""
Memory Scorer

负责评估一条 Memory 的重要程度。

返回:

0-5

0:
    不重要

5:
    非常重要
"""


class MemoryScorer:
    """
    Memory 重要性评分器
    """


    def __init__(self):

        # 高价值关键词
        self.high_value_keywords = {
            "项目",
            "开发",
            "Jarvis",
            "Agent",
            "代码",
            "架构",
            "设计",
            "计划",
            "目标",
            "喜欢",
            "习惯",
            "记住",
        }


        # 中等价值关键词
        self.medium_value_keywords = {
            "学习",
            "研究",
            "测试",
            "尝试",
            "配置",
            "环境",
        }



    def score(
        self,
        content: str
    ) -> int:
        """
        计算 Memory importance

        返回:
            0-5
        """

        if not content:
            return 0


        text = content.strip()


        score = 0



        # 长度基础评分

        if len(text) > 20:
            score += 1


        if len(text) > 50:
            score += 1



        # 高价值关键词

        for keyword in self.high_value_keywords:

            if keyword in text:
                score += 1



        # 中价值关键词

        for keyword in self.medium_value_keywords:

            if keyword in text:
                score += 1



        # 限制最大值

        return min(
            score,
            5
        )