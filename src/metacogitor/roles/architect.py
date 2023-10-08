"""Architect role module."""
# -*- coding: utf-8 -*-


from metacogitor.actions import WritePRD
from metacogitor.actions.design_api import WriteDesign
from metacogitor.roles import Role


class Architect(Role):
    """
    Represents an Architect role in a software development process.

    Attributes:
        name (str): Name of the architect.
        profile (str): Role profile, default is 'Architect'.
        goal (str): Primary goal or responsibility of the architect.
        constraints (str): Constraints or guidelines for the architect.
    """

    def __init__(
        self,
        name: str = "Bob",
        profile: str = "Architect",
        goal: str = "Design a concise, usable, complete python system",
        constraints: str = "Try to specify good open source tools as much as possible",
    ) -> None:
        """Initializes the Architect with given attributes.

        :param name: Name of the architect, defaults to "Bob"
        :type name: str, optional
        :param profile: Role profile, defaults to "Architect"
        :type profile: str, optional
        :param goal: Primary goal or responsibility of the architect, defaults to "Design a concise, usable, complete python system"
        :type goal: str, optional
        :param constraints: Constraints or guidelines for the architect, defaults to "Try to specify good open source tools as much as possible"
        :type constraints: str, optional
        """
        super().__init__(name, profile, goal, constraints)

        # Initialize actions specific to the Architect role
        self._init_actions([WriteDesign])

        # Set events or actions the Architect should watch or be aware of
        self._watch({WritePRD})
