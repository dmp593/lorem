from app.filters.models import Eq, And


def test_filter_and():
    filters = [
        Eq('mother', 'Ada Lovelace'),
        Eq('father', 'Alan Turing')
    ]

    and_filter = And(*filters)

    expected = {
        '$and': [
            {'mother': {'$eq': 'Ada Lovelace'}},
            {'father': {'$eq': 'Alan Turing'}}
        ]
    }

    assert and_filter() == expected
