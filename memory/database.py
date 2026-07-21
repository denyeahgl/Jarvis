"""
Jarvis Memory Database

Day16 (Phase 1: 结构化字段 + 版本链基础设施)

SQLite Metadata Storage

负责:
- 保存memory metadata
- 查询memory内容
- Day16新增: entity_key 精确匹配 / status 状态迁移 / 版本链维护

不负责:
- embedding
- vector search
（这两个仍然在 vector_store.py，Phase 1 会给它加 delete/update，
  但那是另一个文件，这里不动）
"""


import sqlite3
import os
from datetime import datetime
from memory.schema import (
    MemoryItem,
    STATUS_ACTIVE,
    STATUS_SUPERSEDED,
    STATUS_ARCHIVED,
)



class MemoryDatabase:


    def __init__(
        self,
        db_path="data/memory.db"
    ):


        self.db_path = db_path


        os.makedirs(
            os.path.dirname(db_path),
            exist_ok=True
        )


        self.conn = sqlite3.connect(
            self.db_path
        )

        self.conn.row_factory = sqlite3.Row

        self.create_table()

        self.migrate()

    def create_table(self):

        # 新建的库直接带上 Day16 的全部字段；
        # 老库靠下面 migrate() 里的 ALTER TABLE 补齐。
        sql = """

        CREATE TABLE IF NOT EXISTS memories (

            id TEXT PRIMARY KEY,

            content TEXT NOT NULL,

            memory_type TEXT,

            importance REAL DEFAULT 3.0,

            confidence REAL DEFAULT 1.0,

            access_count INTEGER DEFAULT 0,

            last_accessed TEXT,

            created_at TEXT,

            updated_at TEXT,

            version INTEGER DEFAULT 1,

            entity_key TEXT,

            status TEXT DEFAULT 'active',

            superseded_by TEXT,

            parent_id TEXT

        )

        """


        cursor = self.conn.cursor()

        cursor.execute(sql)

        self.conn.commit()


    # =====================================================
    # Migrate
    # =====================================================

    def _existing_columns(self):
        """
        查当前表已有哪些列。

        用来判断 ALTER TABLE ADD COLUMN 是不是真的需要，
        而不是像之前那样无差别 try/except: pass ——
        那样会把"列已存在"（预期内）和其他真实错误
        （比如库文件损坏、磁盘只读）混在一起悄悄吞掉。
        """

        cursor = self.conn.cursor()

        cursor.execute(
            "PRAGMA table_info(memories)"
        )

        return {
            row["name"]
            for row in cursor.fetchall()
        }


    def _add_column_if_missing(
        self,
        column_name,
        column_def,
    ):

        if column_name in self._existing_columns():

            return


        cursor = self.conn.cursor()

        cursor.execute(
            f"ALTER TABLE memories "
            f"ADD COLUMN {column_name} {column_def}"
        )

        self.conn.commit()


    def migrate(self):

        # -----------------------------------------------
        # Day14 已有字段
        #
        # 保留原来的 try/except 写法，兼容 Day14/15 就已经
        # 建好、且可能被其他分支/环境同时使用的旧库文件，
        # 不改动这部分的行为。
        # -----------------------------------------------

        cursor = self.conn.cursor()

        try:

            cursor.execute(
                """
                ALTER TABLE memories
                ADD COLUMN access_count INTEGER DEFAULT 0
                """
            )

        except Exception:

            pass



        try:

            cursor.execute(
                """
                ALTER TABLE memories
                ADD COLUMN last_accessed TEXT
                """
            )

        except Exception:

            pass



        try:

            cursor.execute(
                """
                ALTER TABLE memories
                ADD COLUMN confidence REAL DEFAULT 1.0
                """
            )

        except Exception:

            pass

        self.conn.commit()


        # -----------------------------------------------
        # Day16 新增字段（Phase 1）
        #
        # 用 _add_column_if_missing 而不是裸 try/except，
        # 这样如果 ALTER 因为别的原因失败（不是"列已存在"），
        # 错误会真的抛出来，不会被静默吞掉。
        # -----------------------------------------------

        self._add_column_if_missing(
            "version",
            "INTEGER DEFAULT 1",
        )

        self._add_column_if_missing(
            "entity_key",
            "TEXT",
        )

        self._add_column_if_missing(
            "status",
            "TEXT DEFAULT 'active'",
        )

        self._add_column_if_missing(
            "superseded_by",
            "TEXT",
        )

        self._add_column_if_missing(
            "parent_id",
            "TEXT",
        )

        # 老库里在加 status 列之前插入的行，status 会是 NULL
        # （ALTER TABLE ADD COLUMN 的 DEFAULT 只对之后的 INSERT
        # 生效，不会回填已有的行）。这里补一次，避免后面
        # find_by_entity_key() / 按 status 过滤的查询漏掉旧数据。

        cursor.execute(
            """
            UPDATE memories
            SET status = ?
            WHERE status IS NULL
            """,
            (STATUS_ACTIVE,)
        )

        self.conn.commit()


    def add(
        self,
        memory
    ):
        """
        添加memory

        memory:
        {
            id,
            content,
            memory_type,
            importance,
            entity_key,
            status,
            superseded_by,
            parent_id,
            version,
        }
        """


        if isinstance(
            memory,
            MemoryItem
        ):
            memory = memory.to_dict()


        now = datetime.now().isoformat()


        sql = """

        INSERT INTO memories
        (
            id,
            content,
            memory_type,
            importance,
            confidence,
            access_count,
            last_accessed,
            created_at,
            updated_at,
            version,
            entity_key,
            status,
            superseded_by,
            parent_id
        )

        VALUES
        (
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?
        )

        """


        cursor = self.conn.cursor()


        cursor.execute(
            sql,
            (
                memory["id"],

                memory["content"],

                memory.get(
                    "memory_type"
                ),

                memory.get(
                    "importance",
                    3.0
                ),

                memory.get(
                    "confidence",
                    1.0
                ),

                memory.get(
                    "access_count",
                    0
                ),

                memory.get(
                    "last_accessed"
                ),

                now,

                now,

                memory.get(
                    "version",
                    1
                ),

                memory.get(
                    "entity_key"
                ),

                memory.get(
                    "status",
                    STATUS_ACTIVE
                ) or STATUS_ACTIVE,

                memory.get(
                    "superseded_by"
                ),

                memory.get(
                    "parent_id"
                ),
            )
        )

        self.conn.commit()


    def delete(
        self,
        memory_id
    ):

        cursor=self.conn.cursor()


        cursor.execute(
            """
            DELETE FROM memories
            WHERE id=?
            """,
            (memory_id,)
        )


        self.conn.commit()


    def count(self):

        cursor=self.conn.cursor()


        cursor.execute(
            """
            SELECT COUNT(*)
            FROM memories
            """
        )


        return cursor.fetchone()[0]


    # =====================================================
    # Row -> dict
    # =====================================================

    def _row_to_dict(self, row):

        return {

            "id": row["id"],

            "content": row["content"],

            "memory_type": row["memory_type"],

            "importance": row["importance"],

            "confidence": row["confidence"],

            "access_count": row["access_count"],

            "last_accessed": row["last_accessed"],

            "created_at": row["created_at"],

            "updated_at": row["updated_at"],

            "version": row["version"],

            "entity_key": row["entity_key"],

            "status": row["status"],

            "superseded_by": row["superseded_by"],

            "parent_id": row["parent_id"],

        }


    def get(
        self,
        memory_id
    ):


        sql = """

        SELECT *

        FROM memories

        WHERE id=?

        """


        cursor=self.conn.cursor()


        cursor.execute(
            sql,
            (memory_id,)
        )


        row=cursor.fetchone()


        if row is None:

            return None



        return self._row_to_dict(row)


    # =====================================================
    # Day16: Structured Key Lookup
    # =====================================================

    def find_by_entity_key(
        self,
        entity_key,
        active_only=True,
    ):
        """
        按归一化 entity_key 精确查。

        Phase 3（结构化字段辅助检索）会用这个方法：
        写入新记忆前先查 entity_key，命中就直接当作同一实体处理，
        不需要再退化到向量相似度兜底。

        active_only=True 时只返回 status="active" 的记忆——
        已经 superseded/archived 的旧版本不应该再被当成"当前值"
        参与判重。

        返回: list[dict]，可能为空列表。
        """

        if not entity_key:

            return []


        cursor = self.conn.cursor()


        if active_only:

            cursor.execute(
                """
                SELECT *
                FROM memories
                WHERE entity_key = ?
                AND status = ?
                """,
                (entity_key, STATUS_ACTIVE)
            )

        else:

            cursor.execute(
                """
                SELECT *
                FROM memories
                WHERE entity_key = ?
                """,
                (entity_key,)
            )


        return [
            self._row_to_dict(row)
            for row in cursor.fetchall()
        ]


    def list_by_status(
        self,
        status=STATUS_ACTIVE,
    ):
        """
        按状态批量取记忆。

        主要给 Day19 的定期整理任务（consolidator）用：
        遍历全部 active 记忆做聚类/衰减检查。
        """

        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM memories
            WHERE status = ?
            """,
            (status,)
        )

        return [
            self._row_to_dict(row)
            for row in cursor.fetchall()
        ]


    def update_memory(
        self,
        memory
    ):
        """
        Day15.3

        更新生命周期数据

        （不变：只更新 importance/confidence/access_count/
        last_accessed/updated_at，不涉及 content/status/
        version chain —— 那些交给下面 Day16 新增的几个方法。）
        """

        sql = """

        UPDATE memories

        SET

            importance=?,

            confidence=?,

            access_count=?,

            last_accessed=?,

            updated_at=?

        WHERE id=?

        """


        cursor = self.conn.cursor()

        print(
            "UPDATE MEMORY:",
            memory.content,
            memory.access_count,
            memory.importance
        )
            

        cursor.execute(
            sql,
            (
                memory.importance,

                memory.confidence,

                memory.access_count,

                memory.last_accessed,

                memory.updated_at,

                memory.id
            )
        )


        self.conn.commit()


    # =====================================================
    # Day16: Content Update (原地覆盖，不走版本链)
    # =====================================================

    def update_content(
        self,
        memory_id,
        content,
        bump_version=True,
    ):
        """
        原地覆盖记忆内容。

        对应 Phase 2 UPDATE 决策里"同一条记忆内容小幅修正、
        不需要保留旧版本"的场景，例如纠正一个笔误。

        如果需要保留旧版本、走版本链（"用户偏好从蓝色变成了
        绿色"这种要可追溯的更新），应该用 mark_superseded() +
        单独 add() 一条新记忆，而不是这个方法。

        调用方需要自己同步更新 FAISS 里对应的向量
        （这里只管 SQLite metadata）。
        """

        now = datetime.now().isoformat()

        cursor = self.conn.cursor()

        if bump_version:

            cursor.execute(
                """
                UPDATE memories
                SET
                    content = ?,
                    version = version + 1,
                    updated_at = ?
                WHERE id = ?
                """,
                (content, now, memory_id)
            )

        else:

            cursor.execute(
                """
                UPDATE memories
                SET
                    content = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (content, now, memory_id)
            )

        self.conn.commit()


    # =====================================================
    # Day16: Version Chain (supersede / archive)
    # =====================================================

    def mark_superseded(
        self,
        old_memory_id,
        new_memory_id,
    ):
        """
        把旧记忆标记为已被新记忆取代。

        对应 Phase 2 的 UPDATE / MERGE 决策：旧记忆不物理删除，
        只做状态迁移，保留版本链方便追溯/调试/回滚。

        这里只负责 SQLite 这一侧的两条记录（老记录的
        status/superseded_by，新记录的 parent_id）。
        调用方（manager.py）还需要自己：
        - 把旧记忆的向量从 vector_store 摘掉/替换
        - 如果新记忆这时还没写库，要先 add() 再调用这个方法
        """

        now = datetime.now().isoformat()

        cursor = self.conn.cursor()

        cursor.execute(
            """
            UPDATE memories
            SET
                status = ?,
                superseded_by = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (STATUS_SUPERSEDED, new_memory_id, now, old_memory_id)
        )

        cursor.execute(
            """
            UPDATE memories
            SET
                parent_id = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (old_memory_id, now, new_memory_id)
        )

        self.conn.commit()


    def mark_archived(
        self,
        memory_id,
    ):
        """
        归档：Day19 定期整理任务用，标记长期未访问/
        重要度衰减到阈值以下的记忆。

        区别于 mark_superseded()——archive 不是因为有新记忆
        取代它，只是因为它"不再重要"，所以没有 superseded_by。
        """

        now = datetime.now().isoformat()

        cursor = self.conn.cursor()

        cursor.execute(
            """
            UPDATE memories
            SET
                status = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (STATUS_ARCHIVED, now, memory_id)
        )

        self.conn.commit()


    # =====================================================
    # Day19.1 Bugfix: Version History
    #
    # 生产环境里发现: "用户是广西大学学生" superseded 掉
    # "用户是一名高中生" 之后，问"我上大学前是什么身份"完全
    # 召回不到——不是这条旧记忆丢了，它还在库里，只是
    # status="superseded" 之后，检索路径 (retriever.py 那次
    # Day17.2 修复) 把它过滤掉了，而且没有任何地方能把它
    # 重新捞回来。目标文档里说"保留版本链而不是物理删除"，
    # 但只是保留在数据库里、没有对外的查询接口，等于还是
    # 丢了——这个方法就是补上这个查询接口。
    # =====================================================

    def get_version_chain(
        self,
        memory_id,
    ):
        """
        沿 parent_id 反向走到底，返回 memory_id 所在版本链的
        完整历史，从最旧到最新排序，不受 status 限制
        （查的就是历史，不能按 active 过滤）。

        返回 list[dict]，如果 memory_id 不存在则返回空列表。
        """

        current = self.get(memory_id)

        if not current:

            return []


        chain = [current]

        seen_ids = {current["id"]}

        node = current

        while node.get("parent_id"):

            parent_id = node["parent_id"]

            if parent_id in seen_ids:

                # 防御性处理: 正常不该出现环，但脏数据/手工
                # 改库不能排除，宁可提前截断也不要死循环。
                break

            parent = self.get(parent_id)

            if not parent:

                break

            chain.append(parent)

            seen_ids.add(parent_id)

            node = parent


        chain.reverse()

        return chain


    def close(self):

        self.conn.close()