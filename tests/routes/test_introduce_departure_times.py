import pytest

from routes.route import Route

# setup routes
r1 = Route(["1", "2"], 10)
r2 = Route(["1", "2"], 119)
r3 = Route(["1", "2"], 3)


def test_introduce_departure_times_divides_evenly() -> None:
    r1.introduce_departure_times(5, 10)
    assert r1.departure_times == {0: 2, 10: 2, 20: 2, 30: 2, 40: 2}


def test_introduce_departure_times_pads_remainders_1() -> None:
    r1.introduce_departure_times(3, 5)
    assert r1.departure_times == {0: 4, 5: 3, 10: 3}


def test_introduce_departure_times_pads_remainders_2() -> None:
    r2.introduce_departure_times(2, 35000)
    assert r2.departure_times == {0: 60, 35000: 59}


def test_introduce_departure_times_more_chunks_than_people() -> None:
    r3.introduce_departure_times(6, 60)
    assert r3.departure_times == {0: 1, 60: 1, 120: 1}
