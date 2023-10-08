"""Write a tutorial about MySQL."""
# _*_ coding: utf-8 _*_

import asyncio

from metacogitor.roles.tutorial_assistant import TutorialAssistant


async def main():
    topic = "Write a tutorial about MySQL"
    role = TutorialAssistant(language="Chinese")
    await role.run(topic)


if __name__ == "__main__":
    asyncio.run(main())