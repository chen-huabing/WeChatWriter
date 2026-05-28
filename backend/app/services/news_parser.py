import json
import re
from typing import Any

from app.config import settings
from app.schemas.news import HotNewsItem


def build_user_prompt(
    keywords: list[str],
    days: int,
    *,
    supplement: str = "",
) -> str:
    kw = "、".join(keywords)
    min_n = settings.news_min_items
    max_n = settings.news_max_items
    base = (
        f"请整理最近{days}天内与「{kw}」相关的热点新闻。"
        f"【硬性要求】items 数组必须包含至少 {min_n} 条、最多 {max_n} 条新闻，"
        f"少于 {min_n} 条视为未完成任务。"
        "请针对每个关键词分别联网搜索，汇总去重后输出。"
        "每条须包含：date(YYYY-MM-DD)、title、summary(80-120字)、source、url。"
        "按 date 从新到旧排序。只输出 JSON，不要 markdown 或其它说明。格式："
        '{"items":[{"date":"YYYY-MM-DD","title":"...","summary":"...",'
        '"source":"...","url":"https://..."}]}'
    )
    if supplement:
        return f"{base}\n\n{supplement}"
    return base


def extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            raise ValueError("模型返回内容无法解析为 JSON") from None
        return json.loads(match.group())


def _pick_str(data: dict, *keys: str) -> str:
    for key in keys:
        val = data.get(key)
        if val is not None and str(val).strip():
            return str(val).strip()
    return ""


def normalize_items(raw_items: list[Any]) -> list[HotNewsItem]:
    result: list[HotNewsItem] = []
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        title = _pick_str(item, "title", "headline", "name")
        if not title:
            continue
        try:
            result.append(
                HotNewsItem(
                    date=_pick_str(item, "date", "pub_date", "publish_date", "time"),
                    title=title,
                    summary=_pick_str(item, "summary", "abstract", "desc", "description"),
                    source=_pick_str(item, "source", "media", "publisher", "from"),
                    url=_pick_str(item, "url", "link", "original_url", "source_url"),
                )
            )
        except Exception:
            continue
    return result


def parse_news_items(text: str) -> list[HotNewsItem]:
    parsed = extract_json(text)
    items = parsed.get("items", parsed if isinstance(parsed, list) else [])
    if not isinstance(items, list):
        raise ValueError("返回的 JSON 中缺少 items 数组")

    normalized = normalize_items(items)
    if not normalized:
        raise ValueError("未能从模型响应中解析出有效新闻条目")

    normalized.sort(key=lambda x: x.date, reverse=True)
    return normalized


def item_dedupe_key(item: HotNewsItem) -> str:
    if item.url:
        return item.url.strip().lower()
    return item.title.strip().lower()


def merge_news_items(*groups: list[HotNewsItem]) -> list[HotNewsItem]:
    seen: set[str] = set()
    merged: list[HotNewsItem] = []
    for group in groups:
        for item in group:
            key = item_dedupe_key(item)
            if key in seen:
                continue
            seen.add(key)
            merged.append(item)
    merged.sort(key=lambda x: x.date, reverse=True)
    return merged[: settings.news_max_items]
