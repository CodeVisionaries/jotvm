from typing import Union
from copy import deepcopy
from .json_pointer import JsonPointer
from .json.types import (
    JsonString,
    JsonNumber,
    JsonBool,
    JsonObject,
    JsonArray,
)


def int_to_str(x):
    """Convert a integer-valued number to a string."""
    if isinstance(x, str):
        return x
    elif isinstance(x, float):
        if x != int(x):
            raise ValueError(f'Number {x} is not an integer')
        return str(int(x))
    elif isinstance(x, int):
        return str(x)
    raise TypeError(
        f'Integer to string conversion failed '
        f'(Unsupported type {type(x)})'
    )


def ensure_type(x, type_):
    if not isinstance(x, type_):
        raise TypeError(f'x = {x!s} is not of type {type_!s}')
    return x


def ensure_number(x):
    return ensure_type(x, JsonNumber) 


def ensure_array(x):
    return ensure_type(x, JsonArray)


def ensure_string(x):
    return ensure_type(x, JsonString)


def ensure_bool(x):
    return ensure_type(x, JsonBool)


class MissingValueType:
    pass


MissingValue = MissingValueType()


# Extension of standard JSON Patch format:
#   If a `fieldname-path` field is provided instead
#   of a `fieldname` field, the value is loaded from
#   the path indicated by the JSON Pointer stored under
#   the `fieldname-path` field.
def obtain_value(
    field_name: Union[str, JsonString], fields: JsonObject, json_doc: JsonObject, missing_ok=False
):
    """Obtain value, directly from fields or indirectly from json_doc."""
    if not isinstance(field_name, (str, JsonString)):
        raise TypeError('`field_name` must be type `str` or `JsonString`')
    if not isinstance(fields, JsonObject):
        raise TypeError('`fields` must be a `JsonObject`')
    if not isinstance(json_doc, (JsonObject, JsonArray)):
        raise TypeError('`json_doc` must be a `JsonObject` or `JsonArray`')

    value_path_str = field_name + '-path'
    if field_name in fields:
        value = fields[field_name]
    elif value_path_str in fields:
        value_path = JsonPointer(fields[value_path_str])
        value = value_path.get(json_doc)
    elif missing_ok:
        return MissingValue
    else:
        raise KeyError(f'Missing field `{field_name}`')
    return deepcopy(value)
