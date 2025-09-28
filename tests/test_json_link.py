import pytest
from jotvm.json.json_transform import TransformingJsonFactory
from jotvm.json.json_link import (
    JsonLinkTransform,
    JsonLink,
)


def test_json_link_transform():
    test_dict = {'/': 'abcdef'}
    json_value = TransformingJsonFactory.from_python(test_dict)
    assert isinstance(json_value, JsonLink) 


def test_json_link_to_python():
    json_value = JsonLink('abcdef')
    py_obj = json_value.to_python()
    assert set(py_obj) == {'/'}
    assert py_obj['/'] == 'abcdef'


def test_json_link_to_json():
    json_value = JsonLink('abcdef')
    json_str = json_value.to_json()
    assert json_str == '{"/":"abcdef"}'
