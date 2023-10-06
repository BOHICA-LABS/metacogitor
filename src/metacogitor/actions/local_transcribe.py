"""Local transcription action using Whisper."""
# -*- coding: utf-8 -*-

import asyncio
from pathlib import Path

import whisper

from metacogitor.actions import Action
from metacogitor.logs import logger


def transcribe_wrapper(model, audio_file, language):
    return model.transcribe(audio_file, language=language)


class LocalTranscribe(Action):
    """Transcribe audio files offline using Whisper."""

    def __init__(self, name: str = "LocalTranscribe", model="tiny", *args, **kwargs):
        """Initialize the action.

        :param name: Name of the action.
        :param model: Name of the model to use.
        :param args: Additional arguments.
        :param kwargs: Additional keyword arguments.
        """
        super().__init__(name=name, *args, **kwargs)
        self.model = model

    async def run(self, audio_file: Path, language="en") -> str:
        """
        Transcribe an audio file.

        :param audio_file: Path to audio file.
        :param language: Language spoken in audio file.
        :return: Transcription text.
        """

        try:
            model = whisper.load_model(self.model)
            logger.info(f"Transcribing {audio_file} using {self.model} model...")
            transcript = await self._transcribe(model, audio_file, language)
            return transcript
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return ""

    async def _transcribe(self, model, audio_file: Path, language: str) -> str:
        """Async transcription using asyncio.

        :param model: Whisper model.
        :param audio_file: Path to audio file.
        :param language: Language spoken in audio file.
        :return: Transcription text.
        """
        loop = asyncio.get_event_loop()

        transcript_future = loop.run_in_executor(
            None, transcribe_wrapper, model, str(audio_file), language
        )

        transcript = await transcript_future
        source = audio_file.split("/")[-1]
        return f'source:{source}/n{transcript["text"]}'
