"""Search Google for a query and return the results."""
# -*- coding: utf-8 -*-

import asyncio

from metacogitor.roles import Searcher


async def main():
    await Searcher().run("What are some good sun protection products?")


if __name__ == "__main__":
    asyncio.run(main())
