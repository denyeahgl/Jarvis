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


            for item in items:



                # ======================
                # Old JSON Store
                # ======================


                self.store.add(
                    item
                )



                # ======================
                # Generate Embedding
                # ======================


                vector = self.embedding.encode(
                    item.content
                )



                item.embedding = vector




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



        except Exception as e:


            self.logger.error(
                f"Memory Store失败: {e}"
            )


            return False




        self.logger.info(
            f"保存长期记忆 {len(items)} 条 (JSON + SQLite + FAISS)"
        )



        return True





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