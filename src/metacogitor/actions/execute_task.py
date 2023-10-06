"""ExecuteTask action module."""
# -*- coding: utf-8 -*-

from metacogitor.actions import Action
from metacogitor.schema import Message


class ExecuteTask(Action):
    """ExecuteTask action class."""

    def __init__(self, name="ExecuteTask", context: list[Message] = None, llm=None):
        """Initialize the ExecuteTask action class.

        :param name: The name of the action, defaults to "ExecuteTask"
        :type name: str, optional
        :param context: The context of the action, defaults to None
        :type context: list[Message], optional
        :param llm: The language model to use for the action, defaults to None
        :type llm: LanguageModel, optional
        """
        super().__init__(name, context, llm)

    def run(self, *args, **kwargs):
        """Run the action."""
        pass
