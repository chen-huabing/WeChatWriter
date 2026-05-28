import httpx
from fastapi import APIRouter, HTTPException, Query

from app.schemas.news import HotNewsResponse, ProviderInfo
from app.services.news_provider import (
    DEFAULT_PROVIDER,
    fetch_hot_news,
    get_provider_label,
    list_providers,
)

router = APIRouter(prefix="/api/news", tags=["news"])


def _parse_keywords(keywords: str) -> list[str]:
    return [
        k.strip()
        for part in keywords.replace("，", ",").split(",")
        for k in part.split()
        if k.strip()
    ]


@router.get("/providers", response_model=list[ProviderInfo])
async def get_providers() -> list[ProviderInfo]:
    return list_providers()


@router.get("/hot", response_model=HotNewsResponse)
async def get_hot_news(
    provider: str = Query(
        default=DEFAULT_PROVIDER,
        description="数据源：volcano | tianapi | justoneapi",
    ),
    keywords: str = Query(
        default="高考,强基,大学",
        description="关键词，多个用英文或中文逗号分隔",
    ),
    days: int = Query(default=7, ge=1, le=30, description="回溯天数"),
) -> HotNewsResponse:
    keyword_list = _parse_keywords(keywords)
    if not keyword_list:
        raise HTTPException(status_code=400, detail="请至少提供一个关键词")

    provider_id = provider.strip().lower()
    try:
        provider_label = get_provider_label(provider_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    try:
        items = await fetch_hot_news(provider_id, keyword_list, days)
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=502,
            detail=f"{provider_label} API 请求失败: {e.response.text[:300]}",
        ) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取热点新闻失败: {e}") from e

    return HotNewsResponse(
        provider=provider_id,
        provider_label=provider_label,
        keywords=keyword_list,
        days=days,
        items=items,
        total=len(items),
    )
