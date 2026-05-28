from pydantic import BaseModel, Field

from app.schemas.news import HotNewsItem


class ComposeArticleRequest(BaseModel):
    source_news: HotNewsItem = Field(..., description="作为素材的热点新闻")


class ComposedArticle(BaseModel):
    id: str
    created_at: str
    source_news: HotNewsItem
    title: str = Field(..., description="生成的公众号文章标题")
    content: str = Field(..., description="生成的公众号正文")
