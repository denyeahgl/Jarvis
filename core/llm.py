from openai import OpenAI

from core.config import Config

config = Config()

client = OpenAI(
    api_key=config.openai_api_key,
    base_url=config.base_url,
)


def chat(messages: list, stream: bool = False):
    """
    调用大模型。

    Args:
        messages: OpenAI 消息列表
        stream: 是否启用流式输出

    Returns:
        非流式返回字符串；
        流式直接输出。
    """

    response = client.chat.completions.create(
        model=config.model_name,
        messages=messages,
        stream=stream,
    )

    if not stream:
        return response.choices[0].message.content

    print("Jarvis: ", end="", flush=True)

    for chunk in response:
        delta = chunk.choices[0].delta.content

        if delta:
            print(delta, end="", flush=True)

    print()