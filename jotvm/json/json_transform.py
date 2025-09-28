from __future__ import annotations
from typing import Callable
from abc import ABC, abstractmethod
from .json_factory import JsonFactory
from .tokens import TokenStream
from .json_value import JsonValue
from .json_types import JsonObject, JsonArray
from .json_transform_base import JsonTransformBase
from .json_link import JsonLinkTransform


class JsonTransformRegistry:
    """A registry class for JSON transformations."""

    _transforms: List[JsonTransformBase] = []

    @classmethod
    def register(cls, transform: JsonTransformBase) -> None:
        """Register transformation."""
        cls._transforms.append(transform)

    @classmethod
    def register_deco(cls) -> Callable[[JsonTransformBase], JsonTransformBase]:
        def decorator(transform: JsonTransformBase):
            cls.register(transform)
            return transform

        return decorator

    @classmethod
    def transform(cls, value: JsonValue) -> JsonValue:
        """Apply all registered transformations."""
        for transform in cls._transforms:
            if transform.match(value):
                return transform.transform(value)

        if isinstance(value, JsonObject):
            return JsonObject({
                k: cls.transform(v) for k, v in value.items()
            })
        elif isinstance(value, JsonArray):
            return JsonArray([cls.transform(v) for v in value])

        return value


JsonTransformRegistry.register(JsonLinkTransform())


class TransformingJsonFactory(JsonFactory):

    _transform_func = JsonTransformRegistry.transform

    @classmethod
    def from_python(cls, obj, require_decimal=True) -> JsonValue:
        json_value = super().from_python(obj, require_decimal)
        return cls._transform_func(json_value)

    @classmethod
    def parse(cls, tokens: TokenStream) -> JsonValue:
        json_value = super().parse(tokens)
        return cls._transform_func(json_value)

    @classmethod
    def from_json(cls, json_string: str) -> JsonValue:
        json_value = super().from_json(json_string)
        return cls._transform_func(json_value)
