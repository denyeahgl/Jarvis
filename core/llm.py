"""
LLM 模块

负责：
- 创建 OpenAI Client
- 调用大模型
- 返回模型回复
"""

from openai import OpenAI

from core.config import Config

config = Config()

client = OpenAI(
    api_key=config.openai_api_key,
    base_url=config.base_url,
)

def ask_llm(prompt: str) -> str:
    """
    向大模型发送请求，并返回回复。

    Args:
        prompt: 用户输入

    Returns:
        模型返回的文本
    """

    response = client.chat.completions.create(
        model=config.model_name,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


