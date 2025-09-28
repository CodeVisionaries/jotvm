from __future__ import annotations
from abc import ABC, abstractmethod
from decimal import (
    Decimal,
    Context,
    localcontext,
    ROUND_HALF_EVEN,
)


class JsonValue(ABC):
    """Abstract base class for all JSON types."""

    @abstractmethod
    def to_json(self, conv_args=None) -> str:
        """Convert object to JSON format."""
        pass

    @abstractmethod
    def to_python(self) -> object:
        pass

    @classmethod
    @abstractmethod
    def from_python(cls, **extra_args) -> JsonValue:
        pass

    @classmethod
    @abstractmethod
    def parse(cls, tokens: TokenStream) -> JsonValue:
        pass

    @abstractmethod
    def __eq__(self, other):
        pass

    CONTEXT = Context(
        prec=28, rounding=ROUND_HALF_EVEN
    )

    @staticmethod
    def _create_unary_op(operator, wrap=True):
        """Create binary op method. Assumes existence of self.value."""
        def unary_op(self):
            with localcontext(self.CONTEXT) as ctx:
                pure_value = getattr(self.value, operator)()
                if not wrap:
                    return pure_value
                from .json_factory import JsonFactory
                return JsonFactory.from_python(
                    getattr(self.value, operator())
                )
        return unary_op

    @staticmethod
    def _create_binary_op(operator, wrap=True, strict_type=True):
        """Create unary op method. Assumes presence of self.value."""
        def binary_op(self, other):
            if isinstance(other, type(self)):
                other_value = other.value
            elif not strict_type:
                other_value = other
            else:
                return NotImplemented

            with localcontext(self.CONTEXT) as ctx:
                pure_value = getattr(self.value, operator)(other_value)
                if not wrap:
                    return pure_value
                from .json_factory import JsonFactory
                return JsonFactory.from_python(pure_value)
        return binary_op
