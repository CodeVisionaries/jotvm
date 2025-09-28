import pytest
from jotvm.json.json_types import (
    JsonFactory,
    JsonObject,
    JsonArray,
    JsonNumber,
    JsonString,
    JsonBool,
    JsonNull,
)


@pytest.fixture
def json_example_string(): 
    return '{"a":1.23456789123456789123456789,"x":[["5",6,{"123": "hallo"}],2,"v"]}'


def test_json_value_roundtrip(json_example_string):
    json_value = JsonFactory.from_json(json_example_string)
    json_string = json_value.to_json()
    json_value2 = JsonFactory.from_json(json_string)
    assert json_value == json_value2


def test_json_python_roundtrip(json_example_string):
    json_value = JsonFactory.from_json(json_example_string)
    py_obj = json_value.to_python()
    json_value2 = JsonFactory.from_python(py_obj)
    assert json_value == json_value2
    py_obj2 = json_value2.to_python()
    assert py_obj == py_obj2
