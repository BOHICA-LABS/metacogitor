"""Detail Mining Action"""
# -*- coding: utf-8 -*-

from metacogitor.actions import Action, ActionOutput
from metacogitor.logs import logger

PROMPT_TEMPLATE = """
##TOPIC
{topic}

##RECORD
{record}

##Format example
{format_example}
-----

Task: Refer to the "##TOPIC" (discussion objectives) and "##RECORD" (discussion records) to further inquire about the details that interest you, within a word limit of 150 words.
Special Note 1: Your intention is solely to ask questions without endorsing or negating any individual's viewpoints.
Special Note 2: This output should only include the topic "##OUTPUT". Do not add, remove, or modify the topic. Begin the output with '##OUTPUT', followed by an immediate line break, and then proceed to provide the content in the specified format as outlined in the "##Format example" section.
Special Note 3: The output should be in the same language as the input.
"""
FORMAT_EXAMPLE = """

##

##OUTPUT
...(Please provide the specific details you would like to inquire about here.)

##

##
"""
OUTPUT_MAPPING = {
    "OUTPUT": (str, ...),
}


class DetailMining(Action):
    """Detail Mining Action

    This class allows LLM to further mine noteworthy details based on specific "##TOPIC"(discussion topic) and
    "##RECORD" (discussion records), thereby deepening the discussion.
    """

    def __init__(self, name="", context=None, llm=None):
        """Initialize the DetailMining action.

        :param name: The name of the action.
        :param context: The context of the action.
        :param llm: The language model to use for the action.
        """
        super().__init__(name, context, llm)

    async def run(self, topic, record) -> ActionOutput:
        """Run the DetailMining action.

        :param topic: The topic of the discussion.
        :param record: The record of the discussion.
        :return: The detail mining output.
        """
        prompt = PROMPT_TEMPLATE.format(
            topic=topic, record=record, format_example=FORMAT_EXAMPLE
        )
        rsp = await self._aask_v1(prompt, "detail_mining", OUTPUT_MAPPING)
        return rsp
