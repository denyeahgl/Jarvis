"""
memory/extractor.py

Jarvis Memory Extractor

Day13 Step2 (Refactor)

职责：

User Input
        |
        v
LLM JSON Extraction
        |
        v
粗粒度结构过滤 (是否是 list[dict]，content 是否非空)
        |
        v
Memory Dict List (原始，未做字段归一化)


不负责：

- 字段级校验 / 归一化 (交给 memory/validator.py, 单一数据源)
- Embedding
- Store
- Retrieval
- Lifecycle

架构说明（Day13 修复）：

之前这里有一个 `_validate()` 方法，和 memory/validator.py 做的是同一件事
（校验 content / memory_type / importance），但两边的归一化规则不一致
（例如 memory_type 的同义词映射只在 validator 里做），导致同一条数据在
pipeline 不同阶段可能得到不同结果。

现在 Extractor 只做"结构过滤"（是不是 list、是不是 dict、content 是否为空），
真正的字段校验/归一化全部交给 MemoryValidator，避免双重实现、双重数据源。
"""

from __future__ import annotations


import json
import re
from typing import Callable


from core.llm import chat_json as default_chat_json
from core.logger import Logger


from memory.prompts import (
    MEMORY_EXTRACTOR_PROMPT
)



class MemoryExtractor:
    """
    LLM Memory Extractor
    """

    def __init__(
        self,
        chat_json_fn: Callable | None = None,
    ):

        self.logger = Logger()

        # 依赖注入：默认使用 core.llm.chat_json，
        # 单测时可以传入一个 fake 函数，不必 monkeypatch 模块内部。
        self._chat_json = chat_json_fn or default_chat_json



    # =====================================================
    # Public API
    # =====================================================

    def extract(
        self,
        text: str,
    ) -> list[dict]:
        """
        提取长期记忆（未做字段归一化，交给 MemoryValidator 处理）。

        Input:

        用户文本


        Output:

        [
            {
                "content": "用户喜欢足球",
                "memory_type": "preference",
                "importance": 5
            }
        ]

        """

        if not text:

            return []


        messages = [

            {
                "role":
                "system",

                "content":
                MEMORY_EXTRACTOR_PROMPT,

            },


            {
                "role":
                "user",

                "content":
                text,

            }

        ]


        try:

            response = self._chat_json(

                messages=messages,

            )


        except Exception as e:

            self.logger.error(

                f"Memory Extractor 调用失败: {e}"

            )

            return []



        if not response:

            return []



        memories = self.parse(

            response

        )


        self.logger.info(

            f"Extractor 提取 {len(memories)} 条记忆"

        )


        return memories



    # =====================================================
    # Parse
    # =====================================================

    def parse(
        self,
        text: str,
    ) -> list[dict]:
        """
        JSON解析。

        兼容：

        - JSON Mode
        - 普通文本Fallback
        - markdown JSON

        注意：

        这里只做最基础的结构过滤（是否为 list、是否为 dict、
        content 是否非空），不做 memory_type / importance 的
        归一化 —— 那是 memory/validator.py 的职责，避免两处
        逻辑重复且不一致。
        """

        if not text:

            return []



        text = self._clean_json(
            text
        )



        try:

            data = json.loads(
                text
            )


        except Exception as e:


            self.logger.error(

                f"Memory JSON解析失败: {e}"

            )


            return []



        if not isinstance(
            data,
            list,
        ):

            return []



        result = []


        for item in data:

            if not isinstance(item, dict):

                continue


            content = str(
                item.get("content", "")
            ).strip()


            if not content:

                continue


            # 原样透传给 Validator，不在这里做类型/重要度归一化
            result.append(item)


        return result



    # =====================================================
    # JSON Clean
    # =====================================================

    def _clean_json(
        self,
        text: str,
    ) -> str:
        """
        清理模型输出。

        兼容：

        ```json
        []
        ```

        """

        text = text.strip()


        text = re.sub(

            r"^```json",

            "",

            text,

            flags=re.I,

        )


        text = re.sub(

            r"^```",

            "",

            text,

        )


        text = re.sub(

            r"```$",

            "",

            text,

        )


        text = text.strip()



        # 提取数组

        start = text.find("[")

        end = text.rfind("]")


        if (

            start != -1

            and

            end != -1

        ):

            return text[
                start:end+1
            ]


        return text