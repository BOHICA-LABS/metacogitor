"""Serialize and deserialize the message object."""
# -*- coding: utf-8 -*-


import copy
import pickle
from typing import Dict, List

from metacogitor.actions.action_output import ActionOutput
from metacogitor.schema import Message


def actionoutout_schema_to_mapping(schema: Dict) -> Dict:
    """
    directly traverse the `properties` in the first level.
    schema structure likes
    ```
    {
        "title":"prd",
        "type":"object",
        "properties":{
            "Original Requirements":{
                "title":"Original Requirements",
                "type":"string"
            },
        },
        "required":[
            "Original Requirements",
        ]
    }
    ```

    :param schema:
    :type schema: Dict
    :return:
    """

    mapping = dict()
    for field, property in schema["properties"].items():
        if property["type"] == "string":
            mapping[field] = (str, ...)
        elif property["type"] == "array" and property["items"]["type"] == "string":
            mapping[field] = (List[str], ...)
        elif property["type"] == "array" and property["items"]["type"] == "array":
            # here only consider the `List[List[str]]` situation
            mapping[field] = (List[List[str]], ...)
    return mapping


def serialize_message(message: Message):
    """serialize the message object to string

    :param message:
    :type message: Message
    :return:
    """

    message_cp = copy.deepcopy(
        message
    )  # avoid `instruct_content` value update by reference
    ic = message_cp.instruct_content
    if ic:
        # model create by pydantic create_model like `pydantic.main.prd`, can't pickle.dump directly
        schema = ic.schema()
        mapping = actionoutout_schema_to_mapping(schema)

        message_cp.instruct_content = {
            "class": schema["title"],
            "mapping": mapping,
            "value": ic.dict(),
        }
    msg_ser = pickle.dumps(message_cp)

    return msg_ser


def deserialize_message(message_ser: str) -> Message:
    """deserialize the message string to message object

    :param message_ser:
    :type message_ser: str
    :return:
    """

    message = pickle.loads(message_ser)
    if message.instruct_content:
        ic = message.instruct_content
        ic_obj = ActionOutput.create_model_class(
            class_name=ic["class"], mapping=ic["mapping"]
        )
        ic_new = ic_obj(**ic["value"])
        message.instruct_content = ic_new

    return message