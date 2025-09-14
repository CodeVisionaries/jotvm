from typing import Union
import operator
from .json_patch_op_base import JsonPatchOpBase
from .json_pointer import JsonPointer
from .utils import (
    obtain_value,
    MissingValue,
)
from .json.types import JsonContainerTypeHint


__all__ = ['RELATION_OP_CLASSES']


class BinaryRelationOpBase(JsonPatchOpBase):
    """Abstract base class for relations."""

    @classmethod
    def basic_op(cls, val1, val2):
        """Basic relation operation to be applied."""
        raise NotImplementedError('implement `basic_op` method')

    def apply(self, json_doc: JsonContainerTypeHint):
        path = JsonPointer(self._fields['path'])
        left_value = obtain_value('left-value', self._fields, json_doc) 
        right_value = obtain_value('right-value', self._fields, json_doc)
        relation_value = self.basic_op(left_value, right_value)
        path.add(json_doc, relation_value)


def make_binary_relation_op_class(class_name: str, op_name: str, op_func: callable):
    return type(class_name, (BinaryRelationOpBase,), {
        'get_op_name': classmethod(lambda cls: op_name),
        'basic_op': classmethod(lambda cls, v1, v2: op_func(v1, v2)),
    })


relation_op_class_defs = [
    ('NumberEqual', 'number/equal', operator.eq),
    ('NumberNotEqual', 'number/not-equal', operator.ne),
    ('NumberGreater', 'number/greater', operator.gt),
    ('NumberGreaterEqual', 'number/greater-equal', operator.ge),
    ('NumberLessEqual', 'number/less-equal', operator.le),
]


RELATION_OP_CLASSES = [
    make_binary_relation_op_class(name, op_name, func)
    for name, op_name, func in relation_op_class_defs
]
