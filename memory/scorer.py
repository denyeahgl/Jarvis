"""
Memory Scorer 3.0

负责：

1. 根据 Memory 类型评分
2. 根据内容增加权重
3. 输出 importance (1~5)

注意：

Scorer 不负责决定是否保存，
Filter 才负责过滤垃圾信息。
"""


class MemoryScorer:
    """
    Memory 重要度评分器
    """

    def __init__(self):

        # ==========================
        # 类型基础分
        # ==========================

        self.type_scores = {

            # 项目
            "project": 5,

            # 用户偏好
            "preference": 4,

            # 长期事实
            "fact": 4,

            # 技能
            "skill": 3,

            # 普通对话
            "conversation": 2,

        }

        # ==========================
        # 内容加分
        # ==========================

        self.keyword_scores = {

            # 项目相关
            "Jarvis": 2,
            "Agent": 2,
            "项目": 2,
            "开发": 2,
            "架构": 2,
            "设计": 2,
            "系统": 2,
            "代码": 1,

            # 偏好
            "喜欢": 1,
            "最喜欢": 2,
            "偏好": 1,
            "希望": 1,

            # 长期事实
            "住在": 1,
            "来自": 1,
            "生日": 1,
            "学校": 1,
            "专业": 1,
            "工作": 1,
            "职业": 1,

            # 学习成长
            "学习": 1,
            "完成": 1,
            "实现": 1,
            "掌握": 1,

        }

    def score(
        self,
        content: str,
        memory_type: str,
    ) -> int:
        """
        返回 Memory importance

        取值范围：

            1 ~ 5
        """

        if not content:
            return 1

        text = content.strip()

        if not text:
            return 1

        # --------------------------
        # 基础分
        # --------------------------

        score = self.type_scores.get(
            memory_type,
            2,
        )

        # --------------------------
        # 内容加分
        # --------------------------

        for keyword, value in self.keyword_scores.items():

            if keyword in text:
                score += value

        # --------------------------
        # 长一点的信息通常更完整
        # --------------------------

        if len(text) >= 15:
            score += 1

        if len(text) >= 30:
            score += 1

        # --------------------------
        # 用户长期事实加分
        # --------------------------

        if text.startswith("用户"):

            score += 1

        # --------------------------
        # 限制范围
        # --------------------------

        score = max(1, score)

        score = min(5, score)

        return score