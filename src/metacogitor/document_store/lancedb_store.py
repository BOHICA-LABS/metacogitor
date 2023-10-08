"""LanceDB Store Document Store"""
# -*- coding: utf-8 -*-

import os
import shutil

import lancedb


class LanceStore:
    """LanceDB Store Document Store

    Attributes:
        db (lancedb): The LanceDB database.
        name (str): The name of the table.
        table (lancedb.Table): The table.
    """

    def __init__(self, name):
        """Initialize the LanceStore class.

        :param name: The name of the table.
        :type name: str
        """

        db = lancedb.connect("./data/lancedb")
        self.db = db
        self.name = name
        self.table = None

    def search(self, query, n_results=2, metric="L2", nprobes=20, **kwargs):
        """Search the table for the given query.

        This assumes query is a vector embedding
        kwargs can be used for optional filtering
        .select - only searches the specified columns
        .where - SQL syntax filtering for metadata (e.g. where("price > 100"))
        .metric - specifies the distance metric to use
        .nprobes - values will yield better recall (more likely to find vectors if they exist) at the expense of latency.

        :param query: The query to search for.
        :type query: str
        :param n_results: The number of results to return, defaults to 2
        :type n_results: int, optional
        :param metric: The distance metric to use, defaults to "L2"
        :type metric: str, optional
        :param nprobes: The number of probes to use, defaults to 20
        :type nprobes: int, optional
        :return: The search results.
        :rtype: pandas.DataFrame
        """

        if self.table is None:
            raise Exception("Table not created yet, please add data first.")

        results = (
            self.table.search(query)
            .limit(n_results)
            .select(kwargs.get("select"))
            .where(kwargs.get("where"))
            .metric(metric)
            .nprobes(nprobes)
            .to_df()
        )
        return results

    def persist(self):
        """Persist the table to disk."""
        raise NotImplementedError

    def write(self, data, metadatas, ids):
        """Write the given data to the table.

        This function is similar to add(), but it's for more generalized updates
        "data" is the list of embeddings
        Inserts into table by expanding metadatas into a dataframe: [{'vector', 'id', 'meta', 'meta2'}, ...]

        :param data: The data to write.
        :type data: list
        :param metadatas: The metadatas to write.
        :type metadatas: list
        :param ids: The ids to write.
        :type ids: list
        """

        documents = []
        for i in range(len(data)):
            row = {"vector": data[i], "id": ids[i]}
            row.update(metadatas[i])
            documents.append(row)

        if self.table is not None:
            self.table.add(documents)
        else:
            self.table = self.db.create_table(self.name, documents)

    def add(self, data, metadata, _id):
        """Add the given data to the table.

        This function is for adding individual documents
        It assumes you're passing in a single vector embedding, metadata, and id

        :param data: The data to add.
        :type data: list
        :param metadata: The metadata to add.
        :type metadata: list
        :param _id: The id to add.
        :type _id: list
        """

        row = {"vector": data, "id": _id}
        row.update(metadata)

        if self.table is not None:
            self.table.add([row])
        else:
            self.table = self.db.create_table(self.name, [row])

    def delete(self, _id):
        """Delete the given row by id.

        This function deletes a row by id.
        LanceDB delete syntax uses SQL syntax, so you can use "in" or "="

        :param _id: The id to delete.
        :type _id: str
        """

        if self.table is None:
            raise Exception("Table not created yet, please add data first")

        if isinstance(_id, str):
            return self.table.delete(f"id = '{_id}'")
        else:
            return self.table.delete(f"id = {_id}")

    def drop(self, name):
        """Drop the given table.

        This function drops a table, if it exists.

        :param name: The name of the table to drop.
        :type name: str
        """

        path = os.path.join(self.db.uri, name + ".lance")
        if os.path.exists(path):
            shutil.rmtree(path)
