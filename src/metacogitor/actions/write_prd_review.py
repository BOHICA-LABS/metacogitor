"""WritePRDReview action module."""
# -*- coding: utf-8 -*-

from metacogitor.actions.action import Action


class WritePRDReview(Action):
    """Write PRD Review action."""

    def __init__(self, name, context=None, llm=None):
        """Initialize the write PRD Review handler.

        :param name: The name of the action.
        :type name: str
        :param context: The context for the action.
        :type context: str
        :param llm: The language model to use for the action.
        :type llm: LanguageModel
        """

        super().__init__(name, context, llm)
        self.prd = None
        self.desc = "Based on the PRD, conduct a PRD Review, providing clear and detailed feedback"
        self.prd_review_prompt_template = """
        Given the following Product Requirement Document (PRD):
        {prd}

        As a project manager, please review it and provide your feedback and suggestions.
        """

    async def run(self, prd):
        """Write PRD Review for the given PRD.

        :param prd: The PRD to write PRD Review for.
        :type prd: str
        :return: The PRD Review.
        :rtype: str
        """
        self.prd = prd
        prompt = self.prd_review_prompt_template.format(prd=self.prd)
        review = await self._aask(prompt)
        return review
