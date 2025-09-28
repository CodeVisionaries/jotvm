from abc import ABC, abstractmethod
from .json_value import JsonValue


class JsonTransformBase(ABC):
    """Abstract base class for a JSON Transformation."""

    @abstractmethod
    def match(self, value: JsonValue) -> bool:
        """Return whether transformation applies."""
        pass

    @abstractmethod
    def transform(self, value: JsonValue) -> JsonValue:
        """Perform transformation of JSON value."""
        pass
