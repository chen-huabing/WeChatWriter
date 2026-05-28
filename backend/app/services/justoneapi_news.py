import httpx

from app.config import settings
from app.schemas.news import HotNewsItem
from app.services.news_parser import (
    filter_by_days,
    format_date_from_timestamp,
    merge_news_items,
    strip_html,
)


def _parse_justone_item(raw: dict) -> HotNewsItem | None:
    title = str(raw.get("title", "")).strip()
    if not title:
        return None

    author = raw.get("author") or {}
    source = str(raw.get("sourceName", "")).strip()
    if not source and isinstance(author, dict):
        source = str(author.get("nickname", "")).strip()
    if not source:
        source = "JustOneAPI"

    content = strip_html(str(raw.get("content", "")))
    summary = content[:120] if content else title[:120]

    return HotNewsItem(
        date=format_date_from_timestamp(raw.get("createTime")),
        title=title,
        summary=summary,
        source=source,
        url=str(raw.get("url", "")).strip(),
    )


async def fetch_hot_news(keywords: list[str], days: int = 7) -> list[HotNewsItem]:
    if not settings.justoneapi_token:
        raise ValueError("未配置 JUSTONEAPI_TOKEN，请在 backend/.env 中设置")

    from datetime import datetime, timedelta

    end = datetime.now()
    start = end - timedelta(days=days)
    keyword = " ".join(keywords)

    params: dict = {
        "token": settings.justoneapi_token,
        "keyword": keyword,
        "source": "NEWS",
        "start": start.strftime("%Y-%m-%d %H:%M:%S"),
        "end": end.strftime("%Y-%m-%d %H:%M:%S"),
    }

    batches: list[list[HotNewsItem]] = []
    base = settings.justoneapi_base_url.rstrip("/")

    async with httpx.AsyncClient(timeout=120.0) as client:
        for _ in range(3):
            resp = await client.get(f"{base}/api/search/v1", params=params)
            resp.raise_for_status()
            data = resp.json()

            code = data.get("code")
            if code not in (0, "0"):
                raise ValueError(f"JustOneAPI 错误: {data.get('message', data)}")

            payload = data.get("data") or {}
            raw_list = payload.get("list") or []
            items: list[HotNewsItem] = []
            for raw in raw_list:
                if not isinstance(raw, dict):
                    continue
                item = _parse_justone_item(raw)
                if item:
                    items.append(item)
            batches.append(items)

            next_cursor = payload.get("nextCursor")
            if not next_cursor or len(merge_news_items(*batches)) >= settings.news_max_items:
                break
            params = {
                "token": settings.justoneapi_token,
                "nextCursor": next_cursor,
            }

    merged = merge_news_items(*batches)
    filtered = filter_by_days(merged, days)
    if not filtered:
        raise ValueError("JustOneAPI 未返回符合条件的新闻")
    return filtered
