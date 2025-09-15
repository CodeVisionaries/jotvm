from typing import Union
from .json_patch_op_base import JsonPatchOpBase
from .json_pointer import JsonPointer
from .utils import (
    int_to_str,
    obtain_value,
    ensure_array,
    ensure_string,
)
from .json.types import (
    JsonContainerTypeHint,
    JsonNumber,
    JsonArray,
    JsonString,
)


__all__ = ['TRAFO_UNARY_OP_CLASSES']


class TrafoUnaryOpBase(JsonPatchOpBase):
    """Abstract base class for transforming unary operation."""

    # NOTE: `trafo` (short for transforming) means that the type
    #       of the argument is different from the type of the
    #       result. For instance, len("hallo") is transforming,
    #       because the input is a string and the output is an integer.

    @classmethod
    def basic_op(cls, val):
        """Basic binary operation to be applied."""
        raise NotImplementedError('implement `basic_op` method')

    def apply(self, json_doc: JsonContainerTypeHint):
        arg_value = obtain_value('value', self._fields, json_doc)
        result = self.basic_op(arg_value)
        path = JsonPointer(self._fields['path'])
        if path.exists(json_doc):
            path.remove(json_doc)
        path.add(json_doc, result)


def make_trafo_unary_op_class(class_name: str, op_name: str, op_func: callable):
    return type(class_name, (TrafoUnaryOpBase,), {
        'get_op_name': classmethod(lambda cls: op_name),
        'basic_op': classmethod(lambda cls, v: op_func(v)),
    })


trafo_unary_op_class_defs = [
    ('StringSplitPath', 'string/split-path', lambda v: JsonPointer(ensure_string(v)).to_json_array()),
    ('ArrayJoinPath', 'array/join-path', lambda v: JsonString((str(JsonPointer(ensure_array(v)))))),
    ('ArrayLength', 'array/length', lambda v: JsonNumber(len(ensure_array(v)))),
]


TRAFO_UNARY_OP_CLASSES = [
    make_trafo_unary_op_class(name, op_name, func)
    for name, op_name, func in trafo_unary_op_class_defs
]
