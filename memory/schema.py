"""
Memory Schema

定义 Jarvis Memory 数据结构
"""

from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class MemoryItem:
    """
    一条记忆
    """

    content: str

    memory_type: str = "conversation"

    importance: int = 1

    created_at: str = field(
        default_factory=lambda:
        datetime.now().isoformat()
    )

    id: str = field(
        default_factory=lambda:
        str(uuid.uuid4())
    )


    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type,
            "importance": self.importance,
            "created_at": self.created_at,
        }


    @classmethod
    def from_dict(cls, data):

        return cls(
            content=data["content"],
            memory_type=data.get(
                "memory_type",
                "conversation"
            ),
            importance=data.get(
                "importance",
                1
            ),
            created_at=data.get(
                "created_at"
            ),
            id=data.get(
                "id"
            )
        )