"""
memory/merge.py

Jarvis Memory Merge Engine

Day17 (Phase 2)

职责:

判断两条"语义相关但不完全重复、也没有构成冲突"的 Memory
是否应该合并成一条更完整的记忆，并且在判定"应该合并"之后
真正生成合并后的内容。

Pipeline:

New Memory + Candidates
    ↓
check()   ->  是否应该合并 + 目标是谁（只判断，不改内容）
    ↓
merge()   ->  真正生成合并后的 content
              (LLM 摘要合并优先，规则版拼接兜底)


与 DedupEngine / MemoryConflictDetector 的关系:

DedupEngine:
    判断"是不是同一句话的不同说法" —— 完全重复，跳过。

MemoryConflictDetector:
    判断"是不是同一实体的互斥新旧信息" —— 二选一，不能共存。

MergeEngine:
    判断"是不是同一话题的互补信息" —— 两条都对，
    合并成一条更完整的记忆。

三者在 decision.py 里是互斥的判断顺序：

duplicate -> (entity_key) update -> conflict -> merge -> new

只要前面某一步命中了，就不会再跑到 merge 这一步，
所以 merge 这里不需要重复判断"是不是重复/冲突"。
"""


from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Callable, List, Optional
import logging

import numpy as np


# =====================================================
# Result
# =====================================================

@dataclass
class MergeResult:
    """
    Merge 判断结果

    注意:

    字段名对齐 decision.py 里 MERGE 分支已经在读的
    `result.confidence` / `result.memory_id`，
    不要改名，否则 decision.py 要跟着改。

    should_merge 恒为 True —— check() 判定"不需要合并"时
    直接返回 None，而不是返回一个 should_merge=False 的实例。
    这是刻意的：decision.py 之前处理 Dedup/Conflict 时踩过
    "dataclass 实例恒为真值，必须判断内部字段而不是 `if result:`"
    的坑，这里干脆让"不合并"直接对应 None，`if result:` 就是
    正确的判断，不需要调用方再多记一条规则。
    """

    should_merge: bool = True

    confidence: float = 0.0

    memory_id: Optional[str] = None

    old_memory: object = None

    reason: str = ""



# =====================================================
# Merge Engine
# =====================================================

class MergeEngine:


    def __init__(
        self,
        chat_json_fn: Optional[Callable] = None,
        min_similarity: float = 0.55,
        max_similarity: float = 0.92,
        min_text_overlap: float = 0.15,
    ):

        """
        min_similarity / max_similarity:

            两条 Memory 的 embedding 余弦相似度落在
            [min_similarity, max_similarity) 区间内，
            才认为"同话题但不是同一句话"：

            >= max_similarity:
                这个相似度级别理论上应该已经被
                DedupEngine 判成 duplicate，走到这里说明
                上游没拦住，保险起见这里也不重复处理。

            <  min_similarity:
                话题都不挨边，不该合并。

            阈值和 conflict.py 的 similarity_threshold(0.55)
            对齐，因为 decision.py 里 merge 检查排在 conflict
            检查之后，能落到这一步的候选，语义相似度基本已经
            确认 >= 0.55（否则 conflict 那步就不会看它）。
            这里重新算一遍是为了让 MergeEngine 可以独立于
            ConflictDetector 单独使用/单独测试。

        min_text_overlap:

            SequenceMatcher 字面相似度下限，过滤掉
            "embedding 相似但字面完全不搭"的噪声情况——
            目标文档里提到的"纯向量阈值法很脆弱，短文本 embedding
            相似度本身噪声大"，这里用字面重叠做一次兜底校验，
            不是单靠一个向量阈值定生死。

        chat_json_fn:

            可选注入的 LLM 摘要合并函数，签名对齐
            core.llm.chat_json（跟 extractor.py 的依赖注入
            方式保持一致：`chat_json_fn(messages=[...]) -> str`）。
            不传时 merge() 走规则版拼接兜底，保证系统在没有
            配置 LLM 依赖时也能跑通，不会因为合并这一步失败
            就丢数据。
        """

        self.chat_json_fn = chat_json_fn

        self.min_similarity = min_similarity

        self.max_similarity = max_similarity

        self.min_text_overlap = min_text_overlap

        self.logger = logging.getLogger(
            __name__
        )



    # =================================================
    # Check (只判断，不改内容)
    # =================================================

    def check(
        self,
        new_memory,
        candidates: List,
    ) -> Optional[MergeResult]:

        """
        判断 new_memory 是否应该和 candidates 里某一条合并。

        返回 None 表示不需要合并
        （decision.py 里 `if result:` 会因此判 False，
        走到下一步，也就是 NEW）。
        """

        best = None

        best_score = 0.0

        for old_memory in candidates:

            similarity = self._cosine(
                new_memory,
                old_memory,
            )

            if similarity <= 0:
                continue

            if similarity < self.min_similarity:
                continue

            if similarity >= self.max_similarity:

                # 理论上不该发生：这个相似度级别
                # DedupEngine 应该已经判过 duplicate，
                # 这里跳过，不重复判定。
                continue

            if (
                new_memory.content.strip()
                ==
                old_memory.content.strip()
            ):
                continue

            text_overlap = SequenceMatcher(
                None,
                new_memory.content,
                old_memory.content,
            ).ratio()

            if text_overlap < self.min_text_overlap:

                # embedding 说像，字面完全不像
                # -> 大概率是 embedding 噪声，
                # 不认为是同一话题的互补信息。
                continue

            self.logger.info(
                f"MERGE CANDIDATE: "
                f"{old_memory.content} <-> "
                f"{new_memory.content} "
                f"sim={similarity:.4f} "
                f"text_overlap={text_overlap:.4f}"
            )

            if similarity > best_score:

                best_score = similarity

                best = old_memory

        if best is None:

            return None

        return MergeResult(

            should_merge=True,

            confidence=best_score,

            memory_id=best.id,

            old_memory=best,

            reason=(
                "Complementary information, "
                "same topic"
            ),
        )



    # =================================================
    # Merge (真正生成合并后的内容)
    # =================================================

    def merge(
        self,
        new_memory,
        old_memory,
    ) -> str:

        """
        生成合并后的 content。

        优先走 LLM 摘要合并（如果注入了 chat_json_fn）；
        没有注入、或者 LLM 调用失败时走规则版兜底。
        """

        if self.chat_json_fn is not None:

            try:

                merged = self._merge_with_llm(
                    new_memory,
                    old_memory,
                )

                if merged:

                    return merged

            except Exception as e:

                self.logger.error(
                    f"LLM Merge失败，回退规则版: {e}"
                )

        return self._merge_with_rules(
            new_memory,
            old_memory,
        )



    def _merge_with_llm(
        self,
        new_memory,
        old_memory,
    ) -> Optional[str]:

        messages = [

            {
                "role": "system",
                "content": _MEMORY_MERGE_PROMPT,
            },

            {
                "role": "user",
                "content": (
                    f"旧记忆: {old_memory.content}\n"
                    f"新记忆: {new_memory.content}"
                ),
            },

        ]

        response = self.chat_json_fn(
            messages=messages
        )

        if not response:

            return None

        merged = str(response).strip()

        return merged or None



    def _merge_with_rules(
        self,
        new_memory,
        old_memory,
    ) -> str:

        """
        规则版兜底：

        - 如果一条完全包含另一条，取更长/更完整的那条
        - 否则原样拼接，用中文顿号分隔

        不追求语义上的完美摘要，只保证不丢信息——
        真正的摘要质量交给 LLM 版本（Day17 之后接入）。
        """

        old_text = old_memory.content.strip()

        new_text = new_memory.content.strip()

        if old_text in new_text:

            return new_text

        if new_text in old_text:

            return old_text

        return f"{old_text}；{new_text}"



    # =================================================
    # Utils
    # =================================================

    def _cosine(
        self,
        new_memory,
        old_memory,
    ) -> float:

        if not getattr(new_memory, "embedding", None):

            return 0.0

        if not getattr(old_memory, "embedding", None):

            return 0.0

        a = np.array(new_memory.embedding)

        b = np.array(old_memory.embedding)

        denom = (
            np.linalg.norm(a)
            *
            np.linalg.norm(b)
        )

        if denom == 0:

            return 0.0

        return float(
            np.dot(a, b) / denom
        )



# =====================================================
# LLM Prompt
#
# 不放进 memory/prompts.py：Phase 2 范围只改 merge.py /
# decision.py / manager.py，避免顺手改一个没被要求的文件。
# 如果后续想统一管理所有 Memory 相关 prompt，把这段挪过去
# 即可，MergeEngine 这边只依赖常量名，不依赖它在哪个文件。
# =====================================================

_MEMORY_MERGE_PROMPT = """你是一个记忆合并助手。

你会收到两条关于同一个话题的记忆，它们不冲突，只是
分别包含了一部分信息（互补关系）。请把它们合并成一条
更完整、更精炼的记忆，只输出合并后的一句话，不要输出
任何解释、标点符号以外的多余内容。

要求：
1. 不要丢失任意一条里出现过的具体信息（人物、时间、数值、偏好等）
2. 不要编造两条记忆都没提到的信息
3. 尽量简洁，一句话说清楚
"""