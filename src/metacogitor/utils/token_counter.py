#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/8/18 00:40
@Author  : Joshua Magady
@File    : token_counter.py
@Desc    : Count tokens in a string and return the cost.
ref1: https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
ref2: https://github.com/Significant-Gravitas/Auto-GPT/blob/master/autogpt/llm/token_counter.py
ref3: https://github.com/hwchase17/langchain/blob/master/langchain/chat_models/openai.py
"""
import tiktoken


__ALL__ = [
    "TOKEN_COSTS",
    "TOKEN_MAX",
    "count_string_tokens",
    "count_message_tokens",
    "get_max_completion_tokens",
]

TOKEN_COSTS = {
    "gpt-3.5-turbo": {"prompt": 0.0015, "completion": 0.002},
    "gpt-3.5-turbo-0301": {"prompt": 0.0015, "completion": 0.002},
    "gpt-3.5-turbo-0613": {"prompt": 0.0015, "completion": 0.002},
    "gpt-3.5-turbo-16k": {"prompt": 0.003, "completion": 0.004},
    "gpt-3.5-turbo-16k-0613": {"prompt": 0.003, "completion": 0.004},
    "gpt-4-0314": {"prompt": 0.03, "completion": 0.06},
    "gpt-4": {"prompt": 0.03, "completion": 0.06},
    "gpt-4-32k": {"prompt": 0.06, "completion": 0.12},
    "gpt-4-32k-0314": {"prompt": 0.06, "completion": 0.12},
    "gpt-4-0613": {"prompt": 0.06, "completion": 0.12},
    "text-embedding-ada-002": {"prompt": 0.0004, "completion": 0.0},
}
"""Dict of token costs for different AI models, with prompt and completion costs."""

TOKEN_MAX = {
    "gpt-3.5-turbo": 4096,
    "gpt-3.5-turbo-0301": 4096,
    "gpt-3.5-turbo-0613": 4096,
    "gpt-3.5-turbo-16k": 16384,
    "gpt-3.5-turbo-16k-0613": 16384,
    "gpt-4-0314": 8192,
    "gpt-4": 8192,
    "gpt-4-32k": 32768,
    "gpt-4-32k-0314": 32768,
    "gpt-4-0613": 8192,
    "text-embedding-ada-002": 8192,
}
"""Dict of max tokens allowed for different AI models."""


def count_message_tokens(messages, model="gpt-3.5-turbo-0613"):
    """Count number of tokens for a list of messages.

    Args:
        messages (list): List of message dicts.
        model (str, optional): AI model to use. Defaults to "gpt-3.5-turbo-0613".

    Returns:
        int: Total number of tokens.

    Raises:
        NotImplementedError: If model is not implemented.
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
    }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = (
            4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        )
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        print(
            "Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613."
        )
        return count_message_tokens(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        print(
            "Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613."
        )
        return count_message_tokens(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


def count_string_tokens(string: str, model_name: str) -> int:
    """Count number of tokens in a text string.

    Args:
        string (str): The text string.
        model_name (str): Name of encoding to use.

    Returns:
        int: Number of tokens in the string.
    """

    encoding = tiktoken.encoding_for_model(model_name)
    """Get encoding for the model."""

    return len(encoding.encode(string))
    """Encode string and return length as token count."""


def get_max_completion_tokens(messages: list[dict], model: str, default: int) -> int:
    """Get max completion tokens for a model and list of messages.

    Args:
        messages (list[dict]): List of message dicts.
        model (str): Name of the AI model.
        default (int): Default value if model not found.

    Returns:
        int: Max number of completion tokens.

    """

    if model not in TOKEN_MAX:
        """If model not found, return default."""
        return default

    # Calculate tokens used by messages
    used_tokens = count_message_tokens(messages)

    # Subtract used tokens from model's max
    max_tokens = TOKEN_MAX[model] - used_tokens - 1

    return max_tokens
