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

        self.filter = MemoryFilter()

        self.scorer = MemoryScorer()

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
        memory_type="conversation",

    ):
        """
        保存长期记忆
        """
        if not self.filter.should_remember(
            content
        ):
            return
        
        

        importance = self.scorer.score(content)

        if importance <= 0:
            return

 
        memory = MemoryItem(
            content=content,
            memory_type=memory_type,
            importance=importance
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