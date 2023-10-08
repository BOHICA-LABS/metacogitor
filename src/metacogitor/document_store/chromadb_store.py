"""ChromaDB Metacogitor Document Store"""
# -*- coding: utf-8 -*-

import chromadb


# If inherited from BaseStore, or importing other modules from metacogitor, a Python exception occurs, which is strange.
class ChromaStore:
    """ChromaDB document store.

    This class is responsible for loading and writing to the ChromaDB document store.

    Attributes:
        client (chromadb.Client): The ChromaDB client.
        collection (chromadb.Collection): The ChromaDB collection.
    """

    def __init__(self, name):
        """Initialize the ChromaDB document store.

        :param name: Name of the collection.
        :type name: str
        """

        client = chromadb.Client()
        collection = client.create_collection(name)
        self.client = client
        self.collection = collection

    def search(self, query, n_results=2, metadata_filter=None, document_filter=None):
        """Search the ChromaDB document store.

        :param query: The query to search for.
        :type query: str
        :param n_results: The number of results to return.
        :type n_results: int
        :param metadata_filter: The metadata filter.
        :type metadata_filter: dict
        :param document_filter: The document filter.
        :type document_filter: dict
        :return: The search results.
        :rtype: list
        """

        # kwargs can be used for optional filtering
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=metadata_filter,  # optional filter
            where_document=document_filter,  # optional filter
        )
        return results

    def persist(self):
        """Chroma recommends using server mode and not persisting locally."""
        raise NotImplementedError

    def write(self, documents, metadatas, ids):
        """Write to the ChromaDB document store.

        This function is similar to add(), but it's for more generalized updates
        It assumes you're passing in lists of docs, metadatas, and ids

        :param documents: The documents to write.
        :type documents: list[str]
        :param metadatas: The metadata to write.
        :type metadatas: list[dict]
        :param ids: The ids to write.
        :type ids: list[str]
        :return: The ids of the written documents.
        :rtype: list[str]
        """

        return self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )

    def add(self, document, metadata, _id):
        """Add to the ChromaDB document store.

        This function is for adding individual documents
        It assumes you're passing in a single doc, metadata, and id

        :param document: The document to add.
        :type document: str
        :param metadata: The metadata to add.
        :type metadata: dict
        :param _id: The id to add.
        :type _id: str
        :return: The id of the written document.
        :rtype: str
        """

        return self.collection.add(
            documents=[document],
            metadatas=[metadata],
            ids=[_id],
        )

    def delete(self, _id):
        """Delete from the ChromaDB document store.

        :param _id: The id to delete.
        :type _id: str
        :return: The id of the deleted document.
        :rtype: str
        """

        return self.collection.delete([_id])
