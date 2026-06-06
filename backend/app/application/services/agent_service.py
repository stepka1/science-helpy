"""Сервис для работы с агентами анализа статей."""
import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional
from uuid import UUID, uuid4

from app.application.dto.evaluation_dto import EvaluationDTO
from app.application.dto.review_dto import ReviewDTO
from app.infrastructure.config.settings import settings
from app.shared.exceptions.base import ServiceUnavailableError

AGENTS_ROOT = Path(settings.PROJECT_ROOT) / "agents_system"
if str(AGENTS_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENTS_ROOT))


class AgentService:
    """Адаптер между backend и существующей системой агентов."""

    def __init__(self) -> None:
        self.describe_agent: Optional[Any] = None
        self.eval_agent: Optional[Any] = None
        self.writer_agent: Optional[Any] = None

        if settings.OPENROUTER_API_KEY:
            os.environ.setdefault("OPENROUTER_API_KEY", settings.OPENROUTER_API_KEY)
            os.environ.setdefault("OPENROUTER_BASE_URL", settings.OPENROUTER_BASE_URL)
            if settings.TAVILY_API_KEY:
                os.environ.setdefault("TAVILY_API_KEY", settings.TAVILY_API_KEY)

            from agents.describe_agent import DescribeAgent  # type: ignore
            from agents.review_agent import EvalAgent  # type: ignore
            from agents.writer_agent import WriterAgent  # type: ignore

            self.describe_agent = DescribeAgent()
            self.eval_agent = EvalAgent()
            self.writer_agent = WriterAgent()

    @staticmethod
    def _compose_payload(article_content: str, image_descriptions: List[str]) -> str:
        parts: List[str] = []
        if image_descriptions:
            parts.append("=== ОПИСАНИЯ ИЗОБРАЖЕНИЙ ===\n" + "\n\n".join(image_descriptions))
        parts.append("=== ТЕКСТ СТАТЬИ ===\n" + article_content)
        return "\n\n".join(parts)

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
        sections = {
            "summary": "",
            "methods": "",
            "results": "",
            "criticism": "",
            "application": "",
            "verdict": "",
        }
        current = "summary"
        buckets = {key: [] for key in sections}

        for raw_line in full_text.replace("\r\n", "\n").split("\n"):
            line = raw_line.strip()
            if line.startswith("#"):
                current = headings.get(line.lstrip("#").strip().lower(), current)
                continue
            buckets[current].append(raw_line)

        for key, lines in buckets.items():
            text = "\n".join(lines).strip()
            sections[key] = text

        if not sections["summary"]:
            sections["summary"] = full_text.strip()
        if not sections["verdict"]:
            sections["verdict"] = sections["summary"]
        return sections

    @staticmethod
    def _require_agent(agent: Optional[Any], agent_name: str) -> Any:
        if agent is None:
            raise ServiceUnavailableError(
                f"{agent_name} is unavailable. Configure OPENROUTER_API_KEY and rebuild the backend."
            )
        return agent

    async def describe_images(self, image_paths: List[str]) -> List[str]:
        """Описать изображения из статьи."""
        if not image_paths:
            return []
        describe_agent = self._require_agent(self.describe_agent, "DescribeAgent")

        async def _describe(path: str) -> str:
            try:
                return await asyncio.to_thread(describe_agent.run, path)
            except Exception as exc:
                raise ServiceUnavailableError(f"DescribeAgent failed: {type(exc).__name__}: {exc}") from exc

        return await asyncio.gather(*[_describe(path) for path in image_paths])

    async def evaluate_article(
        self,
        article_id: UUID,
        article_content: str,
        image_descriptions: List[str],
    ) -> EvaluationDTO:
        """Оценить статью по структурированной схеме."""
        payload = self._compose_payload(article_content, image_descriptions)
        eval_agent = self._require_agent(self.eval_agent, "EvalAgent")
        try:
            result = await asyncio.to_thread(eval_agent.evaluate, payload)
        except Exception as exc:
            raise ServiceUnavailableError(f"EvalAgent failed: {type(exc).__name__}: {exc}") from exc
        if not isinstance(result, dict) or "scores" not in result:
            raise ServiceUnavailableError("EvalAgent returned an invalid response.")

        scores = result.get("scores") or {}
        category = result.get("nlp_category", "Unknown")
        if isinstance(result.get("is_relevant"), bool):
            suffix = "relevant" if result["is_relevant"] else "not relevant"
            category = f"{category} ({suffix})"

        return EvaluationDTO(
            id=uuid4(),
            article_id=article_id,
            category=category,
            relevance=result.get("one_sentence_summary") or result.get("reasoning") or "Оценка сгенерирована.",
            novelty_score=max(1, min(5, int(scores.get("novelty", 3)))),
            methodology_score=max(1, min(5, int(scores.get("rigor", 3)))),
            impact_score=max(1, min(5, int(scores.get("impact", 3)))),
            overall_score=max(1, min(5, int(scores.get("overall", 3)))),
            pros=result.get("pros") or [],
            cons=result.get("cons") or [],
            justification=result.get("reasoning") or "",
            created_at=datetime.utcnow(),
            updated_at=None,
        )

    async def write_review(
        self,
        article_id: UUID,
        article_content: str,
        image_descriptions: List[str],
    ) -> ReviewDTO:
        """Написать обзор статьи на русском языке."""
        payload = self._compose_payload(article_content, image_descriptions)
        writer_agent = self._require_agent(self.writer_agent, "WriterAgent")
        try:
            full_text = await asyncio.to_thread(writer_agent.run, payload)
        except Exception as exc:
            raise ServiceUnavailableError(f"WriterAgent failed: {type(exc).__name__}: {exc}") from exc
        if not isinstance(full_text, str) or not full_text.strip():
            raise ServiceUnavailableError("WriterAgent returned an empty response.")
        parts = self._split_review_sections(full_text)

        return ReviewDTO(
            id=uuid4(),
            article_id=article_id,
            summary=parts["summary"],
            methods=parts["methods"],
            results=parts["results"],
            criticism=parts["criticism"],
            application=parts["application"],
            verdict=parts["verdict"],
            full_text=full_text,
            created_at=datetime.utcnow(),
            updated_at=None,
        )
