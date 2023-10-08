"""Search the knowledge base with a query."""
# -*- coding: utf-8 -*-

import asyncio

from metacogitor.const import DATA_PATH
from metacogitor.document_store import FaissStore
from metacogitor.logs import logger
from metacogitor.roles import Sales


async def search():
    store = FaissStore(DATA_PATH / "example.json")
    role = Sales(profile="Sales", store=store)

    queries = [
        "Which facial cleanser is good for oily skin?",
        "Is L'Oreal good to use?",
    ]
    for query in queries:
        logger.info(f"User: {query}")
        result = await role.run(query)
        logger.info(result)


if __name__ == "__main__":
    asyncio.run(search())
