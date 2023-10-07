"""Search engine module."""
# -*- coding: utf-8 -*-

import importlib
from typing import Callable, Coroutine, Literal, overload, Optional, Union

from semantic_kernel.skill_definition import sk_function

from metacogitor.config import CONFIG
from metacogitor.tools import SearchEngineType


class SkSearchEngine:
    """Skill for searching the web."""

    def __init__(self):
        """Initialize the skill."""
        self.search_engine = SearchEngine()

    @sk_function(
        description="searches results from Google. Useful when you need to find short "
        "and succinct answers about a specific topic. Input should be a search query.",
        name="searchAsync",
        input_description="search",
    )
    async def run(self, query: str) -> str:
        """Run a search query.

        :param query: The search query.
        :type query: str
        :return: The search results.
        :rtype: str
        """

        result = await self.search_engine.run(query)
        return result


class SearchEngine:
    """Class representing a search engine.

    Attributes:
        run_func: The function to run the search.
        engine: The search engine type.
    """

    def __init__(
        self,
        engine: Optional[SearchEngineType] = None,
        run_func: Callable[
            [str, int, bool], Coroutine[None, None, Union[str, list[str]]]
        ] = None,
    ):
        """Initialize the search engine.

        :param engine: The search engine type. Defaults to the search engine specified in the config.
        :type engine: Optional[SearchEngineType], optional
        :param run_func: The function to run the search. Defaults to None.
        :type run_func: Callable[[str, int, bool], Coroutine[None, None, Union[str, list[str]]]], optional
        """

        engine = engine or CONFIG.search_engine
        if engine == SearchEngineType.SERPAPI_GOOGLE:
            module = "metacogitor.tools.search_engine_serpapi"
            run_func = importlib.import_module(module).SerpAPIWrapper().run
        elif engine == SearchEngineType.SERPER_GOOGLE:
            module = "metacogitor.tools.search_engine_serper"
            run_func = importlib.import_module(module).SerperWrapper().run
        elif engine == SearchEngineType.DIRECT_GOOGLE:
            module = "metacogitor.tools.search_engine_googleapi"
            run_func = importlib.import_module(module).GoogleAPIWrapper().run
        elif engine == SearchEngineType.DUCK_DUCK_GO:
            module = "metacogitor.tools.search_engine_ddg"
            run_func = importlib.import_module(module).DDGAPIWrapper().run
        elif engine == SearchEngineType.CUSTOM_ENGINE:
            pass  # run_func = run_func
        else:
            raise NotImplementedError
        self.engine = engine
        self.run_func = run_func

    @overload
    def run(
        self,
        query: str,
        max_results: int = 8,
        as_string: Literal[True] = True,
    ) -> str:
        ...

    @overload
    def run(
        self,
        query: str,
        max_results: int = 8,
        as_string: Literal[False] = False,
    ) -> list[dict[str, str]]:
        ...

    async def run(
        self, query: str, max_results: int = 8, as_string: bool = True
    ) -> Union[str, list[dict[str, str]]]:
        """Run a search query.

        :param query: The search query.
        :type query: str
        :param max_results: The maximum number of results to return. Defaults to 8.
        :type max_results: int, optional
        :param: as_string: Whether to return the results as a string or a list of dictionaries. Defaults to True.
        :type as_string: bool, optional
        :return: The search results.
        :rtype: Union[str, list[dict[str, str]]]
        """

        return await self.run_func(query, max_results=max_results, as_string=as_string)
