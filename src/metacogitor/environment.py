#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
from typing import Iterable

from pydantic import BaseModel, Field

from metacogitor.memory import Memory
from metacogitor.roles import Role
from metacogitor.schema import Message


class Environment(BaseModel):
    """Environment

    hosting a batch of roles, roles can publish messages to the environment, and can be observed by other roles

    Attributes:
        roles (dict[str, Role]): all roles in the environment
        memory (Memory): the memory of the environment
        history (str): the history of the environment
    """

    roles: dict[str, Role] = Field(default_factory=dict)
    memory: Memory = Field(default_factory=Memory)
    history: str = Field(default="")

    class Config:
        arbitrary_types_allowed = True

    def add_role(self, role: Role):
        """Add a role in the current environment

        :param role: the role to be added
        :type role: Role
        """

        role.set_env(self)
        self.roles[role.profile] = role

    def add_roles(self, roles: Iterable[Role]):
        """Add a batch of characters in the current environment

        :param roles: the roles to be added
        :type roles: Iterable[Role]
        """

        for role in roles:
            self.add_role(role)

    def publish_message(self, message: Message):
        """Post information to the current environment

        :param message: the message to be published
        :type message: Message
        """

        # self.message_queue.put(message)
        self.memory.add(message)
        self.history += f"\n{message}"

    async def run(self, k=1):
        """Process all Role runs at once

        :param k: the number of steps to run
        :type k: int
        """

        # while not self.message_queue.empty():
        # message = self.message_queue.get()
        # rsp = await self.manager.handle(message, self)
        # self.message_queue.put(rsp)
        for _ in range(k):
            futures = []
            for role in self.roles.values():
                future = role.run()
                futures.append(future)

            await asyncio.gather(*futures)

    def get_roles(self) -> dict[str, Role]:
        """Obtain all the roles within the environment.

        :return: all the roles in the environment
        :rtype: dict[str, Role]
        """

        return self.roles

    def get_role(self, name: str) -> Role:
        """Obtain the specified role within the environment.

        :param name: the name of the role
        :type name: str
        :return: the specified role
        :rtype: Role
        """

        return self.roles.get(name, None)
