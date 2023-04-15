# Copyright (C) 2022 Rainer Garus
#
# This file is part of the ooresults Python package, a software to
# compute results of orienteering events.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from decimal import Decimal

import pytest

from ooresults.handler import build_results
from ooresults.handler import model
from ooresults.repo import result_type
from ooresults.repo import series_type


class Event:
    def __init__(self, name: str, date: str, series: bool):
        self.name = name
        self.date = date
        self.series = series


class Class_:
    def __init__(self, name: str):
        self.name = name


@pytest.fixture
def event_1():
    return Event(name="ev1", date="2021-03-20", series="Run 1")


@pytest.fixture
def event_2():
    return Event(name="ev2", date="2021-02-20", series=None)


@pytest.fixture
def event_3():
    return Event(name="ev3", date="2021-02-21", series="Run 3")


@pytest.fixture
def event_4():
    return Event(name="ev4", date="2021-02-21", series="Run 4")


@pytest.fixture
def event_5():
    return Event(name="ev5", date="2021-02-19", series="Run 5")


def test_use_only_events_in_series(event_1, event_2, event_3):
    events = [event_1, event_2, event_3]
    data = model.create_event_list(events=events)
    assert data == [event_3, event_1]


def test_sort_events_by_date(event_1, event_3, event_5):
    events = [event_1, event_3, event_5]
    data = model.create_event_list(events=events)
    assert data == [event_5, event_3, event_1]

    events = [event_1, event_3, event_5]
    data = model.create_event_list(events=events)
    assert data == [event_5, event_3, event_1]


def test_sort_events_by_name_if_dates_are_equal(event_3, event_4):
    events = [event_3, event_4]
    data = model.create_event_list(events=events)
    assert data == [event_3, event_4]

    events = [event_4, event_3]
    data = model.create_event_list(events=events)
    assert data == [event_3, event_4]


def test_no_results():
    class_a = Class_(name="Bahn A - Lang")
    data = build_results.build_total_results(
        settings=series_type.Settings(),
        list_of_results=[
            [
                (
                    class_a,
                    [
                        {
                            "first_name": "Angela",
                            "last_name": "Merkel",
                            "gender": "",
                            "year": "",
                            "class_": "Bahn A - Lang",
                            "result": result_type.PersonRaceResult(),
                        },
                        {
                            "first_name": "Claudia",
                            "last_name": "Merkel",
                            "gender": "",
                            "year": "",
                            "class_": "Bahn A - Lang",
                            "result": result_type.PersonRaceResult(),
                        },
                        {
                            "first_name": "Birgit",
                            "last_name": "Merkel",
                            "gender": "",
                            "year": "",
                            "class_": "Bahn A - Lang",
                            "result": result_type.PersonRaceResult(),
                        },
                    ],
                ),
            ]
        ],
    )
    assert data == [(class_a.name, [])]


def test_best_3_of_1_race():
    class_a = Class_(name="Bahn A - Lang")
    data = build_results.build_total_results(
        settings=series_type.Settings(
            nr_of_best_results=3,
        ),
        list_of_results=[
            [
                (
                    class_a,
                    [
                        {
                            "first_name": "Angela",
                            "last_name": "Merkel",
                            "gender": "",
                            "year": "",
                            "class_": "Bahn A - Lang",
                            "result": result_type.PersonRaceResult(),
                            "points": 0.365,
                        },
                    ],
                ),
            ],
        ],
    )
    print(data)
    assert data == [
        (
            class_a.name,
            [
                {
                    "first_name": "Angela",
                    "last_name": "Merkel",
                    "year": "",
                    "club": None,
                    "races": {0: Decimal("36.5")},
                    "organizer": {},
                    "sum": Decimal("36.5"),
                    "rank": 1,
                },
            ],
        ),
    ]


def test_best_3_of_2_races():
    class_a = Class_(name="Bahn A - Lang")
    data = build_results.build_total_results(
        settings=series_type.Settings(
            nr_of_best_results=3,
        ),
        list_of_results=[
            [
                (
                    class_a,
                    [
                        {
                            "first_name": "Angela",
                            "last_name": "Merkel",
                            "gender": "",
                            "year": "",
                            "class_": "Bahn A - Lang",
                            "result": result_type.PersonRaceResult(),
                            "points": 0.365,
                        },
                    ],
                ),
            ],
            [
                (
                    class_a,
                    [
                        {
                            "first_name": "Angela",
                            "last_name": "Merkel",
                            "gender": "",
                            "year": "",
                            "class_": "Bahn A - Lang",
                            "result": result_type.PersonRaceResult(),
                            "points": 0.991,
                        },
                    ],
                ),
            ],
        ],
    )
    print(data)
    assert data == [
        (
            class_a.name,
            [
                {
                    "first_name": "Angela",
                    "last_name": "Merkel",
                    "year": "",
                    "club": None,
                    "races": {0: Decimal("36.5"), 1: Decimal("99.1")},
                    "organizer": {},
                    "sum": Decimal("135.6"),
                    "rank": 1,
                },
            ],
        ),
    ]


def test_best_3_of_4_races():
    class_a = Class_(name="Bahn A - Lang")
    data = build_results.build_total_results(
        settings=series_type.Settings(
            nr_of_best_results=3,
        ),
        list_of_results=[
            [
                (
                    class_a,
                    [
                        {
                            "first_name": "Angela",
                            "last_name": "Merkel",
                            "gender": "",
                            "year": "",
                            "class_": "Bahn A - Lang",
                            "result": result_type.PersonRaceResult(),
                            "points": 0.365,
                        },
                    ],
                ),
            ],
            [
                (
                    class_a,
                    [
                        {
                            "first_name": "Angela",
                            "last_name": "Merkel",
                            "gender": "",
                            "year": "",
                            "class_": "Bahn A - Lang",
                            "result": result_type.PersonRaceResult(),
                            "points": 0.991,
                        },
                    ],
                ),
            ],
            [
                (
                    class_a,
                    [
                        {
                            "first_name": "Angela",
                            "last_name": "Merkel",
                            "gender": "",
                            "year": "",
                            "class_": "Bahn A - Lang",
                            "result": result_type.PersonRaceResult(),
                            "points": 0.012,
                        },
                    ],
                ),
            ],
            [
                (
                    class_a,
                    [
                        {
                            "first_name": "Angela",
                            "last_name": "Merkel",
                            "gender": "",
                            "year": "",
                            "class_": "Bahn A - Lang",
                            "result": result_type.PersonRaceResult(),
                            "points": 0.2,
                        },
                    ],
                ),
            ],
        ],
    )
    print(data)
    assert data == [
        (
            class_a.name,
            [
                {
                    "first_name": "Angela",
                    "last_name": "Merkel",
                    "year": "",
                    "club": None,
                    "races": {
                        0: Decimal("36.5"),
                        1: Decimal("99.1"),
                        2: Decimal("1.2"),
                        3: Decimal("20.0"),
                    },
                    "organizer": {},
                    "sum": Decimal("155.6"),
                    "rank": 1,
                },
            ],
        ),
    ]


def test_bonus_1_race():
    class_a = Class_(name="Bahn A - Lang")
    data = build_results.build_total_results(
        settings=series_type.Settings(),
        list_of_results=[
            [
                (
                    class_a,
                    [
                        {
                            "first_name": "Angela",
                            "last_name": "Merkel",
                            "gender": "",
                            "year": "",
                            "class_": "Bahn A - Lang",
                            "result": result_type.PersonRaceResult(),
                            "points": 0.365,
                        },
                    ],
                ),
            ],
            [
                (class_a, []),
            ],
        ],
        organizers=[
            [],
            [{"first_name": "Angela", "last_name": "Merkel"}],
        ],
    )
    print(data)
    assert data == [
        (
            class_a.name,
            [
                {
                    "first_name": "Angela",
                    "last_name": "Merkel",
                    "year": "",
                    "club": None,
                    "races": {0: Decimal("36.5")},
                    "organizer": {1: Decimal("18.25")},
                    "sum": Decimal("54.75"),
                    "rank": 1,
                },
            ],
        ),
    ]


def test_bonus_2_races():
    class_a = Class_(name="Bahn A - Lang")
    data = build_results.build_total_results(
        settings=series_type.Settings(),
        list_of_results=[
            [
                (
                    class_a,
                    [
                        {
                            "first_name": "Angela",
                            "last_name": "Merkel",
                            "gender": "",
                            "year": "",
                            "class_": "Bahn A - Lang",
                            "result": result_type.PersonRaceResult(),
                            "points": 0.365,
                        },
                    ],
                ),
            ],
            [
                (class_a, []),
            ],
            [
                (
                    class_a,
                    [
                        {
                            "first_name": "Angela",
                            "last_name": "Merkel",
                            "gender": "",
                            "year": "",
                            "class_": "Bahn A - Lang",
                            "result": result_type.PersonRaceResult(),
                            "points": 0.991,
                        },
                    ],
                ),
            ],
        ],
        organizers=[
            [],
            [{"first_name": "Angela", "last_name": "Merkel"}],
            [],
        ],
    )
    print(data)
    assert data == [
        (
            class_a.name,
            [
                {
                    "first_name": "Angela",
                    "last_name": "Merkel",
                    "year": "",
                    "club": None,
                    "races": {0: Decimal("36.5"), 2: Decimal("99.1")},
                    "organizer": {1: Decimal("67.8")},
                    "sum": Decimal("203.4"),
                    "rank": 1,
                },
            ],
        ),
    ]


def test_bonus_4_races():
    class_a = Class_(name="Bahn A - Lang")
    data = build_results.build_total_results(
        settings=series_type.Settings(
            nr_of_best_results=3,
        ),
        list_of_results=[
            [
                (
                    class_a,
                    [
                        {
                            "first_name": "Angela",
                            "last_name": "Merkel",
                            "year": "",
                            "gender": "",
                            "class_": "Bahn A - Lang",
                            "result": result_type.PersonRaceResult(),
                            "points": 0.365,
                        },
                    ],
                ),
            ],
            [
                (
                    class_a,
                    [
                        {
                            "first_name": "Angela",
                            "last_name": "Merkel",
                            "gender": "",
                            "year": "",
                            "class_": "Bahn A - Lang",
                            "result": result_type.PersonRaceResult(),
                            "points": 0.991,
                        },
                    ],
                ),
            ],
            [
                (class_a, []),
            ],
            [
                (
                    class_a,
                    [
                        {
                            "first_name": "Angela",
                            "last_name": "Merkel",
                            "gender": "",
                            "year": "",
                            "class_": "Bahn A - Lang",
                            "result": result_type.PersonRaceResult(),
                            "points": 0.012,
                        },
                    ],
                ),
            ],
            [
                (
                    class_a,
                    [
                        {
                            "first_name": "Angela",
                            "last_name": "Merkel",
                            "gender": "",
                            "year": "",
                            "class_": "Bahn A - Lang",
                            "result": result_type.PersonRaceResult(),
                            "points": 0.2,
                        },
                    ],
                ),
            ],
        ],
        organizers=[
            [],
            [],
            [{"first_name": "Angela", "last_name": "Merkel"}],
            [],
            [],
        ],
    )
    print(data)
    assert data == [
        (
            class_a.name,
            [
                {
                    "first_name": "Angela",
                    "last_name": "Merkel",
                    "year": "",
                    "club": None,
                    "races": {
                        0: Decimal("36.5"),
                        1: Decimal("99.1"),
                        3: Decimal("1.2"),
                        4: Decimal("20.0"),
                    },
                    "organizer": {2: Decimal("67.8")},
                    "sum": Decimal("203.4"),
                    "rank": 1,
                },
            ],
        ),
    ]


def test_ranking_1():
    class_a = Class_(name="Bahn A - Lang")
    data = build_results.build_total_results(
        settings=series_type.Settings(),
        list_of_results=[
            [
                (
                    class_a,
                    [
                        {
                            "first_name": "Angela",
                            "last_name": "Merkel",
                            "gender": "",
                            "year": "",
                            "class_": "Bahn A - Lang",
                            "result": result_type.PersonRaceResult(),
                            "points": 0.365,
                        },
                        {
                            "first_name": "Gerd",
                            "last_name": "Müller",
                            "gender": "",
                            "year": "",
                            "class_": "Bahn A - Lang",
                            "result": result_type.PersonRaceResult(),
                            "points": 0.991,
                        },
                    ],
                ),
            ],
        ],
    )
    print(data)
    assert data == [
        (
            class_a.name,
            [
                {
                    "first_name": "Gerd",
                    "last_name": "Müller",
                    "year": "",
                    "club": None,
                    "races": {0: Decimal("99.1")},
                    "organizer": {},
                    "sum": Decimal("99.1"),
                    "rank": 1,
                },
                {
                    "first_name": "Angela",
                    "last_name": "Merkel",
                    "year": "",
                    "club": None,
                    "races": {0: Decimal("36.5")},
                    "organizer": {},
                    "sum": Decimal("36.5"),
                    "rank": 2,
                },
            ],
        ),
    ]


def test_ranking_2():
    class_a = Class_(name="Bahn A - Lang")
    data = build_results.build_total_results(
        settings=series_type.Settings(),
        list_of_results=[
            [
                (
                    class_a,
                    [
                        {
                            "first_name": "Angela",
                            "last_name": "Merkel",
                            "gender": "",
                            "year": "",
                            "class_": "Bahn A - Lang",
                            "result": result_type.PersonRaceResult(),
                            "points": 0.995,
                        },
                    ],
                )
            ],
            [
                (
                    class_a,
                    [
                        {
                            "first_name": "Gerd",
                            "last_name": "Müller",
                            "gender": "",
                            "year": "",
                            "class_": "Bahn A - Lang",
                            "result": result_type.PersonRaceResult(),
                            "points": 0.091,
                        },
                    ],
                ),
            ],
        ],
    )
    print(data)
    assert data == [
        (
            class_a.name,
            [
                {
                    "first_name": "Angela",
                    "last_name": "Merkel",
                    "year": "",
                    "club": None,
                    "races": {0: Decimal("99.5")},
                    "organizer": {},
                    "sum": Decimal("99.5"),
                    "rank": 1,
                },
                {
                    "first_name": "Gerd",
                    "last_name": "Müller",
                    "year": "",
                    "club": None,
                    "races": {1: Decimal("9.1")},
                    "organizer": {},
                    "sum": Decimal("9.1"),
                    "rank": 2,
                },
            ],
        ),
    ]


def test_ranking_3():
    class_a = Class_(name="Bahn A - Lang")
    data = build_results.build_total_results(
        settings=series_type.Settings(),
        list_of_results=[
            [
                (
                    class_a,
                    [
                        {
                            "first_name": "Angela",
                            "last_name": "Merkel",
                            "gender": "",
                            "year": "",
                            "class_": "Bahn A - Lang",
                            "result": result_type.PersonRaceResult(),
                            "points": 0.65,
                        },
                    ],
                )
            ],
            [
                (
                    class_a,
                    [
                        {
                            "first_name": "Gerd",
                            "last_name": "Müller",
                            "gender": "",
                            "year": "",
                            "class_": "Bahn A - Lang",
                            "result": result_type.PersonRaceResult(),
                            "points": 0.95,
                        },
                        {
                            "first_name": "Angela",
                            "last_name": "Merkel",
                            "gender": "",
                            "year": "",
                            "class_": "Bahn A - Lang",
                            "result": result_type.PersonRaceResult(),
                            "points": 0.3,
                        },
                    ],
                ),
            ],
        ],
    )
    print(data)
    assert data == [
        (
            class_a.name,
            [
                {
                    "first_name": "Angela",
                    "last_name": "Merkel",
                    "year": "",
                    "club": None,
                    "races": {0: Decimal("65.0"), 1: Decimal("30.0")},
                    "organizer": {},
                    "sum": Decimal("95.0"),
                    "rank": 1,
                },
                {
                    "first_name": "Gerd",
                    "last_name": "Müller",
                    "year": "",
                    "club": None,
                    "races": {1: Decimal("95.0")},
                    "organizer": {},
                    "sum": Decimal("95.0"),
                    "rank": 1,
                },
            ],
        ),
    ]


def test_if_sum_is_0_then_rank_is_None():
    class_a = Class_(name="Bahn A - Lang")
    data = build_results.build_total_results(
        settings=series_type.Settings(),
        list_of_results=[
            [
                (
                    class_a,
                    [
                        {
                            "first_name": "Angela",
                            "last_name": "Merkel",
                            "gender": "",
                            "year": "",
                            "class_": "Bahn A - Lang",
                            "result": result_type.PersonRaceResult(),
                            "points": 0.65,
                        },
                    ],
                )
            ],
            [
                (
                    class_a,
                    [
                        {
                            "first_name": "Gerd",
                            "last_name": "Müller",
                            "gender": "",
                            "year": "",
                            "class_": "Bahn A - Lang",
                            "result": result_type.PersonRaceResult(),
                            "points": 0,
                        },
                        {
                            "first_name": "Angela",
                            "last_name": "Merkel",
                            "gender": "",
                            "year": "",
                            "class_": "Bahn A - Lang",
                            "result": result_type.PersonRaceResult(),
                            "points": 0.3,
                        },
                    ],
                ),
            ],
        ],
    )
    print(data)
    assert data == [
        (
            class_a.name,
            [
                {
                    "first_name": "Angela",
                    "last_name": "Merkel",
                    "year": "",
                    "club": None,
                    "races": {0: Decimal("65.0"), 1: Decimal("30.0")},
                    "organizer": {},
                    "sum": Decimal("95.0"),
                    "rank": 1,
                },
                {
                    "first_name": "Gerd",
                    "last_name": "Müller",
                    "year": "",
                    "club": None,
                    "races": {1: Decimal("0.0")},
                    "organizer": {},
                    "sum": Decimal("0.0"),
                    "rank": None,
                },
            ],
        ),
    ]
