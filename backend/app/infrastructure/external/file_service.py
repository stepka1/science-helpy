"""Сервис-адаптер над tools из agents_system."""
import asyncio
import json
import sys
from pathlib import Path
from typing import List, Optional

from app.infrastructure.config.settings import settings
from app.shared.exceptions.base import ServiceUnavailableError

AGENTS_ROOT = Path(settings.PROJECT_ROOT) / "agents_system"
if str(AGENTS_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENTS_ROOT))

from agent_tools.tools import (  # type: ignore  # noqa: E402
    download_arxiv_paper,
    download_arxiv_tex,
    list_tex_images,
    parse_img_from_pdf,
    parse_pdf_file,
    parse_tex_file,
)


class FileService:
    """Тонкий адаптер backend над file tools из agents_system."""

    def __init__(
        self,
        downloads_dir: str = settings.DOWNLOADS_DIR,
        extracted_images_dir: str = settings.EXTRACTED_IMAGES_DIR,
    ) -> None:
        self.downloads_dir = Path(downloads_dir)
        self.extracted_images_dir = Path(extracted_images_dir)

    @staticmethod
    def _normalize_tool_path(path_value: str) -> str:
        return (
            path_value.replace("\u2018", "'")
            .replace("\u2019", "'")
            .replace("\u201c", '"')
            .replace("\u201d", '"')
            .strip()
            .strip("'\"`")
            .strip()
        )

    async def download_pdf(self, url: str, arxiv_id: str) -> Optional[str]:
        """Скачать PDF статьи через agents_system."""

        def _download() -> Optional[str]:
            raw = download_arxiv_paper.invoke({"arxiv_id": arxiv_id})
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ServiceUnavailableError(f"download_arxiv_paper returned invalid JSON: {raw}") from exc
            if payload.get("status") != "success":
                raise ServiceUnavailableError(f"download_arxiv_paper failed for {arxiv_id}: {raw}")
            return payload.get("path")

        return await asyncio.to_thread(_download)

    async def download_tex(self, url: str, arxiv_id: str) -> Optional[str]:
        """Скачать TeX статьи через agents_system."""

        def _download() -> Optional[str]:
            raw = download_arxiv_tex.invoke({"arxiv_id": arxiv_id})
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                if "does not have TeX sources" in raw or "Network error" in raw or "Unexpected error" in raw:
                    return None
                raise ServiceUnavailableError(f"download_arxiv_tex returned invalid JSON: {raw}")
            if payload.get("status") != "success":
                return None
            return payload.get("directory")

        return await asyncio.to_thread(_download)

    async def parse_tex(self, file_path: str) -> Optional[str]:
        """Парсинг TeX через agents_system."""

        def _parse() -> Optional[str]:
            raw = parse_tex_file.invoke({"tex_path": self._normalize_tool_path(file_path)})
            if not raw or raw.startswith("Ошибка:"):
                return None
            return raw

        return await asyncio.to_thread(_parse)

    async def parse_pdf(self, file_path: str) -> Optional[str]:
        """Парсинг PDF через agents_system."""
        return await asyncio.to_thread(parse_pdf_file.invoke, {"pdf_path": file_path})

    async def extract_images_from_pdf(self, file_path: str) -> List[str]:
        """Извлечь изображения из PDF через agents_system."""

        def _extract() -> List[str]:
            raw = parse_img_from_pdf.invoke({"path_to_pdf": file_path})
            if raw.startswith("No images found"):
                return []
            if raw.startswith("An error occurred:") or raw.startswith("Error:"):
                raise ServiceUnavailableError(raw)
            return [line.strip() for line in raw.splitlines() if line.strip().startswith("/")]

        return await asyncio.to_thread(_extract)

    async def extract_images_from_tex(self, file_path: str) -> List[str]:
        """Найти изображения в TeX-исходниках через agents_system."""

        def _extract() -> List[str]:
            raw = list_tex_images.invoke({"tex_path": file_path})
            if "Изображения не найдены" in raw:
                return []
            if raw.startswith("Ошибка:"):
                raise ServiceUnavailableError(raw)
            return [
                line.replace("Full:", "").strip()
                for line in raw.splitlines()
                if line.startswith("Full:")
            ]

        return await asyncio.to_thread(_extract)
