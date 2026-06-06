"""Pydantic схемы для валидации запросов и ответов."""
from app.presentation.schemas.article_schemas import (
    SearchArticlesRequest,
    DownloadArticleRequest,
    ParseArticleRequest,
    ArticleResponse
)
from app.presentation.schemas.evaluation_schemas import (
    EvaluationResponse,
    EvaluateArticleRequest
)
from app.presentation.schemas.review_schemas import (
    ReviewResponse,
    WriteReviewRequest
)

__all__ = [
    "SearchArticlesRequest",
    "DownloadArticleRequest",
    "ParseArticleRequest",
    "ArticleResponse",
    "EvaluationResponse",
    "EvaluateArticleRequest",
    "ReviewResponse",
    "WriteReviewRequest"
]
