#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/8/15 11:59
@Author  : Joshua Magady
@File    : const.py
@Description: This defines the constants for the metacogitor project.
"""
from pathlib import Path

# TODO: Review the functionality of this module.
def get_project_root():
    """
    Recursively search upwards to find the project root directory.

    :return: Path to the project root directory.
    :raises: Exception if project root is not found.
    """

    current_path = Path.cwd()
    while True:
        if (
            (current_path / ".git").exists()
            or (current_path / ".project_root").exists()
            or (current_path / ".gitignore").exists()
        ):
            return current_path
        parent_path = current_path.parent
        if parent_path == current_path:
            raise Exception("Project root not found.")
        current_path = parent_path


PROJECT_ROOT = get_project_root()
DATA_PATH = PROJECT_ROOT / "data"
WORKSPACE_ROOT = PROJECT_ROOT / "workspace"
PROMPT_PATH = PROJECT_ROOT / "metacogitor/prompts"
UT_PATH = PROJECT_ROOT / "data/ut"
SWAGGER_PATH = UT_PATH / "files/api/"
UT_PY_PATH = UT_PATH / "files/ut/"
API_QUESTIONS_PATH = UT_PATH / "files/question/"
TMP = PROJECT_ROOT / "tmp"
RESEARCH_PATH = DATA_PATH / "research"

MEM_TTL = 24 * 30 * 3600
