"""Base class for document stores."""
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from pathlib import Path

from metacogitor.config import Config


"""FIXME: consider add_index, set_index and think about granularity."""


class BaseStore(ABC):
    """Base class for document stores."""

    @abstractmethod
    def search(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def write(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def add(self, *args, **kwargs):
        raise NotImplementedError


class LocalStore(BaseStore, ABC):
    """Local document store.

    This class is responsible for loading and writing to the local document store.

    Attributes:
        raw_data (Path): Path to the raw data.
        cache_dir (Path): Path to the cache directory.
        store (dict): The store.
    """

    def __init__(self, raw_data: Path, cache_dir: Path = None):
        """Initialize the local document store.

        :param raw_data: Path to the raw data.
        :type raw_data: Path
        :param cache_dir: Path to the cache directory.
        :type cache_dir: Path
        """

        if not raw_data:
            raise FileNotFoundError
        self.config = Config()
        self.raw_data = raw_data
        if not cache_dir:
            cache_dir = raw_data.parent
        self.cache_dir = cache_dir
        self.store = self._load()
        if not self.store:
            self.store = self.write()

    def _get_index_and_store_fname(self):
        """Get the index and store filenames.

        :return: The index and store filenames.
        :rtype: tuple[Path, Path]
        """

        fname = self.raw_data.name.split(".")[0]
        index_file = self.cache_dir / f"{fname}.index"
        store_file = self.cache_dir / f"{fname}.pkl"
        return index_file, store_file

    @abstractmethod
    def _load(self):
        """Load the store."""

        raise NotImplementedError

    @abstractmethod
    def _write(self, docs, metadatas):
        """Write the store.

        :param docs: The documents.
        :type docs: list[str]
        :param metadatas: The metadata.
        :type metadatas: list[dict]
        """

        raise NotImplementedError
