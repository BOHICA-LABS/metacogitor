"""Generates search queries for a given topic or question."""
# -*- coding: utf-8 -*-

from metacogitor.actions.action import Action
from metacogitor.utils.common import OutputParser


class GenerateSearchQueries(Action):
    """Generates search queries for a given topic or question."""

    def __init__(self, name: str = "GenerateSearchQueries", *args, **kwargs):
        """Initialize the GenerateSearchQueries action class.

        :param name: The name of the action, defaults to "GenerateSearchQueries"
        :type name: str, optional
        """

        super().__init__(name, *args, **kwargs)

    async def run(self, topic: str) -> list[dict]:
        """Runs the action to generate search queries.

        :param topic: The input text.
        :type topic: str
        :return: A list of dictionaries containing the search queries.
        :rtype: list[dict]
        """

        prompt = f"""
        Given the following topic or question:

        {topic}

        Your task is to generate a list of diverse and interconnected search queries related to the topic or question
        provided. These queries should be strategically structured to seek various facets of information, including
        viewpoints, factual data, alternative perspectives, and expert insights. Each query should be unique, singular
        in focus, and aim for objectivity and accuracy.

        The search queries should be formatted as python dictionaries within a list. Each dictionary should have two
        keys: "query" and "purpose". The "query" key should contain the search query, while the "purpose" key should
        explain the intent or information sought through that specific query. Here's an example:

        ```python
        [
            {{"query": "Foundational principles of TOGAF framework", "purpose": "Seeking core principles of TOGAF."}},
            {{"query": "Common challenges in implementing TOGAF methodology", "purpose": "Identifying potential obstacles in TOGAF implementation."}},
            {{"query": "Real-world case studies showcasing successful TOGAF adoption", "purpose": "Exploring practical examples of TOGAF success stories."}},
            {{"query": "Comparison between TOGAF and other enterprise architecture frameworks", "purpose": "Understanding how TOGAF compares to alternative frameworks."}},
            {{"query": "Evolution and updates in TOGAF framework over the years", "purpose": "Understanding how TOGAF has evolved and what updates have been made to the framework throughout its history."}}
        ]
        ```

        Remember, each search query should encapsulate the core ideas from the context and seek relevant information on
        the topic. You may creatively expand on ideas and concepts when necessary. If the context is too subjective or
        interpretative to create a query, respond with an error for the query and explain why in the purpose. Return
        only the Python code block with the list of dictionaries.
        """

        queries = await self._aask(prompt)

        return OutputParser.extract_struct(
            queries, list
        )  # OutputParser.parse_str(notes)  # OutputParser.extract_struct(notes, list)


# Example of usage:
if __name__ == "__main__":
    import asyncio

    async def main():
        action = GenerateSearchQueries()
        queries = await action.run("Benefits and drawbacks of solar energy")
        # print(queries)
        for q in queries:
            print(q["query"], "-", q["purpose"])

    asyncio.run(main())
