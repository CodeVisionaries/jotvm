from __future__ import annotations
from typing import Union
from .json_patch_ops import PATCH_OP_CLASSES
from .binary_ops import BINARY_OP_CLASSES
from .relation_ops import RELATION_OP_CLASSES
from .controls import CONTROL_OP_CLASSES
from .trafo_unary_ops import TRAFO_UNARY_OP_CLASSES
from .endo_unary_ops import ENDO_UNARY_OP_CLASSES
from .json.types import (
    JsonContainerTypeHint,
    JsonContainerTypes,
    JsonArray,
)
from .debug import SimpleDebugPrinter


class JsonPatchBase:

    def __init__(self, patch_ops: list['JsonPatchOpBase']):
        self._patch_ops = patch_ops.copy()
        self._debugger = SimpleDebugPrinter()

    @classmethod
    def _get_op_types(self):
        raise NotImplementedError('Implement in child class')

    @classmethod
    def from_json_array(cls, patch_ops: JsonArray[JsonObject]) -> 'JsonPatchBase':
        if not isinstance(patch_ops, JsonArray):
            raise TypeError('`patch_ops` must be type `JsonArray`')

        op_types = cls._get_op_types()
        op_list = []
        for op_dict in patch_ops:
            op_class = op_types[op_dict['op'].to_python()]
            op = op_class(op_dict)
            op_list.append(op)

        return cls(op_list)

    def to_json_array(self) -> list:
        return JsonArray([op.to_json_object() for op in self._patch_ops])

    @classmethod
    def from_python(cls, patch_ops: list[dict], require_decimal=True):
        json_patch_ops = JsonArray.from_python(patch_ops, require_decimal)
        return cls.from_json_array(json_patch_ops)

    def to_python(self):
        json_arr = self.to_json_array()
        return json_arr.to_python()

    def __call__(self, json_doc: JsonContainerTypeHint):
        if not isinstance(json_doc, JsonContainerTypes):
            raise TypeError('json_doc must be either JsonObject or JsonArray')

        debug_msg = self._debugger.debug
        debug_msg('\n=== Initial State of JSON Document ===\n')
        debug_msg(json_doc.to_python())
        debug_msg('\n=== Start of patch application ===\n')

        for op in self._patch_ops:
            debug_msg(f'Applying {op!r}')
            op(json_doc)
            debug_msg('\n---> New State of JSON Document:\n')
            debug_msg(str(json_doc.to_python()) + '\n')

        debug_msg('=== End of Patch Application ===\n')

    def apply(self, json_doc: JsonContainerTypeHint):
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
