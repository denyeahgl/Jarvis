# core/anchor_store.py
"""
Anchor Profile Store

独立于 Config/.env 的用户偏好持久化。
原因：.env 通常是部署时静态配置，不该被程序运行时写回；
用户偏好需要能被交互式修改并落盘。
"""

import json
from pathlib import Path

from core.logger import Logger


class AnchorProfileStore:

    def __init__(self, path: str = "data/anchor_profile.json"):
        self.path = Path(path)
        self.logger = Logger()
        self._data: dict[str, str] = {}
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                self._data = json.loads(self.path.read_text(encoding="utf-8"))
            except Exception as e:
                self.logger.warning(f"[Anchor] 读取偏好文件失败，重置: {e}")
                self._data = {}

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self._data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def get(self, key: str) -> str | None:
        return self._data.get(key)

    def set(self, key: str, value: str):
        self._data[key] = value
        self._save()

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def as_dict(self) -> dict[str, str]:
        return dict(self._data)