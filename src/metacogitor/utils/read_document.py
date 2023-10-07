"""Read a docx file and return a list of paragraphs"""
# -*- coding: utf-8 -*-


import docx


def read_docx(file_path: str) -> list:
    """Open a docx file

    :param file_path: The path to the docx file
    :type file_path: str
    :return: A list of paragraphs
    :rtype: list
    """
    doc = docx.Document(file_path)

    # Create an empty list to store paragraph contents
    paragraphs_list = []

    # Iterate through the paragraphs in the document and add their content to the list
    for paragraph in doc.paragraphs:
        paragraphs_list.append(paragraph.text)

    return paragraphs_list
