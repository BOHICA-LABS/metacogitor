"""Search engine wrapper for Serper."""
# -*- coding: utf-8 -*-

import json
from typing import Any, Dict, Optional, Tuple

import aiohttp
from pydantic import BaseModel, Field, validator

from metacogitor.config import CONFIG


class SerperWrapper(BaseModel):
    """Search engine wrapper for Serper.

    Attributes:
        search_engine: The search engine.
        payload: The parameters for the search engine.
        serper_api_key: The API key for Serper.
        aiosession: The aiohttp session.
    """

    search_engine: Any  #: :meta private:
    payload: dict = Field(default={"page": 1, "num": 10})
    serper_api_key: Optional[str] = None
    aiosession: Optional[aiohttp.ClientSession] = None

    class Config:
        arbitrary_types_allowed = True

    @validator("serper_api_key", always=True)
    @classmethod
    def check_serper_api_key(cls, val: str):
        """Check if Serper API key is set.

        :param val: The Serper API key.
        :type val: str
        :raises ValueError: If the Serper API key is not set.
        :return: The Serper API key.
        :rtype: str
        :raises ValueError: If the Serper API key is not set.
        """

        val = val or CONFIG.serper_api_key
        if not val:
            raise ValueError(
                "To use, make sure you provide the serper_api_key when constructing an object. Alternatively, "
                "ensure that the environment variable SERPER_API_KEY is set with your API key. You can obtain "
                "an API key from https://serper.dev/."
            )
        return val

    async def run(
        self, query: str, max_results: int = 8, as_string: bool = True, **kwargs: Any
    ) -> str:
        """Run query through Serper and parse result async.

        :param query: The query to run the async search for.
        :type query: str
        :param max_results: The maximum number of results to return, defaults to 8.
        :type max_results: int, optional
        :param as_string: Whether to return the results as a string, defaults to True.
        :type as_string: bool, optional
        :return: The results of the async search for the given query.
        :rtype: str
        :raises ValueError: If the Serper API key is not set.
        """
        if isinstance(query, str):
            return self._process_response(
                (await self.results([query], max_results))[0], as_string=as_string
            )
        else:
            results = [
                self._process_response(res, as_string)
                for res in await self.results(query, max_results)
            ]
        return "\n".join(results) if as_string else results

    async def results(self, queries: list[str], max_results: int = 8) -> dict:
        """Use aiohttp to run query through Serper and return the results async.

        :param queries: The queries to run through Serper.
        :type queries: list[str]
        :param max_results: The maximum number of results to return, defaults to 8.
        :type max_results: int, optional
        :return: The results from Serper.
        :rtype: dict
        """

        def construct_url_and_payload_and_headers() -> Tuple[str, Dict[str, str]]:
            """Construct the URL and payload and headers for Serper.

            :return: The URL and payload and headers for Serper.
            :rtype: Tuple[str, Dict[str, str]]
            """

            payloads = self.get_payloads(queries, max_results)
            url = "https://google.serper.dev/search"
            headers = self.get_headers()
            return url, payloads, headers

        url, payloads, headers = construct_url_and_payload_and_headers()
        if not self.aiosession:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, data=payloads, headers=headers
                ) as response:
                    res = await response.json()
        else:
            async with self.aiosession.get.post(
                url, data=payloads, headers=headers
            ) as response:
                res = await response.json()

        return res

    def get_payloads(self, queries: list[str], max_results: int) -> Dict[str, str]:
        """Get payloads for Serper.

        :param queries: The queries to run through Serper.
        :type queries: list[str]
        :param max_results: The maximum number of results to return.
        :type max_results: int
        :return: The payloads for Serper.
        :rtype: Dict[str, str]
        """
        payloads = []
        for query in queries:
            _payload = {
                "q": query,
                "num": max_results,
            }
            payloads.append({**self.payload, **_payload})
        return json.dumps(payloads, sort_keys=True)

    def get_headers(self) -> Dict[str, str]:
        """Get headers for Serper.

        :return: The headers for Serper.
        :rtype: Dict[str, str]
        """

        headers = {"X-API-KEY": self.serper_api_key, "Content-Type": "application/json"}
        return headers

    @staticmethod
    def _process_response(res: dict, as_string: bool = False) -> str:
        """Process response from SerpAPI.

        :param res: The response from SerpAPI.
        :type res: dict
        :param as_string: Whether to return the results as a string, defaults to False.
        :type as_string: bool, optional
        :return: The parsed result.
        :rtype: str
        """

        # logger.debug(res)
        focus = ["title", "snippet", "link"]

        def get_focused(x):
            return {i: j for i, j in x.items() if i in focus}

        if "error" in res.keys():
            raise ValueError(f"Got error from SerpAPI: {res['error']}")
        if "answer_box" in res.keys() and "answer" in res["answer_box"].keys():
            toret = res["answer_box"]["answer"]
        elif "answer_box" in res.keys() and "snippet" in res["answer_box"].keys():
            toret = res["answer_box"]["snippet"]
        elif (
            "answer_box" in res.keys()
            and "snippet_highlighted_words" in res["answer_box"].keys()
        ):
            toret = res["answer_box"]["snippet_highlighted_words"][0]
        elif (
            "sports_results" in res.keys()
            and "game_spotlight" in res["sports_results"].keys()
        ):
            toret = res["sports_results"]["game_spotlight"]
        elif (
            "knowledge_graph" in res.keys()
            and "description" in res["knowledge_graph"].keys()
        ):
            toret = res["knowledge_graph"]["description"]
        elif "snippet" in res["organic"][0].keys():
            toret = res["organic"][0]["snippet"]
        else:
            toret = "No good search result found"

        toret_l = []
        if "answer_box" in res.keys() and "snippet" in res["answer_box"].keys():
            toret_l += [get_focused(res["answer_box"])]
        if res.get("organic"):
            toret_l += [get_focused(i) for i in res.get("organic")]

        return str(toret) + "\n" + str(toret_l) if as_string else toret_l


if __name__ == "__main__":
    import fire

    fire.Fire(SerperWrapper().run)
