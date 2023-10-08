"""Schema for metacogitor"""
# -*- coding: utf-8 -*-

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Type, TypedDict

from pydantic import BaseModel

from metacogitor.logs import logger


class RawMessage(TypedDict):
    content: str
    role: str


@dataclass
class Message:
    """Message Class

    The scheme for messages in the metacogitor system.

    list[<role>: <content>]

    Attributes:
        content (str): The content of the message.
        role (str): The role of the message.
        cause_by (Action): The action that caused the message.
        sent_from (str): The role that sent the message.
        send_to (str): The role that the message was sent to.
        restricted_to (str): The role that the message is restricted to.
    """

    content: str
    instruct_content: BaseModel = field(default=None)
    role: str = field(default="user")  # system / user / assistant
    cause_by: Type["Action"] = field(default="")
    sent_from: str = field(default="")
    send_to: str = field(default="")
    restricted_to: str = field(default="")

    def __str__(self):
        # prefix = '-'.join([self.role, str(self.cause_by)])
        return f"{self.role}: {self.content}"

    def __repr__(self):
        return self.__str__()

    def to_dict(self) -> dict:
        return {"role": self.role, "content": self.content}


@dataclass
class UserMessage(Message):
    """Facilitate support for OpenAI messages"""

    def __init__(self, content: str):
        super().__init__(content, "user")


@dataclass
class SystemMessage(Message):
    """Facilitate support for OpenAI messages"""

    def __init__(self, content: str):
        super().__init__(content, "system")


@dataclass
class AIMessage(Message):
    """Facilitate support for OpenAI messages"""

    def __init__(self, content: str):
        super().__init__(content, "assistant")


if __name__ == "__main__":
    test_content = "test_message"
    msgs = [
        UserMessage(test_content),
        SystemMessage(test_content),
        AIMessage(test_content),
        Message(test_content, role="QA"),
    ]
    logger.info(msgs)
