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
):
    """
    调用大模型。

    Args:
        messages: OpenAI Chat API 消息列表
        stream: 是否启用流式输出
        tools: Tool Schema 列表
        tool_choice: Tool Calling 策略

    Returns:
        str: 大模型完整回复（stream=True 和 False 均返回完整字符串）
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
        return response.choices[0].message.content

    # 流式输出
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