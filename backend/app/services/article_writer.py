import httpx

from app.config import settings
from app.schemas.news import HotNewsItem
from app.services.news_parser import extract_json

INSTRUCTIONS = (
    "你是教育类微信公众号作者「道哥」，擅长撰写竞赛、升学、强基、高考相关文章。"
    "请严格模仿用户提供的过往文章文风：口语化、有观点、结构清晰，"
    "常用「道哥」第一人称视角，适当分段，可使用「图片」占位描述配图位置。"
    "结合热点素材展开论述，不要简单复述摘要，要写出独到见解与可读性。"
    "只输出 JSON，不要 markdown 代码块或其它说明。格式："
    '{"title":"公众号文章标题","content":"正文，段落之间用\\n\\n分隔"}'
)


def _load_style_reference() -> str:
    path = settings.wechat_style_path
    if not path.is_file():
        raise ValueError(f"文风参考文件不存在: {path}")
    text = path.read_text(encoding="utf-8").strip()
    max_chars = settings.wechat_style_max_chars
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n（…后续范文已截断）"
    return text


def _build_prompt(source: HotNewsItem, style_samples: str) -> str:
    return (
        "【过往公众号文章文风参考（请模仿语气、结构与表达方式）】\n"
        f"{style_samples}\n\n"
        "【本次热点素材】\n"
        f"标题：{source.title}\n"
        f"日期：{source.date}\n"
        f"来源：{source.source}\n"
        f"摘要：{source.summary}\n"
        f"原文链接：{source.url or '无'}\n\n"
        "请基于以上热点素材，撰写一篇完整的微信公众号文章。"
        "标题要有吸引力；正文 800～1500 字，分多个自然段。"
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


def _parse_article_response(text: str) -> tuple[str, str]:
    parsed = extract_json(text)
    title = str(parsed.get("title", "")).strip()
    content = str(parsed.get("content", "")).strip()
    if not title or not content:
        raise ValueError("模型返回的文章缺少 title 或 content 字段")
    return title, content


async def compose_article(source_news: HotNewsItem) -> tuple[str, str]:
    if not settings.volcano_api_key:
        raise ValueError("未配置 VOLCANO_API_KEY，请在 backend/.env 中设置")

    style_samples = _load_style_reference()
    user_prompt = _build_prompt(source_news, style_samples)

    payload = {
        "model": settings.volcano_model,
        "instructions": INSTRUCTIONS,
        "input": [
            {
                "role": "user",
                "content": [{"type": "input_text", "text": user_prompt}],
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

    async with httpx.AsyncClient(timeout=300.0) as client:
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
    return _parse_article_response(content)
