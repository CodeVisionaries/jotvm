from typing import Union
from .json_pointer import JsonPointer
from copy import deepcopy
from .json.json_types import (
    JsonString,
    JsonObject,
    JsonContainerTypeHint,
)


class JsonPatchOpBase:
    """Abstract base class for JSON patch op classes."""

    # Needs to be implemented in derived classes
    @classmethod
    def get_op_name(cls):
        """Get operation name."""
        raise NotImplementedError('implement `get_op_name` method')

    def apply(self, json_doc: JsonContainerTypeHint):
        """Apply JSON patch operation on JSON document."""
        raise NotImplementedError('implement `apply` method')

    # Generic functions for all derived classes
    def __init__(self, json_doc: JsonObject):
        """Initialize JSON patch operation class."""
        if not isinstance(json_doc, JsonObject):
            raise TypeError('`json_doc` must be of type `JsonObject`')

        self._verify(json_doc)
        fields = deepcopy(json_doc)
        for key in fields:
            if isinstance(fields[key], JsonPointer):
                fields[key] = str(fields[key])
        self._fields = fields

    @classmethod
    def _verify(cls, json_doc: JsonContainerTypeHint):
        """Internal method to verify dict representation of op."""
        expect_op = cls.get_op_name()
        current_op = json_doc['op']
        if expect_op != current_op.to_python():
            raise ValueError(
                f'Expected operation `{expect_op}` but encountered `{current_op}`.'
            )

    def __call__(self, json_doc: JsonContainerTypeHint) -> None:
        self.apply(json_doc)

    @classmethod
    def from_json_object(cls, json_doc: JsonObject) -> 'JsonPatchOpBase':
        return cls(json_doc)

    def to_json_object(self) -> JsonObject:
        return deepcopy(self._fields)

    def to_python(self) -> dict:
        """Export operation class instance to dict."""
        return self._fields.to_python()

    @classmethod
    def from_python(cls, json_doc: dict, require_decimal=True) -> 'JsonPatchOpBase':
        """Create operation class from dict."""
        if not isinstance(json_doc, dict):
            raise TypeError('`json_doc` must be of type `dict`')
        json_doc = JsonObject.from_python(json_doc, require_decimal)
        return cls(json_doc)

    def __repr__(self):
        return f'{self.__class__!s}({self._fields!s})'

    def __str__(self):
        return repr(self)


def make_patch_op_class(
    class_name: str, op_name: str, apply_fun: callable,
    base_class=JsonPatchOpBase
):
    """Make concrete JSON patch op class."""
    cls_dict = {
        'get_op_name': classmethod(lambda cls: op_name),
        'apply': apply_fun,
    }
    return type(class_name, (base_class,), cls_dict)
