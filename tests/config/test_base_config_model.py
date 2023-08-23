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
from hypothesis import given, settings
import hypothesis.strategies as st
import hypothesis.provisional as pr


REQUIRED_FIELDS = ["max_tokens_rsp", "max_budget"]
OPTIONAL_FIELDS = ["global_proxy", "deployment_id"]


class TestBaseConfigModel:
    @given(
        st.integers(min_value=100),
        st.floats(min_value=1.0, max_value=1000),
        pr.urls(),
    )
    @settings(max_examples=10)
    def test_model_creation(self, max_tokens, max_budget, proxy):
        model = BaseConfigModel(
            max_tokens_rsp=max_tokens, max_budget=max_budget, global_proxy=proxy
        )
        assert model.max_tokens_rsp == max_tokens
        assert model.max_budget == max_budget
        assert model.global_proxy == proxy

    # Rest of test cases as methods

    def test_base_config_api_keys(self):
        # Test get_api_keys method
        assert BaseConfigModel().get_api_keys() == []

    def test_inheritance(self):
        # Test inheritance
        assert issubclass(BaseConfigModel, BaseModel)

    def test_config_description(self):
        # Test description
        assert (
            BaseConfigModel.__config__.description
            == "Common application configuration settings."
        )

    # Optional - consolidate some test cases
    @pytest.mark.parametrize(
        "invalid_value,expected_error",
        [
            (-100, ValidationError),
            (-20.0, ValidationError),
            ("invalid", ValidationError),
        ],
    )
    def test_validation(self, invalid_value, expected_error):
        with pytest.raises(expected_error):
            BaseConfigModel(max_tokens_rsp=invalid_value)

    @given(
        st.integers(min_value=-100, max_value=99),
        st.floats(min_value=-100, max_value=0),
    )
    @settings(max_examples=10)
    def test_value_validation(self, invalid_token, invalid_budget):
        with pytest.raises(ValidationError):
            BaseConfigModel(max_tokens_rsp=invalid_token, max_budget=invalid_budget)

    @given(
        st.integers(min_value=100),
    )
    @settings(max_examples=10)
    def test_base_config_dict(self, max_tokens):
        # Test config_dict property
        config = BaseConfigModel(max_tokens_rsp=max_tokens)
        assert config.config_dict == config.dict()

    @given(
        config=st.builds(BaseConfigModel),
        required_fields=st.just(REQUIRED_FIELDS),
        optional_fields=st.just(OPTIONAL_FIELDS),
    )
    @settings(max_examples=10)
    def test_required_fields(self, config, required_fields, optional_fields):
        required = config.get_required_fields()
        optional = config.get_optional_fields()

        @given(field=st.sampled_from(required_fields))
        def check_required(field):
            assert field in required

        @given(field=st.sampled_from(optional_fields))
        def check_optional(field):
            assert field not in required

        check_required()
        check_optional()

        assert required != optional

    @given(
        config=st.builds(BaseConfigModel),
        required_fields=st.just(REQUIRED_FIELDS),
        optional_fields=st.just(OPTIONAL_FIELDS),
    )
    @settings(max_examples=10)
    def test_base_config_optional_fields(
        self, config, required_fields, optional_fields
    ):
        # Test optional fields
        required = config.get_required_fields()
        optional = config.get_optional_fields()

        @given(field=st.sampled_from(required_fields))
        def check_required(field):
            assert field not in optional

        @given(field=st.sampled_from(optional_fields))
        def check_optional(field):
            assert field in optional

        check_required()
        check_optional()

        assert required != optional
