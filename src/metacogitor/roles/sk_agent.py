"""SkAgent role implementation."""
# -*- coding: utf-8 -*-

from semantic_kernel.planning import SequentialPlanner
from semantic_kernel.planning.action_planner.action_planner import ActionPlanner
from semantic_kernel.planning.basic_planner import BasicPlanner

from metacogitor.actions import BossRequirement
from metacogitor.actions.execute_task import ExecuteTask
from metacogitor.logs import logger
from metacogitor.roles import Role
from metacogitor.schema import Message
from metacogitor.utils.make_sk_kernel import make_sk_kernel


class SkAgent(Role):
    """Represents an SkAgent implemented using semantic kernel

    Attributes:
        name (str): Name of the SkAgent.
        profile (str): Role profile, default is 'sk_agent'.
        goal (str): Goal of the SkAgent.
        constraints (str): Constraints for the SkAgent.
    """

    def __init__(
        self,
        name: str = "Sunshine",
        profile: str = "sk_agent",
        goal: str = "Execute task based on passed in task description",
        constraints: str = "",
        planner_cls=BasicPlanner,
    ) -> None:
        """Initializes the Engineer role with given attributes.

        :param name: Name of the SkAgent.
        :type name: str
        :param profile: Role profile, default is 'sk_agent'.
        :type profile: str
        :param goal: Goal of the SkAgent.
        :type goal: str
        :param constraints: Constraints for the SkAgent.
        :type constraints: str
        """

        super().__init__(name, profile, goal, constraints)
        self._init_actions([ExecuteTask()])
        self._watch([BossRequirement])
        self.kernel = make_sk_kernel()

        # how funny the interface is inconsistent
        if planner_cls == BasicPlanner:
            self.planner = planner_cls()
        elif planner_cls in [SequentialPlanner, ActionPlanner]:
            self.planner = planner_cls(self.kernel)
        else:
            raise f"Unsupported planner of type {planner_cls}"

        self.import_semantic_skill_from_directory = (
            self.kernel.import_semantic_skill_from_directory
        )
        self.import_skill = self.kernel.import_skill

    async def _think(self) -> None:
        """Think about the task and generate a plan

        :return: None
        :rtype: None
        """

        self._set_state(0)
        # how funny the interface is inconsistent
        if isinstance(self.planner, BasicPlanner):
            self.plan = await self.planner.create_plan_async(
                self._rc.important_memory[-1].content, self.kernel
            )
            logger.info(self.plan.generated_plan)
        elif any(
            isinstance(self.planner, cls) for cls in [SequentialPlanner, ActionPlanner]
        ):
            self.plan = await self.planner.create_plan_async(
                self._rc.important_memory[-1].content
            )

    async def _act(self) -> Message:
        """Performs the action in a single process.

        :return: The message to send to the user.
        :rtype: Message
        """

        # how funny the interface is inconsistent
        if isinstance(self.planner, BasicPlanner):
            result = await self.planner.execute_plan_async(self.plan, self.kernel)
        elif any(
            isinstance(self.planner, cls) for cls in [SequentialPlanner, ActionPlanner]
        ):
            result = (await self.plan.invoke_async()).result
        logger.info(result)

        msg = Message(content=result, role=self.profile, cause_by=type(self._rc.todo))
        self._rc.memory.add(msg)
        # logger.debug(f"{response}")
        return msg
