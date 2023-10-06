"""Clone function from source code to template function."""
# -*- coding: utf-8 -*-

from pathlib import Path
import traceback

from metacogitor.actions.write_code import WriteCode
from metacogitor.logs import logger
from metacogitor.schema import Message
from metacogitor.utils.highlight import highlight

CLONE_PROMPT = """
*context*
Please convert the function code ```{source_code}``` into the the function format: ```{template_func}```.
*Please Write code based on the following list and context*
1. Write code start with ```, and end with ```.
2. Please implement it in one function if possible, except for import statements. for exmaple:
```python
import pandas as pd
def run(*args) -> pd.DataFrame:
    ...
```
3. Do not use public member functions that do not exist in your design.
4. The output function name, input parameters and return value must be the same as ```{template_func}```.
5. Make sure the results before and after the code conversion are required to be exactly the same.
6. Don't repeat my context in your replies.
7. Return full results, for example, if the return value has df.head(), please return df.
8. If you must use a third-party package, use the most popular ones, for example: pandas, numpy, ta, ...
"""


class CloneFunction(WriteCode):
    """Clone function from source code to template function."""

    def __init__(self, name="CloneFunction", context: list[Message] = None, llm=None):
        """Initialize CloneFunction action.

        :param name: The name of the action, defaults to "CloneFunction"
        :type name: str, optional
        :param context: The context of the action, defaults to None
        :type context: list[Message], optional
        """
        super().__init__(name, context, llm)

    def _save(self, code_path, code):
        """Save code to code_path.

        :param code_path: The path to save the code.
        :type code_path: str
        :param code: The code to save.
        :type code: str
        """
        if isinstance(code_path, str):
            code_path = Path(code_path)
        code_path.parent.mkdir(parents=True, exist_ok=True)
        code_path.write_text(code)
        logger.info(f"Saving Code to {code_path}")

    async def run(self, template_func: str, source_code: str) -> str:
        """Run CloneFunction action.

        :param template_func: The template function to clone.
        :type template_func: str
        :param source_code: The source code to clone.
        :type source_code: str
        :return: The cloned function code.
        :rtype: str
        """
        prompt = CLONE_PROMPT.format(
            source_code=source_code, template_func=template_func
        )
        logger.info(f"query for CloneFunction: \n {prompt}")
        code = await self.write_code(prompt)
        logger.info(f"CloneFunction code is \n {highlight(code)}")
        return code


def run_function_code(func_code: str, func_name: str, *args, **kwargs):
    """Run function code from string code.

    :param func_code: The function code.
    :type func_code: str
    :param func_name: The function name.
    :type func_name: str
    :return: The function result and error message.
    :rtype: tuple
    """
    try:
        locals_ = {}
        exec(func_code, locals_)
        func = locals_[func_name]
        return func(*args, **kwargs), ""
    except Exception:
        return "", traceback.format_exc()


def run_function_script(code_script_path: str, func_name: str, *args, **kwargs):
    """Run function code from script.

    :param code_script_path: The path to the code script.
    :type code_script_path: str
    :param func_name: The function name.
    :type func_name: str
    :return: The function result and error message.
    :rtype: tuple
    """
    if isinstance(code_script_path, str):
        code_path = Path(code_script_path)
    code = code_path.read_text(encoding="utf-8")
    return run_function_code(code, func_name, *args, **kwargs)