"""
Memory Context Builder

负责:

Memory -> LLM Context

将长期记忆转换为 Prompt 可使用的上下文。
"""


class MemoryContextBuilder:
    """
    Memory Context 构建器
    """


    def __init__(
        self,
        retriever
    ):
        """
        retriever:
            MemoryRetriever实例
        """

        self.retriever = retriever



    def build(
        self,
        query: str,
        limit=5
    ):
        """
        根据当前用户输入，
        检索相关 Memory 并生成 Context
        """

        if not query:
            return None


        memories = self.retriever.search(
            query=query,
            limit=limit
        )


        if not memories:
            return None


        return self.format(
            memories
        )



    def format(
        self,
        memories
    ):
        """
        MemoryItem列表
        转换成 Prompt文本
        """

        lines = []


        for memory in memories:

            lines.append(
                f"- {memory.content}"
            )


        context = (
            "User memories:\n"
            +
            "\n".join(lines)
        )


        return context