from abc import ABC

from metacogitor.providers import BaseChatbot
import pytest


class MockBaseChatBot(
    BaseChatbot
):  # Create an implementation of the BaseChatbot class for testing purposes
    def ask(self, msg: str) -> str:
        """Ask GPT a question and get an answer"""
        raise NotImplementedError("The method should be implemented in a subclass.")

    def ask_batch(self, msgs: list) -> str:
        """Ask GPT multiple questions and get a series of answers"""
        raise NotImplementedError("The method should be implemented in a subclass.")

    def ask_code(self, msgs: list) -> str:
        """Ask GPT multiple questions and get a piece of code"""
        raise NotImplementedError("The method should be implemented in a subclass.")


@pytest.fixture
def mock_chatbot():
    return MockBaseChatBot()


class TestBaseChatbot:
    def test_ask_abstract_method(self, mock_chatbot):
        with pytest.raises(NotImplementedError):
            mock_chatbot.ask("What's the weather today?")

    def test_ask_batch_abstract_method(self, mock_chatbot):
        with pytest.raises(NotImplementedError):
            mock_chatbot.ask_batch(["How are you?", "What's your name?"])

    def test_ask_code_abstract_method(self, mock_chatbot):
        with pytest.raises(NotImplementedError):
            mock_chatbot.ask_code(["How does this work?", "Show me an example code."])
