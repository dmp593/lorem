from app.filters.models import Eq, Or


def test_filter_or():
    filters = [
        Eq('flash', 'Bary Allen'),
        Eq('nerd', 'Cisco Ramon'),
        Eq('flashpoint', 'The New 52'),
    ]

    or_filter = Or(*filters)

    expected = {
        '$or': [
            {'flash': {'$eq': 'Bary Allen'}},
            {'nerd': {'$eq': 'Cisco Ramon'}},
            {'flashpoint': {'$eq': 'The New 52'}},
        ]
    }

    assert or_filter() == expected
