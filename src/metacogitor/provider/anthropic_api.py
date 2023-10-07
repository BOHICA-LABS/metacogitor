"""Anthropic API provider for Metacogitor."""
# -*- coding: utf-8 -*-

import anthropic
from anthropic import Anthropic

from metacogitor.config import CONFIG


class Claude2:
    """Anthropic API provider for Metacogitor."""

    def ask(self, prompt):
        """Ask a question to the Claude-2 model.

        :param prompt: The prompt to ask.
        :type prompt: str
        :return: The response from the model.
        :rtype: str
        """

        client = Anthropic(api_key=CONFIG.claude_api_key)

        res = client.completions.create(
            model="claude-2",
            prompt=f"{anthropic.HUMAN_PROMPT} {prompt} {anthropic.AI_PROMPT}",
            max_tokens_to_sample=1000,
        )
        return res.completion

    async def aask(self, prompt):
        """Ask a question to the Claude-2 model.

        :param prompt: The prompt to ask.
        :type prompt: str
        :return: The response from the model.
        :rtype: str
        """

        client = Anthropic(api_key=CONFIG.claude_api_key)

        res = client.completions.create(
            model="claude-2",
            prompt=f"{anthropic.HUMAN_PROMPT} {prompt} {anthropic.AI_PROMPT}",
            max_tokens_to_sample=1000,
        )
        return res.completion
