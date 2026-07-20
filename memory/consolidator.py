"""
memory/consolidator.py

Jarvis Memory Consolidator

Day19 (Phase 4: 定期整理)

职责:

即使写入时把关做得再严（Dedup / Update / Conflict / Merge，
Day15.4-Day18 已经做了），长期运行仍然会积累碎片化、语义
漂移的记忆——比如两条记忆各自都没有触发 write-time 的 MERGE
（entity_key 不同、或者当时向量召回 top_k 没刚好带出对方），
但放在一起看其实说的是同一件事。

这个模块负责"睡眠巩固"式的批处理维护，跑在写入路径之外，
按需（cron / 手动 / 外部调度器）周期性触发：

1. Cluster + Merge
   对全部 active 记忆按向量相似度做聚类，同一簇内容合并成
   一条更完整的记忆，旧记忆标记 superseded（复用 Day17 的
   版本链机制，不做物理删除）。

2. Decay + Archive
   对全部 active 记忆做一次时间衰减 (MemoryLifecycle.decay)，
   衰减到阈值以下的标记 archived
   (MemoryLifecycle.should_archive)。

   这两个方法在 Day15.3 就写好了，但从来没有被真正调用过——
   本模块就是那个"调度者"。

3. 可追溯日志
   合并/归档都不是物理删除，但"哪些旧记忆去了哪"这件事本身
   如果不记下来，事后调试/复盘就无从查起。run() 返回一份
   结构化日志，调用方可以自己决定落盘/打印/上报。

不负责:

- 什么时候触发（本模块只提供 run()，接入 cron / APScheduler /
  手动脚本都可以，具体选哪种取决于部署环境，这里不做假设）
- Dedup / Conflict / Merge 的写入时判断逻辑（那是 dedup.py /
  conflict.py / merge.py / decision.py 的职责，本模块只处理
  已经躺在库里的存量数据）
"""


from __future__ import annotations


import logging
from datetime import datetime, timezone


from memory.schema import MemoryItem
from memory.lifecycle import MemoryLifecycle



class MemoryConsolidator:


    def __init__(
        self,
        database,
        vector_store,
        embedding,
        merge_engine,
        lifecycle: MemoryLifecycle | None = None,
        cluster_threshold: float = 0.80,
    ):
        """
        database / vector_store / embedding / merge_engine:

            和 MemoryManager 共用同一套实例，不重新建连接，
            避免 SQLite/FAISS 出现两份不同步的状态。

        lifecycle:

            不传时自己创建一个默认的 MemoryLifecycle()——
            和 MemoryRetriever 的写法保持一致。

        cluster_threshold:

            聚类用的向量相似度阈值。故意比 DedupEngine 的
            duplicate 阈值(0.85)低一些、比 MergeEngine 的
            min_similarity(0.55)高一些：写入时该拦住的重复
            早就被 Dedup 拦住了，这里要抓的是"当时没拦住、
            现在放一起看确实很像"的存量碎片，用一个居中的
            阈值，避免既抓不到（太高）又抓错（太低，把只是
            同类型但内容不同的记忆也聚到一起）。
        """

        self.database = database

        self.vector_store = vector_store

        self.embedding = embedding

        self.merge_engine = merge_engine

        self.lifecycle = lifecycle or MemoryLifecycle()

        self.cluster_threshold = cluster_threshold

        self.logger = logging.getLogger(
            __name__
        )



    # =================================================
    # Public API
    # =================================================

    def run(self) -> dict:
        """
        跑一次完整的定期整理。

        顺序: 先 Decay/Archive，再 Cluster/Merge。

        这个顺序是刻意的: 如果反过来（先合并再衰减），
        刚合并出来的新记忆会在同一轮里立刻被衰减一次，
        它其实还没有"活"过一轮就被打了一次时间折扣，
        不合理。先衰减存量、再合并，合并出来的新记忆
        要等下一轮才会被衰减，这样比较符合"新生成的记忆
        应该有一个完整的生命周期"的直觉。

        返回一份结构化日志，不在这里做任何输出/持久化决定
        （打印/写文件/上报监控都交给调用方）。
        """

        log = {

            "started_at": self._now_iso(),

            "decayed": [],

            "archived": [],

            "merged": [],

            "errors": [],

        }


        try:

            self._decay_and_archive_pass(
                log
            )

        except Exception as e:

            self.logger.error(
                f"Decay/Archive pass失败: {e}"
            )

            log["errors"].append(
                f"decay_and_archive: {e}"
            )


        try:

            self._cluster_merge_pass(
                log
            )

        except Exception as e:

            self.logger.error(
                f"Cluster/Merge pass失败: {e}"
            )

            log["errors"].append(
                f"cluster_merge: {e}"
            )


        log["finished_at"] = self._now_iso()

        self.logger.info(
            f"Consolidation完成: "
            f"decayed={len(log['decayed'])} "
            f"archived={len(log['archived'])} "
            f"merged={len(log['merged'])} "
            f"errors={len(log['errors'])}"
        )

        return log



    # =================================================
    # Pass 1: Decay + Archive
    # =================================================

    def _decay_and_archive_pass(
        self,
        log: dict,
    ):
        """
        对全部 active 记忆做一次时间衰减，衰减后低于阈值的
        标记 archived。

        注意: decay() 每次调用都会让 importance 乘一次
        decay_rate，所以这个 pass 多久跑一次，直接决定了
        "记忆多久不用会被遗忘"——调度频率本身就是一个需要
        跟 decay_rate 一起调的参数，不是这个模块能替你决定的，
        这里只负责"调度到了就真的执行"。
        """

        rows = self.database.list_by_status(
            "active"
        )

        for row in rows:

            memory = MemoryItem.from_dict(
                row
            )

            memory = self.lifecycle.decay(
                memory
            )

            # 只有 importance 变了，其余生命周期字段
            # (access_count/last_accessed) 原样透传，
            # 复用 Day15.3 已有的 update_memory()，
            # 不新造一个只更新 importance 的方法。

            self.database.update_memory(
                memory
            )

            log["decayed"].append(
                {
                    "id": memory.id,
                    "content": memory.content,
                    "importance": memory.importance,
                }
            )


            if self.lifecycle.should_archive(
                memory
            ):

                self.database.mark_archived(
                    memory.id
                )

                log["archived"].append(
                    {
                        "id": memory.id,
                        "content": memory.content,
                        "importance": memory.importance,
                    }
                )

                self.logger.info(
                    f"Memory Archived: "
                    f"{memory.content} "
                    f"(importance={memory.importance})"
                )



    # =================================================
    # Pass 2: Cluster + Merge
    # =================================================

    def _cluster_merge_pass(
        self,
        log: dict,
    ):
        """
        对全部 active 记忆按向量相似度聚类，
        同一簇（>=2 条）合并成一条，旧记忆标记 superseded。

        注意: 上面 Decay/Archive 那一步可能已经把一部分
        记忆状态改成了 archived，这里重新查一次
        "active"，天然就不会把刚被归档的记忆也拉进来聚类——
        不需要额外过滤。
        """

        rows = self.database.list_by_status(
            "active"
        )

        memories = []

        for row in rows:

            item = MemoryItem.from_dict(
                row
            )

            vector = self.vector_store.get_vector(
                item.id
            )

            if not vector:

                # 没有向量的记忆没法参与聚类，跳过
                # （不应该发生，但防御性处理，不让一条
                # 脏数据搞崩整个 pass）。
                continue

            item.embedding = vector

            memories.append(
                item
            )


        clusters = self._cluster(
            memories
        )


        for cluster in clusters:

            if len(cluster) < 2:

                continue


            try:

                self._merge_and_persist_cluster(
                    cluster,
                    log,
                )

            except Exception as e:

                ids = [m.id for m in cluster]

                self.logger.error(
                    f"Cluster合并失败 {ids}: {e}"
                )

                log["errors"].append(
                    f"merge_cluster {ids}: {e}"
                )



    # -------------------------------------------------
    # Clustering
    # -------------------------------------------------

    def _cluster(
        self,
        memories: list,
    ) -> list[list]:
        """
        贪心阈值聚类，不是完整的层次聚类。

        做法: 按顺序取一条还没被分配的记忆作为簇的种子，
        把所有和它相似度 >= cluster_threshold 的记忆都
        拉进同一簇，标记已用；重复直到所有记忆都有簇。

        这不是传递闭包（A-B 像、B-C 像，但 A-C 不够像的话，
        A/C 不会被聚到同一簇，因为分簇只看和"种子"的相似度，
        不看簇内两两关系）——对于 v1 的"清理明显的碎片化重复"
        这个目标已经够用，真正需要更精细聚类（比如 HDBSCAN）
        是后续可以单独升级的点，不影响这里的接口。
        """

        clusters = []

        used = set()


        for i, seed in enumerate(memories):

            if seed.id in used:

                continue


            cluster = [seed]

            used.add(seed.id)


            for j in range(i + 1, len(memories)):

                other = memories[j]

                if other.id in used:

                    continue


                similarity = self._cosine(
                    seed.embedding,
                    other.embedding,
                )

                if similarity >= self.cluster_threshold:

                    cluster.append(other)

                    used.add(other.id)


            clusters.append(cluster)


        return clusters



    # -------------------------------------------------
    # Merge one cluster
    # -------------------------------------------------

    def _merge_and_persist_cluster(
        self,
        cluster: list,
        log: dict,
    ):
        """
        把一个簇合并成一条新记忆并持久化，
        簇内所有旧记忆标记 superseded 指向新记忆。

        注意（对齐 schema.py 里 parent_id 的设计说明）:
        MemoryItem.parent_id 只保留"主链路"的一个指针，
        簇里如果有 3 条以上的旧记忆，parent_id 最终只会
        停在最后一次 mark_superseded 传入的那个 id。
        完整的多源信息在这里的 log["merged"] 里用
        source_ids 完整记录，不依赖 schema 的单指针字段。
        """

        # 按 created_at 从旧到新折叠合并，让"更新的信息"
        # 更自然地作为后一次合并的输入——MergeEngine.merge()
        # 的语义是 merge(new, old)，旧的排在前面更符合直觉。

        ordered = sorted(
            cluster,
            key=lambda m: m.created_at or "",
        )


        accumulated_content = ordered[0].content

        for next_memory in ordered[1:]:

            accumulator = MemoryItem(
                content=accumulated_content
            )

            accumulated_content = self.merge_engine.merge(
                next_memory,
                accumulator,
            )


        # 合并后记忆的元数据不凭空生成，从簇成员里取
        # "最保守"的聚合方式：重要度/置信度取簇内最大值
        # （不能因为合并就把一条高重要度记忆的重要度降下来），
        # entity_key/memory_type 取簇内第一条非空的值。

        importance = max(
            m.importance for m in cluster
        )

        confidence = max(
            m.confidence for m in cluster
        )

        entity_key = next(
            (
                m.entity_key
                for m in cluster
                if m.entity_key
            ),
            None,
        )

        memory_type = next(
            (
                m.memory_type
                for m in cluster
                if m.memory_type
            ),
            "fact",
        )


        merged = MemoryItem(

            content=accumulated_content,

            memory_type=memory_type,

            importance=importance,

            confidence=confidence,

            entity_key=entity_key,

            source="consolidator",

        )

        merged.embedding = self.embedding.encode(
            merged.content
        )


        # 持久化新记忆（顺序同 manager.py remember_if_needed：
        # 先落库，再 supersede 旧记忆——mark_superseded()
        # 对新记忆那一侧的 UPDATE 语句要求这一行已经存在）。

        self.database.add(
            merged.to_dict()
        )

        self.vector_store.add(
            merged.embedding,
            merged.id,
        )


        source_ids = []

        for old_memory in cluster:

            self.database.mark_superseded(
                old_memory.id,
                merged.id,
            )

            source_ids.append(
                old_memory.id
            )


        self.logger.info(
            f"Cluster Merged: "
            f"{[m.content for m in cluster]} "
            f"-> {merged.content!r}"
        )


        log["merged"].append(
            {
                "target_id": merged.id,
                "content": merged.content,
                "source_ids": source_ids,
                "source_contents": [
                    m.content for m in cluster
                ],
            }
        )



    # =================================================
    # Utils
    # =================================================

    def _cosine(
        self,
        a,
        b,
    ) -> float:

        if not a or not b:

            return 0.0


        import numpy as np

        a = np.array(a)

        b = np.array(b)

        denom = (
            np.linalg.norm(a)
            *
            np.linalg.norm(b)
        )

        if denom == 0:

            return 0.0

        return float(
            np.dot(a, b) / denom
        )


    def _now_iso(self) -> str:

        return datetime.now(
            timezone.utc
        ).replace(
            microsecond=0
        ).isoformat()



# =====================================================
# CLI entrypoint
#
# 方便直接接入 cron / 外部调度器:
#
#     */30 * * * * cd /path/to/project && \
#         python -m memory.consolidator
#
# 具体多久跑一次、用 cron 还是 APScheduler 还是别的，
# 取决于部署环境，这里不做假设，只保证"被调用了就真的会跑"。
# =====================================================

if __name__ == "__main__":

    from memory.database import MemoryDatabase
    from memory.vector_store import VectorStore
    from memory.embedding import MemoryEmbedding
    from memory.merge import MergeEngine

    database = MemoryDatabase()

    embedding = MemoryEmbedding()

    vector_store = VectorStore(
        dimension=embedding.dimension
    )

    consolidator = MemoryConsolidator(

        database=database,

        vector_store=vector_store,

        embedding=embedding,

        merge_engine=MergeEngine(),

    )

    result = consolidator.run()

    print(result)