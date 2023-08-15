import pytest
from pydantic import BaseModel, ValidationError
from metacogitor.actions import ActionOutput


class TestActionOutput:
    def test_init(self):
        content = "Output content"
        instruct_content = BaseModel()
        action_output = ActionOutput(content, instruct_content)

        assert action_output.content == content
        assert action_output.instruct_content == instruct_content

    def test_create_model_class(self):
        class_name = "customoutputclass"
        mapping = {"field1": (int, ...), "field2": (str, ...)}

        customoutputclass = ActionOutput.create_model_class(class_name, mapping)

        assert customoutputclass.__name__ == "customoutputclass"
        assert customoutputclass.__fields__.get("field1").type_ == int
        assert customoutputclass.__fields__.get("field2").type_ == str

    def test_create_model_class_with_valid_data(self):
        class_name = "customoutputclass"
        mapping = {"field1": (int, ...), "field2": (str, ...)}

        customoutputclass = ActionOutput.create_model_class(class_name, mapping)

        data = {"field1": 123, "field2": "test_string"}

        instance = customoutputclass(**data)
        field1 = instance.dict().get("field1")
        field2 = instance.dict().get("field2")
        assert field1 == 123
        assert field2 == "test_string"
