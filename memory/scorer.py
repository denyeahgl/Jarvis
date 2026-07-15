"""
Memory Scorer 2.0

考虑：

1. 内容关键词
2. Memory类型
3. 长期价值
"""


class MemoryScorer:


    def __init__(self):


        self.keyword_scores={

            "Jarvis":3,

            "Agent":2,

            "项目":2,

            "开发":2,

            "架构":2,

            "设计":2,

            "目标":2,

            "计划":2,


            "喜欢":1,

            "习惯":1,

        }



        self.type_scores={


            "project":3,


            "preference":2,


            "skill":2,


            "fact":1,


            "conversation":0,

        }



    def score(
        self,
        content:str,
        memory_type:str
    )->int:



        if not content:

            return 0



        score=0



        # 类型权重

        score += self.type_scores.get(
            memory_type,
            0
        )



        # 关键词权重

        for key,value in self.keyword_scores.items():

            if key in content:

                score+=value



        # 长度

        if len(content)>20:

            score+=1



        return min(
            score,
            5
        )