from copy import deepcopy
from .json_pointer import JsonPointer
from .type_aliases import JsonContainerType


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
    return enforce_type(x, (int, float))


def ensure_array(x):
    return ensure_type(x, list)


def ensure_string(x):
    return ensure_type(x, str)


def ensure_bool(x):
    return ensure_type(x, bool)


class MissingValueType:
    pass


MissingValue = MissingValueType()


# Extension of standard JSON Patch format:
#   If a `fieldname-path` field is provided instead
#   of a `fieldname` field, the value is loaded from
#   the path indicated by the JSON Pointer stored under
#   the `fieldname-path` field.
def obtain_value(field_name: str, fields: dict, json_doc: dict, missing_ok=False):
    """Obtain value, directly from fields or indirectly from json_doc."""
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
