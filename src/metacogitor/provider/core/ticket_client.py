from abc import ABC, abstractmethod

__ALL__ = ["TicketClient"]


class TicketClient(ABC):

    @abstractmethod
    def __init__(self, jira_url, username, api_token):
        pass

    @abstractmethod
    def get_ticket(self, ticket_key):
        pass

    @abstractmethod
    def get_tickets(self, jql, fields=None):
        pass

    @abstractmethod
    def get_project(self, project_key):
        pass

    @abstractmethod
    def get_projects(self):
        pass

    @abstractmethod
    def get_versions(self, project):
        pass

    @abstractmethod
    def add_comment(self, ticket, comment):
        pass

    @abstractmethod
    def assign_ticket(self, ticket, assignee):
        pass

    @abstractmethod
    def create_ticket(self, fields):
        pass

    @abstractmethod
    def transition_ticket(self, ticket, transition):
        pass

    @abstractmethod
    def get_ticket_transitions(self, ticket):
        pass

    @abstractmethod
    def get_ticket_types(self):
        pass

    @abstractmethod
    def get_users(self):
        pass

    @abstractmethod
    def upload_attachment(self, ticket, attachment):
        pass