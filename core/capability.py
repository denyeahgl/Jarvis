"""
core/capability.py

Jarvis Capability Layer

Day13 (Refactor)

描述当前 LLM Provider 的能力。

以后：

OpenAI
OpenRouter
Gemini
Claude
Ollama
vLLM

都通过这里统一管理。

架构说明（Day13 修复）：

之前文件末尾有一个模块级全局实例：

    capability = CapabilityResolver().resolve()

但它用的是默认 Config()，和 core/llm.py 里实际使用的
`CapabilityResolver(config).resolve()` 并不是同一个实例，
也没有任何模块真正 import 它 —— 纯粹的死代码，还容易让人
误以为这里才是"唯一真源"。已删除，只保留类定义；由使用方
显式传入 config 并自行 resolve，避免出现两份不一致的实例。
"""

from __future__ import annotations

from dataclasses import dataclass

from core.config import Config


@dataclass(slots=True)
class ModelCapability:
    """
    模型能力描述。
    """

    supports_stream: bool = True

    supports_tools: bool = True

    supports_json_object: bool = False

    supports_json_schema: bool = False

    supports_vision: bool = False


class CapabilityResolver:
    """
    根据当前模型自动推断能力。

    后续也可以改成：

    config.json

    或 provider.yaml
    """

    def __init__(
        self,
        config: Config | None = None,
    ):

        self.config = config or Config()

    def resolve(self) -> ModelCapability:

        model = (
            self.config.model_name
            or ""
        ).lower()

        capability = ModelCapability()

        # -------------------------
        # OpenAI GPT-4o
        # -------------------------

        if "gpt-4o" in model:

            capability.supports_json_object = True

            capability.supports_json_schema = True

            capability.supports_vision = True

            return capability

        # -------------------------
        # GPT-4.1
        # -------------------------

        if "gpt-4.1" in model:

            capability.supports_json_object = True

            capability.supports_json_schema = True

            return capability

        # -------------------------
        # GPT-5
        # -------------------------

        if "gpt-5" in model:

            capability.supports_json_object = True

            capability.supports_json_schema = True

            return capability

        # -------------------------
        # Claude
        # -------------------------

        if "claude" in model:

            capability.supports_json_object = True

            capability.supports_vision = True

            return capability

        # -------------------------
        # Gemini
        # -------------------------

        if "gemini" in model:

            capability.supports_json_object = True

            capability.supports_vision = True

            return capability

        # -------------------------
        # Qwen
        # -------------------------

        if "qwen" in model:

            capability.supports_json_object = True

            return capability

        # -------------------------
        # GLM
        # -------------------------

        if "glm" in model:

            capability.supports_json_object = True

            return capability

        # -------------------------
        # DeepSeek
        # -------------------------

        if "deepseek" in model:

            capability.supports_json_object = True

            return capability

        # -------------------------
        # 默认能力
        # -------------------------

        return capability