"""
memory/manager.py

Jarvis Memory Manager

Day14 Migration Version

新增:

- SQLite Metadata Storage
- BGE Embedding
- FAISS Vector Storage


Pipeline:

User Input

    ↓

MemoryExtractor

    ↓

MemoryValidator

    ↓

MemoryItem

    ↓

+----------------+
|                |
|                |

MemoryStore     SQLite

(JSON)          (Metadata)


                  ↓

              BGE Embedding

                  ↓

                FAISS


"""


from __future__ import annotations


from memory.history import MessageHistory


from memory.extractor import MemoryExtractor
from memory.validator import MemoryValidator


from memory.store import MemoryStore

from memory.database import MemoryDatabase

from memory.embedding import MemoryEmbedding

from memory.vector_store import VectorStore


from memory.retriever import MemoryRetriever
from memory.context import MemoryContextBuilder
from memory.dedup import DedupEngine
from memory.conflict import MemoryConflictDetector
from memory.decision import MemoryDecisionEngine
from memory.schema import MemoryItem
from core.logger import Logger




class MemoryManager:


    """
    Jarvis Memory Manager
    """



    def __init__(self):


        self.logger = Logger()



        # =========================
        # Short Term Memory
        # =========================


        self.history = MessageHistory()



        # =========================
        # Long Term Memory
        # Day14 Semantic Memory
        # =========================


        # 保留旧MemoryStore
        # 兼容Day13

        self.store = MemoryStore()



        # SQLite Metadata

        self.database = MemoryDatabase()



        # BGE Embedding

        self.embedding = MemoryEmbedding()



        # FAISS Vector Store

        self.vector_store = VectorStore(
            dimension=self.embedding.dimension
        )


        # =========================
        # Day15 Memory Dedup
        # =========================

        self.dedup_engine = DedupEngine(
            threshold=0.85
        )


        self.conflict_detector = MemoryConflictDetector(

            vector_store=self.vector_store,

            embedding=self.embedding,

            database=self.database

        )



        self.decision_engine = MemoryDecisionEngine(

            dedup=self.dedup_engine,

            conflict=self.conflict_detector

        )


        self.retriever = MemoryRetriever(
            store=self.store,
            vector_store=self.vector_store,
            database=self.database,
            embedding=self.embedding,
        )


        self.context_builder = MemoryContextBuilder(
            retriever=self.retriever
        )



        # =========================
        # Extract / Validate
        # =========================


        self.extractor = MemoryExtractor()


        self.validator = MemoryValidator()





    # ==================================================
    # Conversation Memory
    # ==================================================


    def add_message(
        self,
        message: dict,
    ):

        self.history.add_message(
            message
        )



    def add_system(
        self,
        content: str,
    ):

        self.history.add_system(
            content
        )



    def add_user(
        self,
        content: str,
    ):

        self.history.add_user(
            content
        )



    def add_assistant(
        self,
        content: str,
    ):

        self.history.add_assistant(
            content
        )



    def get_messages(self):

        return self.history.get_messages()



    def clear_history(self):

        self.history.clear()





    # ==================================================
    # Day14 Long Term Memory Pipeline
    # ==================================================


    def remember_if_needed(
        self,
        content: str,
        source: str = "user",
    ) -> bool:


        if not content:

            return False



        # --------------------------
        # Extract
        # --------------------------


        try:

            memories = self.extractor.extract(
                content
            )


        except Exception as e:

            self.logger.error(
                f"Memory Extract失败: {e}"
            )

            return False



        if not memories:

            return False




        # --------------------------
        # Validate
        # --------------------------


        try:

            items = self.validator.validate(
                memories,
                source=source,
            )


        except Exception as e:

            self.logger.error(
                f"Memory Validate失败: {e}"
            )

            return False



        if not items:

            return False





        # --------------------------
        # Store
        # Day14 Upgrade
        # --------------------------


        try:

            saved_count = 0
            for item in items:


                # ======================
                # Day15.4 Decision Engine
                #
                # 注意:
                #
                # 这里查候选Memory是给
                # Dedup / Conflict 用的，
                # 不是给用户看的检索结果。
                #
                # 所以不能用 self.retriever.search()
                # (它是 RetrievalScorer 混合排序,
                #  且会触发 lifecycle.touch(),
                #  污染 importance / access_count)
                #
                # 直接用 vector_store 做纯embedding
                # 相似度召回。
                # ======================


                candidate_items = self._get_candidates(
                    item
                )



                decision = self.decision_engine.decide(

                    item,

                    candidate_items

                )



                self.logger.info(
                    f"Memory Decision: "
                    f"{decision.decision.value}"
                )



                if decision.decision.value == "duplicate":


                    self.logger.info(
                        f"跳过重复Memory: {item.content}"
                    )

                    continue



                # ======================
                # Generate Embedding
                # ======================


                vector = self.embedding.encode(
                    item.content
                )


                item.embedding = vector



                # ======================
                # Old JSON Store
                # ======================


                self.store.add(
                    item
                )



                # ======================
                # SQLite Metadata
                # ======================


                self.database.add(
                    item.to_dict()
                )



                # ======================
                # FAISS Vector
                # ======================


                self.vector_store.add(
                    vector,
                    item.id
                )

                saved_count += 1


        except Exception as e:


            self.logger.error(
                f"Memory Store失败: {e}"
            )


            return False


        
        self.logger.info(
            f"保存长期记忆 {saved_count} 条 (JSON + SQLite + FAISS)"
        )



        return True




    # ==================================================
    # Day15.4 Candidate Lookup (Dedup / Conflict only)
    # ==================================================


    def _get_candidates(
        self,
        item,
        top_k: int = 5,
    ):
        """
        为 Dedup / Conflict 查候选Memory。

        与 self.retriever.search() 的区别:

        retriever.search():
            面向用户检索，走 RetrievalScorer
            (semantic + importance + confidence 混排)，
            并且会调用 lifecycle.touch() 强化
            access_count / importance —— 这是给
            "用户确实用到了这条记忆" 场景用的。

        _get_candidates():
            纯 embedding 相似度召回，只是内部用来
            判断新Memory是否重复/冲突，不代表这条
            旧Memory真的被检索/使用了，
            所以不应该触发 lifecycle 强化。
        """

        candidate_items = []


        if (
            self.vector_store is None
            or self.embedding is None
        ):

            return candidate_items



        try:

            vector = self.embedding.encode(
                item.content
            )


            raw_hits = self.vector_store.search(
                vector,
                top_k=top_k
            )


        except Exception as e:

            self.logger.error(
                f"Candidate Search失败: {e}"
            )

            return candidate_items



        for hit in raw_hits:


            memory_id = hit.get(
                "memory_id"
            )


            if not memory_id:

                continue



            data = self.database.get(
                memory_id
            )


            if not data:

                continue



            memory_item = MemoryItem.from_dict(
                data
            )



            # 从 FAISS 恢复 embedding
            # (SQLite 里不存 embedding)

            vector = self.vector_store.get_vector(
                memory_id
            )


            if vector:

                memory_item.embedding = vector



            candidate_items.append(
                memory_item
            )



        return candidate_items





    # ==================================================
    # Retrieval
    # ==================================================


    def search_memory(
        self,
        query: str,
        limit: int = 5,
    ):


        return self.retriever.search(
            query,
            limit=limit,
        )





    # ==================================================
    # Context
    # ==================================================


    def build_context(
        self,
        query: str,
        limit: int = 5,
    ):


        return self.context_builder.build(
            query,
            limit=limit,
        )




    def build_memory_context(
        self,
        user_input: str = None,
        query: str = None,
        limit: int = 5,
    ):


        if query is None:

            query = user_input



        return self.context_builder.build(
            query=query,
            limit=limit,
        )





    # ==================================================
    # Debug
    # ==================================================


    def get_all_memory(self):

        return self.store.get_all()





    # ==================================================
    # Day14 Placeholder
    # ==================================================


    def update_memory(
        self,
        memory_id,
        content,
    ):

        raise NotImplementedError




    def merge_memory(
        self,
        memory_ids,
    ):

        raise NotImplementedError




    def delete_memory(
        self,
        memory_id,
    ):

        raise NotImplementedError