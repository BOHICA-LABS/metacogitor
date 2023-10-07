"""Utility functions for text processing."""
# -*- coding: utf-8 -*-

from typing import Generator, Sequence

from metacogitor.utils.token_counter import TOKEN_MAX, count_string_tokens


def reduce_message_length(
    msgs: Generator[str, None, None],
    model_name: str,
    system_text: str,
    reserved: int = 0,
) -> str:
    """Reduce the length of concatenated message segments to fit within the maximum token size.

    :param msgs: A generator of strings representing progressively shorter valid prompts.
    :type msgs: Generator[str, None, None]
    :param model_name: The name of the encoding to use. (e.g., "gpt-3.5-turbo")
    :type model_name: str
    :param system_text: The system prompts.
    :type system_text: str
    :param reserved: The number of reserved tokens.
    :type reserved: int
    :return: The concatenated message segments reduced to fit within the maximum token size.
    :rtype: str
    :raises RuntimeError: If it fails to reduce the concatenated message length.
    """

    max_token = (
        TOKEN_MAX.get(model_name, 2048)
        - count_string_tokens(system_text, model_name)
        - reserved
    )
    for msg in msgs:
        if count_string_tokens(msg, model_name) < max_token:
            return msg

    raise RuntimeError("fail to reduce message length")


def generate_prompt_chunk(
    text: str,
    prompt_template: str,
    model_name: str,
    system_text: str,
    reserved: int = 0,
) -> Generator[str, None, None]:
    """Split the text into chunks of a maximum token size.

    :param text: The text to split.
    :param prompt_template: The template for the prompt, containing a single `{}` placeholder. For example, "### Reference\n{}".
    :param model_name: The name of the encoding to use. (e.g., "gpt-3.5-turbo")
    :param system_text: The system prompts.
    :param reserved: The number of reserved tokens.
    :return: yeilds The chunk of text.
    :rtype: Generator[str, None, None]
    :raises RuntimeError: If it fails to reduce the concatenated message length.

    """

    paragraphs = text.splitlines(keepends=True)
    current_token = 0
    current_lines = []

    reserved = reserved + count_string_tokens(prompt_template + system_text, model_name)
    # 100 is a magic number to ensure the maximum context length is not exceeded
    max_token = TOKEN_MAX.get(model_name, 2048) - reserved - 100

    while paragraphs:
        paragraph = paragraphs.pop(0)
        token = count_string_tokens(paragraph, model_name)
        if current_token + token <= max_token:
            current_lines.append(paragraph)
            current_token += token
        elif token > max_token:
            paragraphs = split_paragraph(paragraph) + paragraphs
            continue
        else:
            yield prompt_template.format("".join(current_lines))
            current_lines = [paragraph]
            current_token = token

    if current_lines:
        yield prompt_template.format("".join(current_lines))


def split_paragraph(paragraph: str, sep: str = ".,", count: int = 2) -> list[str]:
    """Split a paragraph into multiple parts.

    :param paragraph: The paragraph to split.
    :type paragraph: str
    :param sep: The separator character.
    :type sep: str
    :param count: The number of parts to split the paragraph into.
    :type count: int
    :return: A list of split parts of the paragraph.
    :rtype: list[str]
    """
    for i in sep:
        sentences = list(_split_text_with_ends(paragraph, i))
        if len(sentences) <= 1:
            continue
        ret = ["".join(j) for j in _split_by_count(sentences, count)]
        return ret
    return _split_by_count(paragraph, count)


def decode_unicode_escape(text: str) -> str:
    """Decode a text with unicode escape sequences.

    :param text: The text to decode.
    :type text: str
    :return: The decoded text.
    :rtype: str
    """

    return text.encode("utf-8").decode("unicode_escape", "ignore")


def _split_by_count(lst: Sequence, count: int):
    """Split a list into multiple parts.

    :param lst: The list to split.
    :type lst: Sequence
    :param count: The number of parts to split the list into.
    :type count: int
    :return: A generator of split parts of the list.
    :rtype: Generator
    """

    avg = len(lst) // count
    remainder = len(lst) % count
    start = 0
    for i in range(count):
        end = start + avg + (1 if i < remainder else 0)
        yield lst[start:end]
        start = end


def _split_text_with_ends(text: str, sep: str = "."):
    """Split a text into multiple parts.

    :param text: The text to split.
    :type text: str
    :param sep: The separator character.
    :type sep: str
    :return: A generator of split parts of the text.
    :rtype: Generator
    """

    parts = []
    for i in text:
        parts.append(i)
        if i == sep:
            yield "".join(parts)
            parts = []
    if parts:
        yield "".join(parts)
