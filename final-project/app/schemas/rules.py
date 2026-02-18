from pydantic import BaseModel

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
    action: Literal["block", "skip"] = "block"
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

