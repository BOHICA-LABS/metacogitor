"""QA Engineer role, responsible for writing tests, running tests, debugging errors, etc."""
# -*- coding: utf-8 -*-

import os
from pathlib import Path

from metacogitor.actions import (
    DebugError,
    RunCode,
    WriteCode,
    WriteCodeReview,
    WriteDesign,
    WriteTest,
)
from metacogitor.const import WORKSPACE_ROOT
from metacogitor.logs import logger
from metacogitor.roles import Role
from metacogitor.schema import Message
from metacogitor.utils.common import CodeParser, parse_recipient
from metacogitor.utils.special_tokens import FILENAME_CODE_SEP, MSG_SEP


class QaEngineer(Role):
    """QA Engineer role, responsible for writing tests, running tests, debugging errors, etc.

    Attributes:
        name (str): Name of the role.
        profile (str): Profile of the role.
        goal (str): Goal of the role.
        constraints (str): Constraints of the role.
        test_round_allowed (int): Number of rounds of tests allowed.
    """

    def __init__(
        self,
        name="Edward",
        profile="QaEngineer",
        goal="Write comprehensive and robust tests to ensure codes will work as expected without bugs",
        constraints="The test code you write should conform to code standard like PEP8, be modular, easy to read and maintain",
        test_round_allowed=5,
    ):
        """Initialize the role.

        :param name: Name of the role.
        :type name: str
        :param profile: Profile of the role.
        :type profile: str
        :param goal: Goal of the role.
        :type goal: str
        :param constraints: Constraints of the role.
        :type constraints: str
        :param test_round_allowed: Number of rounds of tests allowed.
        :type test_round_allowed: int
        """

        super().__init__(name, profile, goal, constraints)
        self._init_actions(
            [WriteTest]
        )  # FIXME: a bit hack here, only init one action to circumvent _think() logic, will overwrite _think() in future updates
        self._watch([WriteCode, WriteCodeReview, WriteTest, RunCode, DebugError])
        self.test_round = 0
        self.test_round_allowed = test_round_allowed

    @classmethod
    def parse_workspace(cls, system_design_msg: Message) -> str:
        """Parse workspace from system design message.

        :param system_design_msg: System design message.
        :type system_design_msg: Message
        :return: Workspace.
        :rtype: str
        """

        if system_design_msg.instruct_content:
            return system_design_msg.instruct_content.dict().get("Python package name")
        return CodeParser.parse_str(
            block="Python package name", text=system_design_msg.content
        )

    def get_workspace(self, return_proj_dir=True) -> Path:
        """Get workspace.

        :param return_proj_dir: Whether to return project directory or development codes directory, defaults to True
        :type return_proj_dir: bool, optional
        :return: Workspace.
        :rtype: Path
        """

        msg = self._rc.memory.get_by_action(WriteDesign)[-1]
        if not msg:
            return WORKSPACE_ROOT / "src"
        workspace = self.parse_workspace(msg)
        # project directory: workspace/{package_name}, which contains package source code folder, tests folder, resources folder, etc.
        if return_proj_dir:
            return WORKSPACE_ROOT / workspace
        # development codes directory: workspace/{package_name}/{package_name}
        return WORKSPACE_ROOT / workspace / workspace

    def write_file(self, filename: str, code: str):
        """Write file.

        :param filename: File name.
        :type filename: str
        :param code: Code.
        :type code: str
        """

        workspace = self.get_workspace() / "tests"
        file = workspace / filename
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(code)

    async def _write_test(self, message: Message) -> None:
        """Write test.

        :param message: Message.
        :type message: Message
        """

        code_msgs = message.content.split(MSG_SEP)
        # result_msg_all = []
        for code_msg in code_msgs:
            # write tests
            file_name, file_path = code_msg.split(FILENAME_CODE_SEP)
            code_to_test = open(file_path, "r").read()
            if "test" in file_name:
                continue  # Engineer might write some test files, skip testing a test file
            test_file_name = "test_" + file_name
            test_file_path = self.get_workspace() / "tests" / test_file_name
            logger.info(f"Writing {test_file_name}..")
            test_code = await WriteTest().run(
                code_to_test=code_to_test,
                test_file_name=test_file_name,
                # source_file_name=file_name,
                source_file_path=file_path,
                workspace=self.get_workspace(),
            )
            self.write_file(test_file_name, test_code)

            # prepare context for run tests in next round
            command = ["python", f"tests/{test_file_name}"]
            file_info = {
                "file_name": file_name,
                "file_path": str(file_path),
                "test_file_name": test_file_name,
                "test_file_path": str(test_file_path),
                "command": command,
            }
            msg = Message(
                content=str(file_info),
                role=self.profile,
                cause_by=WriteTest,
                sent_from=self.profile,
                send_to=self.profile,
            )
            self._publish_message(msg)

        logger.info(f"Done {self.get_workspace()}/tests generating.")

    async def _run_code(self, msg):
        """Run code.

        :param msg: Message.
        :type msg: Message
        """

        file_info = eval(msg.content)
        development_file_path = file_info["file_path"]
        test_file_path = file_info["test_file_path"]
        if not os.path.exists(development_file_path) or not os.path.exists(
            test_file_path
        ):
            return

        development_code = open(development_file_path, "r").read()
        test_code = open(test_file_path, "r").read()
        proj_dir = self.get_workspace()
        development_code_dir = self.get_workspace(return_proj_dir=False)

        result_msg = await RunCode().run(
            mode="script",
            code=development_code,
            code_file_name=file_info["file_name"],
            test_code=test_code,
            test_file_name=file_info["test_file_name"],
            command=file_info["command"],
            working_directory=proj_dir,  # workspace/package_name, will run tests/test_xxx.py here
            additional_python_paths=[
                development_code_dir
            ],  # workspace/package_name/package_name,
            # import statement inside package code needs this
        )

        recipient = parse_recipient(
            result_msg
        )  # the recipient might be Engineer or myself
        content = str(file_info) + FILENAME_CODE_SEP + result_msg
        msg = Message(
            content=content,
            role=self.profile,
            cause_by=RunCode,
            sent_from=self.profile,
            send_to=recipient,
        )
        self._publish_message(msg)

    async def _debug_error(self, msg):
        """Debug error.

        :param msg: Message.
        :type msg: Message
        """

        file_info, context = msg.content.split(FILENAME_CODE_SEP)
        file_name, code = await DebugError().run(context)
        if file_name:
            self.write_file(file_name, code)
            recipient = (
                msg.sent_from
            )  # send back to the one who ran the code for another run, might be one's self
            msg = Message(
                content=file_info,
                role=self.profile,
                cause_by=DebugError,
                sent_from=self.profile,
                send_to=recipient,
            )
            self._publish_message(msg)

    async def _observe(self) -> int:
        """Observe.

        :return: Number of observed messages.
        :rtype: int
        """

        await super()._observe()
        self._rc.news = [
            msg for msg in self._rc.news if msg.send_to == self.profile
        ]  # only relevant msgs count as observed news
        return len(self._rc.news)

    async def _act(self) -> Message:
        """Act.

        :return: Result message.
        :rtype: Message
        """

        if self.test_round > self.test_round_allowed:
            result_msg = Message(
                content=f"Exceeding {self.test_round_allowed} rounds of tests, skip (writing code counts as a round, too)",
                role=self.profile,
                cause_by=WriteTest,
                sent_from=self.profile,
                send_to="",
            )
            return result_msg

        for msg in self._rc.news:
            # Decide what to do based on observed msg type, currently defined by human,
            # might potentially be moved to _think, that is, let the agent decides for itself
            if msg.cause_by in [WriteCode, WriteCodeReview]:
                # engineer wrote a code, time to write a test for it
                await self._write_test(msg)
            elif msg.cause_by in [WriteTest, DebugError]:
                # I wrote or debugged my test code, time to run it
                await self._run_code(msg)
            elif msg.cause_by == RunCode:
                # I ran my test code, time to fix bugs, if any
                await self._debug_error(msg)
        self.test_round += 1
        result_msg = Message(
            content=f"Round {self.test_round} of tests done",
            role=self.profile,
            cause_by=WriteTest,
            sent_from=self.profile,
            send_to="",
        )
        return result_msg
