# core/anchor_fields.py
"""
Anchor Fields

声明所有"确定性用户偏好"字段。

新增字段只需要在这里加一条 AnchorField，
向导 (anchor_wizard.py)、持久化 (anchor_store.py)、
渲染 (anchor.py) 会自动识别，无需改动其他代码。
"""

from dataclasses import dataclass, field
from collections.abc import Callable


@dataclass(slots=True)
class AnchorField:
    key: str                                  # 存储 key，如 "timezone"
    label: str                                 # 向导里展示的中文名
    prompt: str                                 # 向导提问文案
    default: str | None = None                  # 默认值（Enter 直接采用）
    choices: list[str] | None = None            # 若非 None，展示为选项而非自由输入
    render_label: str | None = None              # 渲染进 system prompt 时的前缀，默认用 label
    validator: Callable[[str], bool] | None = None  # 自定义校验，返回 False 会要求重新输入

    def display_choices(self) -> str:
        if not self.choices:
            return ""
        return " / ".join(
            f"[{i+1}] {c}" for i, c in enumerate(self.choices)
        )


ANCHOR_FIELDS: list[AnchorField] = [
    AnchorField(
        key="timezone",
        label="时区",
        prompt="你所在的时区（IANA 格式，如 Asia/Shanghai）",
        default="Asia/Shanghai",
    ),
    AnchorField(
        key="city",
        label="城市",
        prompt="你所在的城市（用于天气/本地信息类问题）",
        default=None,
    ),
    AnchorField(
        key="language",
        label="回复语言",
        prompt="你偏好的回复语言",
        choices=["中文", "English", "日本語"],
        default="中文",
    ),
    AnchorField(
        key="unit_system",
        label="度量衡",
        prompt="度量衡单位偏好",
        choices=["公制（℃/km/kg）", "英制（℉/mi/lb）"],
        default="公制（℃/km/kg）",
    ),
    # 以后加字段，比如：
    # AnchorField(key="currency", label="货币单位", prompt="...", default="CNY"),
]