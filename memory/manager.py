"""
manager.py

Jarvis Memory Manager

负责统一管理：

1. Conversation Memory（短期记忆）
2. Long-term Memory（长期记忆）
3. Memory Retrieval（记忆检索）
4. Memory Context（上下文构建）
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

        # ==========================
        # Short-Term Memory
        # ==========================

        self.history = MessageHistory()

        # ==========================
        # Long-Term Memory
        # ==========================

        self.store = MemoryStore()

        self.retriever = MemoryRetriever(
            store=self.store
        )

        # ==========================
        # Context Builder
        # ==========================

        self.context_builder = MemoryContextBuilder(
            retriever=self.retriever
        )

        # ==========================
        # Memory Pipeline
        # ==========================

        self.classifier = MemoryClassifier()
        self.extractor = MemoryExtractor()
        self.filter = MemoryFilter()
        self.scorer = MemoryScorer()

    # =====================================================
    # Conversation Memory
    # =====================================================

    def add_system(self, content: str):
        self.history.add_system(content)

    def add_user(self, content: str):
        self.history.add_user(content)

    def add_assistant(self, content: str):
        self.history.add_assistant(content)

    def get_messages(self):
        return self.history.get_messages()

    def clear_history(self):
        self.history.clear()

    # =====================================================
    # Context
    # =====================================================
# =====================================================
# Memory Context
# =====================================================

    def build_memory_context(
        self,
        user_input: str,
        limit: int = 5,
    ):
        """
        构建长期记忆上下文。

        Parameters
        ----------
        user_input : str
            当前用户输入。

        limit : int
            最大召回数量。

        Returns
        -------
        str | None
            Memory Context 文本。
        """

        return self.context_builder.build(
            query=user_input,
            limit=limit,
        )


    # =====================================================
    # Long-Term Memory
    # =====================================================

    def remember_if_needed(
        self,
        content: str,
        source: str = "user",
    ) -> bool:
        """
        智能保存长期记忆。

        Pipeline

            Input
                │
                ▼
          Classifier
                │
                ▼
          Extractor
                │
                ▼
            Filter
                │
                ▼
            Scorer
                │
                ▼
             Store

        Returns
        -------
        bool
            是否成功写入长期记忆
        """

        memory_type = self.classifier.classify(content)

        # classifier 可以主动拒绝记忆
        if memory_type is None:
            return False

        fragments = self.extractor.extract(content)

        items = []

        for fragment in fragments:

            if not self.filter.should_remember(fragment):
                continue

            importance = self.scorer.score(
                fragment,
                memory_type,
            )

            if importance <= 0:
                continue

            items.append(
                MemoryItem(
                    content=fragment,
                    memory_type=memory_type,
                    importance=importance,
                    source=source,
                )
            )

        if not items:
            return False

        self.store.add_batch(items)

        return True

    # 为兼容旧代码保留接口
    def remember(
        self,
        content: str,
        source: str = "user",
    ):
        return self.remember_if_needed(
            content=content,
            source=source,
        )

    # =====================================================
    # Retrieval
    # =====================================================

    def recall(self):
        """
        返回全部长期记忆。
        """
        return self.store.get_all()

    def search_memory(
        self,
        query: str,
        limit: int = 5,
    ):
        """
        根据查询检索长期记忆。
        """
        return self.retriever.search(
            query=query,
            limit=limit,
        )