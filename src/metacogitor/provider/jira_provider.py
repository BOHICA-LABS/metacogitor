"""JiraProvider is a wrapper around the Jira Python SDK."""
# -*- coding: utf-8 -*-

import jira

from metacogitor.provider.core.ticket_client import TicketClient
from metacogitor.config import CONFIG


class JiraProvider(TicketClient):
    """
    JiraProvider is a wrapper around the Jira Python SDK.

    It provides a simple interface to interact with Jira.
    """

    def __init__(self, url, username, api_token):
        """Initialize the JiraProvider instance.

        :param url: The URL of the Jira instance.
        :type url: str
        :param username: The username to authenticate with.
        :type username: str
        :param api_token: The API token to authenticate with.
        :type api_token: str
        """

        self.jira = jira.JIRA(url, basic_auth=(username, api_token))

    def get_ticket(self, issue_key):
        """Get a ticket by its key.

        :param issue_key: The key of the ticket to get.
        :type issue_key: str
        :return: The ticket.
        :rtype: jira.Issue
        """

        return self.jira.issue(issue_key)

    def get_tickets(self, jql, fields=None, max_results=100, **kwargs):
        """Get a list of tickets.

        :param jql: The JQL query to use to get the tickets.
        :type jql: str
        :param fields: The fields to include in the response.
        :type fields: list[str], optional
        :param max_results: The maximum number of results to return.
        :type max_results: int, optional
        :return: The list of tickets.
        :rtype: list[jira.Issue]
        """

        return self.jira.search_issues(
            jql, maxResults=max_results, fields=fields, **kwargs
        )

    def get_project(self, project_key):
        """Get a project by its key.

        :param project_key: The key of the project to get.
        :type project_key: str
        :return: The project.
        :rtype: jira.Project
        """

        return self.jira.project(project_key)

    def get_projects(self):
        """Get a list of projects.

        :return: The list of projects.
        :rtype: list[jira.Project]
        """

        return self.jira.projects()

    def get_versions(self, project):
        """Get a list of versions for a project.

        :param project: The project to get the versions for.
        :type project: jira.Project
        :return: The list of versions.
        :rtype: list[jira.Version]
        """

        return project.versions

    def add_comment(self, issue, comment):
        """Add a comment to a ticket.

        :param issue: The ticket to add the comment to.
        :type issue: jira.Issue
        :param comment: The comment to add.
        :type comment: str
        """

        self.jira.add_comment(issue, comment)

    def assign_ticket(self, issue, assignee):
        """Assign a ticket to a user.

        :param issue: The ticket to assign.
        :type issue: jira.Issue
        :param assignee: The user to assign the ticket to.
        :type assignee: str
        """

        self.jira.assign_issue(issue, assignee)

    def create_ticket(self, fields):
        """Create a ticket.

        :param fields: The fields to use to create the ticket.
        :type fields: dict
        :return: The created ticket.
        :rtype: jira.Issue
        """

        return self.jira.create_issue(fields=fields)

    def transition_ticket(self, issue, transition):
        """Transition a ticket.

        :param issue: The ticket to transition.
        :type issue: jira.Issue
        :param transition: The transition to perform.
        :type transition: str
        """

        self.jira.transition_issue(issue, transition)

    def get_ticket_transitions(self, issue):
        """Get the transitions for a ticket.

        :param issue: The ticket to get the transitions for.
        :type issue: jira.Issue
        :return: The list of transitions.
        :rtype: list[jira.Transition]
        """

        return self.jira.transitions(issue)

    def get_ticket_types(self):
        """Get the ticket types.

        :return: The list of ticket types.
        :rtype: list[jira.IssueType]
        """

        return self.jira.issue_types()

    def get_users(self):
        """Get the users.

        :return: The list of users.
        :rtype: list[jira.User]
        """

        return self.jira.search_users(query=None)

    def upload_attachment(self, issue, attachment):
        """Upload an attachment to a ticket.

        :param issue: The ticket to upload the attachment to.
        :type issue: jira.Issue
        :param attachment: The attachment to upload.
        :type attachment: str
        """

        self.jira.add_attachment(issue, attachment)

    def get_sprints(self, board_id: int, **kwargs):
        """Get the sprints for a board.

        :param board_id: The ID of the board to get the sprints for.
        :type board_id: int
        :return: The list of sprints.
        :rtype: list[jira.Sprint]
        """

        sprints = self.jira.sprints(board_id=board_id, **kwargs)
        """
        sprint_list = []
        for sprint in sprints:
            sprint_data = {
                "id": sprint.id,
                "name": sprint.name,
                "start_date": sprint.startDate.strftime("%Y-%m-%d") if sprint.startDate else None,
                "end_date": sprint.endDate.strftime("%Y-%m-%d") if sprint.endDate else None
            }
            sprint_list.append(sprint_data)
            """

        return sprints


JIRA_PROVIDER = None

if CONFIG.jira_url and CONFIG.jira_username and CONFIG.jira_api_token:
    JIRA_PROVIDER = JiraProvider(
        CONFIG.jira_url, CONFIG.jira_username, CONFIG.jira_api_token
    )
