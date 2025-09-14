import pytest
from jotvm.json_pointer import JsonPointer
from jotvm.json.types import (
    JsonFactory,
    JsonNumber,
)


@pytest.fixture(scope="function")
def json_doc():
    return JsonFactory.from_python({
        "a": 5,
        "b": [1, 2, 3],
        "c": {"u": "cu", "v": [6, {"x": 8}]},
        "d": [1.3, [11, {"y": 19}, 8], 9],
    }, require_decimal=False)


def test_get(json_doc):
    """Expect retrieval of associated value."""
    assert JsonPointer("/a").get(json_doc) == 5
    assert JsonPointer("/b/1").get(json_doc) == 2
    assert JsonPointer("/c/u").get(json_doc) == "cu"
    assert JsonPointer("/c/v/1").get(json_doc) == {"x": 8}
    assert JsonPointer("/d/1/1/y").get(json_doc) == 19


def test_add_if_key_exists(json_doc):
    """Expect replacement of value in JSON object."""
    jp1 = JsonPointer("/a")
    assert jp1.exists(json_doc)
    jp1.add(json_doc, 17)
    assert jp1.get(json_doc) == 17
    jp2 = JsonPointer("/c/v")
    assert jp2.exists(json_doc)
    jp2.add(json_doc, 19)
    assert jp2.get(json_doc) == 19
    jp3 = JsonPointer("/d/1/1/y")
    assert jp3.exists(json_doc)
    jp3.add(json_doc, 23)
    assert jp3.get(json_doc) == 23


def test_add_if_key_not_exists(json_doc):
    """Expect creation of key and assignment of value in JSON object."""
    jp1 = JsonPointer("/x")
    assert not jp1.exists(json_doc)
    jp1.add(json_doc, 99)
    assert jp1.exists(json_doc)
    assert jp1.get(json_doc) == 99
    jp2 = JsonPointer("/c/v/1/y")
    assert not jp2.exists(json_doc)
    jp2.add(json_doc, {"v": "ha"})
    assert jp2.exists(json_doc)
    assert jp2.get(json_doc) == {"v": "ha"}


def test_add_to_array(json_doc):
    """Expect insertion at index and shifting elements back."""
    jp0 = JsonPointer("/b")
    orig_len = len(jp0.get(json_doc))
    jp1 = JsonPointer("/b/1")
    assert jp1.get(json_doc) == 2
    jp1.add(json_doc, JsonNumber('10'))
    assert jp1.get(json_doc) == 10
    jp2 = JsonPointer("/b/2")
    assert jp2.get(json_doc) == 2
    new_len = len(jp0.get(json_doc))
    assert orig_len + 1 == new_len
    jp3 = JsonPointer("/d/1/0")
    assert jp3.get(json_doc) == 11
    jp3.add(
        json_doc, JsonFactory.from_python([101, "a"], require_decimal=False)
    )
    assert jp3.get(json_doc) == [101, "a"]
    jp4 = JsonPointer("/d/1")
    assert jp4.get(json_doc)[1] == 11


def test_remove_existing_key(json_doc):
    """Expect removal of key in object."""
    jp1 = JsonPointer("/a")
    assert jp1.exists(json_doc)
    jp1.remove(json_doc)
    assert not jp1.exists(json_doc)
    jp2 = JsonPointer("/d/1/1/y")
    assert jp2.exists(json_doc)
    jp2.remove(json_doc)
    assert not jp2.exists(json_doc)


def test_remove_missing_key(json_doc):
    """Expect KeyError exception."""
    jp1 = JsonPointer("/x")
    assert not jp1.exists(json_doc)
    with pytest.raises(KeyError):
        jp1.remove(json_doc)
    jp2 = JsonPointer("/d/1/1/z")
    assert not jp2.exists(json_doc)
    with pytest.raises(KeyError):
        jp2.remove(json_doc)


def test_remove_existing_index(json_doc):
    """Expect removal of element at index in array."""
    jp0 = JsonPointer("/b")
    jp1 = JsonPointer("/b/0")
    jp2 = JsonPointer("/b/1")
    jp3 = JsonPointer("/b/2")
    orig_len = len(jp0.get(json_doc))
    orig_val1 = jp1.get(json_doc)
    orig_val2 = jp2.get(json_doc)
    orig_val3 = jp3.get(json_doc)
    jp2.remove(json_doc)
    new_len = len(jp0.get(json_doc))
    val1 = jp1.get(json_doc)
    val2 = jp2.get(json_doc)
    assert new_len + 1 == orig_len
    assert val1 == orig_val1
    assert val2 == orig_val3


def test_remove_missing_index(json_doc):
    """Expect IndexError exception."""
    jp1 = JsonPointer("/b/4")
    with pytest.raises(IndexError):
        jp1.remove(json_doc)
