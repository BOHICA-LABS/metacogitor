"""Write test action."""
# -*- coding: utf-8 -*-

from metacogitor.actions.action import Action
from metacogitor.logs import logger
from metacogitor.utils.common import CodeParser

PROMPT_TEMPLATE = """
NOTICE
1. Role: You are a QA engineer; the main goal is to design, develop, and execute PEP8 compliant, well-structured, maintainable test cases and scripts for Python 3.9. Your focus should be on ensuring the product quality of the entire project through systematic testing.
2. Requirement: Based on the context, develop a comprehensive test suite that adequately covers all relevant aspects of the code file under review. Your test suite will be part of the overall project QA, so please develop complete, robust, and reusable test cases.
3. Attention1: Use '##' to split sections, not '#', and '## <SECTION_NAME>' SHOULD WRITE BEFORE the test case or script.
4. Attention2: If there are any settings in your tests, ALWAYS SET A DEFAULT VALUE, ALWAYS USE STRONG TYPE AND EXPLICIT VARIABLE.
5. Attention3: YOU MUST FOLLOW "Data structures and interface definitions". DO NOT CHANGE ANY DESIGN. Make sure your tests respect the existing design and ensure its validity.
6. Think before writing: What should be tested and validated in this document? What edge cases could exist? What might fail?
7. CAREFULLY CHECK THAT YOU DON'T MISS ANY NECESSARY TEST CASES/SCRIPTS IN THIS FILE.
Attention: Use '##' to split sections, not '#', and '## <SECTION_NAME>' SHOULD WRITE BEFORE the test case or script and triple quotes.
-----
## Given the following code, please write appropriate test cases using Python's unittest framework to verify the correctness and robustness of this code:
```python
{code_to_test}
```
Note that the code to test is at {source_file_path}, we will put your test code at {workspace}/tests/{test_file_name}, and run your test code from {workspace},
you should correctly import the necessary classes based on these file locations!
## {test_file_name}: Write test code with triple quoto. Do your best to implement THIS ONLY ONE FILE.
"""


class WriteTest(Action):
    """Write test action."""

    def __init__(self, name="WriteTest", context=None, llm=None):
        """Initialize the write test handler.

        :param name: The name of the action.
        :type name: str
        :param context: The context for the action.
        :type context: str
        :param llm: The language model to use for the action.
        :type llm: LanguageModel
        """
        super().__init__(name, context, llm)

    async def write_code(self, prompt):
        """Write test code for the given code to test.

        :param prompt: The prompt for writing test code.
        """

        code_rsp = await self._aask(prompt)

        try:
            code = CodeParser.parse_code(block="", text=code_rsp)
        except Exception:
            # Handle the exception if needed
            logger.error(f"Can't parse the code: {code_rsp}")

            # Return code_rsp in case of an exception, assuming llm just returns code as it is and doesn't wrap it inside ```
            code = code_rsp
        return code

    async def run(self, code_to_test, test_file_name, source_file_path, workspace):
        """Write test code for the given code to test.

        :param code_to_test: The code to test.
        :type code_to_test: str
        :param test_file_name: The name of the test file.
        :type test_file_name: str
        :param source_file_path: The path to the source file.
        :type source_file_path: str
        :param workspace: The path to the workspace.
        :type workspace: str
        :return: The test code.
        :rtype: str
        """
        prompt = PROMPT_TEMPLATE.format(
            code_to_test=code_to_test,
            test_file_name=test_file_name,
            source_file_path=source_file_path,
            workspace=workspace,
        )
        code = await self.write_code(prompt)
        return code