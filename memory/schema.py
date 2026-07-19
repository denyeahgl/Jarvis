"""
memory/schema.py

Memory Schema 6.0

Day16 (Phase 1: 结构化字段 + 版本链基础设施)

在 Day13 (updated_at / last_accessed / access_count / confidence / version)
的基础上新增：

- entity_key      结构化归一化 key，例如 "user_favorite_color"，
                  用于在向量检索之前做精确匹配（Day18 会用到）。
- status          "active" / "superseded" / "archived"，
                  记忆的生命周期状态。判重/合并/整理都不做物理删除，
                  只把旧记忆状态迁移走，保留可追溯的版本链。
- superseded_by   如果这条记忆已经被新记忆取代，指向新记忆的 id。
- parent_id       如果这条记忆是由旧记忆更新/合并而来，指向被取代的
                  旧记忆 id（正向指针，配合 superseded_by 反向指针
                  即可完整还原版本链）。

Day14/15 已有字段（content / embedding / memory_type / importance /
source / lifecycle 字段 / confidence / version）全部保留，
未做破坏性变更，manager.py / dedup.py / conflict.py / retriever.py
等现有调用方无需改动即可继续工作。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import uuid


# =========================================================
# Status Constants
# =========================================================

STATUS_ACTIVE = "active"
STATUS_SUPERSEDED = "superseded"
STATUS_ARCHIVED = "archived"

VALID_STATUSES = (
    STATUS_ACTIVE,
    STATUS_SUPERSEDED,
    STATUS_ARCHIVED,
)


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

    importance: float = 3.0

    source: str = "user"

    # =====================================================
    # Structured Key (Day16 / Phase 1)
    # =====================================================

    # 归一化 key，例如 "user_favorite_color"。
    #
    # 同一个 entity_key 理论上应该只存在一条 status="active"
    # 的记忆——写入前可以先按 entity_key 精确查，查到即认为
    # 是同一实体的更新，不必再退化到向量相似度兜底。
    #
    # 允许为 None：不是所有记忆都能/需要归一化成结构化 key
    # （比如一次性的事件记录），此时仍然完全依赖向量检索。
    entity_key: str | None = None

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
    # Version Chain (Day16 / Phase 1)
    # =====================================================

    # "active"    仍然有效，检索/判重候选池应该只取这一类
    # "superseded" 已被更新/合并取代，保留下来只是为了可追溯，
    #              不应该再出现在检索结果或判重候选池里
    # "archived"   长期未被访问、重要度衰减到阈值以下，
    #              被 Day19 的定期整理任务归档
    status: str = STATUS_ACTIVE

    # 指向"取代了这条记忆"的新记忆 id。
    # 只有 status == "superseded" 时才应该有值。
    superseded_by: str | None = None

    # 指向"这条记忆取代/合并自"的旧记忆 id。
    # UPDATE：指向被覆盖的单条旧记忆
    # MERGE：如果需要追溯多个来源，建议在合并逻辑里另外记录
    #        完整来源列表（比如日志），这里只保留主链路的一个指针，
    #        避免 schema 里出现变长字段。
    parent_id: str | None = None

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

            "entity_key": self.entity_key,

            "created_at": self.created_at,

            "updated_at": self.updated_at,

            "last_accessed": self.last_accessed,

            "access_count": self.access_count,

            "confidence": self.confidence,

            "version": self.version,

            "status": self.status,

            "superseded_by": self.superseded_by,

            "parent_id": self.parent_id,

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

            importance=float(
                data.get(
                    "importance",
                    3.0,
                )
            ),

            source=data.get(
                "source",
                "user",
            ),

            entity_key=data.get(
                "entity_key"
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

            status=data.get(
                "status",
                STATUS_ACTIVE,
            ) or STATUS_ACTIVE,

            superseded_by=data.get(
                "superseded_by"
            ),

            parent_id=data.get(
                "parent_id"
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
        importance: float | None = None,
        memory_type: str | None = None,
    ):
        """
        更新记忆。

        Day14 Memory Update 会调用。

        注意：这是"原地覆盖"（同一条记忆内容变了，id/版本链不变），
        对应 Phase 2 里 UPDATE 决策中"内容小幅修正、不需要保留旧版本"
        的场景。如果需要保留旧版本、走版本链，请用下面的
        supersede_by() / mark_as_new_version()，而不是这个方法。
        """

        if content is not None:
            self.content = content

        if importance is not None:
            self.importance = importance

        if memory_type is not None:
            self.memory_type = memory_type

        self.updated_at = now_iso()

        self.version += 1

    # =====================================================
    # Version Chain API (Day16 / Phase 1)
    # =====================================================

    def supersede_by(
        self,
        new_memory_id: str,
    ):
        """
        把这条记忆标记为"已被新记忆取代"。

        用在 Phase 2 的 UPDATE / MERGE 决策里：旧记忆不物理删除，
        只是状态迁移走，保留版本链方便追溯/调试/回滚。

        调用方负责：
        - 把新记忆的 parent_id 设置为这条记忆的 id
        - 把这条旧记忆的向量从 vector_store 里摘掉
          （或者保留但检索/判重时按 status 过滤掉，
          具体取舍见 Phase 2 实现）
        """

        self.status = STATUS_SUPERSEDED

        self.superseded_by = new_memory_id

        self.updated_at = now_iso()

    def archive(self):
        """
        归档：长期未访问 / 重要度衰减到阈值以下。

        Day19 定期整理任务会调用。区别于 supersede_by()——
        archive 不是因为有新记忆取代它，只是因为它"不再重要"。
        """

        self.status = STATUS_ARCHIVED

        self.updated_at = now_iso()

    def reactivate(self):
        """
        取消归档/取消 superseded 标记，恢复为 active。

        预留给"用户纠正了错误的合并/归档"这类人工干预场景，
        当前阶段不强制要求调用方使用。
        """

        self.status = STATUS_ACTIVE

        self.superseded_by = None

        self.updated_at = now_iso()

    @property
    def is_active(self) -> bool:

        return self.status == STATUS_ACTIVE