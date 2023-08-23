# -*- coding: utf-8 -*-
"""
@Time    : 2023/8/21 15:35
@Author  : Joshua Magady
@File    : test_base_config_model.py
@Desc    : This defines Tests to run on the Base Config Model Class.
"""
import pytest
from metacogitor.config import BaseConfigModel
from pydantic import ValidationError, BaseModel


def test_base_config_required_fields():
    # Test required fields
    config = BaseConfigModel()
    required_fields = config.get_required_fields()

    assert "max_tokens_rsp" in required_fields
    assert "max_budget" in required_fields


def test_base_config_optional_fields():
    # Test optional fields
    config = BaseConfigModel()
    optional_fields = config.get_optional_fields()

    assert "global_proxy" in optional_fields
    assert "long_term_memory" in optional_fields

    assert "max_budget" not in optional_fields
    assert "max_tokens_rsp" not in optional_fields


def test_base_config_api_keys():
    # Test get_api_keys method
    assert BaseConfigModel().get_api_keys() == []


def test_base_config_validation():
    # Test type validation
    with pytest.raises(ValueError):
        BaseConfigModel(max_tokens_rsp="abc")


def test_base_config_dict():
    # Test config_dict property
    config = BaseConfigModel(max_tokens_rsp=100)
    assert config.config_dict == config.dict()


def test_config_model_creation():
    # Test creating model with different params
    config = BaseConfigModel(
        max_tokens_rsp=100, max_budget=20.0, global_proxy="https://proxy"
    )
    assert config.max_tokens_rsp == 100
    assert config.max_budget == 20.0
    assert config.global_proxy == "https://proxy"


def test_value_validation():
    # Test value validation
    with pytest.raises(ValidationError):
        BaseConfigModel(max_tokens_rsp=-100)

    with pytest.raises(ValidationError):
        BaseConfigModel(max_tokens_rsp=99)

    with pytest.raises(ValidationError):
        BaseConfigModel(max_budget=-20)

    with pytest.raises(ValidationError):
        BaseConfigModel(total_cost=-20)


def test_inheritance():
    # Test inheritance from BaseModel
    assert issubclass(BaseConfigModel, BaseModel)


def test_config_description():
    # Test config description
    assert (
        BaseConfigModel.__config__.description
        == "Common application configuration settings."
    )
