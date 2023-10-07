"""Highlight code snippets with Pygments."""
# -*- coding: utf-8 -*-

from pygments import highlight as highlight_
from pygments.lexers import PythonLexer, SqlLexer
from pygments.formatters import TerminalFormatter, HtmlFormatter


def highlight(code: str, language: str = "python", formatter: str = "terminal"):
    """Highlight code snippets with Pygments.

    :param code: The code to highlight.
    :type code: str
    :param language: The language to highlight the code in, defaults to "python".
    :type language: str, optional
    :param formatter: The formatter to use, defaults to "terminal".
    :type formatter: str, optional
    :return: The highlighted code.
    :rtype: str
    :raises ValueError: If the language or formatter is not supported.
    """

    # Specify the language to highlight
    if language.lower() == "python":
        lexer = PythonLexer()
    elif language.lower() == "sql":
        lexer = SqlLexer()
    else:
        raise ValueError(f"Unsupported language: {language}")

    # Specify output format
    if formatter.lower() == "terminal":
        formatter = TerminalFormatter()
    elif formatter.lower() == "html":
        formatter = HtmlFormatter()
    else:
        raise ValueError(f"Unsupported formatter: {formatter}")

    # Highlight code snippets using Pygments
    return highlight_(code, lexer, formatter)
