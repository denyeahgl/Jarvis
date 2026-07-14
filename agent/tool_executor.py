"""
Tool Executor

负责：
1. Tool 查找
2. 参数解析
3. Tool 执行
4. 异常处理
"""

import json


class ToolExecutor:
    """Tool 执行器"""


    def __init__(self, registry):

        self.registry = registry



    def execute(self, tool_call):

        tool_name = (
            tool_call.function.name
        )


        try:

            arguments = json.loads(
                tool_call.function.arguments
                or "{}"
            )

        except json.JSONDecodeError:

            arguments = {}



        try:

            result = self.registry.execute(
                tool_name,
                **arguments
            )


            output = {
                "success": True,
                "result": result
            }


        except Exception as e:

            output = {
                "success": False,
                "error": str(e)
            }



        return {

            "role": "tool",

            "tool_call_id":
                tool_call.id,

            "content":
                json.dumps(
                    output,
                    ensure_ascii=False
                )
        }