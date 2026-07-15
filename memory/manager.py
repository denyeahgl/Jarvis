"""
manager.py

Memory 管理中心

负责统一管理:

1. Conversation Memory
2. Persistent Memory
3. Memory Context
"""


from memory.history import MessageHistory
from memory.store import MemoryStore
from memory.schema import MemoryItem
from memory.retriever import MemoryRetriever
from memory.context import MemoryContextBuilder
from memory.filter import MemoryFilter
from memory.scorer import MemoryScorer
from memory.classifier import MemoryClassifier
from memory.extractor import MemoryExtractor



class MemoryManager:
    """
    Jarvis Memory Manager
    """


    def __init__(self):

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


        # =========================
        # Context Layer
        # =========================

        self.context_builder = MemoryContextBuilder(
            retriever=self.retriever
        )

        self.extractor = MemoryExtractor()
        self.filter = MemoryFilter()
        self.scorer = MemoryScorer()
        self.classifier = MemoryClassifier()


    # =========================
    # Conversation Memory
    # =========================


    def add_system(
        self,
        content: str
    ):
        """
        添加 System Prompt
        """

        self.history.add_system(
            content
        )



    def add_user(
        self,
        content: str
    ):
        """
        添加用户消息
        """

        self.history.add_user(
            content
        )



    def add_assistant(
        self,
        content: str
    ):
        """
        添加 Jarvis 回复
        """

        self.history.add_assistant(
            content
        )



    def get_messages(self):
        """
        获取当前对话历史
        """

        return self.history.get_messages()



    # =========================
    # Context Building
    # =========================


    def build_context(
        self,
        user_input=None,
        limit=5
    ):
        """
        构建当前 LLM 上下文。

        注意:

        返回的是临时 messages 副本。

        Memory Context 不会写入 history，
        避免污染长期对话。

        """

        messages = self.history.get_messages()



        if not user_input:
            return messages



        memory_context = self.context_builder.build(
            query=user_input,
            limit=limit
        )



        if memory_context:

            messages.insert(
                0,
                {
                    "role": "system",
                    "content": memory_context
                }
            )


        return messages



    def clear_history(self):
        """
        清空当前会话
        """

        self.history.clear()



    # =========================
    # Long Term Memory
    # =========================


    def remember(
        self,
        content: str,
    ):
        """
        保存长期记忆

        流程:

        Input
        |
        Extractor
        |
        Filter
        |
        Scorer
        |
        Classifier
        |
        Store
        """


        memories = self.extractor.extract(
            content
        )


        for memory_content in memories:


            if not self.filter.should_remember(
                memory_content
            ):
                continue


            memory_type = self.classifier.classify(
                memory_content
            )

            importance = self.scorer.score(
                memory_content,
                memory_type
            )


            if importance <= 0:
                continue


            memory = MemoryItem(
                content=memory_content,
                memory_type=memory_type,
                importance=importance,
                source="user"
            )


            self.store.add(
                memory
            )


    def recall(self):
        """
        获取全部长期记忆
        """

        return self.store.get_all()



    def search_memory(
        self,
        query: str,
        limit=5
    ):
        """
        根据关键词搜索 Memory
        """

        return self.retriever.search(
            query=query,
            limit=limit
        )