"""
core/llm.py

Jarvis LLM Facade Layer

Day13 (Refactor)

职责：

提供统一 LLM 调用接口。

提供：

1. chat()
2. chat_json()

不负责：

- API 请求细节
- JSON 解析
- Retry
- Provider 判断
"""


from __future__ import annotations


from core.config import Config
from core.logger import Logger

from core.capability import CapabilityResolver
from core.llm_response import LLMResponse



# =====================================================
# Initialize
# =====================================================


config = Config()

logger = Logger()


capability = CapabilityResolver(
    config
).resolve()


llm_client = LLMResponse(

    model=config.model_name,

    capability=capability,

    # 显式传入 config，避免 LLMResponse 内部再 new 一份
    # 导致两处配置不一致（单一数据源）。
    config=config,

)



# =====================================================
# Chat
# =====================================================


def chat(
    messages: list,
    stream: bool = False,
    tools: list | None = None,
    tool_choice: str | None = None,
    return_message: bool = False,
):
    """
    普通聊天接口。

    保持 Day07-Day12 兼容。

    Parameters
    ----------

    messages:
        OpenAI messages 格式


    stream:
        是否流式输出


    tools:
        Tool Calling 工具列表


    tool_choice:
        tool 调用策略


    return_message:
        是否返回完整 message 对象

    """

    return llm_client.chat(

        messages=messages,

        stream=stream,

        tools=tools,

        tool_choice=tool_choice,

        return_message=return_message,

    )



# =====================================================
# JSON Chat
# =====================================================


def chat_json(
    messages: list,
    schema: dict | None = None,
    retry: int = 1,
):
    """
    JSON 输出接口。

    Memory / Planner / Reflection 使用。


    注意：

    返回原始 JSON 字符串。

    不在这里 json.loads。


    Example:

        text = chat_json(messages)

        data = json.loads(text)

    """

    return llm_client.chat_json(

        messages=messages,

        schema=schema,

        retry=retry,

    )