"""
core/llm_response.py

Jarvis LLM Response Layer

Day13 Step1.1 (Refactor)

职责：

- OpenAI Compatible API 调用
- Chat
- Streaming
- Tool Calling
- JSON Mode
- JSON Schema
- Retry / Fallback


上层：

core/llm.py

只负责 Facade。

架构说明（Day13 修复）：

之前这里在 __init__ 里无条件 `self.config = Config()`，
把上层（core/llm.py）已经创建好、传下来的 config 完全忽略。
如果 Config 以后从文件/环境变量读取配置，两处实例化时机不同
就可能读到不一致的配置，而且没法在测试里注入一个假的 config。

现在改成接收可选的 config 参数，由上层负责创建并传入唯一实例。
"""

from __future__ import annotations


import time


from openai import OpenAI


from core.config import Config
from core.logger import Logger



class LLMResponse:

    """
    LLM Provider 封装层
    """

    def __init__(
        self,
        model: str,
        capability,
        config: Config | None = None,
    ):

        # 优先使用上层传入的 config，避免和 core/llm.py 里的
        # 实例不一致（单一数据源）。
        self.config = config or Config()

        self.logger = Logger()

        self.model = model

        self.capability = capability


        self.client = OpenAI(

            api_key=self.config.openai_api_key,

            base_url=self.config.base_url,

        )


    # =================================================
    # Chat
    # =================================================

    def chat(
        self,
        messages: list,
        stream: bool = False,
        tools: list | None = None,
        tool_choice: str | None = None,
        return_message: bool = False,
    ):
        """
        普通 Chat。

        支持：

        - streaming
        - tool calling

        保持 Day07-Day12 兼容。
        """


        params = {

            "model": self.model,

            "messages": messages,

            "stream": stream,

        }


        # -------------------------
        # Tool Calling
        # -------------------------

        if tools:

            params["tools"] = tools


            params["tool_choice"] = (
                tool_choice
                or
                "auto"
            )


        try:

            response = (
                self.client
                .chat
                .completions
                .create(
                    **params
                )
            )


        except Exception as e:

            self.logger.error(
                f"LLM Chat失败: {e}"
            )

            raise



        # -------------------------
        # Stream
        # -------------------------

        if stream:

            return self._stream_response(
                response
            )


        message = (
            response
            .choices[0]
            .message
        )


        if return_message:

            return message


        return message.content



    # =================================================
    # Streaming
    # =================================================

    def _stream_response(
        self,
        response,
    ):

        print(
            "Jarvis: ",
            end="",
            flush=True,
        )


        result = []


        for chunk in response:


            if not chunk.choices:

                continue


            delta = (
                chunk
                .choices[0]
                .delta
                .content
            )


            if delta:

                print(
                    delta,
                    end="",
                    flush=True,
                )


                result.append(
                    delta
                )


        print()


        return "".join(result)



    # =================================================
    # JSON Chat
    # =================================================

    def chat_json(
        self,
        messages: list,
        schema: dict | None = None,
        retry: int = 1,
    ):
        """
        JSON 输出。

        返回：

        str


        不负责：

        json.loads()


        优先：

        json_schema

        ↓

        json_object

        ↓

        普通模式

        """


        last_error = None



        for attempt in range(
            retry + 1
        ):


            try:


                return self._chat_json_once(

                    messages,

                    schema,

                )


            except Exception as e:


                last_error = e


                self.logger.warning(

                    f"JSON请求失败 "
                    f"{attempt+1}/{retry+1}: {e}"

                )


                if attempt < retry:

                    time.sleep(
                        0.5
                    )



        raise last_error



    # =================================================
    # JSON Internal
    # =================================================

    def _chat_json_once(
        self,
        messages,
        schema,
    ):

        # -------------------------
        # JSON Schema
        # -------------------------

        if (

            schema

            and

            self.capability.supports_json_schema

        ):


            response = (
                self.client
                .chat
                .completions
                .create(

                    model=self.model,

                    messages=messages,


                    response_format={

                        "type":
                        "json_schema",

                        "json_schema":
                        schema,

                    },

                )
            )


            return (
                response
                .choices[0]
                .message
                .content
            )



        # -------------------------
        # JSON Object
        # -------------------------

        if self.capability.supports_json_object:


            response = (
                self.client
                .chat
                .completions
                .create(

                    model=self.model,

                    messages=messages,


                    response_format={

                        "type":
                        "json_object"

                    },

                )
            )


            return (
                response
                .choices[0]
                .message
                .content
            )



        # -------------------------
        # Fallback
        # -------------------------

        response = (
            self.client
            .chat
            .completions
            .create(

                model=self.model,

                messages=messages,

            )
        )


        return (
            response
            .choices[0]
            .message
            .content
        )