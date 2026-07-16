"""
memory/validator.py

Jarvis Memory Validator

Day13.5


职责：

LLM Extractor
        |
        v
Memory Dict
        |
        v
Validator
        |
        v
MemoryItem


负责：

- 数据校验
- 类型标准化
- importance标准化
- confidence计算
- Schema转换


不负责：

- Embedding
- Store
- Retrieval

"""

from __future__ import annotations


from memory.schema import MemoryItem


from core.logger import Logger



class MemoryValidator:

    """
    Memory 数据验证器
    """


    def __init__(self):

        self.logger = Logger()



    # =====================================================
    # Public
    # =====================================================

    def validate(
        self,
        memories: list[dict],
        source: str = "user",
    ) -> list[MemoryItem]:
        """
        批量验证。
        """

        result = []


        for memory in memories:


            item = self.validate_one(

                memory,

                source,

            )


            if item:

                result.append(
                    item
                )


        return result



    # =====================================================
    # Single
    # =====================================================

    def validate_one(
        self,
        data: dict,
        source: str = "user",
    ) -> MemoryItem | None:
        """
        单条 Memory 校验。
        """

        if not isinstance(
            data,
            dict,
        ):

            return None



        content = self._content(
            data.get(
                "content"
            )
        )


        if not content:

            return None



        memory_type = self._memory_type(

            data.get(
                "memory_type"
            )

        )


        importance = self._importance(

            data.get(
                "importance"
            )

        )


        # Day13.5 新增
        confidence = self._confidence(

            content,

            memory_type,

            importance,

        )



        return MemoryItem(

            content=content,

            memory_type=memory_type,

            importance=importance,

            source=source,

            confidence=confidence,

        )



    # =====================================================
    # Normalize
    # =====================================================

    def _content(
        self,
        content,
    ) -> str:

        if not content:

            return ""


        content = str(
            content
        ).strip()


        if not content:

            return ""


        return content



    def _memory_type(
        self,
        value,
    ) -> str:
        """
        标准化类型。
        """

        if not value:

            return "fact"



        value = (
            str(value)
            .strip()
            .lower()
        )



        mapping = {

            "facts":
            "fact",

            "fact":
            "fact",

            "preference":
            "preference",

            "preferences":
            "preference",

            "project":
            "project",

            "projects":
            "project",

            "goal":
            "goal",

            "goals":
            "goal",

            "identity":
            "identity",

            "habit":
            "habit",

            "skill":
            "skill",

            "experience":
            "experience",

            "relationship":
            "relationship",

        }


        return mapping.get(

            value,

            "fact"

        )



    def _importance(
        self,
        value,
    ) -> int:

        try:

            value = int(
                value
            )

        except Exception:

            value = 3



        return max(

            1,

            min(

                value,

                5,

            )

        )



    # =====================================================
    # Confidence
    # =====================================================

    def _confidence(
        self,
        content: str,
        memory_type: str,
        importance: int,
    ) -> float:
        """
        计算Memory置信度。

        Day13.5新增。

        表示：

        这条信息作为长期记忆是否可靠。


        """

        confidence = 0.7



        # 用户明确陈述

        if content.startswith(
            "用户"
        ):

            confidence += 0.1



        # 稳定信息

        if memory_type in [

            "identity",

            "project",

            "goal",

        ]:

            confidence += 0.1



        # 高价值记忆

        if importance >= 4:

            confidence += 0.1



        return round(

            min(

                confidence,

                1.0

            ),

            2

        )