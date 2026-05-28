from pydantic import BaseModel, Field


class HotNewsItem(BaseModel):
    date: str = Field(..., description="发布日期 YYYY-MM-DD")
    title: str = Field(..., description="文章标题")
    summary: str = Field(..., description="摘要")
    source: str = Field(..., description="来源")
    url: str = Field(..., description="原文链接")


class ProviderInfo(BaseModel):
    id: str
    label: str
    description: str


class HotNewsResponse(BaseModel):
    provider: str
    provider_label: str
    keywords: list[str]
    days: int
    items: list[HotNewsItem]
    total: int
