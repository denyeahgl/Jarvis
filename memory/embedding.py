"""
Jarvis Memory Embedding

Day14

使用:
BAAI/bge-small-zh-v1.5

职责:
文本 -> 向量

固定:
512 dimension
"""
import torch
from sentence_transformers import SentenceTransformer

from core.logger import Logger



class MemoryEmbedding:


    def __init__(
        self,
        model_name="BAAI/bge-small-zh-v1.5"
    ):

        self.logger = Logger()

        self.logger.info(
            f"Loading embedding model: {model_name}"
        )

        self.logger.info(
            f"Embedding device: {'cuda' if torch.cuda.is_available() else 'cpu'}"
        )

        device = "cuda" if torch.cuda.is_available() else "cpu"


        self.model = SentenceTransformer(
            model_name,
            device=device
        )


        self._dimension = None


        self.logger.info(
            "Embedding model loaded"
        )

    @property
    def model_name(self):
        return "BAAI/bge-small-zh-v1.5"


    def validate_vector(
        self,
        vector
    ):

        if len(vector)!=self.dimension:

            raise ValueError(
                f"Embedding dimension error: "
                f"{len(vector)}"
            )


    def encode(
        self,
        text:str
    ) -> list[float]:
        """
        单文本embedding
        """

        vector = self.model.encode(
            text,
            normalize_embeddings=True
        )


        return vector.tolist()



    def encode_batch(
        self,
        texts:list[str]
    ) -> list[list[float]]:
        """
        批量embedding
        """

        vectors = self.model.encode(
            texts,
            normalize_embeddings=True
        )


        return vectors.tolist()



    @property
    def dimension(self):

        if self._dimension is None:

            self._dimension = len(
                self.encode(
                    "dimension test"
                )
            )


        return self._dimension