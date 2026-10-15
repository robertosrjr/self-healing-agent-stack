"""Contratos tipados para o fluxo Maker-Checker."""

import json
from typing import Any, Literal, TypeVar

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)

T = TypeVar("T", bound=BaseModel)

MAX_TASK_LENGTH = 12_000
MAX_CONTEXT_JSON_BYTES = 32_000
MAX_PAYLOAD_JSON_BYTES = 32_000


class ContractValidationError(ValueError):
    """Falha de contrato sem incluir conteúdo rejeitado."""

    def __init__(self, code: str, paths: tuple[str, ...] = ()) -> None:
        self.code = code
        self.paths = paths
        location = ", ".join(paths) if paths else "$"
        super().__init__(f"Falha de contrato ({code}) nos caminhos: {location}")


class StrictContract(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


def _json_size(value: object) -> int:
    serialized = json.dumps(value, ensure_ascii=False, allow_nan=False)
    return len(serialized.encode("utf-8"))


def _is_json_value(value: object) -> bool:
    try:
        serialized = json.dumps(value, ensure_ascii=False, allow_nan=False)
        normalized = json.loads(serialized)
    except (TypeError, ValueError, RecursionError):
        return False

    pending = [(value, normalized)]
    while pending:
        original, decoded = pending.pop()
        if type(original) is not type(decoded):
            return False
        if isinstance(original, dict):
            if any(not isinstance(key, str) for key in original):
                return False
            pending.extend((item, decoded[key]) for key, item in original.items())
        elif isinstance(original, list):
            if len(original) != len(decoded):
                return False
            pending.extend(zip(original, decoded))
        elif not isinstance(original, (str, int, float, bool, type(None))):
            return False
    return True


def _validate_json_object_size(value: dict[str, Any], max_bytes: int) -> dict[str, Any]:
    if not _is_json_value(value):
        raise ValueError("must contain only JSON-compatible values")
    size = _json_size(value)
    if size > max_bytes:
        raise ValueError("JSON object exceeds the allowed size")
    return value


class MakerCheckerRequest(StrictContract):
    request_id: str = Field(min_length=1, max_length=128)
    task: str = Field(min_length=1, max_length=MAX_TASK_LENGTH)
    context: dict[str, Any] = Field(max_length=100)

    @field_validator("context")
    @classmethod
    def validate_context(cls, value: dict[str, Any]) -> dict[str, Any]:
        return _validate_json_object_size(value, MAX_CONTEXT_JSON_BYTES)


class MakerResult(StrictContract):
    status: Literal["COMPLETED", "INCONCLUSIVE"]
    payload: dict[str, Any] = Field(max_length=100)
    evidence: list[str] = Field(max_length=50)

    @field_validator("payload")
    @classmethod
    def validate_payload(cls, value: dict[str, Any]) -> dict[str, Any]:
        return _validate_json_object_size(value, MAX_PAYLOAD_JSON_BYTES)


class CheckerInput(StrictContract):
    request: MakerCheckerRequest
    maker_result: MakerResult


class CheckerResult(StrictContract):
    decision: Literal["APPROVED", "REJECTED", "INCONCLUSIVE"]
    findings: list[str] = Field(max_length=50)
    rationale: str = Field(min_length=1, max_length=4_000)


class MakerCheckerResponse(StrictContract):
    request_id: str = Field(min_length=1, max_length=128)
    status: Literal["APPROVED", "REJECTED", "INCONCLUSIVE"]
    maker_result: MakerResult
    checker_result: CheckerResult | None

    @model_validator(mode="after")
    def validate_decision_consistency(self) -> "MakerCheckerResponse":
        if self.checker_result is None:
            if self.maker_result.status != "INCONCLUSIVE" or self.status != "INCONCLUSIVE":
                raise ValueError("checker may be absent only for an inconclusive Maker result")
        elif self.maker_result.status != "COMPLETED" or self.status != self.checker_result.decision:
            raise ValueError("response status must match the validated Checker decision")
        return self


def _validation_paths(error: ValidationError) -> tuple[str, ...]:
    paths = []
    for item in error.errors(include_url=False, include_input=False, include_context=False):
        location = ".".join(str(part) for part in item["loc"]) or "$"
        if location not in paths:
            paths.append(location)
    return tuple(paths)


def validate_contract(model_type: type[T], value: object) -> T:
    try:
        return model_type.model_validate(value)
    except ValidationError as exc:
        raise ContractValidationError(
            code="schema_invalid",
            paths=_validation_paths(exc),
        ) from exc


def parse_contract_json(model_type: type[T], raw: str) -> T:
    try:
        value = json.loads(raw)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ContractValidationError(code="invalid_json") from exc
    return validate_contract(model_type, value)
