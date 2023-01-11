from datetime import date
from datetime import datetime

import pytest

import taskw.utils as mod


def test_urbb64encode():
    assert mod.urlb64encode("") == ""
    assert mod.urlb64encode("fooba") == "Zm9vYmE="


def test_urbb64decode():
    assert mod.urlb64decode("") == ""
    assert mod.urlb64decode("Zm9vYmE=") == "fooba"


@pytest.mark.parametrize(
    "d,expected",
    [
        pytest.param(None, "", id="empty"),
        pytest.param(date(2022, 2, 17), "2022-02-17", id="long ago"),
        pytest.param(date(2023, 3, 30), "7d ago", id="days ago"),
        pytest.param(date(2023, 4, 5), "yesterday", id="yesterday"),
        pytest.param(date(2023, 4, 6), "today", id="today"),
        pytest.param(date(2023, 4, 7), "tomorrow", id="tomorrow"),
        pytest.param(date(2023, 4, 12), "6d", id="days"),
        pytest.param(date(2023, 4, 13), "1w", id="weeks"),
        pytest.param(date(2023, 12, 25), "2023-12-25", id="long time"),
        pytest.param(datetime(2023, 4, 5, 23, 30, 0), "yesterday", id="datetime"),
    ],
)
def test_hrdate(monkeypatch, d, expected):
    def mock_today():
        return mod.date(2023, 4, 6)

    monkeypatch.setattr(mod, "today", mock_today)
    assert mod.hrdate(d) == expected


def test_partition():
    def is_odd(n):
        return n % 2 == 1

    assert mod.partition(is_odd, []) == ([], [])
    assert mod.partition(is_odd, range(10)) == ([0, 2, 4, 6, 8], [1, 3, 5, 7, 9])


def test_groupby():
    fruits = ["Ananas", "Apple", "banana", "apricot", "blackberry", "melon"]
    get_first_letter = lambda x: x[0].upper()
    assert mod.groupby([], key=lambda x: x) == {}
    assert mod.groupby(fruits, get_first_letter) == {
        "A": ["Ananas", "Apple", "apricot"],
        "B": ["banana", "blackberry"],
        "M": ["melon"],
    }
