"""JSON to Markdown converter."""
# -*- coding: utf-8 -*-


# since we original write docs/*.md in markdown format, so I convert json back to markdown
def json_to_markdown(data, depth=2):
    """
    Convert a JSON object to Markdown with headings for keys and lists for arrays, supporting nested objects.

    Args:
    :param data: JSON object (dictionary) or value.
    :type data: dict or str
    :param depth: Current depth level for Markdown headings.
    :type depth: int, optional
    :return: Markdown representation of the JSON data.
    :rtype: str
    """
    markdown = ""

    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, list):
                # Handle JSON arrays
                markdown += "#" * depth + f" {key}\n\n"
                items = [str(item) for item in value]
                markdown += "- " + "\n- ".join(items) + "\n\n"
            elif isinstance(value, dict):
                # Handle nested JSON objects
                markdown += "#" * depth + f" {key}\n\n"
                markdown += json_to_markdown(value, depth + 1)
            else:
                # Handle other values
                markdown += "#" * depth + f" {key}\n\n{value}\n\n"
    else:
        # Handle non-dictionary JSON data
        markdown = str(data)

    return markdown
