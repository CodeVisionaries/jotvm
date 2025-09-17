from typing import Union
from collections.abc import Sequence
from decimal import Decimal
from .json.types import (
    JsonContainerTypes,
    JsonContainerTypeHint,
    check_container_type,
    JsonValue,
    JsonString,
    JsonArray,
    JsonObject,
)


class JsonPointer(Sequence):

    def __init__(self, json_pointer):
        if isinstance(json_pointer, JsonPointer):
            self._path = tuple(json_pointer)
            return

        if isinstance(json_pointer, JsonValue): 
            json_pointer = json_pointer.to_python()

        if isinstance(json_pointer, str):
            if json_pointer == '':
                self._path = tuple()
            elif json_pointer.startswith('/'):
                segments = json_pointer.split('/')[1:]
                self._path = tuple(self._decode_segment(s) for s in segments)
            else:
                raise ValueError(f'Invalid JSON pointer `{json_pointer!s}`')
        elif isinstance(json_pointer, (list, tuple)):
            err_prefix = f'Invalid tuple representation of JSON pointer {json_pointer}: '
            if any(v != int(v) for v in json_pointer if isinstance(v, (float, Decimal))):
                raise ValueError(
                    err_prefix + 'All path elements of type float must be integer-valued'
                )
            json_pointer = tuple(
                int(v) if isinstance(v, (float, Decimal)) else v
                for v in json_pointer
            )
            if any(type(p) not in (str, int) for p in json_pointer):
                raise ValueError(
                    err_prefix + 'All path elements must be strings or integer-valued'
                )
            if any('/' in str(p) for p in json_pointer):
                raise ValueError(
                    err_prefix + 'Invalid character "/" in field name string'
                )
            self._path = tuple(str(p) for p in json_pointer)
        else:
            raise TypeError(f'Unsupported type {type(json_pointer)}')

    # ------------ Escaping Utilities ------------

    @staticmethod
    def _decode_segment(segment: str) -> str:
        return segment.replace('~1', '/').replace('~0', '~')

    @staticmethod
    def _encode_segment(segment: str) -> str:
        return segment.replace('~', '~0').replace('/', '~1')

    # ------------ Sequence Protocol -------------

    def __eq__(self, other):
        if isinstance(other, JsonPointer):
            return tuple(self) == tuple(other)
        return NotImplemented

    def __iter__(self):
        for part in self._path:
            yield part

    def __len__(self):
        return len(self._path)

    def __getitem__(self, index_or_slice):
        return type(self)(self._path[index_or_slice])

    def __repr__(self):
        path_str = str(self)
        return f'JsonPointer("{path_str!s}")'

    def __str__(self):
        if len(self._path) == 0:
            return ''
        return '/' + '/'.join(self._encode_segment(s) for s in self._path)

    def to_json_array(self):
        return JsonArray([JsonString(s) for s in self._path])

    # ------------ Key Handling ------------------

    @staticmethod
    def _sanitize_key(obj, key):
        if isinstance(obj, JsonArray):
            # special notation for appending
            if key == '-':
                return len(obj)
            return int(key)
        elif isinstance(obj, JsonObject):
            if isinstance(key, JsonString):
                return key
            elif isinstance(key, str):
                return JsonString(key)

        raise TypeError(f"Invalid type {type(obj)} of `obj`")

    @classmethod
    def _get(cls, obj, key):
        key = cls._sanitize_key(obj, key)
        return obj[key]

    @classmethod
    def _exists(cls, obj, key):
        p = cls._sanitize_key(obj, key)
        if isinstance(obj, JsonArray):
            return p >= 0 and p < len(obj)
        elif isinstance(obj, JsonObject):
            return p in obj

    # ------------ Core Methods ------------------

    def exists(self, obj: JsonContainerTypeHint) -> bool:
        check_container_type(obj)
        for p in self._path:
            if not self._exists(obj, p):
                return False
            obj = self._get(obj, p)
        return True

    def get(self, obj: JsonContainerTypeHint, default: JsonValue=...) -> JsonValue:
        check_container_type(obj)
        if default is not ...:
            if not self.exists(obj):
                return default
        for p in self._path:
            obj = self._get(obj, p)
        return obj

    def add(self, obj: JsonContainerTypeHint, value: JsonValue) -> None:
        check_container_type(obj)
        for p in self._path[:-1]:
            obj = self._get(obj, p)
        p = self._sanitize_key(obj, self._path[-1])
        if isinstance(obj, JsonObject):
            obj[p] = value
        elif isinstance(obj, JsonArray):
            if not (0 <= p <= len(obj):
                    raise IndexError(f'Index {p} out of bounds for JSON array')
            obj.insert(p, value)

    def remove(self, obj: JsonContainerTypeHint) -> None:
        check_container_type(obj)
        for p in self._path[:-1]:
            obj = self._get(obj, p)
        p = self._sanitize_key(obj, self._path[-1])
        del obj[p]
