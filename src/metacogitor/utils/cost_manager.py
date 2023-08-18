# -*- coding: utf-8 -*-
"""
@Time    : 2023/8/18 23:08
@Author  : Joshua Magady
@File    : cost_manager.py
@Desc    : This defines the Cost Manager Classes.
"""

from typing import NamedTuple


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
