from abc import ABC, abstractmethod


class BaseTool(ABC):
    """
    Tool 基础接口

    生命周期：

    initialize()
        |
        execute()
        |
    shutdown()
    """



    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError



    @property
    def metadata(self) -> dict:

        return {
            "name": self.name,
            "version": "1.0"
        }



    def initialize(self):
        """
        Tool 初始化

        默认无需处理
        """

        pass



    @property
    @abstractmethod
    def schema(self) -> dict:
        raise NotImplementedError



    @abstractmethod
    def execute(self, **kwargs) -> dict:
        raise NotImplementedError



    def shutdown(self):
        """
        Tool 关闭

        默认无需处理
        """

        pass