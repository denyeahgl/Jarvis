from tools.base import BaseTool


class TestTool(BaseTool):


    @property
    def name(self):
        return "test"



    @property
    def schema(self):

        return {
            "type":"function",
            "function":{
                "name":self.name,
                "description":"Lifecycle test",
                "parameters":{
                    "type":"object",
                    "properties":{}
                }
            }
        }



    def initialize(self):

        print(
            "[TestTool] initialized"
        )



    def execute(self, **kwargs):

        return {
            "message":
            "hello"
        }



    def shutdown(self):

        print(
            "[TestTool] shutdown"
        )