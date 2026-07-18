"""
Jarvis Vector Store

Day14

FAISS based vector storage

负责:
- vector add
- similarity search
- index persistence

不负责:
- memory metadata
"""


import os
import pickle

import faiss
import numpy as np



class VectorStore:


    def __init__(
        self,
        dimension=512,
        index_path="data/vector/faiss.index",
        mapping_path="data/vector/vector_mapping.pkl"
    ):

        self.dimension = dimension

        self.index_path = index_path

        self.mapping_path = mapping_path


        os.makedirs(
            os.path.dirname(index_path),
            exist_ok=True
        )


        self.index = (
            faiss.IndexFlatIP(
                dimension
            )
        )


        # faiss内部id -> memory_id

        self.id_mapping = []



        self.load()



    def add(
        self,
        vector,
        memory_id
    ):

        vector = np.array(
            [vector],
            dtype="float32"
        )


        self.index.add(
            vector
        )


        self.id_mapping.append(
            memory_id
        )


        self.save()



    def search(
        self,
        query_vector,
        top_k=5
    ):


        query = np.array(
            [query_vector],
            dtype="float32"
        )


        scores, ids = (
            self.index.search(
                query,
                top_k
            )
        )


        results=[]


        for score, idx in zip(
            scores[0],
            ids[0]
        ):

            if idx == -1:
                continue


            results.append(
                {
                    "memory_id":
                        self.id_mapping[idx],

                    "score":
                        float(score)
                }
            )


        return results


    def get_vector(
        self,
        memory_id: str
    ):
        """
        根据 memory_id 获取 embedding 向量
        """

        try:

            if memory_id not in self.id_mapping:

                return None


            index_id = self.id_mapping.index(
                memory_id
            )


            vector = self.index.reconstruct(
                index_id
            )


            return vector.tolist()


        except Exception as e:

            print(
                f"Get vector error: {e}"
            )

            return None





    def save(self):

        faiss.write_index(
            self.index,
            self.index_path
        )


        with open(
            self.mapping_path,
            "wb"
        ) as f:

            pickle.dump(
                self.id_mapping,
                f
            )



    def load(self):

        if os.path.exists(
            self.index_path
        ):

            self.index = (
                faiss.read_index(
                    self.index_path
                )
            )


        if os.path.exists(
            self.mapping_path
        ):

            with open(
                self.mapping_path,
                "rb"
            ) as f:

                self.id_mapping = (
                    pickle.load(f)
                )