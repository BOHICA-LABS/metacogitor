"""Design API Review Action"""
# -*- coding: utf-8 -*-

from metacogitor.actions.action import Action


class DesignReview(Action):
    """Design API Review Action"""

    def __init__(self, name, context=None, llm=None):
        """Initialize the Design API Review Action

        :param name: The name of the action
        :param context: The context of the action
        :param llm: The language model to use for the action
        """
        super().__init__(name, context, llm)

    async def run(self, prd, api_design):
        """Run the Design API Review Action

        :param prd: The Product Requirement Document (PRD)
        :param api_design: The API design
        :return: The API review
        """
        prompt = (
            f"Here is the Product Requirement Document (PRD):\n\n{prd}\n\nHere is the list of APIs designed "
            f"based on this PRD:\n\n{api_design}\n\nPlease review whether this API design meets the requirements"
            f" of the PRD, and whether it complies with good design practices."
        )

        api_review = await self._aask(prompt)
        return api_review
