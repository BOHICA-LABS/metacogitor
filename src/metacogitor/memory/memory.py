"""Memory is the most basic storage of Metacogitor, it stores all messages and provides basic operations on them."""
# -*- coding: utf-8 -*-

from collections import defaultdict
from typing import Iterable, Type

from metacogitor.actions import Action
from metacogitor.schema import Message


class Memory:
    """The most basic memory: super-memory

    Attributes:
        storage (list[Message]): the storage of all messages
        index (dict[Type[Action], list[Message]]): the index of messages, key is Action, value is the list of messages
                                                   triggered by the Action
    """

    def __init__(self):
        """Initialize an empty storage list and an empty index dictionary"""
        self.storage: list[Message] = []
        self.index: dict[Type[Action], list[Message]] = defaultdict(list)

    def add(self, message: Message):
        """Add a new message to storage, while updating the index

        :param message: the message to add
        :type message: Message
        """

        if message in self.storage:
            return
        self.storage.append(message)
        if message.cause_by:
            self.index[message.cause_by].append(message)

    def add_batch(self, messages: Iterable[Message]):
        """Add a batch of messages to storage, while updating the index

        :param messages: the messages to add
        :type messages: Iterable[Message]
        """

        for message in messages:
            self.add(message)

    def get_by_role(self, role: str) -> list[Message]:
        """Return all messages of a specified role

        :param role: the role to get messages
        :type role: str
        :return: the messages of the specified role
        :rtype: list[Message]
        """

        return [message for message in self.storage if message.role == role]

    def get_by_content(self, content: str) -> list[Message]:
        """Return all messages containing a specified content

        :param content: the content to search
        :type content: str
        :return: the messages containing the specified content
        :rtype: list[Message]
        """

        return [message for message in self.storage if content in message.content]

    def delete(self, message: Message):
        """Delete the specified message from storage, while updating the index

        :param message: the message to delete
        :type message: Message
        """

        self.storage.remove(message)
        if message.cause_by and message in self.index[message.cause_by]:
            self.index[message.cause_by].remove(message)

    def clear(self):
        """Clear storage and index"""
        self.storage = []
        self.index = defaultdict(list)

    def count(self) -> int:
        """Return the number of messages in storage"""
        return len(self.storage)

    def try_remember(self, keyword: str) -> list[Message]:
        """Try to recall all messages containing a specified keyword

        :param keyword: the keyword to search
        :type keyword: str
        :return: the messages containing the specified keyword
        :rtype: list[Message]
        """

        return [message for message in self.storage if keyword in message.content]

    def get(self, k=0) -> list[Message]:
        """Return the most recent k memories, return all when k=0

        :param k: the number of memories to return, defaults to 0
        :type k: int, optional
        :return: the most recent k memories
        :rtype: list[Message]
        """

        return self.storage[-k:]

    def find_news(self, observed: list[Message], k=0) -> list[Message]:
        """find news (previously unseen messages) from the the most recent k memories, from all memories when k=0

        :param observed: the observed messages
        :type observed: list[Message]
        :param k: the number of memories to search, defaults to 0
        :type k: int, optional
        :return: the news
        :rtype: list[Message]
        """
        already_observed = self.get(k)
        news: list[Message] = []
        for i in observed:
            if i in already_observed:
                continue
            news.append(i)
        return news

    def get_by_action(self, action: Type[Action]) -> list[Message]:
        """Return all messages triggered by a specified Action

        :param action: the Action to get messages
        :type action: Type[Action]
        :return: the messages triggered by the specified Action
        :rtype: list[Message]
        """

        return self.index[action]

    def get_by_actions(self, actions: Iterable[Type[Action]]) -> list[Message]:
        """Return all messages triggered by specified Actions

        :param actions: the Actions to get messages
        :type actions: Iterable[Type[Action]]
        :return: the messages triggered by the specified Actions
        :rtype: list[Message]
        """

        rsp = []
        for action in actions:
            if action not in self.index:
                continue
            rsp += self.index[action]
        return rsp
