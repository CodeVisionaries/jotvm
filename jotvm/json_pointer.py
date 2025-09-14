from typing import Union
from collections.abc import Sequence


class JsonPointer(Sequence):

    def __init__(self, json_pointer):
        if isinstance(json_pointer, JsonPointer):
            self._path = tuple(json_pointer)
        elif isinstance(json_pointer, str):
            if json_pointer == '':
                self._path = []
            elif json_pointer.startswith('/'):
                self._path = tuple(json_pointer.split('/')[1:])
            else:
                raise ValueError(f'Invalid JSON pointer `{json_pointer!s}`')
        elif isinstance(json_pointer, (list, tuple)):
            err_prefix = f'Invalid tuple representation of JSON pointer {json_pointer}: '
            if any(v != int(v) for v in json_pointer if isinstance(v, float)):
                raise ValueError(
                    err_prefix + 'All path elements of type float must be integer-valued'
                )
            json_pointer = tuple(int(v) if isinstance(v, float) else v for v in json_pointer)
            if any(type(p) not in (str, int) for p in json_pointer):
                raise ValueError(
                    err_prefix + 'All path elements must be strings or integer-valued'
                )
            if any('/' in str(p) for p in json_pointer):
                raise ValueError(
                    err_prefix + 'Invalid character "/" in field name string'
                )
            self._path = tuple(str(p) for p in json_pointer)

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
        return '/' + '/'.join(self._path)

    @staticmethod
    def _sanitize_key(obj, key):
        if isinstance(obj, list):
            # special notation for appending
            if key == '-':
                return len(obj)
            return int(key)
        elif isinstance(obj, dict):
            return key
        else:
            raise TypeError(f"Invalid type {type(obj)} of `obj`")

    @classmethod
    def _get(self, obj, key):
        key = self._sanitize_key(obj, key)
        return obj[key]

    @classmethod
    def _exists(self, obj, key):
        p = self._sanitize_key(obj, key)
        if isinstance(obj, list):
            return p >= 0 and p < len(obj)
        elif isinstance(obj, dict):
            return p in obj

    def exists(self, obj):
        for p in self._path:
            if not self._exists(obj, p):
                return False
            obj = self._get(obj, p)
        return True

    def get(self, obj, default=...):
        if default is not ...:
            if not self.exists(obj):
                return default
        for p in self._path:
            obj = self._get(obj, p)
        return obj

    def add(self, obj, value):
        for p in self._path[:-1]:
            obj = self._get(obj, p)
        p = self._sanitize_key(obj, self._path[-1])
        if isinstance(obj, dict):
            obj[p] = value
        elif isinstance(obj, list):
            obj.insert(p, value)

    def remove(self, obj):
        for p in self._path[:-1]:
            obj = self._get(obj, p)
        p = self._sanitize_key(obj, self._path[-1])
        del obj[p]
