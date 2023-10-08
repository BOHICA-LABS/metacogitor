"""Searcher role module."""
# -*- coding: utf-8 -*-

from metacogitor.actions import ActionOutput, SearchAndSummarize
from metacogitor.logs import logger
from metacogitor.roles import Role
from metacogitor.schema import Message
from metacogitor.tools import SearchEngineType


class Searcher(Role):
    """
    Represents a Searcher role responsible for providing search services to users.

    Attributes:
        name (str): Name of the searcher.
        profile (str): Role profile.
        goal (str): Goal of the searcher.
        constraints (str): Constraints or limitations for the searcher.
        engine (SearchEngineType): The type of search engine to use.
    """

    def __init__(
        self,
        name: str = "Alice",
        profile: str = "Smart Assistant",
        goal: str = "Provide search services for users",
        constraints: str = "Answer is rich and complete",
        engine=SearchEngineType.SERPAPI_GOOGLE,
        **kwargs,
    ) -> None:
        """
        Initializes the Searcher role with given attributes.

        :param name: Name of the searcher.
        :type name: str
        :param profile: Role profile.
        :type profile: str
        :param goal: Goal of the searcher.
        :type goal: str
        :param constraints: Constraints or limitations for the searcher.
        :type constraints: str
        :param engine: The type of search engine to use.
        :type engine: SearchEngineType
        """
        super().__init__(name, profile, goal, constraints, **kwargs)
        self._init_actions([SearchAndSummarize(engine=engine)])

    def set_search_func(self, search_func):
        """Sets a custom search function for the searcher.

        :param search_func: The custom search function.
        :type search_func: function
        :return: None
        :rtype: None
        """

        action = SearchAndSummarize(
            "", engine=SearchEngineType.CUSTOM_ENGINE, search_func=search_func
        )
        self._init_actions([action])

    async def _act_sp(self) -> Message:
        """Performs the search action in a single process.

        :return: The message to send to the user.
        :rtype: Message
        """

        logger.info(f"{self._setting}: ready to {self._rc.todo}")
        response = await self._rc.todo.run(self._rc.memory.get(k=0))

        if isinstance(response, ActionOutput):
            msg = Message(
                content=response.content,
                instruct_content=response.instruct_content,
                role=self.profile,
                cause_by=type(self._rc.todo),
            )
        else:
            msg = Message(
                content=response, role=self.profile, cause_by=type(self._rc.todo)
            )
        self._rc.memory.add(msg)
        return msg

    async def _act(self) -> Message:
        """Determines the mode of action for the searcher.

        :return: The message to send to the user.
        :rtype: Message
        """
        return await self._act_sp()
