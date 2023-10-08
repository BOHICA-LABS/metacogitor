"""Long-term memory for Roles"""
# -*- coding: utf-8 -*-

from metacogitor.logs import logger
from metacogitor.memory import Memory
from metacogitor.memory.memory_storage import MemoryStorage
from metacogitor.schema import Message


class LongTermMemory(Memory):
    """The Long-term memory for Roles

    - recover memory when it staruped
    - update memory when it changed

    Attributes:
        memory_storage (MemoryStorage): the memory storage for long-term memory
        rc (RoleContext): the role context
        msg_from_recover (bool): whether the message is from recover
    """

    def __init__(self):
        """Initialize the long-term memory"""

        self.memory_storage: MemoryStorage = MemoryStorage()
        super(LongTermMemory, self).__init__()
        self.rc = None  # RoleContext
        self.msg_from_recover = False

    def recover_memory(self, role_id: str, rc: "RoleContext"):
        """Recover memory from memory storage

        :param role_id: the role id
        :type role_id: str
        :param rc: the role context
        :type rc: RoleContext
        """

        messages = self.memory_storage.recover_memory(role_id)
        self.rc = rc
        if not self.memory_storage.is_initialized:
            logger.warning(
                f"It may the first time to run Agent {role_id}, the long-term memory is empty"
            )
        else:
            logger.warning(
                f"Agent {role_id} has existed memory storage with {len(messages)} messages "
                f"and has recovered them."
            )
        self.msg_from_recover = True
        self.add_batch(messages)
        self.msg_from_recover = False

    def add(self, message: Message):
        """Add a message to memory

        :param message: the message to add
        :type message: Message
        """

        super(LongTermMemory, self).add(message)
        for action in self.rc.watch:
            if message.cause_by == action and not self.msg_from_recover:
                # currently, only add role's watching messages to its memory_storage
                # and ignore adding messages from recover repeatedly
                self.memory_storage.add(message)

    def find_news(self, observed: list[Message], k=0) -> list[Message]:
        """find news (previously unseen messages) from the the most recent k memories, from all memories when k=0

            1. find the short-term memory(stm) news
            2. furthermore, filter out similar messages based on ltm(long-term memory), get the final news

        :param observed: the observed messages
        :type observed: list[Message]
        :param k: the number of memories to search, defaults to 0
        :type k: int, optional
        :return: the news
        :rtype: list[Message]
        """

        stm_news = super(LongTermMemory, self).find_news(
            observed, k=k
        )  # shot-term memory news
        if not self.memory_storage.is_initialized:
            # memory_storage hasn't initialized, use default `find_news` to get stm_news
            return stm_news

        ltm_news: list[Message] = []
        for mem in stm_news:
            # filter out messages similar to those seen previously in ltm, only keep fresh news
            mem_searched = self.memory_storage.search_dissimilar(mem)
            if len(mem_searched) > 0:
                ltm_news.append(mem)
        return ltm_news[-k:]

    def delete(self, message: Message):
        """Delete a message from memory

        :param message: the message to delete
        :type message: Message
        :return: whether the message is deleted
        :rtype: bool
        """

        super(LongTermMemory, self).delete(message)
        # TODO delete message in memory_storage

    def clear(self):
        """Clear the memory"""

        super(LongTermMemory, self).clear()
        self.memory_storage.clean()
