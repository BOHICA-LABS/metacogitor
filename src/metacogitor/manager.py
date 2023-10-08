"""
Manager is the core of the metacogitor system.
It is responsible for managing the flow of information between roles.
"""
# -*- coding: utf-8 -*-

from metacogitor.llm import LLM
from metacogitor.logs import logger
from metacogitor.schema import Message


class Manager:
    """Manager is the core of the metacogitor system.

    It is responsible for managing the flow of information between roles.

    Attributes:
        llm (LLM): The Large Language Model to use for decision making.
        role_directions (dict): A dictionary of role directions.
        prompt_template (str): The template to use for the LLM prompt.
    """

    def __init__(self, llm: LLM = LLM()):
        """Initialize the manager.

        :param llm: The Large Language Model to use for decision making.
        :type llm: LLM
        """

        self.llm = llm  # Large Language Model
        self.role_directions = {
            "BOSS": "Product Manager",
            "Product Manager": "Architect",
            "Architect": "Engineer",
            "Engineer": "QA Engineer",
            "QA Engineer": "Product Manager",
        }
        self.prompt_template = """
        Given the following message:
        {message}

        And the current status of roles:
        {roles}

        Which role should handle this message?
        """

    async def handle(self, message: Message, environment):
        """Handle a message.

        The administrator processes the information, now simply passes the information on to the next person

        :param message: The message to handle.
        :type message: Message
        :param environment: The environment to handle the message in.
        :type environment: Environment
        :return: The result of handling the message.
        :rtype: Any
        """

        # Get all roles from the environment
        roles = environment.get_roles()
        # logger.debug(f"{roles=}, {message=}")

        # Build a context for the LLM to understand the situation
        # context = {
        #     "message": str(message),
        #     "roles": {role.name: role.get_info() for role in roles},
        # }
        # Ask the LLM to decide which role should handle the message
        # chosen_role_name = self.llm.ask(self.prompt_template.format(context))

        # FIXME: The direction of flow is now determined by a simple dictionary, but there should still be a thought
        #  process afterwards

        next_role_profile = self.role_directions[message.role]
        # logger.debug(f"{next_role_profile}")
        for _, role in roles.items():
            if next_role_profile == role.profile:
                next_role = role
                break
        else:
            logger.error(f"No available role can handle message: {message}.")
            return

        # Find the chosen role and handle the message
        return await next_role.handle(message)
