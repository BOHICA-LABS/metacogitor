"""Get the template for the prompt and the format example from the templates"""
# -*- coding: utf-8 -*-

from metacogitor.config import CONFIG


def get_template(templates, format=CONFIG.prompt_format):
    """Get the template for the prompt and the format example from the templates

    :param templates: The templates to get the prompt and format example from
    :type templates: dict
    :param format: The format to get the template for
    :type format: str
    :return: The prompt template and the format example
    :rtype: tuple
    :raises ValueError: If the format is not in the templates
    """

    selected_templates = templates.get(format)
    if selected_templates is None:
        raise ValueError(f"Can't find {format} in passed in templates")

    # Extract the selected templates
    prompt_template = selected_templates["PROMPT_TEMPLATE"]
    format_example = selected_templates["FORMAT_EXAMPLE"]

    return prompt_template, format_example
