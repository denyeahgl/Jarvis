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

        Day19.1 Bugfix:

        如果一条记忆有 parent_id（说明它是从旧记忆更新/合并
        而来的），把它的历史版本也带上，格式类似
        "现在的事实 (此前: 更早的事实)"。

        不这样做的话，"用户是广西大学学生" superseded 掉
        "用户是一名高中生" 之后，"我上大学前是什么身份"这类
        问题永远答不出来——旧记忆并没有被物理删除，只是
        检索默认只看 status="active"，历史版本无处可查。
        这里不去猜"用户是不是在问历史"，而是让历史版本始终
        跟着它对应的当前事实一起出现在 context 里，
        由下游的LLM自己判断要不要用。
        """

        lines = []


        for memory in memories:

            line = f"- {memory.content}"


            parent_id = getattr(
                memory, "parent_id", None
            )

            if parent_id and self.retriever:

                history = self.retriever.get_history(
                    parent_id
                )

                if history:

                    history_text = "；".join(
                        m.content for m in history
                    )

                    line += (
                        f"（此前: {history_text}）"
                    )


            lines.append(
                line
            )


        context = (
            "User memories:\n"
            +
            "\n".join(lines)
        )


        return context