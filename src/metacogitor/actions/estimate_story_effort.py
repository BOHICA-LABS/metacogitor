"""Estimate Story Effort Action."""
# -*- coding: utf-8 -*-

from metacogitor.actions.action import Action, ActionOutput
from metacogitor.utils.common import OutputParser
from pydantic import BaseModel
from typing import Optional, Dict, Any


class EstimateStoryEffortResults(BaseModel):
    """The results of the EstimateStoryEffort action."""

    estimate: Dict[str, Any]


class TicketModel(BaseModel):
    """The ticket model."""

    summary: str
    description: Optional[str]
    priority: Optional[str]
    status: Optional[str]
    assignee: Optional[str]


class EstimateStoryEffort(Action):
    """Estimate Story Effort Action"""

    def __init__(self, name: str = "EstimateStoryEffort", *args, **kwargs):
        """Initialize the EstimateStoryEffort action.

        :param name: The name of the action.
        :param context: The context of the action.
        :param llm: The language model to use for the action.
        """
        super().__init__(name, *args, **kwargs)

    async def run(self, ticket: TicketModel, description: str) -> ActionOutput:
        """Runs the action to generate search queries.

        :param ticket: The ticket to estimate the effort for.
        :param description: Additional context needed to estimate the effort.
        :return: The action output.
        :rtype: ActionOutput
        """

        prompt = f"""
Given the detailed ticket information and additional context provided:

Ticket Information:
- Summary: {ticket.summary}
- Description: {ticket.description}
- Priority: {ticket.priority}
- Status: {ticket.status}
- Assignee: {ticket.assignee}

Additional Context: {description}

Your role is to estimate the effort required to resolve the ticket, represented by a number from the
sequence 0.5, 1, 2, 3, 5, 8, 13, 20, 40, 100. This Fibonacci series implies an escalating complexity
with each step.

The following is the definition, description, and example tasks of each number in the sequence:

1. 0.5:
    * Definition: Trivial complexity.
    * Description: Tasks that are almost non-existent in terms of complexity. They might be very
      routine or have been done numerous times by the team. Often quick fixes or tiny adjustments.
    * Examples:
        - Adjust a setting in the AWS Management Console.
        - Change a single line of code.
        - Change a single line of copy.
        - Update documentation for a cloud deployment process.
        - Modify a minor configuration in a .gitignore file for GitOps.
        - Update a comment in a cloud deployment script.
        - Fixing a typo in the UI or documentation.
    * Base Load Hours: 0.5 - 3.0
2. 1:
    * Definition: Very low complexity.
    * Description: Tasks that are straightforward and don’t require much effort or thought. Examples
      could include minor bug fixes or small adjustments to existing features.
    * Examples:
        - Fix a bug in a cloud deployment script.
        - Create a new user in the AWS Management Console with basic IAM permissions.
        - Updating a link on a webpage.
        - Create a new user with specific IAM permissions in AWS.
        - Pull the latest changes from a Git repository and review changes.
        - Assign static IP to an on-prem server.
    * Base Load Hours: 3.0 - 8.0
3. 2:
    * Definition: Low complexity.
    * Description: Tasks that are relatively simple but may require a bit more effort than the most
      straightforward tasks. Examples might be simple enhancements or changes to existing functionality.
    * Examples:
        - Add a new field to a form.
        - Add a new column to a database table.
        - Adding a new button to a form that triggers an existing function.
        - Set up a basic CloudWatch alarm in AWS.
        - Clone and set up a basic CI/CD pipeline for a new project using Jenkins.
        - Patch a non-critical software update on an on-prem server.
    * Base Load Hours: 8.0 - 16.0
4. 3:
    * Definition: Moderate complexity.
    * Description: Tasks that are more involved than the low complexity ones but aren't too challenging.
      They might require a better understanding of the system or more intricate changes.
    * Examples:
        - Modifying a small feature, like changing the way a date picker behaves.
        - Configure auto-scaling for an existing cloud service.
        - Set up a simple GitOps workflow using GitHub Actions.
        - Install and configure a new utility software on an on-prem server.
    * Base Load Hours: 16.0 - 24.0
5. 5:
    * Definition: Medium complexity.
    * Description: Tasks that require a significant amount of effort and understanding. They might span
      across different parts of the system and involve multiple steps.
    * Examples:
        - Designing and implementing a new contact form on a website.
        - Deploy a new microservice on AWS Lambda and API Gateway.
        - Implement a blue-green deployment strategy for an application using GitOps.
        - Set up and configure a new on-prem database server.
    * Base Load Hours: 24.0 - 40.0
6. 8:
    * Definition: High complexity.
    * Description: Tasks that are quite challenging, requiring comprehensive knowledge of the system
      and possibly integrating multiple components. There's a level of uncertainty involved.
    * Examples:
        - Designing and implementing a new feature.
        - Integrating a third-party payment gateway into an e-commerce site.
        - Implement a basic disaster recovery process for cloud resources.
        - Integrate and automate deployments across multiple Kubernetes clusters using ArgoCD.
        - Migrate a moderately complex application from on-prem to a cloud provider.
    * Base Load Hours: 40.0 - 80.0
7. 13:
    * Definition: Very high complexity.
    * Description: Tasks that are complex and could span multiple sprints. These are tasks that might
      need to be broken down further or require extensive research and understanding.
    * Examples:
        - Designing and implementing a new feature that requires a lot of research and understanding.
        - Integrating a new third-party service into an existing system.
        - Refactoring a significant portion of the codebase to optimize performance.
        - Design and set up a new VPC in AWS with proper subnetting, security groups, and IAM roles.
        - Architect and implement a GitOps-driven multi-environment (staging, production) workflow.
        - Upgrade and optimize an on-prem server cluster for better performance.
    * Base Load Hours: 80.0 - 120.0
8. 20:
    * Definition: Significant complexity.
    * Description: Tasks that are mammoth in size, likely needing to be broken down. They're full of
      unknowns and uncertainties, requiring a lot of time and effort to grasp.
    * Examples:
        - Designing and implementing a new feature that requires a lot of research and understanding.
        - Implementing user authentication from scratch, including sign up, login, and password
          recovery.
        - Set up and configure a multi-account AWS organization with centralized logging and monitoring.
        - Integrate multiple microservices into a seamless CI/CD GitOps pipeline with rollback
          capabilities.
        - Plan and execute the integration of on-prem Active Directory with cloud services.
    * Base Load Hours: 120.0 - 160.0
9. 40:
    * Definition: Extreme complexity.
    * Description: Tasks that are so complex they're almost off the charts. They might require deep
      dives, spikes, or prototypes to understand and tackle. Teams should be wary of such large
      estimates.
    * Examples:
        - Designing and developing a new module for an ERP system, like a HR module.
        - Architect and deploy a globally distributed cloud application with CDN integration, data
          replication, and failover strategy.
        - Implement a comprehensive GitOps strategy across multiple teams, repositories, and cloud
          providers.
        - Migrate a set of legacy on-prem applications to containerized solutions in the cloud.
    * Base Load Hours: 160.0 - 200.0
10. 100:
    * Definition: Monumental complexity.
    * Description: A task so big and filled with uncertainties that it's almost considered a project in
      itself. It's a red flag for something that likely needs to be broken down further or requires a
      rethinking of approach.
    * Examples:
        - Building a new, minimal viable product (MVP) version of a mobile application.
        - Design and implement a hybrid-cloud solution combining resources from AWS, Azure, and on-prem,
          ensuring seamless data flow and fault tolerance.
        - Establish a GitOps center of excellence, standardizing practices, tools, and workflows across
          an organization.
        - Strategize and execute a massive migration of multiple data centers, applications, and
          workflows to a unified cloud platform.
    * Base Load Hours: 200.0 - 320.0+

The complexity level could be influenced by unique problems, significant uncertainties, new vendor
integrations, intricate business rules, inter-system coordination (such as front-end, back-end, and
database coordination), large cloud deployments, and so on. For example, a simple copy change where the
exact copy is known and the process for implementing it is well-established might be rated as 1.
Conversely, a score of 100 would be allocated for substantial or complicated issues that would ideally
be divided into several tickets.

Your response should be a python dictionary with the following keys: "effort", "reason", "assumptions".
Estimate should only contain a number from the provided sequence. A detailed and concise reason,
explaining why the number from the sequence was chosen. If you are unable to determine the estimate
based on the details provided, create assumptions for the ticket using the context provided along with your own
creativity until you can create an estimate and place it in the assumptions list key. It's paramount to ensure that the
effort number is valid from the list as well as documenting all assumptions made. Any text you respond with needs be
located in the dictionary under the correct key.

Example of a response:

```python
{{
  "effort": "number from sequence">,
  "reason": "explanation of why the sequence number was chosen"
  "assumptions": [
    "assumption 1",
    "assumption 2",
    "assumption 3",
    "assumption 4"
    # More assumptions can be added if needed
  ]
}}
```
        """

        estimate = await self._aask(prompt)
        result = OutputParser.extract_struct(estimate, Dict)

        return ActionOutput(
            content="Ticket Estimate Completed",
            instruct_content=EstimateStoryEffortResults(estimate=result),
        )


# Example of usage:
if __name__ == "__main__":
    import asyncio

    from metacogitor.actions.get_all_jira_tickets import GetAllJiraTickets

    mss_description = """
Technical Overview of Our MSSP System

Our MSSP system is technically structured to operate effectively within three distinct AWS environments: Development, Staging, and Production, each with its specific role in our software development lifecycle. Additionally, we leverage Okta for Single Sign-On (SSO) and Gravitational Teleport for unified remote access.

AWS Environment Segmentation:

Our MSSP operates within three distinct AWS environments: Development, Staging, and Production.
Each environment plays a defined role in our software development lifecycle.
Development Environment:

The Development environment serves as the workspace for our teams to actively work on new features, address bugs, and implement enhancements.
Developers create feature branches from the main repository and conduct their work within this environment.
Continuous Integration (CI) pipelines are set up to automatically build and test code changes within this environment.
Staging Environment:

Staging is a mirrored version of our Production environment and functions as an intensive testing ground.
Deployments from the Development environment to Staging undergo a rigorous quality assurance process.
Comprehensive integration and end-to-end testing are performed to ensure that changes are production-ready.
Production Environment:

Our Production environment is the final destination for stable and approved code changes.
All deployments to the Production environment adhere to stringent change management procedures.
Changes are released during predetermined maintenance windows or via a well-defined change approval process.
Change Management via Pull Requests:

Our workflow follows a GitOps-driven approach, where all alterations to infrastructure and application code are proposed through Pull Requests (PRs).
PRs initiate a peer review process that enables team members to inspect, provide comments, and approve changes.
Once changes are approved, they are automatically deployed to the Development environment.
Promotion Workflow:

Changes that prove stable within the Development environment are promoted to the Staging environment.
This promotion process includes comprehensive regression testing and validation.
After successful testing, changes are further promoted to the Production environment.
Rollback Procedures:

In case issues are detected in the Staging or Production environments, we maintain clearly defined rollback procedures.
These procedures facilitate the swift reversal of changes to the last known stable state, minimizing disruptions for our clients.
Environment Isolation:

Every environment is isolated to prevent issues from one environment affecting others.
We employ network policies and IAM (Identity and Access Management) roles to control access to sensitive data and resources within the Production environment.
Logging and Monitoring:

Across all environments, we have implemented robust logging and monitoring solutions.
Tools such as Datadog are utilized to capture and analyze system performance and anomalies, ensuring that we maintain operational excellence.
Security Auditing:

Security is a paramount concern, and as such, security scans and audits are carried out at every stage of our deployment process.
Vulnerability assessments and compliance checks are seamlessly integrated into our pipeline, guaranteeing a secure and compliant environment.
Okta for Single Sign-On (SSO):

Okta serves as our Single Sign-On (SSO) solution, centralizing identity management.
It simplifies user authentication and enhances security with multi-factor authentication (MFA).
Gravitational Teleport for Unified Remote Access:

Gravitational Teleport provides secure unified remote access to our infrastructure and resources.
It enforces role-based access control and facilitates auditing and session recording for enhanced security.
This comprehensive overview illustrates the intricate architecture of our MSSP system, incorporating advanced technologies and best practices to deliver a secure, scalable, and reliable service to our clients, with a strong focus on access control and authentication through Okta and Gravitational Teleport.
    """

    # Initialize actions
    ticket_action = GetAllJiraTickets()
    estimate_action = EstimateStoryEffort()

    # Run actions
    ticket_results = asyncio.run(ticket_action.run(project_key="INFRA"))
    ticket = ticket_results.instruct_content.tickets[0]
    ticket_data = TicketModel(
        summary=ticket.fields.summary,
        description=ticket.fields.description,
        priority=ticket.fields.priority.name,
        status=ticket.fields.status.name,
        assignee=ticket.fields.assignee.displayName,
    )

    estimate_results = asyncio.run(
        estimate_action.run(ticket=ticket_data, description=mss_description)
    )

    print(estimate_results)
    """
    print(f'Summary: {ticket.fields.summary}')
    print(f'Description {ticket.fields.description}')
    print(f'Priority: {ticket.fields.priority.name}')
    print(f'Status: {ticket.fields.status.name}')
    print(f'Assignee: {ticket.fields.assignee}')
    """
    # Generate job description
    # output = asyncio.run(action.run(title2, description2))
    # print(output.instruct_content.description)
    # generate_rst_file(output.instruct_content.description)
