"""Единая orchestration layer между backend и agents_system."""
import asyncio
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional

from langchain_core.messages import HumanMessage, ToolMessage

from app.application.dto.article_dto import ArticleSearchResultDTO
from app.application.dto.evaluation_dto import EvaluationDTO
from app.application.dto.review_dto import ReviewDTO
from app.domain.entities.article import Article
from app.infrastructure.config.settings import settings
from app.shared.exceptions.base import ServiceUnavailableError

AGENTS_ROOT = Path(settings.PROJECT_ROOT) / "agents_system"
if str(AGENTS_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENTS_ROOT))


class OrchestrationService:
    """Тонкий backend-адаптер над CoordinatorAgent и GraphMAS."""

    def __init__(self) -> None:
        self._coordinator: Optional[Any] = None
        self._graph_mas: Optional[Any] = None

        if settings.OPENROUTER_API_KEY:
            os.environ.setdefault("OPENROUTER_API_KEY", settings.OPENROUTER_API_KEY)
            os.environ.setdefault("OPENROUTER_BASE_URL", settings.OPENROUTER_BASE_URL)
            if settings.TAVILY_API_KEY:
                os.environ.setdefault("TAVILY_API_KEY", settings.TAVILY_API_KEY)

    def _require_coordinator(self) -> Any:
        if self._coordinator is None:
            if not settings.OPENROUTER_API_KEY:
                raise ServiceUnavailableError("CoordinatorAgent is unavailable. Configure OPENROUTER_API_KEY and rebuild backend.")
            from agents.coordinator_agent import CoordinatorAgent  # type: ignore

            self._coordinator = CoordinatorAgent()
        return self._coordinator

    def _require_graph(self) -> Any:
        if self._graph_mas is None:
            if not settings.OPENROUTER_API_KEY:
                raise ServiceUnavailableError("GraphMAS is unavailable. Configure OPENROUTER_API_KEY and rebuild backend.")
            from graph_mas import GraphMAS  # type: ignore

            self._graph_mas = GraphMAS()
        return self._graph_mas

    @staticmethod
    def _normalize_tool_path(path_value: Optional[str]) -> Optional[str]:
        if not path_value:
            return path_value

        normalized = (
            path_value.replace("\u2018", "'")
            .replace("\u2019", "'")
            .replace("\u201c", '"')
            .replace("\u201d", '"')
            .strip()
            .strip("'\"`")
            .strip()
        )
        return normalized or None

    @staticmethod
    def _parse_search_tool_output(raw: str) -> List[ArticleSearchResultDTO]:
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
            summary = match.group("summary").strip()
            if summary.endswith("..."):
                summary = summary[:-3].rstrip()
            results.append(
                ArticleSearchResultDTO(
                    arxiv_id=clean_id,
                    title=match.group("title").strip(),
                    authors=[author.strip() for author in match.group("authors").split(",") if author.strip()],
                    abstract=summary,
                    published_date=datetime.strptime(match.group("published"), "%Y-%m-%d"),
                    categories=[],
                    pdf_url=f"https://arxiv.org/pdf/{clean_id}.pdf",
                    tex_url=f"https://arxiv.org/e-print/{clean_id}",
                )
            )
        return results

    @staticmethod
    def _split_review_sections(full_text: str) -> dict[str, str]:
        headings = {
            "резюме": "summary",
            "executive summary": "summary",
            "ключевые идеи и методы": "methods",
            "методы": "methods",
            "результаты и эксперименты": "results",
            "результаты": "results",
            "сильные и слабые стороны": "criticism",
            "критика": "criticism",
            "практическое применение": "application",
            "применение": "application",
            "вердикт": "verdict",
        }
        sections = {key: "" for key in ("summary", "methods", "results", "criticism", "application", "verdict")}
        current = "summary"
        buckets = {key: [] for key in sections}
        for raw_line in full_text.replace("\r\n", "\n").split("\n"):
            line = raw_line.strip()
            if line.startswith("#"):
                current = headings.get(line.lstrip("#").strip().lower(), current)
                continue
            buckets[current].append(raw_line)
        for key, lines in buckets.items():
            sections[key] = "\n".join(lines).strip()
        if not sections["summary"]:
            sections["summary"] = full_text.strip()
        if not sections["verdict"]:
            sections["verdict"] = sections["summary"]
        return sections

    @staticmethod
    def _extract_tool_messages(messages: list[Any], tool_name: str) -> list[ToolMessage]:
        return [msg for msg in messages if isinstance(msg, ToolMessage) and getattr(msg, "name", None) == tool_name]

    async def search_articles(self, query: str, max_results: int = 10) -> List[ArticleSearchResultDTO]:
        """Поиск статей через CoordinatorAgent."""
        coordinator = self._require_coordinator()

        def _run() -> List[ArticleSearchResultDTO]:
            state = {
                "messages": [
                    HumanMessage(
                        content=(
                            f"Найди до {max_results} статей по запросу '{query}'. "
                            "Покажи конкретный список результатов и не скачивай статьи."
                        )
                    )
                ]
            }
            result = coordinator.run_with_state(state)
            tool_messages = self._extract_tool_messages(result["messages"], "search_arxiv_papers")
            if not tool_messages:
                raise ServiceUnavailableError("CoordinatorAgent did not return search results.")
            return self._parse_search_tool_output(tool_messages[-1].content)

        return await asyncio.to_thread(_run)

    async def download_article(self, arxiv_id: str) -> dict[str, Any]:
        """Скачивание статьи через CoordinatorAgent."""
        coordinator = self._require_coordinator()

        def _run() -> dict[str, Any]:
            state = {
                "messages": [
                    HumanMessage(
                        content=(
                            f"Скачай статью с arXiv ID {arxiv_id}. "
                            "Скачай PDF и TeX, если они доступны, но не оценивай и не пиши обзор."
                        )
                    )
                ]
            }
            result = coordinator.run_with_state(state)
            pdf_messages = self._extract_tool_messages(result["messages"], "download_arxiv_paper")
            tex_messages = self._extract_tool_messages(result["messages"], "download_arxiv_tex")
            if not pdf_messages and not tex_messages:
                raise ServiceUnavailableError("CoordinatorAgent did not download the article.")

            pdf_payload: dict[str, Any] = {}
            if pdf_messages:
                try:
                    pdf_payload = json.loads(pdf_messages[-1].content)
                except json.JSONDecodeError as exc:
                    raise ServiceUnavailableError("CoordinatorAgent returned invalid PDF download payload.") from exc

            tex_directory: Optional[str] = None
            if tex_messages:
                try:
                    tex_payload = json.loads(tex_messages[-1].content)
                    if tex_payload.get("status") == "success":
                        tex_directory = self._normalize_tool_path(tex_payload.get("directory"))
                except json.JSONDecodeError:
                    tex_directory = None

            search_results = self._parse_search_tool_output(
                self._extract_tool_messages(result["messages"], "search_arxiv_papers")[-1].content
            ) if self._extract_tool_messages(result["messages"], "search_arxiv_papers") else []
            article_meta = next((item for item in search_results if item.arxiv_id == arxiv_id), None)

            return {
                "arxiv_id": arxiv_id,
                "title": (article_meta.title if article_meta else pdf_payload.get("title")) or arxiv_id,
                "authors": (article_meta.authors if article_meta else pdf_payload.get("authors")) or [],
                "abstract": article_meta.abstract if article_meta else "",
                "published_date": article_meta.published_date if article_meta else (
                    datetime.strptime(pdf_payload["published"], "%Y-%m-%d") if pdf_payload.get("published") else None
                ),
                "categories": article_meta.categories if article_meta and article_meta.categories else [],
                "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}.pdf",
                "tex_url": f"https://arxiv.org/e-print/{arxiv_id}",
                "local_pdf_path": pdf_payload.get("path"),
                "local_tex_path": tex_directory,
            }

        return await asyncio.to_thread(_run)

    async def parse_article(self, article: Article) -> str:
        """Парсинг статьи через agents_system tools."""
        graph = self._require_graph()

        def _run() -> str:
            if article.local_tex_path:
                from agent_tools.tools import parse_tex_file  # type: ignore

                parsed = parse_tex_file.invoke({"tex_path": self._normalize_tool_path(article.local_tex_path)})
                if parsed and not parsed.startswith("Ошибка:"):
                    return parsed
            if article.local_pdf_path:
                from agent_tools.tools import parse_pdf_file  # type: ignore

                return parse_pdf_file.invoke({"pdf_path": article.local_pdf_path})
            raise ServiceUnavailableError("Article has no downloadable assets for parsing.")

        return await asyncio.to_thread(_run)

    async def evaluate_article(self, article: Article) -> tuple[EvaluationDTO, dict[str, Any]]:
        """Полная orchestration-оценка через GraphMAS."""
        graph = self._require_graph()

        def _run() -> tuple[EvaluationDTO, dict[str, Any]]:
            paper_content = article.parsed_content
            if not paper_content:
                if article.local_tex_path:
                    from agent_tools.tools import parse_tex_file  # type: ignore

                    paper_content = parse_tex_file.invoke({"tex_path": self._normalize_tool_path(article.local_tex_path)})
                elif article.local_pdf_path:
                    from agent_tools.tools import parse_pdf_file  # type: ignore

                    paper_content = parse_pdf_file.invoke({"pdf_path": article.local_pdf_path})
            if not paper_content:
                raise ServiceUnavailableError("GraphMAS could not obtain article content for evaluation.")

            extracted_images_path = None
            if article.local_pdf_path:
                from agent_tools.tools import parse_img_from_pdf  # type: ignore

                raw = parse_img_from_pdf.invoke({"path_to_pdf": article.local_pdf_path})
                image_paths = [line.strip() for line in raw.splitlines() if line.strip().startswith("/")]
                if image_paths:
                    extracted_images_path = str(Path(image_paths[0]).parent)

            initial_state = {
                "messages": [HumanMessage(content="Оцени статью и покажи итоговую оценку. [EVAL]")],
                "selected_paper_path": self._normalize_tool_path(article.local_tex_path or article.local_pdf_path),
                "paper_content": paper_content,
                "extracted_images_path": extracted_images_path,
            }
            result = graph.graph.invoke(
                initial_state,
                config={"configurable": {"thread_id": f"eval-{article.arxiv_id}-{datetime.utcnow().timestamp()}"}},
            )
            review_data = result.get("review_data")
            if review_data is None:
                raise ServiceUnavailableError("GraphMAS did not return review_data.")
            dto = EvaluationDTO(
                id=uuid4(),
                article_id=article.id,
                category=f"{review_data.nlp_category} ({'relevant' if review_data.is_relevant else 'not relevant'})",
                relevance=review_data.one_sentence_summary,
                novelty_score=review_data.scores.novelty,
                methodology_score=review_data.scores.rigor,
                impact_score=review_data.scores.impact,
                overall_score=review_data.scores.overall,
                pros=list(review_data.pros),
                cons=list(review_data.cons),
                justification=review_data.reasoning,
                created_at=datetime.utcnow(),
                updated_at=None,
            )
            return dto, {
                "parsed_content": result.get("paper_content") or paper_content,
                "selected_paper_path": self._normalize_tool_path(result.get("selected_paper_path")),
                "extracted_images_path": result.get("extracted_images_path"),
            }

        from uuid import uuid4

        return await asyncio.to_thread(_run)

    async def write_review(self, article: Article) -> tuple[ReviewDTO, dict[str, Any]]:
        """Полная orchestration-генерация обзора через GraphMAS."""
        graph = self._require_graph()

        def _run() -> tuple[ReviewDTO, dict[str, Any]]:
            paper_content = article.parsed_content
            if not paper_content:
                if article.local_tex_path:
                    from agent_tools.tools import parse_tex_file  # type: ignore

                    paper_content = parse_tex_file.invoke({"tex_path": self._normalize_tool_path(article.local_tex_path)})
                elif article.local_pdf_path:
                    from agent_tools.tools import parse_pdf_file  # type: ignore

                    paper_content = parse_pdf_file.invoke({"pdf_path": article.local_pdf_path})
            if not paper_content:
                raise ServiceUnavailableError("GraphMAS could not obtain article content for writing review.")

            extracted_images_path = None
            if article.local_pdf_path:
                from agent_tools.tools import parse_img_from_pdf  # type: ignore

                raw = parse_img_from_pdf.invoke({"path_to_pdf": article.local_pdf_path})
                image_paths = [line.strip() for line in raw.splitlines() if line.strip().startswith("/")]
                if image_paths:
                    extracted_images_path = str(Path(image_paths[0]).parent)

            initial_state = {
                "messages": [HumanMessage(content="Напиши подробный обзор статьи. [WRITE]")],
                "selected_paper_path": self._normalize_tool_path(article.local_tex_path or article.local_pdf_path),
                "paper_content": paper_content,
                "extracted_images_path": extracted_images_path,
            }
            result = graph.graph.invoke(
                initial_state,
                config={"configurable": {"thread_id": f"write-{article.arxiv_id}-{datetime.utcnow().timestamp()}"}},
            )
            written_review = result.get("written_review")
            if not written_review:
                raise ServiceUnavailableError("GraphMAS did not return written_review.")
            parts = self._split_review_sections(written_review)
            dto = ReviewDTO(
                id=uuid4(),
                article_id=article.id,
                summary=parts["summary"],
                methods=parts["methods"],
                results=parts["results"],
                criticism=parts["criticism"],
                application=parts["application"],
                verdict=parts["verdict"],
                full_text=written_review,
                created_at=datetime.utcnow(),
                updated_at=None,
            )
            return dto, {
                "parsed_content": result.get("paper_content") or paper_content,
                "selected_paper_path": self._normalize_tool_path(result.get("selected_paper_path")),
                "extracted_images_path": result.get("extracted_images_path"),
            }

        from uuid import uuid4

        return await asyncio.to_thread(_run)
