"""Browser configuration module."""
# -*- coding: utf-8 -*-

from pydantic import validator
from typing import List, Optional
from metacogitor.config import BaseConfigModel


class BrowserConfig(BaseConfigModel):
    """Configuration for web browser automation.

    Attributes:
        browser_type (Optional[str]): Browser type.
        web_browser_engine_type (Optional[WebBrowserEngineType]): Browser engine type.
        web_browser_engine_path (Optional[str]): Path to browser engine executable.
        playwright_browser_type (Optional[str]): Playwright browser type.
        selenium_browser_type (Optional[str]): Selenium browser type.
        puppeteer_config (Optional[str]): Puppeteer config file path.

    """

    browser_type: Optional[str]

    # Browser Config
    web_browser_engine_type: Optional[WebBrowserEngineType] = None
    web_browser_engine_path: Optional[str] = None

    playwright_browser_type: Optional[str] = None  # chromium, firefox, webkit
    selenium_browser_type: Optional[str] = None  # chrome, firefox, edge, safari
    puppeteer_config: Optional[str] = None  # Path to puppeteer config file

    @validator("browser_type")
    def validate_browser(cls, v):
        # Browser validation
        return v
