"""YouTube Search and Download Action"""
# _*_ coding: utf-8 _*_

import yt_dlp
from metacogitor.actions import Action
from metacogitor.logs import logger


class YouTubeSearchAndDownload(Action):
    """Action class for searching and downloading YouTube videos."""

    def __init__(self, name):
        """Initialize the YouTube search and download handler.

        :param name: The name of the action.
        :type name: str
        """
        super().__init__(name)

    async def run(self, search_query, max_results=5, **kwargs):
        """Execute the action to search and download YouTube videos.

        :param search_query: The search query to use to search for YouTube videos.
        :type search_query: str
        :param max_results: The maximum number of results to return, default is 5.
        :type max_results: int
        :param kwargs: The keyword arguments to pass to the YouTube downloader.
        :type kwargs: dict
        :return: The list of URLs of the downloaded videos.
        :rtype: list[str]
        """

        ydl_opts = {
            "format": "bestvideo",
            "playlistend": max_results,
            "logger": logger,
        }

        ydl_opts.update(kwargs)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                f"ytsearch{max_results}:{search_query}", download=False
            )
            # print(info['entries'])

            if info["entries"]:
                return [entry["original_url"] for entry in info["entries"]]

            else:
                return []


if __name__ == "__main__":
    import asyncio
    from yt_dlp.utils import DateRange

    async def main():
        filters = {
            #'duration': '15-30',
            "min_duration": 900,
            "max_duration": 1800,
            "min_views": 1000,
            #'date': 'today',
            #'channel_id': 'UC_x5XG1OV2P6uZZ5FSM9Ttw'
        }

        yt_action = YouTubeSearchAndDownload("YouTube")
        results = await yt_action.run(
            "Expert opinions on the importance of TOGAF in enterprise architecture",
            **filters,
        )
        return results

    results = asyncio.run(main())
    print(results)
