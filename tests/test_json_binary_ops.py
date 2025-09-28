import pytest
from jotvm.json.json_types import JsonNumber
from decimal import Decimal


def test_addition():
    assert JsonNumber('10') + JsonNumber('20') == JsonNumber('30')


def test_subtraction():
    assert JsonNumber('10') - JsonNumber('20') == JsonNumber('-10')


def test_multiplication():
    assert JsonNumber('10') * JsonNumber('20') == JsonNumber('200')


def test_modulo():
    assert JsonNumber('30') % JsonNumber('20') == JsonNumber('10')


def test_division():
    assert JsonNumber('10') / JsonNumber('20') == JsonNumber('0.5')


def test_floordiv():
    assert JsonNumber('30') // JsonNumber('20') == JsonNumber('1')


def test_power():
    assert JsonNumber('2') ** JsonNumber('5') == JsonNumber('32')


def test_less():
    assert not (JsonNumber('10') < JsonNumber('5'))
    assert JsonNumber('5') < JsonNumber('10')


def test_less_equal():
    assert JsonNumber('10') <= JsonNumber('10')
    assert JsonNumber('5') <= JsonNumber('10')


def test_greater():
    assert not (JsonNumber('5') > JsonNumber('10'))
    assert JsonNumber('15') > JsonNumber('10')


def test_greater_equal():
    assert JsonNumber('10') >= JsonNumber('10')
    assert JsonNumber('13') >= JsonNumber('10')
