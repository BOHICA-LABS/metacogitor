"""Common utility functions and classes used by the metacogitor package."""
# -*- coding: utf-8 -*-

import ast
import contextlib
import inspect
import os
import platform
import re
from typing import List, Tuple, Union

from metacogitor.logs import logger


def check_cmd_exists(command) -> int:
    """Check if a command exists on the system.

    :param command: The command to check.
    :type command: str
    :return: 0 if the command exists, 1 otherwise.
    :rtype: int
    """

    if platform.system().lower() == "windows":
        check_command = "where " + command
    else:
        check_command = (
            "command -v "
            + command
            + ' >/dev/null 2>&1 || { echo >&2 "no mermaid"; exit 1; }'
        )
    result = os.system(check_command)
    return result


class OutputParser:
    """A class for parsing the output of a command."""

    @classmethod
    def parse_blocks(cls, text: str):
        """Parse the output of a command into blocks.

        :param text: The output of a command.
        :type text: str
        :return: A dictionary containing the parsed blocks.
        :rtype: dict
        """

        blocks = text.split("##")

        block_dict = {}

        for block in blocks:

            if block.strip() != "":

                block_title, block_content = block.split("\n", 1)

                if block_title[-1] == ":":
                    block_title = block_title[:-1]
                block_dict[block_title.strip()] = block_content.strip()

        return block_dict

    @classmethod
    def parse_code(cls, text: str, lang: str = "") -> str:
        """Parse the code block from the given text.

        :param text: The text to parse.
        :type text: str
        :param lang: The language of the code block.
        :type lang: str
        :return: The parsed code block.
        :rtype: str
        """

        pattern = rf"```{lang}.*?\s+(.*?)```"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            code = match.group(1)
        else:
            raise Exception
        return code

    @classmethod
    def parse_str(cls, text: str):
        """Parse the string from the given text.

        :param text: The text to parse.
        :type text: str
        :return: The parsed string.
        :rtype: str
        """

        text = text.split("=")[-1]
        text = text.strip().strip("'").strip('"')
        return text

    @classmethod
    def parse_file_list(cls, text: str) -> list[str]:
        """Parse the file list from the given text.

        :param text: The text to parse.
        :type text: str
        :return: The parsed file list.
        :rtype: list[str]
        """

        # Regular expression pattern to find the tasks list.
        pattern = r"\s*(.*=.*)?(\[.*\])"

        # Extract tasks list string using regex.
        match = re.search(pattern, text, re.DOTALL)
        if match:
            tasks_list_str = match.group(2)

            # Convert string representation of list to a Python list using ast.literal_eval.
            tasks = ast.literal_eval(tasks_list_str)
        else:
            tasks = text.split("\n")
        return tasks

    @staticmethod
    def parse_python_code(text: str) -> str:
        """Parse the python code from the given text.

        :param text: The text to parse.
        :type text: str
        :return: The parsed python code.
        :rtype: str
        """

        for pattern in (
            r"(.*?```python.*?\s+)?(?P<code>.*)(```.*?)",
            r"(.*?```python.*?\s+)?(?P<code>.*)",
        ):
            match = re.search(pattern, text, re.DOTALL)
            if not match:
                continue
            code = match.group("code")
            if not code:
                continue
            with contextlib.suppress(Exception):
                ast.parse(code)
                return code
        raise ValueError("Invalid python code")

    @classmethod
    def parse_data(cls, data):
        """Parse the data from the given text.

        :param data: The text to parse.
        :type data: str
        :return: The parsed data.
        :rtype: dict
        """

        block_dict = cls.parse_blocks(data)
        parsed_data = {}
        for block, content in block_dict.items():

            try:
                content = cls.parse_code(text=content)
            except Exception:
                pass

            try:
                content = cls.parse_file_list(text=content)
            except Exception:
                pass
            parsed_data[block] = content
        return parsed_data

    @classmethod
    def parse_data_with_mapping(cls, data, mapping):
        """Parse the data from the given text.

        :param data: The text to parse.
        :type data: str
        :param mapping: The mapping of block to typing.
        :type mapping: dict
        :return: The parsed data.
        :rtype: dict
        """

        block_dict = cls.parse_blocks(data)
        parsed_data = {}
        for block, content in block_dict.items():

            try:
                content = cls.parse_code(text=content)
            except Exception:
                pass
            typing_define = mapping.get(block, None)
            if isinstance(typing_define, tuple):
                typing = typing_define[0]
            else:
                typing = typing_define
            if (
                typing == List[str]
                or typing == List[Tuple[str, str]]
                or typing == List[List[str]]
            ):

                try:
                    content = cls.parse_file_list(text=content)
                except Exception:
                    pass

            parsed_data[block] = content
        return parsed_data

    @classmethod
    def extract_struct(
        cls, text: str, data_type: Union[type(list), type(dict)]
    ) -> Union[list, dict]:
        """Extracts and parses a specified type of structure (dictionary or list) from the given text.

        The text only contains a list or dictionary, which may have nested structures.

        Returns:
            - If extraction and parsing are successful, it returns the corresponding data structure (list or dictionary).
            - If extraction fails or parsing encounters an error, it throw an exception.

        Examples:
            >>> text = 'xxx [1, 2, ["a", "b", [3, 4]], {"x": 5, "y": [6, 7]}] xxx'
            >>> result_list = OutputParser.extract_struct(text, "list")
            >>> print(result_list)
            >>> # Output: [1, 2, ["a", "b", [3, 4]], {"x": 5, "y": [6, 7]}]

            >>> text = 'xxx {"x": 1, "y": {"a": 2, "b": {"c": 3}}} xxx'
            >>> result_dict = OutputParser.extract_struct(text, "dict")
            >>> print(result_dict)
            >>> # Output: {"x": 1, "y": {"a": 2, "b": {"c": 3}}}

        :param text: The text containing the structure (dictionary or list).
        :type text: str
        :param data_type: The data type to extract, can be "list" or "dict".
        :type data_type: type(list) or type(dict)
        :raises Exception: If extraction fails or parsing encounters an error.
        :return: The extracted and parsed structure.
        :rtype: list or dict
        """
        # Find the first "[" or "{" and the last "]" or "}"
        start_index = text.find("[" if data_type is list else "{")
        end_index = text.rfind("]" if data_type is list else "}")

        if start_index != -1 and end_index != -1:
            # Extract the structure part
            structure_text = text[start_index : end_index + 1]

            try:
                # Attempt to convert the text to a Python data type using ast.literal_eval
                result = ast.literal_eval(structure_text)

                # Ensure the result matches the specified data type
                if isinstance(result, list) or isinstance(result, dict):
                    return result

                raise ValueError(f"The extracted structure is not a {data_type}.")

            except (ValueError, SyntaxError) as e:
                raise Exception(
                    f"Error while extracting and parsing the {data_type}: {e}"
                )
        else:
            raise Exception(f"No {data_type} found in the text.")


class CodeParser:
    """A class for parsing code blocks from text."""

    @classmethod
    def parse_block(cls, block: str, text: str) -> str:
        """Parse the specified block from the given text.

        :param block: The block to parse.
        :type block: str
        :param text: The text to parse.
        :type text: str
        :return: The parsed block.
        :rtype: str
        """

        blocks = cls.parse_blocks(text)
        for k, v in blocks.items():
            if block in k:
                return v
        return ""

    @classmethod
    def parse_blocks(cls, text: str):
        """Parse the blocks from the given text.

        :param text: The text to parse.
        :type text: str
        :return: A dictionary containing the parsed blocks.
        :rtype: dict
        """

        blocks = text.split("##")

        block_dict = {}

        for block in blocks:

            if block.strip() != "":

                block_title, block_content = block.split("\n", 1)
                block_dict[block_title.strip()] = block_content.strip()

        return block_dict

    @classmethod
    def parse_code(cls, block: str, text: str, lang: str = "") -> str:
        """Parse the code block from the given text.

        :param block: The block to parse.
        :type block: str
        :param text: The text to parse.
        :type text: str
        :param lang: The language of the code block.
        :type lang: str
        :return: The parsed code block.
        :rtype: str
        """

        if block:
            text = cls.parse_block(block, text)
        pattern = rf"```{lang}.*?\s+(.*?)```"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            code = match.group(1)
        else:
            logger.error(f"{pattern} not match following text:")
            logger.error(text)
            # raise Exception
            return text  # just assume original text is code
        return code

    @classmethod
    def parse_str(cls, block: str, text: str, lang: str = ""):
        """Parse the string from the given text.

        :param block: The block to parse.
        :type block: str
        :param text: The text to parse.
        :type text: str
        :param lang: The language of the code block.
        :type lang: str
        :return: The parsed string.
        :rtype: str
        """

        code = cls.parse_code(block, text, lang)
        code = code.split("=")[-1]
        code = code.strip().strip("'").strip('"')
        return code

    @classmethod
    def parse_file_list(cls, block: str, text: str, lang: str = "") -> list[str]:
        """Parse the file list from the given text.

        :param block: The block to parse.
        :type block: str
        :param text: The text to parse.
        :type text: str
        :param lang: The language of the code block.
        :type lang: str
        :return: The parsed file list.
        :rtype: list[str]
        """

        # Regular expression pattern to find the tasks list.
        code = cls.parse_code(block, text, lang)
        # print(code)
        pattern = r"\s*(.*=.*)?(\[.*\])"

        # Extract tasks list string using regex.
        match = re.search(pattern, code, re.DOTALL)
        if match:
            tasks_list_str = match.group(2)

            # Convert string representation of list to a Python list using ast.literal_eval.
            tasks = ast.literal_eval(tasks_list_str)
        else:
            raise Exception
        return tasks


class NoMoneyException(Exception):
    """NoMoneyException class.

    Raised when the operation cannot be completed due to insufficient funds
    """

    def __init__(self, amount, message="Insufficient funds"):
        """Initialize the NoMoneyException class.

        :param amount: The amount required.
        :type amount: int
        :param message: The error message.
        :type message: str
        """

        self.amount = amount
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} -> Amount required: {self.amount}"


def print_members(module, indent=0):
    """Print the members of a module.
    https://stackoverflow.com/questions/1796180/how-can-i-get-a-list-of-all-classes-within-current-module-in-python
    :param module: The module to print the members of.
    :type module: module
    :param indent: The indentation level.
    :type indent: int
    :return: None
    :rtype: None
    """

    prefix = " " * indent
    for name, obj in inspect.getmembers(module):
        print(name, obj)
        if inspect.isclass(obj):
            print(f"{prefix}Class: {name}")
            # print the methods within the class
            if name in ["__class__", "__base__"]:
                continue
            print_members(obj, indent + 2)
        elif inspect.isfunction(obj):
            print(f"{prefix}Function: {name}")
        elif inspect.ismethod(obj):
            print(f"{prefix}Method: {name}")


def parse_recipient(text):
    """Parse the recipient from the given text.

    :param text: The text to parse.
    :type text: str
    :return: The parsed recipient.
    :rtype: str
    """

    pattern = r"## Send To:\s*([A-Za-z]+)\s*?"  # hard code for now
    recipient = re.search(pattern, text)
    return recipient.group(1) if recipient else ""
