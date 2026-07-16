"""
Memory Schema

定义 Jarvis Memory 数据结构
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List
import uuid


@dataclass
class MemoryItem:
    """
    一条长期记忆
    """

    content: str

    # 新增
    embedding: List[float] = field(default_factory=list)

    memory_type: str = "conversation"

    importance: int = 1

    source: str = "user"

    created_at: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )

    id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    def to_dict(self):

        return {
            "id": self.id,
            "content": self.content,
            "embedding": self.embedding,
            "memory_type": self.memory_type,
            "importance": self.importance,
            "source": self.source,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data):

        return cls(
            content=data["content"],

            embedding=data.get(
                "embedding",
                [],
            ),

            memory_type=data.get(
                "memory_type",
                "conversation",
            ),

            importance=data.get(
                "importance",
                1,
            ),

            source=data.get(
                "source",
                "user",
            ),

            created_at=data.get(
                "created_at"
            ),

            id=data.get(
                "id"
            ),
        )