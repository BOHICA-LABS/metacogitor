# -*- coding: utf-8 -*-
"""
@Time    : 2023/8/18 15:35
@Author  : Joshua Magady
@File    : config.py
@Desc    : This defines the Config Class.
"""

import os

import openai
import yaml

import os
import time
import yaml
from pathlib import Path


from pydantic import BaseModel, validator, root_validator
from typing import Dict, Any, Callable, Optional, List, Union, Type, Required
import hashlib

from metacogitor.const import PROJECT_ROOT
from metacogitor.logs import logger
from metacogitor.tools import SearchEngineType, WebBrowserEngineType
from metacogitor.utils.singleton import Singleton
from metacogitor.exceptions import NotConfiguredException
from metacogitor.utils import debounce


# TODO: add validator to set the search engine type based on the api key, if search engine api key is set, then use that
class ConfigKwargs(BaseModel):
    """
    This class defines the ConfigKwargs class.

    This class is used to define the kwargs for the Config class.

    Attributes:
    """

    def __validators__(cls) -> Dict[str, List[Callable]]:
        return {k: v for k, v in cls.__dict__.items() if k.startswith("_check_")}

    def api_keys(cls) -> List[str]:
        return [k for k, v in cls.__dict__.items() if k.endswith("_api_key")]

    def gpt_api_keys(cls) -> List[str]:
        return ["openai_api_key", "anthropic_api_key"]

    # Global Config
    global_proxy: Optional[str] = None  # !
    max_tokens_rsp: Required[int] = 2048  # !
    deployment_id: Optional[str] = None  # !
    max_budget = Required[float] = 10.00  # !
    total_cost = Required[float] = 0.00  # !
    long_term_memory: Optional[
        bool
    ] = False  # TODO: Log warning if this is set to True with valididator # !
    mmdc: Required[str] = "mmdc"  # !
    calc_usage: Required[bool] = True  # !
    model_for_researcher_summary: Optional[str]  # !
    model_for_researcher_report: Optional[str]  # !

    # OpenAI API Config
    openai_api_key: Optional[str] = None  # !
    openai_api_base: Optional[str] = None  # !
    openai_api_type: Optional[str] = None  # !
    openai_api_version: Optional[str] = None  # !
    openai_api_rpm: Optional[int] = None  # !
    openai_api_model: Optional[str] = None  # !

    # Anthropic API Config
    anthropic_api_key: Optional[str] = None  # !
    claude_api_key: Optional[
        str
    ] = self.anthropic_api_key  # alias for anthropic_api_key # !

    # Browser Config
    search_engine_type: Required[
        SearchEngineType
    ] = SearchEngineType.SERPAPI_GOOGLE  # !
    web_browser_engine_type: Optional[WebBrowserEngineType] = None  # !
    web_browser_engine_path: Optional[str] = None  # !

    # SerpApi Config
    serpapi_api_key: Optional[str] = None  # !

    # Serper Config
    serper_api_key: Optional[str] = None  # !

    # Google Config
    google_api_key: Optional[str] = None  # !
    google_cse_id: Optional[str] = None  # !

    # Browser Config
    playwright_browser_type: Optional[str] = None  # chromium, firefox, webkit  # !
    selenium_browser_type: Optional[str] = None  # chrome, firefox, edge, safari  # !
    puppeteer_config: Optional[str] = None  # Path to puppeteer config file    # !

    @root_validator
    def _check_gpt_fields_set(cls, values):  # !
        openai_api_key = values.get("openai_api_key")
        anthropic_api_key = values.get("anthropic_api_key")

        if not openai_api_key and not anthropic_api_key:
            error_msg = "Set OPENAI_API_KEY or Anthropic_API_KEY first"
            logger.error(error_msg)
            raise NotConfiguredException(error_msg, e)

        return values

    @root_validator
    def _check_openai_proxy(cls, values):  # !
        if values.get("openai_api_key") and not values.get("openai_api_base"):
            openai_proxy = values.get("openai_proxy") or values.get("global_proxy")
            if openai_proxy:
                openai.proxy = openai_proxy
            else:
                logger.info("Set OPENAI_API_BASE in case of network issues")

        return values


class Config(metaclass=Singleton):

    """Configuration manager for application settings.

    Loads config from YAML files and environment variables with precedence:

    1. config/key.yaml
    2. config/config.yaml
    3. Environment variables

    Usage:

        config = Config()
        key = config.get('MY_KEY')

    """

    _instance = None
    key_yaml_file = PROJECT_ROOT / "config/key.yaml"
    default_yaml_file = PROJECT_ROOT / "config/config.yaml"

    def __init__(self, yaml_file=default_yaml_file):
        """Initialize the configuration manager.

        Loads settings from YAML files and environment variables.

        Args:
            yaml_file: Path to default YAML config file.

        """

        self._configs = {}
        self._init_with_config_files_and_env(self._configs, yaml_file)
        logger.info("Config loading done.")
        self.global_proxy = self._get("GLOBAL_PROXY")  # !
        self.openai_api_key = self._get("OPENAI_API_KEY")  # !
        self.anthropic_api_key = self._get("Anthropic_API_KEY")  # !

        # !
        if (not self.openai_api_key or "YOUR_API_KEY" == self.openai_api_key) and (
            not self.anthropic_api_key or "YOUR_API_KEY" == self.anthropic_api_key
        ):
            raise NotConfiguredException(
                "Set OPENAI_API_KEY or Anthropic_API_KEY first"
            )
        # !!

        self.openai_api_base = self._get("OPENAI_API_BASE")  # !

        # !
        if not self.openai_api_base or "YOUR_API_BASE" == self.openai_api_base:
            openai_proxy = self._get("OPENAI_PROXY") or self.global_proxy
            if openai_proxy:
                openai.proxy = openai_proxy
            else:
                logger.info("Set OPENAI_API_BASE in case of network issues")
        # !!

        self.openai_api_type = self._get("OPENAI_API_TYPE")  # !
        self.openai_api_version = self._get("OPENAI_API_VERSION")  # !
        self.openai_api_rpm = self._get("RPM", 3)  # !
        self.openai_api_model = self._get("OPENAI_API_MODEL", "gpt-4")  # !
        self.max_tokens_rsp = self._get("MAX_TOKENS", 2048)  # !
        self.deployment_id = self._get("DEPLOYMENT_ID")  # !

        self.claude_api_key = self._get("Anthropic_API_KEY")  # !
        self.serpapi_api_key = self._get("SERPAPI_API_KEY")  # !
        self.serper_api_key = self._get("SERPER_API_KEY")  # !
        self.google_api_key = self._get("GOOGLE_API_KEY")  # !
        self.google_cse_id = self._get("GOOGLE_CSE_ID")  # !

        # ---
        self.search_engine = SearchEngineType(
            self._get("SEARCH_ENGINE", SearchEngineType.SERPAPI_GOOGLE)
        )
        self.web_browser_engine = WebBrowserEngineType(
            self._get("WEB_BROWSER_ENGINE", WebBrowserEngineType.PLAYWRIGHT)
        )
        # ---

        self.playwright_browser_type = self._get(
            "PLAYWRIGHT_BROWSER_TYPE", "chromium"
        )  # !
        self.selenium_browser_type = self._get("SELENIUM_BROWSER_TYPE", "chrome")  # !

        self.long_term_memory = self._get("LONG_TERM_MEMORY", False)  # !
        if self.long_term_memory:
            logger.warning("LONG_TERM_MEMORY is True")
        self.max_budget = self._get("MAX_BUDGET", 10.0)  # !
        self.total_cost = 0.0  # !

        self.puppeteer_config = self._get("PUPPETEER_CONFIG", "")  # !
        self.mmdc = self._get("MMDC", "mmdc")  # !
        self.calc_usage = self._get("CALC_USAGE", True)  # !
        self.model_for_researcher_summary = self._get(
            "MODEL_FOR_RESEARCHER_SUMMARY"
        )  # !
        self.model_for_researcher_report = self._get("MODEL_FOR_RESEARCHER_REPORT")  # !

    def _init_with_config_files_and_env(self, configs, yaml_file):
        """Load config from YAML files and environment variables. (Private Method)

        Args:
            configs (dict): Config dict to populate.
            yaml_file: YAML file to load.

        """
        configs.update(os.environ)

        for _yaml_file in [yaml_file, self.key_yaml_file]:
            if not _yaml_file.exists():
                continue

            # Load Local YAML config file
            with open(_yaml_file, "r", encoding="utf-8") as file:
                yaml_data = yaml.safe_load(file)
                if not yaml_data:
                    continue
                os.environ.update(
                    {k: v for k, v in yaml_data.items() if isinstance(v, str)}
                )
                configs.update(yaml_data)

    def _get(self, *args, **kwargs):
        """Get a config value (Private Method).

        Checks YAML files and environment variables.

        Args:
            key (str): Config key to get.
            default: Default value if key not found.

        Returns:
            Value for key if found, else default.

        """
        return self._configs.get(*args, **kwargs)

    def get(self, key, *args, **kwargs):
        """Get a config value.

        Gets the key from YAML files or environment variables.
        Raises error if not found.

        Args:
            key (str): Config key to get.
            default: Default value if key not found.

        Returns:
            Value for the given key.

        Raises:
            ValueError: If key not found.

        """
        value = self._get(key, *args, **kwargs)
        if value is None:
            raise ValueError(
                f"Key '{key}' not found in environment variables or in the YAML file"
            )
        return value

    def reload(self):
        """Reload the configuration from files and environment."""
        self._configs = {}
        self._init_with_config_files_and_env(self._configs, self.default_yaml_file)
        logger.info("Config reloaded.")


class Config2:
    def watchdog(self, interval=10):

        prev_mtimes = {
            self.default_yaml_file: self.default_yaml_file.stat().st_mtime,
            self.key_yaml_file: self.key_yaml_file.stat().st_mtime,
        }

        prev_env_hashes = {key: self._hash_env(key) for key in os.environ}

        reload = debounce(self.reload, seconds=60)

        while True:
            time.sleep(interval)

            changed_files = []
            changed_env = []

            for path, mtime in prev_mtimes.items():
                curr_mtime = path.stat().st_mtime
                if curr_mtime != mtime:
                    changed_files.append(path)
                    prev_mtimes[path] = curr_mtime

            for key, prev_hash in prev_env_hashes.items():
                curr_hash = self._hash_env(key)
                if curr_hash != prev_hash:
                    changed_env.append(key)
                    prev_env_hashes[key] = curr_hash

            if changed_files or changed_env:
                reload(keys=changed_files + changed_env)

    def _hash_env(self, key):
        value = os.environ.get(key)
        return hashlib.sha1(value.encode()).hexdigest() if value else None


# class Config3(BaseModel):

CONFIG = Config()
