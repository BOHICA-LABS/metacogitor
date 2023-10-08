"""Project Manager role module."""
# -*- coding: utf-8 -*-

from metacogitor.actions import WriteTasks
from metacogitor.actions.design_api import WriteDesign
from metacogitor.roles import Role


class ProjectManager(Role):
    """
    Represents a Project Manager role responsible for overseeing project execution and team efficiency.

    Attributes:
        name (str): Name of the project manager.
        profile (str): Role profile, default is 'Project Manager'.
        goal (str): Goal of the project manager.
        constraints (str): Constraints or limitations for the project manager.
    """

    def __init__(
        self,
        name: str = "Eve",
        profile: str = "Project Manager",
        goal: str = "Improve team efficiency and deliver with quality and quantity",
        constraints: str = "",
    ) -> None:
        """Initializes the ProjectManager role with given attributes.

        :param name: Name of the project manager.
        :type name: str
        :param profile: Role profile.
        :type profile: str
        :param goal: Goal of the project manager.
        :type goal: str
        :param constraints: Constraints or limitations for the project manager.
        :type constraints: str
        """
        super().__init__(name, profile, goal, constraints)
        self._init_actions([WriteTasks])
        self._watch([WriteDesign])
