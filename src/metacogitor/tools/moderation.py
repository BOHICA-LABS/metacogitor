"""Moderation tool for Metacogitor."""
# -*- coding: utf-8 -*-

from typing import Union

from metacogitor.llm import LLM


class Moderation:
    """Moderation tool for Metacogitor.

    Attributes:
        llm (LLM): The LLM instance.
    """

    def __init__(self):
        """Initialize the moderation tool.

        :param llm: The LLM instance.
        :type llm: LLM
        """
        self.llm = LLM()

    def moderation(self, content: Union[str, list[str]]):
        """Moderate the given content.

        :param content: The content to moderate.
        :type content: Union[str, list[str]]
        :return: The moderation results.
        :rtype: list[bool]
        """

        resp = []
        if content:
            moderation_results = self.llm.moderation(content=content)
            results = moderation_results.results
            for item in results:
                resp.append(item.flagged)

        return resp

    async def amoderation(self, content: Union[str, list[str]]):
        """Moderate the given content.

        :param content: The content to moderate.
        :type content: Union[str, list[str]]
        :return: The moderation results.
        :rtype: list[bool]
        """

        resp = []
        if content:
            moderation_results = await self.llm.amoderation(content=content)
            results = moderation_results.results
            for item in results:
                resp.append(item.flagged)

        return resp


if __name__ == "__main__":
    moderation = Moderation()
    print(
        moderation.moderation(
            content=[
                "I will kill you",
                "The weather is really nice today",
                "I want to hit you",
            ]
        )
    )
