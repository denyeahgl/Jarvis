# tools/datetime_tool.py
"""
tools/datetime_tool.py

Datetime Tool

提供确定性的当前时间，避免模型通过网页搜索
猜测/误判"今天日期"这类问题（搜索结果里的
日期文本往往是网页发布时间或历史事件时间，
不是真实的"今天"）。
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from tools.base import BaseTool
from core.logger import Logger


class DatetimeTool(BaseTool):

    @property
    def name(self) -> str:
        return "get_current_time"

    @property
    def schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": (
                    "获取当前真实日期和时间（服务器系统时钟，权威准确）。"
                    "任何涉及'今天几号''现在几点''当前星期几'等问题，"
                    "必须调用此工具，禁止通过 web_search 或自身知识推测日期。"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "timezone": {
                            "type": "string",
                            "description": "IANA 时区名，默认 Asia/Shanghai",
                        },
                    },
                    "required": [],
                },
            },
        }

    def __init__(self):
        self.logger = Logger()

    def execute(self, timezone: str = "Asia/Shanghai") -> dict:

        try:
            tz = ZoneInfo(timezone)
        except Exception:
            self.logger.warning(f"未知时区 {timezone}，回退 Asia/Shanghai")
            tz = ZoneInfo("Asia/Shanghai")

        now = datetime.now(tz)

        weekday_map = ["一", "二", "三", "四", "五", "六", "日"]

        return {
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "weekday": f"星期{weekday_map[now.weekday()]}",
            "timezone": timezone,
        }