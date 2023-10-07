"""SK Kernel Factory"""
# -*- coding: utf-8 -*-

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion import (
    AzureChatCompletion,
)
from semantic_kernel.connectors.ai.open_ai.services.open_ai_chat_completion import (
    OpenAIChatCompletion,
)

from metacogitor.config import CONFIG


def make_sk_kernel():
    """Make the SK kernel."""

    kernel = sk.Kernel()
    if CONFIG.openai_api_type == "azure":
        kernel.add_chat_service(
            "chat_completion",
            AzureChatCompletion(
                CONFIG.deployment_name, CONFIG.openai_api_base, CONFIG.openai_api_key
            ),
        )
    else:
        kernel.add_chat_service(
            "chat_completion",
            OpenAIChatCompletion(
                CONFIG.openai_api_model,
                CONFIG.openai_api_key,
                org_id=None,
                endpoint=CONFIG.openai_api_base,
            ),
        )

    return kernel
