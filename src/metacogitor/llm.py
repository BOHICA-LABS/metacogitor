"""LLM: Large Language Model"""
# -*- coding: utf-8 -*-

from metacogitor.provider.anthropic_api import Claude2 as Claude
from metacogitor.provider.openai_api import OpenAIGPTAPI as LLM

DEFAULT_LLM = LLM()
CLAUDE_LLM = Claude()


async def ai_func(prompt):
    """QA with LLMs

    :param prompt: The prompt to ask the LLM.
    :type prompt: str
    :return: The answer from the LLM.
    :rtype: str
    """
    return await DEFAULT_LLM.aask(prompt)
