"""Software Company Module"""
# -*- coding: utf-8 -*-

from pydantic import BaseModel, Field

from metacogitor.actions import BossRequirement
from metacogitor.config import CONFIG
from metacogitor.environment import Environment
from metacogitor.logs import logger
from metacogitor.roles import Role
from metacogitor.schema import Message
from metacogitor.utils.common import NoMoneyException


class SoftwareCompany(BaseModel):
    """Software Company Class

    Software Company: Possesses a team, SOP (Standard Operating Procedures), and a platform for instant messaging,
    dedicated to writing executable code.

    Attributes:
        environment (Environment): The environment that the company operates in.
        investment (float): The amount of money invested in the company.
        idea (str): The idea that the company is working on.
    """

    environment: Environment = Field(default_factory=Environment)
    investment: float = Field(default=10.0)
    idea: str = Field(default="")

    class Config:
        """Pydantic Config"""

        arbitrary_types_allowed = True

    def hire(self, roles: list[Role]):
        """Hire roles to cooperate

        :param roles: list of roles
        :type roles: list[Role]
        """
        self.environment.add_roles(roles)

    def invest(self, investment: float):
        """Invest company. raise NoMoneyException when exceed max_budget.

        :param investment: amount of money
        :type investment: float
        """
        self.investment = investment
        CONFIG.max_budget = investment
        logger.info(f"Investment: ${investment}.")

    def _check_balance(self):
        """Check if the company has enough money to run.

        :raises NoMoneyException: raise when exceed max_budget
        """

        if CONFIG.total_cost > CONFIG.max_budget:
            raise NoMoneyException(
                CONFIG.total_cost, f"Insufficient funds: {CONFIG.max_budget}"
            )

    def start_project(self, idea):
        """Start a project from publishing boss requirement.

        :param idea: idea to start
        :type idea: str
        """

        self.idea = idea
        self.environment.publish_message(
            Message(role="BOSS", content=idea, cause_by=BossRequirement)
        )

    def _save(self):
        """Save company status"""

        logger.info(self.json())

    async def run(self, n_round=3):
        """Run company until target round or no money

        :param n_round: number of round to run, defaults to 3
        :type n_round: int, optional
        :raises NoMoneyException: raise when exceed max_budget
        :return: history of the environment
        :rtype: list[Message]
        """

        while n_round > 0:
            # self._save()
            n_round -= 1
            logger.debug(f"{n_round=}")
            self._check_balance()
            await self.environment.run()
        return self.environment.history
