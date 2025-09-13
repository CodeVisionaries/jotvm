from typing import Union
from copy import deepcopy
from .json_patch_ops import PATCH_OP_CLASSES
from .binary_ops import BINARY_OP_CLASSES
from .relation_ops import RELATION_OP_CLASSES
from .controls import CONTROL_OP_CLASSES
from .trafo_unary_ops import TRAFO_UNARY_OP_CLASSES
from .endo_unary_ops import ENDO_UNARY_OP_CLASSES
from .json.types import JsonContainerType
from .debug import SimpleDebugPrinter


class JsonPatchBase:

    def __init__(self, patch_ops, debug=True):
        self._patch_ops = deepcopy(patch_ops)
        self._debugger = SimpleDebugPrinter()

    @classmethod
    def _get_op_types(self):
        raise NotImplementedError('Implement in child class')

    @classmethod
    def from_list(cls, patch_ops, debug=True):
        op_types = cls._get_op_types()
        op_list = []
        for op_dict in patch_ops:
            op_class = op_types[op_dict['op']]
            op = op_class.from_dict(op_dict)
            op_list.append(op)
        return cls(op_list, debug=debug)

    def to_list(self):
        return [op.to_dict() for op in self._patch_ops]

    def __call__(self, json_doc: JsonContainerType):
        debug_msg = self._debugger.debug
        debug_msg('\n=== Initial State of JSON Document ===\n')
        debug_msg(json_doc)
        debug_msg('\n=== Start of patch application ===\n')

        for op in self._patch_ops:
            debug_msg(f'Applying {op!r}')
            op(json_doc)
            debug_msg('\n---> New State of JSON Document:\n')
            debug_msg(str(json_doc) + '\n')

        debug_msg('=== End of Patch Application ===\n')

    def apply(self, json_doc: JsonContainerType):
        self(json_doc)


class JsonPatch(JsonPatchBase):

    @classmethod
    def _get_op_types(self):
        return {
            cl.get_op_name(): cl for cl in PATCH_OP_CLASSES
        }


class ExtJsonPatch(JsonPatch):

    @classmethod
    def _get_op_types(self):
        op_types = super()._get_op_types()
        op_types.update({
            cl.get_op_name(): cl for cl in BINARY_OP_CLASSES
        })
        op_types.update({
            cl.get_op_name(): cl for cl in RELATION_OP_CLASSES
        })
        op_types.update({
            cl.get_op_name(): cl for cl in CONTROL_OP_CLASSES
        })
        op_types.update({
            cl.get_op_name(): cl for cl in TRAFO_UNARY_OP_CLASSES
        })
        op_types.update({
            cl.get_op_name(): cl for cl in ENDO_UNARY_OP_CLASSES
        })
        return op_types
