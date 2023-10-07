"""Search engine using MeiliSearch."""
# -*- coding: utf-8 -*-

from typing import List

import meilisearch
from meilisearch.index import Index


class DataSource:
    """Class representing a data source.

    Attributes:
        name: The name of the data source.
        url: The URL of the data source.
    """

    def __init__(self, name: str, url: str):
        """Initialize the data source.

        :param name: The name of the data source.
        :type name: str
        :param url: The URL of the data source.
        :type url: str
        """

        self.name = name
        self.url = url


class MeilisearchEngine:
    """Class representing a MeiliSearch engine.

    Attributes:
        client: The MeiliSearch client.
        _index: The MeiliSearch index.
    """

    def __init__(self, url, token):
        """Initialize the MeiliSearch engine.

        :param url: The URL of the MeiliSearch server.
        :type url: str
        :param token: The token for the MeiliSearch server.
        :type token: str
        """

        self.client = meilisearch.Client(url, token)
        self._index: Index = None

    def set_index(self, index):
        """Set the MeiliSearch index.

        :param index: The MeiliSearch index.
        :type index: Index
        """

        self._index = index

    def add_documents(self, data_source: DataSource, documents: List[dict]):
        """Add documents to the MeiliSearch index.

        :param data_source: The data source.
        :type data_source: DataSource
        :param documents: The documents to add to the MeiliSearch index.
        :type documents: List[dict]
        """

        index_name = f"{data_source.name}_index"
        if index_name not in self.client.get_indexes():
            self.client.create_index(uid=index_name, options={"primaryKey": "id"})
        index = self.client.get_index(index_name)
        index.add_documents(documents)
        self.set_index(index)

    def search(self, query):
        """Search the MeiliSearch index.

        :param query: The query to search the MeiliSearch index with.
        :type query: str
        :return: The search results.
        :rtype: dict
        """

        try:
            search_results = self._index.search(query)
            return search_results["hits"]
        except Exception as e:
            # Handle MeiliSearch API errors
            print(f"MeiliSearch API error: {e}")
            return []
