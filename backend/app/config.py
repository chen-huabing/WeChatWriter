from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    volcano_api_key: str = ""
    volcano_base_url: str = "https://ark.cn-beijing.volces.com/api/v3"
    volcano_model: str = "doubao-seed-2-0-mini-260428"
    volcano_web_search_max_keyword: int = 3
    volcano_max_output_tokens: int = 8192

    tianapi_api_key: str = ""
    tianapi_social_url: str = "https://apis.tianapi.com/social/index"

    justoneapi_token: str = ""
    justoneapi_base_url: str = "http://47.117.133.51:30015"

    news_min_items: int = 8
    news_max_items: int = 15
    news_fetch_max_retries: int = 2


settings = Settings()
