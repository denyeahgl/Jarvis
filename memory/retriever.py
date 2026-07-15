"""
retriever.py

Memory Retrieval

负责从长期记忆中寻找相关内容
"""

import jieba
import logging


# 关闭 jieba 内部 DEBUG 输出
jieba_logger = logging.getLogger("jieba")
jieba_logger.setLevel(logging.WARNING)



class MemoryRetriever:

    def __init__(self, store):
        self.store = store


    def search(self, query: str, limit=5):

        if not query or not query.strip():
            return []

        memories = self.store.get_all()

        if not memories:
            return []


        query_words = set(
            jieba.cut(query.strip())
        )

        query_words = {
            w for w in query_words
            if len(w) > 1
        }


        results = []


        for memory in memories:

            content = memory.content.strip()

            if not content:
                continue


            content_words = set(
                jieba.cut(content)
            )

            content_words = {
                w for w in content_words
                if len(w) > 1
            }


            common = query_words & content_words

            # 必须至少有一个关键词交集才算相关，
            # 否则单靠 importance*0.2 也会让完全无关的记忆被召回
            if not common:
                continue

            score = len(common) + memory.importance * 0.2

            results.append(
                (score, memory)
            )


        results.sort(
            key=lambda x:x[0],
            reverse=True
        )


        return [
            item[1]
            for item in results[:limit]
        ]