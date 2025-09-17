from __future__ import annotations
import inspect
import json
from abc import ABC, abstractmethod
from collections.abc import (
    MutableMapping,
    MutableSequence,
)
from typing import (
    Optional,
    Union,
    List,
    TypeVar,
    Generic,
)
from decimal import (
    Decimal,
    Context,
    localcontext,
    ROUND_HALF_EVEN,
)
from .tokens import (
    TOK_REGEX,
    tokenize,
    TokenStream,
)


JsonValueType = TypeVar('JsonValueType', bound='JsonValue')


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


class JsonValue(ABC):
    """Abstract base class for all JSON types."""

    @abstractmethod
    def to_json(self, conv_args=None) -> str:
        """Convert object to JSON format."""
        pass

    @abstractmethod
    def to_python(self) -> object:
        pass

    @classmethod
    @abstractmethod
    def from_python(cls, **extra_args) -> JsonValue:
        pass

    @classmethod
    @abstractmethod
    def parse(cls, tokens: TokenStream) -> JsonValue:
        pass

    @abstractmethod
    def __eq__(self, other):
        pass

    CONTEXT = Context(
        prec=28, rounding=ROUND_HALF_EVEN
    )

    @staticmethod
    def _create_unary_op(operator, wrap=True):
        """Create binary op method. Assumes existence of self.value."""
        def unary_op(self):
            with localcontext(self.CONTEXT) as ctx:
                pure_value = getattr(self.value, operator)()
                if not wrap:
                    return pure_value
                return JsonFactory.from_python(
                    getattr(self.value, operator())
                )
        return unary_op

    @staticmethod
    def _create_binary_op(operator, wrap=True, strict_type=True):
        """Create unary op method. Assumes presence of self.value."""
        def binary_op(self, other):
            if isinstance(other, type(self)):
                other_value = other.value
            elif not strict_type:
                other_value = other
            else:
                return NotImplemented

            with localcontext(self.CONTEXT) as ctx:
                pure_value = getattr(self.value, operator)(other_value)
                if not wrap:
                    return pure_value
                return JsonFactory.from_python(pure_value)
        return binary_op


@JsonFactory.register_python_types_deco(
    py_types=(dict,), start_toks=('LBRACE',), require_decimal=True
)
class JsonObject(
    JsonValue, MutableMapping['JsonString', JsonValueType], Generic[JsonValueType]
):
    def __init__(self, items: Optional[dict[JsonString, JsonValue]]=None, require_decimal=True):
        items = items if items else {}
        if not all(isinstance(k, JsonString) for k in items.keys()):
            raise TypeError('keys must be JsonString')
        if not all(isinstance(v, JsonValue) for v in items.values()):
            raise TypeError('All values must be instances of JsonValue')
        self.value = dict(items)

    def to_python(self) -> dict:
        return {k.to_python(): v.to_python() for k, v in self.value.items()}

    @classmethod
    def from_python(cls, py_dict: dict, require_decimal=True) -> JsonObject:
        return cls({
            JsonString(k): JsonFactory.from_python(v, require_decimal)
            for k, v in py_dict.items()
        })

    def to_json(self, conv_args=None) -> str:
        pairs = (
            f'{k.to_json()}:{v.to_json()}' for k, v in self.value.items()
        )
        return '{' + ','.join(pairs) + '}'

    @classmethod
    def parse(cls, tokens: TokenStream) -> JsonObject:
        tokens.consume('LBRACE')
        properties = {}

        if tokens.peek()[0] == 'RBRACE':
            tokens.consume('RBRACE')
            return cls(properties)

        while True:
            _, tok_val = tokens.consume('STRING')
            key = JsonString(JsonString._unquote(tok_val))
            tokens.consume('COLON')
            json_value = JsonFactory.parse(tokens)
            properties[key] = json_value

            tok_type = tokens.peek()[0]
            if tok_type == 'COMMA':
                tokens.consume('COMMA')
            elif tok_type == 'RBRACE':
                tokens.consume('RBRACE')
                break
            else:
                raise SyntaxError(
                    f'Expected "COMMA" or "RBRACE" but got "{tok_type}"'
                )

        return cls(properties)

    def __repr__(self):
        return f'JsonObject({self.value!r})'

    __eq__ = JsonValue._create_binary_op('__eq__', False, False)

    @staticmethod
    def _normalize_key(key: Union[str, JsonString]) -> JsonString:
        if isinstance(key, str):
            key = JsonString(key)
        elif not isinstance(key, JsonString):
            raise TypeError('Key must be a JsonString')
        return key

    def __getitem__(self, key: Union[JsonString, str]) -> JsonValue:
        key = self._normalize_key(key)
        self.value[key]
        return self.value[key]

    def __setitem__(self, key: JsonString, value: JsonValue) -> None:
        key = self._normalize_key(key)
        self.value[key] = value

    def __delitem__(self, key: JsonString) -> None:
        key = self._normalize_key(key)
        del self.value[key]

    def __iter__(self):
        return iter(self.value)

    def __len__(self):
        return len(self.value)


@JsonFactory.register_python_types_deco(
    py_types=(list,), start_toks=('LBRACKET',), require_decimal=True
)
class JsonArray(JsonValue, MutableSequence[JsonValueType], Generic[JsonValueType]):
    def __init__(self, values: Optional[list[JsonValue]]=None):
        values = values if values else []
        if not all (isinstance(v, JsonValue) for v in values):
            raise TypeError('All array elements must be of type `JsonValue`')
        self.value = list(values)

    def to_python(self) -> list:
        return [v.to_python() for v in self.value]

    @classmethod
    def from_python(self, py_list: list, require_decimal=True) -> JsonArray:
        return JsonArray(
            [JsonFactory.from_python(v, require_decimal) for v in py_list]
        )

    def to_json(self, conv_args=None) -> str:
        return '[' + ','.join(v.to_json() for v in self.value) + ']'

    @classmethod
    def parse(cls, tokens: TokenStream) -> JsonArray:
        values = []
        tokens.consume('LBRACKET')
        if tokens.peek()[0] == 'RBRACKET':
            return cls(values)

        while True:
            value = JsonFactory.parse(tokens)
            values.append(value)
            tok_type, tok_val = tokens.consume()
            if tok_type == 'RBRACKET':
                break
            elif tok_type != 'COMMA':
                raise SyntaxError('Expected "COMMA" or "RBRACKET"')

        return cls(values)

    def __repr__(self):
        return f'JsonArray({self.value!r})'

    __eq__ = JsonValue._create_binary_op('__eq__', False, False)

    def __getitem__(self, index: int) -> JsonValue:
        return self.value[index]

    def __setitem__(self, index: int, value: JsonValue) -> None:
        if not isinstance(value, JsonValue):
            raise TypeError('Value must be a JsonValue')
        self.value[index] = value

    def __delitem__(self, index: int) -> None:
        del self.value[index]

    def __len__(self):
        return len(self.value)

    def insert(self, index: int, value: JsonValue) -> None:
        if not isinstance(value, JsonValue):
            raise TypeError('Value must be a JsonValue')
        self.value.insert(index, value)


@JsonFactory.register_python_types_deco(
    py_types=(str,), start_toks=('STRING',)
)
class JsonString(JsonValue):
    def __init__(self, string: str):
        if not isinstance(string, str):
            raise TypeError('Expected a string')
        self.value = string

    def to_python(self) -> str:
        return self.value

    @classmethod
    def from_python(cls, string: str) -> JsonString:
        return cls(string)

    def to_json(self, conv_args=None) -> str:
        return json.dumps(self.value)

    @staticmethod
    def _unquote(string: str) -> str:
        if string.startswith('"') and string.endswith('"'):
            return string[1:-1]
        raise ValueError(f'Invalid JSON string: {string}')

    @staticmethod
    def _quote(string: str) -> str:
        return f'"{string}"'

    @classmethod
    def parse(cls, tokens: TokenStream) -> JsonString:
        tok_type, tok_val = tokens.consume('STRING')
        return cls(cls._unquote(tok_val))

    def __repr__(self):
        return f'JsonString("{self.value}")'

    def __hash__(self):
        return hash(self.value)

    __eq__ = JsonValue._create_binary_op('__eq__', False, False)

    def __getitem__(self, key):
        return JsonString(self.value[key])

    def endswith(self, suffix):
        if isinstance(suffix, JsonString):
            suffix = suffix.value
        elif isinstance(suffix, tuple):
            suffix = tuple(
                s.value if isinstance(s, JsonString) else s for s in suffix
            )
        elif not isinstance(suffix, str):
            raise TypeError(
                '`suffix` must be of type `str`, `JsonString`, or tuple thereof'
            )
        return self.value.endswith(suffix)


@JsonFactory.register_python_types_deco(
    py_types=(int, float, Decimal), start_toks=('NUMBER',), require_decimal=True
)
class JsonNumber(JsonValue):

    def __init__(self, value, require_decimal=True):
        if not isinstance(value, (int, str, Decimal)) and require_decimal:
            raise ValueError('Expected value to be `Decimal` when require_decimal=True')
        decimal_value = Decimal(value)
        if not decimal_value.is_finite():
            raise ValueError('JSON does not support Infinity or NaN')
        self.value = decimal_value

    def to_python(self) -> Decimal:
        return self.value

    @classmethod
    def from_python(cls, value, require_decimal=True) -> JsonNumber:
        return cls(value, require_decimal)

    def to_json(self) -> str:
        return str(self.value)

    @classmethod
    def parse(cls, tokens: TokenStream) -> JsonNumber:
        tok_type, tok_val = tokens.consume('NUMBER')
        value = Decimal(tok_val)
        return cls(value)

    def __repr__(self):
        return f'JsonNumber("{self.value!s}")'

    def __hash__(self):
        return hash(self.value)

    def __index__(self):
        if self.value != self.value.to_integral_value():
            raise TypeError('JsonNumber value is not an integer')
        return int(self.value)

    __float__ = JsonValue._create_unary_op('__float__', False)
    __int__ = JsonValue._create_unary_op('__int__', False)

    __eq__ = JsonValue._create_binary_op('__eq__', False, False)
    __ne__ = JsonValue._create_binary_op('__ne__', False, False)
    __lt__ = JsonValue._create_binary_op('__lt__', False, False)
    __le__ = JsonValue._create_binary_op('__le__', False, False)
    __gt__ = JsonValue._create_binary_op('__gt__', False, False)
    __ge__ = JsonValue._create_binary_op('__ge__', False, False)

    __add__      = JsonValue._create_binary_op('__add__', True, False)
    __radd__     = JsonValue._create_binary_op('__radd__', True, False)
    __sub__      = JsonValue._create_binary_op('__sub__', True, False)
    __mul__      = JsonValue._create_binary_op('__mul__', True, False)
    __truediv__  = JsonValue._create_binary_op('__truediv__', True, False)
    __floordiv__ = JsonValue._create_binary_op('__floordiv__', True, False)
    __mod__      = JsonValue._create_binary_op('__mod__', True, False)
    __pow__      = JsonValue._create_binary_op('__pow__', True, False)


@JsonFactory.register_python_types_deco(py_types=(bool,), start_toks=('TRUE', 'FALSE'))
class JsonBool(JsonValue):
    def __init__(self, value: Union[bool, JsonBool]) -> None:
        if not isinstance(value, (JsonBool, bool)):
            raise TypeError('Expected value of type `bool` or `JsonBool`')
        self.value = bool(value)

    def to_python(self) -> bool:
        return self.value

    @classmethod
    def from_python(cls, value) -> JsonBool:
        return cls(value)

    def to_json(self) -> str:
        return "true" if self.value else "false"

    @classmethod
    def parse(cls, tokens: TokenStream) -> JsonBool:
        tok_type, tok_val = tokens.consume()
        if tok_type == 'TRUE':
            return cls(True)
        elif tok_type == 'FALSE':
            return cls(False)
        raise SyntaxError(
            'Expected token of type "TRUE" or "FALSE"'
        )

    def __repr__(self):
        return f'JsonBool({self.value!r})'

    __bool__ = JsonValue._create_unary_op('__bool__', False)

    __eq__ =  JsonValue._create_binary_op('__eq__', False, False)

    __not__ = JsonValue._create_unary_op('__not__', False)
    __and__ = JsonValue._create_binary_op('__and__', False, False)
    __or__  = JsonValue._create_binary_op('__or__', False, False)
    __xor__ = JsonValue._create_binary_op('__xor__', False, False)


@JsonFactory.register_python_types_deco(py_types=(type(None),), start_toks=('NULL',))
class JsonNull(JsonValue):
    def __init__(obj=None) -> None:
        if obj is not None:
            raise TypeError('Expected obj to be `None`')

    def __eq__(self, other):
        return isinstance(other, JsonNull)

    def to_python(self) -> None:
        return None

    @classmethod
    def from_python(cls, value):
        return cls()

    def to_json(self) -> str:
        return "null"

    @classmethod
    def parse(cls, tokens: TokenStream) -> JsonNull:
        tokens.consume('NULL')
        return JsonNull()

    def __repr__(self) -> str:
        return 'JsonNull()'

    __eq__ =  JsonValue._create_binary_op('__eq__', False, False)


JsonContainerTypes = (JsonObject, JsonArray)
JsonContainerTypeHint = Union[JsonContainerTypes]


def check_container_type(json_doc: JsonContainerTypeHint):
    if not isinstance(json_doc, JsonContainerTypes):
        raise TypeError('json_doc must be either JsonObject or JsonArray')
