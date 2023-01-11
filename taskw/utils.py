from base64 import urlsafe_b64decode
from base64 import urlsafe_b64encode
from collections import defaultdict
from collections.abc import Callable
from collections.abc import Collection
from collections.abc import Iterable
from collections.abc import Mapping
from datetime import date
from datetime import datetime
from typing import TypeVar


def urlb64encode(s: str) -> str:
    return urlsafe_b64encode(s.encode()).decode()


def urlb64decode(s: str) -> str:
    return urlsafe_b64decode(s).decode()


def today():
    """Wrapper around date.today to ease tests.
    date.today cannot be mocked in tests so mock this wrapper instead.
    Performance cost is affordable given the expected throughput.
    """
    return date.today()


def hrdate(d: date | datetime | None) -> str:
    """Human readable relative date"""
    if d is None:
        return ""
    elif isinstance(d, datetime):
        d = d.date()

    days = (d - today()).days
    if days < -7:
        return d.isoformat()
    if days < -1:
        return f"{-days}d ago"
    elif days < 0:
        return "yesterday"
    if days < 1:
        return "today"
    elif days < 2:
        return "tomorrow"
    elif days < 7:
        return f"{days}d"
    elif days < 8 * 7:
        weeks = days // 7
        return f"{weeks}w"
    else:
        return d.isoformat()


T = TypeVar("T")


def partition(
    predicate: Callable[[T], bool], seq: Collection[T]
) -> tuple[list[T], list[T]]:
    """Use a predicate to partition entries into false entries and true entries

    >>> partition(is_odd, range(10))
    ([0 2 4 6 8], [1 3 5 7 9])
    """
    false = []
    true = []
    for elt in seq:
        if predicate(elt):
            true.append(elt)
        else:
            false.append(elt)
    return false, true


Key = TypeVar("Key")


def groupby(iterable: Iterable[T], key: Callable[[T], Key]) -> Mapping[Key, list[T]]:
    groups = defaultdict(list)
    for elt in iterable:
        if k := key(elt):
            groups[k].append(elt)
    return groups
