"""
memory/manager.py

Jarvis Memory Manager

Day13 Migration Version


负责：

1. Conversation Memory
2. Long Term Memory Pipeline
3. Memory Retrieval
4. Context Support


Pipeline:

User Input

    ↓

MemoryExtractor (LLM)

    ↓

MemoryValidator

    ↓

MemoryStore


"""

from __future__ import annotations


from memory.history import MessageHistory


from memory.extractor import MemoryExtractor
from memory.validator import MemoryValidator


from memory.store import MemoryStore
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
        # =========================

        self.store = MemoryStore()


        self.retriever = MemoryRetriever(
            store=self.store
        )


        self.context_builder = MemoryContextBuilder(
            retriever=self.retriever
        )



        # =========================
        # Day13 Pipeline
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
        """
        添加 OpenAI 格式消息
        """

        self.history.add_message(
            message
        )



    def add_system(
        self,
        content: str,
    ):
        """
        添加 System Prompt
        """

        self.history.add_system(
            content
        )



    def add_user(
        self,
        content: str,
    ):
        """
        添加用户消息
        """

        self.history.add_user(
            content
        )



    def add_assistant(
        self,
        content: str,
    ):
        """
        添加助手消息
        """

        self.history.add_assistant(
            content
        )



    def get_messages(self):
        """
        Runtime / ContextBuilder 调用接口

        """

        return self.history.get_messages()



    def clear_history(self):

        self.history.clear()



    # ==================================================
    # Day13 Long Term Memory Pipeline
    # ==================================================

    def remember_if_needed(
        self,
        content: str,
        source: str = "user",
    ) -> bool:
        """
        LLM Memory Pipeline


        User Input

            ↓

        Extractor

            ↓

        Validator

            ↓

        Store


        """


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
        # --------------------------

        try:

            for item in items:

                self.store.add(
                    item
                )


        except Exception as e:

            self.logger.error(
                f"Memory Store失败: {e}"
            )

            return False



        self.logger.info(
            f"保存长期记忆 {len(items)} 条"
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
        """
        Agent ContextBuilder 兼容接口。

        参数兼容：

        user_input:
            Agent Runtime传入

        query:
            内部调用备用


        """

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