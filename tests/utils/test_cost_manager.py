from collections import namedtuple
import pytest

Costs = namedtuple(
    "Costs",
    ["total_prompt_tokens", "total_completion_tokens", "total_cost", "total_budget"],
)


@pytest.fixture(params=[(100, 200, 10.5, 20.0), (50, 100, 5.0, 10.0)])
def costs(request):
    return Costs(*request.param)


def test_costs(costs):
    assert costs.total_prompt_tokens == costs[0]
    assert costs.total_completion_tokens == costs[1]
    assert costs.total_cost == costs[2]
    assert costs.total_budget == costs[3]


def test_immutable():
    c = Costs(100, 200, 10.5, 20.0)
    with pytest.raises(AttributeError):
        c.total_prompt_tokens = 50


def test_value_error():
    with pytest.raises(TypeError):
        Costs(100, 200, 10.5)
