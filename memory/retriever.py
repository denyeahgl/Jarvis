"""
memory/retriever.py

Jarvis Memory Retriever

Day14 Semantic Retrieval

优先:

Query
 |
BGE
 |
FAISS
 |
memory_id
 |
SQLite


Fallback:

Old Store
 |
cosine similarity

"""


from typing import List


import numpy as np



from memory.schema import MemoryItem




class MemoryRetriever:



    def __init__(
        self,
        store=None,
        vector_store=None,
        database=None,
        embedding=None,
    ):


        self.store = store

        self.vector_store = vector_store

        self.database = database

        self.embedding = embedding





    # ==================================================
    # Main Search
    # ==================================================


    def search(
        self,
        query: str,
        limit: int = 5,
    ) -> List[MemoryItem]:


        """
        优先使用 FAISS

        失败则 fallback
        """



        # -------------------------
        # FAISS Semantic Search
        # -------------------------


        if (
            self.vector_store
            and self.embedding
        ):


            try:

                return self.semantic_search(
                    query,
                    limit
                )


            except Exception:

                pass




        # -------------------------
        # fallback
        # -------------------------


        return self.keyword_search(
            query,
            limit
        )





    # ==================================================
    # Day14 Semantic Search
    # ==================================================


    def semantic_search(
        self,
        query: str,
        limit: int = 5,
    ):


        vector = self.embedding.encode(
            query
        )



        results = self.vector_store.search(
            vector,
            top_k=limit
        )

        print(
            "FAISS RESULT:",
            results
        )



        memories=[]



        for result in results:


            memory_id = result[
                "memory_id"
            ]



            # SQLite

            if self.database:


                data = self.database.get(
                    memory_id
                )


                if data:


                    memories.append(
                        self._dict_to_memory(
                            data
                        )
                    )



            # fallback JSON

            elif self.store:


                item = self._find_from_store(
                    memory_id
                )


                if item:

                    memories.append(
                        item
                    )



        return memories





    # ==================================================
    # Old Retrieval fallback
    # ==================================================


    def keyword_search(
        self,
        query: str,
        limit: int = 5,
    ):


        if not self.store:

            return []



        memories = self.store.get_all()



        query_words = set(
            query.lower().split()
        )



        scored=[]



        for memory in memories:


            text = memory.content.lower()


            score = sum(
                1
                for word in query_words
                if word in text
            )



            scored.append(
                (
                    score,
                    memory
                )
            )



        scored.sort(
            key=lambda x:x[0],
            reverse=True
        )



        return [
            item[1]
            for item in scored[:limit]
        ]





    # ==================================================
    # Helpers
    # ==================================================


    def _dict_to_memory(
        self,
        data: dict
    ) -> MemoryItem:


        return MemoryItem(

            id=data["id"],

            content=data["content"],

            memory_type=data.get(
                "memory_type"
            ),

            importance=data.get(
                "importance",
                1
            ),

            created_at=data.get(
                "created_at"
            ),

            updated_at=data.get(
                "updated_at"
            ),

        )





    def _find_from_store(
        self,
        memory_id
    ):


        if not self.store:

            return None



        memories = self.store.get_all()



        for memory in memories:

            if memory.id == memory_id:

                return memory



        return None





    # ==================================================
    # Utility
    # ==================================================


    def count(self):

        if self.store:

            return len(
                self.store.get_all()
            )


        return 0