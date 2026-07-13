from tools.base import BaseTool


class CalculatorTool(BaseTool):

    @property
    def name(self) -> str:
        return "calculator"

    @property
    def schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": "Evaluate a mathematical expression.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "The mathematical expression to evaluate."
                        }
                    },
                    "required": ["expression"]
                }
            }
        }

    def execute(self, **kwargs) -> dict:
        expression = kwargs.get("expression")

        if not expression:
            raise ValueError("Missing 'expression' parameter.")
        
        result = self._calculate(expression)
        
        return {
            "result": result
        }
    
    def _calculate(self, expression: str) -> float:
        """
        计算数学表达式的结果。

        :param expression: 数学表达式
        :return: 计算结果
        """
        allowed = "0123456789+-*/(). "

        if any(c not in allowed for c in expression):
            raise ValueError("Invalid characters in expression.")

        result = eval(
            expression,
            {"__builtins__": {}},
            {}
        )

        return result