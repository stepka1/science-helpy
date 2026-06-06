"""Клиент-адаптер над поиском из agents_system."""
import asyncio
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from app.application.dto.article_dto import ArticleSearchResultDTO
from app.infrastructure.config.settings import settings

AGENTS_ROOT = Path(settings.PROJECT_ROOT) / "agents_system"
if str(AGENTS_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENTS_ROOT))

from agent_tools.tools import search_arxiv_papers  # type: ignore  # noqa: E402


class ArxivClient:
    """Тонкий адаптер backend над search tool из agents_system."""

    @staticmethod
    def _parse_search_output(raw: str) -> List[ArticleSearchResultDTO]:
        results: List[ArticleSearchResultDTO] = []
        pattern = re.compile(
            r"^\s*\d+\.\s+ИСПОЛЬЗУЙ ЭТОТ ID ДЛЯ СКАЧИВАНИЯ:\s*(?P<id>\S+)\s*\n"
            r"\s*Название:\s*(?P<title>[^\n]+)\n"
            r"\s*Авторы:\s*(?P<authors>[^\n]+)\n"
            r"\s*Дата:\s*(?P<published>\d{4}-\d{2}-\d{2})\n"
            r"\s*Аннотация:\s*(?P<summary>.*?)(?=\n\s*\d+\.\s+ИСПОЛЬЗУЙ ЭТОТ ID ДЛЯ СКАЧИВАНИЯ:|\Z)",
            re.S | re.M,
        )
        for match in pattern.finditer(raw):
            clean_id = match.group("id").split("v")[0]
            published_date = datetime.strptime(match.group("published"), "%Y-%m-%d")
            summary = match.group("summary").strip()
            if summary.endswith("..."):
                summary = summary[:-3].rstrip()
            results.append(
                ArticleSearchResultDTO(
                    arxiv_id=clean_id,
                    title=match.group("title").strip(),
                    authors=[author.strip() for author in match.group("authors").split(",") if author.strip()],
                    abstract=summary,
                    published_date=published_date,
                    categories=[],
                    pdf_url=f"https://arxiv.org/pdf/{clean_id}.pdf",
                    tex_url=f"https://arxiv.org/e-print/{clean_id}",
                )
            )
        return results

    async def search_articles(
        self,
        query: str,
        max_results: int = 10,
        sort_by: str = "submittedDate",
        sort_order: str = "descending",
    ) -> List[ArticleSearchResultDTO]:
        """Поиск статей через agents_system tool."""

        def _search() -> List[ArticleSearchResultDTO]:
            sort_strategy = "submittedDate" if sort_by == "submittedDate" else "relevance"
            raw = search_arxiv_papers.invoke(
                {
                    "query": query,
                    "limit": max_results,
                    "sort_strategy": sort_strategy,
                    "search_in_title_only": False,
                }
            )
            return self._parse_search_output(raw)

        return await asyncio.to_thread(_search)

    async def get_article_by_id(self, arxiv_id: str) -> Optional[ArticleSearchResultDTO]:
        """Получить метаданные статьи через search tool."""
        clean_id = arxiv_id.split("/")[-1].split("v")[0]

        def _get() -> Optional[ArticleSearchResultDTO]:
            raw = search_arxiv_papers.invoke(
                {
                    "query": clean_id,
                    "limit": 5,
                    "sort_strategy": "relevance",
                    "search_in_title_only": False,
                }
            )
            results = self._parse_search_output(raw)
            for result in results:
                if result.arxiv_id == clean_id:
                    return result
            return results[0] if results else None

        return await asyncio.to_thread(_get)
