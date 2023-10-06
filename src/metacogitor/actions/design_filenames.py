"""DesignFilenames action module."""
# -*- coding: utf-8 -*-

from metacogitor.actions import Action
from metacogitor.logs import logger

PROMPT = """You are an AI developer, trying to write a program that generates code for users based on their intentions.
When given their intentions, provide a complete and exhaustive list of file paths needed to write the program for the user.
Only list the file paths you will write and return them as a Python string list.
Do not add any other explanations, just return a Python string list."""


class DesignFilenames(Action):
    """DesignFilenames action class."""

    def __init__(self, name, context=None, llm=None):
        """Initialize the DesignFilenames action.

        :param name: The name of the action.
        :param context: The context of the action.
        :param llm: The language model to use for the action.
        """
        super().__init__(name, context, llm)
        self.desc = (
            "Based on the PRD, consider system design, and carry out the basic design of the corresponding "
            "APIs, data structures, and database tables. Please give your design, feedback clearly and in detail."
        )

    async def run(self, prd):
        """Run the DesignFilenames action.

        :param prd: The Product Requirement Document (PRD).
        :return: The design filenames.
        """
        prompt = f"The following is the Product Requirement Document (PRD):\n\n{prd}\n\n{PROMPT}"
        design_filenames = await self._aask(prompt)
        logger.debug(prompt)
        logger.debug(design_filenames)
        return design_filenames
