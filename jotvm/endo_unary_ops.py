import math
from .json_patch_op_base import JsonPatchOpBase
from .json_pointer import JsonPointer
from .utils import (
    obtain_value,
    MissingValue,
    ensure_bool,
    ensure_number,
)
from .json_types import JsonContainerType


__all__ = ['ENDO_UNARY_OP_CLASSES']


class EndoUnaryOpBase(JsonPatchOpBase):
    """Abstract base class for type-preserving unary operation."""

    # NOTE: `endo` (from Greek `within`) means that the argument
    #       and result are of the same type.
    #       For instance, the square root maps a number to another number.

    @classmethod
    def basic_op(cls, val):
        """Basic binary operation to be applied."""
        raise NotImplementedError('implement `basic_op` method')

    def apply(self, json_doc: JsonContainerType):
        path = JsonPointer(self._fields['path'])
        arg_value = obtain_value('value', self._fields, json_doc, missing_ok=True)
        if arg_value is MissingValue:
            arg_value = path.get(json_doc)
        result = self.basic_op(arg_value)
        if path.exists(json_doc):
            path.remove(json_doc)
        path.add(json_doc, result)


def make_endo_unary_op_class(class_name: str, op_name: str, op_func: callable):
    return type(class_name, (EndoUnaryOpBase,), {
        'get_op_name': classmethod(lambda cls: op_name),
        'basic_op': classmethod(lambda cls, v: op_func(v)),
    })


endo_unary_op_class_defs = [
    ('NumberTrunc', 'number/trunc', lambda v: int(ensure_number(v))),
    ('NumberSqrt', 'number/sqrt', lambda v: math.sqrt(ensure_number(v))),
    ('NumberCos', 'number/cos', lambda v: math.cos(ensure_number(v))),
    ('NumberSin', 'number/sin', lambda v: math.sin(ensure_number(v))),
    ('BoolNot', 'bool/not', lambda v: not ensure_bool(v)),
]


ENDO_UNARY_OP_CLASSES = [
    make_endo_unary_op_class(name, op_name, func)
    for name, op_name, func in endo_unary_op_class_defs
]
