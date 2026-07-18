"""
Jarvis Memory Lifecycle

Day15.3

负责:

Memory强化
Memory衰减
Memory归档


"""


from datetime import datetime



class MemoryLifecycle:



    def __init__(
        self,
        max_importance=5,
        decay_rate=0.95,
    ):


        self.max_importance = max_importance

        self.decay_rate = decay_rate





    # =========================
    # Access Reinforcement
    # =========================


    def touch(
        self,
        memory
    ):

        """
        Memory 被使用一次
        """


        memory.access_count += 1


        memory.last_accessed = (
            datetime.now()
        )



        # 小幅强化
        #
        # 注意:
        #
        # max_importance 之前只在 __init__
        # 里存了一下，从未真正用来clamp，
        # 导致 importance 会无限累加
        # (日志里能看到 6.x/7.x 的情况)。
        #
        # 这里必须用 min() 卡住上限，
        # 否则 MemoryScorer / Validator
        # 定义的 1~5 范围形同虚设。

        memory.importance = min(

            round(
                memory.importance + 0.1,
                2
            ),

            self.max_importance

        )


        return memory





    # =========================
    # Time Decay
    # =========================


    def decay(
        self,
        memory
    ):

        """
        时间衰减
        """


        memory.importance = round(

            memory.importance
            *
            self.decay_rate,

            2

        )


        return memory





    # =========================
    # Archive Check
    # =========================


    def should_archive(
        self,
        memory,
        threshold=1
    ):


        return (
            memory.importance
            
            <= threshold
        )