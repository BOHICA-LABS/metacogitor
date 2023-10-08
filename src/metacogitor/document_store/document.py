"""Document class for metacogitor"""
# -*- coding: utf-8 -*-

from pathlib import Path

import pandas as pd
from langchain.document_loaders import (
    TextLoader,
    UnstructuredPDFLoader,
    UnstructuredWordDocumentLoader,
)
from langchain.text_splitter import CharacterTextSplitter
from tqdm import tqdm


def validate_cols(content_col: str, df: pd.DataFrame):
    """Validate the content column exists in the dataframe.

    :param content_col: The content column.
    :type content_col: str
    :param df: The dataframe.
    :type df: pd.DataFrame
    :raises ValueError: If the content column does not exist in the dataframe.
    """

    if content_col not in df.columns:
        raise ValueError


def read_data(data_path: Path):
    """Read the data from the given path.

    :param data_path: The path to the data.
    :type data_path: Path
    :return: The data.
    :rtype: pd.DataFrame or list
    :raises NotImplementedError: If the file type is not supported.
    """

    suffix = data_path.suffix
    if ".xlsx" == suffix:
        data = pd.read_excel(data_path)
    elif ".csv" == suffix:
        data = pd.read_csv(data_path)
    elif ".json" == suffix:
        data = pd.read_json(data_path)
    elif suffix in (".docx", ".doc"):
        data = UnstructuredWordDocumentLoader(str(data_path), mode="elements").load()
    elif ".txt" == suffix:
        data = TextLoader(str(data_path)).load()
        text_splitter = CharacterTextSplitter(
            separator="\n", chunk_size=256, chunk_overlap=0
        )
        texts = text_splitter.split_documents(data)
        data = texts
    elif ".pdf" == suffix:
        data = UnstructuredPDFLoader(str(data_path), mode="elements").load()
    else:
        raise NotImplementedError
    return data


class Document:
    """Document class for metacogitor

    Attributes:
        data (pd.DataFrame or list): The data.
        content_col (str): The content column.
        meta_col (str): The metadata column.
    """

    def __init__(self, data_path, content_col="content", meta_col="metadata"):
        """Initialize the Document class.

        :param data_path: The path to the data.
        :type data_path: Path
        :param content_col: The content column, defaults to "content"
        :type content_col: str, optional
        :param meta_col: The metadata column, defaults to "metadata"
        :type meta_col: str, optional
        """

        self.data = read_data(data_path)
        if isinstance(self.data, pd.DataFrame):
            validate_cols(content_col, self.data)
        self.content_col = content_col
        self.meta_col = meta_col

    def _get_docs_and_metadatas_by_df(self) -> (list, list):
        """Get the documents and metadatas from the dataframe.

        :return: The documents and metadatas.
        :rtype: (list, list)
        """

        df = self.data
        docs = []
        metadatas = []
        for i in tqdm(range(len(df))):
            docs.append(df[self.content_col].iloc[i])
            if self.meta_col:
                metadatas.append({self.meta_col: df[self.meta_col].iloc[i]})
            else:
                metadatas.append({})

        return docs, metadatas

    def _get_docs_and_metadatas_by_langchain(self) -> (list, list):
        """Get the documents and metadatas from the langchain document loader.

        :return: The documents and metadatas.
        :rtype: (list, list)
        """

        data = self.data
        docs = [i.page_content for i in data]
        metadatas = [i.metadata for i in data]
        return docs, metadatas

    def get_docs_and_metadatas(self) -> (list, list):
        """Get the documents and metadatas.

        :return: The documents and metadatas.
        :rtype: (list, list)
        :raises NotImplementedError: If the data type is not supported.
        """

        if isinstance(self.data, pd.DataFrame):
            return self._get_docs_and_metadatas_by_df()
        elif isinstance(self.data, list):
            return self._get_docs_and_metadatas_by_langchain()
        else:
            raise NotImplementedError
