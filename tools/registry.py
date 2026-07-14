from tools.base import BaseTool
from tools.loader import ToolLoader

class ToolRegistry:
    """
    Tool 注册中心

    负责：

    1. 保存 Tool
    2. 查询 Tool
    3. 提供 Tool Schema
    4. 调用 Tool
    """


    def __init__(self):

        self._tools: dict[str, BaseTool] = {}



    @property
    def tools(self) -> dict[str, BaseTool]:
        """
        返回所有 Tool（只读）
        """

        return self._tools.copy()



    def __contains__(self, name: str) -> bool:
        """
        判断 Tool 是否存在
        """

        return name in self._tools


    def load_tools(self) -> list[str]:
        """
        自动加载 Tool

        return:
            成功加载的 Tool 名称
        """

        loader = ToolLoader()
        tools = loader.load()
        loaded = []

        for tool in tools:

            self.register(tool)

            loaded.append(
                tool.name
            )

        return loaded



    def list_tools(self):
        """
        查看当前 Tool
        """
        return list(
            self._tools.keys()
        )


    def register(self, tool: BaseTool):
        """
        注册 Tool
        """

        if not isinstance(tool, BaseTool):
            raise TypeError(
                "Only BaseTool instance can be registered."
            )


        if tool.name in self._tools:

            raise ValueError(
                f"Tool '{tool.name}' already registered."
            )


        self._tools[tool.name] = tool



    def unregister(self, name: str):
        """
        移除 Tool
        """

        if name not in self._tools:

            raise ValueError(
                f"Tool '{name}' not found."
            )


        del self._tools[name]



    def get_tool(self, name: str) -> BaseTool:
        """
        获取指定 Tool
        """

        if name not in self._tools:

            raise ValueError(
                f"Tool '{name}' not found."
            )


        return self._tools[name]



    def get_tool_schemas(self) -> list[dict]:
        """
        提供给 LLM 的 Tool Schema
        """

        return [
            tool.schema
            for tool in self._tools.values()
        ]



    def get_metadata(self) -> list[dict]:
        """
        获取所有 Tool 元信息

        给 Agent 自我认知使用
        """

        return [
            tool.metadata
            for tool in self._tools.values()
        ]


    def initialize_tools(self):
        """
        初始化所有 Tool
        """

        for tool in self._tools.values():

            tool.initialize()   




    def execute(
        self,
        name: str,
        **kwargs
    ) -> dict:
        """
        执行 Tool
        """

        tool = self.get_tool(name)

        return tool.execute(**kwargs)
    

    def shutdown_tools(self):
        """
    关闭所有 Tool
        """

        for tool in self._tools.values():

            tool.shutdown()