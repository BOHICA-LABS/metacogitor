"""Provide configuration, singleton"""
# -*- coding: utf-8 -*-

import os

import openai
import yaml

from metacogitor.const import PROJECT_ROOT
from metacogitor.logs import logger
from metacogitor.tools import SearchEngineType, WebBrowserEngineType
from metacogitor.utils.singleton import Singleton


class NotConfiguredException(Exception):
    """Exception raised for errors in the configuration.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="The required configuration is not set"):
        self.message = message
        super().__init__(self.message)


class Config(metaclass=Singleton):
    """Config class

    Regular usage method:
    config = Config("config.yaml")
    secret_key = config.get_key("MY_SECRET_KEY")
    print("Secret key:", secret_key)

    Attributes:
        _instance (Config): Singleton instance
        key_yaml_file (str): Path to key.yaml
        default_yaml_file (str): Path to config.yaml
        _configs (dict): Configs
        global_proxy (str): Global proxy
        openai_api_key (str): OpenAI API Key
        anthropic_api_key (str): Anthropic API Key
        openai_api_base (str): OpenAI API Base
        openai_api_type (str): OpenAI API Type
        openai_api_version (str): OpenAI API Version
        openai_api_rpm (int): OpenAI API RPM
        openai_api_model (str): OpenAI API Model
        max_tokens_rsp (int): Max tokens response
        deployment_name (str): Deployment name
        deployment_id (str): Deployment ID
        claude_api_key (str): Claude API Key
        serpapi_api_key (str): SerpAPI API Key
        serper_api_key (str): Serper API Key
        google_api_key (str): Google API Key
        search_engine (SearchEngineType): Search engine type
        web_browser_engine (WebBrowserEngineType): Web browser engine type
        playwright_browser_type (str): Playwright browser type
        selenium_browser_type (str): Selenium browser type
        long_term_memory (bool): Long term memory
        max_budget (float): Max budget
        total_cost (float): Total cost
        puppeteer_config (str): Puppeteer config
        mmdc (str): MMDC
        calc_usage (bool): Calc usage
        model_for_researcher_summary (str): Model for researcher summary
        model_for_researcher_report (str): Model for researcher report
        mermaid_engine (str): Mermaid engine
        pyppeteer_executable_path (str): Pyppeteer executable path
        prompt_format (str): Prompt format
        jira_url (str): Jira URL
        jira_username (str): Jira username
        jira_api_token (str): Jira API token
    """

    _instance = None
    key_yaml_file = PROJECT_ROOT / "config/key.yaml"
    default_yaml_file = PROJECT_ROOT / "config/config.yaml"

    def __init__(self, yaml_file=default_yaml_file):
        self._configs = {}
        self._init_with_config_files_and_env(self._configs, yaml_file)
        logger.info("Config loading done.")
        self.global_proxy = self._get("GLOBAL_PROXY")
        self.openai_api_key = self._get("OPENAI_API_KEY", "")
        self.anthropic_api_key = self._get("Anthropic_API_KEY")
        if (not self.openai_api_key or "YOUR_API_KEY" == self.openai_api_key) and (
            not self.anthropic_api_key or "YOUR_API_KEY" == self.anthropic_api_key
        ):
            raise NotConfiguredException(
                "Set OPENAI_API_KEY or Anthropic_API_KEY first"
            )
        self.openai_api_base = self._get("OPENAI_API_BASE")
        openai_proxy = self._get("OPENAI_PROXY") or self.global_proxy
        if openai_proxy:
            openai.proxy = openai_proxy
            openai.api_base = self.openai_api_base
        self.openai_api_type = self._get("OPENAI_API_TYPE")
        self.openai_api_version = self._get("OPENAI_API_VERSION")
        self.openai_api_rpm = self._get("RPM", 3)
        self.openai_api_model = self._get("OPENAI_API_MODEL", "gpt-4")
        self.max_tokens_rsp = self._get("MAX_TOKENS", 2048)
        self.deployment_name = self._get("DEPLOYMENT_NAME")
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
        self.mermaid_engine = self._get("MERMAID_ENGINE", "nodejs")
        self.pyppeteer_executable_path = self._get("PYPPETEER_EXECUTABLE_PATH", "")

        self.prompt_format = self._get("PROMPT_FORMAT", "markdown")

        self.jira_url = self._get("JIRA_URL", "")
        self.jira_username = self._get("JIRA_USERNAME", "")
        self.jira_api_token = self._get(
            "JIRA_API_TOKEN",
            "",
        )

    def _init_with_config_files_and_env(self, configs: dict, yaml_file):
        """Load from config/key.yaml, config/config.yaml, and env in decreasing order of priority"""
        configs.update(os.environ)

        for _yaml_file in [yaml_file, self.key_yaml_file]:
            if not _yaml_file.exists():
                continue

            # Load local YAML file
            with open(_yaml_file, "r", encoding="utf-8") as file:
                yaml_data = yaml.safe_load(file)
                if not yaml_data:
                    continue
                os.environ.update(
                    {k: v for k, v in yaml_data.items() if isinstance(v, str)}
                )
                configs.update(yaml_data)

    def _get(self, *args, **kwargs):
        return self._configs.get(*args, **kwargs)

    def get(self, key, *args, **kwargs):
        """Search for a value in config/key.yaml, config/config.yaml, and env; raise an error if not found"""
        value = self._get(key, *args, **kwargs)
        if value is None:
            raise ValueError(
                f"Key '{key}' not found in environment variables or in the YAML file"
            )
        return value


CONFIG = Config()
