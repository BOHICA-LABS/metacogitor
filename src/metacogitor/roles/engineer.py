"""Engineer role Module."""
# -*- coding: utf-8 -*-

import asyncio
import shutil
from collections import OrderedDict
from pathlib import Path

from metacogitor.actions import WriteCode, WriteCodeReview, WriteDesign, WriteTasks
from metacogitor.const import WORKSPACE_ROOT
from metacogitor.logs import logger
from metacogitor.roles import Role
from metacogitor.schema import Message
from metacogitor.utils.common import CodeParser
from metacogitor.utils.special_tokens import FILENAME_CODE_SEP, MSG_SEP


async def gather_ordered_k(coros, k) -> list:
    """Gather coroutines in order of completion.

    :param coros: List of coroutines.
    :param k: Number of coroutines to run concurrently.
    :return: List of results.
    """

    tasks = OrderedDict()
    results = [None] * len(coros)
    done_queue = asyncio.Queue()

    for i, coro in enumerate(coros):
        if len(tasks) >= k:
            done, _ = await asyncio.wait(
                tasks.keys(), return_when=asyncio.FIRST_COMPLETED
            )
            for task in done:
                index = tasks.pop(task)
                await done_queue.put((index, task.result()))
        task = asyncio.create_task(coro)
        tasks[task] = i

    if tasks:
        done, _ = await asyncio.wait(tasks.keys())
        for task in done:
            index = tasks[task]
            await done_queue.put((index, task.result()))

    while not done_queue.empty():
        index, result = await done_queue.get()
        results[index] = result

    return results


class Engineer(Role):
    """
    Represents an Engineer role responsible for writing and possibly reviewing code.

    Attributes:
        name (str): Name of the engineer.
        profile (str): Role profile, default is 'Engineer'.
        goal (str): Goal of the engineer.
        constraints (str): Constraints for the engineer.
        n_borg (int): Number of borgs.
        use_code_review (bool): Whether to use code review.
        todos (list): List of tasks.
    """

    def __init__(
        self,
        name: str = "Alex",
        profile: str = "Engineer",
        goal: str = "Write elegant, readable, extensible, efficient code",
        constraints: str = "The code should conform to standards like PEP8 and be modular and maintainable",
        n_borg: int = 1,
        use_code_review: bool = False,
    ) -> None:
        """Initializes the Engineer role with given attributes.

        :param name: Name of the engineer, defaults to "Alex"
        :type name: str, optional
        :param profile: Role profile, defaults to "Engineer"
        :type profile: str, optional
        :param goal: Goal of the engineer, defaults to "Write elegant, readable, extensible, efficient code"
        :type goal: str, optional
        :param constraints: Constraints for the engineer, defaults to "The code should conform to standards like PEP8 and be modular and maintainable"
        :type constraints: str, optional
        :param n_borg: Number of borgs, defaults to 1
        :type n_borg: int, optional
        :param use_code_review: Whether to use code review, defaults to False
        :type use_code_review: bool, optional
        """

        super().__init__(name, profile, goal, constraints)
        self._init_actions([WriteCode])
        self.use_code_review = use_code_review
        if self.use_code_review:
            self._init_actions([WriteCode, WriteCodeReview])
        self._watch([WriteTasks])
        self.todos = []
        self.n_borg = n_borg

    @classmethod
    def parse_tasks(self, task_msg: Message) -> list[str]:
        """Parse tasks from the given message.

        :param task_msg: The message to parse tasks from.
        :type task_msg: Message
        :return: List of tasks.
        :rtype: list[str]
        """

        if task_msg.instruct_content:
            return task_msg.instruct_content.dict().get("Task list")
        return CodeParser.parse_file_list(block="Task list", text=task_msg.content)

    @classmethod
    def parse_code(self, code_text: str) -> str:
        """Parse code from the given text.

        :param code_text: The text to parse code from.
        :type code_text: str
        :return: The parsed code.
        :rtype: str
        """

        return CodeParser.parse_code(block="", text=code_text)

    @classmethod
    def parse_workspace(cls, system_design_msg: Message) -> str:
        """Parse workspace from the given message.

        :param system_design_msg: The message to parse workspace from.
        :type system_design_msg: Message
        :return: The parsed workspace.
        :rtype: str
        """

        if system_design_msg.instruct_content:
            return (
                system_design_msg.instruct_content.dict()
                .get("Python package name")
                .strip()
                .strip("'")
                .strip('"')
            )
        return CodeParser.parse_str(
            block="Python package name", text=system_design_msg.content
        )

    def get_workspace(self) -> Path:
        """Get the workspace for writing code.

        :return: The workspace for writing code.
        :rtype: Path
        """

        msg = self._rc.memory.get_by_action(WriteDesign)[-1]
        if not msg:
            return WORKSPACE_ROOT / "src"
        workspace = self.parse_workspace(msg)
        # Codes are written in workspace/{package_name}/{package_name}
        return WORKSPACE_ROOT / workspace / workspace

    def recreate_workspace(self):
        """Recreate the workspace for writing code.

        :return: None
        :rtype: None
        """

        workspace = self.get_workspace()
        try:
            shutil.rmtree(workspace)
        except FileNotFoundError:
            pass  # The folder does not exist, but we don't care
        workspace.mkdir(parents=True, exist_ok=True)

    def write_file(self, filename: str, code: str):
        """Write the given code to the given file.

        :param filename: The name of the file to write to.
        :type filename: str
        :param code: The code to write.
        :type code: str
        :return: The file path.
        :rtype: Path
        """

        workspace = self.get_workspace()
        filename = filename.replace('"', "").replace("\n", "")
        file = workspace / filename
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(code)
        return file

    def recv(self, message: Message) -> None:
        """Receive a message.

        :param message: The message to receive.
        :type message: Message
        :return: None
        :rtype: None
        """

        self._rc.memory.add(message)
        if message in self._rc.important_memory:
            self.todos = self.parse_tasks(message)

    async def _act_mp(self) -> Message:
        """Act in multi-process mode.

        :return: The message to send.
        :rtype: Message
        """

        # self.recreate_workspace()
        todo_coros = []
        for todo in self.todos:
            todo_coro = WriteCode().run(
                context=self._rc.memory.get_by_actions([WriteTasks, WriteDesign]),
                filename=todo,
            )
            todo_coros.append(todo_coro)

        rsps = await gather_ordered_k(todo_coros, self.n_borg)
        for todo, code_rsp in zip(self.todos, rsps):
            _ = self.parse_code(code_rsp)
            logger.info(todo)
            logger.info(code_rsp)
            # self.write_file(todo, code)
            msg = Message(
                content=code_rsp, role=self.profile, cause_by=type(self._rc.todo)
            )
            self._rc.memory.add(msg)
            del self.todos[0]

        logger.info(f"Done {self.get_workspace()} generating.")
        msg = Message(
            content="all done.", role=self.profile, cause_by=type(self._rc.todo)
        )
        return msg

    async def _act_sp(self) -> Message:
        """Act in single-process mode.

        :return: The message to send.
        :rtype: Message
        """

        code_msg_all = (
            []
        )  # gather all code info, will pass to qa_engineer for tests later
        for todo in self.todos:
            code = await WriteCode().run(context=self._rc.history, filename=todo)
            # logger.info(todo)
            # logger.info(code_rsp)
            # code = self.parse_code(code_rsp)
            file_path = self.write_file(todo, code)
            msg = Message(content=code, role=self.profile, cause_by=type(self._rc.todo))
            self._rc.memory.add(msg)

            code_msg = todo + FILENAME_CODE_SEP + str(file_path)
            code_msg_all.append(code_msg)

        logger.info(f"Done {self.get_workspace()} generating.")
        msg = Message(
            content=MSG_SEP.join(code_msg_all),
            role=self.profile,
            cause_by=type(self._rc.todo),
            send_to="QaEngineer",
        )
        return msg

    async def _act_sp_precision(self) -> Message:
        """Act in single-process mode with code review.

        :return: The message to send.
        :rtype: Message
        """

        code_msg_all = (
            []
        )  # gather all code info, will pass to qa_engineer for tests later
        for todo in self.todos:
            """
            # Select essential information from the historical data to reduce the length of the prompt (summarized from human experience):
            1. All from Architect
            2. All from ProjectManager
            3. Do we need other codes (currently needed)?
            TODO: The goal is not to need it. After clear task decomposition, based on the design idea, you should be able to write a single file without needing other codes. If you can't, it means you need a clearer definition. This is the key to writing longer code.
            """
            context = []
            msg = self._rc.memory.get_by_actions([WriteDesign, WriteTasks, WriteCode])
            for m in msg:
                context.append(m.content)
            context_str = "\n".join(context)
            # Write code
            code = await WriteCode().run(context=context_str, filename=todo)
            # Code review
            if self.use_code_review:
                try:
                    rewrite_code = await WriteCodeReview().run(
                        context=context_str, code=code, filename=todo
                    )
                    code = rewrite_code
                except Exception as e:
                    logger.error("code review failed!", e)
                    pass
            file_path = self.write_file(todo, code)
            msg = Message(content=code, role=self.profile, cause_by=WriteCode)
            self._rc.memory.add(msg)

            code_msg = todo + FILENAME_CODE_SEP + str(file_path)
            code_msg_all.append(code_msg)

        logger.info(f"Done {self.get_workspace()} generating.")
        msg = Message(
            content=MSG_SEP.join(code_msg_all),
            role=self.profile,
            cause_by=type(self._rc.todo),
            send_to="QaEngineer",
        )
        return msg

    async def _act(self) -> Message:
        """Determines the mode of action based on whether code review is used.

        :return: The message to send.
        :rtype: Message
        """

        if self.use_code_review:
            return await self._act_sp_precision()
        return await self._act_sp()
