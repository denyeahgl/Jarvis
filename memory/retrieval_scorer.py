"""
Jarvis Memory Retrieval Scorer

Day15.2

负责：

根据多个因素重新排序 Memory


Formula:

score =
0.7 * semantic
+
0.2 * importance
+
0.1 * confidence


"""


class RetrievalScorer:


    def __init__(self):


        self.weights = {

            "semantic":0.7,

            "importance":0.2,

            "confidence":0.1,

        }



    def score(
        self,
        memory,
        semantic_score: float,
    ):

        """
        返回最终检索分数
        """


        importance_score = (
            memory.importance / 5
        )


        confidence_score = (
            memory.confidence
        )



        final_score = (

            self.weights["semantic"]
            *
            semantic_score

            +

            self.weights["importance"]
            *
            importance_score

            +

            self.weights["confidence"]
            *
            confidence_score

        )


        return round(
            final_score,
            4
        )