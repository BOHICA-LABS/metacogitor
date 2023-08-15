#!/usr/bin/env python
# coding: utf-8
"""
@Time    : 2023/8/14 10:03
@Author  : Joshua Magady
@File    : action_output
@Description: This defines the action output class for the metacogitor project.
"""

from typing import Dict, Type

from pydantic import BaseModel, create_model, root_validator, validator

__ALL__ = ["ActionOutput"]


class ActionOutput:
    """
    Represents the output of an action.
    """

    def __init__(self, content: str, instruct_content: BaseModel):
        """
        Initialize an ActionOutput instance.

        :param content: Content of the output.
        :param instruct_content: Instruct content as a BaseModel instance.
        """
        self.content = content
        self.instruct_content = instruct_content

    @classmethod
    def create_model_class(cls, class_name: str, mapping: (Dict[str, Type], ...)):
        """
        Create a new model class based on the provided class name and mapping.

        :param class_name: Name of the new model class.
        :param mapping: Mapping of field names to types.
        :return: New model class.
        """
        new_class = create_model(class_name, **mapping)

        # TODO: Update this to use the new pydantic syntax for validators
        @validator("*", allow_reuse=True)
        def check_name(v, field):
            """
            Validator to check the field name.

            :param v: Field value.
            :param field: Field instance.
            :return: Validated field value.
            """
            if field.name not in mapping.keys():
                raise ValueError(f"Unrecognized block: {field.name}")
            return v

        # TODO: Update this to use the new pydantic syntax for validators
        @root_validator(pre=True, allow_reuse=True)
        def check_missing_fields(values):
            """
            Root validator to check missing fields.

            :param values: Field values.
            :return: Validated field values.
            """
            required_fields = set(mapping.keys())
            missing_fields = required_fields - set(values.keys())
            if missing_fields:
                raise ValueError(f"Missing fields: {missing_fields}")
            return values

        new_class.__validator_check_name = classmethod(check_name)
        new_class.__root_validator_check_missing_fields = classmethod(
            check_missing_fields
        )
        return new_class
