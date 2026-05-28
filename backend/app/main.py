from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.news import router as news_router

app = FastAPI(
    title="WeChatWriter API",
    description="微信公众号文章自动编写 - 火山引擎热点新闻服务",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(news_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
