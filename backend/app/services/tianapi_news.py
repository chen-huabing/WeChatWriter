import httpx

from app.config import settings
from app.schemas.news import HotNewsItem
from app.services.news_parser import (
    filter_by_days,
    format_date_from_ctime,
    merge_news_items,
)


async def fetch_hot_news(keywords: list[str], days: int = 7) -> list[HotNewsItem]:
    if not settings.tianapi_api_key:
        raise ValueError("未配置 TIANAPI_API_KEY，请在 backend/.env 中设置")

    batches: list[list[HotNewsItem]] = []
    num = min(settings.news_max_items, 50)

    async with httpx.AsyncClient(timeout=60.0) as client:
        for keyword in keywords:
            resp = await client.get(
                settings.tianapi_social_url,
                params={
                    "key": settings.tianapi_api_key,
                    "num": num,
                    "word": keyword,
                    "form": 1,
                },
            )
            resp.raise_for_status()
            data = resp.json()

            if data.get("code") != 200:
                raise ValueError(f"天行数据 API 错误: {data.get('msg', data)}")

            result = data.get("result") or {}
            newslist = result.get("list") or result.get("newslist") or []
            items: list[HotNewsItem] = []
            for raw in newslist:
                if not isinstance(raw, dict):
                    continue
                title = str(raw.get("title", "")).strip()
                if not title:
                    continue
                items.append(
                    HotNewsItem(
                        date=format_date_from_ctime(str(raw.get("ctime", ""))),
                        title=title,
                        summary=str(raw.get("description", "")).strip(),
                        source=str(raw.get("source", "天行数据")).strip() or "天行数据",
                        url=str(raw.get("url", "")).strip(),
                    )
                )
            batches.append(items)

    merged = merge_news_items(*batches)
    filtered = filter_by_days(merged, days)
    if not filtered:
        raise ValueError("天行数据未返回符合条件的新闻")
    return filtered
