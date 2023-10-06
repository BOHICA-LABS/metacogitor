"""Write code action."""
# -*- coding: utf-8 -*-

from metacogitor.actions import WriteDesign
from metacogitor.actions.action import Action
from metacogitor.const import WORKSPACE_ROOT
from metacogitor.logs import logger
from metacogitor.schema import Message
from metacogitor.utils.common import CodeParser
from tenacity import retry, stop_after_attempt, wait_fixed

PROMPT_TEMPLATE = """
NOTICE
Role: You are a professional engineer; the main goal is to write PEP8 compliant, elegant, modular, easy to read and maintain Python 3.9 code (but you can also use other programming language)
ATTENTION: Use '##' to SPLIT SECTIONS, not '#'. Output format carefully referenced "Format example".

## Code: {filename} Write code with triple quoto, based on the following list and context.
1. Do your best to implement THIS ONLY ONE FILE. ONLY USE EXISTING API. IF NO API, IMPLEMENT IT.
2. Requirement: Based on the context, implement one following code file, note to return only in code form, your code will be part of the entire project, so please implement complete, reliable, reusable code snippets
3. Attention1: If there is any setting, ALWAYS SET A DEFAULT VALUE, ALWAYS USE STRONG TYPE AND EXPLICIT VARIABLE.
4. Attention2: YOU MUST FOLLOW "Data structures and interface definitions". DONT CHANGE ANY DESIGN.
5. Think before writing: What should be implemented and provided in this document?
6. CAREFULLY CHECK THAT YOU DONT MISS ANY NECESSARY CLASS/FUNCTION IN THIS FILE.
7. Do not use public member functions that do not exist in your design.

-----
# Context
{context}
-----
## Format example
-----
## Code: {filename}
```python
## {filename}
...
```
-----
"""


class WriteCode(Action):
    """Write code action."""

    def __init__(self, name="WriteCode", context: list[Message] = None, llm=None):
        """Initialize WriteCode action.

        :param name: Action name, defaults to "WriteCode"
        :type name: str, optional
        :param context: Context, defaults to None
        :type context: list[Message], optional
        :param llm: Language model, defaults to None
        :type llm: [type], optional
        """
        super().__init__(name, context, llm)

    def _is_invalid(self, filename):
        """Check if the filename is invalid.

        :param filename: Filename
        :type filename: str
        :return: True if the filename is invalid, False otherwise
        :rtype: bool
        """

        return any(i in filename for i in ["mp3", "wav"])

    def _save(self, context, filename, code):
        """Save the code to a file.

        :param context: Context
        :type context: list[Message]
        :param filename: Filename
        :type filename: str
        :param code: Code
        :type code: str
        """

        # logger.info(filename)
        # logger.info(code_rsp)
        if self._is_invalid(filename):
            return

        design = [i for i in context if i.cause_by == WriteDesign][0]

        ws_name = CodeParser.parse_str(block="Python package name", text=design.content)
        ws_path = WORKSPACE_ROOT / ws_name
        if f"{ws_name}/" not in filename and all(
            i not in filename for i in ["requirements.txt", ".md"]
        ):
            ws_path = ws_path / ws_name
        code_path = ws_path / filename
        code_path.parent.mkdir(parents=True, exist_ok=True)
        code_path.write_text(code)
        logger.info(f"Saving Code to {code_path}")

    @retry(stop=stop_after_attempt(2), wait=wait_fixed(1))
    async def write_code(self, prompt):
        """Write code.

        :param prompt: Prompt
        :type prompt: str
        :return: Code
        :rtype: str
        """
        code_rsp = await self._aask(prompt)
        code = CodeParser.parse_code(block="", text=code_rsp)
        return code

    async def run(self, context, filename):
        """Run the action.

        :param context: Context
        :type context: list[Message]
        :param filename: Filename
        :type filename: str
        :return: Code
        :rtype: str
        """
        prompt = PROMPT_TEMPLATE.format(context=context, filename=filename)
        logger.info(f"Writing {filename}..")
        code = await self.write_code(prompt)
        # code_rsp = await self._aask_v1(prompt, "code_rsp", OUTPUT_MAPPING)
        # self._save(context, filename, code)
        return code
