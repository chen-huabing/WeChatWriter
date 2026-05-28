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
    empty_keywords: list[str] = []
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
            code = data.get("code")

            if code == 250:
                empty_keywords.append(keyword)
                continue
            if code != 200:
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
            if items:
                batches.append(items)
            else:
                empty_keywords.append(keyword)

    merged = merge_news_items(*batches)
    filtered = filter_by_days(merged, days)
    if not filtered:
        if empty_keywords:
            raise ValueError(
                f"天行数据未找到与关键词相关的新闻：{'、'.join(empty_keywords)}"
            )
        raise ValueError("天行数据未返回符合条件的新闻")
    return filtered
