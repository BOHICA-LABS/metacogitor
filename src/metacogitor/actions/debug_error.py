"""DebugError action."""
# -*- coding: utf-8 -*-

import re

from metacogitor.logs import logger
from metacogitor.actions.action import Action
from metacogitor.utils.common import CodeParser

PROMPT_TEMPLATE = """
NOTICE
1. Role: You are a Development Engineer or QA engineer;
2. Task: You received this message from another Development Engineer or QA engineer who ran or tested your code.
Based on the message, first, figure out your own role, i.e. Engineer or QaEngineer,
then rewrite the development code or the test code based on your role, the error, and the summary, such that all bugs are fixed and the code performs well.
Attention: Use '##' to split sections, not '#', and '## <SECTION_NAME>' SHOULD WRITE BEFORE the test case or script and triple quotes.
The message is as follows:
{context}
---
Now you should start rewriting the code:
## file name of the code to rewrite: Write code with triple quoto. Do your best to implement THIS IN ONLY ONE FILE.
"""


class DebugError(Action):
    """DebugError action."""

    def __init__(self, name="DebugError", context=None, llm=None):
        """Initializes the DebugError action.

        :param name: The name of the action.
        :type name: str
        :param context: The context of the action.
        :type context: str
        :param llm: The language model to use for the action.
        :type llm: str
        """
        super().__init__(name, context, llm)

    # async def run(self, code, error):
    #     prompt = f"Here is a piece of Python code:\n\n{code}\n\nThe following error occurred during execution:" \
    #              f"\n\n{error}\n\nPlease try to fix the error in this code."
    #     fixed_code = await self._aask(prompt)
    #     return fixed_code

    async def run(self, context):
        """Runs the action to debug the error.

        :param context: The context of the action.
        :type context: str
        :return: The results of the action.
        :rtype: ActionOutput
        """
        if "PASS" in context:
            return "", "the original code works fine, no need to debug"

        file_name = re.search("## File To Rewrite:\s*(.+\\.py)", context).group(1)

        logger.info(f"Debug and rewrite {file_name}")

        prompt = PROMPT_TEMPLATE.format(context=context)

        rsp = await self._aask(prompt)

        code = CodeParser.parse_code(block="", text=rsp)

        return file_name, code
