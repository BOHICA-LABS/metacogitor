"""Researcher role example."""
# -*- coding: utf-8 -*-

import asyncio

from metacogitor.roles.researcher import RESEARCH_PATH, Researcher


async def main():
    topic = "dataiku vs. datarobot"
    role = Researcher(language="en-us")
    await role.run(topic)
    print(f"save report to {RESEARCH_PATH / f'{topic}.md'}.")


if __name__ == "__main__":
    asyncio.run(main())
