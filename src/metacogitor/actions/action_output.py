# -*- coding: utf-8 -*-

from typing import Dict, Type

from pydantic import BaseModel, create_model, root_validator, validator


class ActionOutput:
    """Represents the output of an action.

    :param content: The content of the output.
    :type content: str
    :param instruct_content: The content of the output as a BaseModel.
    :type instruct_content: BaseModel
    """

    content: str
    instruct_content: BaseModel

    def __init__(self, content: str, instruct_content: BaseModel):
        """Initialize the ActionOutput class.

        :param content: The content of the output.
        :param instruct_content: The content of the output as a BaseModel.
        """
        self.content = content
        self.instruct_content = instruct_content

    @classmethod
    def create_model_class(cls, class_name: str, mapping: Dict[str, Type]):
        """Create a model class for the ActionOutput class.

        :param class_name:
        :param mapping:
        :return:
        """
        new_class = create_model(class_name, **mapping)

        @validator("*", allow_reuse=True)
        def check_name(v, field):
            """Check the name of the field.

            :param v: The value of the field.
            :param field: The field.
            :return: The value of the field.
            """
            if field.name not in mapping.keys():
                raise ValueError(f"Unrecognized block: {field.name}")
            return v

        @root_validator(pre=True, allow_reuse=True)
        def check_missing_fields(values):
            """Check for missing fields.

            :param values: The values of the fields.
            :return: The values of the fields.
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
