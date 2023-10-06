#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/11 17:44
@Author  : alexanderwu
@File    : __init__.py
"""
from enum import Enum

from metacogitor.actions.action import Action
from metacogitor.actions.action_output import ActionOutput
from metacogitor.actions.add_requirement import BossRequirement
from metacogitor.actions.debug_error import DebugError
from metacogitor.actions.design_api import WriteDesign
from metacogitor.actions.design_api_review import DesignReview
from metacogitor.actions.design_filenames import DesignFilenames
from metacogitor.actions.project_management import AssignTasks, WriteTasks
from metacogitor.actions.research import (
    CollectLinks,
    WebBrowseAndSummarize,
    ConductResearch,
)
from metacogitor.actions.run_code import RunCode
from metacogitor.actions.search_and_summarize import SearchAndSummarize
from metacogitor.actions.write_code import WriteCode
from metacogitor.actions.write_code_review import WriteCodeReview
from metacogitor.actions.write_prd import WritePRD
from metacogitor.actions.write_prd_review import WritePRDReview
from metacogitor.actions.write_test import WriteTest
from metacogitor.actions.youtube_download import YouTubeDownloadAction
from metacogitor.actions.extract_audio import ExtractAudioFromVideoAction
from metacogitor.actions.local_transcribe import LocalTranscribe
from metacogitor.actions.write_atomic_notes import WriteAtomicNotes


class ActionType(Enum):
    """All types of Actions, used for indexing."""

    ADD_REQUIREMENT = BossRequirement
    WRITE_PRD = WritePRD
    WRITE_PRD_REVIEW = WritePRDReview
    WRITE_DESIGN = WriteDesign
    DESIGN_REVIEW = DesignReview
    DESIGN_FILENAMES = DesignFilenames
    WRTIE_CODE = WriteCode
    WRITE_CODE_REVIEW = WriteCodeReview
    WRITE_TEST = WriteTest
    RUN_CODE = RunCode
    DEBUG_ERROR = DebugError
    WRITE_TASKS = WriteTasks
    ASSIGN_TASKS = AssignTasks
    SEARCH_AND_SUMMARIZE = SearchAndSummarize
    COLLECT_LINKS = CollectLinks
    WEB_BROWSE_AND_SUMMARIZE = WebBrowseAndSummarize
    CONDUCT_RESEARCH = ConductResearch
    YOUTUBE_DOWNLOAD = YouTubeDownloadAction
    EXTRACT_AUDIO = ExtractAudioFromVideoAction
    LOCAL_TRANSCRIBE = LocalTranscribe
    WRITE_ATOMIC_NOTES = WriteAtomicNotes


__all__ = [
    "ActionType",
    "Action",
    "ActionOutput",
]
