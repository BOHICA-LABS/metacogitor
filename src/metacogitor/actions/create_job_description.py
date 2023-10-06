"""Create Job Description Action"""
# -*- coding: utf-8 -*-

from metacogitor.actions.action import Action, ActionOutput
from metacogitor.utils.common import OutputParser
from pydantic import BaseModel
from typing import Dict


class JobDescriptionResults(BaseModel):
    """The results of the CreateJobDescription action."""

    title: str
    description: Dict


class CreateJobDescription(Action):
    """Create Job Description Action"""

    def __init__(self, name: str = "CreateJobDescription", *args, **kwargs):
        """Initialize the CreateJobDescription action.

        :param name: The name of the action.
        :type name: str
        :param args: The action arguments.
        :type args: list
        :param kwargs: The action keyword arguments.
        :type kwargs: dict
        """
        super().__init__(name, *args, **kwargs)

    async def run(self, title: str, description: str) -> ActionOutput:
        """Runs the action to generate search queries.


        :param title: The type of diagram to generate.
        :type title: str
        :param description: The input text.
        :type description: str
        :return: The output of the action.
        :rtype: ActionOutput
        """

        prompt = f"""
        Given the following job role and responsibilities:

        Job Role: {title}

        responsibilities: {description}

        Your task is to generate a Job Description data structure representation of the information related to the job
        role. This structure should encapsulate various facets of the job, including qualifications, responsibilities,
        benefits, and interview questions.

        The structure should be formatted using Python dictionary and list conventions. Each section of the job
        description should clearly convey the relevant information and its relationship to other parts of the
        description. Here's an example:

        python```
        {{
            "Title": "Job Role",
            "Details": {{
                "Location": "Location",
                "Department": "Department",
                "Reports to": "Reports To",
                "Years of Experience": "Years of Experience",
                "Level Range": "Level Range",
                "Base Salary Range": "Salary Range",
                "Employee Type": "Employee Type",
            }},
            "Job Summary": "Brief Description",
            "Key Responsibilities": [
                "Responsibility 1",
                "Responsibility 2",
                "Responsibility 3",
                # Additional responsibilities as required.
            ],
            "Qualifications and Experience": {{
                "Required": [
                    "Required Qualification 1",
                    "Required Qualification 2",
                    # Additional qualifications as required.
                ],
                "Preferred": [
                    "Preferred Qualification 1",
                    "Preferred Qualification 2",
                    # Additional qualifications as required.
                ]
            }},
            "Skills and Competencies": [
                "Skill 1",
                "Skill 2"
                # Additional skills as required.
            ],
            "Benefits": [
                "Benefit 1",
                "Benefit 2"
                # Additional benefits as required.
            ],
            "Notes": {{
                "Sample Interview Questions": [
                    {{
                        "Question": "Interview Question 1",
                        "Example Answer": "Example Answer 1",
                        "Category": "Category of Question",
                        "Purpose": "Purpose of Question",
                        "Interviewer Notes": "Interviewer's Notes on Question"
                }},
                    # Additional interview questions as required.
                ],
                "Disclaimer": "Standard Disclaimer"
            }}
        }}

        ```

        Remember, each section of the job description should encapsulate the core ideas from the given job role and
        responsibilities. You may creatively expand on ideas and concepts when necessary. If a responsibility or detail
        is too vague or lacks context to fit into the structure, consider creating an appropriate placeholder. Return
        only the Python code block with the job description. No additional supporting detail that's not contained in the
        code block should be returned.
        """

        job_description = await self._aask(prompt)
        result = OutputParser.extract_struct(job_description, Dict)

        return ActionOutput(
            content="Job Description Completed",
            instruct_content=JobDescriptionResults(
                title=title,
                description=result,
            ),
        )


# Example of usage:
if __name__ == "__main__":
    import asyncio

    # Create job description action
    action = CreateJobDescription()

    # Example title and description
    title1 = "IAM Microservice Developer"
    description1 = """
    As an IAM Microservice Developer, you will be instrumental in designing, building, and maintaining our Identity and Access Management (IAM) Microservice. This service is a cornerstone of our software architecture, ensuring the secure management of user identities and controlling access to critical system resources.

    Responsibilities:

    1. **Authentication Component Development**: Spearhead the design and development of the authentication component, incorporating mechanisms like multi-factor authentication and session management. Ensure that user credentials are verified securely and efficiently.

    2. **Authorization Logic**: Design and code the authorization component, ensuring users' permissions and roles align with the access control list (ACL) or policy database.

    3. **User Management Integration**: Facilitate user registration, profile management, and password resets. Seamlessly integrate with external identity providers like LDAP, OAuth, or SAML.

    4. **Token Management**: Oversee the generation, validation, and security of various tokens, ensuring they're resistant to tampering and unauthorized access.

    5. **Logging and Auditing**: Implement mechanisms to record authentication, authorization events, and other significant system events, ensuring a reliable audit trail for security analysis and compliance reporting.

    6. **RBAC Development**: Simplify access control by developing the Role-Based Access Control component, which will link permissions to roles rather than individual users.

    7. **SSO Integration**: Enhance user experience by integrating Single Sign-On protocols such as OAuth2, OpenID Connect, or SAML.

    8. **Scaling & Load Balancing**: Ensure the IAM Microservice can handle varying loads, leveraging load balancers and auto-scaling mechanisms for optimum performance and availability.

    9. **Security Measures**: Prioritize the security of data in transit and at rest, following industry best practices and countering potential threats proactively.

    10. **API Design**: Provide robust and secure APIs for other services to seamlessly integrate with the IAM Microservice.

    Essential Qualities:

    - **Modularity**: Adopt a modular approach, ensuring each component of the IAM Microservice is loosely coupled, which aids in maintenance and scalability.

    - **Security-Focused**: With security being paramount, you should be able to embed it in every facet of development.

    - **Flexibility**: Adapt and evolve the IAM Microservice to meet specific organizational security and access control needs.

    - **Team Collaboration**: Work harmoniously with a diverse team to develop a robust IAM Microservice that safeguards user data while providing an efficient user experience.

    In essence, as an IAM Microservice Developer, you play a pivotal role in our organization. You'll be tasked with safeguarding user identities, ensuring secure access to resources, and contributing significantly to our software ecosystem's security and efficiency.
    """

    title2 = "Multidisciplinary Team Lead"
    description2 = """
                Responsibilities for the Multidisciplinary Team Lead:

                1. Technical Proficiency:
                    - Maintain and upgrade expertise in multiple programming languages, including Python, Golang, and JavaScript.
                    - Advise the team on best practices in each language and oversee the code quality and adherence to standards.

                2. QA and Testing Oversight:
                    - Establish and drive quality assurance processes and methodologies.
                    - Oversee the development and implementation of automated testing frameworks.
                    - Ensure timely identification, reporting, and resolution of defects and ensure high-quality software releases.

                3. Cloud Infrastructure Management:
                    - Lead the architecture, design, and implementation of scalable and robust cloud solutions.
                    - Demonstrate expertise in Infrastructure as Code (IaC) practices, leveraging tools like Terraform.
                    - Ensure the team adheres to best practices for cloud-native solutions, optimizing for performance, cost, and scalability.

                4. Distributed Computing Leadership:
                    - Guide the team in designing, building, and maintaining distributed systems.
                    - Drive understanding and implementation of distributed computing patterns, ensuring system reliability and efficiency.

                5. Data Mesh Stewardship:
                    - Lead initiatives to build and maintain data meshes, facilitating decentralized data infrastructure.
                    - Promote best practices for creating, maintaining, and utilizing data products within the data mesh.

                6. Modularity and Scalability:
                    - Champion the design and development of highly modular, scalable, and maintainable code.
                    - Regularly review codebases to ensure they remain clean, maintainable, and follow best architecture practices.

                7. Team Management and Collaboration:
                    - Foster a collaborative environment, ensuring cross-functional team members are aligned, informed, and working towards common goals.
                    - Mentor team members, providing them with guidance, feedback, and opportunities for professional growth.
                    - Coordinate with other departments and stakeholders to ensure smooth project delivery and meet business requirements.

                8. Continual Learning and R&D:
                    - Keep abreast of the latest industry trends, technologies, and best practices, ensuring the team remains at the forefront of technological innovation.
                    - Organize regular training sessions, workshops, or knowledge-sharing sessions to foster a culture of continual learning.

                9. Project Management:
                    - Oversee the complete project lifecycle, from ideation to deployment, ensuring projects remain on track, within scope, and on budget.
                    - Facilitate agile ceremonies, sprint planning, retrospectives, and daily stand-ups, ensuring transparency and effective communication.

                10. Stakeholder Communication:
                    - Regularly update upper management and stakeholders on project statuses, potential risks, and mitigation strategies.
                    - Foster a culture of open communication, ensuring any challenges or blockers are addressed promptly.

                11. Security and Compliance:
                    - Ensure the team follows industry-standard security practices for both code and infrastructure.
                    - Stay updated with compliance requirements, especially if the software is used in regulated industries or markets.

                12. Vendor and Tool Management:
                    - Evaluate, select, and manage tools and vendors that can assist in the development, testing, and deployment processes.
                    - Negotiate contracts, SLAs, and manage relationships with third-party vendors to ensure continuous service.

                13. Budget and Resource Management:
                    - Oversee the team's budget, ensuring resources are allocated effectively.
                    - Justify and advocate for additional resources or budget allocations when necessary.

                14. Feedback Loop:
                    - Establish mechanisms for gathering feedback from end-users, stakeholders, and team members to continuously improve processes and products.
                    - Analyze this feedback to inform decision-making and feature development.

                15. Disaster Recovery and Business Continuity Planning:
                    - Ensure the team has robust disaster recovery plans in place.
                    - Regularly review and test business continuity plans, ensuring minimal service disruption in the event of unforeseen issues.

                16. Soft Skills and Team Well-being:
                    - Foster an environment of mutual respect, openness, and inclusivity.
                    - Regularly check in with team members about their well-being, ensuring a healthy work-life balance and addressing any personal or professional challenges they may face.

                17. Documentation and Knowledge Management:
                    - Ensure that code, architecture decisions, and other processes are thoroughly documented.
                    - Oversee the maintenance of a knowledge base or wiki, ensuring new team members can onboard quickly and existing team members have resources to reference.

                18. Product Lifecycle Management:
                    - Collaborate closely with product managers, business analysts, and stakeholders to align technical capabilities with business objectives.
                    - Ensure the technical team understands product vision and goals, and works in alignment with product roadmaps.

                19. Innovation and Ideation:
                    - Foster a culture where team members are encouraged to bring new ideas, tools, and methodologies to the table.
                    - Periodically hold hackathons or brainstorming sessions to encourage innovation.

                20. Community Engagement and External Representation:
                    - Represent the team at conferences, workshops, and industry events, showcasing achievements and learning from peers.
                    - Engage with the wider tech community, possibly contributing to open-source projects or industry discussions.

                This role, given its multidisciplinary nature, requires a blend of technical expertise, leadership skills, and strong communication abilities. The Team Lead should be adept at navigating complex technical landscapes while also being a pillar of support and guidance for their team.
    """

    def generate_rst_file(job_description):
        formatted_data = []

        # Title
        formatted_data.append("=" * len(job_description["Title"]))
        formatted_data.append(job_description["Title"])
        formatted_data.append("=" * len(job_description["Title"]))
        formatted_data.append("")

        # Details
        details = [
            "Location",
            "Department",
            "Reports to",
            "Years of Experience",
            "Level Range",
            "Base Salary Range",
            "Bonus Range",
            "Employ Stock Ownership Plan",
            "Employee Type",
        ]
        for detail in details:
            if detail in job_description["Details"]:
                formatted_data.append(f"{detail}: {job_description['Details'][detail]}")
                # formatted_data.append(job_description["Details"][detail])
                formatted_data.append("")

        # Job Summary
        formatted_data.append("Job Summary")
        formatted_data.append("-" * 11)
        formatted_data.append("")
        formatted_data.append(f"{job_description['Job Summary']}")
        formatted_data.append("")

        # Key Responsibilities
        formatted_data.append("Key Responsibilities")
        formatted_data.append("-" * 19)
        for responsibility in job_description["Key Responsibilities"]:
            formatted_data.append(f"- {responsibility}")
        formatted_data.append("")

        # Qualifications and Experience
        formatted_data.append("Qualifications and Experience")
        formatted_data.append("-" * 27)
        for qualification in job_description["Qualifications and Experience"][
            "Required"
        ]:
            formatted_data.append(f"- {qualification}")
        formatted_data.append("")

        # Education and Training (Placeholder since it's not available in the input structure)
        formatted_data.append("Education and Training")
        formatted_data.append("-" * 20)
        formatted_data.append("- Required: [Degree or certification]")
        formatted_data.append("- Preferred: [Degree or certification]")
        formatted_data.append("")

        # Skills and Competencies
        formatted_data.append("Skills and Competencies")
        formatted_data.append("-" * 21)
        for skill in job_description["Skills and Competencies"]:
            formatted_data.append(f"- {skill}")
        formatted_data.append("")

        # Preferred Additional Experience (Placeholder since it's not available in the input structure)
        formatted_data.append("Preferred Additional Experience")
        formatted_data.append("_" * 31)
        formatted_data.append("- Experience 1")
        formatted_data.append("- Experience 2")
        formatted_data.append("- Experience 3")
        formatted_data.append("")

        # Working Conditions (Placeholder since it's not available in the input structure)
        formatted_data.append("Working Conditions")
        formatted_data.append("-" * 18)
        formatted_data.append(
            "[Description of working conditions, including hours, environment, etc.]"
        )
        formatted_data.append("")

        # Physical Demands (Placeholder since it's not available in the input structure)
        formatted_data.append("Physical Demands")
        formatted_data.append("-" * 15)
        formatted_data.append(
            "[Description of physical demands of the job, if applicable.]"
        )
        formatted_data.append("")

        # Benefits
        formatted_data.append("Benefits")
        formatted_data.append("-" * 8)
        for benefit in job_description["Benefits"]:
            formatted_data.append(f"- {benefit}")
        formatted_data.append("")

        # Notes
        formatted_data.append("Notes")
        formatted_data.append("-----")
        formatted_data.append("")
        formatted_data.append("Sample Interview Questions")
        formatted_data.append("-" * 27)
        for question in job_description["Notes"]["Sample Interview Questions"]:
            formatted_data.append(f"Question: {question['Question']}")
            formatted_data.append(f"Example Answer: {question['Example Answer']}")
            formatted_data.append(f"Category: {question['Category']}")
            formatted_data.append(f"Purpose: {question['Purpose']}")
            formatted_data.append(f"Interviewer Notes: {question['Interviewer Notes']}")
            formatted_data.append("")

        formatted_data.append("Disclaimer")
        formatted_data.append("-" * 10)
        formatted_data.append(job_description["Notes"]["Disclaimer"])

        # Writing to a file
        with open("job_description.rst", "w") as file:
            file.write("\n".join(formatted_data))

    # Generate job description
    output = asyncio.run(action.run(title2, description2))
    print(output.instruct_content.description)
    generate_rst_file(output.instruct_content.description)
