"""Search Config Model"""
# -*- coding: utf-8 -*-

from metacogitor.config.base_config_model import BaseConfigModel


class SearchConfig(BaseConfigModel):

    # Search type
    search_engine_type: Required[SearchEngineType] = SearchEngineType.SERPAPI_GOOGLE

    # SerpApi Config
    serpapi_api_key: Optional[str] = None

    # Serper Config
    serper_api_key: Optional[str] = None

    # Google Config
    google_api_key: Optional[str] = None
    google_cse_id: Optional[str] = None

    @validator("browser_type")
    def validate_browser(cls, v):
        # Browser validation
        return v
