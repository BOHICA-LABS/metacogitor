"""YouTube Video Analyst Role"""
# _*_ coding: utf-8 _*_

import asyncio
from typing import Type, Iterable
from metacogitor.roles.role import Role
from metacogitor.actions.youtube_download import YouTubeDownloadAction
from metacogitor.actions.extract_audio import ExtractAudioFromVideoAction
from metacogitor.actions.local_transcribe import LocalTranscribe
from metacogitor.actions.write_atomic_notes import WriteAtomicNotes
from metacogitor.schema import Message
from metacogitor.logs import logger


class YouTubeVideoAnalystRole(Role):
    """YouTube Video Analyst Role

    Attributes:
        name (str): The name of the role.
        profile (str): The role profile description.
        goal (str): The goal of the role.
        constraints (str): Constraints or requirements for the role.
        language (str): The language in which the tutorial documents will be generated.
        desc (str): The description of the role.
    """

    def __init__(
        self,
        name: str = "Alex",
        profile: str = "Text Analyst",
        goal: str = "Download, transcribe, and analyze documents",
        constraints: str = "Ensure linguistic accuracy and relevance of information",
        language: str = "en-us",
        desc: str = "A tool for text analysis and content extraction.",
        **kwargs,
    ):
        """Initialize the role with given attributes.

        :param name: The name of the role.
        :type name: str
        :param profile: The role profile description.
        :type profile: str
        :param goal: The goal of the role.
        :type goal: str
        :param constraints: Constraints or requirements for the role.
        :type constraints: str
        :param language: The language in which the tutorial documents will be generated.
        :type language: str
        :param desc: The description of the role.
        :type desc: str
        """

        super().__init__(
            name=name, profile=profile, goal=goal, constraints=constraints, desc=desc
        )
        self.language = language
        if language not in ("en-us"):
            logger.warning(
                f"The language `{language}` has not been tested, it may not work."
            )

        # Initialize actions for this role
        self._init_actions(
            [
                YouTubeDownloadAction(name),
                ExtractAudioFromVideoAction(name),
                LocalTranscribe(name, model="base"),
                WriteAtomicNotes(name),
            ]
        )

    async def _think(self) -> None:
        """Override the _think method to specify the logic for this role.

        :return: None
        :rtype: None
        """
        # Here, the role can decide which action to take based on its current state and the observed messages
        # For simplicity, let's assume it always tries to download a video first and then extract its audio

        if self._rc.todo is None:
            self._set_state(0)
            logger.info(f"{self._setting}: ready to {self._rc.todo}")
            return

        if self._rc.state + 1 < len(self._states):
            self._set_state(self._rc.state + 1)
            logger.info(f"{self._setting}: ready to {self._rc.todo}")
        else:
            self._rc.todo = None
            logger.info(f"{self._setting}: ready to {self._rc.todo}")

    async def _act(self) -> Message:
        """Override the _act method to specify the logic for this role.

        :return: None
        :rtype: None
        """

        if isinstance(self._rc.todo, YouTubeDownloadAction):
            # Download video action
            video_msg = self._rc.memory.get(k=1)[0]
            logger.info(f"video_msg: {video_msg.content}")
            video_path = await self._rc.todo.run(video_url=video_msg.content)

            logger.info(f"video_path: {video_path}")

            # Store result in memory
            # self._rc.memory.add(Message(video_path))
            # Store video path message
            video_path_message = Message(
                content=video_path, role=self.profile, cause_by=YouTubeDownloadAction
            )
            self._rc.memory.add(video_path_message)

        elif isinstance(self._rc.todo, ExtractAudioFromVideoAction):
            # Extract audio action
            video_msg = self._rc.memory.get_by_action(YouTubeDownloadAction)[-1]
            audio_path = await self._rc.todo.run(video_path=video_msg.content)

            # Return result
            audio_path_message = Message(
                content=audio_path,
                role=self.profile,
                cause_by=ExtractAudioFromVideoAction,
            )
            self._rc.memory.add(audio_path_message)

        elif isinstance(self._rc.todo, LocalTranscribe):
            # Transcribe audio action
            audio_msg = self._rc.memory.get_by_action(ExtractAudioFromVideoAction)[-1]
            transcript = await self._rc.todo.run(audio_file=audio_msg.content)

            # Return result
            transcript_message = Message(
                content=transcript, role=self.profile, cause_by=LocalTranscribe
            )
            self._rc.memory.add(transcript_message)

        elif isinstance(self._rc.todo, WriteAtomicNotes):
            # Write atomic notes action
            transcript_msg = self._rc.memory.get_by_action(LocalTranscribe)[-1]
            notes = await self._rc.todo.run(transcript_msg.content)

            # Return result
            notes_message = Message(
                content=notes, role=self.profile, cause_by=WriteAtomicNotes
            )
            self._rc.memory.add(notes_message)
            return notes_message

    async def _react(self) -> Message:
        """Override the _react method to specify the logic for this role.

        :return: None
        :rtype: None
        """

        # Here, the role can decide how to react to the result of the action
        while True:
            await self._think()
            if self._rc.todo is None:
                break
            msg = await self._act()
        # report = msg.instruct_content
        # self.write_report(report.topic, report.content)
        return msg


if __name__ == "__main__":
    # Usage:
    analyst = YouTubeVideoAnalystRole()
    video_link_msg = Message(
        content="https://youtu.be/HglQTn-aMNM?list=PLjRUahwPH71OxXZpa8k6Elm7uWGEX7mcb"
    )  # https://www.youtube.com/watch?v=rn_YodiJO6k") #https://www.youtube.com/watch?v=9bZkp7q19f0")  # Example link
    # video_link_msg = "https://www.youtube.com/watch?v=9bZkp7q19f0"  # Example link
    analyst_response = asyncio.run(analyst.run(video_link_msg))
    # analyst_response = asyncio.run(analyst.handle(video_link_msg))
    print(analyst_response)
