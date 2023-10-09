"""GPT Config Model"""
# -*- coding: utf-8 -*-

from metacogitor.config import BaseConfigModel
from metacogitor.exceptions import NotConfiguredException
from metacogitor.logs import logger
from pydantic import validator, root_validator
from typing import List, Optional


__ALL__ = ["GPTConfig"]


class GPTConfig(BaseConfigModel):
    """GPT Config Model

    Attributes:
        openai_api_key (str): OpenAI API Key
        openai_api_base (str): OpenAI API Base
        openai_api_type (str): OpenAI API Type
        openai_api_version (str): OpenAI API Version
        openai_api_rpm (int): OpenAI API RPM
        openai_api_model (str): OpenAI API Model
        anthropic_api_key (str): Anthropic API Key
        claude_api_key (str): Claude API Key
    """

    # OpenAI API Config
    openai_api_key: Optional[str] = None
    openai_api_base: Optional[str] = None
    openai_api_type: Optional[str] = None
    openai_api_version: Optional[str] = None
    openai_api_rpm: Optional[int] = None
    openai_api_model: Optional[str] = None

    # Anthropic API Config
    anthropic_api_key: Optional[str] = None
    claude_api_key: Optional[str] = anthropic_api_key  # alias for anthropic_api_key

    @root_validator
    def _check_gpt_fields_set(cls, values):
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
