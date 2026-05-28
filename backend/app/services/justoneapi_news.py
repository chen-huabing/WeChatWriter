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


_JUSTONEAPI_ERRORS: dict[int, str] = {
    100: "Token 无效或已失效，请检查 backend/.env 中的 JUSTONEAPI_TOKEN",
    301: "采集失败，请稍后重试",
    302: "超出速率限制，请稍后重试",
    303: "超出每日调用配额",
    400: "请求参数错误",
    500: "服务端内部错误",
    600: "权限不足",
    601: "账户余额不足，请在 JustOneAPI 控制台充值",
}


def _raise_justoneapi_error(data: dict) -> None:
    code = data.get("code")
    try:
        code_int = int(code)
    except (TypeError, ValueError):
        code_int = None

    message = str(data.get("message", "")).strip()
    if code_int in _JUSTONEAPI_ERRORS:
        hint = _JUSTONEAPI_ERRORS[code_int]
        if code_int == 601:
            hint += "（https://justoneapi.com），或改用火山引擎/天行数据"
        raise ValueError(f"JustOneAPI 错误: {hint}")

    if message.upper() == "INSUFFICIENT BALANCE":
        raise ValueError(
            "JustOneAPI 错误: 账户余额不足，请在 https://justoneapi.com 控制台充值，"
            "或改用火山引擎/天行数据"
        )

    raise ValueError(f"JustOneAPI 错误: {message or data}")


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
                _raise_justoneapi_error(data)

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
