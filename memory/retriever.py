"""
retriever.py

Semantic Memory Retriever

负责：

1. Query Embedding
2. Semantic Retrieval
3. Cosine Similarity
4. Memory Ranking
5. Top-K Memory
"""


from math import sqrt

from memory.embedding import embedding_model
from memory.store import MemoryStore


class MemoryRetriever:
    """Semantic Memory Retriever"""


    # Memory Ranking 权重
    #
    # Day11.5:
    #
    # semantic:
    #   语义相关程度
    #
    # importance:
    #   记忆重要程度
    #
    # Future:
    #   recency
    #   access_count
    #
    SCORE_WEIGHTS = {
        "semantic": 0.8,
        "importance": 0.2,
    }


    def __init__(
        self,
        store: MemoryStore | None = None,
        embedding=None,
    ):

        self.store = store or MemoryStore()

        # embedding.py 里导出的是全局单例 embedding_model（EmbeddingModel 实例），
        # 而不是一个叫 Embedding 的类，这里复用单例即可。
        self.embedding = embedding or embedding_model



    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        threshold: float = 0.45,
    ):
        """
        根据 Query 检索长期记忆


        Args:

            query:
                用户问题

            top_k:
                返回数量

            threshold:
                最低语义相似度


        Returns:

            list[MemoryItem]

        """

        query = query.strip()


        if not query:
            return []


        memories = self.store.get_all()


        if not memories:
            return []



        # Query 向量化
        # EmbeddingModel 提供的统一接口方法名是 encode()，不是 embed()

        query_embedding = self.embedding.encode(
            query
        )


        ranked_memories = []



        for memory in memories:


            # 没有 embedding 的旧记忆跳过

            if not memory.embedding:
                continue



            semantic_score = self.cosine_similarity(
                query_embedding,
                memory.embedding,
            )



            # 过滤低相关记忆

            if semantic_score < threshold:
                continue



            final_score = self._calculate_score(
                semantic_score,
                memory,
            )


            ranked_memories.append(
                (
                    final_score,
                    memory,
                )
            )



        # 最终 Memory Ranking

        ranked_memories.sort(
            key=lambda x: x[0],
            reverse=True,
        )



        return [
            memory
            for _, memory in ranked_memories[:top_k]
        ]



    def search(
        self,
        query: str,
        limit: int = 5,
        threshold: float = 0.45,
    ):
        """
        兼容 MemoryManager / MemoryContextBuilder 的调用接口。

        它们调用的是 retriever.search(query=, limit=)，
        这里作为 retrieve() 的别名，仅做参数名转换。
        """

        return self.retrieve(
            query=query,
            top_k=limit,
            threshold=threshold,
        )



    def _calculate_score(
        self,
        semantic_score: float,
        memory,
    ) -> float:
        """
        Memory Ranking


        Day11.5:


        Final Score =


            semantic_score * 0.8

            +

            importance_score * 0.2


        """



        # importance 归一化

        importance_score = min(
            memory.importance / 10.0,
            1.0,
        )



        return (

            semantic_score
            *
            self.SCORE_WEIGHTS["semantic"]

            +

            importance_score
            *
            self.SCORE_WEIGHTS["importance"]

        )



    @staticmethod
    def cosine_similarity(
        vector_a: list[float],
        vector_b: list[float],
    ) -> float:
        """
        计算余弦相似度
        """


        if len(vector_a) != len(vector_b):

            return 0.0



        dot = sum(
            a * b
            for a, b in zip(
                vector_a,
                vector_b,
            )
        )



        norm_a = sqrt(
            sum(
                a * a
                for a in vector_a
            )
        )


        norm_b = sqrt(
            sum(
                b * b
                for b in vector_b
            )
        )



        if norm_a == 0 or norm_b == 0:

            return 0.0



        return dot / (
            norm_a * norm_b
        )