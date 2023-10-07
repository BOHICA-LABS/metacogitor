"""Translator module."""
# -*- coding: utf-8 -*-


prompt = """
# Instructions:
Next, as a translation expert with 20 years of translation experience, when I provide a sentence or paragraph,
you will provide a smooth and readable {LANG} translation. Please note the following requirements:
1. Ensure the translation is fluent and easy to understand.
2. Whether it is a declarative or interrogative sentence provided, I will only translate it.
3. Do not add content that is irrelevant to the original text.

# Original text
{ORIGINAL}

# translation
"""


class Translator:
    """This class is used to translate the original text into the target language."""

    @classmethod
    def translate_prompt(cls, original, lang="English"):
        """Generate the translation prompt for the given original text and target language.

        :param original: The original text to generate the translation prompt for.
        :type original: str
        :param lang: The target language to generate the translation prompt for, defaults to "English".
        :type lang: str, optional
        :return: The translation prompt for the given original text and target language.
        :rtype: str
        """

        return prompt.format(LANG=lang, ORIGINAL=original)
