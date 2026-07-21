# core/anchor.py（在原基础上改造）
from datetime import datetime
from zoneinfo import ZoneInfo

from core.anchor_fields import ANCHOR_FIELDS
from core.anchor_store import AnchorProfileStore
from core.logger import Logger


class AnchorResolver:

    def __init__(self, store: AnchorProfileStore):
        self.store = store
        self.logger = Logger()

    def render(self) -> str:

        tz_name = self.store.get("timezone") or "Asia/Shanghai"
        now = datetime.now(ZoneInfo(tz_name))
        weekday_map = ["一", "二", "三", "四", "五", "六", "日"]

        lines = [
            "[系统锚点信息 - 用户已确认，绝对准确，禁止怀疑或用其他来源覆盖]",
            f"当前日期: {now.strftime('%Y-%m-%d')}（星期{weekday_map[now.weekday()]}）",
            f"当前时间: {now.strftime('%H:%M:%S')} ({tz_name})",
        ]

        # 除 timezone 外，其余字段自动遍历渲染，不用逐个写 if
        for f in ANCHOR_FIELDS:
            if f.key == "timezone":
                continue

            value = self.store.get(f.key)

            if value:
                lines.append(f"{f.render_label or f.label}: {value}（用户已确认）")
            else:
                lines.append(
                    f"{f.render_label or f.label}: 未设置"
                    "（如问题依赖此信息，需先询问用户，不得假设）"
                )

        return "\n".join(lines)