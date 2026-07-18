"""
Memory Decision Engine

负责决定新Memory进入系统时的处理方式:

Duplicate
Update
Conflict
Merge
New

Day15.4
"""


from dataclasses import dataclass
from enum import Enum
from typing import Optional, List

# =====================================================
# Decision Type
# =====================================================

class DecisionType(Enum):
    """
    Memory Decision 类型
    """

    # 完全重复
    DUPLICATE = "duplicate"

    # 信息更新
    UPDATE = "update"

    # 冲突
    CONFLICT = "conflict"

    # 信息互补，需要合并
    MERGE = "merge"

    # 新Memory
    NEW = "new"



# =====================================================
# Decision Result
# =====================================================

@dataclass
class DecisionResult:
    """
    Memory Decision 输出结果
    """

    # 决策类型
    decision: DecisionType = DecisionType.NEW


    # 判断置信度
    confidence: float = 0.0


    # 目标Memory

    # 例如:
    # duplicate:
    #   指向重复Memory
    #
    # update:
    #   指向旧Memory

    target_memory_id: Optional[str] = None


    # 候选Memory

    candidates: list = None


    # 原因说明

    reason: str = ""


    def __post_init__(self):

        if self.candidates is None:
            self.candidates = []



# =====================================================
# Memory Decision Engine
# =====================================================

class MemoryDecisionEngine:
    """
    Memory 决策引擎


    输入:

        new_memory

        candidate_memories


    输出:

        DecisionResult


    """



    def __init__(
        self,
        dedup=None,
        conflict=None,
        merge=None
    ):

        """
        注入判断模块

        dedup:
            Dedup Engine


        conflict:
            Conflict Detector


        merge:
            Merge Engine

        """

        self.dedup = dedup

        self.conflict = conflict

        self.merge = merge



    # =================================================
    # Main Decision
    # =================================================

    def decide(
        self,
        new_memory,
        candidates: List
    ) -> DecisionResult:
        """
        判断新Memory应该如何处理
        """


        # 保存候选

        if not candidates:

            return DecisionResult(

                decision=DecisionType.NEW,

                confidence=1.0,

                reason="No candidate memory"

            )



        # =============================================
        # 1. Duplicate Check
        #    新Memory = 已存在Memory
        # =============================================

        if self.dedup:


            result = self.dedup.check(
                new_memory,
                candidates
            )


            # 注意:
            #
            # result 是 DedupResult 实例，
            # 只要 dedup.check() 不返回 None，
            # `if result:` 恒为 True，
            # 必须判断 result.is_duplicate 本身，
            # 否则所有新Memory都会被误判为重复。

            if result and result.is_duplicate:

                return DecisionResult(

                    decision=DecisionType.DUPLICATE,

                    confidence=result.confidence,

                    target_memory_id=result.memory_id,

                    candidates=candidates,

                    reason=result.reason or "Duplicate memory detected"

                )



        # =============================================
        # 2. Conflict Check
        # =============================================

        if self.conflict:


            result = self.conflict.check(

                new_memory,

                candidates

            )


            # 同上：ConflictResult 也要判断
            # result.is_conflict 本身，
            # 并且 ConflictResult 的字段是
            # is_conflict / similarity / old_memory /
            # new_memory / reason，
            # 没有 confidence / memory_id，
            # 不能照搬 dedup 分支的取值方式。

            if result and result.is_conflict:


                return DecisionResult(

                    decision=DecisionType.CONFLICT,

                    confidence=result.similarity,

                    target_memory_id=(
                        result.old_memory.id
                        if result.old_memory else None
                    ),

                    candidates=candidates,

                    reason=result.reason or "Conflict memory detected"

                )




        # =============================================
        # 3. Merge Check
        # =============================================

        if self.merge:


            result = self.merge.check(

                new_memory,

                candidates

            )


            if result:


                return DecisionResult(

                    decision=DecisionType.MERGE,

                    confidence=result.confidence,

                    target_memory_id=result.memory_id,

                    candidates=candidates,

                    reason="Need merge memories"

                )



        # =============================================
        # 4. Update Check
        #    预留     
        # =============================================



        # =============================================
        # 5. Default New Memory
        # =============================================


        return DecisionResult(

            decision=DecisionType.NEW,

            confidence=1.0,

            candidates=candidates,

            reason="New memory"

        )