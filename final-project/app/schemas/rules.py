from pydantic import BaseModel, model_validator, Field
from typing import Literal, Optional, List

class CreateRulesetRequest(BaseModel):
    name: str
    description: str

class SkipParameters(BaseModel):
    phases: Optional[List[Literal[
        "http_request_firewall_custom",
        "http_request_firewall_managed"
    ]]] = None

    ruleset: Optional[Literal["current"]] = None


class CreateRuleRequest(BaseModel):
    expression: str
    description: str
    action: Literal["block", "skip"] = Field(
    description="If action is 'skip', action_parameters is required. For 'block', it must not be provided."
)
    action_parameters: Optional[SkipParameters] = None

    @model_validator(mode="after")
    def validate_skip(cls, values):
        if values.action == "skip":
            if not values.action_parameters:
                raise ValueError("action_parameters is required when action is 'skip'")

            if not (values.action_parameters.phases or values.action_parameters.ruleset):
                raise ValueError("Skip must define either 'phases' or 'ruleset'")

        else:
            if values.action_parameters is not None:
                raise ValueError("action_parameters must not be provided when action is 'block'")

        return values
    
class RulePosition(BaseModel):
    before: Optional[str] = None
    after: Optional[str] = None
    index: Optional[int] = None

    @model_validator(mode="after")
    def validate_position(cls, values):
        provided = [
            values.before is not None,
            values.after is not None,
            values.index is not None,
        ]

        if sum(provided) != 1:
            raise ValueError(
                "You must provide exactly one of: before, after, or index."
            )
        return values

class ExportedRule(BaseModel):
    index: int
    zone_name: str
    zone_id: str
    ruleset_id: str
    rule_id: str
    description: str | None
    action: str
    expression: str | None
    enabled: bool

