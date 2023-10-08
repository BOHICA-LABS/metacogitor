"""Code interpreter for metacogitor."""
# -*- coding: utf-8 -*-

import re
from typing import List, Callable
from pathlib import Path

import wrapt
import textwrap
import inspect
from interpreter.interpreter import Interpreter

from metacogitor.logs import logger
from metacogitor.config import CONFIG
from metacogitor.utils.highlight import highlight
from metacogitor.actions.clone_function import (
    CloneFunction,
    run_function_code,
    run_function_script,
)


def extract_python_code(code: str):
    """Extract code blocks: If the code comments are the same, only the last code block is kept.

    :param code: code with comments.
    :type code: str
    :return: code without comments.
    :rtype: str
    """

    # Use regular expressions to match comment blocks and related code.
    pattern = r"(#\s[^\n]*)\n(.*?)(?=\n\s*#|$)"
    matches = re.findall(pattern, code, re.DOTALL)

    # Extract the last code block when encountering the same comment.
    unique_comments = {}
    for comment, code_block in matches:
        unique_comments[comment] = code_block

    # concatenate into functional form
    result_code = "\n".join(
        [f"{comment}\n{code_block}" for comment, code_block in unique_comments.items()]
    )
    header_code = code[: code.find("#")]
    code = header_code + result_code

    logger.info(f"Extract python code: \n {highlight(code)}")

    return code


class OpenCodeInterpreter(object):
    """https://github.com/KillianLucas/open-interpreter"""

    def __init__(self, auto_run: bool = True) -> None:
        """Initialize the OpenCodeInterpreter.

        :param auto_run: Whether to automatically run the code after the code is generated, defaults to True
        :type auto_run: bool, optional
        """
        interpreter = Interpreter()
        interpreter.auto_run = auto_run
        interpreter.model = CONFIG.openai_api_model or "gpt-3.5-turbo"
        interpreter.api_key = CONFIG.openai_api_key
        interpreter.api_base = CONFIG.openai_api_base
        self.interpreter = interpreter

    def chat(self, query: str, reset: bool = True):
        """chat with open-interpreter.

        :param query: query for open-interpreter.
        :type query: str
        :param reset: Whether to reset the state of the open-interpreter, defaults to True
        :type reset: bool, optional
        :return: respond from open-interpreter.
        :rtype: dict
        """

        if reset:
            self.interpreter.reset()
        return self.interpreter.chat(query, return_messages=True)

    @staticmethod
    def extract_function(
        query_respond: List,
        function_name: str,
        *,
        language: str = "python",
        function_format: str = None,
    ) -> str:
        """create a function from query_respond.

        :param query_respond: respond from open-interpreter.
        :type query_respond: List
        :param function_name: function name.
        :type function_name: str
        :param language: language of the function, defaults to "python"
        :type language: str, optional
        :param function_format: function format, defaults to None
        :type function_format: str, optional
        :return: function code.
        :rtype: str
        """

        if language not in ("python"):
            raise NotImplementedError(f"Not support to parse language {language}!")

        # set function form
        if function_format is None:
            assert (
                language == "python"
            ), f"Expect python language for default function_format, but got {language}."
            function_format = """def {function_name}():\n{code}"""
        # Extract the code module in the open-interpreter respond message.
        code = [
            item["function_call"]["parsed_arguments"]["code"]
            for item in query_respond
            if "function_call" in item
            and "parsed_arguments" in item["function_call"]
            and "language" in item["function_call"]["parsed_arguments"]
            and item["function_call"]["parsed_arguments"]["language"] == language
        ]
        # add indent.
        indented_code_str = textwrap.indent("\n".join(code), " " * 4)
        # Return the code after deduplication.
        if language == "python":
            return extract_python_code(
                function_format.format(
                    function_name=function_name, code=indented_code_str
                )
            )


def gen_query(func: Callable, args, kwargs) -> str:
    """Generate query for open-interpreter.

    :param func: function.
    :type func: Callable
    :param args: args of function.
    :type args: tuple
    :param kwargs: kwargs of function.
    :type kwargs: dict
    :return: query for open-interpreter.
    :rtype: str
    """

    # Get the annotation of the function as part of the query.
    desc = func.__doc__
    signature = inspect.signature(func)
    # Get the signature of the wrapped function and the assignment of the input parameters as part of the query.
    bound_args = signature.bind(*args, **kwargs)
    bound_args.apply_defaults()
    query = f"{desc}, {bound_args.arguments}, If you must use a third-party package, use the most popular ones, for example: pandas, numpy, ta, ..."
    return query


def gen_template_fun(func: Callable) -> str:
    """Generate template function.

    :param func: function.
    :type func: Callable
    :return: template function.
    :rtype: str
    """

    return f"def {func.__name__}{str(inspect.signature(func))}\n    # here is your code ..."


class OpenInterpreterDecorator(object):
    """OpenInterpreter Decorator."""

    def __init__(
        self,
        save_code: bool = False,
        code_file_path: str = None,
        clear_code: bool = False,
    ) -> None:
        """Initialize the OpenInterpreterDecorator.

        :param save_code: Whether to save the generated code to a file, defaults to False
        :type save_code: bool, optional
        :param code_file_path: The path to the file where the generated code is saved, defaults to None
        :type code_file_path: str, optional
        :param clear_code: Whether to clear the generated code, defaults to False
        :type clear_code: bool, optional
        """

        self.save_code = save_code
        self.code_file_path = code_file_path
        self.clear_code = clear_code

    def __call__(self, wrapped):
        @wrapt.decorator
        async def wrapper(wrapped: Callable, instance, args, kwargs):
            # Get the decorated function name.
            func_name = wrapped.__name__
            # If the script exists locally and clearcode is not required, execute the function from the script.
            if Path(self.code_file_path).is_file() and not self.clear_code:
                return run_function_script(
                    self.code_file_path, func_name, *args, **kwargs
                )

            # Auto run generate code by using open-interpreter.
            interpreter = OpenCodeInterpreter()
            query = gen_query(wrapped, args, kwargs)
            logger.info(f"query for OpenCodeInterpreter: \n {query}")
            respond = interpreter.chat(query)
            # Assemble the code blocks generated by open-interpreter into a function without parameters.
            func_code = interpreter.extract_function(respond, func_name)
            # Clone the `func_code` into wrapped, that is,
            # keep the `func_code` and wrapped functions with the same input parameter and return value types.
            template_func = gen_template_fun(wrapped)
            cf = CloneFunction()
            code = await cf.run(template_func=template_func, source_code=func_code)
            # Display the generated function in the terminal.
            logger_code = highlight(code, "python")
            logger.info(f"Creating following Python function:\n{logger_code}")
            # execute this function.
            try:
                res = run_function_code(code, func_name, *args, **kwargs)
                if self.save_code:
                    cf._save(self.code_file_path, code)
            except Exception as e:
                raise Exception("Could not evaluate Python code", e)
            return res

        return wrapper(wrapped)