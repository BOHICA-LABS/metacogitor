"""Prepare for an interview."""
# -*- coding: utf-8 -*-

from metacogitor.actions import Action

PROMPT_TEMPLATE = """
# Context
{context}

## Format example
---
Q1: question 1 here
References:
  - point 1
  - point 2

Q2: question 2 here...
---

-----
Role: You are an interviewer of our company who is well-knonwn in frontend or backend develop;
Requirement: Provide a list of questions for the interviewer to ask the interviewee, by reading the resume of the interviewee in the context.
Attention: Provide as markdown block as the format above, at least 10 questions.
"""

# prepare for a interview


class PrepareInterview(Action):
    """Prepare for an interview."""

    def __init__(self, name, context=None, llm=None):
        """Initialize the action.

        :param name: Name of the action.
        :param context: Context of the action.
        :param llm: Language model to use.
        """
        super().__init__(name, context, llm)

    async def run(self, context):
        """Run the action.

        :param context:
        :return:
        """
        prompt = PROMPT_TEMPLATE.format(context=context)
        question_list = await self._aask_v1(prompt)
        return question_list
