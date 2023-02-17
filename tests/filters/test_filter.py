from app.filters.facades import Filter


def test_filter():
    f = Filter('foo', 'bar')
    assert f() == {'foo': 'bar'}


def test_filter_empty_value():
    f = Filter('foo', '')
    assert f() == {'foo': ''}


def test_filter_none():
    f = Filter('foo', None)
    assert f() == {'foo': None}
