from typing import Any, Type

from pydantic import BaseModel


def dump(schema: Type[BaseModel], obj: Any) -> dict:
    data = schema.model_validate(obj)
    extra = getattr(obj, "_extra_response", None)
    result = data.model_dump(mode="json")
    if extra:
        result.update(extra)
    return result


def dump_list(schema: Type[BaseModel], items: list[Any]) -> list[dict]:
    return [dump(schema, item) for item in items]
