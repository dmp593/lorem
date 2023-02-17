from app.filters.facades import Eq


def test_filter_equals():
    eq = Eq('foo', 'bar')
    assert eq() == {'foo': {'$eq': 'bar'}}


def test_filter_equals_empty_value():
    eq = Eq('foo', '')
    assert eq() == {'foo': {'$eq': ''}}


def test_filter_equals_none():
    eq = Eq('foo', None)
    assert eq() == {'foo': {'$eq': None}}
