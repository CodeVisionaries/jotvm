import pytest
from jotvm.json_patch import ExtJsonPatch
from copy import deepcopy
from jotvm.json.json_factory import JsonFactory
from jotvm.json.json_types import (
    JsonObject,
    JsonBool,
)


@pytest.fixture(scope="function")
def example_json_patch():
    return [
        {
            "op": "add",
            "path": "/a",
            "value": 10
        },
        {
            "op": "add",
            "path": "/b",
            "value": 40
        },
        {
            "op": "number/add",
            "path": "/a",
            "value": 20
        },
        {
            "op": "number/add",
            "path": "/b",
            "value-path": "/a"
        },
        {
            "op": "test",
            "path": "/a",
            "value": 30
        },
        {
            "op": "test",
            "path": "/b",
            "value": 70
        },
        {
            "op": "number/mul",
            "path": "/a",
            "value": 5
        },
        {
            "op": "test",
            "path": "/a",
            "value": 150
        },
        {
            "op": "number/mul",
            "path": "/b",
            "value-path": "/a"
        },
        {
            "op": "test",
            "path": "/b",
            "value": 10500
        },
        {
            "op": "add",
            "path": "/bool-value",
            "value": True
        },
        {
            "op": "ctrl/cond-apply-patch-op",
            "path": "",
            "check-path": "/bool-value",
            "false-patch-op": {"op": "add", "path": "/x", "value-path": "/a"},
            "true-patch-op": {"op": "add", "path": "/x", "value-path": "/b"},
        },
        {
            "op": "test",
            "path": "/x",
            "value": 10500
        },
        {
            "op": "ctrl/cond-apply-patch-op",
            "path": "",
            "check-path": "/bool-value",
            "false-patch-op": {"op": "add", "path": "/y", "value": "first"},
            "true-patch-op": {"op": "add", "path": "/y", "value": "second"},
        },
        {
            "op": "test",
            "path": "/y",
            "value": "second"
        },
        {
            "op": "replace",
            "path": "/bool-value",
            "value": False
        },
        {
            "op": "ctrl/cond-apply-patch-op",
            "path": "",
            "check-path": "/bool-value",
            "false-patch-op": {"op": "add", "path": "/x", "value-path": "/a"},
            "true-patch-op": {"op": "add", "path": "/x", "value-path": "/b"},
        },
        {
            "op": "test",
            "path": "/x",
            "value": 150
        },
        {
            "op": "ctrl/cond-apply-patch-op",
            "path": "",
            "check-path": "/bool-value",
            "false-patch-op": {"op": "add", "path": "/y", "value": "first"},
            "true-patch-op": {"op": "add", "path": "/y", "value": "second"},
        },
        {
            "op": "test",
            "path": "/y",
            "value": "first"
        },
    ]


def test_ext_patch_ops(example_json_patch):
    patch = ExtJsonPatch.from_python(example_json_patch, require_decimal=False)
    d = JsonObject({})
    patch(d)


def test_relation_ops():
    json_doc = JsonFactory.from_python(
        {'a': 10, 'b': 10, 'c': 30},
        require_decimal=False
    )
    patch_ops = [
            {'op': 'number/equal', 'path': '/x', 'left-value-path': '/a', 'right-value-path': '/b'},
            {'op': 'number/greater-equal', 'path': '/x1', 'left-value-path': '/a', 'right-value-path': '/b'},
            {'op': 'number/equal', 'path': '/y', 'left-value-path': '/a', 'right-value-path': '/c'},
            {'op': 'number/equal', 'path': '/z', 'left-value-path': '/a', 'right-value-path': '/c'},
    ]
    ext_patch = ExtJsonPatch.from_python(patch_ops)
    ext_patch(json_doc)
    assert type(json_doc['x']) is JsonBool
    assert json_doc['x'] == True
    assert type(json_doc['x1']) is JsonBool
    assert json_doc['x1'] == True
    assert type(json_doc['y']) is JsonBool
    assert json_doc['y'] == False
    assert type(json_doc['z']) is JsonBool
    assert json_doc['z'] == False


def test_apply_patch(example_json_patch):
    d1 = JsonFactory.from_python(
        {'patch': example_json_patch, 'xyz': {}},
        require_decimal=False,
    )
    apply_op = {
        "op": "ctrl/apply-patch",
        "path": "/xyz",
        "patch-path": "/patch" ,
    }
    ext_patch_list = example_json_patch + [apply_op]
    ext_patch = ExtJsonPatch.from_python(
        ext_patch_list, require_decimal=False
    )
    ext_patch(d1)
    d1.pop('patch')
    d2 = d1.pop('xyz')
    assert d1 == d2


def test_call_patch_args_values():
    json_doc = JsonFactory.from_python(
        {
            'func': [
                {'op': 'add', 'path': '/result', 'value': 0},
                {'op': 'number/add', 'path': '/result', 'value-path': '/x'},
                {'op': 'number/add', 'path': '/result', 'value-path': '/y'},
            ]
        },
        require_decimal=False
    )
    patch_ops = [
        {
            'op': 'ctrl/call-patch',
            'patch-path': '/func',
            'args': {'/x': 10, '/y': 20},
            'result-paths': {'/result': '/arith-result'}
        },
    ]
    ext_patch = ExtJsonPatch.from_python(
        patch_ops, require_decimal=False
    )
    ext_patch(json_doc)
    assert json_doc['arith-result'] == 30


def test_call_patch_with_args_paths():
    json_doc = {
        'number1': 13,
        'number2': 41,
        'func': [
            {'op': 'add', 'path': '/out', 'value': 0},
            {'op': 'number/add', 'path': '/out', 'value-path': '/inp/x'},
            {'op': 'number/add', 'path': '/out', 'value-path': '/inp/y'},
        ]
    }
    patch_ops = [
        {
            'op': 'ctrl/call-func',
            'patch-path': '/func',
            'x': 5,
            'y-path': '/number2',
            'out-path': '/arith-result',
        }
    ]
    ext_patch = ExtJsonPatch.from_python(patch_ops, require_decimal=False)
    json_doc = JsonFactory.from_python(json_doc, require_decimal=False)
    ext_patch(json_doc)
    assert json_doc['arith-result'] == 46


def test_while():
    json_doc = {
        'block-scope': {},
        'func': [
            {
                'op': 'number/add',
                'path': '/counter',
                'value': -1
            },
            {
                'op': 'number/greater',
                'path': '/check',
                'left-value-path': '/counter',
                'right-value': 0,
            }

        ]
    }
    patch_ops = [
        {
            'op': 'add',
            'path': '/block-scope/counter',
            'value': 10
        },
        {
            'op': 'add',
            'path': '/block-scope/check',
            'value': True
        },
        {
            'op': 'ctrl/while-loop',
            'path': '/block-scope',
            'check-path': '/block-scope/check',
            'patch-path': '/func'
        },
    ]
    ext_patch = ExtJsonPatch.from_python(patch_ops, require_decimal=False)
    json_doc = JsonFactory.from_python(json_doc, require_decimal=False)
    ext_patch.apply(json_doc)
    assert json_doc['block-scope']['counter'] == 0
    assert type(json_doc['block-scope']['check']) is JsonBool
    assert not json_doc['block-scope']['check']


def test_for_loop():
    json_doc = {}
    patch_ops = [
        {
            'op': 'add',
            'path': '/val',
            'value': 0,
        },
        {
            'op': 'ctrl/for-loop',
            'path': '',
            'start-value': 0,
            'stop-value': 10,
            'counter-path': '/i',
            'patch': [
                {
                    'op': 'number/add',
                    'path': '/val',
                    'value': 5,
                }
            ]
        },
    ]
    ext_patch = ExtJsonPatch.from_python(patch_ops, require_decimal=False)
    json_doc = JsonFactory.from_python(json_doc, require_decimal=False)
    ext_patch.apply(json_doc)
    assert json_doc['val'] == 55


def test_path_ops():
    json_doc = {'arr': [1, 2, 3]}
    json_patch = [
        # Add the mathematical operation (as data)
        # to be applied to each array element.
        {
            'op': 'add',
            'path': '/math-op',
            'value': {
                'op': 'number/mul',
                'path': 'filled dynamically with path',
                'value': 3,
            }
        },
        # Array representation of JSON pointer
        # which indicates array index.
        {
            'op': 'add',
            'path': '/array-index',
            'value': ['arr', 0],  # Second element will change dynamically!
        },
        # Determine the upper index limit
        {
            'op': 'array/length',
            'path': '/n',
            'value-path': '/arr',
        },
        {
            'op': 'number/add',
            'path': '/n',
            'value': -1,
        },
        # Cycle through the array.
        {
            'op': 'ctrl/for-loop',
            'path': '',
            'start-value': 0,
            'stop-value-path': '/n',
            'counter-path': '/array-index/1',
            'patch': [
                {
                    'op': 'array/join-path',
                    'path': '/math-op/path',
                    'value-path': '/array-index',
                },
                {
                    'op': 'ctrl/apply-patch-op',
                    'path': '',
                    'patch-op-path': '/math-op',
                },
            ]
        },
    ]
    ext_patch = ExtJsonPatch.from_python(json_patch, require_decimal=False)
    json_doc = JsonFactory.from_python(json_doc, require_decimal=False)
    ext_patch(json_doc)
    assert json_doc['arr'] == [3, 6, 9]


def test_patch_to_dict_translation(example_json_patch):
    json_patch = ExtJsonPatch.from_python(
        example_json_patch, require_decimal=False
    )
    new_json_patch = json_patch.to_python()
    assert example_json_patch == new_json_patch
