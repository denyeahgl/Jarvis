from openai import OpenAI

from core.config import Config

config = Config()

client = OpenAI(
    api_key=config.openai_api_key,
    base_url=config.base_url,
)


def chat(
    messages: list,
    stream: bool = False,
    tools: list | None = None,
    tool_choice: str | None = None,
    return_message: bool = False,
):
    """
    调用大模型。

    Args:
        messages: OpenAI Chat API 消息列表
        stream: 是否启用流式输出
        tools: Tool Schema 列表
        tool_choice: Tool Calling 策略
        return_message: 是否返回完整的 message 对象（而非纯文本）。
            Tool Calling 场景下必须为 True，因为需要读取
            message.tool_calls 字段。仅在 stream=False 时生效。

    Returns:
        - 当 return_message=True 且 stream=False 时: 返回完整的
          ChatCompletionMessage 对象（可访问 .content / .tool_calls）
        - 其他情况: 返回 str（大模型完整回复文本）
    """

    params = {
        "model": config.model_name,
        "messages": messages,
        "stream": stream,
    }

    if tools:
        params["tools"] = tools
        params["tool_choice"] = tool_choice or "auto"

    response = client.chat.completions.create(**params)

    # 非流式输出
    if not stream:
        message = response.choices[0].message

        # Tool Calling 场景：把完整 message 对象交给上层处理
        if return_message:
            return message

        return message.content

    # 流式输出（不支持 Tool Calling，只做纯文本流式打印）
    print("Jarvis: ", end="", flush=True)

    reply = []

    for chunk in response:
        if not chunk.choices:
            continue

        choice = chunk.choices[0]

        if choice.delta is None:
            continue

        delta = choice.delta.content

        if delta is None:
            continue

        print(delta, end="", flush=True)
        reply.append(delta)

    return "".join(reply)
