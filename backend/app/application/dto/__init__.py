"""DTO (Data Transfer Objects) для передачи данных между слоями."""
from app.application.dto.article_dto import ArticleDTO, ArticleSearchResultDTO
from app.application.dto.evaluation_dto import EvaluationDTO
from app.application.dto.review_dto import ReviewDTO

__all__ = [
    "ArticleDTO",
    "ArticleSearchResultDTO",
    "EvaluationDTO",
    "ReviewDTO"
]
