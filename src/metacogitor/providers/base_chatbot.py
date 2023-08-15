#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/08/14 23:00
@Author  : Joshua Magady
@File    : base_chatbot.py
@Description: This defines the base chatbot class for the metacogitor project.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass

__ALL__ = ["BaseChatbot"]


@dataclass
class BaseChatbot(ABC):
    """
    Abstract base class for creating a GPT-based chatbot.
    """

    mode: str = "API"

    @abstractmethod
    def ask(self, msg: str) -> str:
        """
        Ask the GPT-based chatbot a question and receive an answer.

        :param msg: The input question.
        :return: The generated answer.
        """

        raise NotImplementedError("The ask method should be implemented in a subclass.")

    @abstractmethod
    def ask_batch(self, msgs: list) -> str:
        """
        Ask the GPT-based chatbot multiple questions and receive a series of answers.

        :param msgs: A list of input questions.
        :return: A series of generated answers as a concatenated string.
        """

        raise NotImplementedError(
            "The ask_batch method should be implemented in a subclass."
        )

    @abstractmethod
    def ask_code(self, msgs: list) -> str:
        """
        Ask the GPT-based chatbot multiple questions and receive a piece of code.

        :param msgs: A list of input questions.
        :return: A piece of generated code.
        """

        raise NotImplementedError(
            "The ask_code method should be implemented in a subclass."
        )
