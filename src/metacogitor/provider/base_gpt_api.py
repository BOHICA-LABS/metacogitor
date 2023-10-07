"""Base GPT API class"""
# -*- coding: utf-8 -*-

from abc import abstractmethod
from typing import Optional

from metacogitor.logs import logger
from metacogitor.provider.base_chatbot import BaseChatbot


class BaseGPTAPI(BaseChatbot):
    """GPT API abstract class, requiring all inheritors to provide a series of standard capabilities"""

    system_prompt = "You are a helpful assistant."

    def _user_msg(self, msg: str) -> dict[str, str]:
        """User message

        :param msg: User message
        :type msg: str
        :return: {"role": "user", "content": msg}
        :rtype: dict[str, str]
        """
        return {"role": "user", "content": msg}

    def _assistant_msg(self, msg: str) -> dict[str, str]:
        """Assistant message

        :param msg: Assistant message
        :type msg: str
        :return: {"role": "assistant", "content": msg}
        :rtype: dict[str, str]
        """

        return {"role": "assistant", "content": msg}

    def _system_msg(self, msg: str) -> dict[str, str]:
        """System message

        :param msg: System message
        :type msg: str
        :return: {"role": "system", "content": msg}
        :rtype: dict[str, str]
        """

        return {"role": "system", "content": msg}

    def _system_msgs(self, msgs: list[str]) -> list[dict[str, str]]:
        """System messages

        :param msgs: System messages
        :type msgs: list[str]
        :return: [{"role": "system", "content": msg} for msg in msgs]
        :rtype: list[dict[str, str]]
        """

        return [self._system_msg(msg) for msg in msgs]

    def _default_system_msg(self):
        """Default system message

        :return: {"role": "system", "content": self.system_prompt}
        :rtype: dict[str, str]
        """

        return self._system_msg(self.system_prompt)

    def ask(self, msg: str) -> str:
        """Ask GPT a question and get an answer

        :param msg: User message
        :type msg: str
        :return: Assistant message
        :rtype: str
        """

        message = [self._default_system_msg(), self._user_msg(msg)]
        rsp = self.completion(message)
        return self.get_choice_text(rsp)

    async def aask(self, msg: str, system_msgs: Optional[list[str]] = None) -> str:
        """Ask GPT a question and get an answer

        :param msg: User message
        :type msg: str
        :param system_msgs: System messages, defaults to None
        :type system_msgs: Optional[list[str]], optional
        :return: Assistant message
        :rtype: str
        """

        if system_msgs:
            message = self._system_msgs(system_msgs) + [self._user_msg(msg)]
        else:
            message = [self._default_system_msg(), self._user_msg(msg)]
        rsp = await self.acompletion_text(message, stream=True)
        logger.debug(message)
        # logger.debug(rsp)
        return rsp

    def _extract_assistant_rsp(self, context):
        """Extract assistant response from context

        :param context: [{"role": "user", "content": msg}, {"role": "assistant", "content": msg}, ...]
        :type context: list[dict[str, str]]
        :return: Assistant response
        :rtype: str
        """

        return "\n".join([i["content"] for i in context if i["role"] == "assistant"])

    def ask_batch(self, msgs: list) -> str:
        """Batch questioning

        :param msgs: User messages
        :type msgs: list
        :return: Assistant response
        :rtype: str
        """

        context = []
        for msg in msgs:
            umsg = self._user_msg(msg)
            context.append(umsg)
            rsp = self.completion(context)
            rsp_text = self.get_choice_text(rsp)
            context.append(self._assistant_msg(rsp_text))
        return self._extract_assistant_rsp(context)

    async def aask_batch(self, msgs: list) -> str:
        """Sequential questioning

        :param msgs: User messages
        :type msgs: list
        :return: Assistant response
        :rtype: str
        """

        context = []
        for msg in msgs:
            umsg = self._user_msg(msg)
            context.append(umsg)
            rsp_text = await self.acompletion_text(context)
            context.append(self._assistant_msg(rsp_text))
        return self._extract_assistant_rsp(context)

    # TODO: No code segment filtering has been done here, and all results are actually displayed
    def ask_code(self, msgs: list[str]) -> str:
        """Ask GPT multiple questions and get a piece of code

        :param msgs: User messages
        :type msgs: list[str]
        :return: Assistant response
        :rtype: str
        """

        rsp_text = self.ask_batch(msgs)
        return rsp_text

    # TODO: No code segment filtering has been done here, and all results are actually displayed
    async def aask_code(self, msgs: list[str]) -> str:
        """Asynchronous version of ask_code

        :param msgs: User messages
        :type msgs: list[str]
        :return: Assistant response
        :rtype: str
        """

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
        """Required to provide the first text of choice

        :param rsp: {"choices": [{"text": "xxx", "index": 0, "logprobs": {"tokens": [], "text_offset": []}, "finish_reason": "length"}], "created": "2021-08-12T15:00:00.000000Z", "id": "cmpl-xxx", "model": "xxx", "object": "text_completion"}
        :type rsp: dict
        :return: The first text of choice
        :rtype: str
        """

        return rsp.get("choices")[0]["message"]["content"]

    def messages_to_prompt(self, messages: list[dict]):
        """[{"role": "user", "content": msg}] to user: <msg> etc."""
        return "\n".join([f"{i['role']}: {i['content']}" for i in messages])

    def messages_to_dict(self, messages):
        """objects to [{"role": "user", "content": msg}] etc."""
        return [i.to_dict() for i in messages]
