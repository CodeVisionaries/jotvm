from __future__ import annotations
from abc import ABC, abstractmethod
from .tokens import (
    TOK_REGEX,
    tokenize,
    TokenStream,
)
from .json_value import JsonValue


class JsonParsableMixin(ABC):
    """Abstract mixin for JSON classes supporting parsing."""

    @classmethod
    @abstractmethod
    def from_python(cls, **extra_args) -> JsonValue:
        """Method to convert a Python object into a JsonValue."""
        pass

    @classmethod
    @abstractmethod
    def parse(cls, tokens: TokenStream) -> JsonValue:
        """Method to parse tokens into a JsonValue."""
        pass


class JsonFactory:

    PYTHON_JSON_MAP = {}
    REQUIRE_DECIMAL = {}
    START_TOK = {}

    @classmethod
    def register_python_types(
        cls, json_class, py_types, start_toks, require_decimal=False
    ):
        """Register Python types with a Json class."""
        if not issubclass(json_class, JsonValue):
            raise TypeError('json_class must be a subclass of JsonValue')

        for t in py_types:
            cls.PYTHON_JSON_MAP[t] = json_class
        cls.REQUIRE_DECIMAL[json_class] = require_decimal
        for s in start_toks:
            cls.START_TOK[s] = json_class
        return json_class

    @classmethod
    def register_python_types_deco(
        cls, py_types, start_toks, require_decimal=False
    ):
        def decorator(json_class):
            if not issubclass(json_class, JsonParsableMixin):
                json_class = type(
                    json_class.__name__,
                    (json_class, JsonParsableMixin),
                    dict(json_class.__dict__)
                )

            cls.register_python_types(
                json_class, py_types, start_toks, require_decimal
            )
            return json_class

        return decorator

    @classmethod
    def from_python(cls, obj, require_decimal=True):
        json_type = cls.PYTHON_JSON_MAP.get(type(obj))
        if json_type is None:
            raise TypeError(f'No known mapping from {type(obj)} to JSON class')

        extra_args = {}
        if cls.REQUIRE_DECIMAL.get(json_type, False):
            extra_args['require_decimal'] = require_decimal

        return json_type.from_python(obj, **extra_args)

    @classmethod
    def parse(cls, tokens: TokenStream):
        next_tok = tokens.peek()
        json_type = cls.START_TOK.get(next_tok[0])
        if json_type is None:
            raise SyntaxError(f'Unexpected token {next_tok[0]}')
        return json_type.parse(tokens)

    @classmethod
    def _token_stream(cls, json_string: str):
        return TokenStream(list(tokenize(json_string, TOK_REGEX)))


    @classmethod
    def from_json(cls, json_string: str):
        return cls.parse(cls._token_stream(json_string))
