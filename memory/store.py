"""
Memory Store

负责 Memory 持久化
"""


import json
import os
import tempfile

from memory.schema import MemoryItem



class MemoryStore:


    def __init__(
        self,
        path="data/memory.json",
        max_items=500
    ):

        self.path = path

        # 长期记忆容量上限，超出后按 (importance, created_at) 淘汰
        self.max_items = max_items


        directory = os.path.dirname(
            self.path
        )


        if directory:
            os.makedirs(
                directory,
                exist_ok=True
            )


        if not os.path.exists(
            self.path
        ):
            self.save([])



    def save(self, memories):
        """
        原子写入。

        先写入同目录下的临时文件，再用 os.replace 覆盖正式文件。
        os.replace 在同一文件系统下是原子操作，
        即使进程在写入过程中被杀掉/断电，
        也只会留下一个 .tmp 文件，正式的 memory.json 不会被写坏。
        """

        directory = (
            os.path.dirname(self.path)
            or "."
        )

        fd, tmp_path = tempfile.mkstemp(
            dir=directory,
            prefix=".memory_",
            suffix=".tmp",
        )

        try:

            with os.fdopen(
                fd,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    memories,
                    f,
                    ensure_ascii=False,
                    indent=4
                )

                f.flush()
                os.fsync(f.fileno())

            os.replace(
                tmp_path,
                self.path
            )

        except Exception:

            if os.path.exists(tmp_path):
                os.remove(tmp_path)

            raise



    def load(self):
        """
        读取失败（文件不存在/损坏）时返回空列表，
        而不是抛异常拖垮整个 Memory 系统。
        """

        if not os.path.exists(
            self.path
        ):
            return []

        try:

            with open(
                self.path,
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(f)

        except (
            json.JSONDecodeError,
            OSError
        ):

            return []



    def _is_duplicate(
        self,
        memories,
        content
    ):
        """
        简单的精确去重：内容完全一致（去除首尾空白后）则视为重复。
        """

        content = content.strip()

        return any(
            m.get("content", "").strip() == content
            for m in memories
        )



    def _evict_if_needed(
        self,
        memories
    ):
        """
        超出容量上限时，优先淘汰 importance 更低、
        created_at 更早的记忆，保留原有相对顺序。
        """

        if len(memories) <= self.max_items:
            return memories

        overflow = (
            len(memories) - self.max_items
        )

        ranked = sorted(
            memories,
            key=lambda m: (
                m.get("importance", 1),
                m.get("created_at", ""),
            ),
        )

        ids_to_remove = {
            m.get("id")
            for m in ranked[:overflow]
        }

        return [
            m for m in memories
            if m.get("id") not in ids_to_remove
        ]



    def add(
        self,
        memory: MemoryItem
    ):

        self.add_batch([memory])



    def add_batch(
        self,
        memories_to_add: list
    ):
        """
        批量添加多条 MemoryItem。

        只做一次 load / evict / save，
        避免 remember() 对同一句话切分出的多个 fragment
        逐条调用 add() 导致的重复全量文件 IO。
        """

        if not memories_to_add:
            return

        memories = self.load()

        added_any = False

        for memory in memories_to_add:

            content = memory.content.strip()

            if not content:
                continue

            if self._is_duplicate(
                memories,
                content
            ):
                continue

            memories.append(
                memory.to_dict()
            )

            added_any = True

        if not added_any:
            return

        memories = self._evict_if_needed(
            memories
        )

        self.save(
            memories
        )



    def get_all(self):

        return [
            MemoryItem.from_dict(m)
            for m in self.load()
        ]







