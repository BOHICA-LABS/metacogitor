"""Parse HTML content and extract useful information."""
# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Generator, Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from pydantic import BaseModel


class WebPage(BaseModel):
    """Web page model."""

    inner_text: str
    html: str
    url: str

    class Config:
        underscore_attrs_are_private = True

    _soup: Optional[BeautifulSoup] = None
    _title: Optional[str] = None

    @property
    def soup(self) -> BeautifulSoup:
        """Returns the BeautifulSoup object for the given HTML content.

        :return: The BeautifulSoup object for the given HTML content.
        :rtype: BeautifulSoup
        """

        if self._soup is None:
            self._soup = BeautifulSoup(self.html, "html.parser")
        return self._soup

    @property
    def title(self):
        """Returns the title of the web page.

        :return: The title of the web page.
        :rtype: str
        """

        if self._title is None:
            title_tag = self.soup.find("title")
            self._title = title_tag.text.strip() if title_tag is not None else ""
        return self._title

    def get_links(self) -> Generator[str, None, None]:
        """Returns the links in the web page.

        :return: The links in the web page.
        :rtype: Generator[str, None, None]
        """

        for i in self.soup.find_all("a", href=True):
            url = i["href"]
            result = urlparse(url)
            if not result.scheme and result.path:
                yield urljoin(self.url, url)
            elif url.startswith(("http://", "https://")):
                yield urljoin(self.url, url)


def get_html_content(page: str, base: str):
    """Returns the HTML content of the given page.

    :param page: The page to get the HTML content for.
    :type page: str
    :param base: The base URL to use for relative URLs.
    :type base: str
    :return: The HTML content of the given page.
    :rtype: str
    """

    soup = _get_soup(page)

    return soup.get_text(strip=True)


def _get_soup(page: str):
    """Returns the BeautifulSoup object for the given HTML content.

    :param page: The page to get the BeautifulSoup object for.
    :type page: str
    :return: The BeautifulSoup object for the given HTML content.
    :rtype: BeautifulSoup
    """

    soup = BeautifulSoup(page, "html.parser")
    # https://stackoverflow.com/questions/1936466/how-to-scrape-only-visible-webpage-text-with-beautifulsoup
    for s in soup(["style", "script", "[document]", "head", "title"]):
        s.extract()

    return soup
