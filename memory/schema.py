"""
memory/schema.py

Memory Schema 5.0

Day13

统一定义长期记忆的数据结构。

新增：

- updated_at
- last_accessed
- access_count
- confidence
- version
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import uuid


def now_iso() -> str:
    """
    返回 ISO8601 UTC 时间字符串。

    例如：

    2026-07-17T00:15:23Z
    """

    return datetime.utcnow().replace(
        microsecond=0
    ).isoformat() + "Z"


@dataclass
class MemoryItem:
    """
    长期记忆对象。
    """

    # =====================================================
    # Identity
    # =====================================================

    id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    # =====================================================
    # Core
    # =====================================================

    content: str = ""

    embedding: list[float] = field(
        default_factory=list
    )

    memory_type: str = "fact"

    importance: int = 3

    source: str = "user"

    # =====================================================
    # Lifecycle
    # =====================================================

    created_at: str = field(
        default_factory=now_iso
    )

    updated_at: str = field(
        default_factory=now_iso
    )

    last_accessed: str = field(
        default_factory=now_iso
    )

    access_count: int = 0

    # =====================================================
    # Metadata
    # =====================================================

    confidence: float = 1.0

    version: int = 1

    # =====================================================
    # Serialize
    # =====================================================

    def to_dict(self) -> dict:

        return {

            "id": self.id,

            "content": self.content,

            "embedding": self.embedding,

            "memory_type": self.memory_type,

            "importance": self.importance,

            "source": self.source,

            "created_at": self.created_at,

            "updated_at": self.updated_at,

            "last_accessed": self.last_accessed,

            "access_count": self.access_count,

            "confidence": self.confidence,

            "version": self.version,

        }

    # =====================================================
    # Deserialize
    # =====================================================

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ):

        return cls(

            id=data.get(
                "id",
                str(uuid.uuid4()),
            ),

            content=data.get(
                "content",
                "",
            ),

            embedding=data.get(
                "embedding",
                [],
            ),

            memory_type=data.get(
                "memory_type",
                "fact",
            ),

            importance=int(
                data.get(
                    "importance",
                    3,
                )
            ),

            source=data.get(
                "source",
                "user",
            ),

            created_at=data.get(
                "created_at",
                now_iso(),
            ),

            updated_at=data.get(
                "updated_at",
                data.get(
                    "created_at",
                    now_iso(),
                ),
            ),

            last_accessed=data.get(
                "last_accessed",
                data.get(
                    "created_at",
                    now_iso(),
                ),
            ),

            access_count=int(
                data.get(
                    "access_count",
                    0,
                )
            ),

            confidence=float(
                data.get(
                    "confidence",
                    1.0,
                )
            ),

            version=int(
                data.get(
                    "version",
                    1,
                )
            ),
        )

    # =====================================================
    # Lifecycle API
    # =====================================================

    def touch(self):
        """
        记忆被访问。

        Day14 Retrieval 会调用。
        """

        self.access_count += 1

        self.last_accessed = now_iso()

    def update(
        self,
        content: str | None = None,
        importance: int | None = None,
        memory_type: str | None = None,
    ):
        """
        更新记忆。

        Day14 Memory Update 会调用。
        """

        if content is not None:
            self.content = content

        if importance is not None:
            self.importance = importance

        if memory_type is not None:
            self.memory_type = memory_type

        self.updated_at = now_iso()

        self.version += 1