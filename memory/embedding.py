"""
Embedding Model

负责：
1. 文本向量化
2. 批量向量化
3. 提供统一 encode() 接口

后续如果切换到：
- BGE
- Jina
- Voyage
- SentenceTransformer

仅需要修改本文件即可。
"""

from __future__ import annotations

from typing import List, Sequence, Union

from openai import OpenAI

from core.config import Config
from core.logger import Logger


class EmbeddingModel:
    """统一的 Embedding 接口"""

    def __init__(self, config: Config | None = None):

        self.config = config or Config()

        self.client = OpenAI(
            base_url=self.config.embedding_model_base_url,
            api_key=self.config.embedding_model_api_key,
        )

        # Logger 类没有 get_logger() 方法，直接实例化即可，
        # 它自身提供 info()/error() 方法。
        self.logger = Logger()

        self._dimension: int | None = None

    @property
    def dimension(self) -> int:
        """
        返回Embedding维度。

        第一次调用时自动缓存，之后直接返回。
        """
        if self._dimension is None:
            self._dimension = len(self.encode("dimension_test"))

        return self._dimension

    def encode(
        self,
        texts: Union[str, Sequence[str]]
    ) -> Union[List[float], List[List[float]]]:
        """
        文本向量化

        Parameters
        ----------
        texts
            str 或 List[str]

        Returns
        -------
        List[float]
            单条文本

        List[List[float]]
            多条文本
        """

        single_input = isinstance(texts, str)

        inputs = texts if not single_input else [texts]

        try:

            response = self.client.embeddings.create(
                model=self.config.embedding_model_name,
                input=list(inputs),
            )

            vectors = [
                item.embedding
                for item in response.data
            ]

            if single_input:
                return vectors[0]

            return vectors

        except Exception as e:

            # Logger 类没有 exception() 方法，用 error() 代替，
            # 手动把异常信息拼进消息里。
            self.logger.error(
                f"Embedding生成失败: {e}"
            )

            raise

# 全局共享实例
embedding_model = EmbeddingModel()