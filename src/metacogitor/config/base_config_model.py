"""Base configuration model with common settings."""
# -*- coding: utf-8 -*-

from pydantic import BaseModel, validator, constr, confloat, conint, Field
from typing import List, Optional, Required

__ALL__ = ["BaseConfigModel"]


class BaseConfigModel(BaseModel):
    """Base configuration model with common settings.

    Attributes:

        global_proxy (Optional[str]): Global proxy for requests.
        max_tokens_rsp (Required[int]): Max tokens in response.
        deployment_id (Optional[str]): Deployment ID.
        max_budget (Required[float]): Max budget.
        total_cost (Required[float]): Current total cost.
        long_term_memory (Optional[bool]): Use long term memory.
        mmdc (Required[str]): Path to mermaid CLI.
        calc_usage (Required[bool]): Calculate usage.
        model_for_researcher_summary (Optional[str]): Model for summary.
        model_for_researcher_report (Optional[str]): Model for report.

    """

    # Global Config
    global_proxy: Optional[constr(regex="^https?://.*$")] = None
    max_tokens_rsp: Required[conint(ge=100)] = 2048
    deployment_id: Optional[str] = None
    max_budget: Required[confloat(gt=0)] = 10.00
    total_cost: Required[confloat(ge=0)] = 0.00
    long_term_memory: Required[
        bool
    ] = False  # TODO: Log warning if this is set to True with valididator
    mmdc: Required[str] = "mmdc"
    calc_usage: Required[bool] = True
    model_for_researcher_summary: Optional[str]
    model_for_researcher_report: Optional[str]

    class Config:
        title = "Base Application Config"
        description = "Common application configuration settings."

    def get_api_keys(self) -> List[str]:
        """Returns a list of API keys"""
        return [field.name for field in self.__fields__ if field.endswith("_api_key")]

    def get_required_fields(self) -> List[str]:
        """Returns a list of required fields"""
        required_fields = []
        for field_name, field_info in self.__annotations__.items():
            field_value = getattr(self, field_name)
            if field_value is not None:
                required_fields.append(field_name)
        return required_fields

    def get_optional_fields(self) -> List[str]:
        """Returns a list of optional fields"""
        required_fields = []
        for field_name, field_info in self.__annotations__.items():
            field_value = getattr(self, field_name)
            if field_value is None:
                required_fields.append(field_name)
        return required_fields

    @property
    def config_dict(self):
        return self.dict()
