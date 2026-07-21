# tools/web/provider.py
"""
Search Provider 抽象层

以后要换 Bing / SerpAPI，只加一个 Provider 类，
不动 SearchTool / Config 之外的任何代码。
"""
from __future__ import annotations
from abc import ABC, abstractmethod


class SearchProvider(ABC):

    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        返回统一格式：
        [{"title": str, "url": str, "snippet": str}, ...]
        """


class TavilyProvider(SearchProvider):

    def __init__(self, config):
        from tavily import TavilyClient

        if not config.tavily_api_key:
            raise ValueError("缺少 TAVILY_API_KEY，请检查 .env")

        self.client = TavilyClient(api_key=config.tavily_api_key)

    def search(self, query: str, top_k: int = 5) -> list[dict]:

        resp = self.client.search(
            query=query,
            max_results=top_k,
            search_depth="basic",   # "advanced" 更准但更贵/更慢
        )

        return [
            {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("content", ""),
            }
            for item in resp.get("results", [])
        ]


def resolve_provider(config) -> SearchProvider:

    name = (config.search_provider or "tavily").lower()

    if name == "tavily":
        return TavilyProvider(config)

    raise ValueError(f"未知搜索 Provider: {name}")