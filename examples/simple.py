"""Simple example of a metacogitor environment with two roles."""
# -*- coding: utf-8 -*-

import asyncio

from metacogitor.environment import Environment
from metacogitor.roles import Role
from metacogitor.actions import Action, ActionOutput
from metacogitor.schema import Message


class StartAction(Action):
    async def run(self, msg):
        print(f"StartAction Print 1: {msg}")
        print(f"StartAction Print 2 {self.profile}: Started!")
        return ActionOutput(content=msg.content, instruct_content="started")


class PrintAction(Action):
    async def run(self, msg):
        print(f"{self.profile}: {msg.content}")


class StarterRole(Role):
    def __init__(self, name):
        super().__init__(name, "Starter")
        self._init_actions([StartAction()])
        self._watch([StartAction])

    async def run(self, message=None):
        """Observe, and think and act based on the results of the observation"""
        if message:
            if isinstance(message, str):
                message = Message(message)
            if isinstance(message, Message):
                self.recv(message)
            if isinstance(message, list):
                self.recv(Message("\n".join(message)))
        elif not await self._observe():
            # If there is no new information, suspend and wait
            print(f"{self._setting}: no news. waiting.")
            return

        rsp = await self._react()
        # Publish the reply to the environment, waiting for the next subscriber to process
        self._publish_message(rsp)
        return rsp

    async def _observe(self) -> int:
        """Observe from the environment, obtain important information, and add it to memory"""
        if not self._rc.env:
            print(f"{self._setting}: no env")
            return 0
        env_msgs = self._rc.env.memory.get()

        observed = self._rc.env.memory.get_by_actions(self._rc.watch)

        self._rc.news = self._rc.memory.find_news(
            observed
        )  # find news (previously unseen messages) from observed messages

        for i in env_msgs:
            self.recv(i)

        news_text = [f"{i.role}: {i.content[:20]}..." for i in self._rc.news]
        if news_text:
            print(f"{self._setting} observed: {news_text}")
        return len(self._rc.news)


class PrinterRole(Role):
    def __init__(self, name):
        super().__init__(name, "Printer")
        self._init_actions([PrintAction()])
        self._watch([StartAction])


env = Environment()
starter = StarterRole("Alice")
printer = PrinterRole("Bob")

env.add_role(starter)
env.add_role(printer)

# starter.set_env(env)
# printer.set_env(env)

env.publish_message(Message(role="Alice", content="start now", cause_by=StartAction))

if __name__ == "__main__":
    asyncio.run(env.run(3))
