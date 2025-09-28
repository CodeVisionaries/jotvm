import pytest
from jotvm.json_patch import JsonPatch
from jotvm.json.json_types import (
    JsonFactory,
    JsonObject,
)


@pytest.fixture(scope="function")
def example_json_patch():
    return [
        {
            "op": "add",
            "path": "/z",
            "value": ["foo", "bar"]
        },
        {
            "op": "replace",
            "path": "/z/1",
            "value": 42
        },
        {
            "op": "copy",
            "from": "/z/1",
            "path": "/v"
        },
        {
            "op": "move",
            "from": "/z/0",
            "path": "/a"
        },
        {
            "op": "test",
            "path": "/v",
            "value": 42
        },
        {
            "op": "test",
            "path": "/z/0",
            "value": 42
        }
    ]


def test_apply_patch(example_json_patch):
    json_patch = JsonPatch.from_python(
        example_json_patch, require_decimal=False
    )
    json_doc = JsonObject() 
    json_patch(json_doc)


def test_patch_to_dict_translation(example_json_patch):
    json_patch = JsonPatch.from_python(
        example_json_patch, require_decimal=False
    )
    new_json_patch = json_patch.to_python()
    assert example_json_patch == new_json_patch


def test_patch_applied_to_array():
    json_doc = [1, {'a': 5}, 3]
    patch_ops = [
        {
            'op': 'replace',
            'path': '/1/a',
            'value': 10,
        },
        {
            'op': 'add',
            'path': '/-',
            'value': 30,
        },
    ]
    json_doc = JsonFactory.from_python(
        json_doc, require_decimal=False
    )
    json_patch = JsonPatch.from_python(
        patch_ops, require_decimal=False
    )
    json_patch(json_doc)
    assert json_doc[1]['a'] == 10
    assert json_doc[3] == 30
