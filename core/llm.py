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
        # 有些兼容接口最后会返回 choices=[]（例如 usage chunk）
        if not chunk.choices:
            continue

        choice = chunk.choices[0]

        # 有些 chunk 只有 finish_reason，没有 delta
        if choice.delta is None:
            continue

        delta = choice.delta.content

        if delta is None:
            continue

        print(delta, end="", flush=True)
        reply.append(delta)