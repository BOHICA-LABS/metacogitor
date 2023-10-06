"""Action to create atomic notes from a given text."""
# -*- coding: utf-8 -*-

from metacogitor.actions.action import Action
from metacogitor.utils.common import OutputParser
from datetime import datetime


template = """
Given the following text:

{text}

Your goal is to create a list of atomic notes from the provided text. Each atomic note should be formatted as a Python
dictionary within a list. Here's the desired structure:

```python
[
    {
        "title": "Title 1",
        "date": "Date 1",
        "source": ["Source1", "Source2"],
        "tags": ["Tag1", "Tag2"],
        "sections": {
            "Idea": "Idea content for Title 1",
            "Sources": "Sources content for Title 1",
            "Summary": "Summary content for Title 1",
            "Related Ideas": ["Related Idea 1", "Related Idea 2"],
            "Keywords": ["Keyword1", "Keyword2"],
            "Notes": "Notes content for Title 1",
            "Links": ["Link1", "Link2"]
        }
    },

]

```

Each atomic note should encapsulate all the ideas from the text. Link related notes under the "Related Ideas" section,
and include as many related ideas and keywords as needed to accurately represent each note's concept. Ensure to only
return the atomic notes with no additional explanation or context. Please feel free to show creativity and expand on ideas.
"""

# Ensure your notes
# are concise and contain only the key information from the text
"""
Each atomic note should encapsulate all the ideas from the text. Link related notes under the "Related Ideas" section,
and include as many related ideas and keywords as needed to accurately represent each note's concept. Ensure to only
return the atomic notes with no additional explanation or context. Please feel free to show creativity and expand on ideas.
"""

"""
        Each atomic note should encapsulate all the ideas from the text. Link related notes under the "Related Ideas" section,
        and include as many related ideas and keywords as needed to accurately represent each note's concept. Ensure your notes
        are concise and contain only the key information from the text. Ensure to only return the atomic notes with no
        additional explanation or context.

Your task is to distill the provided text into atomic notes. Each atomic note should capture the essential ideas
presented in the text. Please include a "Related Ideas" section in each note, linking all relevant concepts that are
connected to the main idea of that note. It's important to incorporate as many related ideas and keywords as needed to
accurately represent each note's central concept. Remember, the objective is to create standalone atomic notes without
any additional explanation or context, but feel free to creatively expand on ideas and concepts where necessary and make
interpretations when concepts and ideas are abstract in nature. Do not refuse to create a note because you believe it
would be too difficult to create, subjective or highly interpretive. If you are unable to create a note, please explain
why in the "Notes" section of the note.
"""


class WriteAtomicNotes(Action):
    """Action to create atomic notes from a given text."""

    def __init__(self, name: str = "WriteAtomicNotes", *args, **kwargs):
        """Initialize the action.

        :param name: The name of the action.
        :type name: str
        """
        super().__init__(name, *args, **kwargs)

    async def run(self, text: str) -> list[dict]:
        """Runs the action to create atomic notes.

        :param  text: The input text.
        :type text: str
        :return: A list of dictionaries containing the atomic notes.
        :rtype: list[dict]
        """

        today = datetime.today().strftime("%Y-%m-%d")

        prompt = f"""
        Metadata:
        date: {today}

        Given the following text:

        {text}

        Your goal is to create a list of atomic notes from the provided text. Each atomic note should be formatted as a
        Python dictionary within a list. Here's the desired structure:

        ```python
        [
            {{
                "title": "Title 1",
                "date": "Date 1",
                "source": ["Source1", "Source2"],
                "tags": ["Tag1", "Tag2"],
                "sections": {{
                "Idea": "Idea content for Title 1",
                    "Sources": "Sources content for Title 1",
                    "Summary": "Summary content for Title 1",
                    "Related Ideas": ["Related Idea 1", "Related Idea 2"],
                    "Keywords": ["Keyword1", "Keyword2"],
                    "Notes": "Notes content for Title 1",
                    "Links": ["Link1", "Link2"]
                }}
            }},
            # additional notes as required
        ]

        ```

        Your task is to distill the provided text into atomic notes. Each atomic note should capture the essential ideas
        presented in the text. Please include a "Related Ideas" section in each note, linking all relevant concepts that
        are connected to the main idea of that note. It's important to incorporate as many related ideas and keywords as
        needed to accurately represent each note's central concept. Remember, the objective is to create standalone
        atomic notes without any additional explanation or context, but feel free to creatively expand on ideas and
        concepts where necessary and make interpretations when concepts and ideas are abstract in nature. Do not refuse
        to create a note because you believe it would be too difficult to create, subjective or highly interpretive. If
        you are unable to create a note, please explain why in the "Notes" section of the note.
        """

        notes = await self._aask(prompt)

        return OutputParser.parse_str(notes)  # OutputParser.extract_struct(notes, list)
