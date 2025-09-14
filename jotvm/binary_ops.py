from typing import Union
from .json_patch_op_base import JsonPatchOpBase
from .json_pointer import JsonPointer
from .utils import (
    obtain_value,
    MissingValue,
)
import operator
from .json.types import (
    JsonContainerTypes,
    JsonContainerTypeHint,
)


__all__ = ['BINARY_OP_CLASSES']


class BinaryOpBase(JsonPatchOpBase):
    """Abstract base class for in-place binary operation."""

    @classmethod
    def basic_op(cls, val1, val2):
        """Basic binary operation to be applied."""
        raise NotImplementedError('implement `basic_op` method')

    def apply(self, json_doc: JsonContainerTypeHint):
        path = JsonPointer(self._fields['path'])
        old_value = path.get(json_doc)
        add_value = obtain_value('value', self._fields, json_doc)
        new_value = self.basic_op(old_value, add_value)
        path.remove(json_doc)
        path.add(json_doc, new_value)


def make_binary_op_class(class_name: str, op_name: str, op_func: callable):
    return type(class_name, (BinaryOpBase,), {
        'get_op_name': classmethod(lambda cls: op_name),
        'basic_op': classmethod(lambda cls, v1, v2: op_func(v1, v2)),
    })


binary_op_class_defs = [
    # binary math operators
    ('NumberAdd', 'number/add', operator.add),
    ('NumberSub', 'number/sub', operator.sub),
    ('NumberMul', 'number/mul', operator.mul),
    ('NumberDiv', 'number/div', operator.truediv),
    # binary logic operators
    ('BoolOr', 'bool/or', operator.or_),
    ('BoolAnd', 'bool/and', operator.and_),
]


BINARY_OP_CLASSES = [
    make_binary_op_class(name, op_name, func)
    for name, op_name, func in binary_op_class_defs
]
