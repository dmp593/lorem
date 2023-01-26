from app.filters import In


def test_filter_in():
    in_ = In('foo', 'bar')
    assert in_() == {'foo': {'$in': ['bar']}}


def test_filter_in_with_list():
    in_ = In('foo', ['bar', 'baz', 'boo'])
    assert in_() == {'foo': {'$in': ['bar', 'baz', 'boo']}}


def test_filter_in_empty_value():
    in_ = In('foo', '')
    assert in_() == {'foo': {'$in': ['']}}


def test_filter_in_none():
    in_ = In('foo', None)
    assert in_() == {'foo': {'$in': [None]}}
