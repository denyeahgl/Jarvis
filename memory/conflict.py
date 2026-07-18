"""
memory/conflict.py

Jarvis Memory Conflict Detector

Day15.4.1 / Day15.4.2

功能:

检测新Memory是否和已有Memory存在冲突


Pipeline:

New Memory

    ↓

(优先使用外部传入的 candidates)

    或

Embedding -> FAISS Similar Memories

    ↓

Conflict Rule

    ↓

ConflictResult


注意:

这里只负责检测

不负责解决

Resolver 在 Day15.4.2 实现

"""


from dataclasses import dataclass

import numpy as np



@dataclass
class ConflictResult:
    """
    Conflict Detection Result
    """


    is_conflict: bool = False


    similarity: float = 0.0


    old_memory: object = None


    new_memory: object = None


    reason: str = ""





class MemoryConflictDetector:


    def __init__(
        self,
        vector_store=None,
        embedding=None,
        database=None,
    ):


        self.vector_store = vector_store

        self.embedding = embedding

        self.database = database



        # Conflict 阈值
        #
        # Dedup:
        #     >0.9
        #
        # Conflict:
        #     同领域不同事实
        #
        self.similarity_threshold = 0.55






    # =====================================================
    # Main Conflict Check
    # =====================================================


    def check(
        self,
        memory,
        candidates=None,
    ) -> ConflictResult:


        """
        检查新Memory是否冲突


        参数:

            memory:
                新产生 MemoryItem

            candidates:
                Day15.4.2 新增

                外部(MemoryDecisionEngine)已经查好的
                候选MemoryItem列表 (已包含 embedding)。

                如果传入了 candidates，直接复用，
                不再重新查一次FAISS。

                如果为 None，回退到原来的
                自己查FAISS的逻辑（兼容旧调用方式）。


        返回:

            ConflictResult

        """


        if candidates:

            return self._check_with_candidates(
                memory,
                candidates,
            )


        return self._check_via_vector_store(
            memory
        )



    # =====================================================
    # Day15.4.2: Check Using External Candidates
    # =====================================================


    def _check_with_candidates(
        self,
        memory,
        candidates,
    ) -> ConflictResult:


        for old_memory in candidates:


            similarity = self._estimate_similarity(
                memory,
                old_memory
            )


            if similarity < self.similarity_threshold:

                continue


            # Debug

            print(
                "CONFLICT CHECK:",
                old_memory.content,
                "<->",
                memory.content,
                "similarity=",
                round(similarity, 4)
            )


            if self._detect_conflict(
                old_memory,
                memory
            ):


                return ConflictResult(

                    is_conflict=True,

                    similarity=similarity,

                    old_memory=old_memory,

                    new_memory=memory,

                    reason=(
                        "same topic "
                        "but different preference"
                    )

                )


        return ConflictResult(
            is_conflict=False
        )



    def _estimate_similarity(
        self,
        new_memory,
        old_memory,
    ) -> float:
        """
        基于 embedding 的余弦相似度。

        candidates 里的 MemoryItem 是
        manager._get_candidates() 补齐过
        embedding 字段的，如果没有 embedding
        (理论上不该发生)，返回 0。
        """

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
    # Fallback: Check Via Vector Store (原始逻辑，兼容旧调用)
    # =====================================================


    def _check_via_vector_store(
        self,
        memory,
    ) -> ConflictResult:


        if (
            self.vector_store is None
            or self.embedding is None
        ):


            return ConflictResult(
                is_conflict=False
            )



        # =================================================
        # Generate Embedding
        # =================================================


        vector = self.embedding.encode(
            memory.content
        )



        # =================================================
        # FAISS Search
        # =================================================


        results = self.vector_store.search(
            vector,
            top_k=10
        )



        if not results:


            return ConflictResult(
                is_conflict=False
            )



        # =================================================
        # Analyze Candidates
        # =================================================


        for result in results:


            similarity = float(
                result.get(
                    "score",
                    0
                )
            )



            if similarity < self.similarity_threshold:

                continue



            old_memory = self._load_memory(
                result["memory_id"]
            )



            if old_memory is None:

                continue



            # Debug

            print(
                "CONFLICT CHECK:",
                old_memory.content,
                "<->",
                memory.content,
                "similarity=",
                round(similarity,4)
            )



            if self._detect_conflict(
                old_memory,
                memory
            ):


                return ConflictResult(

                    is_conflict=True,

                    similarity=similarity,

                    old_memory=old_memory,

                    new_memory=memory,

                    reason=(
                        "same topic "
                        "but different preference"
                    )

                )



        return ConflictResult(
            is_conflict=False
        )







    # =====================================================
    # Conflict Rule
    # =====================================================


    def _detect_conflict(
        self,
        old_memory,
        new_memory,
    ):


        """
        第一版冲突规则:


        1.
        内容不能完全相同


        2.
        同时包含偏好关键词


        3.
        核心对象不同



        例:

        用户喜欢巴黎圣日耳曼

        用户喜欢皇家马德里


        => Conflict


        """



        old_text = (
            old_memory.content
            .lower()
        )


        new_text = (
            new_memory.content
            .lower()
        )



        # 完全相同

        if old_text == new_text:

            return False





        # =================================================
        # Preference Keywords
        # =================================================


        conflict_words = [

            "喜欢",

            "支持",

            "最喜欢",

            "讨厌",

            "现在",

        ]



        has_keyword = False



        for word in conflict_words:


            if (
                word in old_text
                and word in new_text
            ):

                has_keyword = True



        if not has_keyword:

            return False





        # =================================================
        # Chinese Text Overlap
        # =================================================


        common_chars = (
            set(old_text)
            &
            set(new_text)
        )


        overlap = len(
            common_chars
        )



        print(
            "CONFLICT OVERLAP:",
            overlap
        )



        #


        # 共同字符少:
        #
        # 用户喜欢巴黎圣日耳曼
        #
        # 用户喜欢皇家马德里
        #
        # 说明主体不同
        #

        if overlap <= 5:

            return True



        return False






    # =====================================================
    # Load Memory (仅供 fallback 分支使用)
    # =====================================================


    def _load_memory(
        self,
        memory_id
    ):


        if self.database is None:

            return None



        data = self.database.get(
            memory_id
        )



        if data is None:

            return None



        from memory.schema import MemoryItem



        return MemoryItem(

            id=data["id"],


            content=data["content"],


            embedding=data.get(
                "embedding",
                []
            ),


            memory_type=data.get(
                "memory_type",
                "fact"
            ),


            importance=float(
                data.get(
                    "importance",
                    3
                )
            ),


            source=data.get(
                "source",
                "user"
            ),


            confidence=float(
                data.get(
                    "confidence",
                    1.0
                )
            ),


            access_count=int(
                data.get(
                    "access_count",
                    0
                )
            ),


            last_accessed=data.get(
                "last_accessed"
            ),


            created_at=data.get(
                "created_at"
            ),


            updated_at=data.get(
                "updated_at"
            ),

        )