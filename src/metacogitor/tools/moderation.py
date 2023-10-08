"""Moderation tool for Metacogitor."""
# -*- coding: utf-8 -*-

from typing import Union

from metacogitor.llm import LLM


class Moderation:
    def __init__(self):
        self.llm = LLM()

    def moderation(self, content: Union[str, list[str]]):
        resp = []
        if content:
            moderation_results = self.llm.moderation(content=content)
            results = moderation_results.results
            for item in results:
                resp.append(item.flagged)

        return resp

    async def amoderation(self, content: Union[str, list[str]]):
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
