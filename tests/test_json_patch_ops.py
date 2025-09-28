import pytest
from jotvm.json_pointer import JsonPointer
from jotvm.json_patch_ops import PATCH_OP_CLASSES
from jotvm.json.json_types import JsonObject


OP_CLASS_DICT = {cl.__name__: cl for cl in PATCH_OP_CLASSES}
globals().update(OP_CLASS_DICT)  # expose classes as variables


@pytest.fixture(scope="function")
def json_doc():
    return JsonObject.from_python({
        "a": 5,
        "b": [1, 2, 3],
        "c": {"u": "cu", "v": [6, {"x": 8}]},
        "d": [1.3, [11, {"y": 19}, 8], 9],
    }, require_decimal=False)


def test_add_op_missing_key(json_doc):
    """Expect addition of key with specified value."""
    jp1 = JsonPointer("/x")
    assert not jp1.exists(json_doc)
    add_op1 = JsonPatchAddOp(
        JsonObject.from_python({
        'op': 'add', 'path': "/x", 'value': 27
        }, require_decimal=False)
    )
    add_op1(json_doc)
    assert jp1.get(json_doc) == 27
    jp2 = JsonPointer("/c/v/1/y")
    assert not jp2.exists(json_doc)
    add_op2 = JsonPatchAddOp(
        JsonObject.from_python({
        'op': 'add', 'path': str(jp2), 'value': "test"
        }, require_decimal=False)
    )
    add_op2(json_doc)
    assert jp2.get(json_doc) == "test"


def test_add_op_existing_key(json_doc):
    """Expect replacement of value."""
    jp1 = JsonPointer("/a")
    assert jp1.exists(json_doc)
    JsonPatchAddOp.from_python({
        'op': 'add', 'path': "/a", 'value': 28,
    }, require_decimal=False)(json_doc)
    assert jp1.get(json_doc) == 28
    jp2 = JsonPointer("/d/1/1/y")
    value = jp2.get(json_doc)
    JsonPatchAddOp.from_python({
        'op': 'add', 'path': "/d/1/1/y", 'value': 39
    }, require_decimal=False)(json_doc)
    assert jp2.get(json_doc) == 39


def test_add_op_in_array(json_doc):
    """Expect insertion of value."""
    jp1 = JsonPointer("/b/2")
    value = jp1.get(json_doc)
    JsonPatchAddOp.from_python({
        'op': 'add', 'path': str(jp1), 'value': 72
    }, require_decimal=False)(json_doc)
    assert jp1.get(json_doc) == 72
    assert JsonPointer("/b/3").get(json_doc) == value


def test_remove_op_existing_key(json_doc):
    jp = JsonPointer("/a")
    assert jp.exists(json_doc)
    JsonPatchRemoveOp.from_python({
        'op': 'remove', 'path': str(jp)
    }, require_decimal=False)(json_doc)
    assert not jp.exists(json_doc)


def test_remove_op_missing_keyx(json_doc):
    jp = JsonPointer("/d/1/1/z")
    assert not jp.exists(json_doc)
    with pytest.raises(KeyError):
        JsonPatchRemoveOp.from_python({
            'op': 'remove', 'path': str(jp)
        }, require_decimal=False)(json_doc)


def test_remove_existing_index(json_doc):
    jp = JsonPointer("/d/1/2")
    assert jp.exists(json_doc)
    JsonPatchRemoveOp.from_python({
        'op': 'remove', 'path': str(jp)
    }, require_decimal=False)(json_doc)
    assert not jp.exists(json_doc)


def test_remove_missing_index(json_doc):
    jp = JsonPointer("/d/3/2")
    assert not jp.exists(json_doc)
    with pytest.raises(IndexError):
        JsonPatchRemoveOp.from_python({
            'op': 'remove', 'path': str(jp)
        }, require_decimal=False)(json_doc)


def test_replace_existing_key(json_doc):
    jp = JsonPointer("/a")
    assert jp.exists(json_doc)
    JsonPatchReplaceOp.from_python({
        'op': 'replace', 'path': str(jp), 'value': 23
    }, require_decimal=False)(json_doc)
    assert jp.get(json_doc) == 23


def test_replace_missing_key(json_doc):
    jp = JsonPointer("/x")
    assert not jp.exists(json_doc)
    with pytest.raises(KeyError):
        JsonPatchReplaceOp.from_python({
            'op': 'replace', 'path': "/x", 'value': 18
        }, require_decimal=False)(json_doc)


def test_replace_existing_index(json_doc):
    jp = JsonPointer("/b/1")
    assert jp.exists(json_doc)
    JsonPatchReplaceOp.from_python({
        'op': 'replace', 'path': str(jp), 'value':  ["t"]
    }, require_decimal=False)(json_doc)
    assert jp.get(json_doc) == ["t"]


def test_replace_missing_index(json_doc):
    jp = JsonPointer("/b/8")
    assert not jp.exists(json_doc)
    with pytest.raises(IndexError):
        JsonPatchReplaceOp.from_python({
            'op': 'replace', 'path': str(jp), 'value': 19
        }, require_decimal=False)(json_doc)


def test_move_existing_index(json_doc):
    jp1 = JsonPointer("/b/1")
    jp2 = JsonPointer("/x")
    orig_value = jp1.get(json_doc)
    JsonPatchMoveOp.from_python({
        'op': 'move', 'from': str(jp1), 'path': str(jp2)
    }, require_decimal=False)(json_doc)
    assert jp1.get(json_doc) == 3
    assert jp2.get(json_doc) == orig_value


def test_move_existing_key(json_doc):
    jp1 = JsonPointer("/a")
    jp2 = JsonPointer("/x")
    old_value = jp1.get(json_doc)
    assert jp1.exists(json_doc)
    assert not jp2.exists(json_doc)
    JsonPatchMoveOp.from_python({
        'op': 'move', 'from': str(jp1), 'path': str(jp2)
    }, require_decimal=False)(json_doc)
    assert jp2.get(json_doc) == old_value
    assert not jp1.exists(json_doc)


def test_move_missing_key(json_doc):
    jp1 = JsonPointer("/x")
    jp2 = JsonPointer("/y")
    assert not jp1.exists(json_doc)
    with pytest.raises(KeyError):
        JsonPatchMoveOp.from_python({
            'op': 'move', 'from': str(jp1), 'path': str(jp2)
        }, require_decimal=False)(json_doc)


def test_copy_existing_index(json_doc):
    jp1 = JsonPointer("/b/1")
    jp2 = JsonPointer("/x")
    assert not jp2.exists(json_doc)
    JsonPatchCopyOp.from_python({
        'op': 'copy', 'from': str(jp1), 'path': str(jp2)
    }, require_decimal=False)(json_doc)
    assert jp1.get(json_doc) == jp2.get(json_doc)


def test_copy_existing_key(json_doc):
    jp1 = JsonPointer("/a")
    jp2 = JsonPointer("/x")
    assert jp1.exists(json_doc)
    assert not jp2.exists(json_doc)
    JsonPatchCopyOp.from_python({
        'op': 'copy', 'from': str(jp1), 'path': str(jp2)
    }, require_decimal=False)(json_doc)
    assert jp1.get(json_doc) == jp2.get(json_doc)


def test_copy_missing_key(json_doc):
    jp1 = JsonPointer("/x")
    jp2 = JsonPointer("/y")
    assert not jp1.exists(json_doc)
    with pytest.raises(KeyError):
        JsonPatchCopyOp.from_python({
            'op': 'copy', 'from': str(jp1), 'path': str(jp2)
        }, require_decimal=False)(json_doc)


def test_test_with_good_value(json_doc):
    JsonPatchTestOp.from_python({
        'op': 'test', 'path': "/a", 'value': 5
    }, require_decimal=False)(json_doc)


def test_test_with_bad_value(json_doc):
    with pytest.raises(ValueError):
        JsonPatchTestOp.from_python({
            'op': 'test', 'path': "/a", 'value': 7
        }, require_decimal=False)(json_doc)
