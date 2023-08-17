#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/8/14 23:04
@Author  : Joshua Magady
@File    : base_gpt_api.py
@Desc    : This is the base class for all GPT API providers
"""
from abc import abstractmethod
from typing import Optional

from metacogitor.logs import logger
from metacogitor.providers import BaseChatbot


__ALL__ = ["BaseGPTAPI"]


class BaseGPTAPI(BaseChatbot):
    """
    Abstract class for GPT-based chatbot using an API.
    This class requires all inheritors to provide a series of standard capabilities.
    """

    system_prompt = "You are a helpful assistant."

    def _user_msg(self, msg: str) -> dict[str, str]:
        """
        Create a user message dictionary.

        :param msg: User message content.
        :return: Dictionary containing user message.
        """
        return {"role": "user", "content": msg}

    def _assistant_msg(self, msg: str) -> dict[str, str]:
        """
        Create an assistant message dictionary.

        :param msg: Assistant message content.
        :return: Dictionary containing assistant message.
        """
        return {"role": "assistant", "content": msg}

    def _system_msg(self, msg: str) -> dict[str, str]:
        """
        Create a system message dictionary.

        :param msg: System message content.
        :return: Dictionary containing system message.
        """
        return {"role": "system", "content": msg}

    def _system_msgs(self, msgs: list[str]) -> list[dict[str, str]]:
        """
        Create a list of system message dictionaries.

        :param msgs: List of system message contents.
        :return: List of dictionaries containing system messages.
        """
        return [self._system_msg(msg) for msg in msgs]

    def _default_system_msg(self):
        """
        Create the default system message.

        :return: Dictionary containing the default system message.
        """
        return self._system_msg(self.system_prompt)

    def ask(self, msg: str) -> str:
        """
        Ask the GPT-based chatbot a question and receive an answer.

        :param msg: The input question.
        :return: The generated answer.
        """
        message = [self._default_system_msg(), self._user_msg(msg)]
        rsp = self.completion(message)
        logger.debug(message)
        return self.get_choice_text(rsp)

    async def aask(self, msg: str, system_msgs: Optional[list[str]] = None) -> str:
        """
        Asynchronously ask the GPT-based chatbot a question and receive an answer.

        :param msg: The input question.
        :param system_msgs: List of system messages.
        :return: The generated answer.
        """
        if system_msgs:
            message = self._system_msgs(system_msgs) + [self._user_msg(msg)]
        else:
            message = [self._default_system_msg(), self._user_msg(msg)]
        rsp = await self.acompletion_text(message, stream=True)
        logger.debug(message)
        return rsp

    def _extract_assistant_rsp(self, context):
        """
        Extract assistant responses from context.

        :param context: List of conversation context.
        :return: Extracted assistant responses as a concatenated string.
        """
        return "\n".join([i["content"] for i in context if i["role"] == "assistant"])

    def ask_batch(self, msgs: list) -> str:
        """
        Ask the GPT-based chatbot multiple questions and receive a series of answers.

        :param msgs: A list of input questions.
        :return: A series of generated answers as a concatenated string.
        """
        context = [self._default_system_msg()]
        for msg in msgs:
            umsg = self._user_msg(msg)
            context.append(umsg)
            rsp = self.completion(context)
            rsp_text = self.get_choice_text(rsp)
            context.append(self._assistant_msg(rsp_text))
        return self._extract_assistant_rsp(context)

    async def aask_batch(self, msgs: list) -> str:
        """
        Asynchronously ask the GPT-based chatbot multiple questions and receive a series of answers.

        :param msgs: A list of input questions.
        :return: A series of generated answers as a concatenated string.
        """
        context = []
        context = [self._default_system_msg()]
        for msg in msgs:
            umsg = self._user_msg(msg)
            context.append(umsg)
            rsp_text = await self.acompletion_text(context)
            context.append(self._assistant_msg(rsp_text))
        return self._extract_assistant_rsp(context)

    def ask_code(self, msgs: list[str]) -> str:
        """
        Ask the GPT-based chatbot multiple questions and receive a piece of code.

        :param msgs: A list of input questions.
        :return: A piece of generated code.
        """

        # TODO: No code segment filtering has been done here, and all results are actually displayed
        rsp_text = self.ask_batch(msgs)
        return rsp_text

    async def aask_code(self, msgs: list[str]) -> str:
        """
        Asynchronously ask the GPT-based chatbot multiple questions and receive a piece of code.

        :param msgs: A list of input questions.
        :return: A piece of generated code.
        """
        # TODO: No code segment filtering has been done here, and all results are actually displayed
        rsp_text = await self.aask_batch(msgs)
        return rsp_text

    @abstractmethod
    def completion(self, messages: list[dict]):
        """All GPTAPIs are required to provide the standard OpenAI completion interface
        [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "hello, show me python hello world code"},
            # {"role": "assistant", "content": ...}, # If there is an answer in the history, also include it
        ]
        """

    @abstractmethod
    async def acompletion(self, messages: list[dict]):
        """Asynchronous version of completion
        All GPTAPIs are required to provide the standard OpenAI completion interface
        [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "hello, show me python hello world code"},
            # {"role": "assistant", "content": ...}, # If there is an answer in the history, also include it
        ]
        """

    @abstractmethod
    async def acompletion_text(self, messages: list[dict], stream=False) -> str:
        """Asynchronous version of completion. Return str. Support stream-print"""

    def get_choice_text(self, rsp: dict) -> str:
        """
        Retrieve the first text of a choice.

        :param rsp: Response dictionary.
        :return: The first choice's content.
        """
        return rsp.get("choices")[0]["message"]["content"]

    def messages_to_prompt(self, messages: list[dict]):
        """
        Convert a list of messages to a prompt string.

        :param messages: List of message dictionaries.
        :return: Prompt string.
        """

        # [{"role": "user", "content": msg}] to user: <msg> etc.
        return "\n".join([f"{i['role']}: {i['content']}" for i in messages])

    def messages_to_dict(self, messages):
        """
        Convert message objects to a list of dictionaries.

        :param messages: List of message objects.
        :return: List of message dictionaries.
        """

        # objects to [{"role": "user", "content": msg}] etc.
        return [i.to_dict() for i in messages]
