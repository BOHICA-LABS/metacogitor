"""Extract audio from a video file using ffmpeg."""
# -*- coding: utf-8 -*-

import asyncio
import logging
from pathlib import Path
from pydub import AudioSegment
from typing import Optional
from mutagen import File
from metacogitor.actions.action import Action


class ExtractAudioFromVideoAction(Action):
    """Extract audio from a video file using ffmpeg."""

    def __init__(self, name: str = "ExtractAudio", *args, **kwargs):
        """Initialize the ExtractAudio action class.

        :param name: The name of the action, defaults to "ExtractAudio"
        :type name: str, optional
        """
        super().__init__(name, *args, **kwargs)

    async def run(
        self,
        video_path: Path,
        output_folder: Path = Path("./audio_output"),
        output_format: str = "wav",
        bitrate: Optional[str] = None,
        channels: Optional[int] = None,
        codec: Optional[str] = None,
        normalize: bool = False,
        *args,
        **kwargs,
    ) -> str:
        """Run the action.

        :param video_path: The path to the video file.
        :type video_path: Path
        :param output_folder: The folder to save the extracted audio file to, defaults to Path("./audio_output")
        :type output_folder: Path, optional
        :param output_format: The format to save the audio file in, defaults to "wav"
        :type output_format: str, optional
        :param bitrate: The bitrate to save the audio file in, defaults to None
        :type bitrate: Optional[str], optional
        :param channels: The number of channels to save the audio file in, defaults to None
        :type channels: Optional[int], optional
        :param codec: The codec to save the audio file in, defaults to None
        :type codec: Optional[str], optional
        :param normalize: Whether to normalize the audio levels, defaults to False
        :type normalize: bool, optional
        :return: The path to the extracted audio file.
        :rtype: str
        """

        self.ensure_dependencies()

        output_folder.mkdir(exist_ok=True, parents=True)

        output_audio_path = output_folder / f"{video_path.stem}.{output_format}"
        if output_audio_path.exists():
            logging.warning(f"File {output_audio_path} already exists. Overwriting.")

        try:
            audio_data = AudioSegment.from_file(video_path)
            if normalize:
                audio_data = audio_data.normalize()
            if channels:
                audio_data = audio_data.set_channels(channels)
            audio_data.export(
                output_audio_path, format=output_format, bitrate=bitrate, codec=codec
            )

            return f"{output_audio_path}"
        except Exception as e:
            logging.error(f"Error extracting audio: {e}")
            return str(e)

    def ensure_dependencies(self):
        """Ensure that ffmpeg is installed and available in the path."""

        if not AudioSegment.converter:
            raise Exception(
                "ffmpeg not found! Ensure ffmpeg is installed and available in the path."
            )

    def get_metadata(self, audio_path: Path) -> dict:
        """Get metadata from the audio file such as duration, sample rate, etc.

        :param audio_path: The path to the audio file.
        :type audio_path: Path
        """
        audio_file = File(audio_path)
        metadata = {
            "duration": len(audio_file),
            "bitrate": audio_file.info.bitrate,
            "sample_rate": audio_file.info.sample_rate,
            "channels": audio_file.info.channels,
            "codec": audio_file.mime[0] if audio_file.mime else "Unknown",
        }
        return metadata


if __name__ == "__main__":

    # Example usage:
    logging.basicConfig(level=logging.INFO)
    action = ExtractAudioFromVideoAction(
        video_path="path_to_your_video.mp4", normalize=True, channels=2
    )
    response = asyncio.run(action.run())
    print(response)
