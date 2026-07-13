from abc import ABC, abstractmethod


class BaseTool(ABC):
    """
    所有 Tool 的抽象基类。

    每个 Tool 必须实现：
    - name：Tool 唯一名称
    - schema：OpenAI Tool Schema
    - execute()：执行 Tool
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool 的唯一名称"""
        raise NotImplementedError

    @property
    @abstractmethod
    def schema(self) -> dict:
        """返回 OpenAI Tool Schema"""
        raise NotImplementedError

    @abstractmethod
    def execute(self, **kwargs) -> dict:
        """执行 Tool"""
        raise NotImplementedError