import pytest
from metacogitor.providers import BaseGPTAPI
from metacogitor.logs import logger


class MockGPTAPI(BaseGPTAPI):
    async def acompletion(self, messages):
        pass

    async def acompletion_text(self, messages, stream=False) -> dict:
        return messages[1][
            "content"
        ]  # we are just replaying message, it's located in 1

    def completion(self, messages):
        logger.debug(messages)
        return {
            "choices": [
                {
                    "message": {
                        "content": messages[1][
                            "content"
                        ],  # we are just replaying message, it's located in 1
                    }
                }
            ]
        }


@pytest.fixture
def mock_chatbot():
    return MockGPTAPI()


@pytest.mark.asyncio
async def test_ask(mock_chatbot):
    response = mock_chatbot.ask("What's the weather today?")
    assert isinstance(response, str)


@pytest.mark.asyncio
async def test_aask(mock_chatbot):
    response = await mock_chatbot.aask("What's the weather today?")
    assert isinstance(response, str)


@pytest.mark.asyncio
async def test_ask_batch(mock_chatbot):
    responses = mock_chatbot.ask_batch(["How are you?", "What's your name?"])
    assert isinstance(responses, str)


@pytest.mark.asyncio
async def test_aask_batch(mock_chatbot):
    responses = await mock_chatbot.aask_batch(["How are you?", "What's your name?"])
    assert isinstance(responses, str)


@pytest.mark.asyncio
async def test_ask_code(mock_chatbot):
    code = mock_chatbot.ask_code(["How does this work?", "Show me an example code."])
    assert isinstance(code, str)


@pytest.mark.asyncio
async def test_aask_code(mock_chatbot):
    code = await mock_chatbot.aask_code(
        ["How does this work?", "Show me an example code."]
    )
    assert isinstance(code, str)


# Add more tests for other methods and scenarios

# Run tests
if __name__ == "__main__":
    pytest.main()
