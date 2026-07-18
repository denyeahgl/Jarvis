"""
Jarvis Memory Database

Day14

SQLite Metadata Storage

负责:
- 保存memory metadata
- 查询memory内容

不负责:
- embedding
- vector search
"""


import sqlite3
import os
from datetime import datetime
from memory.schema import MemoryItem



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

            updated_at TEXT

        )

        """


        cursor = self.conn.cursor()

        cursor.execute(sql)

        self.conn.commit()


    def migrate(self):

        cursor=self.conn.cursor()


        try:

            cursor.execute(
                """
                ALTER TABLE memories
                ADD COLUMN access_count INTEGER DEFAULT 0
                """
            )

        except:

            pass



        try:

            cursor.execute(
                """
                ALTER TABLE memories
                ADD COLUMN last_accessed TEXT
                """
            )

        except:

            pass



        try:

            cursor.execute(
                """
                ALTER TABLE memories
                ADD COLUMN confidence REAL DEFAULT 1.0
                """
            )

        except:

            pass

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
            importance
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
            updated_at
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

                now
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


        }




    def update_memory(
        self,
        memory
    ):
        """
        Day15.3

        更新生命周期数据

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


    def close(self):

        self.conn.close()