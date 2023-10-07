"""Write tutorial action class."""
# _*_ coding: utf-8 _*_

from typing import Dict

from metacogitor.actions import Action
from metacogitor.prompts.tutorial_assistant import DIRECTORY_PROMPT, CONTENT_PROMPT
from metacogitor.utils.common import OutputParser


class WriteDirectory(Action):
    """Action class for writing tutorial directories."""

    def __init__(self, name: str = "", language: str = "English", *args, **kwargs):
        """Initialize the write directory handler.

        :param name: The name of the action.
        :type name: str
        :param language: The language to output, default is "English".
        :type language: str
        """
        super().__init__(name, *args, **kwargs)
        self.language = language

    async def run(self, topic: str, *args, **kwargs) -> Dict:
        """Execute the action to generate a tutorial directory according to the topic.

        :param topic: The tutorial topic.
        :type topic: str
        :return: The tutorial directory information, including {"title": "xxx", "directory": [{"dir 1": ["sub dir 1", "sub dir 2"]}]}.
        :rtype: dict
        """

        prompt = DIRECTORY_PROMPT.format(topic=topic, language=self.language)
        resp = await self._aask(prompt=prompt)
        return OutputParser.extract_struct(resp, dict)


class WriteContent(Action):
    """Action class for writing tutorial content."""

    def __init__(
        self,
        name: str = "",
        directory: str = "",
        language: str = "English",
        *args,
        **kwargs
    ):
        """Initialize the write content handler.

        :param name: The name of the action.
        :param directory: The content to write.
        :param language: The language to output, default is "English".
        """

        super().__init__(name, *args, **kwargs)
        self.language = language
        self.directory = directory

    async def run(self, topic: str, *args, **kwargs) -> str:
        """Execute the action to write document content according to the directory and topic.

        :param topic: The tutorial topic.
        :type topic: str
        :return: The written tutorial content.
        :rtype: str
        """

        prompt = CONTENT_PROMPT.format(
            topic=topic, language=self.language, directory=self.directory
        )
        return await self._aask(prompt=prompt)
