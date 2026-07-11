from openai import OpenAI

from core.config import Config

config = Config()

client = OpenAI(
    api_key=config.openai_api_key,
    base_url=config.base_url,
)


def chat(messages: list, stream: bool = False) -> str:
    """
    调用大模型。

    Args:
        messages: OpenAI Chat API 消息列表
        stream: 是否启用流式输出

    Returns:
        str: 大模型完整回复
    """

    response = client.chat.completions.create(
        model=config.model_name,
        messages=messages,
        stream=stream,
    )

    # 非流式输出
    if not stream:
        return response.choices[0].message.content

    # 流式输出
    print("Jarvis: ", end="", flush=True)

    reply = []

    for chunk in response:
        delta = chunk.choices[0].delta.content

        if delta:
            print(delta, end="", flush=True)
            reply.append(delta)

    print()

    return "".join(reply)