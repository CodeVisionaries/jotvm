from copy import deepcopy
from .json_patch_op_base import make_patch_op_class
from .json_pointer import JsonPointer
from .utils import obtain_value
from .json.types import JsonContainerType


__all__ = ['PATCH_OP_CLASSES']


# Define the apply method for each standard JSON patch operations

def add_op_apply(self, json_doc: JsonContainerType):
    path = JsonPointer(self._fields['path'])
    value = obtain_value('value', self._fields, json_doc)
    path.add(json_doc, value)


def remove_op_apply(self, json_doc: JsonContainerType):
    path = JsonPointer(self._fields['path'])
    path.remove(json_doc)


def replace_op_apply(self, json_doc: JsonContainerType):
    path = JsonPointer(self._fields['path'])
    value = obtain_value('value', self._fields, json_doc)
    path.remove(json_doc)
    path.add(json_doc, value)


def move_op_apply(self, json_doc: JsonContainerType):
    from_path = JsonPointer(self._fields['from'])
    to_path = JsonPointer(self._fields['path'])
    value = deepcopy(from_path.get(json_doc))
    from_path.remove(json_doc)
    to_path.add(json_doc, value)


def copy_op_apply(self, json_doc: JsonContainerType):
    from_path = JsonPointer(self._fields['from'])
    to_path = JsonPointer(self._fields['path'])
    value = deepcopy(from_path.get(json_doc))
    to_path.add(json_doc, value)


def test_op_apply(self, json_doc: JsonContainerType):
    path = JsonPointer(self._fields['path'])
    value = path.get(json_doc)
    test_value = obtain_value('value', self._fields, json_doc)
    if value != test_value:
        raise ValueError(
            f'value {value} does not match test value {test_value}'
        )


# Dynamically create the JSON patch operation classes.

patch_op_class_defs = [
    ('JsonPatchAddOp', 'add', add_op_apply),
    ('JsonPatchRemoveOp', 'remove', remove_op_apply),
    ('JsonPatchReplaceOp', 'replace', replace_op_apply),
    ('JsonPatchMoveOp', 'move', move_op_apply),
    ('JsonPatchCopyOp', 'copy', copy_op_apply),
    ('JsonPatchTestOp', 'test', test_op_apply),
]


PATCH_OP_CLASSES = [
    make_patch_op_class(class_name, op_name, apply_func)
    for class_name, op_name, apply_func in patch_op_class_defs
]
