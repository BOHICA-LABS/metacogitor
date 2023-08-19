# -*- coding: utf-8 -*-
"""
@Time    : 2023/8/18 23:08
@Author  : Joshua Magady
@File    : cost_manager.py
@Desc    : This defines the Cost Manager Classes.
"""

from typing import NamedTuple
from metacogitor.utils.singleton import Singleton
from metacogitor.utils.token_counter import (
    TOKEN_COSTS,
    count_message_tokens,
    count_string_tokens,
    get_max_completion_tokens,
)
from metacogitor.logs import logger
from metacogitor.config import CONFIG

__ALL__ = ["Costs", "CostManager"]


class Costs(NamedTuple):
    """Costs class to track prompt tokens, completion tokens, total cost and budget.

    This class is a named tuple that stores information about the costs
    incurred during conversational interactions with the AI assistant.
    It can be used to track usage and manage budgets.

    Attributes:
        total_prompt_tokens (int): The total number of prompt tokens used.
        total_completion_tokens (int): The total number of completion tokens generated.
        total_cost (float): The total cost accrued so far.
        total_budget (float): The maximum budget allowed.
    """

    total_prompt_tokens: int
    """The total number of prompt tokens used."""

    total_completion_tokens: int
    """The total number of completion tokens generated."""

    total_cost: float
    """The total cost accrued so far."""

    total_budget: float
    """The maximum budget allowed."""


class CostManager(metaclass=Singleton):
    """Manages costs incurred from using the AI assistant.

    This singleton class tracks the number of tokens, costs,
    and budget when making API calls to the AI assistant.
    """

    def __init__(self):
        self.total_prompt_tokens = 0
        """Total number of prompt tokens used."""

        self.total_completion_tokens = 0
        """Total number of completion tokens generated."""

        self.total_cost = 0
        """Total cost accrued so far."""

        self.total_budget = 0
        """Total budget allowed."""

    def update_cost(self, prompt_tokens, completion_tokens, model):
        """Update the total cost, prompt tokens, and completion tokens.

        Args:
            prompt_tokens (int): Number of prompt tokens used.
            completion_tokens (int): Number of completion tokens generated.
            model (str): The AI model used.
        """

        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        cost = (
            prompt_tokens * TOKEN_COSTS[model]["prompt"]
            + completion_tokens * TOKEN_COSTS[model]["completion"]
        ) / 1000
        self.total_cost += cost
        logger.info(
            f"Total running cost: ${self.total_cost:.3f} | Max budget: ${CONFIG.max_budget:.3f} | "
            f"Current cost: ${cost:.3f}, prompt_tokens: {prompt_tokens}, completion_tokens: {completion_tokens}"
        )
        CONFIG.total_cost = self.total_cost

    def get_total_prompt_tokens(self):
        """Get the total number of prompt tokens used.

        Returns:
            int: Total prompt tokens.
        """

        return self.total_prompt_tokens

    def get_total_completion_tokens(self):
        """Get the total number of completion tokens generated.

        Returns:
            int: Total completion tokens.
        """

        return self.total_completion_tokens

    def get_total_cost(self):
        """Get the total cost accrued so far.

        Returns:
            float: The total cost.
        """

        return self.total_cost

    def get_costs(self) -> Costs:
        """Get Costs tuple with current token, cost and budget info.

        Returns:
            Costs: Named tuple instance holding cost info.
        """

        return Costs(
            self.total_prompt_tokens,
            self.total_completion_tokens,
            self.total_cost,
            self.total_budget,
        )
