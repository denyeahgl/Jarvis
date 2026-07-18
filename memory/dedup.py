"""
Memory Deduplication Engine 2.0

Multi Signal Dedup:

1. Embedding similarity
2. Text similarity
3. Entity overlap
4. Relation similarity


Day15.4
"""


from dataclasses import dataclass
from difflib import SequenceMatcher
import logging



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



# =====================================================
# Dedup Engine
# =====================================================


class DedupEngine:


    def __init__(
        self,
        threshold=0.85
    ):

        self.threshold = threshold

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


        return DedupResult(
            is_duplicate=False,
            confidence=best_score
        )



    # =================================================
    # Score
    # =================================================


    def _calculate_score(
        self,
        new,
        old
    ):


        scores=[]



        # -----------------------------
        # 1. Embedding similarity
        # -----------------------------

        if (

            hasattr(new,"embedding")

            and hasattr(old,"embedding")

            and new.embedding

            and old.embedding

        ):

            scores.append(

                self._cosine(

                    new.embedding,

                    old.embedding

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


        scores.append(
            text_score
        )



        # -----------------------------
        # 3. Entity overlap
        # -----------------------------

        entity_score = (

            self._entity_similarity(

                new,

                old

            )

        )


        scores.append(
            entity_score
        )



        # -----------------------------
        # 4. Relation similarity
        # -----------------------------

        relation_score = (

            self._relation_similarity(

                new,

                old

            )

        )


        scores.append(
            relation_score
        )



        # weighted average

        weights=[

            0.5, # embedding

            0.2, # text

            0.2, # entity

            0.1  # relation

        ]



        score=sum(

            s*w

            for s,w in zip(
                scores,
                weights
            )

        )


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