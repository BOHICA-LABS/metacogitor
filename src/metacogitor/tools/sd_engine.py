"""SD Engine for Metacogitor"""
# -*- coding: utf-8 -*-

import asyncio
import base64
import io
import json
import os
from os.path import join
from typing import List

from aiohttp import ClientSession
from PIL import Image, PngImagePlugin

from metacogitor.config import Config
from metacogitor.const import WORKSPACE_ROOT
from metacogitor.logs import logger

config = Config()

payload = {
    "prompt": "",
    "negative_prompt": "(easynegative:0.8),black, dark,Low resolution",
    "override_settings": {"sd_model_checkpoint": "galaxytimemachinesGTM_photoV20"},
    "seed": -1,
    "batch_size": 1,
    "n_iter": 1,
    "steps": 20,
    "cfg_scale": 7,
    "width": 512,
    "height": 768,
    "restore_faces": False,
    "tiling": False,
    "do_not_save_samples": False,
    "do_not_save_grid": False,
    "enable_hr": False,
    "hr_scale": 2,
    "hr_upscaler": "Latent",
    "hr_second_pass_steps": 0,
    "hr_resize_x": 0,
    "hr_resize_y": 0,
    "hr_upscale_to_x": 0,
    "hr_upscale_to_y": 0,
    "truncate_x": 0,
    "truncate_y": 0,
    "applied_old_hires_behavior_to": None,
    "eta": None,
    "sampler_index": "DPM++ SDE Karras",
    "alwayson_scripts": {},
}

default_negative_prompt = "(easynegative:0.8),black, dark,Low resolution"


class SDEngine:
    """SD Engine for Metacogitor"""

    def __init__(self):
        """Initialize the SDEngine instance."""

        # Initialize the SDEngine with configuration
        self.config = Config()
        self.sd_url = self.config.get("SD_URL")
        self.sd_t2i_url = f"{self.sd_url}{self.config.get('SD_T2I_API')}"
        # Define default payload settings for SD API
        self.payload = payload
        logger.info(self.sd_t2i_url)

    def construct_payload(
        self,
        prompt,
        negtive_prompt=default_negative_prompt,
        width=512,
        height=512,
        sd_model="galaxytimemachinesGTM_photoV20",
    ):
        """Construct the payload for the SD API.

        :param prompt: The prompt to use for the SD API
        :type prompt: str
        :param negtive_prompt: The negative prompt to use for the SD API
        :type negtive_prompt: str
        :param width: The width of the output image
        :type width: int
        :param height: The height of the output image
        :type height: int
        :param sd_model: The SD model to use for the SD API
        :type sd_model: str
        :return:
        """

        # Configure the payload with provided inputs
        self.payload["prompt"] = prompt
        self.payload["negtive_prompt"] = negtive_prompt
        self.payload["width"] = width
        self.payload["height"] = height
        self.payload["override_settings"]["sd_model_checkpoint"] = sd_model
        logger.info(f"call sd payload is {self.payload}")
        return self.payload

    def _save(self, imgs, save_name=""):
        """Save the images returned from the SD API.

        :param imgs: The images returned from the SD API
        :type imgs: list
        :param save_name: The name to use for the saved images
        :type save_name: str
        :return:
        """

        save_dir = WORKSPACE_ROOT / "resources" / "SD_Output"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir, exist_ok=True)
        batch_decode_base64_to_image(imgs, save_dir, save_name=save_name)

    async def run_t2i(self, prompts: List):
        """Run the SD API for multiple prompts.

        :param prompts: The prompts to use for the SD API
        :type prompts: list
        :return:
        """

        # Asynchronously run the SD API for multiple prompts
        session = ClientSession()
        for payload_idx, payload in enumerate(prompts):
            results = await self.run(
                url=self.sd_t2i_url, payload=payload, session=session
            )
            self._save(results, save_name=f"output_{payload_idx}")
        await session.close()

    async def run(self, url, payload, session):
        """
        Run the SD API.

        :param url: The URL for the SD API
        :param payload: The payload to use for the SD API
        :param session: The session to use for the SD API
        :return:
        """

        # Perform the HTTP POST request to the SD API
        async with session.post(url, json=payload, timeout=600) as rsp:
            data = await rsp.read()

        rsp_json = json.loads(data)
        imgs = rsp_json["images"]
        logger.info(f"callback rsp json is {rsp_json.keys()}")
        return imgs

    async def run_i2i(self):
        # TODO: Add the graph interface call
        raise NotImplementedError

    async def run_sam(self):
        # TODO：Add SAM interface call
        raise NotImplementedError


def decode_base64_to_image(img, save_name):
    """Decode a base64 image to a PNG image.

    :param img: The base64 image to decode
    :type img: str
    :param save_name: The name to use for the saved image
    :type save_name: str
    :return:
    """

    image = Image.open(io.BytesIO(base64.b64decode(img.split(",", 1)[0])))
    pnginfo = PngImagePlugin.PngInfo()
    logger.info(save_name)
    image.save(f"{save_name}.png", pnginfo=pnginfo)
    return pnginfo, image


def batch_decode_base64_to_image(imgs, save_dir="", save_name=""):
    """Decode a batch of base64 images to PNG images.

    :param imgs: The batch of base64 images to decode
    :type imgs: list
    :param save_dir: The directory to save the images to
    :type save_dir: str
    :param save_name: The name to use for the saved images
    :type save_name: str
    :return:
    """

    for idx, _img in enumerate(imgs):
        save_name = join(save_dir, save_name)
        decode_base64_to_image(_img, save_name=save_name)


if __name__ == "__main__":
    engine = SDEngine()
    prompt = "pixel style, game design, a game interface should be minimalistic and intuitive with the score and high score displayed at the top. The snake and its food should be easily distinguishable. The game should have a simple color scheme, with a contrasting color for the snake and its food. Complete interface boundary"

    engine.construct_payload(prompt)

    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(engine.run_t2i(prompt))
