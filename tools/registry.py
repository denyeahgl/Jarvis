from tools.base import BaseTool
from tools.calculator import CalculatorTool

class ToolRegistry:
    """Tool 注册中心"""

    @property
    def tools(self) -> dict[str, BaseTool]:
        """返回所有已注册 Tool(只读)"""
        return self._tools.copy()

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}
        self.register(CalculatorTool())

    def __contains__(self, name: str) -> bool:
        return name in self._tools
    
    def register(self, tool: BaseTool):
        """注册 Tool"""
        if tool.name in self._tools:
            raise ValueError(
                f"Tool '{tool.name}' already registered."
            )
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> BaseTool:
        """获取 Tool"""

        if name not in self._tools:
            raise ValueError(
                f"Tool '{name}' not found."
            )

        return self._tools[name]

    def get_tool_schemas(self) -> list[dict]:
        """返回所有 Tool Schema"""

        return [
            tool.schema
            for tool in self._tools.values()
        ]

    def execute(self, name: str, **kwargs) -> dict:
        """执行 Tool"""

        tool = self.get_tool(name)

        return tool.execute(**kwargs)