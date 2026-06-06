"""Use Cases приложения."""
from app.application.use_cases.search_articles import SearchArticlesUseCase
from app.application.use_cases.download_article import DownloadArticleUseCase
from app.application.use_cases.parse_article import ParseArticleUseCase
from app.application.use_cases.evaluate_article import EvaluateArticleUseCase
from app.application.use_cases.write_review import WriteReviewUseCase

__all__ = [
    "SearchArticlesUseCase",
    "DownloadArticleUseCase",
    "ParseArticleUseCase",
    "EvaluateArticleUseCase",
    "WriteReviewUseCase"
]
