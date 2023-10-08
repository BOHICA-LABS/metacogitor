"""FaissStore Document Store"""
# -*- coding: utf-8 -*-

import pickle
from pathlib import Path
from typing import Optional

import faiss
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

from metacogitor.const import DATA_PATH
from metacogitor.document_store.base_store import LocalStore
from metacogitor.document_store.document import Document
from metacogitor.logs import logger


class FaissStore(LocalStore):
    """FaissStore Document Store

    Attributes:
        raw_data (Path): The path to the raw data.
        cache_dir (Path): The path to the cache directory.
        meta_col (str): The metadata column.
        content_col (str): The content column.
    """

    def __init__(
        self, raw_data: Path, cache_dir=None, meta_col="source", content_col="output"
    ):
        """Initialize the FaissStore class.

        :param raw_data: The path to the raw data.
        :type raw_data: Path
        :param cache_dir: The path to the cache directory, defaults to None
        :type cache_dir: Path, optional
        :param meta_col: The metadata column, defaults to "source"
        :type meta_col: str, optional
        :param content_col: The content column, defaults to "output"
        :type content_col: str, optional
        """

        self.meta_col = meta_col
        self.content_col = content_col
        super().__init__(raw_data, cache_dir)

    def _load(self) -> Optional["FaissStore"]:
        """Load the store from the cache directory.

        :return: The store.
        :rtype: Optional["FaissStore"]
        """

        index_file, store_file = self._get_index_and_store_fname()
        if not (index_file.exists() and store_file.exists()):
            logger.info(
                "Missing at least one of index_file/store_file, load failed and return None"
            )
            return None
        index = faiss.read_index(str(index_file))
        with open(str(store_file), "rb") as f:
            store = pickle.load(f)
        store.index = index
        return store

    def _write(self, docs, metadatas):
        """Write the store.

        :param docs: The documents.
        :type docs: list
        :param metadatas: The metadatas.
        :type metadatas: list
        :return: The store.
        :rtype: FAISS
        """

        store = FAISS.from_texts(
            docs, OpenAIEmbeddings(openai_api_version="2020-11-07"), metadatas=metadatas
        )
        return store

    def persist(self):
        """Persist the store to the cache directory."""

        index_file, store_file = self._get_index_and_store_fname()
        store = self.store
        index = self.store.index
        faiss.write_index(store.index, str(index_file))
        store.index = None
        with open(store_file, "wb") as f:
            pickle.dump(store, f)
        store.index = index

    def search(self, query, expand_cols=False, sep="\n", *args, k=5, **kwargs):
        """Search the store.

        :param query: The query.
        :type query: str
        :param expand_cols: Whether to expand the columns, defaults to False
        :type expand_cols: bool, optional
        :param sep: The separator, defaults to "\n"
        :type sep: str, optional
        :param k: The number of results to return, defaults to 5
        :type k: int, optional
        :return: The search results.
        :rtype: str
        """

        rsp = self.store.similarity_search(query, k=k, **kwargs)
        logger.debug(rsp)
        if expand_cols:
            return str(sep.join([f"{x.page_content}: {x.metadata}" for x in rsp]))
        else:
            return str(sep.join([f"{x.page_content}" for x in rsp]))

    def write(self):
        """Initialize the index and library based on the Document (JSON / XLSX, etc.) file provided by the user."""
        if not self.raw_data.exists():
            raise FileNotFoundError
        doc = Document(self.raw_data, self.content_col, self.meta_col)
        docs, metadatas = doc.get_docs_and_metadatas()

        self.store = self._write(docs, metadatas)
        self.persist()
        return self.store

    # TODO: Currently, the store is not updated after adding.
    def add(self, texts: list[str], *args, **kwargs) -> list[str]:
        """Add the given texts to the store.

        :param texts: The texts to add.
        :type texts: list[str]
        :return: The added texts.
        :rtype: list[str]
        """

        return self.store.add_texts(texts)

    def delete(self, *args, **kwargs):
        """Currently, langchain does not provide a delete interface."""
        raise NotImplementedError


if __name__ == "__main__":
    faiss_store = FaissStore(DATA_PATH / "qcs/qcs_4w.json")
    logger.info(faiss_store.search("Oily Skin Facial Cleanser"))
    faiss_store.add([f"Oily Skin Facial Cleanser-{i}" for i in range(3)])
    logger.info(faiss_store.search("Oily Skin Facial Cleanser"))
