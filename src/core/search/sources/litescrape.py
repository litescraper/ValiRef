"""Optional API-backed Google snippets, not verified academic metadata."""

# Candidate for etheia-agent-map — no equivalent could be inspected (404).
# See: https://github.com/Etheia-Consulting-LLC/etheia-agent-map

import os

import httpx

from ..base import SearchResult, SearchTool


class LitescrapeSearch(SearchTool):
    """Use the existing cache, request queue, retry and circuit-breaker path."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        super().__init__()
        self._api_key = api_key or os.getenv("LITESCRAPE_API_KEY")
        self._base_url = (
            base_url or os.getenv("LITESCRAPE_BASE_URL") or "https://api.litescrape.com"
        ).rstrip("/")

    async def _perform_asearch(self, query: str, limit: int) -> list[SearchResult]:
        if not self._api_key:
            raise ValueError("Set LITESCRAPE_API_KEY for this search source")
        limit = max(1, min(10, limit))
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                self._base_url + "/api/google/search",
                params={"q": query, "num": limit},
                headers={"Authorization": f"Bearer {self._api_key}"},
            )
            response.raise_for_status()
            return [
                SearchResult(
                    title=item.get("title", "N/A"),
                    authors=[],
                    published_date="N/A",
                    abstract=item.get("snippet", "N/A"),
                    venue="Web search (snippet only)",
                    url=item["link"],
                    source="litescrape",
                )
                for item in response.json().get("organic_results", [])
                if item.get("link")
            ]
