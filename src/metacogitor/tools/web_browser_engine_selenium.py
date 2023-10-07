"""Web browser engine using Selenium."""
# -*- coding: utf-8 -*-

from __future__ import annotations

import asyncio
import importlib
from concurrent import futures
from copy import deepcopy
from typing import Literal

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from metacogitor.config import CONFIG
from metacogitor.utils.parse_html import WebPage


class SeleniumWrapper:
    """Wrapper around Selenium.

    To use this module, you should check the following:

    1. Run the following command: pip install metacogitor[selenium].
    2. Make sure you have a compatible web browser installed and the appropriate WebDriver set up
       for that browser before running. For example, if you have Mozilla Firefox installed on your
       computer, you can set the configuration SELENIUM_BROWSER_TYPE to firefox. After that, you
       can scrape web pages using the Selenium WebBrowserEngine.

    Attributes:
        browser_type (Literal["chrome", "firefox", "edge", "ie"]): The browser type to use.
        launch_kwargs (dict): The keyword arguments to pass to the browser type's launch method.
        _has_run_precheck (bool): Whether the precheck has been run.
    """

    def __init__(
        self,
        browser_type: Literal["chrome", "firefox", "edge", "ie"] | None = None,
        launch_kwargs: dict | None = None,
        *,
        loop: asyncio.AbstractEventLoop | None = None,
        executor: futures.Executor | None = None,
    ) -> None:
        """Initialize the SeleniumWrapper instance.

        :param browser_type: The browser type to use, defaults to None
        :type browser_type: Literal["chrome", "firefox", "edge", "ie"] | None, optional
        :param launch_kwargs: The keyword arguments to pass to the browser type's launch method, defaults to None
        :type launch_kwargs: dict | None, optional
        :param loop: The event loop to use, defaults to None
        :type loop: asyncio.AbstractEventLoop | None, optional
        :param executor: The executor to use, defaults to None
        :type executor: futures.Executor | None, optional
        """

        if browser_type is None:
            browser_type = CONFIG.selenium_browser_type
        self.browser_type = browser_type
        launch_kwargs = launch_kwargs or {}
        if CONFIG.global_proxy and "proxy-server" not in launch_kwargs:
            launch_kwargs["proxy-server"] = CONFIG.global_proxy

        self.executable_path = launch_kwargs.pop("executable_path", None)
        self.launch_args = [f"--{k}={v}" for k, v in launch_kwargs.items()]
        self._has_run_precheck = False
        self._get_driver = None
        self.loop = loop
        self.executor = executor

    async def run(self, url: str, *urls: str) -> WebPage | list[WebPage]:
        """Run the web browser engine.

        :param url: The URL to run the web browser engine for.
        :type url: str
        :param urls: The URLs to run the web browser engine for.
        :type urls: str
        :return: The web page or web pages.
        :rtype: WebPage | list[WebPage]
        """

        await self._run_precheck()

        _scrape = lambda url: self.loop.run_in_executor(
            self.executor, self._scrape_website, url
        )

        if urls:
            return await asyncio.gather(_scrape(url), *(_scrape(i) for i in urls))
        return await _scrape(url)

    async def _run_precheck(self):
        """Run the precheck."""

        if self._has_run_precheck:
            return
        self.loop = self.loop or asyncio.get_event_loop()
        self._get_driver = await self.loop.run_in_executor(
            self.executor,
            lambda: _gen_get_driver_func(
                self.browser_type,
                *self.launch_args,
                executable_path=self.executable_path,
            ),
        )
        self._has_run_precheck = True

    def _scrape_website(self, url):
        """Scrape the web page.

        :param url: The URL to scrape.
        :type url: str
        :return: The web page.
        :rtype: WebPage
        """

        with self._get_driver() as driver:
            try:
                driver.get(url)
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                inner_text = driver.execute_script("return document.body.innerText;")
                html = driver.page_source
            except Exception as e:
                inner_text = f"Fail to load page content for {e}"
                html = ""
            return WebPage(inner_text=inner_text, html=html, url=url)


_webdriver_manager_types = {
    "chrome": ("webdriver_manager.chrome", "ChromeDriverManager"),
    "firefox": ("webdriver_manager.firefox", "GeckoDriverManager"),
    "edge": ("webdriver_manager.microsoft", "EdgeChromiumDriverManager"),
    "ie": ("webdriver_manager.microsoft", "IEDriverManager"),
}


def _gen_get_driver_func(browser_type, *args, executable_path=None):
    """Generate a function to get the web driver.

    :param browser_type: The browser type.
    :type browser_type: Literal["chrome", "firefox", "edge", "ie"]
    :param args: The arguments to pass to the web driver.
    :type args: tuple
    :param executable_path: The path to the executable, defaults to None
    :type executable_path: str | None, optional
    :return: The function to get the web driver.
    :rtype: function
    """

    WebDriver = getattr(
        importlib.import_module(f"selenium.webdriver.{browser_type}.webdriver"),
        "WebDriver",
    )
    Service = getattr(
        importlib.import_module(f"selenium.webdriver.{browser_type}.service"), "Service"
    )
    Options = getattr(
        importlib.import_module(f"selenium.webdriver.{browser_type}.options"), "Options"
    )

    if not executable_path:
        module_name, type_name = _webdriver_manager_types[browser_type]
        DriverManager = getattr(importlib.import_module(module_name), type_name)
        driver_manager = DriverManager()
        # driver_manager.driver_cache.find_driver(driver_manager.driver))
        executable_path = driver_manager.install()

    def _get_driver():
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--enable-javascript")
        if browser_type == "chrome":
            options.add_argument("--no-sandbox")
        for i in args:
            options.add_argument(i)
        return WebDriver(
            options=deepcopy(options), service=Service(executable_path=executable_path)
        )

    return _get_driver


if __name__ == "__main__":
    import fire

    async def main(url: str, *urls: str, browser_type: str = "chrome", **kwargs):
        return await SeleniumWrapper(browser_type, **kwargs).run(url, *urls)

    fire.Fire(main)
