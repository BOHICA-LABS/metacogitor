"""File util for file operations."""
# _*_ coding: utf-8 _*_

import aiofiles
from pathlib import Path

from metacogitor.logs import logger


class File:
    """A general util for file operations."""

    CHUNK_SIZE = 64 * 1024

    @classmethod
    async def write(cls, root_path: Path, filename: str, content: bytes) -> Path:
        """Write the file content to the local specified path.

        :param root_path: The root path of file, such as "/data".
        :type root_path: Path
        :param filename: The name of file, such as "test.txt".
        :type filename: str
        :param content: The binary content of file.
        :type content: bytes
        :return: The full filename of file, such as "/data/test.txt".
        :rtype: Path
        :raises Exception: If an unexpected error occurs during the file writing process.
        """

        try:
            root_path.mkdir(parents=True, exist_ok=True)
            full_path = root_path / filename
            async with aiofiles.open(full_path, mode="wb") as writer:
                await writer.write(content)
                logger.debug(f"Successfully write file: {full_path}")
                return full_path
        except Exception as e:
            logger.error(f"Error writing file: {e}")
            raise e

    @classmethod
    async def read(cls, file_path: Path, chunk_size: int = None) -> bytes:
        """Partitioning read the file content from the local specified path.

        :param file_path: The full file name of file, such as "/data/test.txt".
        :type file_path: Path
        :param chunk_size: The size of each chunk in bytes (default is 64kb).
        :type chunk_size: int
        :return: The binary content of file.
        :rtype: bytes
        :raises Exception: If an unexpected error occurs during the file reading process.
        """

        try:
            chunk_size = chunk_size or cls.CHUNK_SIZE
            async with aiofiles.open(file_path, mode="rb") as reader:
                chunks = list()
                while True:
                    chunk = await reader.read(chunk_size)
                    if not chunk:
                        break
                    chunks.append(chunk)
                content = b"".join(chunks)
                logger.debug(f"Successfully read file, the path of file: {file_path}")
                return content
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            raise e
