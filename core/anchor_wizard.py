# core/anchor_wizard.py
"""
Anchor Wizard

交互式录入/编辑用户偏好。

触发时机：
1. 首次启动，anchor_profile.json 为空 —— 自动进入完整向导
2. 用户主动输入 /setup —— 重新走一遍完整向导
3. 用户输入 /setup <字段名> —— 只修改单个字段
"""

from core.anchor_fields import ANCHOR_FIELDS, AnchorField
from core.anchor_store import AnchorProfileStore


class AnchorWizard:

    def __init__(self, store: AnchorProfileStore):
        self.store = store

    # ==================================================
    # 完整向导
    # ==================================================

    def run_full(self):

        print("\n== 初次使用设置（直接回车可使用默认值/跳过） ==\n")

        for f in ANCHOR_FIELDS:
            self._ask_field(f)

        print("\n设置完成，之后可随时输入 /setup 修改。\n")

    # ==================================================
    # 单字段修改
    # ==================================================

    def run_single(self, key: str) -> bool:

        field_map = {f.key: f for f in ANCHOR_FIELDS}

        target = field_map.get(key)

        if not target:
            print(f"未知字段: {key}")
            print(f"可用字段: {', '.join(field_map.keys())}")
            return False

        self._ask_field(target)
        return True

    # ==================================================
    # 展示当前设置
    # ==================================================

    def show(self):
        print("\n== 当前偏好设置 ==")
        for f in ANCHOR_FIELDS:
            value = self.store.get(f.key) or f"(未设置，默认: {f.default or '无'})"
            print(f"  {f.label} ({f.key}): {value}")
        print()

    # ==================================================
    # Private
    # ==================================================

    def _ask_field(self, f: AnchorField):

        current = self.store.get(f.key) or f.default

        if f.choices:
            print(f"{f.prompt}")
            print(f"  {f.display_choices()}")
            hint = f"（当前: {current}，直接回车保留）" if current else ""
            raw = input(f"请选择编号{hint}: ").strip()

            if not raw:
                if current:
                    self.store.set(f.key, current)
                return

            try:
                idx = int(raw) - 1
                value = f.choices[idx]
            except (ValueError, IndexError):
                print("输入无效，保留原值。")
                if current:
                    self.store.set(f.key, current)
                return

        else:
            hint = f"（当前: {current}，直接回车保留）" if current else "（直接回车跳过）"
            raw = input(f"{f.prompt}{hint}: ").strip()
            value = raw or current

        if value:
            if f.validator and not f.validator(value):
                print("输入未通过校验，请稍后用 /setup 重新设置。")
                return
            self.store.set(f.key, value)