from app.filters.models import Ne


def test_filter_not_equals():
    ne = Ne('foo', 'bar')
    assert ne() == {'foo': {'$ne': 'bar'}}


def test_filter_not_equals_empty_value():
    ne = Ne('foo', '')
    assert ne() == {'foo': {'$ne': ''}}


def test_filter_not_equals_none():
    ne = Ne('foo', None)
    assert ne() == {'foo': {'$ne': None}}
