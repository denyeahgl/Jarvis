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


        self.create_table()



    def create_table(self):

        sql = """

        CREATE TABLE IF NOT EXISTS memories (

            id TEXT PRIMARY KEY,

            content TEXT NOT NULL,

            memory_type TEXT,

            importance INTEGER DEFAULT 1,

            created_at TEXT,

            updated_at TEXT

        )

        """


        cursor = self.conn.cursor()

        cursor.execute(sql)

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


        now = datetime.now().isoformat()


        sql = """

        INSERT INTO memories
        (
            id,
            content,
            memory_type,
            importance,
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
                    1
                ),
                now,
                now
            )
        )


        self.conn.commit()



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

            "id":row[0],

            "content":row[1],

            "memory_type":row[2],

            "importance":row[3],

            "created_at":row[4],

            "updated_at":row[5]

        }



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



    def close(self):

        self.conn.close()