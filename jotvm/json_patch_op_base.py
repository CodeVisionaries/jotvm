from .json_pointer import JsonPointer
from copy import deepcopy
from .json.types import JsonContainerType


class JsonPatchOpBase:
    """Abstract base class for JSON patch op classes."""

    # Needs to be implemented in derived classes
    @classmethod
    def get_op_name(cls):
        """Get operation name."""
        raise NotImplementedError('implement `get_op_name` method')

    def apply(self, json_doc: JsonContainerType):
        """Apply JSON patch operation on JSON document."""
        raise NotImplementedError('implement `apply` method')

    # Generic functions for all derived classes
    def __init__(self, json_doc: JsonContainerType):
        """Initialize JSON patch operation class."""
        self._verify(json_doc)
        fields = deepcopy(json_doc)
        for key in fields:
            if isinstance(fields[key], JsonPointer):
                fields[key] = str(fields[key])
        self._fields = fields

    @classmethod
    def _verify(cls, json_doc: JsonContainerType):
        """Internal method to verify dict representation of op."""
        expect_op = cls.get_op_name()
        current_op = json_doc['op']
        if expect_op != current_op:
            raise ValueError(
                f'Expected operation `{expect_op}` but encountered `{current_op}`.'
            )

    def __call__(self, json_doc: JsonContainerType):
        self.apply(json_doc)

    def to_dict(self):
        """Export operation class instance to dict."""
        return deepcopy(self._fields)

    @classmethod
    def from_dict(cls, json_doc: JsonContainerType):
        """Create operation class from dict."""
        return cls(json_doc)

    def __repr__(self):
        return f'{self.__class__!s}({self._fields!s})'

    def __str__(self):
        return repr(self)


def make_patch_op_class(
    class_name: str, op_name: str, apply_fun: callable,
    base_class=JsonPatchOpBase
):
    """Make concrete JSON patch op class."""
    cls_dict = {
        'get_op_name': classmethod(lambda cls: op_name),
        'apply': apply_fun,
    }
    return type(class_name, (base_class,), cls_dict)
