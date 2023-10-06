"""Create Mermaid.js Diagram Action"""
# -*- coding: utf-8 -*-

from metacogitor.actions.action import Action, ActionOutput
from metacogitor.utils.common import OutputParser
from pydantic import BaseModel


class DiagramResults(BaseModel):
    """The results of the diagram generation."""

    diagram_type: str
    diagram: str


class CreateMermaidDiagram(Action):
    """Create Mermaid.js Diagram Action"""

    def __init__(self, name: str = "CreateMermaidDiagram", *args, **kwargs):
        """Initialize the action.

        :param name: The name of the action.
        :type name: str
        :param args: The positional arguments.
        :type args: list
        :param kwargs: The keyword arguments.
        :type kwargs: dict
        """
        super().__init__(name, *args, **kwargs)

    async def run(self, description: str, diagram_type: str) -> ActionOutput:
        """Run the action.

        :param description: The input text.
        :type description: str
        :param diagram_type: The diagram type.
        :type diagram_type: str
        :return: The action output.
        :rtype: ActionOutput
        """

        prompt = f"""
        Given the following context and diagram type:

        {description}

        diagram type: {diagram_type}

        Your task is to generate a Mermaid.js diagram representation of the information related to the context using the
        diagram type. This diagram should visually represent various facets of the information, including relationships,
        hierarchies, processes, and components.

        The diagram should be formatted in a string that follows the Mermaid.js syntax conventions. Each section of the
        diagram should clearly convey the relevant information and its relationship to other parts of the diagram.
        Here's an example:

        javascript```
        graph TD;
            A[Core principles of Mermaid.js];
            B[Applications of Mermaid.js];
            C[Comparison with other diagramming tools];
            D[Evolution and updates in Mermaid.js];
            E[Real-world case studies using Mermaid.js];

            A --> B;
            A --> C;
            A --> D;
            A --> E;
            C --> |"Explores differences"| E;
        ```

        Remember, each section of the diagram should encapsulate the core ideas from the context and visually represent
        the relevant information on the topic. You may creatively expand on ideas and concepts when necessary. If the
        context is too subjective or interpretative to create a section in the diagram, represent that with an isolated
        node and explain its lack of connection. Return only the javascript code block with the diagram. No additional
        supporting detail that's not contained in the code block should be returned.
        """

        diagram = await self._aask(prompt)
        result = OutputParser.parse_code(diagram, "javascript")

        return ActionOutput(
            content="Diagram Completed",
            instruct_content=DiagramResults(diagram_type=diagram_type, diagram=result),
        )


# Example of usage:
if __name__ == "__main__":
    import asyncio

    # Create diagram action
    action = CreateMermaidDiagram()

    # Example context
    # context = "User Authentication process"
    context = f"""
    The Identity and Access Management (IAM) Microservice is a critical component of modern software architecture, designed to securely manage user identities and control access to resources within a system or application. This microservice plays a pivotal role in ensuring that only authorized users can interact with the system's resources and data while maintaining a high degree of security, scalability, and flexibility. Let's delve into the detailed components and workings of the IAM Microservice.

1. Authentication Component:

Purpose: The authentication component is the front door of the IAM Microservice. It verifies the identity of users or entities trying to access the system.
How it works: When a user initiates a login request, the authentication component validates their credentials, such as username and password, or more advanced methods like multi-factor authentication (MFA). Once validated, it generates an authentication token, which represents the user's authenticated session.
2. Authorization Component:

Purpose: The authorization component is responsible for determining what actions a user or entity can perform within the system.
How it works: It checks the user's permissions and roles against an access control list (ACL) or policy database. Based on this information, it decides whether to grant or deny access to specific resources or actions.
3. User Management Component:

Purpose: This component manages user accounts and their associated information.
How it works: It handles user registration, profile management, and password resets. It can also integrate with external identity providers (like LDAP, OAuth, or SAML) to streamline user onboarding and authentication processes.
4. Token Management Component:

Purpose: Tokens play a crucial role in secure user sessions and API interactions.
How it works: The token management component generates and validates tokens, including authentication tokens (JWTs), session tokens, and API tokens. It ensures tokens are properly signed and encrypted to prevent tampering.
5. Logging and Auditing Component:

Purpose: Security and compliance are paramount in IAM. This component tracks and logs all access attempts and changes to user permissions.
How it works: It records details about authentication and authorization events, providing an audit trail that can be used for security analysis, debugging, and compliance reporting.
6. Role-Based Access Control (RBAC) Component:

Purpose: RBAC simplifies access control by assigning permissions to roles rather than individual users.
How it works: Users are assigned one or more roles, each with specific permissions. This component handles role assignment, ensuring that users receive the appropriate access rights based on their job responsibilities.
7. Single Sign-On (SSO) Component:

Purpose: SSO streamlines user access by allowing them to log in once and access multiple interconnected applications without re-entering credentials.
How it works: It utilizes protocols like OAuth2, OpenID Connect, or SAML to facilitate secure authentication and user information exchange between applications, removing the need for redundant logins.
8. Scalability and Load Balancing Component:

Purpose: As user loads vary, the IAM Microservice needs to scale horizontally and distribute traffic effectively.
How it works: This component employs load balancers and auto-scaling mechanisms to ensure high availability and performance even during traffic spikes.
9. Security and Encryption Component:

Purpose: Security is paramount in IAM. This component ensures data is stored and transmitted securely.
How it works: It implements encryption (both in transit and at rest), security best practices, and monitors for potential threats, such as brute force attacks or unauthorized access attempts.
10. API and Integration Layer:

Purpose: The IAM Microservice should offer APIs for other services to interact with.
How it works: It provides a well-documented set of APIs for user and permission management, making it easy for other microservices or external systems to integrate and interact securely with the IAM Microservice.
Design and Functionality Concepts:

Modularity: The IAM Microservice is designed as a set of loosely coupled components, making it easier to maintain, scale, and update individual parts of the system without disrupting the entire IAM infrastructure.

Scalability: The microservice architecture allows for horizontal scaling of components, ensuring that the IAM system can handle growing numbers of users and requests seamlessly.

Security: Security is ingrained in every aspect of the IAM Microservice, from encryption and token management to access control and auditing. It follows industry best practices to protect sensitive user data.

Flexibility: The IAM Microservice is designed to be flexible and extensible, allowing organizations to adapt it to their specific security and access control requirements.

User Experience: A well-designed IAM Microservice prioritizes a smooth and user-friendly authentication and authorization experience, minimizing friction for legitimate users while maintaining security.

In summary, the Identity and Access Management Microservice is a multifaceted system designed to ensure secure and efficient user authentication, authorization, and management within a larger software ecosystem. Its various components work together harmoniously to create a robust security infrastructure, safeguarding valuable data and resources while providing a seamless experience for users and developers alike.
    """

    # Generate class diagram
    output = asyncio.run(action.run(context, "class"))
    print(output.instruct_content.diagram)

    # Generate sequence diagram
    output = asyncio.run(action.run(context, "sequence"))
    print(output.instruct_content.diagram)
