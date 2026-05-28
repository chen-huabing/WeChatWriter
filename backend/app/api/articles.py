import httpx
from fastapi import APIRouter, HTTPException

from app.schemas.article import ComposeArticleRequest, ComposedArticle
from app.services.article_store import get_article, save_article
from app.services.article_writer import compose_article

router = APIRouter(prefix="/api/articles", tags=["articles"])


@router.post("/compose", response_model=ComposedArticle)
async def compose_from_hot_news(body: ComposeArticleRequest) -> ComposedArticle:
    try:
        title, content = await compose_article(body.source_news)
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=502,
            detail=f"火山引擎 API 请求失败: {e.response.text[:300]}",
        ) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"撰写文章失败: {e}") from e

    return save_article(
        source_news=body.source_news,
        title=title,
        content=content,
    )


@router.get("/{article_id}", response_model=ComposedArticle)
async def read_article(article_id: str) -> ComposedArticle:
    article = get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    return article
