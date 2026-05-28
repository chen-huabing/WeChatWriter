# WeChatWriter

自动编写微信公众号文章的应用。当前已实现：通过火山引擎 Doubao 模型按关键词获取热点新闻，并在前端展示列表页。

## 项目结构

```
backend/     FastAPI + 火山引擎 Ark Responses API
frontend/    Vue 3 + Vite
doc/         产品需求文档
```

## 快速开始

### 1. 后端

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env          # 填入 VOLCANO_API_KEY
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API 文档：http://127.0.0.1:8000/docs

热点新闻接口：`GET /api/news/hot?provider=volcano&keywords=高考,强基,大学&days=7`

`provider` 可选：`volcano`（火山引擎）、`tianapi`（天行数据）、`justoneapi`

### 2. 前端

```bash
cd frontend
npm install
npm run dev
```

浏览器打开 http://localhost:5173 ，输入关键词后点击「获取热点」。

## 环境变量

| 变量 | 说明 |
|------|------|
| `VOLCANO_API_KEY` | 火山方舟 API Key（必填） |
| `VOLCANO_BASE_URL` | 默认 `https://ark.cn-beijing.volces.com/api/v3` |
| `VOLCANO_MODEL` | 默认 `doubao-seed-2-0-mini-260428` |
| `TIANAPI_API_KEY` | 天行数据 API Key |
| `JUSTONEAPI_TOKEN` | JustOneAPI 访问令牌 |
| `JUSTONEAPI_BASE_URL` | 默认 `http://47.117.133.51:30015` |

## 说明

热点内容由火山引擎 `doubao-seed-2.0-mini` 根据关键词整理生成，链接与日期供编辑参考；正式发布前请人工核实来源与原文。后续可接入天行数据、JustOneAPI 等作为真实数据源。
