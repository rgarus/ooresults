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

from ooresults.model import model, build_results
from ooresults.repo import series_type
from ooresults.repo.class_params import ClassParams
from ooresults.repo.class_type import ClassInfoType
from ooresults.repo.entry_type import EntryType
from ooresults.repo.entry_type import RankedEntryType
from ooresults.repo.event_type import EventType
from ooresults.repo.result_type import PersonRaceResult
from ooresults.repo.result_type import ResultStatus
from ooresults.repo.series_type import PersonSeriesResult
from ooresults.repo.series_type import Points


@pytest.fixture
def event_1() -> EventType:
    return EventType(
        id=1,
        name="ev1",
        date="2021-03-20",
        key=None,
        publish=False,
        series="Run 1",
        fields=[],
    )


@pytest.fixture
def event_2() -> EventType:
    return EventType(
        id=2,
        name="ev2",
        date="2021-02-20",
        key=None,
        publish=False,
        series=None,
        fields=[],
    )


@pytest.fixture
def event_3() -> EventType:
    return EventType(
        id=3,
        name="ev3",
        date="2021-02-21",
        key=None,
        publish=False,
        series="Run 3",
        fields=[],
    )


@pytest.fixture
def event_4() -> EventType:
    return EventType(
        id=4,
        name="ev4",
        date="2021-02-21",
        key=None,
        publish=False,
        series="Run 4",
        fields=[],
    )


@pytest.fixture
def event_5() -> EventType:
    return EventType(
        id=5,
        name="ev5",
        date="2021-02-19",
        key=None,
        publish=False,
        series="Run 5",
        fields=[],
    )


@pytest.fixture
def class_info_1() -> ClassInfoType:
    return ClassInfoType(
        id=1,
        name="Bahn A - Lang",
        short_name=None,
        course_id=None,
        course_name=None,
        course_length=None,
        course_climb=None,
        number_of_controls=None,
        params=ClassParams(),
    )


@pytest.fixture
def class_info_2() -> ClassInfoType:
    return ClassInfoType(
        id=2,
        name="Bahn A - Lang",
        short_name=None,
        course_id=None,
        course_name=None,
        course_length=None,
        course_climb=None,
        number_of_controls=None,
        params=ClassParams(),
    )


@pytest.fixture
def class_info_3() -> ClassInfoType:
    return ClassInfoType(
        id=3,
        name="Bahn A - Lang",
        short_name=None,
        course_id=None,
        course_name=None,
        course_length=None,
        course_climb=None,
        number_of_controls=None,
        params=ClassParams(),
    )


@pytest.fixture
def class_info_4() -> ClassInfoType:
    return ClassInfoType(
        id=1,
        name="Bahn A - Lang",
        short_name=None,
        course_id=None,
        course_name=None,
        course_length=None,
        course_climb=None,
        number_of_controls=None,
        params=ClassParams(),
    )


@pytest.fixture
def class_info_5() -> ClassInfoType:
    return ClassInfoType(
        id=5,
        name="Bahn A - Lang",
        short_name=None,
        course_id=None,
        course_name=None,
        course_length=None,
        course_climb=None,
        number_of_controls=None,
        params=ClassParams(),
    )


def test_use_only_events_in_series(
    event_1: EventType, event_2: EventType, event_3: EventType
):
    events = [event_1, event_2, event_3]
    data = model.create_event_list(events=events)
    assert data == [event_3, event_1]


def test_sort_events_by_date(
    event_1: EventType, event_3: EventType, event_5: EventType
):
    events = [event_1, event_3, event_5]
    data = model.create_event_list(events=events)
    assert data == [event_5, event_3, event_1]

    events = [event_3, event_5, event_1]
    data = model.create_event_list(events=events)
    assert data == [event_5, event_3, event_1]


def test_sort_events_by_name_if_dates_are_equal(event_3: EventType, event_4: EventType):
    events = [event_3, event_4]
    data = model.create_event_list(events=events)
    assert data == [event_3, event_4]

    events = [event_4, event_3]
    data = model.create_event_list(events=events)
    assert data == [event_3, event_4]


def test_no_results(event_1: EventType, class_info_1: ClassInfoType):
    entry_1 = EntryType(
        id=1,
        event_id=event_1.id,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        class_id=class_info_1.id,
        class_name=class_info_1.name,
    )

    entry_2 = EntryType(
        id=2,
        event_id=event_1.id,
        competitor_id=2,
        first_name="Claudia",
        last_name="Merkel",
        class_id=class_info_1.id,
        class_name=class_info_1.name,
    )

    entry_3 = EntryType(
        id=3,
        event_id=event_1.id,
        competitor_id=3,
        first_name="Birgit",
        last_name="Merkel",
        class_id=class_info_1.id,
        class_name=class_info_1.name,
    )

    data = build_results.build_total_results(
        settings=series_type.Settings(),
        list_of_results=[
            [
                (
                    class_info_1,
                    [
                        RankedEntryType(
                            entry=entry_1,
                        ),
                        RankedEntryType(
                            entry=entry_2,
                        ),
                        RankedEntryType(
                            entry=entry_3,
                        ),
                    ],
                ),
            ]
        ],
    )
    assert data == [(class_info_1.name, [])]


def test_best_3_of_1_race(event_1: EventType, class_info_1: ClassInfoType):
    entry_1 = EntryType(
        id=1,
        event_id=event_1.id,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        class_id=class_info_1.id,
        class_name=class_info_1.name,
        result=PersonRaceResult(
            time=600,
        ),
    )

    data = build_results.build_total_results(
        settings=series_type.Settings(
            nr_of_best_results=3,
        ),
        list_of_results=[
            [
                (
                    class_info_1,
                    [
                        RankedEntryType(
                            entry=entry_1,
                            rank=1,
                        ),
                    ],
                ),
            ],
        ],
    )
    print(data)
    assert data == [
        (
            class_info_1.name,
            [
                PersonSeriesResult(
                    first_name="Angela",
                    last_name="Merkel",
                    year=None,
                    club_name=None,
                    races={
                        0: Points(points=Decimal("100")),
                    },
                    total_points=Decimal("100"),
                    rank=1,
                ),
            ],
        ),
    ]


def test_best_3_of_2_races(
    event_1: EventType,
    event_2: EventType,
    class_info_1: ClassInfoType,
    class_info_2: ClassInfoType,
):
    entry_1 = EntryType(
        id=1,
        event_id=event_1.id,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        class_id=class_info_1.id,
        class_name=class_info_1.name,
        result=PersonRaceResult(
            time=600,
        ),
    )

    entry_2 = EntryType(
        id=2,
        event_id=event_2.id,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        class_id=class_info_2.id,
        class_name=class_info_2.name,
        result=PersonRaceResult(
            time=600,
        ),
    )

    data = build_results.build_total_results(
        settings=series_type.Settings(
            nr_of_best_results=3,
        ),
        list_of_results=[
            [
                (
                    class_info_1,
                    [
                        RankedEntryType(
                            entry=entry_1,
                            rank=1,
                        ),
                    ],
                ),
            ],
            [
                (
                    class_info_2,
                    [
                        RankedEntryType(
                            entry=entry_2,
                            rank=1,
                        ),
                    ],
                ),
            ],
        ],
    )
    print(data)
    assert data == [
        (
            class_info_1.name,
            [
                PersonSeriesResult(
                    first_name="Angela",
                    last_name="Merkel",
                    year=None,
                    club_name=None,
                    races={
                        0: Points(points=Decimal("100")),
                        1: Points(points=Decimal("100")),
                    },
                    total_points=Decimal("200"),
                    rank=1,
                ),
            ],
        ),
    ]


def test_best_3_of_4_races(
    event_1: EventType,
    event_2: EventType,
    event_3: EventType,
    event_4: EventType,
    class_info_1: ClassInfoType,
    class_info_2: ClassInfoType,
    class_info_3: ClassInfoType,
    class_info_4: ClassInfoType,
):
    entry_1 = EntryType(
        id=1,
        event_id=event_1.id,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        class_id=class_info_1.id,
        class_name=class_info_1.name,
        result=PersonRaceResult(
            time=600,
        ),
    )

    entry_2 = EntryType(
        id=2,
        event_id=event_2.id,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        class_id=class_info_2.id,
        class_name=class_info_2.name,
        result=PersonRaceResult(
            time=600,
        ),
    )

    entry_3 = EntryType(
        id=3,
        event_id=event_3.id,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        class_id=class_info_3.id,
        class_name=class_info_3.name,
        result=PersonRaceResult(
            time=600,
        ),
    )

    entry_4 = EntryType(
        id=4,
        event_id=event_4.id,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        class_id=class_info_4.id,
        class_name=class_info_4.name,
        result=PersonRaceResult(
            time=600,
        ),
    )

    data = build_results.build_total_results(
        settings=series_type.Settings(
            nr_of_best_results=3,
        ),
        list_of_results=[
            [
                (
                    class_info_1,
                    [
                        RankedEntryType(
                            entry=entry_1,
                            rank=1,
                        ),
                    ],
                ),
            ],
            [
                (
                    class_info_2,
                    [
                        RankedEntryType(
                            entry=entry_2,
                            rank=1,
                        ),
                    ],
                ),
            ],
            [
                (
                    class_info_3,
                    [
                        RankedEntryType(
                            entry=entry_3,
                            rank=1,
                        ),
                    ],
                ),
            ],
            [
                (
                    class_info_4,
                    [
                        RankedEntryType(
                            entry=entry_4,
                            rank=1,
                        ),
                    ],
                ),
            ],
        ],
    )
    print(data)
    assert data == [
        (
            class_info_1.name,
            [
                PersonSeriesResult(
                    first_name="Angela",
                    last_name="Merkel",
                    year=None,
                    club_name=None,
                    races={
                        0: Points(points=Decimal("100")),
                        1: Points(points=Decimal("100")),
                        2: Points(points=Decimal("100")),
                        3: Points(points=Decimal("100")),
                    },
                    total_points=Decimal("300"),
                    rank=1,
                ),
            ],
        ),
    ]


def test_bonus_1_race(
    event_1: EventType,
    event_2: EventType,
    class_info_1: ClassInfoType,
    class_info_2: ClassInfoType,
):
    entry_1 = EntryType(
        id=1,
        event_id=event_1.id,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        class_id=class_info_1.id,
        class_name=class_info_1.name,
        result=PersonRaceResult(
            time=600,
        ),
    )

    entry_2 = EntryType(
        id=2,
        event_id=event_2.id,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        class_id=2,
        class_name="Organizer",
    )

    data = build_results.build_total_results(
        settings=series_type.Settings(),
        list_of_results=[
            [
                (
                    class_info_1,
                    [
                        RankedEntryType(
                            entry=entry_1,
                            rank=1,
                        ),
                    ],
                ),
            ],
            [
                (class_info_2, []),
            ],
        ],
        organizers=[
            [],
            [entry_2],
        ],
    )
    print(data)
    assert data == [
        (
            class_info_1.name,
            [
                PersonSeriesResult(
                    first_name="Angela",
                    last_name="Merkel",
                    year=None,
                    club_name=None,
                    races={
                        0: Points(points=Decimal("100.00")),
                        1: Points(points=Decimal("50.00"), bonus=True),
                    },
                    total_points=Decimal("150.00"),
                    rank=1,
                ),
            ],
        ),
    ]


def test_bonus_2_races(
    event_1: EventType,
    event_2: EventType,
    event_3: EventType,
    class_info_1: ClassInfoType,
    class_info_2: ClassInfoType,
    class_info_3: ClassInfoType,
):
    entry_1 = EntryType(
        id=1,
        event_id=event_1.id,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        class_id=class_info_1.id,
        class_name=class_info_1.name,
        result=PersonRaceResult(
            time=600,
        ),
    )

    entry_2 = EntryType(
        id=2,
        event_id=event_2.id,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        class_id=2,
        class_name="Organizer",
    )

    entry_3 = EntryType(
        id=3,
        event_id=event_3.id,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        class_id=class_info_3.id,
        class_name=class_info_3.name,
        result=PersonRaceResult(
            time=600,
        ),
    )

    data = build_results.build_total_results(
        settings=series_type.Settings(),
        list_of_results=[
            [
                (
                    class_info_1,
                    [
                        RankedEntryType(
                            entry=entry_1,
                            rank=1,
                        ),
                    ],
                ),
            ],
            [
                (class_info_2, []),
            ],
            [
                (
                    class_info_3,
                    [
                        RankedEntryType(
                            entry=entry_3,
                            rank=1,
                        ),
                    ],
                ),
            ],
        ],
        organizers=[
            [],
            [entry_2],
            [],
        ],
    )
    print(data)
    assert data == [
        (
            class_info_1.name,
            [
                PersonSeriesResult(
                    first_name="Angela",
                    last_name="Merkel",
                    year=None,
                    club_name=None,
                    races={
                        0: Points(points=Decimal("100")),
                        2: Points(points=Decimal("100")),
                        1: Points(points=Decimal("100"), bonus=True),
                    },
                    total_points=Decimal("300"),
                    rank=1,
                ),
            ],
        ),
    ]


def test_bonus_4_races(
    event_1: EventType,
    event_2: EventType,
    event_3: EventType,
    event_4: EventType,
    event_5: EventType,
    class_info_1: ClassInfoType,
    class_info_2: ClassInfoType,
    class_info_3: ClassInfoType,
    class_info_4: ClassInfoType,
    class_info_5: ClassInfoType,
):
    entry_1 = EntryType(
        id=1,
        event_id=event_1.id,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        class_id=class_info_1.id,
        class_name=class_info_1.name,
        result=PersonRaceResult(
            time=600,
        ),
    )

    entry_2 = EntryType(
        id=1,
        event_id=event_2.id,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        class_id=class_info_2.id,
        class_name=class_info_2.name,
        result=PersonRaceResult(
            time=600,
        ),
    )

    entry_3 = EntryType(
        id=1,
        event_id=event_3.id,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        class_id=3,
        class_name="Organizer",
    )

    entry_4 = EntryType(
        id=4,
        event_id=event_4.id,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        class_id=class_info_4.id,
        class_name=class_info_4.name,
        result=PersonRaceResult(
            time=600,
        ),
    )

    entry_5 = EntryType(
        id=5,
        event_id=event_5.id,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        class_id=class_info_5.id,
        class_name=class_info_5.name,
        result=PersonRaceResult(
            time=600,
        ),
    )

    data = build_results.build_total_results(
        settings=series_type.Settings(
            nr_of_best_results=3,
        ),
        list_of_results=[
            [
                (
                    class_info_1,
                    [
                        RankedEntryType(
                            entry=entry_1,
                            rank=1,
                        ),
                    ],
                ),
            ],
            [
                (
                    class_info_2,
                    [
                        RankedEntryType(
                            entry=entry_2,
                            rank=1,
                        ),
                    ],
                ),
            ],
            [
                (class_info_3, []),
            ],
            [
                (
                    class_info_4,
                    [
                        RankedEntryType(
                            entry=entry_4,
                            rank=1,
                        ),
                    ],
                ),
            ],
            [
                (
                    class_info_5,
                    [
                        RankedEntryType(
                            entry=entry_5,
                            rank=1,
                        ),
                    ],
                ),
            ],
        ],
        organizers=[
            [],
            [],
            [entry_3],
            [],
            [],
        ],
    )
    print(data)
    assert data == [
        (
            class_info_1.name,
            [
                PersonSeriesResult(
                    first_name="Angela",
                    last_name="Merkel",
                    year=None,
                    club_name=None,
                    races={
                        0: Points(points=Decimal("100")),
                        1: Points(points=Decimal("100")),
                        3: Points(points=Decimal("100")),
                        4: Points(points=Decimal("100")),
                        2: Points(points=Decimal("100"), bonus=True),
                    },
                    total_points=Decimal("300"),
                    rank=1,
                ),
            ],
        ),
    ]


def test_ranking_1(event_1: EventType, class_info_1: ClassInfoType):
    entry_1 = EntryType(
        id=1,
        event_id=event_1.id,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        class_id=class_info_1.id,
        class_name=class_info_1.name,
        result=PersonRaceResult(
            time=600,
        ),
    )

    entry_2 = EntryType(
        id=2,
        event_id=event_1.id,
        competitor_id=2,
        first_name="Gerd",
        last_name="Müller",
        class_id=class_info_1.id,
        class_name=class_info_1.name,
        result=PersonRaceResult(
            time=400,
        ),
    )

    data = build_results.build_total_results(
        settings=series_type.Settings(),
        list_of_results=[
            [
                (
                    class_info_1,
                    [
                        RankedEntryType(
                            entry=entry_2,
                            rank=1,
                        ),
                        RankedEntryType(
                            entry=entry_1,
                            rank=2,
                        ),
                    ],
                ),
            ],
        ],
    )
    print(data)
    assert data == [
        (
            class_info_1.name,
            [
                PersonSeriesResult(
                    first_name="Gerd",
                    last_name="Müller",
                    year=None,
                    club_name=None,
                    races={
                        0: Points(points=Decimal("100")),
                    },
                    total_points=Decimal("100"),
                    rank=1,
                ),
                PersonSeriesResult(
                    first_name="Angela",
                    last_name="Merkel",
                    year=None,
                    club_name=None,
                    races={
                        0: Points(points=Decimal("66.67")),
                    },
                    total_points=Decimal("66.67"),
                    rank=2,
                ),
            ],
        ),
    ]


def test_ranking_2(
    event_1: EventType,
    event_2: EventType,
    class_info_1: ClassInfoType,
    class_info_2: ClassInfoType,
):
    entry_1 = EntryType(
        id=1,
        event_id=event_1.id,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        class_id=class_info_1.id,
        class_name=class_info_1.name,
        result=PersonRaceResult(
            time=600,
        ),
    )

    entry_2 = EntryType(
        id=2,
        event_id=event_2.id,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        class_id=class_info_2.id,
        class_name=class_info_2.name,
        result=PersonRaceResult(
            time=600,
        ),
    )

    entry_3 = EntryType(
        id=3,
        event_id=event_2.id,
        competitor_id=1,
        first_name="Gerd",
        last_name="Müller",
        class_id=class_info_2.id,
        class_name=class_info_2.name,
        result=PersonRaceResult(
            time=300,
        ),
    )

    data = build_results.build_total_results(
        settings=series_type.Settings(),
        list_of_results=[
            [
                (
                    class_info_1,
                    [
                        RankedEntryType(
                            entry=entry_1,
                            rank=1,
                        ),
                    ],
                )
            ],
            [
                (
                    class_info_2,
                    [
                        RankedEntryType(
                            entry=entry_3,
                            rank=1,
                        ),
                        RankedEntryType(
                            entry=entry_2,
                            rank=2,
                        ),
                    ],
                ),
            ],
        ],
    )
    print(data)
    assert data == [
        (
            class_info_1.name,
            [
                PersonSeriesResult(
                    first_name="Angela",
                    last_name="Merkel",
                    year=None,
                    club_name=None,
                    races={
                        0: Points(points=Decimal("100")),
                        1: Points(points=Decimal("50")),
                    },
                    total_points=Decimal("150"),
                    rank=1,
                ),
                PersonSeriesResult(
                    first_name="Gerd",
                    last_name="Müller",
                    year=None,
                    club_name=None,
                    races={
                        1: Points(points=Decimal("100")),
                    },
                    total_points=Decimal("100"),
                    rank=2,
                ),
            ],
        ),
    ]


def test_ranking_3(
    event_1: EventType,
    event_2: EventType,
    class_info_1: ClassInfoType,
    class_info_2: ClassInfoType,
):
    entry_1 = EntryType(
        id=1,
        event_id=event_1.id,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        class_id=class_info_1.id,
        class_name=class_info_1.name,
        result=PersonRaceResult(
            time=320,
        ),
    )

    entry_2 = EntryType(
        id=2,
        event_id=event_1.id,
        competitor_id=2,
        first_name="Gerd",
        last_name="Müller",
        class_id=class_info_1.id,
        class_name=class_info_1.name,
        result=PersonRaceResult(
            time=640,
        ),
    )

    entry_3 = EntryType(
        id=3,
        event_id=event_2.id,
        competitor_id=2,
        first_name="Gerd",
        last_name="Müller",
        class_id=class_info_2.id,
        class_name=class_info_2.name,
        result=PersonRaceResult(
            time=375,
        ),
    )

    entry_4 = EntryType(
        id=4,
        event_id=event_2.id,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        class_id=class_info_2.id,
        class_name=class_info_2.name,
        result=PersonRaceResult(
            time=750,
        ),
    )

    data = build_results.build_total_results(
        settings=series_type.Settings(),
        list_of_results=[
            [
                (
                    class_info_1,
                    [
                        RankedEntryType(
                            entry=entry_1,
                            rank=1,
                        ),
                        RankedEntryType(
                            entry=entry_2,
                            rank=2,
                        ),
                    ],
                )
            ],
            [
                (
                    class_info_2,
                    [
                        RankedEntryType(
                            entry=entry_3,
                            rank=1,
                        ),
                        RankedEntryType(
                            entry=entry_4,
                            rank=2,
                        ),
                    ],
                ),
            ],
        ],
    )
    print(data)
    assert data == [
        (
            class_info_1.name,
            [
                PersonSeriesResult(
                    first_name="Angela",
                    last_name="Merkel",
                    year=None,
                    club_name=None,
                    races={
                        0: Points(points=Decimal("100")),
                        1: Points(points=Decimal("50")),
                    },
                    total_points=Decimal("150"),
                    rank=1,
                ),
                PersonSeriesResult(
                    first_name="Gerd",
                    last_name="Müller",
                    year=None,
                    club_name=None,
                    races={
                        0: Points(points=Decimal("50")),
                        1: Points(points=Decimal("100")),
                    },
                    total_points=Decimal("150"),
                    rank=1,
                ),
            ],
        ),
    ]


def test_if_sum_is_0_then_rank_is_none(
    event_1: EventType,
    event_2: EventType,
    class_info_1: ClassInfoType,
    class_info_2: ClassInfoType,
):
    entry_1 = EntryType(
        id=1,
        event_id=event_1.id,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        class_id=class_info_1.id,
        class_name=class_info_1.name,
        result=PersonRaceResult(
            time=300,
        ),
    )

    entry_2 = EntryType(
        id=2,
        event_id=event_2.id,
        competitor_id=2,
        first_name="Gerd",
        last_name="Müller",
        class_id=class_info_2.id,
        class_name=class_info_2.name,
        result=PersonRaceResult(
            status=ResultStatus.MISSING_PUNCH,
            time=280,
        ),
    )

    entry_3 = EntryType(
        id=3,
        event_id=event_2.id,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        class_id=class_info_2.id,
        class_name=class_info_2.name,
        result=PersonRaceResult(
            time=300,
        ),
    )

    data = build_results.build_total_results(
        settings=series_type.Settings(),
        list_of_results=[
            [
                (
                    class_info_1,
                    [
                        RankedEntryType(
                            entry=entry_1,
                            rank=1,
                        ),
                    ],
                )
            ],
            [
                (
                    class_info_2,
                    [
                        RankedEntryType(
                            entry=entry_3,
                            rank=1,
                        ),
                        RankedEntryType(
                            entry=entry_2,
                            rank=None,
                        ),
                    ],
                ),
            ],
        ],
    )
    print(data)
    assert data == [
        (
            class_info_1.name,
            [
                PersonSeriesResult(
                    first_name="Angela",
                    last_name="Merkel",
                    year=None,
                    club_name=None,
                    races={
                        0: Points(points=Decimal("100")),
                        1: Points(points=Decimal("100")),
                    },
                    total_points=Decimal("200"),
                    rank=1,
                ),
                PersonSeriesResult(
                    first_name="Gerd",
                    last_name="Müller",
                    year=None,
                    club_name=None,
                    races={
                        1: Points(points=Decimal("0")),
                    },
                    total_points=Decimal("0"),
                    rank=None,
                ),
            ],
        ),
    ]


def test_compute_points_for_max_points_100_and_decimals_2(
    event_1: EventType, class_info_1: ClassInfoType
):
    entry_1 = EntryType(
        id=1,
        event_id=event_1.id,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        class_id=class_info_1.id,
        class_name=class_info_1.name,
        result=PersonRaceResult(
            time=300,
        ),
    )

    entry_2 = EntryType(
        id=2,
        event_id=event_1.id,
        competitor_id=2,
        first_name="Gerd",
        last_name="Müller",
        class_id=class_info_1.id,
        class_name=class_info_1.name,
        result=PersonRaceResult(
            time=260,
        ),
    )

    data = build_results.build_total_results(
        settings=series_type.Settings(
            maximum_points=100,
            decimal_places=2,
        ),
        list_of_results=[
            [
                (
                    class_info_1,
                    [
                        RankedEntryType(
                            entry=entry_2,
                            rank=1,
                        ),
                        RankedEntryType(
                            entry=entry_1,
                            rank=2,
                        ),
                    ],
                )
            ],
        ],
    )
    print(data)
    assert data == [
        (
            class_info_1.name,
            [
                PersonSeriesResult(
                    first_name="Gerd",
                    last_name="Müller",
                    year=None,
                    club_name=None,
                    races={
                        0: Points(points=Decimal("100")),
                    },
                    total_points=Decimal("100"),
                    rank=1,
                ),
                PersonSeriesResult(
                    first_name="Angela",
                    last_name="Merkel",
                    year=None,
                    club_name=None,
                    races={
                        0: Points(points=Decimal("86.67")),
                    },
                    total_points=Decimal("86.67"),
                    rank=2,
                ),
            ],
        ),
    ]


def test_compute_points_for_max_points_85_and_decimals_3(
    event_1: EventType, class_info_1: ClassInfoType
):
    entry_1 = EntryType(
        id=1,
        event_id=event_1.id,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        class_id=class_info_1.id,
        class_name=class_info_1.name,
        result=PersonRaceResult(
            time=300,
        ),
    )

    entry_2 = EntryType(
        id=2,
        event_id=event_1.id,
        competitor_id=2,
        first_name="Gerd",
        last_name="Müller",
        class_id=class_info_1.id,
        class_name=class_info_1.name,
        result=PersonRaceResult(
            time=260,
        ),
    )

    data = build_results.build_total_results(
        settings=series_type.Settings(
            maximum_points=85,
            decimal_places=3,
        ),
        list_of_results=[
            [
                (
                    class_info_1,
                    [
                        RankedEntryType(
                            entry=entry_2,
                            rank=1,
                        ),
                        RankedEntryType(
                            entry=entry_1,
                            rank=2,
                        ),
                    ],
                )
            ],
        ],
    )
    print(data)
    assert data == [
        (
            class_info_1.name,
            [
                PersonSeriesResult(
                    first_name="Gerd",
                    last_name="Müller",
                    year=None,
                    club_name=None,
                    races={
                        0: Points(points=Decimal("85")),
                    },
                    total_points=Decimal("85"),
                    rank=1,
                ),
                PersonSeriesResult(
                    first_name="Angela",
                    last_name="Merkel",
                    year=None,
                    club_name=None,
                    races={
                        0: Points(points=Decimal("73.667")),
                    },
                    total_points=Decimal("73.667"),
                    rank=2,
                ),
            ],
        ),
    ]


@pytest.mark.parametrize(
    "status, not_competing",
    [
        (ResultStatus.INACTIVE, False),
        (ResultStatus.INACTIVE, True),
        (ResultStatus.FINISHED, False),
        (ResultStatus.FINISHED, True),
        (ResultStatus.DID_NOT_START, False),
        (ResultStatus.DID_NOT_START, True),
    ],
)
def test_points_are_none_for_not_started_entries(
    event_1: EventType,
    class_info_1: ClassInfoType,
    status: ResultStatus,
    not_competing: bool,
):
    entry_1 = EntryType(
        id=1,
        event_id=event_1.id,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        class_id=class_info_1.id,
        class_name=class_info_1.name,
        result=PersonRaceResult(
            time=300,
        ),
    )

    data = build_results.build_total_results(
        settings=series_type.Settings(),
        list_of_results=[
            [
                (
                    class_info_1,
                    [
                        RankedEntryType(
                            entry=entry_1,
                            rank=None,
                        ),
                    ],
                )
            ],
        ],
    )
    print(data)
    assert data == [
        (
            class_info_1.name,
            [],
        ),
    ]


@pytest.mark.parametrize(
    "status, not_competing",
    [
        (ResultStatus.OK, True),
        (ResultStatus.MISSING_PUNCH, False),
        (ResultStatus.MISSING_PUNCH, True),
        (ResultStatus.DID_NOT_FINISH, False),
        (ResultStatus.DID_NOT_FINISH, True),
        (ResultStatus.OVER_TIME, False),
        (ResultStatus.OVER_TIME, True),
        (ResultStatus.DISQUALIFIED, False),
        (ResultStatus.DISQUALIFIED, True),
    ],
)
def test_points_are_0_for_not_classified_entries(
    event_1: EventType,
    class_info_1: ClassInfoType,
    status: ResultStatus,
    not_competing: bool,
):
    entry_1 = EntryType(
        id=1,
        event_id=event_1.id,
        competitor_id=1,
        first_name="Angela",
        last_name="Merkel",
        class_id=class_info_1.id,
        class_name=class_info_1.name,
        not_competing=True,
        result=PersonRaceResult(
            status=status,
            time=300,
        ),
    )

    data = build_results.build_total_results(
        settings=series_type.Settings(),
        list_of_results=[
            [
                (
                    class_info_1,
                    [
                        RankedEntryType(
                            entry=entry_1,
                            rank=None,
                        ),
                    ],
                )
            ],
        ],
    )
    print(data)
    assert data == [
        (
            class_info_1.name,
            [
                PersonSeriesResult(
                    first_name="Angela",
                    last_name="Merkel",
                    year=None,
                    club_name=None,
                    races={
                        0: Points(points=Decimal("0")),
                    },
                    total_points=Decimal("0"),
                    rank=None,
                ),
            ],
        ),
    ]
