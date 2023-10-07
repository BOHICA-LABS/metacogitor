"""YouTubeDownloadAction class."""
# _*_ coding: utf-8 _*_

from pathlib import Path
import string
import yt_dlp
import asyncio
import re
from metacogitor.actions.action import Action
from metacogitor.logs import logger


class YouTubeDownloadAction(Action):
    """Action class for downloading YouTube videos."""

    def __init__(self, name: str = "YouTubeDownload", *args, **kwargs):
        """Initialize the YouTube download handler.

        :param name: The name of the action.
        :type name: str
        """

        super().__init__(name, *args, **kwargs)

    async def run(
        self,
        video_url: str,
        download_folder: str = "./downloads",
        ydl_opts: dict = None,
        *args,
        **kwargs,
    ) -> Path:
        """Execute the action to download a YouTube video.

        :param video_url: The URL of the YouTube video to download.
        :type video_url: str
        :param download_folder: The folder to download the video to, default is "./downloads".
        :type download_folder: str
        :param ydl_opts: The options to pass to the YouTube downloader, default is None.
        :type ydl_opts: dict
        :return: The path to the downloaded video.
        :rtype: Path
        """

        download_folder = Path(download_folder)
        download_folder.mkdir(exist_ok=True, parents=True)

        ydl_opts = ydl_opts or {
            "outtmpl": (Path(download_folder) / "%(id)s.%(title)s.%(ext)s").as_posix(),
            "restrictfilenames": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        info_dict = ydl.extract_info(video_url, download=False)
        video_title = info_dict.get("title", None)
        video_id = info_dict.get("id", None)
        video_title_clean = self.sanitize_title(video_title)
        video_extension = info_dict.get("ext", None)
        file_path = (
            download_folder / f"{video_id}.{video_title_clean}.{video_extension}"
        )
        return file_path

    def sanitize_title(self, title: str) -> str:
        """Sanitize the title of a YouTube video.

        :param title: The title of the YouTube video.
        :type title: str
        :return: The sanitized title of the YouTube video.
        :rtype: str
        """

        valid_chars = "-_.%s%s" % (string.ascii_letters, string.digits)
        sanitized_title = "".join(c if c in valid_chars else "_" for c in title)

        # Replace consecutive underscores with a single underscore
        sanitized_title = re.sub(r"_{2,}", "_", sanitized_title)

        # Remove beginning and trailing spaces, underscores, and dashes
        sanitized_title = sanitized_title.strip(" -_")

        return sanitized_title


if __name__ == "__main__":
    action = YouTubeDownloadAction()
    response = asyncio.run(
        action.run(video_url="https://www.youtube.com/watch?v=9bZkp7q19f0")
    )
    print(response)
