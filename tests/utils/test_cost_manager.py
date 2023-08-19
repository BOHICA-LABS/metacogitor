from metacogitor.utils import CostManager, Costs
from metacogitor.utils import TOKEN_MAX
import pytest


@pytest.fixture(params=[(100, 200, 10.5, 20.0), (50, 100, 5.0, 10.0)])
def costs(request):
    return Costs(*request.param)


@pytest.fixture(params=TOKEN_MAX.keys())
def model(request):
    return request.param


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


@pytest.fixture
def cost_manager():
    return CostManager()


def test_cost_manager_singleton(cost_manager):
    # Test that CostManager is a singleton
    assert CostManager() is cost_manager


def test_initial_costs(cost_manager):
    assert cost_manager.get_total_prompt_tokens() == 0
    assert cost_manager.get_total_completion_tokens() == 0
    assert cost_manager.get_total_cost() == 0


def test_update_cost(cost_manager, model):
    cost_manager.update_cost(100, 200, model)
    assert cost_manager.get_total_prompt_tokens() == 100
    assert cost_manager.get_total_completion_tokens() == 200
    assert cost_manager.get_total_cost() > 0
    cost_manager.reset()
    assert cost_manager.get_total_prompt_tokens() == 0
    assert cost_manager.get_total_completion_tokens() == 0
    assert cost_manager.get_total_cost() == 0


def test_get_current_costs(cost_manager):
    cost_manager.update_cost(100, 200, "gpt-3.5-turbo")
    costs = cost_manager.get_current_cost()
    assert isinstance(costs, Costs)
    assert costs.total_prompt_tokens == 100
    assert costs.total_completion_tokens == 200
    assert costs.total_cost > 0


# This is an aggregate of all costs incurred so far (above)
def test_get_costs(cost_manager):
    cost_manager.reset()
    cost_manager.update_cost(100, 200, "gpt-3.5-turbo")
    cost_manager.update_cost(100, 200, "gpt-3.5-turbo")
    costs = cost_manager.get_costs()
    assert isinstance(costs, Costs)
    assert costs.total_prompt_tokens == 200
    assert costs.total_completion_tokens == 400
    assert costs.total_cost > 0
