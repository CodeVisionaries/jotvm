from __future__ import annotations
from .json_value import JsonValue
from .json_types import JsonObject, JsonString
from .json_transform_base import JsonTransformBase


class JsonLink(JsonValue):
    def __init__(self, target: str):
        if not isinstance(target, str):
            raise TypeError('Expected target to be type `str`')
        self.target = target

    def to_python(self) -> dict:
        return {'/': self.target}

    def to_json(self) -> str:
        return '{"/":"' + self.target + '"}'

    def __repr__(self) -> str:
        return f'JsonLink({self.target!r})'

    def __eq__(self, other):
        if isinstance(other, JsonLink):
            return self.target == other.target
        return False


class JsonLinkTransform(JsonTransformBase):

    def match(self, value: JsonValue) -> bool:
        return (
            isinstance(value, JsonObject)
            and set(value) == {JsonString('/')}
            and isinstance(value['/'], JsonString)
        )

    def transform(self, value: JsonValue) -> JsonLink:
        return JsonLink(value['/'].to_python())
