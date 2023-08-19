# -*- coding: utf-8 -*-
"""
@Time    : 2023/8/18 15:35
@Author  : Joshua Magady
@File    : __init__.py
@Desc    : This defines the tools package.
"""


from enum import Enum


class SearchEngineType(Enum):
    """Enumeration for supported search engines."""

    SERPAPI_GOOGLE = "serpapi"
    """Use SerpApi to search Google."""

    SERPER_GOOGLE = "serper"
    """Use Serper to search Google."""

    DIRECT_GOOGLE = "google"
    """Search Google directly."""

    DUCK_DUCK_GO = "ddg"
    """Search DuckDuckGo."""

    CUSTOM_ENGINE = "custom"
    """Use a custom search engine."""


class WebBrowserEngineType(Enum):
    """Enumeration for supported web browser automation engines."""

    PLAYWRIGHT = "playwright"
    """Use Playwright for browser automation."""

    SELENIUM = "selenium"
    """Use Selenium for browser automation."""

    CUSTOM = "custom"
    """Use a custom browser automation engine."""
