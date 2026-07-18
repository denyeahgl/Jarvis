"""
memory/retriever.py

Jarvis Memory Retriever

Day15.3

Features:

Day15.2:
- Semantic Retrieval
- Importance-aware Ranking


Day15.3:
- Memory Lifecycle
- Access Reinforcement
- Persistence Update



Pipeline:


Query

 |

Embedding

 |

FAISS Candidate Search

 |

Memory Metadata

 |

Retrieval Scorer

 |

Ranking

 |

Lifecycle Touch

 |

SQLite Update

 |

Return Memory


"""


from typing import List


from memory.schema import MemoryItem

from memory.retrieval_scorer import RetrievalScorer

from memory.lifecycle import MemoryLifecycle





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



        # Day15.2
        # Importance Ranking

        self.scorer = RetrievalScorer()



        # Day15.3
        # Memory Lifecycle

        self.lifecycle = MemoryLifecycle()





    # ==================================================
    # Main Search
    # ==================================================


    def search(
        self,
        query: str,
        limit: int = 5,
    ) -> List[MemoryItem]:


        """
        Semantic Search 优先

        fallback keyword
        """


        if (
            self.vector_store
            and self.embedding
        ):


            try:

                return self.semantic_search(
                    query,
                    limit
                )


            except Exception as e:


                print(
                    "Semantic Search Error:",
                    e
                )



        return self.keyword_search(
            query,
            limit
        )





    # ==================================================
    # Semantic Search
    # Day15.2 + Day15.3
    # ==================================================


    def semantic_search(
        self,
        query: str,
        limit: int = 5,
    ):



        vector = self.embedding.encode(
            query
        )



        # -------------------------
        # Candidate Retrieval
        # -------------------------


        candidate_k = limit * 3


        results = self.vector_store.search(
            vector,
            top_k=candidate_k
        )



        print(
            "FAISS RESULT:",
            results
        )



        scored_memories = []



        # -------------------------
        # Load Metadata
        # -------------------------


        for result in results:



            memory_id = result[
                "memory_id"
            ]


            semantic_score = result.get(
                "score",
                0
            )



            memory = None



            # SQLite

            if self.database:


                data = self.database.get(
                    memory_id
                )


                if data:

                    memory = self._dict_to_memory(
                        data
                    )



            # JSON fallback

            elif self.store:


                memory = self._find_from_store(
                    memory_id
                )



            if memory:



                final_score = self.scorer.score(
                    memory,
                    semantic_score
                )



                print(
                    "MEMORY SCORE:",
                    memory.content,
                    final_score
                )



                scored_memories.append(
                    (
                        final_score,
                        memory
                    )
                )





        # -------------------------
        # Ranking
        # -------------------------


        scored_memories.sort(
            key=lambda x:x[0],
            reverse=True
        )



        # -------------------------
        # Day15.3 Lifecycle Touch
        # -------------------------


        final_memories=[]



        for score, memory in scored_memories[:limit]:


            # Memory 被使用

            memory = self.lifecycle.touch(
                memory
            )



            # 保存生命周期状态

            if self.database:


                self.database.update_memory(
                    memory
                )



            final_memories.append(
                memory
            )



        return final_memories





    # ==================================================
    # Keyword fallback
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



        final=[]



        for score,memory in scored[:limit]:


            memory = self.lifecycle.touch(
                memory
            )


            if self.database:

                self.database.update_memory(
                    memory
                )


            final.append(
                memory
            )



        return final





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
                3.0
            ),


            confidence=float(
                data.get(
                    "confidence",
                    1.0
                )
            ),

            access_count=int(
                data.get(
                    "access_count",
                    0
                )
            ),

            last_accessed=data.get(
                "last_accessed"
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