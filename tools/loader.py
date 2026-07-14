"""
Tool Loader

负责：

1. 扫描 tools 目录
2. 发现 Tool 类
3. 自动实例化
4. 返回 Tool 实例
"""


import inspect
import importlib
from pathlib import Path

from tools.base import BaseTool



class ToolLoader:
    """
    Tool 自动加载器
    """



    def __init__(self, package="tools"):

        self.package = package



    def load(self) -> list[BaseTool]:
        """
        自动发现并加载 Tool

        return:
            Tool实例列表
        """

        tools = []


        package_path = Path(
            __file__
        ).parent


        for file in package_path.glob("*.py"):


            # 跳过自身
            if file.name in [
                "__init__.py",
                "base.py",
                "loader.py",
                "registry.py"
            ]:
                continue



            module_name = (
                f"{self.package}.{file.stem}"
            )


            module = importlib.import_module(
                module_name
            )


            for _, obj in inspect.getmembers(
                module,
                inspect.isclass
            ):

                # 判断是否是 Tool
                if (
                    issubclass(obj, BaseTool)
                    and obj is not BaseTool
                ):

                    tool = obj()

                    print(
                        f"[ToolLoader] loaded: {tool.name}"
                    )

                    tools.append(tool)


        return tools