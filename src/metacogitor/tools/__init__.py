"""This module contains the tools used by the metacogitor package."""
# -*- coding: utf-8 -*-

from enum import Enum


class SearchEngineType(Enum):
    """Enum for search engine types."""

    SERPAPI_GOOGLE = "serpapi"
    SERPER_GOOGLE = "serper"
    DIRECT_GOOGLE = "google"
    DUCK_DUCK_GO = "ddg"
    CUSTOM_ENGINE = "custom"


class WebBrowserEngineType(Enum):
    """Enum for web browser engine types."""

    PLAYWRIGHT = "playwright"
    SELENIUM = "selenium"
    CUSTOM = "custom"
