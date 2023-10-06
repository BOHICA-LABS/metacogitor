"""Get all Jira tickets for a given project key"""
# -*- coding: utf-8 -*-

import jira

from metacogitor.actions import Action, ActionOutput
from metacogitor.provider.jira_provider import JIRA_PROVIDER
from metacogitor.logs import logger
from metacogitor.schema import Message
from pydantic import BaseModel
from typing import List


class JiraTicketResults(BaseModel):
    """Jira ticket results"""

    project_key: str
    tickets: List


class GetAllJiraTickets(Action):
    """Get all Jira tickets for a given project key"""

    def __init__(self, name: str = "GetAllJiraTickets", context=None, llm=None):
        """Initialize the GetAllJiraTickets action class.

        :param name: The name of the action, defaults to "GetAllJiraTickets"
        :type name: str, optional
        :param context: The context for the action, defaults to None
        :type context: dict, optional
        :param llm: The low-level model for the action, defaults to None
        :type llm: dict, optional
        """
        super().__init__(name, context, llm)

    async def run(self, project_key: str):
        """Runs the action to get all Jira tickets for a given project key.

        :param project_key: The project key to get tickets for.
        :type project_key: str
        :return: The action output.
        :rtype: ActionOutput
        """

        if JIRA_PROVIDER is None:
            raise Exception("Jira provider is not configured")

        tickets = []
        while issues_chunk := JIRA_PROVIDER.get_tickets(
            jql=f"project = {project_key}", max_results=100, startAt=len(tickets)
        ):
            logger.info(f"Got {len(issues_chunk)} tickets")
            tickets.extend(issues_chunk)
        logger.info(f"Got {len(tickets)} tickets in total")

        return ActionOutput(
            content="Ticket Retrival Completed",
            instruct_content=JiraTicketResults(
                project_key=project_key, tickets=tickets
            ),
        )


if __name__ == "__main__":
    import asyncio

    action = GetAllJiraTickets()
    results = asyncio.run(action.run(project_key="INFRA"))
    print(results)
