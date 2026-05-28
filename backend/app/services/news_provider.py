from collections.abc import Awaitable, Callable

from app.schemas.news import HotNewsItem, ProviderInfo

FetchFn = Callable[[list[str], int], Awaitable[list[HotNewsItem]]]

PROVIDERS: dict[str, ProviderInfo] = {
    "volcano": ProviderInfo(
        id="volcano",
        label="火山引擎",
        description="Doubao 模型 + 联网搜索",
    ),
    "tianapi": ProviderInfo(
        id="tianapi",
        label="天行数据",
        description="社会新闻热点 API",
    ),
    "justoneapi": ProviderInfo(
        id="justoneapi",
        label="JustOneAPI",
        description="跨平台社交媒体搜索（新闻源）",
    ),
}

DEFAULT_PROVIDER = "volcano"


def list_providers() -> list[ProviderInfo]:
    return list(PROVIDERS.values())


def get_provider_label(provider: str) -> str:
    info = PROVIDERS.get(provider)
    if not info:
        raise ValueError(f"不支持的数据源: {provider}，可选: {', '.join(PROVIDERS)}")
    return info.label


async def fetch_hot_news(
    provider: str,
    keywords: list[str],
    days: int = 7,
) -> list[HotNewsItem]:
    provider = provider.strip().lower()
    if provider not in PROVIDERS:
        raise ValueError(f"不支持的数据源: {provider}，可选: {', '.join(PROVIDERS)}")

    if provider == "volcano":
        from app.services.volcano_news import fetch_hot_news as fetch_volcano

        return await fetch_volcano(keywords, days)
    if provider == "tianapi":
        from app.services.tianapi_news import fetch_hot_news as fetch_tianapi

        return await fetch_tianapi(keywords, days)
    from app.services.justoneapi_news import fetch_hot_news as fetch_justone

    return await fetch_justone(keywords, days)
