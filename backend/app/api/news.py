import httpx
from fastapi import APIRouter, HTTPException, Query

from app.schemas.news import HotNewsResponse
from app.services.volcano_news import fetch_hot_news

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/hot", response_model=HotNewsResponse)
async def get_hot_news(
    keywords: str = Query(
        default="高考,强基,大学",
        description="关键词，多个用英文或中文逗号分隔",
    ),
    days: int = Query(default=7, ge=1, le=30, description="回溯天数"),
) -> HotNewsResponse:
    keyword_list = [
        k.strip()
        for part in keywords.replace("，", ",").split(",")
        for k in part.split()
        if k.strip()
    ]
    if not keyword_list:
        raise HTTPException(status_code=400, detail="请至少提供一个关键词")

    try:
        items = await fetch_hot_news(keyword_list, days)
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=502,
            detail=f"火山引擎 API 请求失败: {e.response.text[:300]}",
        ) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取热点新闻失败: {e}") from e

    return HotNewsResponse(
        keywords=keyword_list,
        days=days,
        items=items,
        total=len(items),
    )
