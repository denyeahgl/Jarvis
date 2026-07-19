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


            # Day18 / Phase 3
            #
            # DedupEngine 在灰色地带调用 LLM 裁决后，如果认为
            # "这是对旧记忆的更新"，会把 suggested_update 置 True
            # 而不是 is_duplicate——这时候应该直接按 UPDATE 处理，
            # 不需要再走下面 entity_key / conflict / merge 那一套
            # 规则去猜，因为这是已经拿着两条具体记忆问过 LLM 的
            # 结论，比规则判断更可靠。

            if result and getattr(result, "suggested_update", False):

                return DecisionResult(

                    decision=DecisionType.UPDATE,

                    confidence=result.confidence,

                    target_memory_id=result.memory_id,

                    candidates=candidates,

                    reason=result.reason or "LLM judged as update"

                )



        # =============================================
        # 2. Structured entity_key Update Check
        #    Day17 / Phase 2
        #
        #    比 Conflict 的关键词+字符重叠规则更可靠：
        #    如果新旧记忆的 entity_key 相同（同一个归一化槽位，
        #    比如 "user_favorite_color"），说明这是对同一件事的
        #    更新，而不是需要靠猜的"冲突"。
        #
        #    放在 Conflict 检查之前，因为这是结构化信号，
        #    应该比基于文本规则的模糊猜测优先级更高。
        # =============================================

        update_target = self._check_entity_key_update(
            new_memory,
            candidates,
        )

        if update_target is not None:

            return DecisionResult(

                decision=DecisionType.UPDATE,

                confidence=1.0,

                target_memory_id=update_target.id,

                candidates=candidates,

                reason=(
                    f"Same entity_key "
                    f"'{new_memory.entity_key}', "
                    f"treated as update"
                )

            )



        # =============================================
        # 3. Conflict Check
        # =============================================
        #
        # 注意: entity_key 命中的都已经在上面第2步走
        # UPDATE 分支返回了，走到这里说明 entity_key 为空/
        # 不匹配，只能退回这套基于关键词+字符重叠的模糊规则。

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
        # 4. Merge Check
        #
        #    注意: MergeEngine.check() 在"不需要合并"时
        #    直接返回 None（而不是 should_merge=False 的
        #    实例），所以这里 `if result:` 是安全的，
        #    不会重复踩 Dedup/Conflict 那个
        #    "dataclass 实例恒为真值" 的坑。
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

                    reason=result.reason or "Need merge memories"

                )



        # =============================================
        # 5. Default New Memory
        # =============================================


        return DecisionResult(

            decision=DecisionType.NEW,

            confidence=1.0,

            candidates=candidates,

            reason="New memory"

        )



    # =================================================
    # Day17 / Phase 2: Structured entity_key Update
    # =================================================

    def _check_entity_key_update(
        self,
        new_memory,
        candidates: List,
    ):
        """
        结构化 entity_key 匹配。

        如果新记忆和某条候选记忆的 entity_key 相同（且非空），
        说明它们描述的是同一个归一化槽位（比如同一个
        "user_favorite_color"），新记忆应该被当作对这个槽位的
        更新，而不是靠 conflict.py 里那套基于关键词+字符重叠的
        模糊规则去猜"是不是冲突"。

        返回:

            命中的旧 MemoryItem，或者 None（不命中）。

        注意:

        - entity_key 需要 Extractor/Validator 在 Phase 3
          才会真正产出；在那之前 new_memory.entity_key
          基本都是 None，这个分支不会命中，属于预留能力，
          不影响现有 pipeline。
        - 只在传入的 candidates（向量召回结果）里找，不会
          重新查库——如果同 entity_key 的旧记忆恰好没有被
          向量召回进 candidates，这里也发现不了。完整的
          "先按 entity_key 精确查，查不到再退化到向量相似度"
          要等 Phase 3 把 database.find_by_entity_key() 接到
          manager._get_candidates() 里才算补完。
        - 跳过内容完全相同的候选：那种理论上已经在上面
          Dedup 那一步被判成 duplicate 了，不应该也不需要
          在这里再走一次 update。
        """

        entity_key = getattr(
            new_memory,
            "entity_key",
            None,
        )

        if not entity_key:

            return None

        for old_memory in candidates:

            old_key = getattr(
                old_memory,
                "entity_key",
                None,
            )

            if not old_key:

                continue

            if old_key != entity_key:

                continue

            if (
                old_memory.content.strip()
                ==
                new_memory.content.strip()
            ):

                continue

            return old_memory

        return None