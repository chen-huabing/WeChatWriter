#自动编写微信公众号文章的应用

##根据关键词去调用第三方服务，获取7天内关于“高考、强基”的热点新闻；
调用天行数据api获取社会新闻热点
接口文档
https://www.tianapi.com/apiview/3#apiprice
密钥key
d0407d03aab14d5d3c9122b1948713bd

调用justoneapi的社交媒体跨平台搜索接口，获取指定关键词相关新闻
产品介绍
https://justoneapi.com/zh
接口文档
https://docs.justoneapi.com/zh/api/social-media/cross-platform-search-v1
接口地址
http://47.117.133.51:30015/api/search/v1
密钥key
AuojUrv1N1QS3BiT

deepseek
接口文档
https://api-docs.deepseek.com/zh-cn/
密钥key
sk-94556ba604ad4ed281cefafd552257e6
提示词
提供最近7天有关“高考、强基、大学”的热点新闻日期、标题、摘要、来源、原文链接，转成json结构化输出


火山引擎doubao-seed-2.0-mini模型
接口示例
curl https://ark.cn-beijing.volces.com/api/v3/responses \
-H "Authorization: Bearer ark-4e756ea8-d247-41be-b078-fde3ef2a0e14-8943d" \
-H 'Content-Type: application/json' \
-d '{
    "model": "doubao-seed-2-0-mini-260428",
    "input": [
        {
            "role": "user",
            "content": [
                {
                    "type": "input_image",
                    "image_url": "https://ark-project.tos-cn-beijing.volces.com/doc_image/ark_demo_img_1.png"
                },
                {
                    "type": "input_text",
                    "text": "你看见了什么？"
                }
            ]
        }
    ]
}'
密钥key
ark-4e756ea8-d247-41be-b078-fde3ef2a0e14-8943d






##热点新闻列表页
显示获取到的热点新闻列表，列表里包括日期、文章标题、摘要，来源、原文链接

##人工挑选热点；

##仿照以往公众号文章的文风，对热点内容重新编写文章；
调用coze智能体，以往文章事先上传到coze智能体的知识库

##对新文章内容进行公众号文章格式排版；
调用md2wechat服务

##自动发布到公众号。
调用微信API

#技术栈
前端：vue3
后端：python fastapi
数据库：MySQL/PostgreSQL