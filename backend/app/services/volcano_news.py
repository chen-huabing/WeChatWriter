import httpx

from app.config import settings
from app.schemas.news import HotNewsItem
from app.services.news_parser import (
    build_user_prompt,
    merge_news_items,
    parse_news_items,
)

INSTRUCTIONS = (
    "你是专业的新闻资讯分析师。请使用联网搜索获取最新资讯。"
    f"每次任务必须输出不少于 {settings.news_min_items} 条、不超过 {settings.news_max_items} 条热点新闻。"
    "若单次搜索所得不足，必须更换关键词或平台继续搜索直至条数达标。"
    "仅输出与关键词高度相关、具有新闻价值的内容；来源名称需可识别；"
    "链接使用搜索到的真实原文链接；严格按 JSON 格式输出，不要输出 markdown 代码块或其他说明文字。"
)


def _extract_response_text(data: dict) -> str:
    texts: list[str] = []
    for block in data.get("output", []):
        if block.get("type") != "message":
            continue
        for part in block.get("content", []):
            if part.get("type") == "output_text" and part.get("text"):
                texts.append(part["text"])
    if not texts:
        raise ValueError("火山引擎响应中未找到文本输出")
    return texts[-1]


def _web_search_max_keyword(keywords: list[str]) -> int:
    return max(
        settings.volcano_web_search_max_keyword,
        min(len(keywords), 5),
    )


async def _request_news(
    client: httpx.AsyncClient,
    keywords: list[str],
    days: int,
    supplement: str = "",
) -> list[HotNewsItem]:
    payload = {
        "model": settings.volcano_model,
        "instructions": INSTRUCTIONS,
        "tools": [
            {
                "type": "web_search",
                "max_keyword": _web_search_max_keyword(keywords),
            }
        ],
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": build_user_prompt(keywords, days, supplement=supplement),
                    }
                ],
            }
        ],
        "text": {"format": {"type": "json_object"}},
        "thinking": {"type": "disabled"},
        "max_output_tokens": settings.volcano_max_output_tokens,
    }

    headers = {
        "Authorization": f"Bearer {settings.volcano_api_key}",
        "Content-Type": "application/json",
    }

    resp = await client.post(
        f"{settings.volcano_base_url.rstrip('/')}/responses",
        headers=headers,
        json=payload,
    )
    resp.raise_for_status()
    data = resp.json()

    if data.get("status") == "failed":
        raise ValueError(f"火山引擎请求失败: {data.get('error', data)}")

    content = _extract_response_text(data)
    return parse_news_items(content)


async def fetch_hot_news(keywords: list[str], days: int = 7) -> list[HotNewsItem]:
    if not settings.volcano_api_key:
        raise ValueError("未配置 VOLCANO_API_KEY，请在 backend/.env 中设置")

    min_items = settings.news_min_items
    batches: list[list[HotNewsItem]] = []

    async with httpx.AsyncClient(timeout=300.0) as client:
        batches.append(await _request_news(client, keywords, days))

        for attempt in range(settings.news_fetch_max_retries):
            merged = merge_news_items(*batches)
            if len(merged) >= min_items:
                return merged

            need = min_items - len(merged)
            titles = "、".join(i.title[:20] for i in merged[:5])
            supplement = (
                f"【补充任务】当前仅 {len(merged)} 条，还差至少 {need} 条。"
                f"请继续联网搜索其它相关热点（勿与已有重复）。"
                f"已有标题示例：{titles}。"
                f"请输出完整 JSON，items 总数达到 {min_items}～{settings.news_max_items} 条。"
            )
            batches.append(
                await _request_news(client, keywords, days, supplement=supplement)
            )

    merged = merge_news_items(*batches)
    if len(merged) < min_items:
        raise ValueError(
            f"模型仅返回 {len(merged)} 条新闻（要求至少 {min_items} 条），请稍后重试或调整关键词"
        )
    return merged
