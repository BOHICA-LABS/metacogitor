"""Create System Description Action."""
# -*- coding: utf-8 -*-

from metacogitor.actions.action import Action, ActionOutput
from metacogitor.utils.common import OutputParser
from pydantic import BaseModel


class SystemDescriptionResults(BaseModel):
    """The results of the CreateSystemDescription action."""

    system_context: str
    system_description: str


class CreateSystemDescription(Action):
    def __init__(self, name: str = "CreateSystemDescription", *args, **kwargs):
        """Initializes the CreateSystemDescription action.

        :param name: The name of the action.
        :type name: str
        :param args: The arguments to pass to the action.
        :type args: list
        :param kwargs: The keyword arguments to pass to the action.
        :type kwargs: dict
        """
        super().__init__(name, *args, **kwargs)

    async def run(self, system: str) -> ActionOutput:
        """Runs the action to generate search queries.

        :param system: The system to describe.
        :type system: str
        :param context: The context of the system.
        :type context: str
        :return: The results of the action.
        :rtype: ActionOutput
        """

        # TODO: Provide better examples for few shot learning. Revamp the prompt to be clearer. Create a seperate
        # action for generating all the microservices that would make up the system. Then use that to generate the
        # system description.
        # Should follow the format of of our other prompt based actions. the one below is weak.

        prompt = f"""
        Provide a detailed description of the {system}. You should describe each component of the {system} in detail and
        explain how these components work together to enable the {system}'s operation. Elaborate on the concepts and
        ideas behind the {system}'s design and functionality, ensuring a comprehensive understanding of the {system}'s
        overall operation. Feel free to use creative descriptions as necessary to clarify complex aspects of the
        {system}. Your response should be formatted as a markdown document. The example should not be used verbatim,

        Here's an example of the format based on Identity and Access Management (IAM) Microservice:



        ```markdown
        The Identity and Access Management (IAM) Microservice is a critical component of modern software architecture,
        designed to securely manage user identities and control access to resources within a system or application. This
        microservice plays a pivotal role in ensuring that only authorized users can interact with the system's
        resources and data while maintaining a high degree of security, scalability, and flexibility. Let's delve into
        the detailed components and workings of the IAM Microservice.

        1. Authentication Component:
        Purpose: The authentication component is the front door of the IAM Microservice. It verifies the identity of
        users or entities trying to access the system.
        How it works: When a user initiates a login request, the authentication component validates their credentials,
        such as username and password, or more advanced methods like multi-factor authentication (MFA). Once validated,
        it generates an authentication token, which represents the user's authenticated session.

        2. Authorization Component:
        Purpose: The authorization component is responsible for determining what actions a user or entity can perform
        within the system.
        How it works: It checks the user's permissions and roles against an access control list (ACL) or policy database.
        Based on this information, it decides whether to grant or deny access to specific resources or actions.

        3. User Management Component:
        Purpose: This component manages user accounts and their associated information.
        How it works: It handles user registration, profile management, and password resets. It can also integrate with
        external identity providers (like LDAP, OAuth, or SAML) to streamline user onboarding and authentication
        processes.

        4. Token Management Component:
        Purpose: Tokens play a crucial role in secure user sessions and API interactions.
        How it works: The token management component generates and validates tokens, including authentication tokens
        (JWTs), session tokens, and API tokens. It ensures tokens are properly signed and encrypted to prevent tampering.

        5. Logging and Auditing Component:
        Purpose: Security and compliance are paramount in IAM. This component tracks and logs all access attempts and
        changes to user permissions.
        How it works: It records details about authentication and authorization events, providing an audit trail that
        can be used for security analysis, debugging, and compliance reporting.

        6. Role-Based Access Control (RBAC) Component:
        Purpose: RBAC simplifies access control by assigning permissions to roles rather than individual users.
        How it works: Users are assigned one or more roles, each with specific permissions. This component handles role
        assignment, ensuring that users receive the appropriate access rights based on their job responsibilities.

        7. Single Sign-On (SSO) Component:
        Purpose: SSO streamlines user access by allowing them to log in once and access multiple interconnected
        applications without re-entering credentials.
        How it works: It utilizes protocols like OAuth2, OpenID Connect, or SAML to facilitate secure authentication and
        user information exchange between applications, removing the need for redundant logins.

        8. Scalability and Load Balancing Component:
        Purpose: As user loads vary, the IAM Microservice needs to scale horizontally and distribute traffic
        effectively.
        How it works: This component employs load balancers and auto-scaling mechanisms to ensure high availability and
        performance even during traffic spikes.

        9. Security and Encryption Component:
        Purpose: Security is paramount in IAM. This component ensures data is stored and transmitted securely.
        How it works: It implements encryption (both in transit and at rest), security best practices, and monitors for
        potential threats, such as brute force attacks or unauthorized access attempts.

        10. API and Integration Layer:
        Purpose: The IAM Microservice should offer APIs for other services to interact with.
        How it works: It provides a well-documented set of APIs for user and permission management, making it easy for
        other microservices or external systems to integrate and interact securely with the IAM Microservice.

        Design and Functionality Concepts:
        Modularity: The IAM Microservice is designed as a set of loosely coupled components, making it easier to
        maintain, scale, and update individual parts of the system without disrupting the entire IAM infrastructure.

        Scalability: The microservice architecture allows for horizontal scaling of components, ensuring that the IAM
        system can handle growing numbers of users and requests seamlessly.

        Security: Security is ingrained in every aspect of the IAM Microservice, from encryption and token management to
        access control and auditing. It follows industry best practices to protect sensitive user data.

        Flexibility: The IAM Microservice is designed to be flexible and extensible, allowing organizations to adapt it
        to their specific security and access control requirements.

        User Experience: A well-designed IAM Microservice prioritizes a smooth and user-friendly authentication and
        authorization experience, minimizing friction for legitimate users while maintaining security.

        In summary, the Identity and Access Management Microservice is a multifaceted system designed to ensure secure
        and efficient user authentication, authorization, and management within a larger software ecosystem. Its various
        components work together harmoniously to create a robust security infrastructure, safeguarding valuable data and
        resources while providing a seamless experience for users and developers alike.
        ```
        """

        system_description = await self._aask(prompt)
        result = OutputParser.parse_str(system_description)

        return ActionOutput(
            content="System Description Created",
            instruct_content=SystemDescriptionResults(
                system_context=system, system_description=result
            ),
        )


# Example of usage:
if __name__ == "__main__":
    import asyncio

    # Create diagram action
    action = CreateSystemDescription()

    # Example context
    # context = "User Authentication process"
    context1 = f"""
    Identity and Access Management (IAM) Microservice Architecture (MSA) is a microservice architecture that enables
    the management of user identities and access to resources in a distributed environment. IAM MSA is a collection of
    microservices that work together to provide a secure and scalable solution for managing user identities and access
    to resources in a distributed environment.
    """

    context2 = f"""
    Authentication Microservice is responsible for authenticating users and providing them with access to resources. It
    is responsible for authenticating users and providing them with access to resources.
    """

    # Generate class diagram
    output = asyncio.run(action.run(context1))
    print(output.instruct_content.system_description)

    # Generate sequence diagram
    output = asyncio.run(action.run(context2))
    print(output.instruct_content.system_description)
