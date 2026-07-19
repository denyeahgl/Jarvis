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
from memory.dedup import DedupEngine
from memory.conflict import MemoryConflictDetector
from memory.merge import MergeEngine
from memory.decision import MemoryDecisionEngine
from memory.schema import MemoryItem
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


        # =========================
        # Day15 Memory Dedup
        # =========================

        self.dedup_engine = DedupEngine(
            threshold=0.85
        )


        self.conflict_detector = MemoryConflictDetector(

            vector_store=self.vector_store,

            embedding=self.embedding,

            database=self.database

        )


        # Day17 / Phase 2
        # 互补信息合并
        #
        # 默认不注入 chat_json_fn，走规则版拼接兜底；
        # 后续如果要接 LLM 摘要合并，在这里传入
        # core.llm.chat_json 即可（和 extractor.py 的
        # 依赖注入方式保持一致）。

        self.merge_engine = MergeEngine()


        self.decision_engine = MemoryDecisionEngine(

            dedup=self.dedup_engine,

            conflict=self.conflict_detector,

            merge=self.merge_engine,

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

            saved_count = 0
            for item in items:


                # ======================
                # Day17 / Phase 2 Bugfix
                #
                # 这里必须先算一次 item.embedding，再去查候选/
                # 做决策——之前的写法是"决策完了才生成
                # embedding"，导致 DedupEngine / MergeEngine /
                # MemoryConflictDetector 里所有依赖
                # new_memory.embedding 的余弦相似度计算，
                # 拿到的都是 MemoryItem 默认的空列表 []
                # （`if not new_memory.embedding: return 0.0`），
                # 相当于把三者的向量信号全部悄悄短路成 0——
                # UPDATE(entity_key 那条不受影响) 以外的
                # CONFLICT / MERGE 分支因此实际上永远不会命中。
                #
                # 如果 MERGE 命中，下面 MERGE 分支会替换
                # item.content，这里的 embedding 会在存储前
                # 重新生成一次，不会存错向量。
                # ======================


                item.embedding = self.embedding.encode(
                    item.content
                )



                # ======================
                # Day15.4 Decision Engine
                #
                # 注意:
                #
                # 这里查候选Memory是给
                # Dedup / Conflict 用的，
                # 不是给用户看的检索结果。
                #
                # 所以不能用 self.retriever.search()
                # (它是 RetrievalScorer 混合排序,
                #  且会触发 lifecycle.touch(),
                #  污染 importance / access_count)
                #
                # 直接用 vector_store 做纯embedding
                # 相似度召回。
                # ======================


                candidate_items = self._get_candidates(
                    item
                )



                decision = self.decision_engine.decide(

                    item,

                    candidate_items

                )



                self.logger.info(
                    f"Memory Decision: "
                    f"{decision.decision.value}"
                )



                if decision.decision.value == "duplicate":


                    self.logger.info(
                        f"跳过重复Memory: {item.content}"
                    )

                    continue



                # ======================
                # Day17 / Phase 2
                #
                # UPDATE / CONFLICT / MERGE 分支处理
                #
                # supersede_target_id 不为 None 时，说明这条
                # 新记忆入库之后，需要把某条旧记忆标记为
                # superseded（版本链），而不是物理删除它。
                # ======================


                supersede_target_id = None


                if decision.decision.value == "update":

                    # 结构化 entity_key 命中：同一槽位的新值，
                    # 走版本链——旧记忆不删除，只标记
                    # superseded，新记忆正常入库，
                    # parent_id 指向旧记忆。

                    supersede_target_id = (
                        decision.target_memory_id
                    )

                    item.parent_id = supersede_target_id

                    self.logger.info(
                        f"Memory Update: "
                        f"entity_key={item.entity_key} "
                        f"旧记忆 {supersede_target_id} "
                        f"-> 新记忆 {item.id}"
                    )


                elif decision.decision.value == "merge":

                    # 互补信息：先把新记忆内容替换成合并后的
                    # 内容，再按 update 的方式走版本链
                    # （旧记忆 superseded）。

                    old_memory = self._find_candidate(
                        candidate_items,
                        decision.target_memory_id,
                    )

                    if old_memory is not None:

                        merged_content = (
                            self.merge_engine.merge(
                                item,
                                old_memory,
                            )
                        )

                        self.logger.info(
                            f"Memory Merge: "
                            f"{old_memory.content!r} + "
                            f"{item.content!r} -> "
                            f"{merged_content!r}"
                        )

                        item.content = merged_content

                        supersede_target_id = old_memory.id

                        item.parent_id = supersede_target_id

                    else:

                        # 候选在这一轮循环里丢了
                        # （理论上不该发生，比如同一批
                        # extract 出多条记忆、前一条已经
                        # 把这条候选 supersede 掉了）。
                        # 降级为普通 New，不能让整条流程
                        # 因为一次内部查找失败就崩掉。

                        self.logger.error(
                            f"Merge目标记忆 "
                            f"{decision.target_memory_id} "
                            f"未在候选中找到，降级为New"
                        )


                elif decision.decision.value == "conflict":

                    # 冲突：不覆盖、不合并，两条并存，
                    # 只记录日志留痕，交给上层
                    # （用户/后续人工审阅）决定，
                    # 而不是像之前那样静默吃掉。

                    self.logger.warning(
                        f"Memory Conflict: "
                        f"旧记忆({decision.target_memory_id}) "
                        f"与新记忆冲突: {item.content!r} "
                        f"reason={decision.reason}"
                    )



                # ======================
                # Generate Embedding
                #
                # 放在决策处理之后：MERGE 分支可能已经
                # 把 item.content 换成合并后的内容，
                # embedding 必须按最终 content 重新生成，
                # 否则向量和实际存的文字对不上。
                # ======================


                vector = self.embedding.encode(
                    item.content
                )


                item.embedding = vector



                # ======================
                # Old JSON Store
                # ======================


                self.store.add(
                    item
                )



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

                saved_count += 1



                # ======================
                # 版本链: 标记旧记忆 superseded
                #
                # 必须放在新记忆已经 add() 完之后调用——
                # mark_superseded() 里对新记忆那一侧的
                # UPDATE 语句要求这一行已经存在于表里。
                # ======================


                if supersede_target_id:

                    self.database.mark_superseded(
                        supersede_target_id,
                        item.id,
                    )


        except Exception as e:


            self.logger.error(
                f"Memory Store失败: {e}"
            )


            return False


        
        self.logger.info(
            f"保存长期记忆 {saved_count} 条 (JSON + SQLite + FAISS)"
        )



        return True




    # ==================================================
    # Day15.4 Candidate Lookup (Dedup / Conflict only)
    # ==================================================


    def _get_candidates(
        self,
        item,
        top_k: int = 5,
    ):
        """
        为 Dedup / Conflict 查候选Memory。

        与 self.retriever.search() 的区别:

        retriever.search():
            面向用户检索，走 RetrievalScorer
            (semantic + importance + confidence 混排)，
            并且会调用 lifecycle.touch() 强化
            access_count / importance —— 这是给
            "用户确实用到了这条记忆" 场景用的。

        _get_candidates():
            纯 embedding 相似度召回，只是内部用来
            判断新Memory是否重复/冲突，不代表这条
            旧Memory真的被检索/使用了，
            所以不应该触发 lifecycle 强化。
        """

        candidate_items = []

        seen_ids = set()


        # ======================
        # Day18 / Phase 3
        #
        # 结构化 entity_key 精确匹配优先：如果这条新记忆有
        # entity_key，先直接按 key 去查有没有同槽位的旧记忆，
        # 不依赖向量召回——向量召回是有 top_k 上限的近似搜索，
        # 同一个 entity_key 的旧记忆完全可能因为遣词造句差异
        # 没被召回进 top_k，那样的话下面 decision.py 里的
        # entity_key 匹配就形同虚设。这里查到的结果无条件加入
        # 候选池（不受 top_k 限制），后面向量召回的结果会用
        # seen_ids 去重，不会重复出现。
        # ======================

        entity_key = getattr(
            item,
            "entity_key",
            None,
        )

        if entity_key and self.database:

            for data in self.database.find_by_entity_key(
                entity_key,
                active_only=True,
            ):

                memory_item = MemoryItem.from_dict(
                    data
                )

                if memory_item.id in seen_ids:

                    continue

                vector = self.vector_store.get_vector(
                    memory_item.id
                ) if self.vector_store else None

                if vector:

                    memory_item.embedding = vector

                candidate_items.append(
                    memory_item
                )

                seen_ids.add(
                    memory_item.id
                )


        if (
            self.vector_store is None
            or self.embedding is None
        ):

            return candidate_items



        try:

            vector = self.embedding.encode(
                item.content
            )


            raw_hits = self.vector_store.search(
                vector,
                top_k=top_k
            )


        except Exception as e:

            self.logger.error(
                f"Candidate Search失败: {e}"
            )

            return candidate_items



        for hit in raw_hits:


            memory_id = hit.get(
                "memory_id"
            )


            if not memory_id:

                continue


            if memory_id in seen_ids:

                # 已经在上面 entity_key 精确匹配里加过了，
                # 不重复加入候选池。
                continue



            data = self.database.get(
                memory_id
            )


            if not data:

                continue



            memory_item = MemoryItem.from_dict(
                data
            )


            # Day17 / Phase 2
            #
            # 已经被 supersede/archive 掉的旧记忆不应该
            # 再参与判重/更新/冲突/合并的候选池——
            # 它们已经不是"当前有效"的记忆了，让它们继续
            # 参与判断，只会导致新记忆被错误地拿去和一条
            # 早就过期的旧记忆比较。
            #
            # 注意：FAISS 里这条旧记忆的向量目前还没有被
            # 物理删除（vector_store 还没有 delete 能力，
            # 属于遗留 TODO），所以它依然会被召回进
            # raw_hits，这里必须显式过滤掉，否则上面这条
            # "只挡不删"的设计就名存实亡。

            if memory_item.status != "active":

                continue



            # 从 FAISS 恢复 embedding
            # (SQLite 里不存 embedding)

            vector = self.vector_store.get_vector(
                memory_id
            )


            if vector:

                memory_item.embedding = vector



            candidate_items.append(
                memory_item
            )

            seen_ids.add(
                memory_item.id
            )



        return candidate_items



    # ==================================================
    # Day17 / Phase 2: Candidate Lookup by id
    # ==================================================


    def _find_candidate(
        self,
        candidate_items,
        memory_id,
    ):
        """
        在已经查好的候选列表里按 id 找一条 MemoryItem。

        MERGE 分支需要拿到旧记忆的完整对象（content +
        embedding）才能调用 merge_engine.merge()，而
        DecisionResult.target_memory_id 只有一个 id 字符串，
        所以要在 candidate_items 里查一次，不重新查库。
        """

        if not memory_id:

            return None

        for candidate in candidate_items:

            if candidate.id == memory_id:

                return candidate

        return None




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