import pytest
from unittest.mock import Mock
from metagpt.actions.action import Action
from metagpt.actions.action_output import ActionOutput
from metagpt.llm import LLM

@pytest.fixture
def llm_mock():
    return Mock(spec=LLM)

class TestAction:
    @pytest.mark.asyncio
    async def test_aask(self, llm_mock):
        action = Action(llm=llm_mock)
        llm_mock.aask.return_value = "Mocked response"

        response = await action._aask("Question")

        assert response == "Mocked response"
        llm_mock.aask.assert_called_once_with("Question", [action.prefix])

    @pytest.mark.asyncio
    async def test_aask_v1(self, llm_mock):
        action = Action(llm=llm_mock)
        llm_mock.aask.return_value = "Mocked content"
        output_data_mapping = {'key': 'value'}
        action_output_mock = Mock(spec=ActionOutput)
        ActionOutput.create_model_class = Mock(return_value=action_output_mock)
        OutputParser.parse_data_with_mapping = Mock(return_value={'key': 'value'})

        result = await action._aask_v1("Question", "OutputClass", output_data_mapping)

        assert result == action_output_mock(content="Mocked content", instruct_content={'key': 'value'})
        llm_mock.aask.assert_called_once_with("Question", [action.prefix])
        ActionOutput.create_model_class.assert_called_once_with("OutputClass", output_data_mapping)
        OutputParser.parse_data_with_mapping.assert_called_once_with("Mocked content", output_data_mapping)

    def test_set_prefix(self):
        action = Action()

        action.set_prefix("prefix", "profile")

        assert action.prefix == "prefix"
        assert action.profile == "profile"

    # Add more similar test methods for other non-async methods

    @pytest.mark.asyncio
    async def test_run_not_implemented(self):
        action = Action()
        with pytest.raises(NotImplementedError):
            await action.run()

class TestCustomAction(TestAction):
    @pytest.mark.asyncio
    async def test_run(self):
        custom_action = CustomActionSubclass()
        # Assuming you have a CustomActionSubclass that implements 'run'

        await custom_action.run()

        # Add assertions as needed
