"""Skill manager, used to manage all skills"""
# -*- coding: utf-8 -*-

from metacogitor.actions import Action
from metacogitor.const import PROMPT_PATH
from metacogitor.document_store.chromadb_store import ChromaStore
from metacogitor.llm import LLM
from metacogitor.logs import logger

Skill = Action


class SkillManager:
    """Used to manage all skills

    Attributes:
        _llm (LLM): Language model
        _store (ChromaStore): ChromaStore
        _skills (dict[str:Skill]): Skill pool
    """

    def __init__(self):
        self._llm = LLM()
        self._store = ChromaStore("skill_manager")
        self._skills: dict[str:Skill] = {}

    def add_skill(self, skill: Skill):
        """Add a skill, add the skill to the skill pool and searchable storage

        :param skill: Skill
        :type skill: Skill
        :return: None
        :rtype: None
        """
        self._skills[skill.name] = skill
        self._store.add(skill.desc, {}, skill.name)

    def del_skill(self, skill_name: str):
        """Delete a skill, remove the skill from the skill pool and searchable storage

        :param skill_name: Skill name
        :type skill_name: str
        :return: None
        :rtype: None
        """

        self._skills.pop(skill_name)
        self._store.delete(skill_name)

    def get_skill(self, skill_name: str) -> Skill:
        """Obtain a specific skill by skill name

        :param skill_name: Skill name
        :type skill_name: str
        :return: Skill
        :rtype: Skill
        """

        return self._skills.get(skill_name)

    def retrieve_skill(self, desc: str, n_results: int = 2) -> list[Skill]:
        """Obtain skills through the search engine

        :param desc: Skill description
        :type desc: str
        :param n_results: Number of results
        :type n_results: int
        :return: Multiple skills
        :rtype: list[Skill]
        """

        return self._store.search(desc, n_results=n_results)["ids"][0]

    def retrieve_skill_scored(self, desc: str, n_results: int = 2) -> dict:
        """Obtain skills through the search engine

        :param desc: Skill description
        :type desc: str
        :return: Dictionary consisting of skills and scores
        :rtype: dict
        """

        return self._store.search(desc, n_results=n_results)

    def generate_skill_desc(self, skill: Skill) -> str:
        """Generate descriptive text for each skill

        :param skill: The skill to generate the description for
        :type skill: Skill
        :return: The generated description
        :rtype: str
        """

        path = PROMPT_PATH / "generate_skill.md"
        text = path.read_text()
        logger.info(text)


if __name__ == "__main__":
    manager = SkillManager()
    manager.generate_skill_desc(Action())
