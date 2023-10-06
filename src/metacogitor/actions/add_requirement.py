#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/20 17:46
@Author  : alexanderwu
@File    : add_requirement.py
"""
from metacogitor.actions import Action


class BossRequirement(Action):
    """Boss Requirement without any implementation details"""

    async def run(self, *args, **kwargs):
        """Run the action

        :param args: The arguments to run the action with
        :param kwargs: The keyword arguments to run the action with
        :return: The result of running the action
        """
        raise NotImplementedError
