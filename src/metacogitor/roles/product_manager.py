"""Product Manager role module."""
# -*- coding: utf-8 -*-

from metacogitor.actions import BossRequirement, WritePRD
from metacogitor.roles import Role


class ProductManager(Role):
    """
    Represents a Product Manager role responsible for product development and management.

    Attributes:
        name (str): Name of the product manager.
        profile (str): Role profile, default is 'Product Manager'.
        goal (str): Goal of the product manager.
        constraints (str): Constraints or limitations for the product manager.
    """

    def __init__(
        self,
        name: str = "Alice",
        profile: str = "Product Manager",
        goal: str = "Efficiently create a successful product",
        constraints: str = "",
    ) -> None:
        """Initializes the ProductManager role with given attributes.

        :param name (str): Name of the product manager.
        :param profile (str): Role profile.
        :param goal (str): Goal of the product manager.
        :param constraints (str): Constraints or limitations for the product manager.
        """

        super().__init__(name, profile, goal, constraints)
        self._init_actions([WritePRD])
        self._watch([BossRequirement])
