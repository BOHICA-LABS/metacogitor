"""Simple example of how to use the semantic kernel to create an agent."""
# -*- coding: utf-8 -*-

import asyncio

from semantic_kernel.core_skills import FileIOSkill, MathSkill, TextSkill, TimeSkill
from semantic_kernel.planning import SequentialPlanner

# from semantic_kernel.planning import SequentialPlanner
from semantic_kernel.planning.action_planner.action_planner import ActionPlanner

from metacogitor.actions import BossRequirement
from metacogitor.const import SKILL_DIRECTORY
from metacogitor.roles.sk_agent import SkAgent
from metacogitor.schema import Message
from metacogitor.tools.search_engine import SkSearchEngine


async def main():
    # await basic_planner_example()
    # await action_planner_example()

    # await sequential_planner_example()
    await basic_planner_web_search_example()


async def basic_planner_example():
    task = """
    Tomorrow is Valentine's day. I need to come up with a few date ideas. She speaks French so write it in French.
    Convert the text to uppercase"""
    role = SkAgent()

    # let's give the agent some skills
    role.import_semantic_skill_from_directory(SKILL_DIRECTORY, "SummarizeSkill")
    role.import_semantic_skill_from_directory(SKILL_DIRECTORY, "WriterSkill")
    role.import_skill(TextSkill(), "TextSkill")
    # using BasicPlanner
    await role.run(Message(content=task, cause_by=BossRequirement))


async def sequential_planner_example():
    task = """
    Tomorrow is Valentine's day. I need to come up with a few date ideas. She speaks French so write it in French.
    Convert the text to uppercase"""
    role = SkAgent(planner_cls=SequentialPlanner)

    # let's give the agent some skills
    role.import_semantic_skill_from_directory(SKILL_DIRECTORY, "SummarizeSkill")
    role.import_semantic_skill_from_directory(SKILL_DIRECTORY, "WriterSkill")
    role.import_skill(TextSkill(), "TextSkill")
    # using BasicPlanner
    await role.run(Message(content=task, cause_by=BossRequirement))


async def basic_planner_web_search_example():
    task = """
    Question: Who made the 1989 comic book, the film version of which Jon Raymond Polito appeared in?"""
    role = SkAgent()

    role.import_skill(SkSearchEngine(), "WebSearchSkill")
    # role.import_semantic_skill_from_directory(skills_directory, "QASkill")

    await role.run(Message(content=task, cause_by=BossRequirement))


async def action_planner_example():
    role = SkAgent(planner_cls=ActionPlanner)
    # let's give the agent 4 skills
    role.import_skill(MathSkill(), "math")
    role.import_skill(FileIOSkill(), "fileIO")
    role.import_skill(TimeSkill(), "time")
    role.import_skill(TextSkill(), "text")
    task = "What is the sum of 110 and 990?"
    await role.run(
        Message(content=task, cause_by=BossRequirement)
    )  # it will choose mathskill.Add


if __name__ == "__main__":
    asyncio.run(main())
