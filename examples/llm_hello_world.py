"""llm hello world example"""
# -*- coding: utf-8 -*-

import asyncio

from metacogitor.llm import LLM, Claude
from metacogitor.logs import logger


async def main():
    llm = LLM()
    claude = Claude()
    logger.info(await claude.aask("Hello, please introduce yourself"))
    logger.info(await llm.aask("hello world"))
    logger.info(await llm.aask_batch(["hi", "write python hello world."]))

    hello_msg = [{"role": "user", "content": "count from 1 to 10. split by newline."}]
    logger.info(await llm.acompletion(hello_msg))
    logger.info(await llm.acompletion_batch([hello_msg]))
    logger.info(await llm.acompletion_batch_text([hello_msg]))

    logger.info(await llm.acompletion_text(hello_msg))
    await llm.acompletion_text(hello_msg, stream=True)


if __name__ == "__main__":
    asyncio.run(main())
