from pydantic import BaseModel, Field


class HotNewsItem(BaseModel):
    date: str = Field(..., description="发布日期 YYYY-MM-DD")
    title: str = Field(..., description="文章标题")
    summary: str = Field(..., description="摘要")
    source: str = Field(..., description="来源")
    url: str = Field(..., description="原文链接")


class HotNewsRequest(BaseModel):
    keywords: list[str] = Field(
        default=["高考", "强基"],
        min_length=1,
        description="搜索关键词列表",
    )
    days: int = Field(default=7, ge=1, le=30, description="回溯天数")


class HotNewsResponse(BaseModel):
    keywords: list[str]
    days: int
    items: list[HotNewsItem]
    total: int
