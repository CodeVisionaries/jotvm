from typing import Union
from copy import deepcopy
from decimal import Decimal
from .json_patch_op_base import (
    JsonPatchOpBase,
    make_patch_op_class,
)
from .json_pointer import JsonPointer
from .utils import (
    obtain_value,
    MissingValue,
)
from .json.types import (
    JsonContainerTypes,
    JsonContainerTypeHint,
    JsonNumber,
    JsonArray,
    JsonObject,
)


__all__ = ['CONTROL_OP_CLASSES']


class ControlOpBase(JsonPatchOpBase):
    """Abstract base class for flow control operations."""
    pass


# Define the concrete .apply() methods of the
# ControlOpBase-derived classes implementing
# specific control flow structures, such as
# conditional assigment, loops, function calls


def cond_apply_patch_op_apply(self, json_doc: JsonContainerTypeHint):
    """Select and apply patch based on logical condition."""
    path = JsonPointer(self._fields['path'])
    bool_value = bool(obtain_value("check", self._fields, json_doc))
    if bool_value is True:
        patch_ops = obtain_value(
            'true-patch', self._fields, json_doc, missing_ok=True
        )
    elif bool_value is False:
        patch_ops = obtain_value(
            'false-patch', self._fields, json_doc, missing_ok=True
        )
    else:
        raise ValueError(
            f'Value of `check` or `check-path` must be bool but is {bool_value!s}'
        )

    if patch_ops is MissingValue:
        return

    target_dict = path.get(json_doc)
    from .json_patch import ExtJsonPatch
    patch = ExtJsonPatch.from_json_array(patch_ops)
    patch.apply(target_dict)


def cond_apply_patch_op_op_apply(self, json_doc: JsonContainerTypeHint):
    """Select and apply a patch operation based on logical condition."""
    path = JsonPointer(self._fields['path'])
    bool_value = bool(obtain_value("check", self._fields, json_doc))
    if bool_value is True:
        patch_op = obtain_value(
            'true-patch-op', self._fields, json_doc, missing_ok=True
        )
    elif bool_value is False:
        patch_op = obtain_value(
            'false-patch-op', self._fields, json_doc, missing_ok=True
        )
    else:
        raise ValueError(
            f'Value of `check` or `check-path` must be bool but is {bool_value!s}'
        )

    if patch_op is MissingValue:
        return

    target_dict = path.get(json_doc)
    from .json_patch import ExtJsonPatch
    # TODO: Get rid of this inefficient conversion
    patch = ExtJsonPatch.from_json_array(JsonArray([patch_op]))
    patch.apply(target_dict)


def while_op_apply(self, json_doc: JsonContainerTypeHint):
    check_path = JsonPointer(self._fields['check-path'])
    path = JsonPointer(self._fields['path'])
    if check_path[:len(path)] != path:
        raise ValueError(
            'check-path "{check_path!s}" not within path "{path!s}"'
        )
    local_check_path = check_path[len(path):]

    patch_ops = obtain_value('patch', self._fields, json_doc)
    from .json_patch import ExtJsonPatch
    ext_patch = ExtJsonPatch.from_json_array(patch_ops)
    work_dict = path.get(json_doc)
    check_value = local_check_path.get(work_dict)
    ext_patch.apply(work_dict)
    while check_value:
        ext_patch.apply(work_dict)
        check_value = local_check_path.get(work_dict)


def for_op_apply(self, json_doc: JsonContainerTypeHint):
    path = JsonPointer(self._fields['path'])
    local_counter_path = None
    if 'counter-path' in self._fields:
        counter_path = JsonPointer(self._fields['counter-path'])
        if counter_path[:len(path)] != path:
            raise ValueError(
                'counter-path "{counter_path!s}" not within path "{path!s}"'
            )
        local_counter_path = counter_path[len(path):]

    start_value = obtain_value('start-value', self._fields, json_doc)
    stop_value = obtain_value('stop-value', self._fields, json_doc)
    increment = obtain_value('increment', self._fields, json_doc, missing_ok=True)
    if increment is MissingValue:
        increment = 1

    patch_ops = obtain_value('patch', self._fields, json_doc)
    from .json_patch import ExtJsonPatch
    ext_patch = ExtJsonPatch.from_json_array(patch_ops)

    counter_backup = False
    orig_counter_value = None
    if counter_path.exists(json_doc):
        counter_backup = True
        orig_counter_value = deepcopy(counter_path.get(json_doc))

    work_dict = path.get(json_doc)
    for counter in range(start_value, stop_value+1, increment):
        json_counter = JsonNumber(Decimal(counter))
        if local_counter_path is not None:
            if not counter_backup:
                local_counter_path.add(work_dict, json_counter)
            else:
                # This special case is introduced to ensure
                # that the counter value is replacing a list
                # element rather than inserting into a list.
                local_counter_path.remove(work_dict)
                local_counter_path.add(work_dict, json_counter)
        ext_patch.apply(work_dict)

    if counter_backup:
        # Remove the temporary counter...
        local_counter_path.remove(work_dict)
        # ... and restore the original value
        local_counter_path.add(work_dict, orig_counter_value)
    else:
        local_counter_path.remove(json_doc)


def apply_patch_op_apply(self, json_doc: JsonContainerTypeHint):
    # here to avoid circular import
    from .json_patch import ExtJsonPatch
    path = JsonPointer(self._fields['path'])
    target_dict = path.get(json_doc)
    patch_ops = obtain_value('patch', self._fields, json_doc)
    patch = ExtJsonPatch.from_json_array(patch_ops)
    patch.apply(target_dict)


def apply_patch_op_op_apply(self, json_doc: JsonContainerTypeHint):
    # here to avoid circular import
    from .json_patch import ExtJsonPatch
    path = JsonPointer(self._fields['path'])
    target_dict = path.get(json_doc)
    patch_op = obtain_value('patch-op', self._fields, json_doc)
    patch = ExtJsonPatch.from_json_array(JsonArray([patch_op]))
    patch.apply(target_dict)


def call_patch_op_apply(self, json_doc: JsonContainerTypeHint):
    # prepare work dict by copying request fields into it
    work_dict = JsonObject()
    if 'args' in self._fields:
        for local_path, value in self._fields['args'].items():
            value = deepcopy(value)
            JsonPointer(local_path).add(work_dict, value)
    if 'args-paths' in self._fields:
        for local_path, ext_path in self._fields['args-paths'].items():
            value = deepcopy(JsonPointer(ext_path).get(json_doc))
            JsonPointer(local_path).add(work_dict, value)

    # obtain json patch and apply it to work dict
    from .json_patch import ExtJsonPatch
    patch_ops = obtain_value('patch', self._fields, json_doc)
    patch = ExtJsonPatch.from_json_array(patch_ops)
    patch.apply(work_dict)

    # copy the requested fields from work dict back into the json dict
    if 'result-paths' in self._fields:
        for local_path, ext_path in self._fields['result-paths'].items():
            value = deepcopy(JsonPointer(local_path).get(work_dict))
            JsonPointer(ext_path).add(json_doc, value)


def _prepare_func_input(
    inp_dict: dict, inp_args: dict, json_doc: JsonContainerTypeHint
):
    for inp_arg, value in inp_args.items():
        mod_inp_arg = inp_arg
        if inp_arg.endswith('-path'):
            inp_path = JsonPointer(value)
            value = deepcopy(inp_path.get(json_doc))
            mod_inp_arg = inp_arg[:-len('-path')]
        # Recursively descend into dictionaries
        # and apply the same -path replace mechanism.
        if isinstance(value, JsonObject):
            child_inp_dict = JsonObject()
            _prepare_func_input(child_inp_dict, value, json_doc)
            value = child_inp_dict

        inp_dict[mod_inp_arg] = value


def call_func_op_apply(self, json_doc: JsonContainerTypeHint):
    # Prepare work dict by copying request fields into it.
    # Assume standard convention everything except
    # "op", "patch", "patch-path", "out" field gets mapped
    # to a field in "/inp" in the work dict. If the name
    # ends with "-path", the value is interpreted as JSON Pointer
    # and the value at the corresponding address copied.
    work_dict = JsonObject()
    inp_args = deepcopy(self._fields)
    inp_args.pop('op', None)
    inp_args.pop('patch', None)
    inp_args.pop('patch-path', None)
    inp_args.pop('out-path', None)
    inp_dict = work_dict.setdefault('inp', JsonObject())
    _prepare_func_input(inp_dict, inp_args, json_doc)
    # move injected dependencies under /inp/req to /req
    work_dict['req'] = work_dict['inp'].pop('req', JsonObject())

    # obtain json patch and apply it to work dict
    from .json_patch import ExtJsonPatch
    patch_ops = obtain_value('patch', self._fields, json_doc)
    patch = ExtJsonPatch.from_json_array(patch_ops)
    patch.apply(work_dict)

    # copy the requested fields from work dict back into the json dict
    out_path = JsonPointer(self._fields['out-path'])
    out_path.add(json_doc, work_dict['out'])


control_op_class_defs = [
    ('CondApplyPatchOp', 'ctrl/cond-apply-patch', cond_apply_patch_op_apply, ControlOpBase),
    ('CondApplyPatchOpOp', 'ctrl/cond-apply-patch-op', cond_apply_patch_op_op_apply, ControlOpBase),
    ('WhileOp', 'ctrl/while-loop', while_op_apply, ControlOpBase),
    ('ForOp', 'ctrl/for-loop', for_op_apply, ControlOpBase),
    ('ApplyPatchOp', 'ctrl/apply-patch', apply_patch_op_apply, ControlOpBase),
    ('ApplyPatchOpOp', 'ctrl/apply-patch-op', apply_patch_op_op_apply, ControlOpBase),
    ('CallPatchOp', 'ctrl/call-patch', call_patch_op_apply, ControlOpBase),
    ('CallFuncOp', 'ctrl/call-func', call_func_op_apply, ControlOpBase),
]


CONTROL_OP_CLASSES = [
    make_patch_op_class(class_name, op_name, apply_func, base_class)
    for class_name, op_name, apply_func, base_class in control_op_class_defs
]
