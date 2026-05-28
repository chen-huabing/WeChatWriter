import json
from pathlib import Path
from uuid import uuid4

from app.config import settings
from app.schemas.article import ComposedArticle
from app.schemas.news import HotNewsItem


def _articles_dir() -> Path:
    path = settings.articles_data_dir
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_article(
    *,
    source_news: HotNewsItem,
    title: str,
    content: str,
) -> ComposedArticle:
    from datetime import datetime, timezone

    article = ComposedArticle(
        id=uuid4().hex,
        created_at=datetime.now(timezone.utc).isoformat(),
        source_news=source_news,
        title=title.strip(),
        content=content.strip(),
    )
    path = _articles_dir() / f"{article.id}.json"
    path.write_text(
        json.dumps(article.model_dump(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return article


def get_article(article_id: str) -> ComposedArticle | None:
    path = _articles_dir() / f"{article_id}.json"
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return ComposedArticle.model_validate(data)
