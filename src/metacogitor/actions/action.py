"""Action class"""
# -*- coding: utf-8 -*-

import re
from abc import ABC
from typing import Optional

from tenacity import retry, stop_after_attempt, wait_fixed

from metacogitor.actions.action_output import ActionOutput
from metacogitor.llm import LLM
from metacogitor.logs import logger
from metacogitor.utils.common import OutputParser
from metacogitor.utils.custom_decoder import CustomDecoder


class Action(ABC):
    """
    Action class

    Attributes:
        name (str): name of the action
        llm (LLM): LLM instance
        context (dict): context
        prefix (str): prefix
        profile (str): profile
        desc (str): description
        content (str): content
        instruct_content (ActionOutput): instruct content
    """

    def __init__(self, name: str = "", context=None, llm: LLM = None):
        self.name: str = name
        if llm is None:
            llm = LLM()
        self.llm = llm
        self.context = context
        self.prefix = ""
        self.profile = ""
        self.desc = ""
        self.content = ""
        self.instruct_content = None

    def set_prefix(self, prefix, profile):
        """
        Set prefix for later usage

        Args:
            prefix (str): prefix
            profile (str): profile
        """
        self.prefix = prefix
        self.profile = profile

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return self.__str__()

    async def _aask(self, prompt: str, system_msgs: Optional[list[str]] = None) -> str:
        """
        Append default prefix

        Args:
            prompt (str): prompt
            system_msgs (Optional[list[str]], optional): system messages. Defaults to None.
        """
        if not system_msgs:
            system_msgs = []
        system_msgs.append(self.prefix)
        return await self.llm.aask(prompt, system_msgs)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    async def _aask_v1(
        self,
        prompt: str,
        output_class_name: str,
        output_data_mapping: dict,
        system_msgs: Optional[list[str]] = None,
        format="markdown",  # compatible to original format
    ) -> ActionOutput:
        """
        Private aask v1 with retry

        Append default prefix

        Args:
            prompt (str): prompt
            output_class_name (str): output class name
            output_data_mapping (dict): output data mapping
            system_msgs (Optional[list[str]], optional): system messages. Defaults to None.
            format (str, optional): format. Defaults to "markdown".
        """
        if not system_msgs:
            system_msgs = []
        system_msgs.append(self.prefix)
        content = await self.llm.aask(prompt, system_msgs)
        logger.debug(content)
        output_class = ActionOutput.create_model_class(
            output_class_name, output_data_mapping
        )

        if format == "json":
            pattern = r"\[CONTENT\](\s*\{.*?\}\s*)\[/CONTENT\]"
            matches = re.findall(pattern, content, re.DOTALL)

            for match in matches:
                if match:
                    content = match
                    break

            parsed_data = CustomDecoder(strict=False).decode(content)

        else:  # using markdown parser
            parsed_data = OutputParser.parse_data_with_mapping(
                content, output_data_mapping
            )

        logger.debug(parsed_data)
        instruct_content = output_class(**parsed_data)
        return ActionOutput(content, instruct_content)

    async def run(self, *args, **kwargs):
        """
        Run action

        Args:
            *args: args
            **kwargs: kwargs

        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError("The run method should be implemented in a subclass.")
