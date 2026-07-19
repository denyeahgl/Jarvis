"""
Memory Deduplication Engine 2.0

Multi Signal Dedup:

1. Embedding similarity
2. Text similarity
3. Entity overlap
4. Relation similarity


Day15.4

Day18 / Phase 3:

- 加权分数落在阈值以下的"灰色地带"时，调用一次 LLM 做三选一
  语义裁决："重复表达 / 信息更新 / 完全不同的新事实"，
  而不是简单地靠阈值一刀切判"不是重复"。
"""


from dataclasses import dataclass
from difflib import SequenceMatcher
import json
import logging
import re


from core.llm import chat_json as default_chat_json



# =====================================================
# Result
# =====================================================

@dataclass
class DedupResult:
    """
    Dedup 判断结果
    """

    is_duplicate: bool = False

    confidence: float = 0.0

    memory_id: str = None

    reason: str = ""

    # Day18 / Phase 3
    #
    # LLM 灰色地带裁决为"这是对旧记忆的更新"时置 True。
    # decision.py 读到这个字段会直接判 UPDATE
    # （而不是继续往下走 entity_key / conflict / merge 那一套），
    # 因为这是已经拿着两条具体记忆问过 LLM 的结论，
    # 比后面那些规则判断更可靠。
    suggested_update: bool = False



# =====================================================
# Dedup Engine
# =====================================================


class DedupEngine:


    def __init__(
        self,
        threshold=0.85,
        chat_json_fn=None,
        gray_zone_low=0.60,
    ):
        """
        threshold:

            加权分数 >= threshold 直接判 duplicate，
            不需要 LLM 介入（省调用）。

        gray_zone_low:

            加权分数落在 [gray_zone_low, threshold) 区间时，
            才会触发 LLM 裁决——低于这个下限说明候选和新记忆
            关联度本来就低，问 LLM 意义不大，纯粹浪费一次调用。

        chat_json_fn:

            可选注入的 LLM 判断函数，签名对齐
            core.llm.chat_json（跟 extractor.py 的依赖注入方式
            保持一致）。不传时默认用 core.llm.chat_json，
            单测可以注入 fake 函数覆盖。如果连默认的都拿不到
            /调用失败，灰色地带直接按"不是重复"处理，
            不会因为 LLM 不可用就把整条 pipeline 打断。
        """

        self.threshold = threshold

        self.gray_zone_low = gray_zone_low

        self.chat_json_fn = (
            chat_json_fn or default_chat_json
        )

        self.logger = logging.getLogger(
            __name__
        )



    # =================================================
    # Main Check
    # =================================================

    def check(
        self,
        new_memory,
        candidates
    ):

        """
        检查是否存在重复Memory
        """


        best = None

        best_score = 0



        for old_memory in candidates:


            score = self._calculate_score(

                new_memory,

                old_memory

            )


            self.logger.info(

                f"DEDUP SCORE: "
                f"{old_memory.content} "
                f"{score:.4f}"

            )


            if score > best_score:

                best_score = score

                best = old_memory



        if best_score >= self.threshold:


            return DedupResult(

                is_duplicate=True,

                confidence=best_score,

                memory_id=best.id,

                reason=
                "Multi signal similarity"

            )



        # =============================================
        # Day18 / Phase 3
        # 灰色地带: LLM 语义裁决
        # =============================================
        #
        # 只有存在候选、且加权分数落在
        # [gray_zone_low, threshold) 区间才问 LLM——
        # 分数太低说明候选跟新记忆本来就不太相关，
        # 不值得为了这种情况多花一次 LLM 调用。

        if (
            best is not None
            and best_score >= self.gray_zone_low
        ):

            verdict = self._llm_arbitrate(
                new_memory,
                best,
                best_score,
            )

            if verdict == "duplicate":

                return DedupResult(

                    is_duplicate=True,

                    confidence=best_score,

                    memory_id=best.id,

                    reason=(
                        "LLM judged as duplicate "
                        "(gray zone)"
                    ),

                )

            if verdict == "update":

                return DedupResult(

                    is_duplicate=False,

                    confidence=best_score,

                    memory_id=best.id,

                    reason=(
                        "LLM judged as update "
                        "(gray zone)"
                    ),

                    suggested_update=True,

                )

            # verdict == "different" (或者 LLM 调用失败/
            # 解析失败的兜底值) -> 按原来的逻辑处理，
            # 不是重复，交给后面 entity_key / conflict /
            # merge 那一套继续判断。


        return DedupResult(
            is_duplicate=False,
            confidence=best_score
        )



    # =================================================
    # Day18 / Phase 3: LLM Gray-zone Arbitration
    # =================================================

    def _llm_arbitrate(
        self,
        new_memory,
        old_memory,
        score,
    ) -> str:
        """
        返回 "duplicate" / "update" / "different" 三选一。

        任何异常(LLM 调用失败、返回内容解析不出合法结果)
        都兜底成 "different"——宁可退化成"当作新记忆处理，
        后面还有 entity_key/conflict/merge 兜底"，也不要因为
        LLM 抽风就误判成 duplicate 把用户的新信息吞掉。
        """

        try:

            messages = [

                {
                    "role": "system",
                    "content": _DEDUP_ARBITRATION_PROMPT,
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

            verdict = self._parse_verdict(
                response
            )

            self.logger.info(
                f"DEDUP LLM ARBITRATION: "
                f"{old_memory.content} <-> "
                f"{new_memory.content} "
                f"score={score:.4f} "
                f"verdict={verdict}"
            )

            return verdict

        except Exception as e:

            self.logger.error(
                f"Dedup LLM裁决失败，按different处理: {e}"
            )

            return "different"


    def _parse_verdict(
        self,
        response,
    ) -> str:

        if not response:

            return "different"

        text = str(response).strip()

        text = re.sub(
            r"^```json", "", text, flags=re.I
        )

        text = re.sub(r"^```", "", text)

        text = re.sub(r"```$", "", text)

        text = text.strip()

        try:

            data = json.loads(text)

            verdict = str(
                data.get("verdict", "")
            ).strip().lower()

        except Exception:

            # 不是合法 JSON，退化成在原始文本里找关键词，
            # 兼容 LLM 没有严格按 JSON 格式回复的情况。

            verdict = text.strip().lower()


        if verdict in (
            "duplicate",
            "update",
            "different",
        ):

            return verdict


        return "different"



    # =================================================
    # Score
    # =================================================


    def _calculate_score(
        self,
        new,
        old
    ):


        # Day17.2 Bugfix
        #
        # 只收集"这一轮真的算出来了"的信号 (score, weight)，
        # 缺失的信号 (比如 entity/relation 因为 schema 里没有
        # 对应字段，hasattr 恒为 False) 直接不参与加权
        # 平均，而不是像之前那样被硬塞成 0 还占着
        # 权重 ---- 否则哪怕两句话逐字完全相同，加权总分
        # 也永远到不了 0.85 阈值
        # (0.5*1.0 + 0.2*1.0 = 0.7，entity/relation 的 0.2+0.1
        # 权重全程陪跑却什么都没算)。

        weighted = []



        # -----------------------------
        # 1. Embedding similarity
        # -----------------------------

        if (

            hasattr(new,"embedding")

            and hasattr(old,"embedding")

            and new.embedding

            and old.embedding

        ):

            weighted.append(
                (
                    self._cosine(
                        new.embedding,
                        old.embedding
                    ),
                    0.5,
                )
            )



        # -----------------------------
        # 2. Text similarity
        # -----------------------------

        text_score = (

            SequenceMatcher(

                None,

                new.content,

                old.content

            ).ratio()

        )


        weighted.append(
            (text_score, 0.2)
        )



        # -----------------------------
        # 3. Entity overlap
        # -----------------------------

        if (

            hasattr(new,"entities")

            and hasattr(old,"entities")

            and new.entities

            and old.entities

        ):

            weighted.append(
                (
                    self._entity_similarity(
                        new,
                        old
                    ),
                    0.2,
                )
            )



        # -----------------------------
        # 4. Relation similarity
        # -----------------------------

        if (

            hasattr(new,"relation")

            and hasattr(old,"relation")

            and getattr(new,"relation",None)

            and getattr(old,"relation",None)

        ):

            weighted.append(
                (
                    self._relation_similarity(
                        new,
                        old
                    ),
                    0.1,
                )
            )



        # weighted average, 只按实际参与的权重归一化

        total_weight = sum(
            w for _, w in weighted
        )

        if total_weight == 0:

            return 0.0


        score = sum(
            s * w for s, w in weighted
        ) / total_weight


        return score



    # =================================================
    # Utils
    # =================================================


    def _cosine(
        self,
        a,
        b
    ):


        import numpy as np


        a=np.array(a)

        b=np.array(b)



        return float(

            np.dot(a,b)

            /

            (

                np.linalg.norm(a)

                *

                np.linalg.norm(b)

            )

        )



    def _entity_similarity(
        self,
        a,
        b
    ):

        """
        Entity overlap

        当前没有entity字段时返回0

        """

        if not hasattr(a,"entities"):

            return 0



        if not hasattr(b,"entities"):

            return 0



        if not a.entities:

            return 0



        if not b.entities:

            return 0



        x=set(a.entities)

        y=set(b.entities)



        return len(x&y)/len(x|y)



    def _relation_similarity(
        self,
        a,
        b
    ):

        """
        relation similarity

        预留给 Memory Representation 2.0

        """

        if not hasattr(a,"relation"):

            return 0



        if not hasattr(b,"relation"):

            return 0



        return float(

            a.relation == b.relation

        )



# =====================================================
# LLM Arbitration Prompt
#
# 不放进 memory/prompts.py: 和 merge.py 的 _MEMORY_MERGE_PROMPT 同样的考量——
# 这是 DedupEngine 自己用的内部裁决 prompt，不是面向
# 用户的 Extractor prompt，放在这里自含，不需要 dedup.py
# 和 prompts.py 交叉依赖。
# =====================================================

_DEDUP_ARBITRATION_PROMPT = """你是一个记忆判重裁决助手。

你会收到两条关于同一个用户的记忆，它们的向量/文字相似度很高，但不确定它们究竟是:

1. duplicate  -- 同一件事的重复表达，换个说法或者多说了一遍，没有新信息
2. update     -- 新记忆是对旧记忆的更新/修正，旧信息已经不再成立，应该用新的取代旧的
3. different  -- 表面相似，但其实是两件独立的事情/互补信息，两条都应该保留

只输出一个 JSON，不要任何其他文字:

{"verdict": "duplicate" 或 "update" 或 "different"}
"""