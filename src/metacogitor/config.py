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

from metacogitor.const import PROJECT_ROOT
from metacogitor.logs import logger
from metacogitor.tools import SearchEngineType, WebBrowserEngineType
from metacogitor.utils.singleton import Singleton
from metacogitor.errors import NotConfiguredException


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
        self.global_proxy = self._get("GLOBAL_PROXY")
        self.openai_api_key = self._get("OPENAI_API_KEY")
        self.anthropic_api_key = self._get("Anthropic_API_KEY")
        if (not self.openai_api_key or "YOUR_API_KEY" == self.openai_api_key) and (
            not self.anthropic_api_key or "YOUR_API_KEY" == self.anthropic_api_key
        ):
            raise NotConfiguredException(
                "Set OPENAI_API_KEY or Anthropic_API_KEY first"
            )
        self.openai_api_base = self._get("OPENAI_API_BASE")
        if not self.openai_api_base or "YOUR_API_BASE" == self.openai_api_base:
            openai_proxy = self._get("OPENAI_PROXY") or self.global_proxy
            if openai_proxy:
                openai.proxy = openai_proxy
            else:
                logger.info("Set OPENAI_API_BASE in case of network issues")
        self.openai_api_type = self._get("OPENAI_API_TYPE")
        self.openai_api_version = self._get("OPENAI_API_VERSION")
        self.openai_api_rpm = self._get("RPM", 3)
        self.openai_api_model = self._get("OPENAI_API_MODEL", "gpt-4")
        self.max_tokens_rsp = self._get("MAX_TOKENS", 2048)
        self.deployment_id = self._get("DEPLOYMENT_ID")

        self.claude_api_key = self._get("Anthropic_API_KEY")
        self.serpapi_api_key = self._get("SERPAPI_API_KEY")
        self.serper_api_key = self._get("SERPER_API_KEY")
        self.google_api_key = self._get("GOOGLE_API_KEY")
        self.google_cse_id = self._get("GOOGLE_CSE_ID")
        self.search_engine = SearchEngineType(
            self._get("SEARCH_ENGINE", SearchEngineType.SERPAPI_GOOGLE)
        )
        self.web_browser_engine = WebBrowserEngineType(
            self._get("WEB_BROWSER_ENGINE", WebBrowserEngineType.PLAYWRIGHT)
        )
        self.playwright_browser_type = self._get("PLAYWRIGHT_BROWSER_TYPE", "chromium")
        self.selenium_browser_type = self._get("SELENIUM_BROWSER_TYPE", "chrome")

        self.long_term_memory = self._get("LONG_TERM_MEMORY", False)
        if self.long_term_memory:
            logger.warning("LONG_TERM_MEMORY is True")
        self.max_budget = self._get("MAX_BUDGET", 10.0)
        self.total_cost = 0.0

        self.puppeteer_config = self._get("PUPPETEER_CONFIG", "")
        self.mmdc = self._get("MMDC", "mmdc")
        self.calc_usage = self._get("CALC_USAGE", True)
        self.model_for_researcher_summary = self._get("MODEL_FOR_RESEARCHER_SUMMARY")
        self.model_for_researcher_report = self._get("MODEL_FOR_RESEARCHER_REPORT")

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


CONFIG = Config()
