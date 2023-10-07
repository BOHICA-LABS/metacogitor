"""OpenAI API provider"""
# -*- coding: utf-8 -*-

import asyncio
import time
from typing import NamedTuple, Union

import openai
from openai.error import APIConnectionError
from tenacity import (
    after_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
)

from metacogitor.config import CONFIG
from metacogitor.logs import logger
from metacogitor.provider.base_gpt_api import BaseGPTAPI
from metacogitor.utils.singleton import Singleton
from metacogitor.utils.token_counter import (
    TOKEN_COSTS,
    count_message_tokens,
    count_string_tokens,
    get_max_completion_tokens,
)


class RateLimiter:
    """Rate control class, each call goes through wait_if_needed, sleep if rate control is needed"""

    def __init__(self, rpm):
        self.last_call_time = 0
        # Here 1.1 is used because even if the calls are made strictly according to time,
        # they will still be QOS'd; consider switching to simple error retry later
        self.interval = 1.1 * 60 / rpm
        self.rpm = rpm

    def split_batches(self, batch):
        return [batch[i : i + self.rpm] for i in range(0, len(batch), self.rpm)]

    async def wait_if_needed(self, num_requests):
        current_time = time.time()
        elapsed_time = current_time - self.last_call_time

        if elapsed_time < self.interval * num_requests:
            remaining_time = self.interval * num_requests - elapsed_time
            logger.info(f"sleep {remaining_time}")
            await asyncio.sleep(remaining_time)

        self.last_call_time = time.time()


class Costs(NamedTuple):
    """Costs of API calls"""

    total_prompt_tokens: int
    total_completion_tokens: int
    total_cost: float
    total_budget: float


class CostManager(metaclass=Singleton):
    """Cost manager for API calls"""

    def __init__(self):
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost = 0
        self.total_budget = 0

    def update_cost(self, prompt_tokens, completion_tokens, model):
        """Update the total cost, prompt tokens, and completion tokens.


        :param prompt_tokens: The number of tokens used in the prompt.
        :type prompt_tokens: int
        :param completion_tokens: The number of tokens used in the completion.
        :type completion_tokens: int
        :param model: The model used for the API call.
        :type model: str
        """
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        cost = (
            prompt_tokens * TOKEN_COSTS[model]["prompt"]
            + completion_tokens * TOKEN_COSTS[model]["completion"]
        ) / 1000
        self.total_cost += cost
        logger.info(
            f"Total running cost: ${self.total_cost:.3f} | Max budget: ${CONFIG.max_budget:.3f} | "
            f"Current cost: ${cost:.3f}, prompt_tokens: {prompt_tokens}, completion_tokens: {completion_tokens}"
        )
        CONFIG.total_cost = self.total_cost

    def get_total_prompt_tokens(self):
        """Get the total number of prompt tokens.

        :return: The total number of prompt tokens.
        :rtype: int
        """

        return self.total_prompt_tokens

    def get_total_completion_tokens(self):
        """Get the total number of completion tokens.

        :return: The total number of completion tokens.
        :rtype: int
        """

        return self.total_completion_tokens


def get_total_cost(self):
    """Get the total cost of API calls.

    :return: The total cost of API calls.
    :rtype: float
    """
    return self.total_cost


def get_costs(self) -> Costs:
    """Get all costs

    :return: The total cost of API calls.
    :rtype: Costs
    """

    return Costs(
        self.total_prompt_tokens,
        self.total_completion_tokens,
        self.total_cost,
        self.total_budget,
    )


def log_and_reraise(retry_state):
    """Log and reraise the last exception

    :param retry_state: The retry state.
    :type retry_state: tenacity.RetryCallState
    """

    logger.error(
        f"Retry attempts exhausted. Last exception: {retry_state.outcome.exception()}"
    )
    logger.warning(
        """
Recommend going to https://deepwisdom.feishu.cn/wiki/MsGnwQBjiif9c3koSJNcYaoSnu4#part-XdatdVlhEojeAfxaaEZcMV3ZniQ
See FAQ 5.8
"""
    )
    raise retry_state.outcome.exception()


class OpenAIGPTAPI(BaseGPTAPI, RateLimiter):
    """OpenAI API provider

    Check https://platform.openai.com/examples for examples
    """

    def __init__(self):
        """Initialize the OpenAIGPTAPI instance."""

        self.__init_openai(CONFIG)
        self.llm = openai
        self.model = CONFIG.openai_api_model
        self.auto_max_tokens = False
        self._cost_manager = CostManager()
        RateLimiter.__init__(self, rpm=self.rpm)

    def __init_openai(self, config):
        """Initialize the OpenAI API.

        :param config: The config.
        :type config: Config
        """

        openai.api_key = config.openai_api_key
        if config.openai_api_base:
            openai.api_base = config.openai_api_base
        if config.openai_api_type:
            openai.api_type = config.openai_api_type
            openai.api_version = config.openai_api_version
        self.rpm = int(config.get("RPM", 10))

    async def _achat_completion_stream(self, messages: list[dict]) -> str:
        """when streaming, print each token in place.

        :param messages: The messages to use for the API call.
        :type messages: list[dict]
        :return: The full reply content.
        :rtype: str
        """
        response = await openai.ChatCompletion.acreate(
            **self._cons_kwargs(messages), stream=True
        )

        # create variables to collect the stream of chunks
        collected_chunks = []
        collected_messages = []
        # iterate through the stream of events
        async for chunk in response:
            collected_chunks.append(chunk)  # save the event response
            choices = chunk["choices"]
            if len(choices) > 0:
                chunk_message = chunk["choices"][0].get(
                    "delta", {}
                )  # extract the message
                collected_messages.append(chunk_message)  # save the message
                if "content" in chunk_message:
                    print(chunk_message["content"], end="")
        print()

        full_reply_content = "".join([m.get("content", "") for m in collected_messages])
        usage = self._calc_usage(messages, full_reply_content)
        self._update_costs(usage)
        return full_reply_content

    def _cons_kwargs(self, messages: list[dict]) -> dict:
        """Construct kwargs for API call.

        :param messages: The messages to use for the API call.
        :type messages: list[dict]
        :return: The kwargs for the API call.
        :rtype: dict
        """

        kwargs = {
            "messages": messages,
            "max_tokens": self.get_max_tokens(messages),
            "n": 1,
            "stop": None,
            "temperature": 0.3,
            "timeout": 3,
        }
        if CONFIG.openai_api_type == "azure":
            if CONFIG.deployment_name and CONFIG.deployment_id:
                raise ValueError(
                    "You can only use one of the `deployment_id` or `deployment_name` model"
                )
            elif not CONFIG.deployment_name and not CONFIG.deployment_id:
                raise ValueError(
                    "You must specify `DEPLOYMENT_NAME` or `DEPLOYMENT_ID` parameter"
                )
            kwargs_mode = (
                {"engine": CONFIG.deployment_name}
                if CONFIG.deployment_name
                else {"deployment_id": CONFIG.deployment_id}
            )
        else:
            kwargs_mode = {"model": self.model}
        kwargs.update(kwargs_mode)
        return kwargs

    async def _achat_completion(self, messages: list[dict]) -> dict:
        """Async Chat Completion API call.

        :param messages: The messages to use for the API call.
        :type messages: list[dict]
        :return: The full JSON response.
        :rtype: dict
        """

        rsp = await self.llm.ChatCompletion.acreate(**self._cons_kwargs(messages))
        self._update_costs(rsp.get("usage"))
        return rsp

    def _chat_completion(self, messages: list[dict]) -> dict:
        """Sync Chat Completion API call.

        :param messages: The messages to use for the API call.
        :type messages: list[dict]
        :return: The full JSON response.
        :rtype: dict
        """

        rsp = self.llm.ChatCompletion.create(**self._cons_kwargs(messages))
        self._update_costs(rsp)
        return rsp

    def completion(self, messages: list[dict]) -> dict:
        """Sync Chat Completion API call.

        :param messages: The messages to use for the API call.
        :type messages: list[dict]
        :return: The full JSON response.
        :rtype: dict
        """

        # if isinstance(messages[0], Message):
        #     messages = self.messages_to_dict(messages)
        return self._chat_completion(messages)

    async def acompletion(self, messages: list[dict]) -> dict:
        """Async Chat Completion API call.

        :param messages: The messages to use for the API call.
        :type messages: list[dict]
        :return: The full JSON response.
        :rtype: dict
        """

        # if isinstance(messages[0], Message):
        #     messages = self.messages_to_dict(messages)
        return await self._achat_completion(messages)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(1),
        after=after_log(logger, logger.level("WARNING").name),
        retry=retry_if_exception_type(APIConnectionError),
        retry_error_callback=log_and_reraise,
    )
    async def acompletion_text(self, messages: list[dict], stream=False) -> str:
        """Async Chat Completion API call.

        :param messages: The messages to use for the API call.
        :type messages: list[dict]
        :param stream: Whether to stream the response.
        :type stream: bool
        :return: The full reply content.
        :rtype: str
        """

        if stream:
            return await self._achat_completion_stream(messages)
        rsp = await self._achat_completion(messages)
        return self.get_choice_text(rsp)

    def _calc_usage(self, messages: list[dict], rsp: str) -> dict:
        """Calculate the usage of the API call.

        :param messages: The messages to use for the API call.
        :type messages: list[dict]
        :param rsp: The response from the API call.
        :type rsp: str
        :return: The usage of the API call.
        :rtype: dict
        """

        usage = {}
        if CONFIG.calc_usage:
            try:
                prompt_tokens = count_message_tokens(messages, self.model)
                completion_tokens = count_string_tokens(rsp, self.model)
                usage["prompt_tokens"] = prompt_tokens
                usage["completion_tokens"] = completion_tokens
                return usage
            except Exception as e:
                logger.error("usage calculation failed!", e)
        else:
            return usage

    async def acompletion_batch(self, batch: list[list[dict]]) -> list[dict]:
        """Async Chat Completion API call. Batch

        :param batch: The batch of messages to use for the API call.
        :type batch: list[list[dict]]
        :return: The full JSON response.
        :rtype: list[dict]
        """

        split_batches = self.split_batches(batch)
        all_results = []

        for small_batch in split_batches:
            logger.info(small_batch)
            await self.wait_if_needed(len(small_batch))

            future = [self.acompletion(prompt) for prompt in small_batch]
            results = await asyncio.gather(*future)
            logger.info(results)
            all_results.extend(results)

        return all_results

    async def acompletion_batch_text(self, batch: list[list[dict]]) -> list[str]:
        """Only return plain text

        :param batch: The batch of messages to use for the API call.
        :type batch: list[list[dict]]
        :return: The full JSON response.
        :rtype: list[dict]
        """

        raw_results = await self.acompletion_batch(batch)
        results = []
        for idx, raw_result in enumerate(raw_results, start=1):
            result = self.get_choice_text(raw_result)
            results.append(result)
            logger.info(f"Result of task {idx}: {result}")
        return results

    def _update_costs(self, usage: dict):
        """Update the costs of the API call.

        :param usage: The usage of the API call.
        :type usage: dict
        """

        if CONFIG.calc_usage:
            try:
                prompt_tokens = int(usage["prompt_tokens"])
                completion_tokens = int(usage["completion_tokens"])
                self._cost_manager.update_cost(
                    prompt_tokens, completion_tokens, self.model
                )
            except Exception as e:
                logger.error("updating costs failed!", e)

    def get_costs(self) -> Costs:
        """Get all costs

        :return: The total cost of API calls.
        :rtype: Costs
        """

        return self._cost_manager.get_costs()

    def get_max_tokens(self, messages: list[dict]):
        """Get the maximum number of tokens for the API call.

        :param messages: The messages to use for the API call.
        :type messages: list[dict]
        :return: The maximum number of tokens for the API call.
        :rtype: int
        """

        if not self.auto_max_tokens:
            return CONFIG.max_tokens_rsp
        return get_max_completion_tokens(messages, self.model, CONFIG.max_tokens_rsp)

    def moderation(self, content: Union[str, list[str]]):
        """moderating content

        :param content: The content to be moderated.
        :type content: Union[str, list[str]]
        :return: The moderation result.
        :rtype: dict
        """

        try:
            if not content:
                logger.error("content cannot be empty!")
            else:
                rsp = self._moderation(content=content)
                return rsp
        except Exception as e:
            logger.error(f"moderating failed:{e}")

    def _moderation(self, content: Union[str, list[str]]):
        """moderating content

        :param content: The content to be moderated.
        :type content: Union[str, list[str]]
        :return: The moderation result.
        :rtype: dict
        """

        rsp = self.llm.Moderation.create(input=content)
        return rsp

    async def amoderation(self, content: Union[str, list[str]]):
        """moderating content

        :param content: The content to be moderated.
        :type content: Union[str, list[str]]
        :return: The moderation result.
        :rtype: dict
        """

        try:
            if not content:
                logger.error("content cannot be empty!")
            else:
                rsp = await self._amoderation(content=content)
                return rsp
        except Exception as e:
            logger.error(f"moderating failed:{e}")

    async def _amoderation(self, content: Union[str, list[str]]):
        """moderating content Async

        :param content: The content to be moderated.
        :type content: Union[str, list[str]]
        :return: The moderation result.
        :rtype: dict
        """

        rsp = await self.llm.Moderation.acreate(input=content)
        return rsp
